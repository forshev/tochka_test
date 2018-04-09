# -*- coding: utf-8; -*-
import requests

from datetime import datetime, timedelta
from django.db import connection
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from lxml import html
from mainapp.models import Ticker, Price, InsiderTrade


def get_html(url):
    r = requests.get(url)
    if r.status_code != 200:
        r.raise_for_status()

    tree = html.fromstring(r.text)

    return tree


def paginate(request, objects, num):
    paginator = Paginator(objects, num)
    page = request.GET.get('page', '1')

    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)

    return result


def get_all_tickers(request):
    # do not return tickers without data
    tickers = Ticker.objects.filter(
        Q(insider_trades__isnull=False) & Q(prices__isnull=False)
    ).distinct().order_by('symbol')

    return paginate(request, tickers, 50)


def get_prices(ticker):
    ticker = get_object_or_404(Ticker, symbol=ticker)
    return Price.objects.filter(ticker=ticker).order_by('-date')


def get_insiders(request, ticker, insider=None):
    ticker = get_object_or_404(Ticker, symbol=ticker)
    if insider:
        insiders = InsiderTrade.objects.filter(slug=insider)
    else:
        insiders = InsiderTrade.objects.filter(
            ticker=ticker)

    return paginate(request, insiders.order_by('-last_date'), 15)


def get_analytics(ticker, date_from, date_to):
    ticker = get_object_or_404(Ticker, symbol=ticker)
    diffs = {}

    # if date is not specified, get earliest/latest date from DB
    if not date_from:
        date_from = Price.objects.earliest('date').date
    else:
        try:
            date_from = datetime.strptime(date_from, '%d-%m-%Y').date()
        except:
            diffs['error'] = "Date parameters must match format 'dd-mm-yyyy'"
            return diffs

    if not date_to:
        date_to = Price.objects.latest('date').date
    else:
        try:
            date_to = datetime.strptime(date_to, '%d-%m-%Y').date()
        except:
            diffs['error'] = "Date parameters must match format 'dd-mm-yyyy'"
            return diffs

    prices_from = Price.objects.filter(ticker=ticker, date=date_from).first()
    prices_to = Price.objects.filter(ticker=ticker, date=date_to).first()

    if not prices_from or not prices_to:
        diffs['error'] = "No data found for these dates"
        return diffs

    diffs['ticker'] = ticker.symbol
    diffs['date_from'] = date_from
    diffs['date_to'] = date_to
    diffs['diff_open'] = prices_from.open - prices_to.open
    diffs['diff_high'] = prices_from.high - prices_to.high
    diffs['diff_low'] = prices_from.low - prices_to.low
    diffs['diff_close'] = prices_from.close - prices_to.close

    return diffs


def min_interval(diffs, value):
    length = len(diffs)
    min_len = length + 1

    starts = []
    ends = []

    for start in range(0, length):

        curr_sum = diffs[start]

        for end in range(start + 1, length):
            curr_sum += diffs[end]

            if curr_sum > value and (end - start + 1) <= min_len:
                min_len = (end - start + 1)
                starts.append(start)
                ends.append(end)

    return min_len, starts, ends


# боль
def get_ticker_delta(ticker, value, _type):
    delta = {}
    if not value or not _type:
        delta['error'] = "You should specify value and type parameters"
        return delta

    ticker = get_object_or_404(Ticker, symbol=ticker)

    cursor = connection.cursor()
    query = """with series as (
                    SELECT generate_series((select min(date) from mainapp_price)::date
                                        ,(select max(date) from mainapp_price)::date
                                        ,interval '1 day') as date
                )
                select series.date::date, diff from (
                    select date,
                        abs({0} - lag({0}) over (order by date)) as diff
                    from mainapp_price
                    where ticker_id = {1}
                    order by date
                ) t1
                right join series on t1.date = series.date;"""
    cursor.execute(query.format(_type, ticker.pk))
    rows = cursor.fetchall()

    dates = [i[0] for i in rows]
    diffs = [0.0 if i[1] is None else i[1] for i in rows]

    # получаем списки с первыми и последними датами всех интервалов,
    # сумма изменений по которым больше заданного значения
    min_len, starts, ends = min_interval(diffs, float(value))

    if min_len > len(diffs):
        delta['error'] = "Value is greater than whole data changes sum"
        return delta

    starts = [dates[i] for i in starts]
    ends = [dates[i] for i in ends]

    intervals = list(zip(starts, ends))
    # выбираем из полученных выше интервалов те, разница дат которых равна
    # длинне минимального подсписка - 1
    intervals = [i for i in intervals if (i[1] - i[0]).days == min_len - 1]

    delta['ticker'] = ticker.symbol
    delta['min_len'] = min_len
    delta['intervals'] = intervals

    return delta

# -*- coding: utf-8; -*-
import requests

from datetime import datetime
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

    starts = None
    ends = None
    # starts = []
    # ends = []

    for start in range(0, length):

        curr_sum = diffs[start]

        if (curr_sum > value):
            return 1, 0, 1

        for end in range(start + 1, length):
            curr_sum += diffs[end]

            if curr_sum > value and (end - start + 1) < min_len:
                min_len = (end - start + 1)
                # starts.append(start + 1)
                # ends.append(end)
                starts = start
                ends = end

    return min_len, starts, ends


def get_ticker_delta(ticker, value, _type):
    ticker = get_object_or_404(Ticker, symbol=ticker)
    delta = {}

    cursor = connection.cursor()
    query = """select date,
                    abs({0} - lag({0}) over (order by date)) as diff
                from mainapp_price
                where ticker_id = {1}
                order by date
                offset 1"""
    # query = """select
    #             t1.date,
    #             abs(t1.{0} - t2.{0}) as diff
    #         from mainapp_price t1
    #         left join mainapp_price t2
    #             on t2.date = t1.date - INTERVAL '1' DAY
    #             and t2.ticker_id = t1.ticker_id
    #         where t1.ticker_id = {1}"""
    cursor.execute(query.format(_type, ticker.pk))
    rows = cursor.fetchall()

    dates = [i[0] for i in rows]
    diffs = [0.0 if i[1] is None else i[1] for i in rows]

    min_len, starts, ends = min_interval(diffs, float(value))

    # starts = [dates[i] for i in starts]
    # ends = [dates[i] for i in ends]

    # intervals = list(zip(starts, ends))
    # intervals = [i for i in intervals if (i[1] - i[0]).days == min_len]
    # for i in intervals:
    #     d = (i[1] - i[0]).days
    #     print(d)
    #     if d == min_len:
    #         print(i)

    start = dates[starts]
    end = dates[ends]

    print(min_len)
    print(start)
    print(end)
    # print(intervals)

    return delta

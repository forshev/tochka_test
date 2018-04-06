# -*- coding: utf-8; -*-
import requests

from datetime import datetime
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
            ticker=ticker).order_by('-last_date')

    return paginate(request, insiders, 15)


def get_analytics(ticker, date_from, date_to):
    ticker = get_object_or_404(Ticker, symbol=ticker)

    date_from = datetime.strptime(date_from, '%d-%m-%Y')
    date_to = datetime.strptime(date_to, '%d-%m-%Y')

    prices_from = Price.objects.get(ticker=ticker, date=date_from)
    prices_to = Price.objects.get(ticker=ticker, date=date_to)

    diffs = {}
    diffs['ticker'] = ticker
    diffs['diff_open'] = prices_from.open - prices_to.open
    diffs['diff_high'] = prices_from.high - prices_to.high
    diffs['diff_low'] = prices_from.low - prices_to.low
    diffs['diff_close'] = prices_from.close - prices_to.close

    return diffs

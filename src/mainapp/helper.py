# -*- coding: utf-8; -*-
import requests

from django.db.models import Min, Max
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
    tickers = Ticker.objects.all()
    return paginate(request, tickers, 30)


def get_prices(ticker):
    ticker = get_object_or_404(Ticker, symbol=ticker)
    return Price.objects.filter(ticker=ticker).order_by('-date')


def get_insiders(request, ticker):
    ticker = get_object_or_404(Ticker, symbol=ticker)
    insiders = InsiderTrade.objects.filter(ticker=ticker).order_by('-last_date')
    return paginate(request, insiders, 15)


def get_analytics(ticker, date_from, date_to):
    ticker = get_object_or_404(Ticker, symbol=ticker)
    prices = Price.objects.filter(
        ticker=ticker, date__range=(date_from, date_to)
    )

    open_max = prices.aggregate(Max('open'))
    open_min = prices.aggregate(Min('open'))
    high_max = prices.aggregate(Max('high'))
    high_min = prices.aggregate(Min('high'))
    low_max = prices.aggregate(Max('low'))
    low_min = prices.aggregate(Min('low'))
    close_max = prices.aggregate(Max('close'))
    close_min = prices.aggregate(Min('close'))

    return prices

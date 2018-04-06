# -*- coding: utf-8; -*-
from django.shortcuts import render
from mainapp.helper import (
    get_all_tickers, get_prices,
    get_insiders, get_analytics,
)


def index(request):
    tickers = get_all_tickers(request)
    return render(request, 'mainapp/index.html', {'tickers': tickers})


def ticker_prices(request, ticker):
    prices = get_prices(ticker)
    return render(request, 'mainapp/prices.html', {'prices': prices})


def ticker_insiders(request, ticker):
    insiders = get_insiders(request, ticker)
    return render(request, 'mainapp/insiders.html', {'insiders': insiders})


def insider_trades(request, ticker, insider):
    insiders = get_insiders(request, ticker, insider)
    return render(request, 'mainapp/insiders.html', {'insiders': insiders})


def ticker_analytics(request, ticker):
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)
    analytics = get_analytics(ticker, date_from, date_to)
    return render(request, 'mainapp/analytics.html', {'analytics': analytics})

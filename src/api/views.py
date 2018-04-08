# -*- coding: utf-8; -*-
import json

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import render
from mainapp.helper import (
    get_all_tickers, get_prices,
    get_insiders, get_analytics,
    get_ticker_delta,
)


def api_index(request):
    tickers = get_all_tickers(request)
    # Django querysets are not json serializable, so doing this
    # One can use Django Rest Framework to build APIs
    tickers = tickers.object_list.values(
        'id', 'symbol', 'security_name', 'market_category',
        'test_issue', 'financial_status', 'round_lot_size', 'etf',
        'next_shares',
    )
    return JsonResponse({'results': list(tickers)}, safe=False)


def api_ticker_prices(request, ticker):
    prices = get_prices(ticker)
    prices = prices.values(
        'id', 'ticker__symbol', 'date', 'open',
        'high', 'low', 'close', 'volume'
    )
    return JsonResponse({'results': list(prices)}, safe=False)


def api_ticker_insiders(request, ticker):
    insiders = get_insiders(request, ticker)
    insiders = insiders.object_list.values(
        'id', 'ticker__symbol', 'insider', 'relation',
        'last_date', 'transaction_type', 'owner_type', 'shares_traded',
        'last_price', 'shares_held',
    )
    return JsonResponse({'results': list(insiders)}, safe=False)


def api_insider_trades(request, ticker, insider):
    insiders = get_insiders(request, ticker, insider)
    insiders = insiders.object_list.values(
        'id', 'ticker__symbol', 'insider', 'relation',
        'last_date', 'transaction_type', 'owner_type', 'shares_traded',
        'last_price', 'shares_held',
    )
    return JsonResponse({'results': list(insiders)}, safe=False)


def api_ticker_analytics(request, ticker):
    date_from = request.GET.get('date_from', None)
    date_to = request.GET.get('date_to', None)
    analytics = get_analytics(ticker, date_from, date_to)

    return JsonResponse({'results': analytics}, safe=False)


def api_ticker_delta(request, ticker):
    value = request.GET.get('value', None)
    _type = request.GET.get('type', None)
    delta = get_ticker_delta(ticker, value, _type)

    return JsonResponse({'results': delta}, safe=False)

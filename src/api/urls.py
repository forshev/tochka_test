# -*- coding: utf-8 -*-
from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^$', views.api_index, name="api_index"),
    url(r'^(?P<ticker>[-\w]+)/$', views.api_ticker_prices, name="api_ticker_prices"),
    url(r'^(?P<ticker>[-\w]+)/insider$', views.api_ticker_insiders, name="api_ticker_insiders"),
    url(r'^(?P<ticker>[-\w]+)/insider/(?P<insider>[-\w]+)/$', views.api_insider_trades, name="api_insider_trades"),
    url(r'^(?P<ticker>[-\w]+)/analytics$', views.api_ticker_analytics, name="api_ticker_analytics"),
]

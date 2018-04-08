# -*- coding: utf-8 -*-
from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^(?P<ticker>[-\w]+)/$', views.ticker_prices, name="ticker_prices"),
    url(r'^(?P<ticker>[-\w]+)/insider$', views.ticker_insiders, name="ticker_insiders"),
    url(r'^(?P<ticker>[-\w]+)/insider/(?P<insider>[-\w]+)/$', views.insider_trades, name="insider_trades"),
    url(r'^(?P<ticker>[-\w]+)/analytics$', views.ticker_analytics, name="ticker_analytics"),
    url(r'^(?P<ticker>[-\w]+)/delta$', views.ticker_delta, name="ticker_delta"),
]

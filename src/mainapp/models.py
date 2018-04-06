# -*- coding: utf-8 -*-
from django.db import models


class Ticker(models.Model):
    symbol = models.CharField('Symbol', max_length=10)
    security_name = models.CharField('Security name', max_length=255)
    market_category = models.CharField('Market category', max_length=5)
    test_issue = models.CharField('Test Issue', max_length=5)
    financial_status = models.CharField('Financial status', max_length=5)
    round_lot_size = models.PositiveIntegerField('Round lot size')
    etf = models.CharField('ETF', max_length=5)
    next_shares = models.CharField('Next shares', max_length=5)

    def __str__(self):
        return self.symbol

    class Meta:
        verbose_name = 'ticker'
        verbose_name_plural = 'tickers'


class Price(models.Model):
    ticker = models.ForeignKey(Ticker, related_name='prices',
                               verbose_name=u'Ticker')
    date = models.DateField('Date')
    open = models.FloatField('Open')
    high = models.FloatField('High')
    low = models.FloatField('Low')
    close = models.FloatField('Close')
    volume = models.PositiveIntegerField('Volume')

    def __str__(self):
        return '{}:{}'.format(self.ticker.symbol, self.date)

    class Meta:
        verbose_name = 'price'
        verbose_name_plural = 'prices'


class InsiderTrade(models.Model):
    ticker = models.ForeignKey(Ticker, related_name='insider_trades',
                               verbose_name=u'Ticker')
    insider = models.CharField('Insider', max_length=70)
    relation = models.CharField('Relation', max_length=70)
    last_date = models.DateField('Last date')
    transaction_type = models.CharField('Transaction type', max_length=50)
    owner_type = models.CharField('Owner type', max_length=50)
    shares_traded = models.PositiveIntegerField('Shares traded')
    last_price = models.FloatField('Last price')
    shares_held = models.PositiveIntegerField('Shares held')
    slug = models.SlugField('Slug', max_length=255, blank=True, null=True)

    def __str__(self):
        return '{}-{}-{}'.format(
            self.insider, self.last_date, self.transaction_type
        )

    class Meta:
        verbose_name = 'insider trade'
        verbose_name_plural = 'insider trades'

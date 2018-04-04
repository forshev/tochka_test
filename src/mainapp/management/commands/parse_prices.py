# -*- coding: utf-8; -*-
import csv
import os
import requests
import time

from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from lxml import html
from mainapp.models import Ticker, Price


class Command(BaseCommand):
    help = "Parse csv and create tickers"

    def handle(self, *args, **options):
        print('Start')
        start = time.time()

        tickers = self.parse_many()

        end = time.time()
        time_total = end - start

        print(
            'Elapsed: {:.2f}s\nObjects created: {}\nFinish'.format(
                time_total, tickers
            )
        )

    def parse_one(self, symbol):
        url = 'https://www.nasdaq.com/symbol/{}/historical'.format(symbol.lower())
        ticker = Ticker.objects.get(symbol=symbol)
        r = requests.get(url)
        tree = html.fromstring(r.text)

        historical_table = tree.xpath(
            "//div[@id = 'historicalContainer']/div/table/tbody")[0]
        rows = historical_table.xpath(".//tr")

        for row in rows[1:]:
            tds = row.xpath(".//td/text()")
            new_price = Price(
                ticker=ticker,
                date=datetime.strptime(tds[0].strip(), '%m/%d/%Y'),
                open=tds[1].strip(),
                high=tds[2].strip(),
                low=tds[3].strip(),
                close=tds[4].strip(),
                volume=tds[5].strip().replace(',', ''),
            )
            new_price.save()

    def parse_many(self):
        tickers = Ticker.objects.all()[:1].values_list('symbol', flat=True)

        for t in tickers:
            self.parse_one(t)

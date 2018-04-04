# -*- coding: utf-8; -*-
import csv
import os
import requests
import time

from concurrent import futures
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from lxml import html
from mainapp.models import Ticker, Price


class Command(BaseCommand):
    help = "Parse html and create prices"

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_threads',
            default=1,
            help='Number of threads',
        )

    def handle(self, *args, **options):
        self.stdout.write('Start')
        start = time.time()

        tickers = Ticker.objects.all()[:3].values_list('symbol', flat=True)

        total = self.parse_many(tickers, options['num_threads'])

        end = time.time()
        time_total = end - start

        self.stdout.write(
            'Elapsed: {:.2f}s\nObjects created: {}'.format(
                time_total, total
            )
        )
        self.stdout.write(self.style.SUCCESS('Done'))

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

    def parse_many(self, t_list, num):
        with futures.ThreadPoolExecutor(max_workers=int(num)) as executor:
            to_do = []
            for t in t_list:
                future = executor.submit(self.parse_one, t)
                to_do.append(future)
                msg = 'Scheduled for {}: {}'
                print(msg.format(t, future))

            results = []
            for future in futures.as_completed(to_do):
                res = future.result()
                msg = '{} result: {!r}'
                print(msg.format(future, res))
                results.append(res)

        return len(results)

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
            default=30,
            help='Number of threads',
        )

    def handle(self, *args, **options):
        self.stdout.write('Start')
        start = time.time()

        tickers = Ticker.objects.all().values_list('symbol', flat=True)

        saved, errors = self.parse_many(tickers, options['num_threads'])

        end = time.time()
        time_total = end - start

        self.stdout.write(self.style.SUCCESS('\nDone'))
        self.stdout.write(
            'Elapsed: {:.2f}s\nErrors: {}\nObjects created: {}'.format(
                time_total, errors, saved))

    def parse_one(self, symbol):
        url = 'https://www.nasdaq.com/symbol/{}/historical'.format(symbol.lower())
        ticker = Ticker.objects.get(symbol=symbol)

        r = requests.get(url)
        if r.status_code != 200:
            r.raise_for_status()

        tree = html.fromstring(r.text)
        historical_table = tree.xpath(
            "//div[@id = 'historicalContainer']/div/table/tbody")[0]
        rows = historical_table.xpath(".//tr")

        prices = []
        for row in rows:
            tds = row.xpath(".//td/text()")

            # first td is time, not date
            try:
                date = datetime.strptime(tds[0].strip(), '%m/%d/%Y')
            except:
                date = datetime.now().date()

            new_price = Price(
                ticker=ticker,
                date=date,
                open=tds[1].strip(),
                high=tds[2].strip(),
                low=tds[3].strip(),
                close=tds[4].strip(),
                volume=tds[5].strip().replace(',', ''),
            )
            prices.append(new_price)

        Price.objects.bulk_create(prices, batch_size=1000)

        return len(prices)

    def parse_many(self, t_list, num_threads):
        # avoid creating more threads than necessary
        workers = min(1000, len(t_list), int(num_threads))
        self.stdout.write('{} threads created'.format(workers))

        with futures.ThreadPoolExecutor(max_workers=workers) as executor:
            to_do = []
            for t in t_list:
                future = executor.submit(self.parse_one, t)
                to_do.append(future)
                # msg = 'Scheduled for {}: {}'
                # self.stdout.write(msg.format(t, future))

            results = []
            errors = 0
            for idx, future in enumerate(futures.as_completed(to_do)):
                # Progress display
                msg = 'Parsing: {}/{}'
                self.stdout.write(
                    msg.format(idx + 1, len(to_do)),
                    ending='\r'
                )
                self.stdout.flush()

                try:
                    res = future.result()
                except:
                    errors += 1
                else:
                    # msg = '{} result: {!r}'
                    # self.stdout.write(msg.format(future, res))
                    results.append(res)

        return sum(results), errors

# -*- coding: utf-8; -*-
import csv
import os
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from mainapp.models import Ticker


class Command(BaseCommand):
    help = "Parse csv and create tickers"

    def handle(self, *args, **options):
        self.stdout.write('Start')
        start = time.time()

        tickers = self.parse()

        end = time.time()
        time_total = end - start

        self.stdout.write(
            'Elapsed: {:.2f}s\nObjects created: {}'.format(
                time_total, tickers
            )
        )
        self.stdout.write(self.style.SUCCESS('Done'))

    def parse(self):
        filename = 'nasdaqlisted.txt'
        input_file = os.path.join(
            settings.BASE_DIR, 'static', filename)

        with open(input_file) as f:
            lines = csv.reader(f, delimiter='|')
            next(lines, None)  # skip header

            tickers = []

            for l in lines:
                ticker = Ticker(
                    symbol=l[0], security_name=l[1], market_category=l[2],
                    test_issue=l[3], financial_status=l[4],
                    round_lot_size=l[5], etf=l[6], next_shares=l[7]
                )
                tickers.append(ticker)

        Ticker.objects.bulk_create(tickers, batch_size=1000)

        return len(tickers)

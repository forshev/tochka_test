# -*- coding: utf-8; -*-
import time

from concurrent import futures
from django.core.management.base import BaseCommand
from mainapp.models import Ticker


class ParseCommandMixin(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--num_threads',
            default=30,
            help='Number of threads',
        )

    def handle(self, *args, **options):
        self.stdout.write('Start')
        start = time.time()

        tickers = Ticker.objects.all()[:2].values_list('symbol', flat=True)

        saved, errors = self.parse_many(tickers, options['num_threads'])

        end = time.time()
        time_total = end - start

        self.stdout.write(self.style.SUCCESS('\nDone'))
        self.stdout.write(
            'Elapsed: {:.2f}s\nErrors: {}\nObjects created: {}'.format(
                time_total, errors, saved))

    def parse_one(self, symbol):
        pass

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

                res = future.result()
                results.append(res)
                # try:
                #     res = future.result()
                # except:
                #     errors += 1
                # else:
                #     # msg = '{} result: {!r}'
                #     # self.stdout.write(msg.format(future, res))
                #     results.append(res)

        return sum(results), errors

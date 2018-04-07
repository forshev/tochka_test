# -*- coding: utf-8; -*-
from concurrent import futures
from datetime import datetime
from django.utils.text import slugify
from itertools import chain
from mainapp.helper import get_html
from mainapp.mixins import ParseCommandMixin
from mainapp.models import Ticker, InsiderTrade


class Command(ParseCommandMixin):
    help = "Parse html and create insider trades"

    def parse_page(self, symbol, page_num):
        url = 'https://www.nasdaq.com/symbol/{}/insider-trades?page={}'.\
            format(symbol.lower(), page_num)
        ticker = Ticker.objects.get(symbol=symbol)

        tree = get_html(url)
        rows = tree.xpath("//div[@class='genTable']/table/tr")

        trades = []
        for row in rows:
            tds_row = row.xpath(".//td")
            tds = ['0' if td.text_content() == '' else td.text_content().strip() for td in tds_row]

            new_trade = InsiderTrade(
                ticker=ticker,
                insider=tds[0],
                relation=tds[1],
                last_date=datetime.strptime(tds[2], '%m/%d/%Y'),
                transaction_type=tds[3],
                owner_type=tds[4],
                shares_traded=tds[5].replace(',', ''),
                last_price=tds[6],
                shares_held=tds[7].replace(',', ''),
                slug=slugify(tds[0])
            )
            trades.append(new_trade)

        return trades

    def parse_one(self, symbol):
        url = 'https://www.nasdaq.com/symbol/{}/insider-trades'.\
            format(symbol.lower())

        tree = get_html(url)
        last_page = tree.xpath(
            "//a[@id='quotes_content_left_lb_LastPage']/@href")

        trades = []
        if last_page:
            # do not parse more than 10 pages
            last_num = min(int(last_page[0].split('=')[-1]), 10)

            # spawn thread for each pagination link (up to 10)
            with futures.ThreadPoolExecutor(max_workers=last_num) as executor:
                to_do = []
                for i in range(1, last_num+1):
                    future = executor.submit(self.parse_page, symbol, i)
                    to_do.append(future)

                results = []
                for future in futures.as_completed(to_do):
                    try:
                        res = future.result()
                    except:
                        pass
                    else:
                        results.append(res)

                trades = list(chain.from_iterable(results))

        else:
            trades = self.parse_page(symbol, 1)

        InsiderTrade.objects.bulk_create(trades, batch_size=1000)

        return len(trades)

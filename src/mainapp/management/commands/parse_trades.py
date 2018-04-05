# -*- coding: utf-8; -*-
import requests

from datetime import datetime
from lxml import html
from mainapp.mixins import ParseCommandMixin
from mainapp.models import Ticker, InsiderTrade


class Command(ParseCommandMixin):
    help = "Parse html and create insider trades"

    def parse_one(self, symbol, url=None):
        if not url:
            url = 'https://www.nasdaq.com/symbol/{}/insider-trades'.\
                format(symbol.lower())

        ticker = Ticker.objects.get(symbol=symbol)

        r = requests.get(url)
        if r.status_code != 200:
            r.raise_for_status()

        tree = html.fromstring(r.text)
        rows = tree.xpath("//div[@class='genTable']/table/tr")

        trades = []
        for row in rows:
            tds = row.xpath(".//td/text()")

            new_trade = InsiderTrade(
                ticker=ticker,
                insider=row.xpath(".//a/text()")[0].strip(),
                relation=tds[0].strip(),
                last_date=datetime.strptime(tds[1].strip(), '%m/%d/%Y'),
                transaction_type=tds[2].strip(),
                owner_type=tds[3].strip(),
                shares_traded=tds[4].strip().replace(',', ''),
                last_price=tds[5].strip(),
                shares_held=tds[6].strip().replace(',', ''),
            )
            trades.append(new_trade)

        # InsiderTrade.objects.bulk_create(trades, batch_size=1000)

        next_page = tree.xpath(
            "//a[@id='quotes_content_left_lb_NextPage']/@href")

        if next_page:
            print(next_page)[0]
            next_num = int(next_page[0].split('=')[-1])
            if next_num <= 10:
                self.parse_one(symbol, next_page[0])

        return len(trades)

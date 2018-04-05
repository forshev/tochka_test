# -*- coding: utf-8; -*-
import requests
import time

from concurrent import futures
from datetime import datetime
from lxml import html
from mainapp.mixins import ParseCommandMixin
from mainapp.models import Ticker, InsiderTrade


class Command(ParseCommandMixin):
    help = "Parse html and create insider trades"

    def parse_one(self, symbol):
        url = 'https://www.nasdaq.com/symbol/{}/insider-trades'.format(symbol.lower())
        ticker = Ticker.objects.get(symbol=symbol)

        r = requests.get(url)
        if r.status_code != 200:
            r.raise_for_status()

        tree = html.fromstring(r.text)
        trades_table = tree.xpath(
            "//div[@class='genTable']/table/tbody")[0]
        rows = trades_table.xpath(".//tr")

        trades = []
        for row in rows:
            print(html.tostring(row))
            tds = row.xpath(".//td/text()")

            new_trade = InsiderTrade(
                ticker=ticker,
                insider=tds[0].strip(),
                relation=tds[1].strip(),
                last_date=datetime.strptime(tds[2].strip(), '%m/%d/%Y'),
                transaction=tds[3].strip(),
                owner_type=tds[4].strip(),
                shares_traded=tds[5].strip(),
                last_price=tds[6].strip(),
                shares_held=tds[7].strip(),
            )
            trades.append(new_trade)

        InsiderTrade.objects.bulk_create(trades, batch_size=1000)

        return len(trades)

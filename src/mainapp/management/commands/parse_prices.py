# -*- coding: utf-8; -*-
import requests

from datetime import datetime
from lxml import html
from mainapp.mixins import ParseCommandMixin
from mainapp.models import Ticker, Price


class Command(ParseCommandMixin):
    help = "Parse html and create prices"

    def parse_one(self, symbol):
        url = 'https://www.nasdaq.com/symbol/{}/historical'.format(symbol.lower())
        ticker = Ticker.objects.get(symbol=symbol)

        r = requests.get(url)
        if r.status_code != 200:
            r.raise_for_status()

        tree = html.fromstring(r.text)
        historical_table = tree.xpath(
            "//div[@id='historicalContainer']/div/table/tbody")[0]
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

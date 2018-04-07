# -*- coding: utf-8; -*-
from datetime import datetime
from lxml import html
from mainapp.helper import get_html
from mainapp.mixins import ParseCommandMixin
from mainapp.models import Ticker, Price


class Command(ParseCommandMixin):
    help = "Parse html and create prices"

    def parse_one(self, symbol):
        url = 'https://www.nasdaq.com/symbol/{}/historical'.format(symbol.lower())
        ticker = Ticker.objects.get(symbol=symbol)

        tree = get_html(url)
        historical_table = tree.xpath(
            "//div[@id='historicalContainer']/div/table/tbody")[0]
        rows = historical_table.xpath(".//tr")

        prices = []
        for row in rows[1:]:
            tds_row = row.xpath(".//td")
            tds = ['0' if td.text_content() == '' else td.text_content().strip() for td in tds_row]

            new_price = Price(
                ticker=ticker,
                date=datetime.strptime(tds[0], '%m/%d/%Y'),
                open=tds[1],
                high=tds[2],
                low=tds[3],
                close=tds[4],
                volume=tds[5].replace(',', ''),
            )
            prices.append(new_price)

        Price.objects.bulk_create(prices, batch_size=1000)

        return len(prices)

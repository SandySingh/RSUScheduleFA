import argparse
import csv
import os
from collections import namedtuple

import currencyapicom

from polygon.rest import RESTClient
from polygon.rest.models import TickerDetails

Stock = namedtuple("Stock", ["ticker", "buy_date", "no_of_shares"])
StockValues = namedtuple("StockValues", ["name", "address", "postal_code", "buy_date", "initial_value",
                                         "highest_value", "closing_value"])


def get_complete_address(ticker_details: TickerDetails) -> str:
    address = ticker_details.address
    add = [address.address1, address.address2, address.city, address.state,
           "USA" if address.country is None else address.country, address.postal_code]
    add = list(filter(None, add))
    return ", ".join(add)


def get_exchange_rate(date: str) -> float:
    return currency_client.historical(date, "USD", ["INR"])["data"]["INR"]["value"]


def get_highest_and_closing_values(ticker: str, buy_date: str) -> (float, float):
    aggregate = polygon_client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=buy_date, to=f"{year}-12-31")
    highest = 0
    for value in aggregate:
        highest = max(highest, value.high)
    closing = aggregate[-1].close
    return highest, closing


def get_values(ticker: str, buy_date: str, no_of_shares: float) -> StockValues:
    details = details_cache.get(ticker)
    if details is None:
        details = polygon_client.get_ticker_details(ticker)
        details_cache[ticker] = details
    name = details.name
    address = get_complete_address(details)
    postal_code = details.address.postal_code

    initial_value = polygon_client.get_daily_open_close_agg(ticker=ticker, date=buy_date).close
    highest_value, closing_value = get_highest_and_closing_values(ticker, buy_date)

    exchange_rate = get_exchange_rate(buy_date)
    shares_inr_multiplier = no_of_shares * exchange_rate
    return StockValues(name, address, postal_code, buy_date, initial_value * shares_inr_multiplier,
                       highest_value * shares_inr_multiplier, closing_value * shares_inr_multiplier)


def get_stocks_list(file: str) -> list[Stock]:
    stocks = []
    with open(file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            stocks.append(Stock(row[0], row[1], float(row[2])))

    return stocks


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("ticker", type=str, help="Name of the stock")
    # parser.add_argument("buy_date", type=str, help="In yyyy-mm-dd format")  # yyyy-mm-dd
    # parser.add_argument("no_of_shares", type=int)
    parser.add_argument("file", type=str, help="CSV file containing list of stocks")
    parser.add_argument("year", type=str, help="Year for filing return")
    args = parser.parse_args()
    year = args.year

    stocks = get_stocks_list(args.file)

    polygon_client = RESTClient(api_key=os.environ["POLYGON_API_KEY"])
    currency_client = currencyapicom.Client(api_key=os.environ["EXCHANGE_API_KEY"])

    details_cache = {}
    stock_values = []

    for stock in stocks:
        stock_values.append(get_values(stock.ticker, stock.buy_date, stock.no_of_shares))

    print(stock_values)

    with open("output.csv", 'w') as csv_out:
        writer = csv.writer(csv_out, delimiter=",")
        writer.writerow(
            ("name", "address", "postal_code", "buy_date", "initial_value", "highest_value", "closing_value"))

        for stock in stock_values:
            writer.writerow((stock.name, stock.address, stock.postal_code, stock.buy_date, stock.initial_value,
                             stock.highest_value, stock.closing_value))

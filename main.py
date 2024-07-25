import argparse
import datetime
import os
import currencyapicom

from polygon.rest import RESTClient
from polygon.rest.models import TickerDetails


def get_complete_address(ticker_details: TickerDetails) -> str:
    address = ticker_details.address
    add = [address.address1, address.address2, address.city, address.state,
           "USA" if address.country is None else address.country, address.postal_code]
    add = list(filter(None, add))
    return ", ".join(add)


def get_exchange_rate(date: str) -> float:
    currency_client = currencyapicom.Client(os.environ["EXCHANGE_API_KEY"])
    return currency_client.historical(date, "USD", ["INR"])["data"]["INR"]["value"]


def get_highest_and_closing_values() -> (float, float):
    aggregate = polygon_client.get_aggs(ticker=ticker, multiplier=1, timespan="day", from_=buy_date, to="2024-03-31")
    highest = 0
    for value in aggregate:
        highest = max(highest, value.high)
    closing = aggregate[-1].close
    return highest, closing


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", type=str, help="Name of the stock")
    parser.add_argument("buy_date", type=str, help="In yyyy-mm-dd format")  # yyyy-mm-dd
    parser.add_argument("no_of_shares", type=int)
    args = parser.parse_args()

    ticker = args.ticker
    buy_date = args.buy_date
    no_of_shares = args.no_of_shares

    polygon_client = RESTClient(api_key=os.environ["POLYGON_API_KEY"])
    exchange_rate = get_exchange_rate(buy_date)

    details = polygon_client.get_ticker_details(ticker)
    name = details.name
    address = get_complete_address(details)
    postal_code = details.address.postal_code

    initial_value = polygon_client.get_daily_open_close_agg(ticker, date=buy_date).close
    highest_value, closing_value = get_highest_and_closing_values()

    shares_inr_multiplier = no_of_shares * exchange_rate
    print(name, address, postal_code, buy_date, initial_value * shares_inr_multiplier,
          highest_value * shares_inr_multiplier, closing_value * shares_inr_multiplier, sep=" || ")

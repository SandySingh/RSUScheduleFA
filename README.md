# RSUScheduleFA

## Requirements

[Polygon api key](https://polygon.io/dashboard/api-keys)

[Currency exchange api key](https://app.currencyapi.com/api-keys)

## Usage

Install requirements: `pip install -r requirements.txt`

Set Polygon api key: `set POLYGON_API_KEY=<polygon_api_key>`

Set Exchange api key: `set EXCHANGE_API_KEY=<exchange_api_key>`

Run: `python3 main.py <file> <year>` where file is your csv file containing all the stocks and year is the year of
filing returns (eg. 2023)

There is a sample [foreign_shares_sample.csv](foreign_shares_sample.csv) given for your reference.
from statistics import mean, median

import requests
import pandas as pd
from datetime import datetime, timedelta

PREFIX = "https://api.nbp.pl/api"
FIRSTELEMENT = 0
TABLES = ['a', 'b', 'c']


def get_url(table="A"):
    return f"{PREFIX}/exchangerates/tables/{table.upper()}/"


def get_all_currency():
    table = []
    for el in TABLES:
        response = requests.get(get_url(el))
        json = response.json()
        counter = 0
        for _ in json[0]['rates']:
            code = json[0]['rates'][counter]['code']
            if code not in table:
                table.append(code)
            counter = counter + 1
    return table


def check_the_currency(input):
    return get_all_currency().__contains__(input.upper())


def fetching_currency_data():
    days = 60
    df = pd.DataFrame(user_pairs_currency('EUR USD CHF', days))
    df.columns = ['EUR/PLN', 'USD/PLN', 'CHF/PLN']

    df['EUR/USD'] = round(df['EUR/PLN'] / df['USD/PLN'], 4)
    df['CHF/USD'] = round(df['CHF/PLN'] / df['USD/PLN'], 4)

    return df


def user_pairs_currency(currency_pairs, days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    exchange_rates = {}

    for pair in currency_pairs.split():
        url = f"{PREFIX}/exchangerates/rates/{check_where_is_currency_available(pair)}/{pair}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/?format=json"
        response = requests.get(url)
        data = response.json()

        rates = {entry['effectiveDate']: entry['mid'] for entry in data['rates']}
        exchange_rates[pair + '/PLN'] = rates

    return exchange_rates


def save_all_currency_data(df, filename="all_currency_data.csv"):
    df.to_csv(filename, index=False)


def save_selected_currency_data(df, selected_pairs, filename="selected_currency_data.csv"):
    filtered_df = df[["Date"] + selected_pairs]
    filtered_df.to_csv(filename, index=False)
    return filtered_df


def save_all_columns(data1, data2):
    noUsedColumns = []

    for data in data2.columns:
        if data not in data1.columns:
            noUsedColumns.append(data)

    if noUsedColumns is not None:
        for element in noUsedColumns:
            data1[element] = data2[element]

    data1.to_csv('all_currency_data.csv')

    print("Data for EUR/PLN, USD/PLN, CHF/PLN, EUR/USD, CHF/USD, " + ", ".join(
        [zmienna for zmienna in noUsedColumns]) + " has bean saved!")


def take_the_input():
    while True:
        user_input = input("Enter the currency separated by space (e.g. EUR USD CHF): ")
        length = len(user_input.split())
        counter = 0
        for el in user_input.upper().split():
            if check_the_currency(el):
                counter = counter + 1
            else:
                print("Wrong currency, try again")
                continue
        if length == counter:
            break
        else:
            continue
    return user_input


def data_selection():
    currency_pairs = take_the_input()
    exchange_rates_data = user_pairs_currency(currency_pairs.upper(), 60)

    df = pd.DataFrame.from_dict(exchange_rates_data)

    return df, currency_pairs


def only_user_selected_currency():
    data, currency = data_selection()
    data.to_csv('selected_currency_data.csv')
    print("Data for  " + "/PLN, ".join([zmienna.upper() for zmienna in currency.split()]) + "/PLN has bean saved!")


def check_where_is_currency_available(rate):
    for table in TABLES:
        codes = []
        url = f"{PREFIX}/exchangerates/tables/{table.upper()}/"
        response = requests.get(url)
        data = response.json()
        counter = 0
        for _ in data[0]['rates']:
            code = data[0]['rates'][counter]['code']
            if code not in table:
                if code not in codes:
                    codes.append(code)
            counter = counter + 1
        if rate in codes:
            return table.upper()


def take_rates_values(code):
    values = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    url = f"{PREFIX}/exchangerates/rates/{check_where_is_currency_available(code)}/{code}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/?format=json"
    response = requests.get(url)
    data = response.json()
    for mid in data['rates']:
        values.append(mid['mid'])
    return values


def take_date_for_rate(code, value):
    values = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    url = f"{PREFIX}/exchangerates/rates/{check_where_is_currency_available(code)}/{code}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/?format=json"
    response = requests.get(url)
    data = response.json()
    for mid in data['rates']:
        values.append(mid['mid'])

    if value == 'max':
        value = max(values)
    else:
        value = min(values)

    for rate in data['rates']:
        if value == rate['mid']:
            return rate['effectiveDate']


def show_average_rate(input):
    for code in input.upper().split():
        print('----------------------' + code + '------------------------')
        print(f'The average rate value for {code} is equal to {round(mean(take_rates_values(code)), 4)}')
        print(f'The median for {code} is equal to {round(median(take_rates_values(code)), 4)}')
        print(f'Max value for {code} currency occuried {take_date_for_rate(code, "max")} and is equal to {round(max(take_rates_values(code)), 4)}')
        print(f'Min value for {code} currency occuried {take_date_for_rate(code, "min")} and is equal to {round(min(take_rates_values(code)), 4)}\n')


if __name__ == "__main__":
    choices = ['0', '1', '2', '3', '4', '5', '9']

    print('Choose what you want to do:\n' +
          '1. Retrieve exchange rates for EUR/PLN, USD/PLN, CHF/PLN, EUR/USD, CHF/USD for the last 60 days\n' +
          '2. Select the currencies you want to see\n' +
          '3. Save all the data from point 1. and 2. into a CSV file \n' +
          '4. Select the currencies you want to see and save them into a CSV file\n' +
          '5. Show the average rate value, median, minimum, and maximum for the selected currency pair\n' +
          '9. Exit\n')

    while True:
        user_input = input("Your choice: ")
        if user_input in choices:
            break
        else:
            print("Wrong input, try again")
            continue

    while (user_input != 9):
        match user_input:
            case "1":
                print(fetching_currency_data())
                break
            case "2":
                print(data_selection()[FIRSTELEMENT])
                break
            case "3":
                save_all_columns(fetching_currency_data(), data_selection()[FIRSTELEMENT])
                break
            case "4":
                only_user_selected_currency()
                break
            case "5":
                show_average_rate(take_the_input())
                break
            case "9":
                exit()

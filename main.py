from statistics import mean, median

import requests
import pandas as pd
from datetime import datetime, timedelta

PREFIX = "https://api.nbp.pl/api"
FIRSTELEMENT = 0
TABLES = ['a', 'b', 'c']


def getUrl(table="A"):
    return f"{PREFIX}/exchangerates/tables/{table.upper()}/"


def getAllCurrency():
    table = []
    for el in TABLES:
        response = requests.get(getUrl(el))
        json = response.json()
        counter = 0
        for _ in json[0]['rates']:
            code = json[0]['rates'][counter]['code']
            if code not in table:
                table.append(code)
            counter = counter + 1
    return table


def checkTheCurrency(input):
    return getAllCurrency().__contains__(input.upper())


def fetch_exchange_rates(currency_code, days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    url = f"{PREFIX}/exchangerates/rates/A/{currency_code}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/"
    response = requests.get(url)
    data = response.json()
    rates = {rate['effectiveDate']: rate['mid'] for rate in data['rates']}
    return rates


def fetchingCurrencyData():
    days = 60
    eur_pln_rates = fetch_exchange_rates('EUR', days)
    usd_pln_rates = fetch_exchange_rates('USD', days)
    chf_pln_rates = fetch_exchange_rates('CHF', days)

    df = pd.DataFrame([eur_pln_rates, usd_pln_rates, chf_pln_rates]).T
    df.columns = ['EUR/PLN', 'USD/PLN', 'CHF/PLN']

    df['EUR/USD'] = df['EUR/PLN'] / df['USD/PLN']
    df['CHF/USD'] = df['CHF/PLN'] / df['USD/PLN']

    return df


def userPairsCurrency(currency_pairs, days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    exchange_rates = {}

    for pair in currency_pairs.split():
        url = f"{PREFIX}/exchangerates/rates/{checkWhereIsCurrencyAvailable(pair)}/{pair}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/?format=json"
        response = requests.get(url)
        data = response.json()

        rates = {entry['effectiveDate']: entry['mid'] for entry in data['rates']}
        exchange_rates[pair + '/PLN'] = rates

    return exchange_rates


# Function to save all previously mentioned data into a CSV file2
def save_all_currency_data(df, filename="all_currency_data.csv"):
    df.to_csv(filename, index=False)


def save_selected_currency_data(df, selected_pairs, filename="selected_currency_data.csv"):
    filtered_df = df[["Date"] + selected_pairs]
    filtered_df.to_csv(filename, index=False)
    return filtered_df


def saveAllColumns(data1, data2):
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


def takeTheInput():
    while True:
        user_input = input("Enter the currency separated by space (e.g. EUR USD CHF): ")
        length = len(user_input.split())
        counter = 0
        for el in user_input.upper().split():
            if checkTheCurrency(el):
                counter = counter + 1
            else:
                print("Wrong input, try again")
                continue
        if length == counter:
            break
        else:
            continue
    return user_input


def dataSelection():
    # Allow the user to input the name of the currency pairs they wish to access information for
    currency_pairs = takeTheInput()
    # Fetch the exchange rates for the last 60 days
    exchange_rates_data = userPairsCurrency(currency_pairs.upper(), 60)

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame.from_dict(exchange_rates_data)

    return df, currency_pairs


def onlyUserSelectedCurrency():
    data, currency = dataSelection()
    data.to_csv('selected_currency_data.csv')
    print("Data for  " + "/PLN, ".join([zmienna.upper() for zmienna in currency.split()]) + "/PLN has bean saved!")


def checkWhereIsCurrencyAvailable(rate):
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


def takeRatesValues(code):
    values = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    url = f"{PREFIX}/exchangerates/rates/{checkWhereIsCurrencyAvailable(code)}/{code}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/?format=json"
    response = requests.get(url)
    data = response.json()
    for mid in data['rates']:
        values.append(mid['mid'])
    return values


def takeDateForRate(code, value):
    values = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    url = f"{PREFIX}/exchangerates/rates/{checkWhereIsCurrencyAvailable(code)}/{code}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/?format=json"
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


def showAverageRate(input):
    for code in input.upper().split():
        print('----------------------' + code + '------------------------')
        print(f'The average rate value for {code} is equal to {round(mean(takeRatesValues(code)), 4)}')
        print(f'The median for {code} is equal to {round(median(takeRatesValues(code)), 4)}')
        print(f'Max value for {code} currency occuried {takeDateForRate(code, "max")} and is equal to {round(max(takeRatesValues(code)), 4)}')
        print(f'Min value for {code} currency occuried {takeDateForRate(code, "min")} and is equal to {round(min(takeRatesValues(code)), 4)}')


if __name__ == "__main__":
    choices = ['0', '1', '2', '3', '4', '5', '9']

    print('Choose what you want to do:\n' +
          '1. Retrieve exchange rates for EUR/PLN, USD/PLN, CHF/PLN, EUR/USD, CHF/USD for the last 60 days\n' +
          '2. Select the currencies you want to see\n' +
          '3. Save all the data from point 1. and 2. into a CSV file \n' +
          '4. Select the currencies you want to see and save them into a CSV file\n' +
          '5. Show the average rate value, median, minimum, and maximum for the selected currency pair\n' +
          '9. Exit')

    while (True):
        user_input = input("Your choice: ")
        if user_input in choices:
            break
        else:
            print("Wrong input, try again")
            continue

    while (user_input != 9):
        match user_input:
            case "1":
                print(fetchingCurrencyData())
                break
            case "2":
                print(dataSelection()[FIRSTELEMENT])
                break
            case "3":
                saveAllColumns(fetchingCurrencyData(), dataSelection()[FIRSTELEMENT])
                break
            case "4":
                onlyUserSelectedCurrency()
                break
            case "5":
                showAverageRate(takeTheInput())
                break
            case "9":
                exit()

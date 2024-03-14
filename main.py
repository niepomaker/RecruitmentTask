import requests
import pandas as pd
from datetime import datetime, timedelta
prefix = "https://api.nbp.pl/api"
FIRSTELEMENT = 0

def fetch_exchange_rates(currency_code, days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    url = f"{prefix}/exchangerates/rates/A/{currency_code}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/"
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

    for pair in currency_pairs:
        url = f"{prefix}/exchangerates/rates/A/{pair}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}/?format=json"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        rates = {entry['effectiveDate']: entry['mid'] for entry in data['rates']}
        exchange_rates[pair + '/PLN'] = rates

    return exchange_rates

# Function to save all previously mentioned data into a CSV file
def save_all_currency_data(df, filename="all_currency_data.csv"):
    df.to_csv(filename, index=False)


# Function to save only user-selected currency pairs into a CSV file
def save_selected_currency_data(df, selected_pairs, filename="selected_currency_data.csv"):
    # Filter the DataFrame to include only the selected currency pairs
    filtered_df = df[["Date"] + selected_pairs]
    filtered_df.to_csv(filename, index=False)
    return filtered_df

def saveAllColumns(data1, data2):
    noUsedColumns = []

    for data in data2.columns:
        if (data not in data1.columns):
            noUsedColumns.append(data)

    if noUsedColumns is not None:
        for element in noUsedColumns:
            data1[element] = data2[element]

    data1.to_csv('all_currency_data.csv')

    # Używając list comprehension do konwersji wszystkich elementów na stringi
    print("Data for EUR/PLN, USD/PLN, CHF/PLN, EUR/USD, CHF/USD, " + ", ".join([zmienna for zmienna in noUsedColumns]) + " has bean saved!")



def dataSelection():
    # Allow the user to input the name of the currency pairs they wish to access information for
    user_input = input("Enter the currency separated by space (e.g. EUR USD CHF): ")
    currency_pairs = user_input.upper().split()
    # Fetch the exchange rates for the last 60 days
    exchange_rates_data = userPairsCurrency(currency_pairs, 60)

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame.from_dict(exchange_rates_data)

    return (df, currency_pairs)


def onlyUserSelectedCurrency():
    data , currency = dataSelection()
    data.to_csv('selected_currency_data.csv')
    print("Data for  " + ", ".join([zmienna for zmienna in currency]) + " has bean saved!")

if __name__ == "__main__":

    print('Choose what you want to do:\n' +
          '1. Retrieve exchange rates for EUR/PLN, USD/PLN, CHF/PLN, EUR/USD, CHF/USD for the last 60 days\n' +
          '2. Select the currencies you want to see\n' +
          '3. Save all the data from point 1. and 2. into a CSV file \n' +
          '4. Select the currencies you want to see and save them into a CSV file\n'+
          '9. Exit\n')

    user_input = input("Your choice: ")
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
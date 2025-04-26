import numpy as np
import pandas as pd
from urllib.error import HTTPError
import streamlit as st

def get_data(data_path):
    data = pd.read_csv(data_path)
    return data.set_index(data.columns[0])


def get_provinces():
    data = pd.read_csv('data/local_data.csv')
    columns = list(data.columns)
    columns.pop(0)  # remove index column
    return columns


def get_pop():

    pop_data = pd.read_csv("data/pop.csv")
    pop = pop_data["popolazione"].apply(lambda x: int(x.replace(".","")[:-3]))

    return pop


def mysign(inp):
    if np.sign(inp) > 0:
        return '+'
    else:
        return ''


def add_day(day):
    # Convert each day to the correct argument
    argument = day.strftime("%Y%m%d")

    # Link to the appropriate csv with the info
    url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-' + argument + '.csv'
    url2 = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-' + argument + '.csv'
    try:
        df_loc = pd.read_csv(url, index_col=0)
        df_nat = pd.read_csv(url2, index_col=0)
    except HTTPError as err:
        if err.code == 404:
            print('Non existent file (yet) for day', day, '- skipping it.')
            return 0
        else:
            raise

    return [df_nat, df_loc]


provinces = get_provinces()


def append_lines(day, arg):
    giorni = day.strftime("%d/%m/%Y")

    df_nat = arg[0]
    casi = np.sum(df_nat["totale_casi"])
    tamponi = np.sum(df_nat["tamponi"])
    hospital = np.sum(df_nat["ricoverati_con_sintomi"])
    icu = np.sum(df_nat["terapia_intensiva"])
    deaths = np.sum(df_nat["deceduti"])
    data_nat = pd.DataFrame(
        {'Casi': casi, 'Tamponi': tamponi, 'Ospedalizzati': hospital, 'TI': icu, 'Deceduti': deaths}, index=[giorni])
    data_nat.to_csv('data/national_data.csv', mode='a', header=False)

    df_loc = arg[1]
    casi0 = []
    for prov in provinces:
        casi0.append(df_loc["totale_casi"][df_loc["denominazione_provincia"] == prov].values[0])

    casiprov = np.array(casi0)
    data_loc = pd.DataFrame([casiprov], columns=provinces, index=[giorni])
    data_loc.to_csv('data/local_data.csv', mode='a', header=False)
    return True


def compute_rollingmean(quantity):
    D = pd.Series(quantity, np.arange(len(quantity)))
    d_mva = D.rolling(7).mean()
    average = []
    for i in range(len(d_mva.array)):
        average.append(d_mva.array[i])
    return average


def get_delta(mylist):
    return np.array([mylist[i + 1] - mylist[i] for i in range(len(mylist) - 1)])

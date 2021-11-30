import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from urllib.error import HTTPError
from tqdm import tqdm
import sys

def scrape_data_italy(day):
  
    # Convert each day to the correct argument
    argument = day.strftime("%Y%m%d")

    # Link to the appropriate csv with the info
    url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-'+argument+'.csv'
    df = pd.read_csv(url, index_col=0)

    return df

def scrape_data_local(day):
 
    # Convert each day to the correct argument
    argument = day.strftime("%Y%m%d")
    
    # Link to the appropriate csv with the info
    url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-'+argument+'.csv'
    df = pd.read_csv(url, index_col=0)
    
    return df


start = datetime.strptime('01/03/2020', "%d/%m/%Y").date()
stop = datetime.today().date()

# Array of days
t = np.arange(start, stop+timedelta(days=1), timedelta(days=1)).astype(datetime)

# National part
'''
giorni, casi, tamponi, icu, hospital = [],[],[],[],[]
for day in tqdm(t):
    try:
        df = scrape_data_italy(day)
    except HTTPError as err:
        if err.code == 404:
            print('Non existent file for day',day.date(),'- skipping it.')
            continue
        else:
            raise
    
    giorni.append(day.strftime("%d/%m/%Y"))
    casi.append(np.sum(df["totale_casi"]))
    tamponi.append(np.sum(df["tamponi"]))
    hospital.append(np.sum(df["ricoverati_con_sintomi"]))
    icu.append(np.sum(df["terapia_intensiva"]))

data = pd.DataFrame({'Casi': casi, 'Tamponi': tamponi, 'Ospedalizzati': hospital, 'TI': icu}, index=giorni)
data.to_csv('data/national_data.csv')
'''
# Local part
province=[
    "L'Aquila","Teramo","Pescara","Chieti",
    "Potenza","Matera",
    "Cosenza","Catanzaro","Reggio di Calabria","Crotone","Vibo Valentia",
    "Caserta","Benevento","Napoli","Avellino","Salerno",
    "Piacenza","Parma","Reggio nell'Emilia","Modena","Bologna","Ferrara","Ravenna","Forlì-Cesena","Rimini",
    "Udine","Gorizia","Trieste","Pordenone",
    "Viterbo","Rieti","Roma","Latina","Frosinone",
    "Imperia","Genova","Savona","La Spezia",
    "Varese","Como","Sondrio","Milano","Bergamo","Brescia","Pavia","Cremona","Mantova","Lecco","Lodi","Monza e della Brianza",
    "Pesaro e Urbino","Ancona","Macerata","Ascoli Piceno","Fermo",
    "Campobasso","Isernia",
    "Trento","Bolzano",
    "Torino","Vercelli","Novara","Cuneo","Asti","Alessandria","Biella","Verbano-Cusio-Ossola",
    "Foggia","Bari","Taranto","Brindisi","Lecce","Barletta-Andria-Trani",
    "Sassari","Nuoro","Cagliari","Oristano","Sud Sardegna",
    "Trapani","Palermo","Messina","Agrigento","Caltanissetta","Enna","Catania","Ragusa","Siracusa",
    "Massa Carrara","Lucca","Pistoia","Firenze","Livorno","Pisa","Arezzo","Siena","Grosseto","Prato",
    "Perugia","Terni",
    "Aosta",
    "Verona","Vicenza","Belluno","Treviso","Venezia","Padova","Rovigo"
]

giorni, casi, nomi = [],[],[]
for day in tqdm(t):
    try:
        df = scrape_data_local(day)
    except HTTPError as err:
        if err.code == 404:
            print('Non existent file for day',day.date(),'- skipping it.')
            continue
        else:
            raise
    
    giorni.append(day.strftime("%d/%m/%Y"))

    casi0 = []
    for prov in province:
        casi0.append(df["totale_casi"][df["denominazione_provincia"] == prov].values[0])

    casi.append(casi0)

nomi.append(province)
nomi = np.array(nomi)

data = pd.DataFrame(casi, columns=province, index=giorni)
data.to_csv('data/local_data_prova.csv')
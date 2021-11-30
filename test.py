import pandas as pd 
from urllib.error import HTTPError
from datetime import datetime, timedelta
import sys
import numpy as np

def add_day(day):

    # Convert each day to the correct argument
    argument = day.strftime("%Y%m%d")
    
    # Link to the appropriate csv with the info
    url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-'+argument+'.csv'
    url2 = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-'+argument+'.csv'
    try:
        df_loc = pd.read_csv(url, index_col=0)
        df_nat = pd.read_csv(url2, index_col=0)
    except HTTPError as err:
        if err.code == 404:
            print('Non existent file (yet) for day',day,'- skipping it.')
            return 0
        else:
            raise
    
    return [df_nat, df_loc]

def append_lines(day,arg):
    giorni = day.strftime("%d/%m/%Y")

    df_nat = arg[0]
    casi = np.sum(df_nat["totale_casi"])
    tamponi = np.sum(df_nat["tamponi"])
    hospital = np.sum(df_nat["ricoverati_con_sintomi"])
    icu = np.sum(df_nat["terapia_intensiva"])
    data_nat = pd.DataFrame({'Casi': casi, 'Tamponi': tamponi, 'Ospedalizzati': hospital, 'TI': icu}, index=[giorni])
    data_nat.to_csv('data/national_data.csv', mode='a', header=False)

    df_loc = arg[1]
    casi0 = []
    for prov in province:
        casi0.append(df_loc["totale_casi"][df_loc["denominazione_provincia"] == prov].values[0])

    casiprov = np.array(casi0)
    data_loc = pd.DataFrame([casiprov], columns=province, index=[giorni])
    data_loc.to_csv('data/local_data.csv', mode='a', header=False)
    return True

start = '10/11/2021'
stop = '30/11/2021'
where = 'Varese'


giorni = [start, stop]

giorni2 = list([datetime.strptime(giorno, "%d/%m/%Y").date() for giorno in giorni])
print(giorni2)
sys.exit()

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

local_data = pd.read_csv('data/local_data.csv')
local_data = local_data.set_index(local_data.columns[0])

natio_data = pd.read_csv('data/national_data.csv')
natio_data = natio_data.set_index(natio_data.columns[0])

# Check the dates
if len(local_data[local_data.index == stop]) == 0:
    delta = datetime.strptime(stop, "%d/%m/%Y").date() - datetime.strptime(local_data.index[-1], "%d/%m/%Y").date()
    print(delta.days,'days to add.')
    # Array of days
    t = np.arange(datetime.strptime(local_data.index[-1], "%d/%m/%Y").date()+timedelta(days=1), datetime.strptime(stop, "%d/%m/%Y").date()+timedelta(days=1), timedelta(days=1)).astype(datetime)
    
    for i,day in enumerate(t):
        
        # Put here the addition to the csv file 
        result = add_day(day)
        if result == 0:
            stop = local_data.index[-1]
            break
        else:
            print('Sto aggiungendo...')
            append_lines(day,result)
    
    print('Fatto!')
    # reload data
    local_data = pd.read_csv('data/local_data.csv')
    local_data = local_data.set_index(local_data.columns[0])

    natio_data = pd.read_csv('data/national_data.csv')
    natio_data = natio_data.set_index(natio_data.columns[0])

if len(local_data[local_data.index == start]) == 0:
    if datetime.strptime(start, "%d/%m/%Y").date() < datetime.now().date():
        start = '01/03/2020'
    else:
        start = datetime.now().date()-timedelta(days=30)
        start = start.strftime("%d/%m/%Y")

df0 = local_data.loc[start:stop][where]
#print(df0.head())
#print(local_data.loc[start:stop][where])
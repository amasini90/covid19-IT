import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pandas.plotting import register_matplotlib_converters
from urllib.error import HTTPError
register_matplotlib_converters()

# syntax python update_covid_it.py from to (in yyyymmdd)
# or python update_covid_it.py to (by default, plot the 30 days prior to the input)
# Input either 'latest' or 'yyyymmdd' for a given day

# Check if there is a start and stop or just a stop
if len(sys.argv) < 2:
	print('No arguments given. Please input either an end date in format yyyymmdd, or a range of dates.')
	sys.exit()
elif len(sys.argv) == 2: # If there is just a stop, default to the 30 days before today or given date
    if sys.argv[1] == 'latest':
        date = datetime.now().date()
        today = date.strftime("%Y%m%d")
        stop = datetime.strptime(today, '%Y%m%d').date()
    else:
        stop = datetime.strptime(sys.argv[1], '%Y%m%d').date() # convert from yyyymmdd string to date
    start = stop-timedelta(days=30)
elif len(sys.argv) > 2: # If there are both a start and stop, the start is the first argument
    start = datetime.strptime(sys.argv[1], '%Y%m%d').date()
    if sys.argv[2] == 'latest':
        date = datetime.now().date()
        today = date.strftime("%Y%m%d")
        stop = datetime.strptime(today, '%Y%m%d').date()
    else:
        stop = datetime.strptime(sys.argv[2], '%Y%m%d').date()

# Array of days
t = np.arange(start, stop+timedelta(days=1), timedelta(days=1)).astype(datetime)

giorni, casi, tamponi = [],[],[]
icu, hospital = [],[]
for day in t:
    
    # Convert each day to the correct argument
    argument = day.strftime("%Y%m%d")
    
    # Link to the appropriate csv with the info
    url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-'+argument+'.csv'
    
    try:
        df = pd.read_csv(url, index_col=0)
    except HTTPError as err:
        if err.code == 404:
            print('Non existent file for day',day.date(),'- skipping it.')
            continue
        else:
            raise
    
    giorni.append(day)
        
    casi.append(np.sum(df["totale_casi"]))
    tamponi.append(np.sum(df["tamponi"]))

    hospital.append(np.sum(df["ricoverati_con_sintomi"]))
    icu.append(np.sum(df["terapia_intensiva"]))

giorni = np.array(giorni)

# Compute increments of interest
delta_casi = np.array(list(casi[i+1]-casi[i] for i in range(len(casi)-1)))
delta_tamponi = np.array(list(tamponi[i+1]-tamponi[i] for i in range(len(tamponi)-1)))
ratio = (delta_casi/delta_tamponi)*100.

delta_icu = np.array(list(icu[i+1]-icu[i] for i in range(len(icu)-1)))
delta_hospital = np.array(list(hospital[i+1]-hospital[i] for i in range(len(hospital)-1)))

# Compute the rolling mean at 7 days
D = pd.Series(ratio, np.arange(len(ratio)))
d_mva = D.rolling(7).mean()
average = []
for i in range(len(d_mva.array)):
    average.append(d_mva.array[i])

# Plot the results
fig, ax = plt.subplots(nrows=2, figsize=[8,5], sharex=True)
ax[0].plot(giorni[1:], ratio, color='lime', linewidth=2)
ax[0].plot(giorni[1:], average, color='k', linestyle='dashed', label='Media mobile a 7 giorni')
ax[0].legend()
ax[0].set_ylim(bottom=0)
ax[0].set_ylabel('Incremento casi (%)')
ax[0].tick_params(direction='in', right=True, top=True)

ax[1].plot(giorni[1:], delta_icu, color='tomato',label='ICU')
ax[1].plot(giorni[1:], delta_hospital, color='royalblue',label='Ricoverati')
ax[1].legend()
ax[1].set_xlabel('Data')
ax[1].set_ylabel('Incremento ospedalizzati')
ax[1].tick_params(direction='in', right=True, top=True)
plt.xticks(rotation=90)
plt.tight_layout()
plt.subplots_adjust(hspace=0)
plt.show()
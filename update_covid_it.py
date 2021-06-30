import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# syntax python update_covid_it.py from to (in yyyymmdd)
# or python update_covid_it.py to (by default, plot the 30 days prior to the input)
# Input either 'latest' or 'yyyymmdd' for a given day

# Check if user gave a start and stop, or just a stop date
# If there is just a stop, default to the 30 days before today or given date
# If there are both a start and stop, the start is the first argument
if len(sys.argv) == 2: 
    if sys.argv[1] == 'latest':
        date = datetime.now().date()
        today = date.strftime("%Y%m%d")
        stop = datetime.strptime(today, '%Y%m%d').date()
    else:
        stop = datetime.strptime(sys.argv[1], '%Y%m%d').date() # convert from yyyymmdd string to date
    start = stop-timedelta(days=30)
else: 
    start = datetime.strptime(sys.argv[1], '%Y%m%d').date()
    if sys.argv[2] == 'latest':
        date = datetime.now().date()
        today = date.strftime("%Y%m%d")
        stop = datetime.strptime(today, '%Y%m%d').date()
    else:
        stop = datetime.strptime(sys.argv[2], '%Y%m%d').date()

# Array of days between start and stop
t = np.arange(start, stop+timedelta(days=1), timedelta(days=1)).astype(datetime)

casi, tamponi = [],[]
for day in t:

    # Convert each day to the correct argument
    argument = day.strftime("%Y%m%d")
    
    # Link to the appropriate csv with the info
    url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-'+argument+'.csv'

    df = pd.read_csv(url, index_col=0)
    
    # Register the total numnber of cases and tests for the given day
    casi.append(np.sum(df["totale_casi"]))
    tamponi.append(np.sum(df["tamponi"]))

# Compute the increment in cases and tests from day before, and their ratio
delta_casi = np.array(list(casi[i+1]-casi[i] for i in range(len(casi)-1)))
delta_tamponi = np.array(list(tamponi[i+1]-tamponi[i] for i in range(len(tamponi)-1)))
ratio = (delta_casi/delta_tamponi)*100.

# Compute weekly rolling mean 
D = pd.Series(ratio, np.arange(len(ratio)))
d_mva = D.rolling(7).mean()
average = []
for i in range(len(d_mva.array)):
    average.append(d_mva.array[i])

# Manage the ticklabels to look prettier
ticklabels = [x.strftime("%Y%m%d")[-4:] for x in t[1:]]
newlab = [x[-2:]+'-'+x[:2] for x in ticklabels]

# Plot the result
fig, ax = plt.subplots()
ax.plot(t[1:], ratio, color='lime', linewidth=2)
ax.plot(t[1:], average, color='k', linestyle='dashed')
ax.set_xlabel('Data')
ax.set_ylabel('Incremento percentuale di casi (%)')
ax.set_xticks(t[1:])
ax.set_xticklabels(newlab)
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

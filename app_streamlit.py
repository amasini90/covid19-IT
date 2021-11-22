import streamlit as st
from streamlit import legacy_caching
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pandas.plotting import register_matplotlib_converters
from urllib.error import HTTPError
import matplotlib.dates as mdates
from numerize import numerize
from matplotlib import rc
from PIL import Image
import plotly.figure_factory as ff
import plotly.graph_objects as go
register_matplotlib_converters()
myFmt = mdates.DateFormatter('%d/%m')
font = {'family' : 'serif'}
rc('font', **font)

def get_dates(args=['latest']):
    
    if len(args) < 1:
        print('No arguments given. Please input either an end date in format dd/mm/yyyy, or a range of dates.')
        raise ValueError

    elif len(args) == 1: # If there is just a stop, default to the 30 days before today or given date
        if args[0] == 'latest':
            date = datetime.now().date()
            today = date.strftime("%d/%m/%Y")
            stop = datetime.strptime(today, "%d/%m/%Y").date()
        else:
            stop = datetime.strptime(args[0], "%d/%m/%Y").date() # convert from yyyymmdd string to date
        start = stop-timedelta(days=30)
    elif len(args) > 1: # If there are both a start and stop, the start is the first argument
        start = datetime.strptime(args[0], "%d/%m/%Y").date()
        if args[1] == 'latest':
            date = datetime.now().date()
            today = date.strftime("%d/%m/%Y")
            stop = datetime.strptime(today, "%d/%m/%Y").date()
        else:
            stop = datetime.strptime(args[1], "%d/%m/%Y").date()

    return (start,stop)

def mysign(inp):
    if np.sign(inp) > 0:
        return '+'
    elif np.sign(inp) < 0:
        return '-'
    else:
        return ''

@st.cache(suppress_st_warning=True, show_spinner=False)
def load_data_italy():
  
  # Array of days
  t = np.arange(start, stop+timedelta(days=1), timedelta(days=1)).astype(datetime)
  
  giorni, casi, tamponi = [],[],[]
  icu, hospital = [],[]
  progress_bar = st.progress(0)
  for i,day in enumerate(t):

      progress_bar.progress((i+1)/len(t))
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
  
  return [giorni,casi,tamponi,hospital,icu]

@st.cache(suppress_st_warning=True, show_spinner=False)
def load_data_local(where='Varese'):

    # Array of days
    t = np.arange(start, stop+timedelta(days=1), timedelta(days=1)).astype(datetime)
  
    giorni, casi = [],[]
    progress_bar = st.progress(0)
    for i,day in enumerate(t):

        progress_bar.progress((i+1)/len(t))
 
        # Convert each day to the correct argument
        argument = day.strftime("%Y%m%d")
      
        # Link to the appropriate csv with the info
        url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-'+argument+'.csv'
      
        try:
           df = pd.read_csv(url, index_col=0)
        except HTTPError as err:
           if err.code == 404:
               print('Non existent file for day',day.date(),'- skipping it.')
               continue
           else:
               raise
      
        giorni.append(day)
        casi.append(df[df['denominazione_provincia']==where]["totale_casi"].values[0])
 
    giorni = np.array(giorni)
  
    return [giorni,casi]

def set_dark(ax):
    ax.xaxis.label.set_color(switch)
    ax.yaxis.label.set_color(switch)
    ax.tick_params(axis='both', colors=switch)
    ax.set_facecolor('none')

def compute_rollingmean(quantity):
    D = pd.Series(quantity, np.arange(len(quantity)))
    d_mva = D.rolling(7).mean()
    average = []
    for i in range(len(d_mva.array)):
        average.append(d_mva.array[i])
    return average

# Page configuration
im = Image.open("virus.ico")
st.set_page_config(page_title="Covid19 in Italia", page_icon=im)

# Title of the App
st.title('Covid19 in Italia')
st.subheader('by A. Masini')

#if st.config.get_option('theme.base') == 'dark':
#    dark=True

if st.button('Aggiorna'):
    legacy_caching.clear_cache()

# Get start and stop dates - defaults to previous 30 days
start,stop = st.date_input('Periodo da visualizzare (default: ultimi 30 giorni)', value=(datetime.now().date()-timedelta(days=30),datetime.now().date()), min_value=datetime.strptime('01/03/2020', "%d/%m/%Y").date(), max_value=None, key=None, help=None, on_change=None, args=None, kwargs=None)

# Get the location for regional sub-area
where = st.text_input('Provincia da visualizzare (default: Varese)', value="Varese", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None)

# Scrape national data from public GitHub repo
with st.spinner('Attendere...'):
    giorni,casi,tamponi,hospital,icu = load_data_italy()

# Compute increments of interest
delta_casi = np.array(list(casi[i+1]-casi[i] for i in range(len(casi)-1)))
delta_tamponi = np.array(list(tamponi[i+1]-tamponi[i] for i in range(len(tamponi)-1)))
ratio = (delta_casi/delta_tamponi)*100.

delta_icu = np.array(list(icu[i+1]-icu[i] for i in range(len(icu)-1)))
delta_hospital = np.array(list(hospital[i+1]-hospital[i] for i in range(len(hospital)-1)))

perc_delta_icu = 100*delta_icu/icu[1:]
perc_delta_hospital = 100*delta_hospital/hospital[1:]

# Compute the rolling mean at 7 days
average = compute_rollingmean(ratio)

st.subheader('Percentuale di tamponi positivi e variazione ospedalizzazioni')

# Show the metrics of the last day, only if last day is today
if stop == datetime.now().date():
    giorno = giorni[-1].strftime("%d/%m/%Y")
    st.markdown(f'Numeri pi&ugrave recenti, relativi al '+giorno)
    col1, col2, col3 = st.columns(3)
    col1.metric("Casi", mysign(delta_casi[-1])+str(delta_casi[-1]), str(round(ratio[-1],1))+'%', delta_color="inverse")
    col2.metric("Ospedalizzati", mysign(delta_hospital[-1])+str(delta_hospital[-1]), str(round(perc_delta_hospital[-1],1))+'%', delta_color="inverse")
    col3.metric("Terapie Intensive", mysign(delta_icu[-1])+str(delta_icu[-1]), str(round(perc_delta_icu[-1],1))+'%', delta_color="inverse")

#my_data = pd.DataFrame({'Dati':ratio, 'Media mobile':average}, index=giorni[1:])
#import plotly.express as px
#fig = px.line(my_data, labels={'x':'Data','y':'Incremento'})
#st.plotly_chart(fig, use_container_width=True)

# Plot national cases
fig, ax = plt.subplots(nrows=2)
ax[0].plot(giorni[1:], ratio, color='lime', linewidth=2)
ax[0].plot(giorni[1:], average, color='k', linestyle='dashed', label='Media mobile a 7 giorni')
ax[0].legend(loc='best')
ax[0].set_ylim(bottom=0)
ax[0].set_ylabel('Incremento casi (%)',fontsize=12)
ax[0].tick_params(direction='in', right=True, top=True)
ax[0].xaxis.set_major_formatter(myFmt)
ax[0].xaxis.set_ticks_position('top')

ax[1].plot(giorni[1:], perc_delta_icu, color='tomato',label='Terapie intensive')
ax[1].plot(giorni[1:], perc_delta_hospital, color='royalblue',label='Ricoverati')
ax[1].axhline(y=0, color='k', linewidth=0.8)
ax[1].annotate("", xy=(0.02, 0.25), xytext=(0.02, 0.5), xycoords='axes fraction', arrowprops=dict(arrowstyle="->", color='limegreen', linewidth=2))
ax[1].annotate("", xy=(0.02, 0.75), xytext=(0.02, 0.5), xycoords='axes fraction', arrowprops=dict(arrowstyle="->", color='r', linewidth=2))
ax[1].legend(loc='best')
ax[1].set_xlabel('Data',fontsize=12)
ax[1].set_ylabel('Variazione (%)',fontsize=12)
# get y-axis limits of the plot
low, high = ax[1].get_ylim()
# find the new limits
bound = max(abs(low), abs(high))
# set new limits
ax[1].set_ylim(-bound, bound)
ax[1].tick_params(axis='both', direction='in', left=True, right=True, bottom=True, top=True)
ax[1].xaxis.set_major_formatter(myFmt)
plt.setp(ax[0].xaxis.get_majorticklabels(), rotation=35)
plt.setp(ax[1].xaxis.get_majorticklabels(), rotation=35)
plt.subplots_adjust(hspace=0)

#st.pyplot(fig)
st.pyplot(fig)

st.subheader('Casi positivi a '+str(where))

# Scrape local data from public GitHub repo
with st.spinner('Attendere...'):
    giorni,casi = load_data_local(where)

# Compute increments of interest
delta_casi = np.array(list(casi[i+1]-casi[i] for i in range(len(casi)-1)))

# Compute the rolling mean at 7 days
average = compute_rollingmean(delta_casi)

# Show the metrics of the last day, only if last day is today
if stop == datetime.now().date():
    giorno = giorni[-1].strftime("%d/%m/%Y")
    st.markdown(f'Numeri pi&ugrave recenti, relativi al '+giorno)
    st.metric("Casi", numerize.numerize(int(casi[-1]),1), mysign(delta_casi[-1])+str(delta_casi[-1]), delta_color="inverse")

# Plot regional cases
fig, ax = plt.subplots(nrows=1)
ax.plot(giorni[1:], delta_casi, color='lime', linewidth=2)
ax.plot(giorni[1:], average, color='k', linestyle='dashed', label='Media mobile a 7 giorni')
ax.legend(loc='best')
ax.set_ylim(bottom=0)
ax.set_ylabel('Incremento casi', fontsize=12)
ax.set_xlabel('Data', fontsize=12)
ax.tick_params(direction='in', right=True, top=True)
ax.xaxis.set_major_formatter(myFmt)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=35)
plt.subplots_adjust(hspace=0)

st.pyplot(fig)
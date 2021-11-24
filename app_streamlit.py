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
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

st.subheader('Percentuale di tamponi positivi e variazione ospedalizzazioni in Italia')

# Show the metrics of the last day, only if last day is today
if stop == datetime.now().date():
    giorno = giorni[-1].strftime("%d/%m/%Y")
    st.markdown(f'Numeri pi&ugrave recenti, relativi al '+giorno)
    col1, col2, col3 = st.columns(3)
    col1.metric("Casi", mysign(delta_casi[-1])+str(delta_casi[-1]), str(round(ratio[-1],1))+'%', delta_color="inverse")
    col2.metric("Ospedalizzati", mysign(delta_hospital[-1])+str(delta_hospital[-1]), str(round(perc_delta_hospital[-1],1))+'%', delta_color="inverse")
    col3.metric("Terapie Intensive", mysign(delta_icu[-1])+str(delta_icu[-1]), str(round(perc_delta_icu[-1],1))+'%', delta_color="inverse")

# Plot the national cases
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)

fig.append_trace(go.Scatter(
    x=giorni[1:], 
    y=ratio,
    mode='lines', 
    line = dict(color='lime', width=2), 
    showlegend=True, 
    name='Tamponi positivi', 
    legendgroup='1'
    ), 
    row=1, 
    col=1
)

fig.append_trace(go.Scatter(
    x=giorni[1:], 
    y=average,
    mode='lines',
    line = dict(color='orange', width=4, dash='dash'), 
    name='Media mobile a 7 giorni', 
    legendgroup='2'
    ), 
    row=1, 
    col=1
)

fig.append_trace(go.Scatter(
    x=giorni[1:], 
    y=perc_delta_hospital,
    mode='lines', 
    line = dict(color='royalblue', width=2),
    name = 'Ricoverati',
    legendgroup='3'
    ),
    row=2, 
    col=1
)

fig.append_trace(go.Scatter(
    x=giorni[1:], 
    y=perc_delta_icu,
    mode='lines', 
    line = dict(color='tomato', width=2),
    name = 'Terapie intensive', 
    legendgroup='4'
    ), 
    row=2, 
    col=1
)

fig.update_yaxes(title_text="Incremento casi (%)", row=1, col=1)
fig.update_yaxes(title_text="Variazione (%)", row=2, col=1)
fig.update_xaxes(title_text="Data", row=2, col=1)

fig.update_layout(
    height=600, width=600,
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
    font = dict(size = 12)
    ),
    #legend_tracegroupgap = 180,
    font=dict(size=15)
)

st.plotly_chart(fig, use_container_width=True)

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

# Plot the local cases
fig = go.Figure()

fig.add_trace(go.Scatter(x=giorni[1:], y=delta_casi,mode='lines', line = dict(color='lime', width=2), showlegend=True, name='Tamponi positivi', legendgroup='1'))
fig.add_trace(go.Scatter(x=giorni[1:], y=average,mode='lines',line = dict(color='orange', width=4, dash='dash'), name='Media mobile a 7 giorni', legendgroup='2'))

fig.update_yaxes(title_text="Incremento casi")
fig.update_xaxes(title_text="Data")

fig.update_layout(
    height=600, width=600,
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
    font = dict(size = 12)
    ),
    #legend_tracegroupgap = 180,
    font=dict(size=15)
)

st.plotly_chart(fig, use_container_width=True)
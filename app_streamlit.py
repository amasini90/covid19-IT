import streamlit as st
from streamlit import legacy_caching
import numpy as np
from datetime import datetime, timedelta
from PIL import Image
import util, analysis

local_data_path = 'data/local_data.csv'
national_data_path = 'data/national_data.csv'

def date_callback(start,stop):
    st.session_state['inp_start'] = start
    st.session_state['inp_stop'] = stop

def main():
    # Page configuration
    im = Image.open("virus.ico")
    st.set_page_config(page_title="Covid19 in Italia", page_icon=im)

    # Title of the App
    st.title('Covid19 in Italia')

    if st.button('Aggiorna'):
        legacy_caching.clear_cache()
    
    ############################
    # Get start and stop dates - defaults to previous 30 days
    # Initialization in Session State
    if 'inp_start' not in st.session_state:
        input_start = datetime.now().date()-timedelta(days=30)
        input_stop = datetime.now().date()
        st.session_state['inp_start'] = input_start
        st.session_state['inp_stop'] = input_stop
    else:
        input_start = st.session_state['inp_start']
        input_stop = st.session_state['inp_stop']

    #try:
    #    input_start, input_stop = st.date_input('Periodo da visualizzare (default: ultimi 30 giorni)',
    #                                        value=(input_start.strftime("%d/%m/%Y"), input_stop.strftime("%d/%m/%Y")),
    #                                        min_value=datetime.strptime('01/03/2020', "%d/%m/%Y").date(),
    #                                        max_value=datetime.now().date(),
    #                                        key=None, help=None, on_change=date_callback(), args=(input_start,input_stop), kwargs=None)
    #except:
    #   pass

    #col1,col2 = st.columns(2)
    #col3,col4 = st.columns(2)
    delta = datetime.now().date()-datetime.strptime('01/03/2020',"%d/%m/%Y").date()
    for what,when in zip(['Ultimo mese','Ultimi 3 mesi','Ultimi 6 mesi','Ultimo anno',"Dall'inizio"],[30,90,180,365,delta.days]):
        if st.button(what):
            input_start = datetime.now().date()-timedelta(days=when)
            input_stop = datetime.now().date()

            st.session_state['inp_start'] = input_start
            st.session_state['inp_stop'] = input_stop

    # Load the data
    # TODO should first download and update this data and then read it
    local_data = util.get_data(local_data_path)
    national_data = util.get_data(national_data_path)
    last_date = national_data.index[-1]
    # Scrape missing national and local data from public GitHub repo, if available
    with st.spinner('Attendere...'):
        start_date = input_start.strftime("%d/%m/%Y")
        stop_date = input_stop.strftime("%d/%m/%Y")

        # Check the dates
        if len(national_data[national_data.index == stop_date]) == 0:
            # Array of days
            t = np.arange(datetime.strptime(national_data.index[-1], "%d/%m/%Y").date()+timedelta(days=1),
                          datetime.strptime(stop_date, "%d/%m/%Y").date()+timedelta(days=1),
                          timedelta(days=1)).astype(datetime)

            for day in t:
                result = util.add_day(day)

                if result == 0:
                    stop_date = national_data.index[-1]
                    break
                else:
                    util.append_lines(day, result)

            # Reload data
            local_data = util.get_data(local_data_path)
            national_data = util.get_data(national_data_path)

        if len(local_data[local_data.index == start_date]) == 0:
            if datetime.strptime(start_date, "%d/%m/%Y").date() < datetime.now().date():
                start_date = '01/03/2020'
            else:
                start_date = datetime.now().date()-timedelta(days=30)
                start_date = start_date.strftime("%d/%m/%Y")
    
    st.session_state['inp_start'] = datetime.strptime(start_date, "%d/%m/%Y").date()
    st.session_state['inp_stop'] = datetime.strptime(stop_date, "%d/%m/%Y").date()
    analysis.show_national_cases(national_data, st.session_state.inp_start.strftime("%d/%m/%Y"), st.session_state.inp_stop.strftime("%d/%m/%Y"), last_date)
    analysis.show_local_cases(local_data, st.session_state.inp_start.strftime("%d/%m/%Y"), st.session_state.inp_stop.strftime("%d/%m/%Y"), last_date)

    # Footer
    st.write('Fonte dei dati: Presidenza del Consiglio dei Ministri - Dipartimento della Protezione Civile')
    st.write('Fonte popolazione province: https://www.tuttitalia.it/province/')
    #col1, col2 = st.columns([2,1])
    link = '[Alberto Masini](http://www.linkedin.com/in/almasini/)'
    st.write('Autore: '+link+' (2021); Licenza CC BY-NC-ND 3.0')
    st.image('by-nc-nd.eu.png', width=60)

if __name__ == '__main__':
    main()
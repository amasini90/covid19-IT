import streamlit as st
from datetime import datetime, timedelta
from PIL import Image
import util
import analysis
import update

local_data_path = 'data/local_data.csv'
national_data_path = 'data/national_data.csv'


def main():
    # Page configuration
    im = Image.open("virus.ico")
    st.set_page_config(page_title="Covid19 in Italia", page_icon=im)

    # Title of the App
    st.title('Covid19 in Italia')
    st.markdown("NOTA: Dall'8 Gennaio 2025 non sono più stati pubblicati dati relativi alla pandemia di Covid19 in Italia.")

    # Startup - update CSVs with most up-to-date data
    #update.update_at_startup()  No more data published from January 8th 2025, no need to do that again

    # Read data
    national_data = util.get_data(national_data_path)
    local_data = util.get_data(local_data_path)
    last_date = national_data.index[-1]
    last_date_dt = datetime.strptime(last_date, "%d/%m/%Y").date()

    ############################
    # Get start and stop dates - defaults to previous 365 days from last date in data
    # Initialization in Session State
    if 'inp_start' not in st.session_state:
        input_start = last_date_dt - timedelta(days=365)
        input_stop = last_date_dt
        st.session_state['inp_start'] = input_start
        st.session_state['inp_stop'] = input_stop

    from_start = last_date_dt - datetime.strptime('01/03/2020', "%d/%m/%Y").date()
    for what, when in zip(['Ultimo anno', "Dall'inizio"],
                          [365, from_start.days]):
        if st.button(what):
            input_start = last_date_dt - timedelta(days=when)
            input_stop = last_date_dt

            st.session_state['inp_start'] = input_start
            st.session_state['inp_stop'] = input_stop

    # Plot results
    analysis.show_national_cases(national_data, st.session_state.inp_start.strftime("%d/%m/%Y"),last_date, last_date)
    analysis.show_local_cases(local_data, st.session_state.inp_start.strftime("%d/%m/%Y"),last_date, last_date)

    # Footer
    st.write('Fonte dei dati: Presidenza del Consiglio dei Ministri - Dipartimento della Protezione Civile')
    st.write('Fonte popolazione province: https://www.tuttitalia.it/province/')
    # col1, col2 = st.columns([2,1])
    link = '[Alberto Masini](http://www.linkedin.com/in/almasini/)'
    st.write('Autore: ' + link + ' (2021); Licenza CC BY-NC-ND 3.0')
    st.image('by-nc-nd.eu.png', width=60)


if __name__ == '__main__':
    main()

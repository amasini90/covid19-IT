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

    # Startup - update CSVs with most up-to-date data
    update.update_at_startup()

    # Read data
    national_data = util.get_data(national_data_path)
    local_data = util.get_data(local_data_path)
    last_date = national_data.index[-1]

    ############################
    # Get start and stop dates - defaults to previous 30 days
    # Initialization in Session State
    if 'inp_start' not in st.session_state:
        input_start = datetime.now().date() - timedelta(days=30)
        input_stop = datetime.now().date()
        st.session_state['inp_start'] = input_start
        st.session_state['inp_stop'] = input_stop

    from_start = datetime.now().date() - datetime.strptime('01/03/2020', "%d/%m/%Y").date()
    for what, when in zip(['Ultimo mese', 'Ultimi 3 mesi', 'Ultimi 6 mesi', 'Ultimo anno', "Dall'inizio"],
                          [30, 90, 180, 365, from_start.days]):
        if st.button(what):
            input_start = datetime.now().date() - timedelta(days=when)
            input_stop = datetime.now().date()

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

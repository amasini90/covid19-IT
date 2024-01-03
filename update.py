import streamlit as st
import numpy as np
from datetime import datetime, timedelta
import util

local_data_path = 'data/local_data.csv'
national_data_path = 'data/national_data.csv'


def update_at_startup():
    # Read data to find the last date
    national_data = util.get_data(national_data_path)
    last_date = national_data.index[-1]

    today = datetime.now().date().strftime("%d/%m/%Y")

    # Scrape missing national and local data from public GitHub repo, if available
    if today not in national_data.index:
        with st.spinner('Attendere: cerco i dati più recenti...'):
            # Array of days to be scanned
            t = np.arange(datetime.strptime(last_date, "%d/%m/%Y").date() + timedelta(days=1),
                          datetime.strptime(today, "%d/%m/%Y").date() + timedelta(days=1),
                          timedelta(days=1)).astype(datetime)

            # For each missing day, add the line in the csv
            for day in t:
                result = util.add_day(day)
                if result == 0:
                    break
                else:
                    util.append_lines(day, result)

    return

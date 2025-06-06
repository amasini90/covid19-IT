import streamlit as st
from datetime import datetime
import util, plot
from numerize import numerize
import pandas as pd


def show_national_cases(national_data, start_date, stop_date, last_date):
    st.subheader('Situazione a livello nazionale')

    national_data_df = national_data.loc[start_date:stop_date]
    days = national_data_df.index.values
    cases = national_data_df["Casi"].values
    tamponi = national_data_df["Tamponi"].values
    hospital = national_data_df["Ospedalizzati"].values
    icu = national_data_df["TI"].values
    deaths = national_data_df["Deceduti"].values

    # Compute increments of interest
    delta_cases = util.get_delta(cases)
    delta_tamponi = util.get_delta(tamponi)
    ratio = (delta_cases / delta_tamponi) * 100.

    delta_icu = util.get_delta(icu)
    delta_hospital = util.get_delta(hospital)

    perc_delta_icu = 100 * delta_icu / icu[1:]
    perc_delta_hospital = 100 * delta_hospital / hospital[1:]

    delta_deaths = util.get_delta(deaths)

    # Compute the rolling means at 7 days
    average = util.compute_rollingmean(ratio)
    average_hosp = util.compute_rollingmean(delta_hospital)
    average_icu = util.compute_rollingmean(delta_icu)
    average_deaths = util.compute_rollingmean(delta_deaths)

    # Show the metrics of the last day, only if last day is today
    if stop_date == last_date:
        last_day = days[-1]
        st.markdown(f'Dati più recenti, relativi al ' + last_day)

        st.metric("Casi", numerize.numerize(int(cases[-1]), 2),
                  util.mysign(delta_cases[-1]) + str(delta_cases[-1]) + ' (' + str(round(ratio[-1], 1)) + '%)',
                  delta_color="inverse")
        if delta_hospital[-1] != 0:
            st.metric("Ospedalizzati", str(hospital[-1]),
                      util.mysign(delta_hospital[-1]) + str(delta_hospital[-1]) + ' (' + str(
                          round(perc_delta_hospital[-1], 1)) + '%)', delta_color="inverse")
        else:
            st.metric("Ospedalizzati", str(hospital[-1]), delta=None, delta_color="off")
        if delta_icu[-1] != 0:
            st.metric("Terapie Intensive", str(icu[-1]),
                      util.mysign(delta_icu[-1]) + str(delta_icu[-1]) + ' (' + str(round(perc_delta_icu[-1], 1)) + '%)',
                      delta_color="inverse")
        else:
            st.metric("Terapie Intensive", str(icu[-1]), delta=None, delta_color="off")
        st.metric("Deceduti", str(deaths[-1]), util.mysign(delta_deaths[-1]) + str(delta_deaths[-1]),
                  delta_color="inverse")

    giorni0 = [datetime.strptime(giorno, "%d/%m/%Y").date() for giorno in days]

    # Plot the national cases
    fig = plot.get_national_cases_fig(giorni0, ratio, average, delta_hospital, average_hosp, delta_icu, average_icu,
                                      delta_deaths, average_deaths)
    st.plotly_chart(fig, use_container_width=True)


def show_local_cases(local_data, start_date, stop_date, last_date):
    st.subheader('Situazione a livello provinciale')

    # Get the location for regional sub-area
    provinces_sorted = util.provinces.copy()
    provinces_sorted.sort()

    # Get population automatically
    pop = util.get_pop()

    pop_df = pd.DataFrame({'Provincia': provinces_sorted, 'Pop': pop})
    province_to_visualize = st.selectbox('Provincia da visualizzare (default: Varese)', provinces_sorted, index=99,
                                         format_func=lambda x: 'Seleziona provincia' if x == '' else x)
    province_to_compare = st.selectbox('Compara con altra provincia?', provinces_sorted,
                                       format_func=lambda x: 'Seleziona provincia' if x == '' else x)

    local_data_df = local_data.loc[start_date:stop_date][province_to_visualize]
    days = local_data_df.index.values
    cases = local_data_df.values
    pop1 = pop_df[pop_df['Provincia'] == province_to_visualize]['Pop'].values

    # Compute increments of interest
    delta_cases = util.get_delta(cases)
    delta_casi_pertho = 1e5 * delta_cases / pop1

    # Compute the rolling mean at 7 days
    average = util.compute_rollingmean(delta_casi_pertho)

    # Show the metrics of the last day, only if last day is today
    if stop_date == last_date:
        last_day = days[-1]
        st.markdown(f'Dati più recenti, relativi al ' + last_day)
        st.metric("Casi a " + province_to_visualize, numerize.numerize(int(cases[-1]), 1),
                  util.mysign(delta_cases[-1]) + str(delta_cases[-1]),
                  delta_color="inverse")

    if province_to_compare:
        df2 = local_data.loc[start_date:stop_date][province_to_compare]
        casi2 = df2.values
        delta_cases2 = util.get_delta(casi2)

        st.metric("Casi a " + province_to_compare, numerize.numerize(int(casi2[-1]), 1),
                  util.mysign(delta_cases2[-1]) + str(delta_cases2[-1]),
                  delta_color="inverse")

    giorni0 = [datetime.strptime(giorno, "%d/%m/%Y").date() for giorno in days]

    # Plot the local cases
    fig = plot.get_local_cases_fig(giorni0, province_to_visualize, average, local_data, start_date, stop_date, pop_df,
                                   delta_casi_pertho, province_to_compare)
    st.plotly_chart(fig, use_container_width=True)

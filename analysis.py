import streamlit as st
from datetime import datetime, timedelta
import util, plot
from numerize import numerize
import pandas as pd


def show_national_cases(national_data, start_date, stop_date, input_stop):

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
    ratio = (delta_cases/delta_tamponi)*100.

    delta_icu = util.get_delta(icu)
    delta_hospital = util.get_delta(hospital)

    perc_delta_icu = 100*delta_icu/icu[1:]
    perc_delta_hospital = 100*delta_hospital/hospital[1:]

    delta_deaths = util.get_delta(deaths)

    # Compute the rolling means at 7 days
    average = util.compute_rollingmean(ratio)
    average_hosp = util.compute_rollingmean(delta_hospital)
    average_icu = util.compute_rollingmean(delta_icu)
    average_deaths = util.compute_rollingmean(delta_deaths)

    # Show the metrics of the last day, only if last day is today
    if input_stop == datetime.now().date():
        last_day = days[-1]
        st.markdown(f'Dati pi&ugrave recenti, relativi al '+last_day)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Casi", numerize.numerize(int(cases[-1]), 3), util.mysign(delta_cases[-1])+str(delta_cases[-1])+' ('+str(round(ratio[-1],1))+'%)', delta_color="inverse")
        col2.metric("Ospedalizzati", str(hospital[-1]), util.mysign(delta_hospital[-1])+str(delta_hospital[-1])+' ('+str(round(perc_delta_hospital[-1],1))+'%)', delta_color="inverse")
        col3.metric("Terapie Intensive", str(icu[-1]), util.mysign(delta_icu[-1])+str(delta_icu[-1])+' ('+str(round(perc_delta_icu[-1],1))+'%)', delta_color="inverse")
        col4.metric("Deceduti", str(deaths[-1]), util.mysign(delta_deaths[-1])+str(delta_deaths[-1]), delta_color="inverse")

    giorni0 = [datetime.strptime(giorno, "%d/%m/%Y").date() for giorno in days]

    # Plot the national cases
    fig = plot.get_national_cases_fig(giorni0, ratio, average, delta_hospital, average_hosp, delta_icu, average_icu, delta_deaths, average_deaths)
    st.plotly_chart(fig, use_container_width=True)


def show_local_cases(local_data, start_date, stop_date, input_stop):

    st.subheader('Situazione a livello provinciale')

    # Get the location for regional sub-area
    provinces_sorted = util.provinces.copy()
    provinces_sorted.sort()
    provinces_sorted.insert(0, '')
    # TODO get this automatically
    pop = [0, 419847, 411922, 465023, 123895, 336870, 204575, 209648, 405963,
           1222818, 382685, 199599, 269233, 1099621, 171838, 1019539, 533715,
           1247583, 382454, 420117, 252803, 214629, 911606, 1066765, 346514,
           376397, 594671, 684786, 351698, 166617, 582353, 158183, 170248, 341967,
           986001, 601419, 393556, 473467, 816916, 136809, 218538, 208585, 81918,
           292356, 215538, 561139, 777507, 332593, 329590, 225885, 380676, 307421,
           403585, 189841, 193457, 609223, 3249821, 704672, 867421, 3017658, 362199,
           202951, 153226, 929520, 1214291, 453604, 534951, 643311, 354139, 314689,
           284075, 416425, 290819, 309058, 354122, 256047, 314950, 386309, 526586, 526349,
           151668, 335478, 4227588, 229652, 1075299, 481052, 268766, 263526,
           386451, 179234, 340879, 560048, 301814, 221702, 2212996, 418363, 544745,
           878070, 229470, 523416, 879929, 842942, 155065, 167189, 922291, 153225,
           850379, 306934]
    pop_df = pd.DataFrame({'Provincia': provinces_sorted, 'Pop': pop})
    province_to_visualize = st.selectbox('Provincia da visualizzare (default: Varese)', provinces_sorted, index=100,
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
    if input_stop == datetime.now().date():
        last_day = days[-1]
        st.markdown(f'Dati pi&ugrave recenti, relativi al ' + last_day)
        st.metric("Casi", numerize.numerize(int(cases[-1]), 1), util.mysign(delta_cases[-1]) + str(delta_cases[-1]),
                  delta_color="inverse")

    giorni0 = [datetime.strptime(giorno, "%d/%m/%Y").date() for giorno in days]

    # Plot the local cases
    fig = plot.get_local_cases_fig(giorni0, province_to_visualize, average, local_data, start_date, stop_date, pop_df,
                                   delta_casi_pertho, province_to_compare)
    st.plotly_chart(fig, use_container_width=True)
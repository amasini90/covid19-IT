from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import util


def get_national_cases_fig(giorni0, ratio, average, perc_delta_hospital, average_hosp, perc_delta_icu, average_icu, delta_deaths, average_deaths):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02)

    fig.append_trace(go.Scatter(
        x=giorni0[1:],
        y=ratio,
        mode='lines',
        line=dict(color='lawngreen', width=1),
        opacity=.0,
        showlegend=False,
        name='Tamponi positivi',
        legendgroup='1'
        ),
        row=1,
        col=1
    )

    fig.append_trace(go.Bar(
        x=giorni0[1:], 
        y=ratio,
        opacity=.2,
        showlegend=False,
        marker_color = 'lawngreen'
        ),
        row=1,
        col=1
    )

    fig.append_trace(go.Scatter(
        x=giorni0[1:],
        y=average,
        mode='lines',
        line=dict(color='lawngreen', width=3),
        name='% tamponi positivi',
        legendgroup='2'
        ),
        row=1,
        col=1
    )

    fig.append_trace(go.Scatter(
        x=giorni0[1:],
        y=perc_delta_hospital,
        mode='lines',
        line=dict(color='turquoise', width=1),
        opacity=.0,
        showlegend=False,
        name='Ricoverati',
        legendgroup='3'
        ),
        row=2,
        col=1
    )
    fig.append_trace(go.Bar(
        x=giorni0[1:], 
        y=perc_delta_hospital,
        opacity=.2,
        showlegend=False,
        marker_color = 'turquoise'
        ),
        row=2,
        col=1
    )

    fig.append_trace(go.Scatter(
        x=giorni0[1:],
        y=average_hosp,
        mode='lines',
        line=dict(color='turquoise', width=3),
        name='Ricoverati',
        legendgroup='4'
        ),
        row=2,
        col=1
    )

    fig.append_trace(go.Scatter(
        x=giorni0[1:],
        y=perc_delta_icu,
        mode='lines',
        line=dict(color='coral', width=1),
        opacity=.0,
        showlegend=False,
        name='Terapie intensive',
        legendgroup='5'
        ),
        row=3,
        col=1
    )
    fig.append_trace(go.Bar(
        x=giorni0[1:], 
        y=perc_delta_icu,
        opacity=.2,
        showlegend=False,
        marker_color = 'coral'
        ),
        row=3,
        col=1
    )

    fig.append_trace(go.Scatter(
        x=giorni0[1:],
        y=average_icu,
        mode='lines',
        line=dict(color='coral', width=3),
        name='Terapie intensive',
        legendgroup='6'
        ),
        row=3,
        col=1
    )

    fig.append_trace(go.Scatter(
        x=giorni0[1:],
        y=delta_deaths,
        mode='lines',
        line=dict(color='gold', width=1),
        opacity=.0,
        showlegend=False,
        name='Decessi',
        legendgroup='7'
        ),
        row=4,
        col=1
    )
    fig.append_trace(go.Bar(
        x=giorni0[1:], 
        y=delta_deaths,
        opacity=.2,
        showlegend=False,
        marker_color = 'gold'
        ),
        row=4,
        col=1
    )
    fig.append_trace(go.Scatter(
        x=giorni0[1:],
        y=average_deaths,
        mode='lines',
        line=dict(color='gold', width=3),
        name='Decessi',
        legendgroup='8'
        ),
        row=4,
        col=1
    )

    fig.update_yaxes(title_text="Incremento casi (%)", row=1, col=1)
    fig.update_yaxes(title_text="Ricoveri", row=2, col=1)
    fig.update_yaxes(title_text="TI", row=3, col=1)
    fig.update_yaxes(title_text="Decessi", row=4, col=1)
    fig.update_xaxes(title_text="Data", row=4, col=1)

    fig.update_layout(
        height=800, width=600,
        yaxis_rangemode="nonnegative",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12)
            ),
        #legend_tracegroupgap = 180,
        font=dict(size=15)
    )

    return fig


def get_local_cases_fig(giorni0, where, average, local_data, start, stop, pop_df, delta_casi_pertho, compare):
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=giorni0[1:], y=average, mode='lines', line=dict(color='hotpink', width=3), name=where,
                             legendgroup='2'))

    if compare:
        df2 = local_data.loc[start:stop][compare]
        pop2 = pop_df[pop_df['Provincia'] == compare]['Pop'].values
        casi2 = df2.values

        delta_casi2 = 1e5 * np.array(list(casi2[i + 1] - casi2[i] for i in range(len(casi2) - 1))) / pop2
        average2 = util.compute_rollingmean(delta_casi2)
        fig.add_trace(go.Scatter(x=giorni0[1:], y=average2, mode='lines', line=dict(color='mediumaquamarine', width=3),
                                 name=compare, legendgroup='3'))
    else:
        fig.add_trace(go.Bar(
        x=giorni0[1:], 
        y=delta_casi_pertho,
        opacity=.2,
        showlegend=False,
        marker_color = 'hotpink'
        ),
        )
        fig.add_trace(go.Scatter(x=giorni0[1:], y=delta_casi_pertho, mode='lines', line=dict(color='hotpink', width=1),
                                 opacity=.0, showlegend=False, name='Tamponi positivi', legendgroup='1'))

    fig.update_yaxes(title_text="Casi ogni 100mila abitanti")
    fig.update_xaxes(title_text="Data")

    fig.update_layout(
        height=400, width=600,
        yaxis_rangemode="nonnegative",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12)
        ),
        # legend_tracegroupgap = 180,
        font=dict(size=15)
    )

    return fig
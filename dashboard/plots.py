# # Standard library imports
# import json
# from urllib.request import urlopen

# Third party imports
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.graph_objs import Layout
from plotly.offline import plot


# Project dependencies imports
from .processdata import Covid_data

# Create an instace of the Covid_data class
data = Covid_data()

# Make a choropleth of the total cases for each CCAA
def total_cases_map():
    ISO_code_column_name = data.column_names_dict['ISO_code_column_name']
    cartodb_id_column_name = data.column_names_dict['cartodb_id_column_name']
    cases_column_name = data.column_names_dict['cases_column_name']
    #I can do the following, because values are unique
    CCAA_dict = {data.CCAA_dict[key]:key for key in data.CCAA_dict}

    df = data.data_COVID19_spain_last[[ISO_code_column_name,cartodb_id_column_name,cases_column_name]]
    df['Comunidad'] = [ CCAA_dict[code] for code in df[ISO_code_column_name]]

    color_scale = ['#57ebde', '#6cedcd', '#7ceebd', '#88f0ac', '#91f29a', '#99f388', '#a0f575', '#a6f761', '#aaf94a', '#aefb2a']

    fig = px.choropleth(df,
        geojson=data.geoJSON_dict_CCAA,
        color=cases_column_name,
        locations=cartodb_id_column_name,
        featureidkey="properties.cartodb_id",
        projection="mercator",
        color_continuous_scale=color_scale,
        hover_name= 'Comunidad',
        hover_data = [cases_column_name],
        title = 'Casos totales',
    )
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)'
    )
    fig.update_geos(
        fitbounds="locations",
        visible=False)
    plot_div = plot(
        fig,
        include_plotlyjs=False,
        output_type='div',
        config={'displayModeBar': False}
    )
    return plot_div

# # Standard library imports
import os

# Third party imports
import plotly.express as px
import plotly.graph_objs as go
from plotly.graph_objs import Layout
from plotly.offline import plot

# Project dependencies imports
from .processdata import Covid_data

# Set mapbox custom style
if os.getenv('MAPBOX_TOKEN'):
    px.set_mapbox_access_token(os.getenv('MAPBOX_TOKEN'))
    mapbox_style = os.getenv('MAPBOX_STYLE_URL')
else:
    mapbox_style = 'carto-positron'

# Create an instace of the Covid_data class
data = Covid_data()

# Make a plot showing the evolution of the Outbreak in Spain
def makeNationalGrowthPlot():
    # Define basic layout of the plot
    fig_layout = Layout(
        legend = {'x':0,'y':1},
        xaxis = {'showgrid': False},
        yaxis = {'showgrid': False},
        yaxis_title="Casos",
        xaxis_title="",
        margin={"r":10,"t":0,"l":10,"b":0},
        template='plotly_white',
        font=dict(color='#8898aa')
    )

    # data for the figure
    df = data.data_COVID19_spain_sum
    date_column_name = data.column_names_dict['date_column_name']
    active_cases_column_name = data.column_names_dict['active_cases_column_name']
    deaths_column_name = data.column_names_dict['deaths_column_name']
    recovered_column_name = data.column_names_dict['recovered_column_name']

    active_cases_trace = go.Scatter(
        x=df[date_column_name], y=df[active_cases_column_name],
        mode='none',
        line=dict(width=0.5, color='rgb(131, 90, 241)'),
        name = active_cases_column_name,
        stackgroup='one' # define stack group
    )

    fig = go.Figure(
        layout = fig_layout,
        data = [active_cases_trace]
    )

    plot_div = plot(
        fig,
        include_plotlyjs=False,
        output_type='div'
    )

    return plot_div

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

    fig = px.choropleth_mapbox(df,
        geojson=data.geoJSON_dict_CCAA,
        color=cases_column_name,
        locations=cartodb_id_column_name,
        featureidkey="properties.cartodb_id",
        color_continuous_scale=color_scale,
        mapbox_style = mapbox_style,
        center = {'lat':40.335280, 'lon':-3.697136 },
        zoom = 4,
        hover_name= 'Comunidad',
        hover_data = [cases_column_name],
        opacity = 1.
    )
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}
    )
    # fig.update_geos(
    #     fitbounds="locations",
    #     visible=False)
    plot_div = plot(
        fig,
        include_plotlyjs=False,
        output_type='div',
        config={'displayModeBar': False}
    )
    return plot_div

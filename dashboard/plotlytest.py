# # Standard library imports
# import json
# from urllib.request import urlopen

# Third party imports
# import pandas as pd
# import plotly.express as px
import plotly.graph_objs as go
# from plotly.graph_objs import Layout
from plotly.offline import plot


def plot_somethin():
    fig = go.Figure()
    plot_div = plot(fig, include_plotlyjs=False, output_type='div', config={'displayModeBar': False})
    return plot_div

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, path="/", name="Home", order=0)

layout = dbc.Container([

    html.Div([
        html.H1(["Dashboard"],className="h3 mb-0 text-gray-800")
    ])

], fluid=True)

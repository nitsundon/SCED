import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, path="/", name="Home", order=0)

layout=html.Div("Hello world")
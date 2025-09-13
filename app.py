# app.py
import dash
import dash_bootstrap_components as dbc


# Initialize Dash with a Bootstrap theme
app = dash.Dash(
__name__,
use_pages=True,
suppress_callback_exceptions=True,
title="Dash Multipage App",
external_stylesheets=[dbc.themes.BOOTSTRAP],
)


server = app.server
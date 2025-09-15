# app.py
import dash
import dash_bootstrap_components as dbc


# Initialize Dash with a Bootstrap theme
app = dash.Dash(
__name__,
use_pages=True,
suppress_callback_exceptions=True,
title="Maharashtra SCED",
external_stylesheets=[dbc.themes.BOOTSTRAP,
                      "https://fonts.googleapis.com/css?family=Nunito:200,200i,300,300i,400,400i,600,600i,700,700i,800,800i,900,900i",
                      "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
                      ],
)


server = app.server
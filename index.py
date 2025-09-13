import app as app
import dash
from dash import html
import dash_bootstrap_components as dbc
from pages.Widgets.Sidebar import NavBar,Sidebar

ap = app.app
ap.layout = html.Div([
    dbc.Container(
        [
            NavBar()
        ]
    ,fluid=True),
    dbc.Container([
        dbc.Row([
            dbc.Col([
                Sidebar()
            ], lg=2,className=" vh-100"),
            dbc.Col([
                html.Div([
                    dash.page_container
                ], className="wrapper")
            ], lg=9),
        ])

    ], fluid=True)

])

if __name__ == "__main__":
    ap.run(debug=True)

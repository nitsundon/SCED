import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, callback
import classses.graph.home_graphs
from classses.ConnectionHandler import MongoConnect
from classses.Model.getInput import getSingleInput
from classses.graph.home_graphs import HomeGraphs
import plotly.graph_objs as go

dash.register_page(__name__, path="/", name="Home", order=0)

db = MongoConnect().getDB()

df = getSingleInput(db=db).getDCwithRate()
hg = HomeGraphs(db)
layout = dbc.Container([

    html.Div([
        html.H1(["Dashboard"], className="h3 mb-0 text-gray-800"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H6(["Sun Burst Plot"], className="m-0 font-weight-bold text-primary")
                    ], className=""),
                    dbc.CardBody([
                        dcc.Graph(id="home-sunburst-fig", ),

                        dcc.Slider(
                            min=1,
                            max=96,
                            id="sunburst_block_selector",
                            step=1,
                            value=1,
                            dots=False,
                            marks={1: "1", 50: "50"},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )

                    ])
                ], )
            ], lg=4)
        ], className="mt-3")
    ])

], fluid=True)


@callback(Output("home-sunburst-fig", "figure"),
          Input("sunburst_block_selector", "value"),
          prevent_initial_call=True)
def loadSunBurstPlot(val):
    print(val)
    figure = HomeGraphs(db).SunburstGraph(df, val)
    return figure

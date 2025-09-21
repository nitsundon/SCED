import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, callback, dash_table
import classses.graph.home_graphs
from classses.ConnectionHandler import MongoConnect
from classses.Model.getInput import getSingleInput
from classses.graph.home_graphs import HomeGraphs
import plotly.graph_objs as go

dash.register_page(__name__, path="/", name="Home", order=0)
db = MongoConnect().getDB()
hg = HomeGraphs(db)

ipf = getSingleInput(db=db)
df = ipf.getDCwithRate()
df_demandcurve = ipf.getDatafromDemandCurve()
df_dc = ipf.getDC()

layout = dbc.Container([

    html.Div([
        html.H1(["Dashboard"], className="h3 mb-0 text-gray-800"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H6(["Generator DC Distribution"], className="m-0 font-weight-bold text-primary")
                    ], className=""),
                    dbc.CardBody([
                        dcc.Graph(id="home-sunburst-fig", figure=hg.SunburstGraph(df, 1)),

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
            ], lg=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            dbc.Col(
                                [html.H6(["Forecasted Demand Curve"], className="m-0 font-weight-bold text-primary"), ],
                                lg=6),
                            dbc.Col([
                                dcc.Loading(id="loading",
                                            type="circle",  # "default", "circle", or "dot"
                                            children=[
                                                dcc.Dropdown(
                                                    options={
                                                        "demand": "Demand",
                                                        "centre": "Centre Share",
                                                        "px": "Power Exchange",
                                                        "remc": "REMC",
                                                        "rtm": "Real Time Market",
                                                        "standby": "Standby",
                                                        "interdiscom": "Inter Discom Trade"

                                                    },
                                                    id="dd_share_from_demand_curve",
                                                )
                                            ])

                            ],
                                lg=6
                            )

                        ], className="d-flex")

                    ]),
                    dbc.CardBody([
                        dcc.Graph(id="home-demand-curve", figure=hg.PlotDemandCurve(df_demandcurve)),
                    ])
                ], className="h-100")
            ], lg=8)
        ], className="mt-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardHeader([
                            html.Div([
                                dbc.Col([html.H6(["Generation Graph"], className="m-0 font-weight-bold text-primary",id="temp")],lg=6),
                                dbc.Col([
                                    dcc.Dropdown(options=df_dc['Generator_Name'].values,id="dd_home_gen_select")
                                ],lg=6)
                            ],className="d-flex")

                        ], className="text-primary"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="home_dc_curve",

                            )
                        ])
                    ]
                )
            ], lg=6, className="h-100")
        ], className="py-4")
    ])

], fluid=True)


@callback(Output("home-sunburst-fig", "figure"),
          Input("sunburst_block_selector", "value"),
          prevent_initial_call=True)
def loadSunBurstPlot(val):
    figure = hg.SunburstGraph(df, val)
    return figure


@callback(Output("home-demand-curve", "figure"),
          Input("dd_share_from_demand_curve", "value"),
          prevent_initial_call=True)
def loadDemandCurve(val):
    print(val)
    figure = hg.PlotDemandCurve(df_demandcurve, head=val)
    return figure

@callback(Output("home_dc_curve", "figure"),
          Input("dd_home_gen_select", "value"),
          prevent_initial_call=True)
def loadDemandCurve(val):

    df=df_dc[df_dc['Generator_Name']==val].drop(columns="Generator_Name")
    fig=go.Figure(go.Scatter(df.to_dict(),marker="lines"))
    return fig
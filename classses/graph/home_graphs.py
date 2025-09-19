from typing import Any

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
import plotly.graph_objs
from dash import html
from classses.ConnectionHandler import MongoConnect
from classses.Model.getInput import getSingleInput


class HomeGraphs:
    def __init__(self,db):
        self.db=db
        pass

    def SunburstGraph(self,df,block:int)-> plotly.graph_objs.Figure:
        # df = getSingleInput(db=self.db).getDCwithRate()

        # Filter Block 1
        df = df[df['Block'] == str(block)].copy()


        df = df.sort_values(by=["Discom_Name", "MOD_Rate"], ascending=True)



        # Build Sunburst
        fig = px.sunburst(
            df,
            path=[ "Discom_Name", "MOD_Rate","Generator_Name"],
            values="MW",

        )
        fig.update_layout(
            margin=dict(l=10, r=10, t=30, b=10),  # adjust as needed
        )
        return fig

    def PlotDemandCurve(self):
        df = getSingleInput(db=self.db).getDemand()
        df=df.melt(id_vars=["Discom_Name"],var_name="Block",value_name="MW")
        group_object=df.groupby(by="Discom_Name")
        fig=go.Figure()
        for discom, grouped_df in df.groupby("Discom_Name"):
            fig.add_trace(
                go.Scatter(
                    x=grouped_df["Block"],  # x-axis values
                    y=grouped_df["MW"],  # y-axis values
                    mode="lines",
                    name=discom
                )
            )

        fig.update_layout(
            title="Demand Curves per DISCOM",
            xaxis_title="Block (1–96)",
            yaxis_title="MW",
            margin=dict(l=0, r=0, t=30, b=50),

            legend=dict(
                orientation="h",  # horizontal
                yanchor="bottom",  # anchor legend to bottom
                y=-0.7,  # push it below plot
                xanchor="center",
                x=0.5
            )
        )
        return fig


HomeGraphs(MongoConnect().getDB()).PlotDemandCurve()
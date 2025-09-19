from typing import Any

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
import plotly.graph_objs
from dash import html

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



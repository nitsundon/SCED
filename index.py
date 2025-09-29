import app as app
import dash
from dash import html, Input,Output
import dash_bootstrap_components as dbc
from pages.Widgets.Sidebar import get_topbar,get_sidebar

ap = app.app
ap.layout = html.Div(
    [
        get_sidebar(),
        html.Div([
            get_topbar(),
            dash.page_container

        ],className="d-flex flex-column",id="content-wrapper")
    ], id="wrapper")

if __name__ == "__main__":
    ap.run(debug=True)



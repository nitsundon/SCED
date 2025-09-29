
import dash_bootstrap_components as dbc
from dash import html, dcc,Input,Output,callback

from classses.ExcelDataProcessor import ExcelDataProcessor


def get_topbar():
    return dbc.Navbar(
        className="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow",
        children=[
            # dbc.Breadcrumb(
            #     items=[
            #         {"label": "Home", "active": True},  # clickable link
            #
            #     ]
            # ),
            # Sidebar Toggle (Topbar)
            html.Button(["RUN SCED"],id="temp_btn"),
            dbc.Button(
                html.I(className="fa fa-bars"),
                id="sidebarToggleTop",
                class_name="btn btn-link d-md-none rounded-circle mr-3",
                n_clicks=0,
            ),

            # Topbar Search (md+)
            # dbc.Form(
            #     dbc.InputGroup(
            #         [
            #             dbc.Input(
            #                 placeholder="Search for...",
            #                 class_name="bg-light border-0 small",
            #                 type="text",
            #                 id="topbar-search-input",
            #             ),
            #             dbc.InputGroupText(
            #                 dbc.Button(
            #                     html.I(className="fas fa-search fa-sm"),
            #                     color="primary",
            #                     class_name="px-3",
            #                     id="topbar-search-btn",
            #                     n_clicks=0,
            #                 ),
            #                 class_name="p-0 bg-transparent border-0",
            #             ),
            #         ],
            #         class_name="mw-100 navbar-search",
            #     ),
            #     class_name="d-none d-sm-inline-block form-inline mr-auto ml-md-3 my-2 my-md-0",
            # ),

            # Right side

        ],
    )

def get_sidebar():
    return dbc.Nav(
        [
            # Sidebar Brand
            html.A(
                dbc.Row(
                    [

                        dbc.Col(html.Div("MAHA-SCED", className="sidebar-brand-text mx-3")),
                    ],
                    className="sidebar-brand d-flex align-items-center justify-content-center",
                ),
                href="index.html",
            ),

            html.Hr(className="sidebar-divider my-0"),

            # Dashboard Link
            dbc.NavItem(
                dbc.NavLink(
                    [html.I(className="fas fa-fw fa-tachometer-alt"), " Dashboard"],
                    href="index.html",

                )
            ),
            dbc.NavItem(
                dbc.NavLink(
                    [html.I(className="fas fa-fw fa-tachometer-alt"), "Utility Insights"],
                    href="/home",

                )
            ),

            html.Hr(className="sidebar-divider"),

            # # Heading
            # html.Div("Interface", className="sidebar-heading"),
            #
            # # Components Collapse
            # dbc.NavItem(
            #     dbc.Collapse(
            #         [
            #             dbc.NavLink("Buttons", href="buttons.html", className="collapse-item"),
            #             dbc.NavLink("Cards", href="cards.html", className="collapse-item"),
            #         ],
            #         id="collapse-components",
            #         is_open=False,
            #         className="bg-white py-2 collapse-inner rounded"
            #     )
            # ),
            #
            # # Utilities Collapse
            # dbc.NavItem(
            #     dbc.Collapse(
            #         [
            #             dbc.NavLink("Colors", href="utilities-color.html", className="collapse-item"),
            #             dbc.NavLink("Borders", href="utilities-border.html", className="collapse-item"),
            #             dbc.NavLink("Animations", href="utilities-animation.html", className="collapse-item"),
            #             dbc.NavLink("Other", href="utilities-other.html", className="collapse-item"),
            #         ],
            #         id="collapse-utilities",
            #         is_open=False,
            #         className="bg-white py-2 collapse-inner rounded"
            #     )
            # ),
            #
            # html.Hr(className="sidebar-divider"),
            #
            # html.Div("Addons", className="sidebar-heading"),
            #
            # # Pages Collapse
            # dbc.Collapse(
            #     [
            #         html.H6("Login Screens:", className="collapse-header"),
            #         dbc.NavLink("Login", href="login.html", className="collapse-item"),
            #         dbc.NavLink("Register", href="register.html", className="collapse-item"),
            #         dbc.NavLink("Forgot Password", href="forgot-password.html", className="collapse-item"),
            #         html.Div(className="collapse-divider"),
            #         html.H6("Other Pages:", className="collapse-header"),
            #         dbc.NavLink("404 Page", href="404.html", className="collapse-item"),
            #         dbc.NavLink("Blank Page", href="blank.html", className="collapse-item"),
            #     ],
            #     id="collapse-pages",
            #     is_open=False,
            #     className="bg-white py-2 collapse-inner rounded"
            # ),
            #
            # dbc.NavItem(
            #     dbc.NavLink([html.I(className="fas fa-fw fa-chart-area"), " Charts"], href="charts.html")
            # ),
            #
            # dbc.NavItem(
            #     dbc.NavLink([html.I(className="fas fa-fw fa-table"), " Tables"], href="tables.html")
            # ),
            #
            # html.Hr(className="sidebar-divider d-none d-md-block"),



        ],
        vertical=True,
        pills=True,
        className="navbar-nav bg-gradient-primary sidebar sidebar-dark accordion",
        id="accordionSidebar",
    )


@callback(
    Output("temp_btn","n_clicks"),
    Input("temp_btn","n_clicks")
)
def temp_btn(n):
    ExcelDataProcessor().createGAMSfile()
    return 2
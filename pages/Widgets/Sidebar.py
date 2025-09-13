import dash_bootstrap_components as dbc


def NavBar():
    return dbc.Navbar(
        [
            dbc.NavbarBrand([
                "DashBoard"
            ]
            )]
    )


def Sidebar():
    return dbc.Nav([
        dbc.NavItem([
            dbc.NavLink(["Home"],active=True,href="www.google.com")
        ]),
        dbc.NavItem([
            dbc.NavLink(["Monitor"], href="www.google.com")
        ])
    ],fill=True,pills=True,vertical=True,horizontal="start",justified=False)
import dash
import dash_bootstrap_components as dbc
from dash import html

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
)
server = app.server  # Expose the Flask server (needed for deployment)

# ── Navbar ──────────────────────────────────────────────────────────────────
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overview",    href="/")),
        dbc.NavItem(dbc.NavLink("Cities",      href="/cities")),
        dbc.NavItem(dbc.NavLink("Map",         href="/map")),
        dbc.NavItem(dbc.NavLink("Trends",      href="/trends")),
    ],
    brand="🏠 Texas Airbnb Insights",
    brand_href="/",
    color="primary",
    dark=True,
    fluid=True,
    className="mb-4",
)

app.layout = dbc.Container(
    [
        navbar,
        dash.page_container,
    ],
    fluid=True,
)

if __name__ == "__main__":
    app.run(debug=True)

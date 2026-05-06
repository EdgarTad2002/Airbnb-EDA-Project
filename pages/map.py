import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from data_loader import load_data

dash.register_page(__name__, path="/map", name="Map", title="Map Explorer")

_, df_final, _ = load_data()

ALL_CITIES  = sorted(df_final["city"].unique())
PRICE_MIN   = int(df_final["average_rate_per_night"].min())
PRICE_MAX   = int(df_final["average_rate_per_night"].max())
PRICE_P95   = int(df_final["average_rate_per_night"].quantile(0.95))
BEDROOM_MAX = int(df_final["bedrooms_count"].max())


# ── Layout ────────────────────────────────────────────────────────────────────
layout = dbc.Container(
    [
        # Page header
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H2("Map Explorer", className="fw-bold mb-0"),
                        html.P(
                            "Browse Texas Airbnb listings geographically.",
                            className="text-muted",
                        ),
                    ]
                )
            ),
            className="mb-3",
        ),

        # ── Filters ──────────────────────────────────────────────────────────
        dbc.Card(
            dbc.CardBody(
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Filter by City", className="fw-semibold small"),
                                dcc.Dropdown(
                                    id="map-city-dropdown",
                                    options=[{"label": c, "value": c} for c in ALL_CITIES],
                                    value=[],
                                    multi=True,
                                    placeholder="All cities",
                                ),
                            ],
                            md=4,
                        ),
                        dbc.Col(
                            [
                                html.Label("Color Map By", className="fw-semibold small"),
                                dcc.Dropdown(
                                    id="map-color-dropdown",
                                    options=[
                                        {"label": "Nightly Price ($)", "value": "average_rate_per_night"},
                                        {"label": "Bedrooms",          "value": "bedrooms_count"},
                                    ],
                                    value="average_rate_per_night",
                                    clearable=False,
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                html.Label("Price Range ($)", className="fw-semibold small"),
                                dcc.RangeSlider(
                                    id="map-price-slider",
                                    min=PRICE_MIN,
                                    max=PRICE_MAX,
                                    step=1,
                                    pushable=10,
                                    value=[PRICE_MIN, PRICE_P95],
                                    marks={
                                        PRICE_MIN: f"${PRICE_MIN}",
                                        PRICE_MAX: f"${PRICE_MAX}",
                                    },
                                    tooltip={"placement": "bottom", "always_visible": True},
                                    allowCross=False,
                                ),
                            ],
                            md=3,
                            className="pt-1",
                        ),
                        dbc.Col(
                            [
                                html.Label("Max Bedrooms", className="fw-semibold small"),
                                dcc.Slider(
                                    id="map-bedroom-slider",
                                    min=0,
                                    max=BEDROOM_MAX,
                                    step=1,
                                    value=BEDROOM_MAX,
                                    marks={0: "Studio", BEDROOM_MAX: str(BEDROOM_MAX)},
                                    tooltip={"placement": "bottom", "always_visible": True},
                                ),
                            ],
                            md=2,
                            className="pt-1",
                        ),
                    ],
                    className="g-3",
                )
            ),
            className="shadow-sm mb-4",
        ),

        # ── KPI strip ────────────────────────────────────────────────────────
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.P("Listings on Map", className="text-muted small mb-1"),
                                html.H4(id="map-kpi-count", className="fw-bold mb-0"),
                            ],
                            className="text-center",
                        ),
                        className="border-top border-4 border-primary shadow-sm h-100",
                    ),
                    md=3,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.P("Median Price", className="text-muted small mb-1"),
                                html.H4(id="map-kpi-median", className="fw-bold mb-0"),
                            ],
                            className="text-center",
                        ),
                        className="border-top border-4 border-success shadow-sm h-100",
                    ),
                    md=3,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.P("Cities Shown", className="text-muted small mb-1"),
                                html.H4(id="map-kpi-cities", className="fw-bold mb-0"),
                            ],
                            className="text-center",
                        ),
                        className="border-top border-4 border-warning shadow-sm h-100",
                    ),
                    md=3,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.P("Avg Nightly Rate", className="text-muted small mb-1"),
                                html.H4(id="map-kpi-avg", className="fw-bold mb-0"),
                            ],
                            className="text-center",
                        ),
                        className="border-top border-4 border-info shadow-sm h-100",
                    ),
                    md=3,
                ),
            ],
            className="mb-4 g-3",
        ),

        # ── Map ───────────────────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Listing Locations", className="card-title fw-semibold"),
                            html.P(
                                "Each dot is an Airbnb listing. Hover for details. "
                                "Pan and zoom to explore.",
                                className="text-muted small",
                            ),
                            dcc.Graph(
                                id="map-scatter",
                                config={"displayModeBar": True, "scrollZoom": True},
                                style={"height": "520px"},
                            ),
                        ]
                    ),
                    className="shadow-sm",
                )
            ),
            className="mb-4",
        ),

        # ── City price heatmap (bar) ──────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Avg Price by City — Top 10 by Listing Count", className="card-title fw-semibold"),
                            html.P(
                                "Fixed top 10 cities by number of listings and their average nightly price.",
                                className="text-muted small",
                            ),
                            dcc.Graph(id="map-city-bar", config={"displayModeBar": False}),
                        ]
                    ),
                    className="shadow-sm",
                )
            ),
            className="mb-4",
        ),
    ],
    fluid=True,
)


# ── Callbacks ─────────────────────────────────────────────────────────────────
def _filter(price_range, bedroom_max, city_list):
    low, high = price_range[0], max(price_range[1], price_range[0] + 10)
    d = df_final[
        (df_final["average_rate_per_night"] >= low) &
        (df_final["average_rate_per_night"] <= high) &
        (df_final["bedrooms_count"] <= bedroom_max)
    ]
    if city_list:
        d = d[d["city"].isin(city_list)]
    return d


@callback(
    Output("map-kpi-count",  "children"),
    Output("map-kpi-median", "children"),
    Output("map-kpi-cities", "children"),
    Output("map-kpi-avg",    "children"),
    Input("map-price-slider",    "value"),
    Input("map-bedroom-slider",  "value"),
    Input("map-city-dropdown",   "value"),
    Input("map-color-dropdown",  "value"),
)
def update_kpis(price_range, bedroom_max, city_list, _color):
    d = _filter(price_range, bedroom_max, city_list)
    if d.empty:
        return "0", "N/A", "0", "N/A"
    return (
        f"{len(d):,}",
        f"${d['average_rate_per_night'].median():.0f}",
        str(d["city"].nunique()),
        f"${d['average_rate_per_night'].mean():.0f}",
    )


@callback(
    Output("map-scatter", "figure"),
    Input("map-price-slider",   "value"),
    Input("map-bedroom-slider", "value"),
    Input("map-city-dropdown",  "value"),
    Input("map-color-dropdown", "value"),
)
def update_map(price_range, bedroom_max, city_list, color_col):
    d = _filter(price_range, bedroom_max, city_list)
    if d.empty:
        fig = px.scatter_map(lat=[], lon=[], zoom=6)
        fig.update_layout(map_style="open-street-map")
        return fig

    sample = d.sample(min(len(d), 3000), random_state=42)

    color_label = "Nightly Price ($)" if color_col == "average_rate_per_night" else "Bedrooms"
    hover_data = {
        "city": True,
        "average_rate_per_night": ":$,.0f",
        "bedrooms_count": True,
        #color_col: False,
    }

    fig = px.scatter_map(
        sample,
        lat="latitude",
        lon="longitude",
        color=color_col,
        color_continuous_scale="Plasma",
        size_max=8,
        zoom=5,
        center={"lat": 31.0, "lon": -99.0},
        hover_name="city",
        hover_data=hover_data,
        labels={
            "average_rate_per_night": "Nightly Price ($)",
            "bedrooms_count": "Bedrooms",
        },
        opacity=0.75,
    )
    fig.update_layout(
        map_style="open-street-map",
        coloraxis_colorbar=dict(title=color_label, thickness=14),
        margin=dict(t=0, b=0, l=0, r=0),
    )
    return fig


def _top10_city_bar():
    top10_cities = df_final["city"].value_counts().head(10).index.tolist()
    avg_price = (
        df_final[df_final["city"].isin(top10_cities)]
        .groupby("city")["average_rate_per_night"]
        .mean()
        .sort_values(ascending=True)
        .reset_index()
    )
    avg_price.columns = ["city", "avg_price"]
    fig = px.bar(
        avg_price,
        x="avg_price",
        y="city",
        orientation="h",
        color="avg_price",
        color_continuous_scale="Blues",
        labels={"avg_price": "Avg Nightly Price ($)", "city": ""},
        template="plotly_white",
        text_auto="$.0f",
    )
    fig.update_layout(
        margin=dict(t=10, b=40, l=10, r=60),
        coloraxis_showscale=False,
        height=300,
    )
    fig.update_traces(textposition="outside")
    return fig


_CITY_BAR_FIGURE = _top10_city_bar()


@callback(
    Output("map-city-bar", "figure"),
    Input("map-price-slider", "value"),
)
def update_city_bar(_price):
    return _CITY_BAR_FIGURE

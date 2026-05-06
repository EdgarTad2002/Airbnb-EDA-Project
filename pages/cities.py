import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from data_loader import load_data

dash.register_page(__name__, path="/cities", name="Cities", title="City Intelligence")

_, _, df_story = load_data()

ALL_CITIES = sorted(df_story["city"].unique())
BEDROOM_OPTIONS = [{"label": "All", "value": "all"}] + [
    {"label": ("Studio" if b == 0 else f"{b} BR"), "value": b}
    for b in sorted(df_story["bedrooms_count"].unique().astype(int))
]


# ── Layout ────────────────────────────────────────────────────────────────────
layout = dbc.Container(
    [
        # Page header
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H2("City Intelligence", className="fw-bold mb-0"),
                        html.P(
                            "Compare cities by pricing, volume, and value metrics.",
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
                                html.Label("Metric to Compare", className="fw-semibold small"),
                                dcc.Dropdown(
                                    id="cities-metric-dropdown",
                                    options=[
                                        {"label": "Median Nightly Price ($)",  "value": "median_price"},
                                        {"label": "Number of Listings",        "value": "listing_count"},
                                        {"label": "Avg Bedrooms",              "value": "avg_bedrooms"},
                                        {"label": "Price per Bedroom ($)",     "value": "price_per_bedroom"},
                                    ],
                                    value="median_price",
                                    clearable=False,
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                html.Label("Filter by Bedrooms", className="fw-semibold small"),
                                dcc.Dropdown(
                                    id="cities-bedroom-dropdown",
                                    options=BEDROOM_OPTIONS,
                                    value="all",
                                    clearable=False,
                                ),
                            ],
                            md=3,
                        ),
                        dbc.Col(
                            [
                                html.Label("Top N Cities (by listing count)", className="fw-semibold small"),
                                dcc.Slider(
                                    id="cities-n-slider",
                                    min=5,
                                    max=20,
                                    step=5,
                                    value=10,
                                    marks={5: "5", 10: "10", 15: "15", 20: "20"},
                                ),
                            ],
                            md=3,
                            className="pt-1",
                        ),
                        dbc.Col(
                            [
                                html.Label("Focus on Cities (optional)", className="fw-semibold small"),
                                dcc.Dropdown(
                                    id="cities-city-dropdown",
                                    options=[{"label": c, "value": c} for c in ALL_CITIES],
                                    value=[],
                                    multi=True,
                                    placeholder="All cities",
                                ),
                            ],
                            md=3,
                        ),
                    ],
                    className="g-3",
                )
            ),
            className="shadow-sm mb-4",
        ),

        # ── KPI Cards ────────────────────────────────────────────────────────
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.P("Cities in View", className="text-muted small mb-1"),
                                html.H4(id="cities-kpi-count", className="fw-bold mb-0"),
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
                                html.P("Highest Median Price", className="text-muted small mb-1"),
                                html.H4(id="cities-kpi-highest", className="fw-bold mb-0"),
                            ],
                            className="text-center",
                        ),
                        className="border-top border-4 border-danger shadow-sm h-100",
                    ),
                    md=3,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.P("Most Listings", className="text-muted small mb-1"),
                                html.H4(id="cities-kpi-most", className="fw-bold mb-0"),
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
                                html.P("Best Value ($/BR)", className="text-muted small mb-1"),
                                html.H4(id="cities-kpi-value", className="fw-bold mb-0"),
                            ],
                            className="text-center",
                        ),
                        className="border-top border-4 border-success shadow-sm h-100",
                    ),
                    md=3,
                ),
            ],
            className="mb-4 g-3",
        ),

        # ── Main bar chart ────────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("City Comparison Bar Chart", className="card-title fw-semibold"),
                            html.P(
                                "Ranked cities by the selected metric. Use filters above to slice.",
                                className="text-muted small",
                            ),
                            dcc.Graph(id="cities-bar", config={"displayModeBar": False}),
                        ]
                    ),
                    className="shadow-sm",
                )
            ),
            className="mb-4",
        ),

        # ── Box plot + Scatter ────────────────────────────────────────────────
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Price Distribution by City", className="card-title fw-semibold"),
                                html.P(
                                    "Box plot showing spread and outliers per city.",
                                    className="text-muted small",
                                ),
                                dcc.Graph(id="cities-boxplot", config={"displayModeBar": False}),
                            ]
                        ),
                        className="shadow-sm h-100",
                    ),
                    md=7,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Price vs Volume", className="card-title fw-semibold"),
                                html.P(
                                    "Median price vs listing count per city. Bubble = avg bedrooms.",
                                    className="text-muted small",
                                ),
                                dcc.Graph(id="cities-scatter", config={"displayModeBar": False}),
                            ]
                        ),
                        className="shadow-sm h-100",
                    ),
                    md=5,
                ),
            ],
            className="mb-4 g-3",
        ),
    ],
    fluid=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────────
METRIC_LABELS = {
    "median_price":      "Median Nightly Price ($)",
    "listing_count":     "Number of Listings",
    "avg_bedrooms":      "Avg Bedrooms",
    "price_per_bedroom": "Price per Bedroom ($)",
}


def _filter(bedroom_val, city_list):
    d = df_story.copy()
    if bedroom_val != "all":
        d = d[d["bedrooms_count"] == int(bedroom_val)]
    if city_list:
        d = d[d["city"].isin(city_list)]
    return d


def _aggregate(d):
    agg = d.groupby("city").agg(
        median_price=("average_rate_per_night", "median"),
        listing_count=("average_rate_per_night", "count"),
        avg_bedrooms=("bedrooms_count", "mean"),
        price_per_bedroom=("price_per_bedroom", "median"),
    ).reset_index()
    return agg


# ── Callbacks ─────────────────────────────────────────────────────────────────
@callback(
    Output("cities-kpi-count",   "children"),
    Output("cities-kpi-highest", "children"),
    Output("cities-kpi-most",    "children"),
    Output("cities-kpi-value",   "children"),
    Input("cities-metric-dropdown",  "value"),
    Input("cities-bedroom-dropdown", "value"),
    Input("cities-n-slider",         "value"),
    Input("cities-city-dropdown",    "value"),
)
def update_kpis(metric, bedroom_val, n, city_list):
    d = _filter(bedroom_val, city_list)
    if d.empty:
        return "0", "N/A", "N/A", "N/A"
    agg = _aggregate(d).nlargest(n, "listing_count")
    highest = agg.loc[agg["median_price"].idxmax(), "city"]
    most    = agg.loc[agg["listing_count"].idxmax(), "city"]
    best    = agg.loc[agg["price_per_bedroom"].idxmin(), "city"]
    return str(len(agg)), highest, most, best


@callback(
    Output("cities-bar", "figure"),
    Input("cities-metric-dropdown",  "value"),
    Input("cities-bedroom-dropdown", "value"),
    Input("cities-n-slider",         "value"),
    Input("cities-city-dropdown",    "value"),
)
def update_bar(metric, bedroom_val, n, city_list):
    d = _filter(bedroom_val, city_list)
    if d.empty:
        return px.bar(title="No data for this selection", template="plotly_white")
    agg = _aggregate(d).nlargest(n, "listing_count").sort_values(metric, ascending=False)
    fig = px.bar(
        agg,
        x="city",
        y=metric,
        color=metric,
        color_continuous_scale="Teal",
        labels={"city": "City", metric: METRIC_LABELS[metric]},
        template="plotly_white",
        text_auto=".3s",
    )
    fig.update_layout(
        margin=dict(t=10, b=60, l=50, r=10),
        coloraxis_showscale=False,
        xaxis_tickangle=-35,
        yaxis_title=METRIC_LABELS[metric],
        xaxis_title="",
    )
    fig.update_traces(textposition="outside")
    return fig


@callback(
    Output("cities-boxplot", "figure"),
    Input("cities-bedroom-dropdown", "value"),
    Input("cities-n-slider",         "value"),
    Input("cities-city-dropdown",    "value"),
)
def update_boxplot(bedroom_val, n, city_list):
    d = _filter(bedroom_val, city_list)
    if d.empty:
        return px.box(title="No data for this selection", template="plotly_white")
    top_cities = (
        _aggregate(d).nlargest(n, "listing_count")["city"].tolist()
    )
    d = d[d["city"].isin(top_cities)]
    order = d.groupby("city")["average_rate_per_night"].median().sort_values(ascending=False).index.tolist()
    fig = px.box(
        d,
        x="city",
        y="average_rate_per_night",
        color="city",
        category_orders={"city": order},
        labels={"city": "City", "average_rate_per_night": "Nightly Price ($)"},
        template="plotly_white",
    )
    fig.update_layout(
        margin=dict(t=10, b=60, l=50, r=10),
        showlegend=False,
        xaxis_tickangle=-35,
        xaxis_title="",
        yaxis_title="Nightly Price ($)",
    )
    return fig


@callback(
    Output("cities-scatter", "figure"),
    Input("cities-bedroom-dropdown", "value"),
    Input("cities-n-slider",         "value"),
    Input("cities-city-dropdown",    "value"),
)
def update_scatter(bedroom_val, n, city_list):
    d = _filter(bedroom_val, city_list)
    if d.empty:
        return px.scatter(title="No data for this selection", template="plotly_white")
    agg = _aggregate(d).nlargest(n, "listing_count")
    fig = px.scatter(
        agg,
        x="listing_count",
        y="median_price",
        size="avg_bedrooms",
        color="median_price",
        text="city",
        color_continuous_scale="RdYlGn_r",
        size_max=30,
        labels={
            "listing_count": "Number of Listings",
            "median_price":  "Median Price ($)",
        },
        template="plotly_white",
    )
    fig.update_traces(textposition="top center", textfont_size=9)
    fig.update_layout(
        margin=dict(t=10, b=40, l=50, r=10),
        coloraxis_showscale=False,
        showlegend=False,
    )
    return fig

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from data_loader import load_data

dash.register_page(__name__, path="/map", name="Map", title="Listings Explorer")

_, df_final, _ = load_data()

ALL_CITIES   = sorted(df_final["city"].unique())
PRICE_MIN    = int(df_final["average_rate_per_night"].min())
PRICE_MAX    = int(df_final["average_rate_per_night"].max())
PRICE_P95    = int(df_final["average_rate_per_night"].quantile(0.95))
BEDROOM_MAX  = int(df_final["bedrooms_count"].max())

# Treemap configuration ──────────────────────────────────────────────────────
TOP_CITIES        = 10
PRICE_TIER_BINS   = [-1, 75, 150, 250, float("inf")]
PRICE_TIER_LABELS = ["Budget (<$75)", "Mid ($75–150)", "High ($150–250)", "Luxury ($250+)"]
BEDROOM_ORDER     = ["Studio", "1 bd", "2 bd", "3 bd", "4+ bd"]


def _bedroom_label(n: int) -> str:
    n = int(n)
    if n == 0:
        return "Studio"
    if n >= 4:
        return "4+ bd"
    return f"{n} bd"


# Pre-tag price tier and bedrooms label ONCE — these don't depend on filters.
# Both are ordered categoricals so sunburst slices come out in a stable order.
df_final = df_final.copy()
df_final["price_tier"] = pd.cut(
    df_final["average_rate_per_night"],
    bins=PRICE_TIER_BINS,
    labels=PRICE_TIER_LABELS,
    ordered=True,
)
df_final["bedrooms_label"] = pd.Categorical(
    df_final["bedrooms_count"].apply(_bedroom_label),
    categories=BEDROOM_ORDER,
    ordered=True,
)


# ── Helpers ──────────────────────────────────────────────────────────────────
def _empty_treemap(message: str = "No listings match these filters"):
    fig = px.treemap(
        names=[message],
        parents=[""],
        values=[1],
    )
    fig.update_traces(
        marker=dict(colors=["#e9ecef"]),
        textfont=dict(color="#6c757d", size=14),
        hoverinfo="skip",
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="white",
        height=620,
    )
    return fig


def _build_treemap(d: pd.DataFrame):
    if d.empty:
        return _empty_treemap()

    # Keep only the top cities by listing count — otherwise the chart becomes
    # a mosaic of tiny illegible rectangles.
    top_city_names = d["city"].value_counts().head(TOP_CITIES).index
    d_top = d[d["city"].isin(top_city_names)]
    if d_top.empty:
        return _empty_treemap()

    fig = px.treemap(
        d_top,
        path=[px.Constant("All cities"), "city", "bedrooms_label", "price_tier"],
        values=None,
        color="average_rate_per_night",
        color_continuous_scale="Plasma",
        range_color=(PRICE_MIN, PRICE_P95),
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Listings: %{value:,}<br>"
            "Avg Price: $%{color:.0f}/night"
            "<extra></extra>"
        ),
        textinfo="label+value",
        textfont=dict(size=13, color="white", family="Inter, Arial, sans-serif"),
        marker=dict(
            line=dict(color="white", width=2),
            cornerradius=4,
        ),
        root_color="white",
        tiling=dict(packing="squarify", pad=2),
    )
    fig.update_layout(
        margin=dict(t=30, b=10, l=10, r=100),
        paper_bgcolor="white",
        height=620,
        uirevision="treemap",
        coloraxis_colorbar=dict(
            title=dict(text="Avg Price ($)", side="right"),
            thickness=12,
            len=0.7,
            outlinewidth=0,
            tickfont=dict(size=11, color="#495057"),
        ),
        font=dict(family="Inter, Arial, sans-serif"),
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


CITY_BAR_FIGURE = _top10_city_bar()


# ── Layout ────────────────────────────────────────────────────────────────────
layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H2("Listings Explorer", className="fw-bold mb-0"),
                        html.P(
                            "How Texas Airbnb listings break down by city, bedroom count, and price tier.",
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
                            md=5,
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
                                    updatemode="mouseup",
                                ),
                            ],
                            md=4,
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
                                    updatemode="mouseup",
                                ),
                            ],
                            md=3,
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
                                html.P("Listings Shown", className="text-muted small mb-1"),
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

        # ── Sunburst ─────────────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5(
                                "Listings Treemap — City → Bedrooms → Price Tier",
                                className="card-title fw-semibold",
                            ),
                            html.P(
                                "Top 10 cities, broken down by bedroom count and then by price tier. "
                                "Box size = number of listings, color = avg nightly price. "
                                "Click any box to zoom in; use the breadcrumb at the top to zoom out.",
                                className="text-muted small",
                            ),
                            dcc.Graph(
                                id="map-scatter",
                                config={"displayModeBar": False},
                                style={"height": "620px", "width": "100%"},
                            ),
                        ]
                    ),
                    className="shadow-sm",
                )
            ),
            className="mb-4",
        ),

        # ── City price bar (static) ──────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5(
                                "Avg Price by City — Top 10 by Listing Count",
                                className="card-title fw-semibold",
                            ),
                            html.P(
                                "Fixed top 10 cities by number of listings and their average nightly price.",
                                className="text-muted small",
                            ),
                            dcc.Graph(
                                id="map-city-bar",
                                figure=CITY_BAR_FIGURE,
                                config={"displayModeBar": False},
                            ),
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
    Output("map-scatter",    "figure"),
    Input("map-price-slider",   "value"),
    Input("map-bedroom-slider", "value"),
    Input("map-city-dropdown",  "value"),
)
def update_treemap_and_kpis(price_range, bedroom_max, city_list):
    d = _filter(price_range, bedroom_max, city_list)

    if d.empty:
        return "0", "N/A", "0", "N/A", _empty_treemap()

    return (
        f"{len(d):,}",
        f"${d['average_rate_per_night'].median():.0f}",
        str(d["city"].nunique()),
        f"${d['average_rate_per_night'].mean():.0f}",
        _build_treemap(d),
    )

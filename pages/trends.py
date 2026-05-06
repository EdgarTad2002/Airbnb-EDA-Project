import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from data_loader import load_data

dash.register_page(__name__, path="/trends", name="Trends", title="Trends")

_, df_final, _ = load_data()

# Keep only rows with valid dates
df_trends = df_final.dropna(subset=["listing_year", "listing_month"]).copy()
df_trends["listing_year"] = df_trends["listing_year"].astype(int)

ALL_CITIES = sorted(df_trends["city"].unique())
YEAR_MIN   = int(df_trends["listing_year"].min())
YEAR_MAX   = int(df_trends["listing_year"].max())

# Top-10 cities by listing count (used for default multi-select)
TOP10_CITIES = (
    df_trends["city"].value_counts().head(10).index.tolist()
)


# ── Layout ────────────────────────────────────────────────────────────────────
layout = dbc.Container(
    [
        # Page header
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H2("Trends", className="fw-bold mb-0"),
                        html.P(
                            "How Texas Airbnb listings and prices evolved over time.",
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
                                html.Label("Year Range", className="fw-semibold small"),
                                dcc.RangeSlider(
                                    id="trends-year-slider",
                                    min=YEAR_MIN,
                                    max=YEAR_MAX,
                                    pushable=1,
                                    step=1,
                                    value=[YEAR_MIN, YEAR_MAX],
                                    marks={y: str(y) for y in range(YEAR_MIN, YEAR_MAX + 1)},
                                    allowCross=False,
                                    tooltip={"placement": "bottom", "always_visible": True},
                                ),
                            ],
                            md=5,
                            className="pt-1",
                        ),
                        dbc.Col(
                            [
                                html.Label("Cities to Highlight", className="fw-semibold small"),
                                dcc.Dropdown(
                                    id="trends-city-dropdown",
                                    options=[{"label": c, "value": c} for c in ALL_CITIES],
                                    value=TOP10_CITIES[:5],
                                    multi=True,
                                    placeholder="Select cities…",
                                ),
                            ],
                            md=4,
                        ),
                        dbc.Col(
                            [
                                html.Label("Aggregation", className="fw-semibold small"),
                                dcc.Dropdown(
                                    id="trends-agg-dropdown",
                                    options=[
                                        {"label": "By Year",       "value": "year"},
                                        {"label": "By Year-Month", "value": "month"},
                                    ],
                                    value="year",
                                    clearable=False,
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
                                html.P("Total Listings in Period", className="text-muted small mb-1"),
                                html.H4(id="trends-kpi-total", className="fw-bold mb-0"),
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
                                html.P("Peak Year", className="text-muted small mb-1"),
                                html.H4(id="trends-kpi-peak-year", className="fw-bold mb-0"),
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
                                html.P("Earliest Listing Year", className="text-muted small mb-1"),
                                html.H4(id="trends-kpi-first-year", className="fw-bold mb-0"),
                            ],
                            className="text-center",
                        ),
                        className="border-top border-4 border-info shadow-sm h-100",
                    ),
                    md=3,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.P("Avg Price Change (first→last yr)", className="text-muted small mb-1"),
                                html.H4(id="trends-kpi-price-change", className="fw-bold mb-0"),
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

        # ── Listings over time ────────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("New Listings Over Time", className="card-title fw-semibold"),
                            html.P(
                                "Number of listings added per year (or month) across Texas.",
                                className="text-muted small",
                            ),
                            dcc.Graph(id="trends-listings-line", config={"displayModeBar": False}),
                        ]
                    ),
                    className="shadow-sm",
                )
            ),
            className="mb-4",
        ),

        # ── Price trend + City growth ─────────────────────────────────────────
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Median Price Trend (all Texas)", className="card-title fw-semibold"),
                                html.P(
                                    "How the median nightly rate shifted over the selected period.",
                                    className="text-muted small",
                                ),
                                dcc.Graph(id="trends-price-line", config={"displayModeBar": False}),
                            ]
                        ),
                        className="shadow-sm h-100",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Listing Growth by City", className="card-title fw-semibold"),
                                html.P(
                                    "Year-by-year listing count for the selected cities.",
                                    className="text-muted small",
                                ),
                                dcc.Graph(id="trends-city-line", config={"displayModeBar": False}),
                            ]
                        ),
                        className="shadow-sm h-100",
                    ),
                    md=6,
                ),
            ],
            className="mb-4 g-3",
        ),

        # ── Heatmap: listings by month × year ────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Listing Activity Heatmap (Month × Year)", className="card-title fw-semibold"),
                            html.P(
                                "Intensity of new listings by month and year — reveals seasonal patterns.",
                                className="text-muted small",
                            ),
                            dcc.Graph(id="trends-heatmap", config={"displayModeBar": False}),
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
MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def _filter_years(year_range):
    y1, y2 = year_range
    return df_trends[
        (df_trends["listing_year"] >= y1) &
        (df_trends["listing_year"] <= y2)
    ]


@callback(
    Output("trends-kpi-total",        "children"),
    Output("trends-kpi-peak-year",    "children"),
    Output("trends-kpi-first-year",   "children"),
    Output("trends-kpi-price-change", "children"),
    Input("trends-year-slider", "value"),
)
def update_kpis(year_range):
    d = _filter_years(year_range)
    if d.empty:
        return "0", "N/A", "N/A", "N/A"
    by_year = d.groupby("listing_year").agg(
        count=("average_rate_per_night", "count"),
        median_price=("average_rate_per_night", "median"),
    )
    peak_year  = str(int(by_year["count"].idxmax()))
    first_year = str(int(by_year.index.min()))
    years_sorted = by_year.index.sort_values()
    if len(years_sorted) >= 2:
        p_first = by_year.loc[years_sorted[0], "median_price"]
        p_last  = by_year.loc[years_sorted[-1], "median_price"]
        change  = ((p_last - p_first) / p_first) * 100
        price_change = f"{change:+.1f}%"
    else:
        price_change = "N/A"
    return f"{len(d):,}", peak_year, first_year, price_change


@callback(
    Output("trends-listings-line", "figure"),
    Input("trends-year-slider", "value"),
    Input("trends-agg-dropdown", "value"),
)
def update_listings_line(year_range, agg):
    d = _filter_years(year_range)
    if d.empty:
        return px.line(title="No data for this selection", template="plotly_white")

    if agg == "year":
        by_time = d.groupby("listing_year").size().reset_index(name="listings")
        by_time.columns = ["period", "listings"]
        by_time["period"] = by_time["period"].astype(str)
        x_label = "Year"
    else:
        by_time = (
            d.groupby(["listing_year", "listing_month"])
            .size()
            .reset_index(name="listings")
        )
        by_time["listing_month"] = by_time["listing_month"].astype(int)
        by_time["period"] = (
            by_time["listing_year"].astype(str)
            + "-"
            + by_time["listing_month"].astype(str).str.zfill(2)
        )
        by_time = by_time.sort_values("period")
        x_label = "Year-Month"

    fig = px.line(
        by_time,
        x="period",
        y="listings",
        markers=True,
        labels={"period": x_label, "listings": "Number of Listings"},
        template="plotly_white",
        color_discrete_sequence=["#2563eb"],
    )
    fig.update_traces(line_width=2.5, marker_size=6)
    fig.update_layout(
        margin=dict(t=10, b=50, l=50, r=10),
        xaxis_tickangle=-35,
        yaxis_title="Number of Listings",
        xaxis_title=x_label,
    )
    return fig


@callback(
    Output("trends-price-line", "figure"),
    Input("trends-year-slider",  "value"),
    Input("trends-agg-dropdown", "value"),
)
def update_price_line(year_range, agg):
    d = _filter_years(year_range)
    if d.empty:
        return px.line(title="No data for this selection", template="plotly_white")

    if agg == "year":
        by_time = d.groupby("listing_year")["average_rate_per_night"].median().reset_index()
        by_time.columns = ["period", "median_price"]
        by_time["period"] = by_time["period"].astype(str)
        x_label = "Year"
    else:
        by_time = (
            d.groupby(["listing_year", "listing_month"])["average_rate_per_night"]
            .median()
            .reset_index()
        )
        by_time = by_time.rename(columns={"average_rate_per_night": "median_price"})
        by_time["listing_month"] = by_time["listing_month"].astype(int)
        by_time["period"] = (
            by_time["listing_year"].astype(str)
            + "-"
            + by_time["listing_month"].astype(str).str.zfill(2)
        )
        by_time = by_time.sort_values("period")
        x_label = "Year-Month"

    fig = px.line(
        by_time,
        x="period",
        y="median_price",
        markers=True,
        labels={"period": x_label, "median_price": "Median Price ($)"},
        template="plotly_white",
        color_discrete_sequence=["#16a34a"],
    )
    fig.update_traces(line_width=2.5, marker_size=6)
    fig.update_layout(
        margin=dict(t=10, b=50, l=50, r=10),
        xaxis_tickangle=-35,
        yaxis_title="Median Nightly Price ($)",
        xaxis_title=x_label,
    )
    return fig


MAX_CITIES = 10


@callback(
    Output("trends-city-line", "figure"),
    Input("trends-year-slider",   "value"),
    Input("trends-city-dropdown", "value"),
)
def update_city_line(year_range, city_list):
    d = _filter_years(year_range)
    if not city_list:
        city_list = TOP10_CITIES[:5]

    # Cap at MAX_CITIES — pick the ones with the most listings
    was_capped = False
    if len(city_list) > MAX_CITIES:
        top = (
            d[d["city"].isin(city_list)]
            .groupby("city")
            .size()
            .nlargest(MAX_CITIES)
            .index.tolist()
        )
        city_list = top
        was_capped = True

    d = d[d["city"].isin(city_list)]
    if d.empty:
        return px.line(title="No data for the selected cities", template="plotly_white")

    by_city_year = (
        d.groupby(["listing_year", "city"]).size().reset_index(name="listings")
    )
    by_city_year["listing_year"] = by_city_year["listing_year"].astype(str)

    title = f"Showing top {MAX_CITIES} cities by listing count" if was_capped else None
    fig = px.line(
        by_city_year,
        x="listing_year",
        y="listings",
        color="city",
        markers=True,
        labels={"listing_year": "Year", "listings": "Listings", "city": "City"},
        template="plotly_white",
        title=title,
    )
    fig.update_traces(line_width=2, marker_size=5)
    fig.update_layout(
        margin=dict(t=30 if title else 10, b=50, l=50, r=10),
        xaxis_tickangle=-35,
        yaxis_title="Number of Listings",
        xaxis_title="Year",
        legend_title="City",
    )
    return fig


@callback(
    Output("trends-heatmap", "figure"),
    Input("trends-year-slider", "value"),
)
def update_heatmap(year_range):
    d = _filter_years(year_range)
    if d.empty:
        return px.imshow([[0]], title="No data", template="plotly_white")
    pivot = (
        d.groupby(["listing_year", "listing_month"])
        .size()
        .unstack(fill_value=0)
    )
    pivot.columns = [MONTH_NAMES.get(m, m) for m in pivot.columns]
    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=[str(y) for y in pivot.index],
            colorscale="YlOrRd",
            hovertemplate="Year: %{y}<br>Month: %{x}<br>Listings: %{z}<extra></extra>",
            colorbar=dict(title="Listings"),
        )
    )
    fig.update_layout(
        margin=dict(t=10, b=40, l=60, r=10),
        xaxis_title="Month",
        yaxis_title="Year",
        plot_bgcolor="white",
    )
    return fig

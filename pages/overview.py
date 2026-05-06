import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from data_loader import load_data

dash.register_page(__name__, path="/", name="Overview", title="Market Overview")

df_clean, df_final, _ = load_data()

# ── Helpers ──────────────────────────────────────────────────────────────────
PRICE_MIN  = int(df_final["average_rate_per_night"].min())
PRICE_MAX  = int(df_final["average_rate_per_night"].max())
PRICE_P95  = int(df_final["average_rate_per_night"].quantile(0.95))  # sensible slider cap


def make_kpi_card(title, value_id, icon, color):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(icon, className="fs-2 mb-1"),
                html.P(title, className="text-muted small mb-1"),
                html.H4(id=value_id, className="fw-bold mb-0"),
            ],
            className="text-center",
        ),
        className=f"border-top border-4 border-{color} shadow-sm h-100",
    )


# ── Layout ───────────────────────────────────────────────────────────────────
layout = dbc.Container(
    [
        # Page header
        dbc.Row(
            dbc.Col(
                html.Div(
                    [
                        html.H2("Market Overview", className="fw-bold mb-0"),
                        html.P(
                            "A snapshot of the entire Texas Airbnb market.",
                            className="text-muted",
                        ),
                    ]
                )
            ),
            className="mb-3",
        ),

        # ── Global price filter ──────────────────────────────────────────────
        dbc.Card(
            dbc.CardBody(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Label(
                                "Filter by Nightly Price Range ($)",
                                className="fw-semibold",
                            ),
                            width=12,
                        ),
                        dbc.Col(
                            dcc.RangeSlider(
                                id="overview-price-slider",
                                min=PRICE_MIN,
                                max=PRICE_MAX,
                                step=1,
                                value=[PRICE_MIN, PRICE_MAX],
                                pushable=10,
                                marks={
                                    PRICE_MIN: f"${PRICE_MIN}",
                                    # int(PRICE_P95 * 0.33): f"${int(PRICE_P95 * 0.33)}",
                                    # int(PRICE_P95 * 0.66): f"${int(PRICE_P95 * 0.66)}",
                                    # PRICE_P95: f"${PRICE_P95}",
                                    PRICE_MAX: f"${PRICE_MAX}"
                                },
                                tooltip={"placement": "bottom", "always_visible": True},
                                allowCross=False,
                            ),
                            width=12,
                            className="pt-3",
                        ),
                    ]
                )
            ),
            className="shadow-sm mb-4",
        ),

        # ── KPI Cards ────────────────────────────────────────────────────────
        dbc.Row(
            [
                dbc.Col(make_kpi_card("Total Listings",      "kpi-total",   "🏠", "primary"), md=3),
                dbc.Col(make_kpi_card("Median Nightly Rate", "kpi-median",  "💲", "success"), md=3),
                dbc.Col(make_kpi_card("Most Active City",    "kpi-city",    "📍", "warning"), md=3),
                dbc.Col(make_kpi_card("Avg Bedrooms",        "kpi-bedrooms","🛏️", "info"),   md=3),
            ],
            className="mb-4 g-3",
        ),

        # ── Price Distribution ───────────────────────────────────────────────
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("Price Distribution", className="card-title fw-semibold"),
                            html.P(
                                "Distribution of nightly rates across Texas listings. "
                                "Use the slider above to focus on a specific price range.",
                                className="text-muted small",
                            ),
                            dcc.Graph(id="overview-histogram", config={"displayModeBar": False}),
                        ]
                    ),
                    className="shadow-sm",
                )
            ),
            className="mb-4",
        ),

        # ── Top Cities + Bedroom Distribution ────────────────────────────────
        dbc.Row(
            [
                # Top N cities
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Top Cities by Listing Count", className="card-title fw-semibold"),
                                html.P(
                                    "Drag the slider to change how many cities are shown.",
                                    className="text-muted small",
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.Label("Show top N cities:", className="fw-semibold small"),
                                            width=12,
                                        ),
                                        dbc.Col(
                                            dcc.Slider(
                                                id="overview-n-cities-slider",
                                                min=5,
                                                max=20,
                                                step=5,
                                                value=10,
                                                marks={5: "5", 10: "10", 15: "15", 20: "20"},
                                            ),
                                            width=12,
                                            className="mb-3",
                                        ),
                                    ]
                                ),
                                dcc.Graph(id="overview-cities-bar", config={"displayModeBar": False}),
                            ]
                        ),
                        className="shadow-sm h-100",
                    ),
                    md=7,
                ),

                # Bedroom distribution
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Bedroom Count Distribution", className="card-title fw-semibold"),
                                html.P(
                                    "How many listings exist for each bedroom count.",
                                    className="text-muted small",
                                ),
                                dcc.Graph(id="overview-bedroom-bar", config={"displayModeBar": False}),
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


# ── Callbacks ────────────────────────────────────────────────────────────────
@callback(
    Output("kpi-total",    "children"),
    Output("kpi-median",   "children"),
    Output("kpi-city",     "children"),
    Output("kpi-bedrooms", "children"),
    Input("overview-price-slider", "value"),
)
def update_kpis(price_range):
    low, high = price_range[0], max(price_range[1], price_range[0] + 10)
    filtered = df_final[
        (df_final["average_rate_per_night"] >= low) &
        (df_final["average_rate_per_night"] <= high)
    ]
    if filtered.empty:
        return "0", "N/A", "N/A", "N/A"
    total    = f"{len(filtered):,}"
    median   = f"${filtered['average_rate_per_night'].median():.0f}"
    top_city = filtered["city"].value_counts().index[0]
    avg_bed  = f"{filtered['bedrooms_count'].mean():.1f}"
    return total, median, top_city, avg_bed


@callback(
    Output("overview-histogram", "figure"),
    Input("overview-price-slider", "value"),
)
def update_histogram(price_range):
    # Notebook cell 10 — converted from seaborn to px.histogram
    low, high = price_range[0], max(price_range[1], price_range[0] + 10)
    filtered = df_final[
        (df_final["average_rate_per_night"] >= low) &
        (df_final["average_rate_per_night"] <= high)
    ]
    if filtered.empty:
        return px.histogram(title="No listings in this price range", template="plotly_white")

    prices = filtered["average_rate_per_night"].to_numpy()
    span = max(high - low, 1)

    # Snap bin width to a "nice" number based on the slider span — keeps bars
    # aligned to readable price ticks and avoids fractional-dollar gaps.
    nice_widths = [1, 2, 5, 10, 25, 50, 100]
    target = span / 25
    bin_width = next((w for w in nice_widths if w >= target), nice_widths[-1])

    # Don't ask for more bins than the data can fill.
    max_bins_by_density = max(5, len(prices) // 3)
    n_bins = min(int(np.ceil(span / bin_width)), max_bins_by_density)
    bin_width = span / n_bins

    bin_edges = np.linspace(low, high, n_bins + 1)
    counts, _ = np.histogram(prices, bins=bin_edges)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Smooth the bar heights with a small Gaussian kernel for a polished
    # density-curve overlay (no scipy needed).
    kernel_size = max(3, n_bins // 6 | 1)  # odd number
    sigma = kernel_size / 3
    x = np.arange(kernel_size) - kernel_size // 2
    kernel = np.exp(-(x**2) / (2 * sigma**2))
    kernel /= kernel.sum()
    smoothed = np.convolve(counts, kernel, mode="same")

    median_price = float(np.median(prices))

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=bin_centers,
            y=counts,
            width=bin_width * 0.95,
            marker=dict(color="#20c997", line=dict(width=0)),
            opacity=0.55,
            hovertemplate="<b>$%{x:.0f}</b><br>%{y} listings<extra></extra>",
            name="Listings",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=bin_centers,
            y=smoothed,
            mode="lines",
            line=dict(color="#0f766e", width=2.5, shape="spline", smoothing=1.0),
            fill="tozeroy",
            fillcolor="rgba(32, 201, 151, 0.18)",
            hoverinfo="skip",
            name="Density",
        )
    )
    fig.add_vline(
        x=median_price,
        line=dict(color="#475569", width=1.5, dash="dash"),
        annotation_text=f"Median ${median_price:.0f}",
        annotation_position="top",
        annotation_font_size=11,
        annotation_font_color="#475569",
    )
    fig.update_layout(
        margin=dict(t=30, b=50, l=50, r=20),
        bargap=0.02,
        showlegend=False,
        yaxis_title="Number of Listings",
        xaxis_title="Price per Night ($)",
        xaxis=dict(range=[low, high], showgrid=False, ticks="outside", tickcolor="rgba(0,0,0,0.2)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.06)", zeroline=False),
        plot_bgcolor="white",
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    return fig


@callback(
    Output("overview-cities-bar", "figure"),
    Input("overview-n-cities-slider", "value"),
)
def update_cities_bar(n_cities):
    # Notebook cell 11 — uses df_clean (pre-IQR, no price filter) to match exactly
    top_n = (
        df_clean["city"]
        .value_counts()
        .head(n_cities)
        .reset_index()
    )
    top_n.columns = ["city", "count"]

    fig = px.bar(
        top_n,
        x="city",
        y="count",
        color="count",
        color_continuous_scale="Viridis",
        labels={"city": "City", "count": "Number of Listings"},
        template="plotly_white",
    )
    fig.update_layout(
        margin=dict(t=10, b=60, l=40, r=10),
        coloraxis_showscale=False,
        xaxis_tickangle=-35,
        yaxis_title="Number of Listings",
        xaxis_title="",
    )
    return fig


@callback(
    Output("overview-bedroom-bar", "figure"),
    Input("overview-price-slider", "value"),
)
def update_bedroom_bar(price_range):
    # Notebook cell 19 — converted from seaborn countplot to px.bar
    low, high = price_range[0], max(price_range[1], price_range[0] + 10)
    filtered = df_final[
        (df_final["average_rate_per_night"] >= low) &
        (df_final["average_rate_per_night"] <= high)
    ]
    if filtered.empty:
        return px.bar(title="No listings in this price range", template="plotly_white")
    bedroom_counts = (
        filtered["bedrooms_count"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    bedroom_counts.columns = ["bedrooms", "count"]
    bedroom_counts["bedrooms"] = bedroom_counts["bedrooms"].astype(int).astype(str)
    bedroom_counts.loc[bedroom_counts["bedrooms"] == "0", "bedrooms"] = "Studio"

    fig = px.bar(
        bedroom_counts,
        x="bedrooms",
        y="count",
        color="count",
        color_continuous_scale="Blues",
        labels={"bedrooms": "Bedrooms", "count": "Listings"},
        template="plotly_white",
    )
    fig.update_layout(
        margin=dict(t=10, b=40, l=40, r=10),
        coloraxis_showscale=False,
        yaxis_title="Number of Listings",
        xaxis_title="Bedrooms",
    )
    return fig

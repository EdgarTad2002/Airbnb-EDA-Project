import numpy as np
import pandas as pd

_cache = {}


def load_data():
    """
    Runs the full cleaning pipeline from the notebook (cells 5, 6, 9, 15, 22, 31)
    and returns two cleaned DataFrames:
        df_final  — used for overview, map, and trends pages
        df_story  — df_final + price_per_bedroom, used for city intelligence page
    Results are cached after the first call so the CSV is only read once.
    """
    if "df_final" in _cache:
        return _cache["df_final"], _cache["df_story"]

    # --- Cell 2: Load ---
    df = pd.read_csv("Airbnb_Texas_Rentals.csv")

    # --- Cell 5: Drop unnamed index column ---
    df = df.drop("Unnamed: 0", axis=1)

    # --- Cell 6: Clean price column ---
    df["average_rate_per_night"] = (
        df["average_rate_per_night"]
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df["average_rate_per_night"] = pd.to_numeric(
        df["average_rate_per_night"], errors="coerce"
    )

    # --- Cell 9: Clean bedrooms column ---
    df["bedrooms_count"] = df["bedrooms_count"].replace("Studio", "0")
    df["bedrooms_count"] = pd.to_numeric(df["bedrooms_count"], errors="coerce")
    df.dropna(subset=["average_rate_per_night", "bedrooms_count"], inplace=True)

    # --- Cell 15: Remove extreme outliers (4 × IQR rule) ---
    Q1 = df["average_rate_per_night"].quantile(0.25)
    Q3 = df["average_rate_per_night"].quantile(0.75)
    IQR = Q3 - Q1
    extreme_upper_limit = Q3 + 4 * IQR
    df_final = df[df["average_rate_per_night"] <= extreme_upper_limit].copy()

    # --- Cell 22: Parse dates and extract year / month ---
    df_final["date_of_listing"] = pd.to_datetime(
        df_final["date_of_listing"], format="%B %Y", errors="coerce"
    )
    df_final["listing_year"] = df_final["date_of_listing"].dt.year
    df_final["listing_month"] = df_final["date_of_listing"].dt.month

    # --- Cell 31: Feature engineering for the story / city page ---
    cols_to_drop = ["url", "description", "title"]
    df_story = df_final.drop(
        columns=[c for c in cols_to_drop if c in df_final.columns]
    ).copy()
    df_story["price_per_bedroom"] = df_story["average_rate_per_night"] / df_story[
        "bedrooms_count"
    ].replace(0, 1)
    df_story = df_story.replace([np.inf, -np.inf], np.nan).dropna(
        subset=["price_per_bedroom"]
    )

    _cache["df_final"] = df_final
    _cache["df_story"] = df_story
    return df_final, df_story

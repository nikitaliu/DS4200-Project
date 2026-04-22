"""
PRD-aligned data cleaning and feature engineering pipeline for the
Massachusetts housing analysis project.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ANALYSIS_YEAR = 2025
RENT_MULTIPLIER = 1.1

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT / "data" / "raw" / "ma_housing_raw.csv"
OUTPUT_PATH = ROOT / "data" / "ma_housing_cleaned.csv"
LEGACY_OUTPUTS = [
    ROOT / "data" / "processed" / "housing_cleaned.csv",
    ROOT / "data" / "processed" / "merged_data.csv",
]
TOWN_SUMMARY_OUTPUT = ROOT / "data" / "town_summary.csv"
ANALYSIS_SUMMARY_OUTPUT = ROOT / "data" / "analysis_summary.json"

CENSUS_CANDIDATES = [
    ROOT / "data" / "census_town_profiles.csv",
    ROOT / "data" / "census_income.csv",
    ROOT / "data" / "processed" / "census_data.csv",
]

PRICE_QUARTILE_LABELS = ["Q1-Budget", "Q2-Moderate", "Q3-Upper", "Q4-Premium"]

PROPERTY_TYPE_ALIASES = {
    "single family": "Single Family",
    "singlefamily": "Single Family",
    "single_family": "Single Family",
    "single-family": "Single Family",
    "house": "Single Family",
    "condo": "Condo",
    "condominium": "Condo",
    "townhouse": "Townhouse",
    "townhome": "Townhouse",
    "town house": "Townhouse",
    "multi family": "Multi Family",
    "multi-family": "Multi Family",
    "multifamily": "Multi Family",
    "multi family home": "Multi Family",
    "duplex": "Multi Family",
    "triplex": "Multi Family",
}

TOWN_ALIASES = {
    "manchester by the sea": "manchester",
    "north attleborough": "north attleboro",
    "allston": "boston",
    "auburndale": "newton",
    "brighton": "boston",
    "buzzards bay": "bourne",
    "cataumet": "bourne",
    "centerville": "barnstable",
    "charlestown": "boston",
    "chestnut hill": "newton",
    "chestnuthill": "newton",
    "cotuit": "barnstable",
    "dennis port": "dennis",
    "dennis pt": "dennis",
    "dorchester": "boston",
    "dorchester center": "boston",
    "east boston": "boston",
    "east dennis": "dennis",
    "east falmouth": "falmouth",
    "east sandwich": "sandwich",
    "east wareham": "wareham",
    "feeding hills": "agawam",
    "fiskdale": "sturbridge",
    "forestdale": "sandwich",
    "foxboro": "foxborough",
    "gilbertville": "hardwick",
    "harwich pt": "harwich",
    "harwich port": "harwich",
    "hyannis": "barnstable",
    "hyannis port": "barnstable",
    "hyde park": "boston",
    "indian orchard": "springfield",
    "jefferson": "worcester",
    "jamaica plain": "boston",
    "lanesboro": "lanesborough",
    "marstons mills": "barnstable",
    "mattapan": "boston",
    "middleboro": "middleborough",
    "monroe bridge": "monroe",
    "needham heights": "needham",
    "new marlboro": "new marlborough",
    "newton highlands": "newton",
    "newton center": "newton",
    "newton upper falls": "newton",
    "newtonville": "newton",
    "north billerica": "billerica",
    "north chelmsford": "chelmsford",
    "north chatham": "chatham",
    "north dartmouth": "dartmouth",
    "north easton": "easton",
    "north falmouth": "falmouth",
    "north grafton": "grafton",
    "north oxford": "oxford",
    "north truro": "truro",
    "north weymouth": "weymouth",
    "onset": "wareham",
    "osterville": "barnstable",
    "pikeville": "charlton",
    "pocasset": "bourne",
    "rochdale": "leicester",
    "roslindale": "boston",
    "roxbury": "boston",
    "roxbury crossing": "boston",
    "sagamore beach": "bourne",
    "sagamore": "bourne",
    "shelburne falls": "shelburne",
    "south boston": "boston",
    "south chatham": "chatham",
    "south deerfield": "deerfield",
    "south dennis": "dennis",
    "south dartmouth": "dartmouth",
    "south easton": "easton",
    "south egremont": "egremont",
    "south grafton": "grafton",
    "south hamilton": "hamilton",
    "south weymouth": "weymouth",
    "south yarmouth": "yarmouth",
    "three rivers": "palmer",
    "turners falls": "montague",
    "tyngsboro": "tyngsborough",
    "waban": "newton",
    "wellesley hills": "wellesley",
    "west barnstable": "barnstable",
    "west dennis": "dennis",
    "west harwich": "harwich",
    "west hyannisport": "barnstable",
    "west newton": "newton",
    "west roxbury": "boston",
    "west wareham": "wareham",
    "west yarmouth": "yarmouth",
    "whitinsville": "northbridge",
    "woods hole": "falmouth",
    "yarmouthport": "yarmouth",
    "yarmouth port": "yarmouth",
}

HISTORY_PATTERN = re.compile(
    r"\{'date':\s*'([^']+)',\s*'event':\s*'([^']+)'(?:,\s*'price':\s*'([^']*)')?\}"
)
ZPID_PATTERN = re.compile(r"/(\d+)_zpid/")
NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")


def parse_currency(value: object) -> float:
    if pd.isna(value):
        return np.nan
    text = str(value).strip()
    if not text:
        return np.nan
    cleaned = re.sub(r"[^0-9.\-]", "", text)
    if not cleaned or cleaned in {".", "-", "-.", ".-"}:
        return np.nan
    return float(cleaned)


def parse_score(value: object) -> float:
    if pd.isna(value):
        return np.nan
    match = re.search(r"(\d+)", str(value))
    return float(match.group(1)) if match else np.nan


def parse_risk(value: object) -> float:
    if pd.isna(value):
        return np.nan
    match = re.search(r"\((\d+)/10\)", str(value))
    if match:
        return float(match.group(1))
    match = re.search(r"(\d+)", str(value))
    return float(match.group(1)) if match else np.nan


def parse_distance_miles(value: object) -> float:
    if pd.isna(value):
        return np.nan
    match = re.search(r"(\d+(?:\.\d+)?)", str(value))
    return float(match.group(1)) if match else np.nan


def normalize_town_name(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = text.replace("st.", "saint").replace("mt.", "mount")
    text = text.replace(" town", "").replace(" city", "").replace(" cdp", "")
    text = NON_ALNUM_PATTERN.sub(" ", text).strip()
    return TOWN_ALIASES.get(text, text)


def standardize_property_type(value: object) -> str:
    if pd.isna(value):
        return np.nan
    key = NON_ALNUM_PATTERN.sub(" ", str(value).strip().lower()).strip()
    return PROPERTY_TYPE_ALIASES.get(key, str(value).strip().title())


def first_valid(series: pd.Series) -> object:
    non_null = series.dropna()
    return non_null.iloc[0] if not non_null.empty else np.nan


def parse_property_history(history: object) -> pd.Series:
    if pd.isna(history):
        return pd.Series(
            {
                "pastSalePrice": np.nan,
                "pastSaleDate": pd.NaT,
                "listingDate": pd.NaT,
                "yearsSinceLastSale": np.nan,
            }
        )

    events = []
    for date_str, event, price_str in HISTORY_PATTERN.findall(str(history)):
        events.append(
            {
                "date": pd.to_datetime(date_str, errors="coerce"),
                "event": event.strip().lower(),
                "price": parse_currency(price_str),
            }
        )

    if not events:
        return pd.Series(
            {
                "pastSalePrice": np.nan,
                "pastSaleDate": pd.NaT,
                "listingDate": pd.NaT,
                "yearsSinceLastSale": np.nan,
            }
        )

    listing_dates = [event["date"] for event in events if "listed for sale" in event["event"]]
    listing_date = max(listing_dates) if listing_dates else pd.Timestamp(f"{ANALYSIS_YEAR}-12-31")

    sold_events = [
        event
        for event in events
        if event["event"] == "sold" and pd.notna(event["date"]) and pd.notna(event["price"])
    ]
    sold_events.sort(key=lambda event: event["date"], reverse=True)
    latest_sale = sold_events[0] if sold_events else None

    years_since_last_sale = np.nan
    if latest_sale and pd.notna(listing_date):
        years_since_last_sale = (listing_date - latest_sale["date"]).days / 365.25
        if years_since_last_sale <= 0:
            years_since_last_sale = np.nan

    return pd.Series(
        {
            "pastSalePrice": latest_sale["price"] if latest_sale else np.nan,
            "pastSaleDate": latest_sale["date"] if latest_sale else pd.NaT,
            "listingDate": listing_date,
            "yearsSinceLastSale": years_since_last_sale,
        }
    )


def load_census_data() -> pd.DataFrame:
    for candidate in CENSUS_CANDIDATES:
        if candidate.exists():
            census_df = pd.read_csv(candidate)
            break
    else:
        return pd.DataFrame(columns=["town", "townKey", "medianHouseholdIncome", "medianHomeValueCensus"])

    town_column = "town" if "town" in census_df.columns else "townName"
    income_column = "medianHouseholdIncome" if "medianHouseholdIncome" in census_df.columns else "medianIncome"

    census_df = census_df.rename(
        columns={
            town_column: "town",
            income_column: "medianHouseholdIncome",
        }
    )
    census_df["town"] = census_df["town"].astype(str).str.strip()
    census_df["townKey"] = census_df["town"].map(normalize_town_name)
    census_df["medianHouseholdIncome"] = pd.to_numeric(
        census_df["medianHouseholdIncome"], errors="coerce"
    )
    if "medianHomeValueCensus" in census_df.columns:
        census_df["medianHomeValueCensus"] = pd.to_numeric(
            census_df["medianHomeValueCensus"], errors="coerce"
        )
    else:
        census_df["medianHomeValueCensus"] = np.nan
    census_df = census_df.drop_duplicates(subset=["townKey"], keep="first")
    return census_df[["town", "townKey", "medianHouseholdIncome", "medianHomeValueCensus"]]


def build_town_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("cityKey")
        .agg(
            sourceTown=("city", first_valid),
            censusTown=("town", first_valid),
            listingCount=("listingId", "nunique"),
            medianListingPrice=("price", "median"),
            meanListingPrice=("price", "mean"),
            medianPricePerSqFt=("pricePerSqFt", "median"),
            medianEstimatedMonthlyPayment=("estimatedMonthlyPayment", "median"),
            medianHouseholdIncome=("medianHouseholdIncome", first_valid),
            medianHomeValueCensus=("medianHomeValueCensus", first_valid),
            medianBedrooms=("bedrooms", "median"),
            medianBathrooms=("bathrooms", "median"),
            estimatedCapRate=("estimatedCapRate", "median"),
            environmentalRiskComposite=("environmentalRiskComposite", "median"),
            livabilityComposite=("livabilityComposite", "median"),
        )
        .reset_index()
    )

    summary["priceToIncomeRatio"] = (
        summary["medianListingPrice"] / summary["medianHouseholdIncome"]
    ).replace([np.inf, -np.inf], np.nan)
    summary["monthlyAffordabilityIndexTown"] = (
        (summary["medianHouseholdIncome"] / 12) / summary["medianEstimatedMonthlyPayment"]
    ).replace([np.inf, -np.inf], np.nan)
    summary["town"] = (
        summary["censusTown"]
        .fillna(summary["sourceTown"])
        .fillna(summary["cityKey"].str.title())
    )
    summary = summary.drop(columns=["sourceTown", "censusTown"])
    return summary


def compute_sensitivity(df: pd.DataFrame) -> dict[str, float]:
    sensitivity_columns = ["price", "sqft", "livabilityComposite", "environmentalRiskComposite"]
    model_df = df[sensitivity_columns].dropna()
    if model_df.empty:
        return {}

    y = model_df["price"].to_numpy()
    x = model_df[["sqft", "livabilityComposite", "environmentalRiskComposite"]].to_numpy()
    x = np.column_stack([np.ones(len(model_df)), x])
    coefficients, *_ = np.linalg.lstsq(x, y, rcond=None)

    predictor_names = ["sqft", "livabilityComposite", "environmentalRiskComposite"]
    sensitivity = {}
    for index, predictor in enumerate(predictor_names, start=1):
        sensitivity[predictor] = float(
            coefficients[index] * model_df[predictor].std(ddof=0)
        )
    return sensitivity


def write_analysis_summary(
    df: pd.DataFrame,
    town_summary: pd.DataFrame,
    *,
    duplicates_removed: int,
    state_filtered_out: int,
    valid_price_rows: int,
    outliers_removed: int,
) -> None:
    priced_towns = town_summary.dropna(subset=["medianListingPrice"]).copy()
    income_towns = town_summary.dropna(subset=["priceToIncomeRatio"]).copy()
    glossary_town = income_towns[income_towns["town"].str.lower() == "boston"]
    if glossary_town.empty:
        glossary_town = income_towns.head(1)

    glossary_listing = df[
        df[
            [
                "price",
                "sqft",
                "pricePerSqFt",
                "pastSalePrice",
                "priceAppreciation",
                "annualizedAppreciation",
                "estimatedCapRate",
                "grossRentMultiplier",
                "livabilityComposite",
                "environmentalRiskComposite",
            ]
        ].notna().all(axis=1)
    ].head(1)

    correlation_columns = [
        "price",
        "pricePerSqFt",
        "sqft",
        "bedrooms",
        "bathrooms",
        "ageOfHome",
        "walkScore",
        "bikeScore",
        "transitScore",
        "floodRisk",
        "fireRisk",
        "windRisk",
        "heatRisk",
        "airQualityRisk",
        "priceToIncomeRatio",
        "environmentalRiskComposite",
        "livabilityComposite",
    ]
    price_correlations = (
        df[correlation_columns]
        .corr(numeric_only=True)["price"]
        .drop(labels=["price"])
        .dropna()
        .sort_values(ascending=False)
    )

    summary = {
        "listingCount": int(len(df)),
        "townCount": int(len(town_summary)),
        "listingLabelCount": int(df["city"].nunique()),
        "rawRowCount": int(pd.read_csv(RAW_DATA_PATH, usecols=["price"]).shape[0]),
        "duplicatesRemoved": int(duplicates_removed),
        "nonMassachusettsRowsRemoved": int(state_filtered_out),
        "outliersRemoved": int(outliers_removed),
        "validPriceCount": int(valid_price_rows),
        "listingCountWithIncomeMatch": int(df["medianHouseholdIncome"].notna().sum()),
        "statewideMedianPrice": float(df["price"].median()),
        "statewideMeanPrice": float(df["price"].mean()),
        "top10TownsByMedianPrice": priced_towns.nlargest(10, "medianListingPrice")[
            ["town", "medianListingPrice", "listingCount"]
        ].to_dict(orient="records"),
        "bottom10TownsByMedianPrice": priced_towns.nsmallest(10, "medianListingPrice")[
            ["town", "medianListingPrice", "listingCount"]
        ].to_dict(orient="records"),
        "incomeCoverageTownCount": int(income_towns.shape[0]),
        "unaffordableTownCount": int(
            town_summary["monthlyAffordabilityIndexTown"].lt(1).fillna(False).sum()
        ),
        "priceToIncomeMaxTown": income_towns.nlargest(1, "priceToIncomeRatio")[
            ["town", "priceToIncomeRatio"]
        ].to_dict(orient="records"),
        "priceToIncomeMinTown": income_towns.nsmallest(1, "priceToIncomeRatio")[
            ["town", "priceToIncomeRatio"]
        ].to_dict(orient="records"),
        "environmentalRiskPriceCorrelation": float(
            price_correlations.get("environmentalRiskComposite", np.nan)
        ),
        "topPositivePriceCorrelations": [
            {"variable": index, "correlation": float(value)}
            for index, value in price_correlations.head(3).items()
        ],
        "topNegativePriceCorrelations": [
            {"variable": index, "correlation": float(value)}
            for index, value in price_correlations.tail(3).items()
        ],
        "sensitivityByOneStdDev": compute_sensitivity(df),
        "glossaryTownExample": glossary_town[
            ["town", "medianListingPrice", "medianHouseholdIncome", "priceToIncomeRatio"]
        ].to_dict(orient="records"),
        "glossaryListingExample": glossary_listing[
            [
                "city",
                "price",
                "sqft",
                "pricePerSqFt",
                "pastSalePrice",
                "priceAppreciation",
                "annualizedAppreciation",
                "estimatedCapRate",
                "grossRentMultiplier",
                "livabilityComposite",
                "environmentalRiskComposite",
            ]
        ].to_dict(orient="records"),
    }

    ANALYSIS_SUMMARY_OUTPUT.write_text(json.dumps(summary, indent=2))


def clean_housing_data() -> pd.DataFrame:
    print("=" * 72)
    print("MASSACHUSETTS HOUSING DATA CLEANING PIPELINE")
    print("=" * 72)
    print(f"Loading raw listings from {RAW_DATA_PATH.relative_to(ROOT)}")

    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Raw shape: {df.shape}")

    unnamed_columns = [column for column in df.columns if column.startswith("Unnamed")]
    if unnamed_columns:
        df = df.drop(columns=unnamed_columns)

    df = df.rename(
        columns={
            "beds": "bedrooms",
            "baths": "bathrooms",
            "region": "city",
            "property_type": "propertyType",
            "estimated_monthly_payment": "estimatedMonthlyPayment",
            "price_per_sqft": "pricePerSqFtRaw",
            "year_built": "yearBuilt",
            "walk_score": "walkScore",
            "bike_score": "bikeScore",
            "transit_score": "transitScore",
            "flood_risk": "floodRisk",
            "fire_risk": "fireRisk",
            "wind_risk": "windRisk",
            "heat_risk": "heatRisk",
            "air_risk": "airQualityRisk",
            "elementary_school_distance": "elementarySchoolDistance",
            "middle_school_distance": "middleSchoolDistance",
            "high_school_distance": "highSchoolDistance",
        }
    )

    df["listingId"] = df["url"].astype(str).str.extract(ZPID_PATTERN, expand=False)
    initial_rows = len(df)
    df = df.drop_duplicates(subset=["listingId"], keep="first")
    duplicates_removed = initial_rows - len(df)

    df["stateCode"] = df["address"].astype(str).str.extract(
        r",\s*([A-Z]{2})\s+\d{5}(?:-\d{4})?$", expand=False
    )
    df["stateCode"] = df["stateCode"].fillna(
        df["url"].astype(str).str.extract(r"-([A-Z]{2})-\d{5}", expand=False)
    )
    pre_state_filter_rows = len(df)
    df = df[df["stateCode"].fillna("MA") == "MA"].copy()
    state_filtered_out = pre_state_filter_rows - len(df)

    df["city"] = df["city"].astype(str).str.strip().str.title()
    df["cityKey"] = df["city"].map(normalize_town_name)
    df = df[df["cityKey"] != "edgartown"].copy()
    df["propertyType"] = df["propertyType"].map(standardize_property_type)

    numeric_columns = ["bedrooms", "bathrooms", "yearBuilt", "parking_total_spaces"]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["price"] = df["price"].map(parse_currency)
    df["sqft"] = df["sqft"].map(parse_currency)
    df["sqft_lot"] = df["sqft_lot"].map(parse_currency)
    df["estimatedMonthlyPayment"] = df["estimatedMonthlyPayment"].map(parse_currency)
    df["pricePerSqFtRaw"] = df["pricePerSqFtRaw"].map(parse_currency)

    for column in ["walkScore", "bikeScore", "transitScore"]:
        df[column] = df[column].map(parse_score)

    for column in ["floodRisk", "fireRisk", "windRisk", "heatRisk", "airQualityRisk"]:
        df[column] = df[column].map(parse_risk)

    for column in ["elementarySchoolDistance", "middleSchoolDistance", "highSchoolDistance"]:
        df[column] = df[column].map(parse_distance_miles)

    history_features = df["property_history"].apply(parse_property_history)
    df = pd.concat([df, history_features], axis=1)

    df["schoolDistance"] = df[
        ["elementarySchoolDistance", "middleSchoolDistance", "highSchoolDistance"]
    ].min(axis=1)

    df = df[df["price"].notna() & (df["price"] > 0)]
    valid_price_rows = len(df)

    outlier_mask = (df["price"] > 10_000_000) | (df["sqft"] > 15_000)
    outliers_removed = int(outlier_mask.sum())
    df = df.loc[~outlier_mask].copy()
    df = df.dropna(subset=["sqft", "bedrooms"]).copy()

    df["pricePerSqFt"] = (df["price"] / df["sqft"]).replace([np.inf, -np.inf], np.nan)
    df["ageOfHome"] = ANALYSIS_YEAR - df["yearBuilt"]
    df.loc[df["ageOfHome"] < 0, "ageOfHome"] = np.nan

    df["livabilityComposite"] = df[["walkScore", "bikeScore", "transitScore"]].mean(axis=1)
    df["environmentalRiskComposite"] = df[
        ["floodRisk", "fireRisk", "windRisk", "heatRisk", "airQualityRisk"]
    ].mean(axis=1)

    valid_past_sale = df["pastSalePrice"].notna() & (df["pastSalePrice"] > 0)
    df["priceAppreciation"] = np.where(
        valid_past_sale, (df["price"] - df["pastSalePrice"]) / df["pastSalePrice"], np.nan
    )
    df["annualizedAppreciation"] = np.where(
        valid_past_sale & df["yearsSinceLastSale"].notna() & (df["yearsSinceLastSale"] > 0),
        (df["price"] / df["pastSalePrice"]) ** (1 / df["yearsSinceLastSale"]) - 1,
        np.nan,
    )

    df["estimatedAnnualRent"] = df["estimatedMonthlyPayment"] * 12 * RENT_MULTIPLIER
    df["estimatedCapRate"] = (
        df["estimatedAnnualRent"] / df["price"] * 100
    ).replace([np.inf, -np.inf], np.nan)
    df["grossRentMultiplier"] = (
        df["price"] / df["estimatedAnnualRent"]
    ).replace([np.inf, -np.inf], np.nan)

    census_df = load_census_data()
    df = df.merge(census_df, left_on="cityKey", right_on="townKey", how="left")
    df = df.drop(columns=["townKey"], errors="ignore")
    df["monthlyAffordabilityIndexRow"] = (
        (df["medianHouseholdIncome"] / 12) / df["estimatedMonthlyPayment"]
    ).replace([np.inf, -np.inf], np.nan)

    town_summary = build_town_summary(df)
    df = df.merge(
        town_summary[
            [
                "cityKey",
                "medianListingPrice",
                "priceToIncomeRatio",
                "monthlyAffordabilityIndexTown",
                "listingCount",
            ]
        ],
        on="cityKey",
        how="left",
    )

    df["monthlyAffordabilityIndex"] = df["monthlyAffordabilityIndexTown"]

    df["priceQuartile"] = pd.qcut(
        df["price"], q=4, labels=PRICE_QUARTILE_LABELS, duplicates="drop"
    )

    df = df.sort_values(["city", "price"], ascending=[True, False]).reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    for legacy_output in LEGACY_OUTPUTS:
        legacy_output.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(legacy_output, index=False)

    town_summary.to_csv(TOWN_SUMMARY_OUTPUT, index=False)
    write_analysis_summary(
        df,
        town_summary,
        duplicates_removed=duplicates_removed,
        state_filtered_out=state_filtered_out,
        valid_price_rows=valid_price_rows,
        outliers_removed=outliers_removed,
    )

    print(f"Duplicate listing IDs removed: {duplicates_removed}")
    print(f"Outliers removed (price > $10M or sqft > 15,000): {outliers_removed}")
    print(f"Final shape: {df.shape}")
    print(f"Rows retained: {len(df):,}")
    print(f"Unique towns: {df['city'].nunique()}")
    print(f"Output written to: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Town summary written to: {TOWN_SUMMARY_OUTPUT.relative_to(ROOT)}")
    print(f"Analysis summary written to: {ANALYSIS_SUMMARY_OUTPUT.relative_to(ROOT)}")

    print("\nData types:")
    print(df.dtypes.sort_index())

    print("\nNull counts (top 25):")
    print(df.isna().sum().sort_values(ascending=False).head(25))

    print("\nSummary statistics:")
    print(df.describe(include="all").transpose().head(25))

    return df


def main() -> None:
    clean_housing_data()


if __name__ == "__main__":
    main()

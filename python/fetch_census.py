"""
Fetch Massachusetts ACS 5-year estimates for median household income and population.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from data_cleaning import ROOT, normalize_town_name


ACS_URL = "https://api.census.gov/data/2023/acs/acs5"
OUTPUT_PATH = ROOT / "data" / "census_income.csv"


def fetch_census_data() -> pd.DataFrame:
    load_dotenv()
    api_key = os.getenv("CENSUS_API_KEY")

    params = {
        "get": "NAME,B19013_001E,B01003_001E",
        "for": "county subdivision:*",
        "in": "state:25",
    }
    if api_key:
        params["key"] = api_key

    response = requests.get(ACS_URL, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()
    df = pd.DataFrame(payload[1:], columns=payload[0])
    df = df.rename(
        columns={
            "NAME": "rawName",
            "B19013_001E": "medianHouseholdIncome",
            "B01003_001E": "population",
        }
    )

    df["town"] = (
        df["rawName"]
        .str.replace(", Massachusetts", "", regex=False)
        .str.split(",")
        .str[0]
        .str.replace(" town", "", regex=False)
        .str.replace(" city", "", regex=False)
        .str.replace(" CDP", "", regex=False)
        .str.strip()
    )
    df["townKey"] = df["town"].map(normalize_town_name)
    df["medianHouseholdIncome"] = pd.to_numeric(df["medianHouseholdIncome"], errors="coerce")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")

    df = df.drop_duplicates(subset=["townKey"], keep="first")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df[["town", "townKey", "medianHouseholdIncome", "population"]].to_csv(
        OUTPUT_PATH, index=False
    )

    print(f"Saved {len(df)} Massachusetts county subdivisions to {OUTPUT_PATH.relative_to(ROOT)}")
    return df


def main() -> None:
    fetch_census_data()


if __name__ == "__main__":
    main()

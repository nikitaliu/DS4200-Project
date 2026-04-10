"""
Fetch Massachusetts ACS 5-year estimates for the dashboard and town profiles.
"""

from __future__ import annotations

import os
from functools import reduce

import pandas as pd
import requests
from dotenv import load_dotenv

from data_cleaning import ROOT, normalize_town_name


ACS_URL = "https://api.census.gov/data/2023/acs/acs5"
PROFILE_OUTPUT_PATH = ROOT / "data" / "census_town_profiles.csv"
INCOME_OUTPUT_PATH = ROOT / "data" / "census_income.csv"
LEGACY_OUTPUT_PATH = ROOT / "data" / "processed" / "census_data.csv"

AGE_COLUMNS = {
    "B01001_003E": "male_under_5",
    "B01001_004E": "male_5_9",
    "B01001_005E": "male_10_14",
    "B01001_006E": "male_15_17",
    "B01001_028E": "female_under_5",
    "B01001_029E": "female_5_9",
    "B01001_030E": "female_10_14",
    "B01001_031E": "female_15_17",
    "B01001_020E": "male_65_66",
    "B01001_021E": "male_67_69",
    "B01001_022E": "male_70_74",
    "B01001_023E": "male_75_79",
    "B01001_024E": "male_80_84",
    "B01001_025E": "male_85_plus",
    "B01001_044E": "female_65_66",
    "B01001_045E": "female_67_69",
    "B01001_046E": "female_70_74",
    "B01001_047E": "female_75_79",
    "B01001_048E": "female_80_84",
    "B01001_049E": "female_85_plus",
}

RACE_COLUMNS = {
    "B02001_001E": "race_total",
    "B02001_002E": "pop_white",
    "B02001_003E": "pop_black",
    "B02001_005E": "pop_asian",
}

TENURE_COLUMNS = {
    "B25003_002E": "ownerOccupied",
    "B25003_003E": "renterOccupied",
    "B25077_001E": "medianHomeValueCensus",
}

INCOME_COLUMNS = {
    "B19013_001E": "medianHouseholdIncome",
}

HISPANIC_COLUMNS = {
    "B03003_003E": "pop_hispanic",
}

EMPLOYMENT_COLUMNS = {
    "C24030_003E": "emp_agriculture",
    "C24030_006E": "emp_construction",
    "C24030_007E": "emp_manufacturing",
    "C24030_010E": "emp_wholesale",
    "C24030_013E": "emp_retail",
    "C24030_017E": "emp_information",
    "C24030_020E": "emp_finance_real_estate",
    "C24030_023E": "emp_professional",
    "C24030_027E": "emp_education_health",
    "C24030_030E": "emp_arts_food",
    "C24030_033E": "emp_other_services",
    "C24030_036E": "emp_public_administration",
}


def clean_town_label(raw_name: str) -> str:
    return (
        raw_name.replace(", Massachusetts", "")
        .split(",")[0]
        .replace(" town", "")
        .replace(" city", "")
        .replace(" CDP", "")
        .strip()
    )


def fetch_table(column_map: dict[str, str], api_key: str | None) -> pd.DataFrame:
    request_columns = ["NAME", *column_map.keys()]
    params = {
        "get": ",".join(request_columns),
        "for": "county subdivision:*",
        "in": "state:25",
    }
    if api_key:
        params["key"] = api_key

    response = requests.get(ACS_URL, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()

    df = pd.DataFrame(payload[1:], columns=payload[0]).rename(columns={"NAME": "rawName", **column_map})
    df["town"] = df["rawName"].map(clean_town_label)
    df["townKey"] = df["town"].map(normalize_town_name)

    numeric_columns = [name for name in column_map.values()]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    keep_columns = ["town", "townKey", *numeric_columns]
    return df[keep_columns].drop_duplicates(subset=["townKey"], keep="first")


def build_profile_dataset(api_key: str | None) -> pd.DataFrame:
    tables = [
        fetch_table(INCOME_COLUMNS, api_key),
        fetch_table(TENURE_COLUMNS, api_key),
        fetch_table(RACE_COLUMNS, api_key),
        fetch_table(HISPANIC_COLUMNS, api_key),
        fetch_table(AGE_COLUMNS, api_key),
        fetch_table(EMPLOYMENT_COLUMNS, api_key),
    ]

    profile_df = reduce(
        lambda left, right: left.merge(right, on=["town", "townKey"], how="outer"),
        tables,
    )

    under_18_columns = [
        "male_under_5",
        "male_5_9",
        "male_10_14",
        "male_15_17",
        "female_under_5",
        "female_5_9",
        "female_10_14",
        "female_15_17",
    ]
    age_65_plus_columns = [
        "male_65_66",
        "male_67_69",
        "male_70_74",
        "male_75_79",
        "male_80_84",
        "male_85_plus",
        "female_65_66",
        "female_67_69",
        "female_70_74",
        "female_75_79",
        "female_80_84",
        "female_85_plus",
    ]

    profile_df["ageUnder18"] = profile_df[under_18_columns].sum(axis=1, min_count=1)
    profile_df["age65Plus"] = profile_df[age_65_plus_columns].sum(axis=1, min_count=1)
    profile_df["age18to64"] = (
        profile_df["race_total"] - profile_df["ageUnder18"] - profile_df["age65Plus"]
    )
    profile_df["pop_other"] = (
        profile_df["race_total"]
        - profile_df["pop_white"]
        - profile_df["pop_black"]
        - profile_df["pop_asian"]
    )
    profile_df["ownerShare"] = profile_df["ownerOccupied"] / (
        profile_df["ownerOccupied"] + profile_df["renterOccupied"]
    )
    profile_df["renterShare"] = profile_df["renterOccupied"] / (
        profile_df["ownerOccupied"] + profile_df["renterOccupied"]
    )

    industry_columns = list(EMPLOYMENT_COLUMNS.values())
    profile_df["employmentTotalSelected"] = profile_df[industry_columns].sum(axis=1, min_count=1)
    dominant = profile_df[industry_columns].idxmax(axis=1)
    profile_df["dominantIndustry"] = dominant.map(
        {
            "emp_agriculture": "Agriculture and natural resources",
            "emp_construction": "Construction",
            "emp_manufacturing": "Manufacturing",
            "emp_wholesale": "Wholesale trade",
            "emp_retail": "Retail trade",
            "emp_information": "Information",
            "emp_finance_real_estate": "Finance and real estate",
            "emp_professional": "Professional services",
            "emp_education_health": "Education and health",
            "emp_arts_food": "Arts, food, and hospitality",
            "emp_other_services": "Other services",
            "emp_public_administration": "Public administration",
        }
    )

    profile_df = profile_df.drop_duplicates(subset=["townKey"], keep="first").sort_values("town")
    return profile_df


def fetch_census_data() -> pd.DataFrame:
    load_dotenv()
    api_key = os.getenv("CENSUS_API_KEY")

    profile_df = build_profile_dataset(api_key)

    PROFILE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    profile_df.to_csv(PROFILE_OUTPUT_PATH, index=False)
    profile_df[["town", "townKey", "medianHouseholdIncome"]].to_csv(INCOME_OUTPUT_PATH, index=False)
    LEGACY_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    profile_df.rename(
        columns={
            "town": "townName",
            "medianHouseholdIncome": "medianIncome",
        }
    )[["townName", "medianIncome", "medianHomeValueCensus"]].to_csv(
        LEGACY_OUTPUT_PATH, index=False
    )

    print(
        f"Saved {len(profile_df)} Massachusetts county subdivisions to "
        f"{PROFILE_OUTPUT_PATH.relative_to(ROOT)}"
    )
    return profile_df


def main() -> None:
    fetch_census_data()


if __name__ == "__main__":
    main()

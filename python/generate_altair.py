"""
Generate the Altair charts used in the Massachusetts housing dashboard.
"""

from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd

from data_cleaning import PRICE_QUARTILE_LABELS, ROOT


DATA_PATH = ROOT / "data" / "ma_housing_cleaned.csv"
OUTPUT_DIR = ROOT / "altair_charts"
PROPERTY_TYPE_DOMAIN = ["Single Family", "Condo", "Townhouse", "Multi Family"]
PROPERTY_TYPE_RANGE = ["#2b6cb0", "#e53e3e", "#38a169", "#d69e2e"]


def register_theme() -> None:
    @alt.theme.register("ma_housing", enable=True)
    def theme() -> alt.theme.ThemeConfig:
        return alt.theme.ThemeConfig(
            {
                "config": {
                    "background": "#ffffff",
                    "view": {"stroke": None},
                    "title": {"font": "Source Sans 3", "fontSize": 20, "color": "#1a365d"},
                    "axis": {
                        "labelFont": "Source Sans 3",
                        "titleFont": "Source Sans 3",
                        "labelColor": "#1f2d3d",
                        "titleColor": "#1a365d",
                        "gridColor": "#d7e3f0",
                        "domainColor": "#9bb0c8",
                        "tickColor": "#9bb0c8",
                    },
                    "legend": {
                        "labelFont": "Source Sans 3",
                        "titleFont": "Source Sans 3",
                        "labelColor": "#1f2d3d",
                        "titleColor": "#1a365d",
                    },
                    "range": {
                        "category": PROPERTY_TYPE_RANGE,
                        "heatmap": {"scheme": "redblue"},
                    },
                }
            }
        )


def load_data() -> pd.DataFrame:
    alt.data_transformers.disable_max_rows()
    return pd.read_csv(DATA_PATH)


def chart_scatter_price_drivers(df: pd.DataFrame) -> alt.Chart:
    chart_df = df[
        [
            "listingId",
            "city",
            "price",
            "propertyType",
            "sqft",
            "bedrooms",
            "yearBuilt",
            "livabilityComposite",
            "environmentalRiskComposite",
        ]
    ].dropna(subset=["price", "propertyType"])

    selector = alt.param(
        name="xMetric",
        value="sqft",
        bind=alt.binding_select(
            options=["sqft", "bedrooms", "yearBuilt", "livabilityComposite"],
            labels=["Square Footage", "Bedrooms", "Year Built", "Livability Composite"],
            name="X-axis feature ",
        ),
    )
    brush = alt.selection_interval(name="priceBrush")

    folded = (
        alt.Chart(chart_df)
        .transform_fold(
            ["sqft", "bedrooms", "yearBuilt", "livabilityComposite"],
            as_=["metric", "metricValue"],
        )
        .transform_calculate(
            metricValueJitter="""
            datum.metric === 'sqft'
              ? datum.metricValue + (random() - 0.5) * 90
              : datum.metric === 'yearBuilt'
                ? datum.metricValue + (random() - 0.5) * 2
                : datum.metricValue + (random() - 0.5) * 0.35
            """
        )
        .transform_filter("datum.metric === xMetric")
        .add_params(selector, brush)
    )

    view_selector = alt.param(
        name="scatterView",
        value="Dots",
        bind=alt.binding_radio(options=["Dots", "Density"], name="View "),
    )
    folded = folded.add_params(view_selector)

    points = (
        folded.transform_filter("scatterView === 'Dots'")
        .mark_circle(opacity=0.35, stroke="#ffffff", strokeWidth=0.5, size=44)
        .encode(
            x=alt.X("metricValueJitter:Q", title="Selected Driver"),
            y=alt.Y("price:Q", title="Listing Price ($)", scale=alt.Scale(zero=False)),
            color=alt.Color(
                "propertyType:N",
                title="Property Type",
                scale=alt.Scale(domain=PROPERTY_TYPE_DOMAIN, range=PROPERTY_TYPE_RANGE),
            ),
            size=alt.Size(
                "environmentalRiskComposite:Q",
                title="Environmental Risk Composite",
                scale=alt.Scale(range=[40, 500]),
            ),
            opacity=alt.condition(brush, alt.value(0.9), alt.value(0.2)),
            tooltip=[
                alt.Tooltip("city:N", title="Town"),
                alt.Tooltip("propertyType:N", title="Property Type"),
                alt.Tooltip("price:Q", title="Price", format="$,.0f"),
                alt.Tooltip("sqft:Q", title="Sqft", format=",.0f"),
                alt.Tooltip("bedrooms:Q", title="Bedrooms", format=".0f"),
                alt.Tooltip("yearBuilt:Q", title="Year Built", format=".0f"),
                alt.Tooltip("livabilityComposite:Q", title="Livability", format=".1f"),
                alt.Tooltip("environmentalRiskComposite:Q", title="Env. Risk", format=".1f"),
            ],
        )
        .properties(
            width=760,
            height=430,
            title="Price Drivers and Comparable Listing Selection",
        )
    )

    density = (
        folded.transform_filter("scatterView === 'Density'")
        .mark_rect()
        .encode(
            x=alt.X("metricValueJitter:Q", bin=alt.Bin(maxbins=38), title="Selected Driver"),
            y=alt.Y("price:Q", bin=alt.Bin(maxbins=38), title="Listing Price ($)"),
            color=alt.Color("count():Q", title="Listings", scale=alt.Scale(scheme="blues")),
            tooltip=[alt.Tooltip("count():Q", title="Listings in bin")],
        )
    )

    summary = (
        folded.transform_filter(brush)
        .transform_aggregate(
            selectedCount="count()",
            meanPrice="mean(price)",
            medianPrice="median(price)",
        )
        .transform_calculate(
            summaryText="'Selected listings: ' + datum.selectedCount + "
            "' | Mean price: $' + format(datum.meanPrice, ',.0f') + "
            "' | Median price: $' + format(datum.medianPrice, ',.0f')"
        )
        .mark_text(align="left", font="Source Sans 3", fontSize=14, color="#1a365d")
        .encode(text="summaryText:N")
        .properties(width=760, height=28)
    )

    return alt.vconcat((density + points).properties(width=760, height=430), summary, spacing=12)


def chart_grouped_bar_livability(df: pd.DataFrame) -> alt.Chart:
    chart_df = (
        df[["priceQuartile", "walkScore", "bikeScore", "transitScore"]]
        .dropna(subset=["priceQuartile"])
        .copy()
    )
    melted = chart_df.melt(
        id_vars=["priceQuartile"],
        value_vars=["walkScore", "bikeScore", "transitScore"],
        var_name="scoreType",
        value_name="score",
    )
    melted["scoreType"] = melted["scoreType"].map(
        {
            "walkScore": "Walk Score",
            "bikeScore": "Bike Score",
            "transitScore": "Transit Score",
        }
    )

    return (
        alt.Chart(melted)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("priceQuartile:N", title="Price Quartile", sort=PRICE_QUARTILE_LABELS),
            y=alt.Y("mean(score):Q", title="Average Score", scale=alt.Scale(domain=[0, 100])),
            xOffset=alt.XOffset("scoreType:N"),
            color=alt.Color(
                "scoreType:N",
                title="Livability Score",
                scale=alt.Scale(
                    domain=["Walk Score", "Bike Score", "Transit Score"],
                    range=["#2b6cb0", "#38a169", "#e53e3e"],
                ),
            ),
            tooltip=[
                alt.Tooltip("priceQuartile:N", title="Quartile"),
                alt.Tooltip("scoreType:N", title="Score Type"),
                alt.Tooltip("mean(score):Q", title="Average Score", format=".1f"),
            ],
        )
        .properties(
            width=760,
            height=420,
            title="Livability Premium by Listing Price Quartile",
        )
    )


def chart_heatmap_correlation(df: pd.DataFrame) -> alt.Chart:
    columns = [
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
    ]
    corr = df[columns].corr(numeric_only=True).stack().reset_index()
    corr.columns = ["variable1", "variable2", "correlation"]

    base = (
        alt.Chart(corr)
        .mark_rect()
        .encode(
            x=alt.X("variable1:N", title=None, sort=columns),
            y=alt.Y("variable2:N", title=None, sort=columns),
            color=alt.Color(
                "correlation:Q",
                title="Correlation",
                scale=alt.Scale(scheme="redblue", domain=[-1, 1]),
            ),
            tooltip=[
                alt.Tooltip("variable1:N", title="Variable A"),
                alt.Tooltip("variable2:N", title="Variable B"),
                alt.Tooltip("correlation:Q", title="Correlation", format=".3f"),
            ],
        )
    )
    overlay = (
        alt.Chart(corr)
        .transform_filter("abs(datum.correlation) >= 0.3")
        .mark_text(font="Source Sans 3", fontSize=10)
        .encode(
            x=alt.X("variable1:N", sort=columns),
            y=alt.Y("variable2:N", sort=columns),
            text=alt.Text("correlation:Q", format=".2f"),
            color=alt.condition(
                "abs(datum.correlation) >= 0.6",
                alt.value("white"),
                alt.value("#1a365d"),
            ),
        )
    )
    return (base + overlay).properties(
        width=640,
        height=640,
        title="Correlation Heatmap of Financial, Livability, and Risk Factors",
    )


def chart_income_vs_price(df: pd.DataFrame) -> alt.Chart:
    town_df = (
        df.groupby("cityKey")
        .agg(
            town=("city", "first"),
            medianHouseholdIncome=("medianHouseholdIncome", "first"),
            medianListingPrice=("price", "median"),
            priceToIncomeRatio=("priceToIncomeRatio", "first"),
        )
        .dropna(subset=["medianHouseholdIncome", "medianListingPrice"])
        .reset_index(drop=True)
    )

    max_income = town_df["medianHouseholdIncome"].max()
    line_df = pd.DataFrame(
        {
            "medianHouseholdIncome": [0, max_income],
            "affordablePrice": [0, max_income * 4],
        }
    )

    points = (
        alt.Chart(town_df)
        .mark_circle(opacity=0.82, stroke="#ffffff", strokeWidth=0.6)
        .encode(
            x=alt.X(
                "medianHouseholdIncome:Q",
                title="Median Household Income ($)",
                scale=alt.Scale(zero=False),
            ),
            y=alt.Y(
                "medianListingPrice:Q",
                title="Median Listing Price ($)",
                scale=alt.Scale(zero=False),
            ),
            color=alt.Color(
                "priceToIncomeRatio:Q",
                title="Price-to-Income Ratio",
                scale=alt.Scale(scheme="redyellowblue", reverse=True),
            ),
            tooltip=[
                alt.Tooltip("town:N", title="Town"),
                alt.Tooltip("medianHouseholdIncome:Q", title="Median Income", format="$,.0f"),
                alt.Tooltip("medianListingPrice:Q", title="Median Listing Price", format="$,.0f"),
                alt.Tooltip("priceToIncomeRatio:Q", title="Price-to-Income", format=".2f"),
            ],
        )
    )

    reference = (
        alt.Chart(line_df)
        .mark_line(strokeDash=[6, 5], color="#1a365d")
        .encode(
            x="medianHouseholdIncome:Q",
            y="affordablePrice:Q",
        )
    )

    return (
        (points + reference)
        .properties(
            width=760,
            height=460,
            title="Income vs. Housing Price by Massachusetts Town",
        )
        .interactive()
    )


def save_chart(chart: alt.Chart, filename: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    chart.save(str(OUTPUT_DIR / filename))


def main() -> None:
    register_theme()
    df = load_data()

    save_chart(chart_scatter_price_drivers(df), "scatter_price_drivers.html")
    save_chart(chart_grouped_bar_livability(df), "grouped_bar_livability.html")
    save_chart(chart_heatmap_correlation(df), "heatmap_correlation.html")
    save_chart(chart_income_vs_price(df), "income_vs_price.html")

    print(f"Saved Altair charts to {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

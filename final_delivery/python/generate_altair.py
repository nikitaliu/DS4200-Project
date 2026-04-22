"""
Generate the Altair charts used in the Massachusetts housing dashboard.
"""

from __future__ import annotations

from pathlib import Path

import altair as alt
import numpy as np
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
            "bathrooms",
            "yearBuilt",
            "ageOfHome",
            "livabilityComposite",
            "environmentalRiskComposite",
        ]
    ].dropna(subset=["price", "propertyType"])

    selector = alt.param(
        name="xMetric",
        value="sqft",
        bind=alt.binding_select(
            options=["sqft", "bathrooms", "bedrooms", "ageOfHome"],
            labels=["Square Footage", "Bathrooms", "Bedrooms", "Age of Home"],
            name="X-axis feature ",
        ),
    )
    property_filter = alt.param(
        name="propertyFilter",
        value="All",
        bind=alt.binding_select(
            options=["All", *PROPERTY_TYPE_DOMAIN],
            name="Property type ",
        ),
    )
    brush = alt.selection_interval(name="priceBrush")

    folded = (
        alt.Chart(chart_df)
        .transform_fold(
            ["sqft", "bathrooms", "bedrooms", "ageOfHome"],
            as_=["metric", "metricValue"],
        )
        .transform_calculate(
            metricValueJitter="""
            datum.metric === 'sqft'
              ? datum.metricValue + (random() - 0.5) * 90
              : datum.metric === 'ageOfHome'
                ? datum.metricValue + (random() - 0.5) * 2
                : datum.metricValue + (random() - 0.5) * 0.35
            """
        )
        .transform_filter("datum.metric === xMetric")
        .transform_filter("propertyFilter === 'All' || datum.propertyType === propertyFilter")
        .add_params(selector, property_filter, brush)
    )

    points = (
        folded.mark_circle(opacity=0.5, stroke="#ffffff", strokeWidth=0.5, size=22)
        .encode(
            x=alt.X("metricValueJitter:Q", title="Selected Driver"),
            y=alt.Y("price:Q", title="Listing Price ($)", scale=alt.Scale(zero=False)),
            color=alt.Color(
                "propertyType:N",
                title="Property Type",
                scale=alt.Scale(domain=PROPERTY_TYPE_DOMAIN, range=PROPERTY_TYPE_RANGE),
            ),
            opacity=alt.condition(brush, alt.value(0.85), alt.value(0.15)),
            tooltip=[
                alt.Tooltip("city:N", title="Town"),
                alt.Tooltip("propertyType:N", title="Property Type"),
                alt.Tooltip("price:Q", title="Price", format="$,.0f"),
                alt.Tooltip("sqft:Q", title="Sqft", format=",.0f"),
                alt.Tooltip("bathrooms:Q", title="Bathrooms", format=".1f"),
                alt.Tooltip("bedrooms:Q", title="Bedrooms", format=".0f"),
                alt.Tooltip("ageOfHome:Q", title="Age of Home", format=".0f"),
            ],
        )
    )

    regression_line = (
        folded
        .transform_regression("metricValueJitter", "price", method="linear")
        .mark_line(color="#1a365d", strokeWidth=2, opacity=0.65)
        .encode(
            x=alt.X("metricValueJitter:Q"),
            y=alt.Y("price:Q"),
        )
    )

    scatter_layer = (points + regression_line).properties(
        width=760,
        height=430,
        title="Price Drivers and Comparable Listing Selection",
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

    return alt.vconcat(scatter_layer, summary, spacing=12)


def chart_feature_importance(df: pd.DataFrame) -> alt.Chart:
    model_df = df[
        [
            "price",
            "sqft",
            "bathrooms",
            "bedrooms",
            "ageOfHome",
            "livabilityComposite",
            "environmentalRiskComposite",
        ]
    ].dropna()

    feature_columns = [
        "sqft",
        "bathrooms",
        "bedrooms",
        "ageOfHome",
        "livabilityComposite",
        "environmentalRiskComposite",
    ]

    x_raw = model_df[feature_columns]
    x = (x_raw - x_raw.mean()) / x_raw.std(ddof=0)
    y = (model_df["price"] - model_df["price"].mean()) / model_df["price"].std(ddof=0)

    coefficients, *_ = np.linalg.lstsq(x.to_numpy(), y.to_numpy(), rcond=None)

    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "standardizedEffect": coefficients,
        }
    )
    importance["featureLabel"] = importance["feature"].map(
        {
            "sqft": "Square Footage",
            "bathrooms": "Bathrooms",
            "bedrooms": "Bedrooms",
            "ageOfHome": "Age of Home",
            "livabilityComposite": "Livability Composite",
            "environmentalRiskComposite": "Environmental Risk Composite",
        }
    )
    importance["direction"] = importance["standardizedEffect"].apply(
        lambda value: "Positive association" if value >= 0 else "Negative association"
    )
    importance["absEffect"] = importance["standardizedEffect"].abs()
    importance = importance.sort_values("absEffect", ascending=False)

    base = alt.Chart(importance)
    bars = base.mark_bar(cornerRadiusEnd=6).encode(
        x=alt.X(
            "standardizedEffect:Q",
            title="Standardized Association With Price",
            axis=alt.Axis(format=".2f"),
        ),
        y=alt.Y(
            "featureLabel:N",
            sort=importance["featureLabel"].tolist(),
            title=None,
        ),
        color=alt.Color(
            "direction:N",
            title="Direction",
            scale=alt.Scale(
                domain=["Positive association", "Negative association"],
                range=["#2b6cb0", "#e53e3e"],
            ),
        ),
        tooltip=[
            alt.Tooltip("featureLabel:N", title="Feature"),
            alt.Tooltip("standardizedEffect:Q", title="Standardized effect", format=".3f"),
            alt.Tooltip("direction:N", title="Direction"),
        ],
    )
    labels = base.mark_text(
        align="left",
        baseline="middle",
        dx=6,
        font="Source Sans 3",
        fontSize=12,
        color="#1a365d",
    ).encode(
        x=alt.X("standardizedEffect:Q"),
        y=alt.Y("featureLabel:N", sort=importance["featureLabel"].tolist()),
        text=alt.Text("standardizedEffect:Q", format=".2f"),
    )
    rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="#6b7b91", strokeDash=[5, 4]).encode(
        x="x:Q"
    )

    return (rule + bars + labels).properties(
        width=760,
        height=280,
        title="Which Home Features Are Most Strongly Associated With Price?",
    )


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
            width="container",
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

    # Remove extreme price outliers (> 3×IQR fence) so the plot is readable
    q1 = town_df["medianListingPrice"].quantile(0.25)
    q3 = town_df["medianListingPrice"].quantile(0.75)
    iqr = q3 - q1
    town_df = town_df[town_df["medianListingPrice"] <= q3 + 3 * iqr].copy()

    max_income = town_df["medianHouseholdIncome"].max()
    line_df = pd.DataFrame(
        {
            "medianHouseholdIncome": [0, max_income],
            "affordablePrice": [0, max_income * 4],
        }
    )

    points = (
        alt.Chart(town_df)
        .mark_circle(size=55, opacity=0.82, stroke="#ffffff", strokeWidth=0.6)
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
                scale=alt.Scale(scheme="blues"),
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
        .mark_line(strokeDash=[6, 5], color="#e53e3e", strokeWidth=1.5)
        .encode(
            x="medianHouseholdIncome:Q",
            y="affordablePrice:Q",
        )
    )

    return (
        (points + reference)
        .properties(
            width="container",
            height=460,
            title="Income vs. Housing Price by Massachusetts Town",
        )
        .interactive()
    )


def chart_price_per_sqft(df: pd.DataFrame) -> alt.Chart:
    # ── Data prep (unchanged filtering logic) ─────────────────────────────
    chart_df = df[["propertyType", "price", "sqft"]].copy()
    chart_df = chart_df[
        chart_df["price"].notna() & (chart_df["price"] > 0) &
        chart_df["sqft"].notna() & (chart_df["sqft"] > 0)
    ].copy()
    chart_df["pricePerSqFt"] = chart_df["price"] / chart_df["sqft"]
    chart_df = chart_df[chart_df["pricePerSqFt"] >= 50].copy()
    p99 = chart_df["pricePerSqFt"].quantile(0.99)
    chart_df = chart_df[chart_df["pricePerSqFt"] <= p99].copy()
    chart_df = chart_df[chart_df["propertyType"].isin(PROPERTY_TYPE_DOMAIN)].copy()
    y_max = int(p99 / 100 + 1) * 100

    # ── Pre-compute IQR-fenced 5-number summaries per property type ────────
    # Using explicit loop avoids pandas apply() version quirks
    stats_rows = []
    for pt, grp in chart_df.groupby("propertyType")["pricePerSqFt"]:
        q1 = grp.quantile(0.25)
        q3 = grp.quantile(0.75)
        iqr = q3 - q1
        stats_rows.append({
            "propertyType": pt,
            "lower_whisker": grp[grp >= q1 - 1.5 * iqr].min(),
            "q1": q1,
            "median_val": grp.median(),
            "q3": q3,
            "upper_whisker": grp[grp <= q3 + 1.5 * iqr].max(),
        })
    stats = pd.DataFrame(stats_rows)

    # Pre-format tooltip strings so every label reads naturally in the panel
    _fmt = lambda v: f"${v:,.0f} / sqft"
    stats["tip_max"]    = stats["upper_whisker"].map(_fmt)
    stats["tip_q3"]     = stats["q3"].map(_fmt)
    stats["tip_median"] = stats["median_val"].map(_fmt)
    stats["tip_q1"]     = stats["q1"].map(_fmt)
    stats["tip_min"]    = stats["lower_whisker"].map(_fmt)

    # ── Shared encodings ──────────────────────────────────────────────────
    x_enc = alt.X("propertyType:N", title="Property Type", sort=PROPERTY_TYPE_DOMAIN)
    y_scale = alt.Scale(domain=[0, y_max])
    color_enc = alt.Color(
        "propertyType:N",
        scale=alt.Scale(domain=PROPERTY_TYPE_DOMAIN, range=PROPERTY_TYPE_RANGE),
        legend=None,
    )
    # Box/whisker layers share this tooltip — fully human-readable, no raw field names
    box_tooltip = [
        alt.Tooltip("propertyType:N",  title="Property Type"),
        alt.Tooltip("tip_max:N",        title="Max"),
        alt.Tooltip("tip_q3:N",         title="75th Percentile"),
        alt.Tooltip("tip_median:N",     title="Median"),
        alt.Tooltip("tip_q1:N",         title="25th Percentile"),
        alt.Tooltip("tip_min:N",        title="Min"),
    ]

    base = alt.Chart(stats)

    # ── Layers (back → front) ─────────────────────────────────────────────
    # 1. Jitter strip — individual points behind the box
    strip = (
        alt.Chart(chart_df)
        .transform_calculate(jitter="(random() - 0.5)")
        .mark_circle(opacity=0.2, size=8)
        .encode(
            x=x_enc,
            xOffset=alt.XOffset("jitter:Q", scale=alt.Scale(domain=[-1, 1])),
            y=alt.Y("pricePerSqFt:Q", scale=y_scale),
            color=color_enc,
            tooltip=[
                alt.Tooltip("propertyType:N", title="Property Type"),
                alt.Tooltip("pricePerSqFt:Q", title="Price / sqft", format=",.0f"),
            ],
        )
    )

    # 2. Lower whisker rule (lower_whisker → Q1)
    lower_rule = (
        base.mark_rule(strokeWidth=1.5)
        .encode(
            x=x_enc,
            y=alt.Y("lower_whisker:Q", scale=y_scale),
            y2=alt.Y2("q1:Q"),
            color=color_enc,
            tooltip=box_tooltip,
        )
    )

    # 3. Upper whisker rule (Q3 → upper_whisker)
    upper_rule = (
        base.mark_rule(strokeWidth=1.5)
        .encode(
            x=x_enc,
            y=alt.Y("q3:Q", scale=y_scale),
            y2=alt.Y2("upper_whisker:Q"),
            color=color_enc,
            tooltip=box_tooltip,
        )
    )

    # 4. IQR box (Q1 → Q3)
    iqr_box = (
        base.mark_bar(size=44)
        .encode(
            x=x_enc,
            y=alt.Y("q1:Q", title="Price per Square Foot ($/sqft)", scale=y_scale),
            y2=alt.Y2("q3:Q"),
            color=color_enc,
            tooltip=box_tooltip,
        )
    )

    # 5. Median tick — white line on top of the box
    median_tick = (
        base.mark_tick(thickness=3, size=44)
        .encode(
            x=x_enc,
            y=alt.Y("median_val:Q", scale=y_scale),
            color=alt.value("#ffffff"),
            tooltip=box_tooltip,
        )
    )

    return (strip + lower_rule + upper_rule + iqr_box + median_tick).properties(
        width=760,
        height=400,
        title="Which Property Type Is Most Expensive per Square Foot?",
    )


def chart_price_per_room(df: pd.DataFrame) -> alt.Chart:
    # ── Data prep ──────────────────────────────────────────────────────────
    chart_df = df[["propertyType", "price", "bedrooms"]].copy()
    # Drop nulls and exclude ≤1-bedroom properties: tiny bedroom counts
    # (studios, 1-beds) produce inflated per-room ratios that dominate the axis
    chart_df = chart_df[
        chart_df["price"].notna() & (chart_df["price"] > 0) &
        chart_df["bedrooms"].notna() & (chart_df["bedrooms"] > 1)
    ].copy()
    chart_df["pricePerRoom"] = chart_df["price"] / chart_df["bedrooms"]
    # Clip both tails (1st–99th percentile) for a clean distribution
    p01 = chart_df["pricePerRoom"].quantile(0.01)
    p99 = chart_df["pricePerRoom"].quantile(0.99)
    chart_df = chart_df[
        (chart_df["pricePerRoom"] >= p01) & (chart_df["pricePerRoom"] <= p99)
    ].copy()
    chart_df = chart_df[chart_df["propertyType"].isin(PROPERTY_TYPE_DOMAIN)].copy()
    y_max = 800_000
    # Clip strip data to y_max — strip points above this are outside the axis
    # domain but still cause Vega-Lite to allocate extra vertical space
    chart_df = chart_df[chart_df["pricePerRoom"] <= y_max].copy()

    # ── Pre-compute IQR-fenced 5-number summaries ─────────────────────────
    stats_rows = []
    for pt, grp in chart_df.groupby("propertyType")["pricePerRoom"]:
        q1 = grp.quantile(0.25)
        q3 = grp.quantile(0.75)
        iqr = q3 - q1
        stats_rows.append({
            "propertyType": pt,
            "lower_whisker": grp[grp >= q1 - 1.5 * iqr].min(),
            "q1": q1,
            "median_val": grp.median(),
            "q3": q3,
            "upper_whisker": grp[grp <= q3 + 1.5 * iqr].max(),
        })
    stats = pd.DataFrame(stats_rows)

    # Pre-format tooltip strings — dollar only, no /sqft
    _fmt = lambda v: f"${v:,.0f}"
    stats["tip_max"]    = stats["upper_whisker"].map(_fmt)
    stats["tip_q3"]     = stats["q3"].map(_fmt)
    stats["tip_median"] = stats["median_val"].map(_fmt)
    stats["tip_q1"]     = stats["q1"].map(_fmt)
    stats["tip_min"]    = stats["lower_whisker"].map(_fmt)

    # ── Shared encodings ───────────────────────────────────────────────────
    x_enc = alt.X("propertyType:N", title="Property Type", sort=PROPERTY_TYPE_DOMAIN)
    y_scale = alt.Scale(domain=[0, y_max])
    color_enc = alt.Color(
        "propertyType:N",
        scale=alt.Scale(domain=PROPERTY_TYPE_DOMAIN, range=PROPERTY_TYPE_RANGE),
        legend=None,
    )
    box_tooltip = [
        alt.Tooltip("propertyType:N", title="Property Type"),
        alt.Tooltip("tip_max:N",       title="Max"),
        alt.Tooltip("tip_q3:N",        title="75th Percentile"),
        alt.Tooltip("tip_median:N",    title="Median"),
        alt.Tooltip("tip_q1:N",        title="25th Percentile"),
        alt.Tooltip("tip_min:N",       title="Min"),
    ]

    base = alt.Chart(stats)

    # ── Layers (back → front) ──────────────────────────────────────────────
    strip = (
        alt.Chart(chart_df)
        .transform_calculate(jitter="(random() - 0.5)")
        .mark_circle(opacity=0.2, size=8)
        .encode(
            x=x_enc,
            xOffset=alt.XOffset("jitter:Q", scale=alt.Scale(domain=[-1, 1])),
            y=alt.Y("pricePerRoom:Q", scale=y_scale),
            color=color_enc,
            tooltip=[
                alt.Tooltip("propertyType:N", title="Property Type"),
                alt.Tooltip("pricePerRoom:Q", title="Price per Bedroom ($)", format="$,.0f"),
            ],
        )
    )

    lower_rule = (
        base.mark_rule(strokeWidth=1.5)
        .encode(
            x=x_enc,
            y=alt.Y("lower_whisker:Q", scale=y_scale),
            y2=alt.Y2("q1:Q"),
            color=color_enc,
            tooltip=box_tooltip,
        )
    )

    upper_rule = (
        base.mark_rule(strokeWidth=1.5)
        .encode(
            x=x_enc,
            y=alt.Y("q3:Q", scale=y_scale),
            y2=alt.Y2("upper_whisker:Q"),
            color=color_enc,
            tooltip=box_tooltip,
        )
    )

    iqr_box = (
        base.mark_bar(size=44)
        .encode(
            x=x_enc,
            y=alt.Y("q1:Q", title="Price per Bedroom ($)", scale=y_scale,
                    axis=alt.Axis(format="$~s", labelLimit=80)),
            y2=alt.Y2("q3:Q"),
            color=color_enc,
            tooltip=box_tooltip,
        )
    )

    median_tick = (
        base.mark_tick(thickness=3, size=44)
        .encode(
            x=x_enc,
            y=alt.Y("median_val:Q", scale=y_scale),
            color=alt.value("#ffffff"),
            tooltip=box_tooltip,
        )
    )

    return (strip + lower_rule + upper_rule + iqr_box + median_tick).properties(
        width=760,
        height=400,
        title="Which Property Type Is Most Expensive per Bedroom?",
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
    save_chart(chart_price_per_sqft(df), "price_per_sqft.html")
    save_chart(chart_price_per_room(df), "price_per_room.html")

    print(f"Saved Altair charts to {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

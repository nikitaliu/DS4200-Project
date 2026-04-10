# DS4200 Final Presentation Script

Published site: https://nikitaliu.github.io/DS4200-Project/

Target length: about 10 minutes total

## Speaker 1: Xinyue Du (about 3 minutes)

Hello everyone. Our project is called "Exploring Massachusetts Housing Costs." We built an interactive website that explains why housing prices vary so much across Massachusetts towns. Instead of writing for investors or technical analysts, we designed this project for the general public. We wanted the site to answer a simple question in plain English: why does one town feel financially out of reach while another feels more realistic?

We combined three kinds of information. First, we used a Massachusetts housing listing dataset from Kaggle based on Zillow-style listings. Second, we pulled town-level data from the U.S. Census Bureau's American Community Survey. Third, we incorporated environmental risk fields already included in the housing listings. Together, these sources let us compare prices, home features, livability, affordability, and risk.

One of our main goals was to make the analysis approachable. That is why the website opens with an introduction, lays out our research questions, explains our methodology in plain language, and includes a glossary for every technical term. If someone does not know what "price-to-income ratio" or "cap rate" means, they can click directly to the definition. We wanted the site to feel more like a visual explainer article than a finance dashboard.

I also worked on the D3 side of the project, especially the choropleth map and the town drill-down interaction. On the map, users can compare towns by median listing price, affordability pressure, cap-rate proxy, or environmental risk. When users click a town, a slide-in profile opens with housing, demographic, and employment context for that town. That interaction helped us move from a statewide picture to a local story without creating hundreds of separate pages.

## Speaker 2: Xiqiao Liu (about 3.5 minutes)

I focused on the data pipeline and the Altair charts. The raw housing file had nearly nine thousand rows, but it needed substantial cleaning before we could analyze it. Prices were stored as strings with dollar signs and commas, livability scores were stored like "81 out of 100," and risk values were stored as text labels with embedded scores. We parsed those into numeric variables, standardized property types, removed duplicate listing IDs, filtered out non-Massachusetts rows, and removed extreme outliers above ten million dollars or fifteen thousand square feet.

After cleaning, we engineered the metrics that power the rest of the analysis. These included price per square foot, home age, a livability composite, an environmental risk composite, estimated cap rate, gross rent multiplier, price-to-income ratio, and monthly affordability index. We also joined town-level ACS income and home-value data so we could compare local housing prices against local earning power.

For the visual analysis, one key chart is the scatter plot of price drivers. It lets users switch the x-axis between square footage, bedrooms, year built, and livability composite. We color the points by property type, and users can brush over points to create their own comparison set. We also added a density view because the dataset is large enough that overlapping points can hide patterns.

Another important pair of charts answers the livability question. We grouped listings into price quartiles and compared average walk, bike, and transit scores. We also plotted town income against median listing price with a four-times-income guideline line. Together, these charts show that accessibility often comes with a price premium, and many towns remain financially stretched even when local incomes are relatively high.

## Speaker 3: Lin Pan (about 3.5 minutes)

I focused on the narrative design, the findings, and the overall site experience. We organized the Findings section around four research questions so that every chart has a clear purpose. The first question is geographic: where are prices highest and lowest across Massachusetts? The choropleth shows a strong concentration of high-price towns near the coast, on the islands, and around the Boston metro area, while much of western Massachusetts remains more affordable.

The second question is about property features. Our scatter plot and D3 box plot show that larger homes and homes with more bathrooms tend to have higher asking prices, but housing type matters too. Single-family homes, condos, and multi-family properties do not occupy the same price bands, so users need to think about both size and market segment.

The third question is whether livability comes with a premium. We found that higher-priced listings generally have stronger walkability and transit scores. This means there is often a tradeoff between convenience and affordability. The fourth question is whether environmental risk is clearly reflected in prices. Our correlation heatmap suggests that the relationship is weak rather than strongly negative, which means some higher-risk places may still remain expensive because of location advantages.

Our main conclusion is that Massachusetts housing pressure is not driven by one factor alone. Price is shaped by location, home features, local income, and access to daily life amenities. At the same time, affordability varies dramatically from town to town, and environmental risk does not seem to be consistently discounted. If we had more time, we would add time-series data, better rent estimates, and neighborhood-level breakdowns for places like Boston. Thank you.

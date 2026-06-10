# Streamlit-economic-explorer
Interactive Streamlit dashboard for exploring World Bank GDP indicators with country filters, regional comparison, top-N rankings, growth metrics, and CSV export.
# Streamlit Economic Explorer

An interactive **Streamlit economic data dashboard** for exploring country-level GDP trends, GDP per capita, inflation-adjusted GDP, regional comparisons, top-N country rankings, and filtered CSV exports using World Bank data.

This project turns raw economic indicators into a simple browser-based analytics tool. Users can select countries, regions, metrics, and year ranges, then compare economic patterns through charts, KPI cards, ranking tables, and downloadable datasets.

## Overview

Economic data is powerful, but it is often hard to explore quickly. Public datasets usually require cleaning, reshaping, filtering, and charting before they become useful.

This app solves that problem by combining:

* World Bank API integration
* Pandas data preparation
* Streamlit interactive controls
* GDP trend charts
* GDP per capita comparison
* Inflation-adjusted GDP comparison
* Region-level aggregation
* Top-N rankings
* Filtered CSV download

The result is a lightweight economic data explorer that works directly in the browser.

## Problem

Country-level economic indicators are usually available through CSV files or public APIs, but they are not always analysis-ready.

A user often needs to:

* Find the right indicator
* Fetch data from an API
* Clean missing values
* Add country metadata
* Filter countries and regions
* Compare values across time
* Calculate growth
* Export the filtered dataset

The real problem is not “show GDP data.”

The real problem is:

> Make economic trends easy to explore, compare, and export without forcing the user to write analysis code.

## Solution

Streamlit Economic Explorer loads GDP indicators from the World Bank API or a local CSV fallback, enriches them with country metadata, and presents the results in an interactive dashboard.

Users can:

* Select a data source
* Choose a year range
* Filter by region
* Select countries by full country name
* Compare GDP, GDP per capita, or constant-dollar GDP
* View region-level trends
* Generate top-N country rankings
* Calculate percentage growth
* Download filtered data as CSV

## Key Features

| Feature                    | Description                                                             |
| -------------------------- | ----------------------------------------------------------------------- |
| World Bank API integration | Fetches current GDP, GDP per capita, and constant-dollar GDP indicators |
| Local CSV fallback         | Supports local GDP datasets stored in `data/gdp_data.csv`               |
| Full country names         | Displays readable country labels such as `Germany (DEU)`                |
| GDP per capita             | Compares country-level GDP per person                                   |
| Inflation-adjusted GDP     | Uses constant 2015 US$ GDP where available                              |
| Region comparison          | Aggregates selected metric by World Bank region                         |
| Top-N rankings             | Shows highest-ranked countries for the selected metric and year         |
| Percentage growth          | Calculates growth between selected start and end years                  |
| Filtered CSV export        | Lets users download the current filtered dataset                        |
| Deployment checklist       | Includes Streamlit Community Cloud deployment notes                     |

## Tech Stack

| Area              | Technology                         |
| ----------------- | ---------------------------------- |
| Language          | Python                             |
| Web App Framework | Streamlit                          |
| Data Processing   | Pandas                             |
| API Client        | Requests                           |
| Data Source       | World Bank API, local CSV fallback |
| Visualization     | Streamlit charts and metric cards  |
| Caching           | `st.cache_data`                    |
| File Handling     | `pathlib`                          |

## Indicators Used

The dashboard uses the following World Bank indicators:

| Indicator                  | World Bank Code  | Meaning                                            |
| -------------------------- | ---------------- | -------------------------------------------------- |
| GDP current US$            | `NY.GDP.MKTP.CD` | Nominal GDP in current US dollars                  |
| GDP per capita current US$ | `NY.GDP.PCAP.CD` | GDP per person in current US dollars               |
| GDP constant 2015 US$      | `NY.GDP.MKTP.KD` | Inflation-adjusted GDP in constant 2015 US dollars |

## App Workflow

```text
Select data source
        |
Fetch World Bank indicators or load local CSV
        |
Fetch country metadata
        |
Merge GDP data with country names and regions
        |
Select year range, regions, countries, and metric
        |
Render GDP trend charts
        |
Calculate country growth
        |
Generate top-N rankings
        |
Allow filtered CSV download
```

## Project Structure

```text
streamlit-economic-explorer/
│
├── streamlit_app.py
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── gdp_data.csv

```

The `data/gdp_data.csv` file is optional if using the World Bank API mode. It is required only for local CSV mode.

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/streamlit-economic-explorer.git
cd streamlit-economic-explorer
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment.

On macOS or Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Requirements

Create a `requirements.txt` file with:

```text
streamlit
pandas
requests
```

## Run the App

```bash
streamlit run streamlit_app.py
```

Then open the local Streamlit URL shown in the terminal.

Usually:

```text
http://localhost:8501
```

## Dashboard Controls

The sidebar provides the main dashboard controls.

| Control            | Purpose                                     |
| ------------------ | ------------------------------------------- |
| Data source        | Choose World Bank API or local CSV          |
| Year range         | Select the analysis period                  |
| Region filter      | Limit analysis to selected regions          |
| Country selector   | Select countries using full country names   |
| Primary metric     | Choose GDP, GDP per capita, or constant GDP |
| Top-N ranking size | Select ranking table size                   |

## Dashboard Sections

### 1. KPI Summary

The app displays:

* Number of selected countries
* Number of selected regions
* Selected year range
* Latest available year

### 2. GDP Over Time

A time-series chart compares the selected metric across selected countries.

Useful for questions such as:

* How has Germany’s GDP changed over time?
* How does Japan compare with Brazil?
* Which selected country shows stronger long-term growth?

### 3. Filtered Dataset

The app shows the filtered dataframe and provides a CSV download button.

This is useful when a user wants to export the selected data for further analysis.

### 4. Country Snapshot

The dashboard displays country-level metric cards for the final selected year.

Each card shows:

* Selected country
* Final-year value
* Percentage growth from start year to end year

### 5. GDP Per Capita Comparison

This section compares GDP per capita across selected countries.

It helps separate total economic size from average economic output per person.

### 6. Inflation-Adjusted GDP Comparison

This section uses constant 2015 US$ GDP where available.

This gives a cleaner long-term comparison because it reduces the distortion caused by price-level changes over time.

### 7. Region-Level Comparison

The app aggregates the selected metric by World Bank region.

This helps users compare broader economic patterns across regions instead of only individual countries.

### 8. Top-N Rankings

The dashboard ranks countries by the selected metric for the selected final year.

Examples:

* Top 10 countries by GDP
* Top 10 countries by GDP per capita
* Top 15 countries by constant-dollar GDP

### 9. Percentage Growth Table

The app calculates growth between the selected start and end years.

Formula:

```text
Percentage growth = ((end value / start value) - 1) × 100
```

## Data Transformation

The app supports two data paths.

### World Bank API Mode

In API mode, the app fetches indicator data directly from the World Bank API and joins it with country metadata.

The country metadata adds:

* Country code
* Country name
* Region
* Income level

This makes the dashboard easier to read and enables region-level aggregation.

### Local CSV Mode

In local CSV mode, the app expects a file at:

```text
data/gdp_data.csv
```

Expected structure:

```text
Country Code | 1960 | 1961 | 1962 | ... | 2022
```

The app reshapes the file into long format:

```text
Country Code | Year | GDP current US$
```

This is done with `pandas.melt()`.

```python
gdp_df = raw_gdp_df.melt(
    id_vars=id_columns,
    value_vars=year_columns,
    var_name="Year",
    value_name="GDP current US$",
)
```

## First-Principles Design

The project was designed around one core question:

> What is the simplest useful way to explore economic trends without writing code?

A spreadsheet is easy to start with, but weak for interactive filtering and repeatable analysis.

A full BI tool is powerful, but too heavy for a lightweight GitHub portfolio project.

A Streamlit app is the right middle ground. It is interactive, Python-native, easy to deploy, and close to the data workflow used by analysts and data scientists.

## OODA Summary

### Observe

Economic data is available, but raw CSV/API formats are not friendly for fast comparison.

### Orient

The task is exploratory analysis, not forecasting. Users need filters, charts, rankings, and exports.

### Decide

Use Streamlit for the interface, Pandas for transformation, and the World Bank API for live data access.

### Act

Build a dashboard that fetches indicators, enriches country metadata, filters by user selections, visualizes trends, calculates growth, and exports filtered data.

## Founder-Style Product Diagnosis

### User

Students, analysts, data scientists, policy learners, and portfolio reviewers who want to explore GDP trends quickly.

### Pain Point

Economic datasets are available but not immediately usable. Users need a fast way to compare countries, regions, and growth patterns.

### Smallest Useful Version

A dashboard that loads GDP data, allows country and year filtering, and plots GDP over time.

## Security and Data Notes

This app is low-risk because it uses public economic data and does not require user authentication, secrets, or private files.

| Area                    | Status                               |
| ----------------------- | ------------------------------------ |
| API keys                | Not required                         |
| Secrets                 | None used                            |
| User authentication     | Not required for demo                |
| File uploads            | Not enabled                          |
| User credentials        | None collected                       |
| Dynamic code execution  | None                                 |
| Data privacy risk       | Low if using public data             |
| External API dependency | World Bank API availability required |

Recommended safeguards:

* Do not commit private datasets
* Keep `.streamlit/secrets.toml` out of version control
* Add API error handling for production use
* Validate local CSV schema before loading
* Add clear source attribution
* Avoid storing user-specific data in the app

## Data Analysis Notes

This project demonstrates a practical exploratory data analysis workflow:

1. Fetch or load structured data
2. Clean and normalize fields
3. Add metadata
4. Filter by analytical dimensions
5. Visualize time-series patterns
6. Calculate growth
7. Export filtered results

The main analytical value comes from comparing three views:

| View                  | Insight                                 |
| --------------------- | --------------------------------------- |
| GDP current US$       | Total economic size in nominal terms    |
| GDP per capita        | Average economic output per person      |
| GDP constant 2015 US$ | Long-term growth adjusted for inflation |

These views help avoid a common mistake: comparing only headline GDP without considering population size or inflation.


## Streamlit Community Cloud Deployment

To deploy:

1. Push the repository to GitHub.
2. Confirm `streamlit_app.py` is in the repository root.
3. Add `requirements.txt`.
4. Go to Streamlit Community Cloud.
5. Select the GitHub repository.
6. Choose `streamlit_app.py` as the app file.
7. Deploy.

Recommended `requirements.txt`:

```text
streamlit
pandas
requests
```

## Suggested `.gitignore`

```text
__pycache__/
*.pyc
.env
.venv/
venv/
.streamlit/secrets.toml
```

## Example Questions This App Can Answer

* Which selected country had the highest GDP in the final selected year?
* How has GDP changed across selected countries since 1960?
* Which regions show the strongest GDP trend?
* How does GDP per capita compare across countries?
* How different is nominal GDP from inflation-adjusted GDP?
* Which countries rank highest by GDP or GDP per capita?
* What is the percentage growth between two selected years?

## Repository Topics

```text
streamlit
python
pandas
requests
world-bank-api
gdp
gdp-per-capita
economic-data
data-visualization
dashboard
open-data
time-series
```

import plotly.express as px
import pandas as pd


def plot_indicator_trend(df: pd.DataFrame):
    """Create a line chart for an economic indicator over time."""
    return px.line(
        df,
        x="year",
        y="value",
        color="country",
        markers=True,
        title="Economic Indicator Trend"
    )

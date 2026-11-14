"""Web interface: build the dataset and analyse each asset (parts 1 and 2)."""

import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# Make the project root importable so that `src` can be found,
# whatever folder the app is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis import build_summary, compute_drawdown, normalise_prices  # noqa: E402
from src.data import DataError, build_dataset, get_asset_names  # noqa: E402

DEFAULT_TICKERS = "GLD, ASML.AS, TTE.PA, AI.PA, MC.PA, IWDA.AS, BTC-USD, NVDA, EXS1.DE"
CURRENCIES = ["USD", "EUR", "GBP", "CHF", "JPY", "CAD"]


@st.cache_data(ttl=6 * 3600, show_spinner=False)
def load_data(tickers, base_currency, n_years):
    """Download and prepare the data once, then reuse it for 6 hours."""
    prices, info = build_dataset(list(tickers), base_currency, n_years)
    names = get_asset_names(prices.columns)
    return prices, info, names


def to_long(df, value_name):
    """Wide DataFrame (one column per asset) -> long format for Altair."""
    return df.reset_index(names="Date").melt("Date", var_name="Asset", value_name=value_name)


def line_chart(df, value_name, y_format):
    data = to_long(df, value_name)
    return (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y(f"{value_name}:Q", axis=alt.Axis(format=y_format)),
            color=alt.Color("Asset:N", legend=alt.Legend(orient="bottom", columns=3)),
            tooltip=["Date:T", "Asset:N", alt.Tooltip(f"{value_name}:Q", format=y_format)],
        )
        .properties(height=380)
        .interactive(bind_y=False)
    )


# ---------------------------------------------------------------- Page setup
st.set_page_config(page_title="Portfolio Diversification", page_icon="📊", layout="wide")
st.title("Portfolio Diversification Analysis")
st.caption(
    "Download prices from Yahoo Finance, convert them to one currency, "
    "and compare the return and risk of each asset. Educational project, not investment advice."
)

# ---------------------------------------------------------------- Parameters
with st.sidebar:
    st.header("Parameters")
    with st.form("parameters"):
        tickers_text = st.text_area(
            "Tickers (Yahoo Finance)",
            value=DEFAULT_TICKERS,
            help="Separate tickers with commas. Find them on finance.yahoo.com "
                 "(e.g. MC.PA for LVMH in Paris, EXS1.DE for a DAX ETF on Xetra).",
        )
        base_currency = st.selectbox("Base currency", CURRENCIES, index=0)
        n_years = st.slider("Period (years)", min_value=1, max_value=10, value=5)
        submitted = st.form_submit_button("Run analysis", type="primary", width="stretch")

if not submitted and "params" not in st.session_state:
    st.info("Choose your assets in the sidebar, then click **Run analysis**.")
    st.stop()

if submitted:
    tickers = tuple(dict.fromkeys(t.strip().upper() for t in tickers_text.split(",") if t.strip()))
    st.session_state["params"] = (tickers, base_currency, n_years)

tickers, base_currency, n_years = st.session_state["params"]

try:
    with st.spinner("Downloading data from Yahoo Finance..."):
        prices, info, name_by_ticker = load_data(tickers, base_currency, n_years)
except DataError as error:
    st.error(str(error))
    st.stop()
except Exception as error:  # network problems, Yahoo rate limiting...
    st.error(f"Unexpected error while downloading the data: {error}")
    st.stop()

display_prices = prices.rename(columns=name_by_ticker)

# ---------------------------------------------------------------- Part 1: dataset
st.header("1. Dataset")
rows_removed = info["rows_before"] - info["rows_after"]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Assets", prices.shape[1])
col2.metric("Common trading days", info["rows_after"])
col3.metric("Rows removed", rows_removed, help="Days when at least one asset or exchange rate had no price.")
col4.metric("Period", f"{prices.index.min():%d/%m/%Y} → {prices.index.max():%d/%m/%Y}")

with st.expander("Details: currencies and exchange rates"):
    currencies = pd.DataFrame({
        "Asset": [name_by_ticker.get(t, t) for t in info["currency_by_ticker"]],
        "Ticker": list(info["currency_by_ticker"]),
        "Quoted in": list(info["currency_by_ticker"].values()),
    })
    st.dataframe(currencies, hide_index=True, width="stretch")
    if info["fx_tickers"]:
        st.write(f"Prices converted to **{base_currency}** with: {', '.join(info['fx_tickers'])}")
    else:
        st.write(f"All assets are already quoted in **{base_currency}**: no conversion needed.")
    st.download_button(
        "Download the clean dataset (CSV)",
        prices.to_csv().encode("utf-8"),
        file_name="dataset_clean.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------------- Part 2: analysis
st.header("2. Asset analysis")

st.subheader("Price evolution (base 100)")
st.altair_chart(line_chart(normalise_prices(display_prices), "Base 100", ",.0f"), width="stretch")

st.subheader("Summary")
summary = build_summary(prices).rename(index=name_by_ticker)
st.dataframe(
    summary.style.format("{:.2f}").background_gradient(subset=["Return / risk ratio"], cmap="RdYlGn"),
    width="stretch",
)
st.caption(
    "Annualisation uses the number of common trading days actually observed per year. "
    "The return / risk ratio does not include a risk-free rate, so it is not a Sharpe ratio."
)

st.subheader("Return vs risk")
scatter_data = summary.reset_index(names="Asset")
points = alt.Chart(scatter_data).mark_circle(size=120).encode(
    x=alt.X("Annual volatility (%):Q", title="Annual volatility (%)"),
    y=alt.Y("Annual return (%):Q", title="Annual return (%)"),
    color=alt.Color("Asset:N", legend=None),
    tooltip=["Asset", alt.Tooltip("Annual return (%):Q", format=".2f"),
             alt.Tooltip("Annual volatility (%):Q", format=".2f"),
             alt.Tooltip("Return / risk ratio:Q", format=".2f")],
)
labels = points.mark_text(align="left", dx=8, dy=-6).encode(text="Asset:N")
zero_line = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="grey").encode(y="y:Q")
st.altair_chart((zero_line + points + labels).properties(height=420), width="stretch")
st.caption("Assets towards the top left delivered more return for less risk.")

st.subheader("Drawdown")
st.altair_chart(line_chart(compute_drawdown(display_prices), "Drawdown", ".0%"), width="stretch")
st.caption("How far each asset was below its previous peak. The lowest point is the maximum drawdown.")

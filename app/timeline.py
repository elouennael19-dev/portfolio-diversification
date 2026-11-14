"""Content of the "00 Project" page: the steps of the project, in order.

Each step: number, title, status ("done", "progress" or "planned"), where it lives,
a one-line summary, and the key decisions taken along the way.
Update the statuses here as the project moves forward.
"""

INTRO = (
    "A data project on a real personal portfolio: how much does diversification actually reduce risk? "
    "Each step is a notebook. The code is written step by step in the notebooks, then reused as functions "
    "for this interface."
)

STEPS = [
    {
        "num": "00", "title": "Framing", "status": "done", "where": "README",
        "summary": "Define the question, the assets and the rules before touching any data.",
        "points": [
            "Question: which assets really diversify the portfolio, and how much risk does it remove?",
            "Assets: the ones actually held (equities, ETFs, gold, crypto).",
            "One base currency (USD) and a rolling 5-year window.",
        ],
    },
    {
        "num": "01", "title": "Data collection", "status": "done", "where": "01_data_collection.ipynb",
        "summary": "Download adjusted prices, convert them into one currency and keep only comparable days.",
        "points": [
            "Adjusted closing prices from Yahoo Finance (dividends and splits included).",
            "Currency of each asset detected automatically; exchange-rate tickers generated, nothing hard-coded.",
            "Only days when every market is open are kept: filling the gaps would invent flat days.",
            "Conversion checked by hand (ASML × EUR/USD), and tested with a stock quoted in CNY.",
            "Lesson learnt: check the full name behind a ticker (a wrong “DAX” turned out to be a Canadian fund).",
        ],
    },
    {
        "num": "02", "title": "Asset analysis", "status": "done", "where": "02_asset_analysis.ipynb",
        "summary": "Describe each asset on its own: return, volatility, return per unit of risk, worst fall.",
        "points": [
            "Prices rebased to 100 to compare assets with very different price levels.",
            "Annualisation with the number of trading days actually observed, not the usual 252.",
            "Return / risk ratio without a risk-free rate, so not called a Sharpe ratio.",
            "Maximum drawdown to show the worst loss an investor could have lived through.",
            "Conclusion written to stay true whatever the period or the assets.",
        ],
    },
    {
        "num": "03", "title": "Correlations", "status": "progress", "where": "03_correlation_analysis.ipynb",
        "summary": "Study how the assets move together, to see what really diversifies.",
        "points": [
            "Correlations computed on returns, not prices (prices show trends, not common moves).",
            "Daily vs weekly: markets close at different hours, which lowers daily correlations (Epps effect).",
            "Rolling 60-day correlations: relationships change over time.",
            "Stress test on the 5% worst days, compared with the 5% best days to remove a selection bias.",
            "Findings so far: gold stays the main diversifier; correlations rise when markets fall.",
            "Left to do: written interpretation and conclusion.",
        ],
    },
    {
        "num": "04", "title": "Portfolio construction", "status": "planned", "where": "",
        "summary": "Compare an equal-weight portfolio and the real weights with the assets on their own.",
        "points": [],
    },
    {
        "num": "05", "title": "Markowitz optimisation", "status": "planned", "where": "",
        "summary": "Efficient frontier, minimum-variance and maximum-Sharpe portfolios.",
        "points": [],
    },
    {
        "num": "06", "title": "Risk analysis", "status": "planned", "where": "",
        "summary": "Value at Risk, Expected Shortfall and each asset's contribution to risk.",
        "points": [],
    },
    {
        "num": "07", "title": "Robustness", "status": "planned", "where": "",
        "summary": "Check optimised portfolios on data they have not seen (out-of-sample).",
        "points": [],
    },
    {
        "num": "08", "title": "Functions and interface", "status": "progress", "where": "src/ · app/",
        "summary": "Turn the notebook code into reusable functions and build this web interface.",
        "points": [
            "Steps 01 and 02 rewritten as functions in src/ (parameters in, values out, no prints).",
            "Streamlit interface: search assets by name, report with charts, shareable links.",
            "Left to do: add the correlation analysis, then deploy online.",
        ],
    },
]

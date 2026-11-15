"""Content of the "00 Project" page: the steps of the project, in order.

Each step: number, title, status ("done", "progress" or "planned"), where it lives,
a short summary, the key decisions, an optional code extract (shown on hover)
and optional notebook screenshots (files in app/static/notebooks/, shown as a clickable pile).
Update the statuses here as the project moves forward.
"""

import json
from pathlib import Path

INTRO = "Does diversification really cut risk? A data project on my own portfolio, one notebook per step."

# Who did what (shown under the intro)
CREDITS = [
    ("Analysis", "Elouen", "data, notebooks, algorithm"),
    ("Interface", "Claude Code", "design and web app, built on my functions"),
]

NOTEBOOKS = Path(__file__).resolve().parents[1] / "notebooks"


def notebook_code(filename, markers, max_lines=40):
    """The code cells of a notebook that contain one of the markers, exactly as written
    in the notebook (read live, so the card follows the notebooks)."""
    try:
        cells = json.loads((NOTEBOOKS / filename).read_text(encoding="utf-8"))["cells"]
    except (OSError, ValueError, KeyError):
        return ""
    blocks = []
    for cell in cells:
        source = "".join(cell.get("source", [])).strip()
        if cell.get("cell_type") == "code" and any(m in source for m in markers):
            lines = []
            for line in source.splitlines():
                if line.strip() or (lines and lines[-1].strip()):  # no double blank lines
                    lines.append(line.rstrip())
            blocks.append("\n".join(lines).strip())
    code = "\n\n".join(blocks).splitlines()
    if len(code) > max_lines:
        code = code[:max_lines] + ["# ... (see the notebook for the rest)"]
    return "\n".join(code)


CODE_01 = notebook_code("01_data_collection.ipynb",
                        ["currency_by_ticker[ticker] =", "fx_ticker_by_currency[currency] =", "yf.download(",
                         "column_to_convert[ticker] ="])
CODE_02 = notebook_code("02_asset_analysis.ipynb", ["def compute_daily_returns", "def compute_drawdown"])
CODE_03 = notebook_code("03_correlation_analysis.ipynb",
                        ["daily_returns.corr()", 'resample("W")', "rolling(60)", "quantile(0.05)"])

IMAGES_01 = [
    ("01-fx-tickers.jpg", "Exchange-rate tickers generated"),
    ("01-download.jpg", "Missing values, then rows kept"),
    ("01-converted.jpg", "Prices converted to USD"),
]

IMAGES_02 = [
    ("02-price-gld.jpg", "Price of each asset (here GLD)"),
    ("02-base-100.jpg", "Every asset rebased to 100"),
    ("02-returns-output.jpg", "Total and annual returns"),
    ("02-drawdown.jpg", "Drawdown over time"),
    ("02-return-vs-risk.jpg", "Annualised return vs risk"),
    ("02-summary-table.jpg", "Summary table"),
]

IMAGES_03 = [
    ("03-daily-matrix.jpg", "Daily correlation matrix"),
    ("03-weekly-matrix.jpg", "Weekly correlation matrix"),
    ("03-rolling.jpg", "Rolling correlation with MSCI World"),
    ("03-worst-days.jpg", "Correlation on the 5% worst days"),
    ("03-best-days.jpg", "Correlation on the 5% best days"),
]

STEPS = [
    {
        "num": "00", "title": "Framing", "status": "done", "where": "README",
        "summary": "Question, assets and rules first.",
        "points": [
            "Which assets really diversify?",
            "Real holdings: stocks, ETFs, gold, crypto",
            "One currency (USD), rolling 5 years",
        ],
    },
    {
        "num": "01", "title": "Data collection", "status": "done", "where": "01_data_collection.ipynb", "code": CODE_01, "images": IMAGES_01,
        "summary": "Clean prices, one currency, comparable days.",
        "points": [
            "Adjusted prices · Yahoo Finance",
            "Currencies & FX tickers detected automatically",
            "Only days when every market is open",
            "Conversion checked by hand (EUR, CNY)",
            "Lesson: check the name behind a ticker",
        ],
    },
    {
        "num": "02", "title": "Asset analysis", "status": "done", "where": "02_asset_analysis.ipynb", "code": CODE_02, "images": IMAGES_02,
        "summary": "Each asset on its own.",
        "points": [
            "Base 100 to compare prices",
            "Annualised on observed trading days",
            "Return / risk ratio (not a Sharpe)",
            "Maximum drawdown",
        ],
    },
    {
        "num": "03", "title": "Correlations", "status": "done", "where": "03_correlation_analysis.ipynb", "code": CODE_03, "images": IMAGES_03,
        "summary": "How the assets move together.",
        "points": [
            "Returns, not prices",
            "Daily vs weekly: time-zone effect",
            "Rolling 60-day correlations",
            "Stress: 5% worst vs 5% best days",
            "Gold diversifies, even in falls",
            "Correlations rise when the market falls",
            "DAX and MSCI World are redundant",
        ],
    },
    {
        "num": "04", "title": "Portfolio construction", "status": "planned", "where": "",
        "summary": "Equal weights vs real weights.",
        "points": [],
    },
    {
        "num": "05", "title": "Markowitz optimisation", "status": "planned", "where": "",
        "summary": "Efficient frontier, min variance, max Sharpe.",
        "points": [],
    },
    {
        "num": "06", "title": "Risk analysis", "status": "planned", "where": "",
        "summary": "VaR, Expected Shortfall, risk contributions.",
        "points": [],
    },
    {
        "num": "07", "title": "Robustness", "status": "planned", "where": "",
        "summary": "Out-of-sample test.",
        "points": [],
    },
    {
        "num": "08", "title": "Functions and interface", "status": "progress", "where": "src/ · app/",
        "summary": "Notebook code → functions → this web app.",
        "points": [
            "Steps 01–02 as functions in src/",
            "Web app: search, report, shareable links",
            "To do: add correlations",
        ],
    },
]

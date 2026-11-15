"""Part 1 – Data collection and preparation (logic of notebook 01)."""

from datetime import date, timedelta

import pandas as pd
import yfinance as yf

# Yahoo quotes some markets in a sub-unit of the currency (e.g. London in pence).
# Each entry maps the sub-unit to (main currency, divisor).
SUBUNIT_CURRENCIES = {
    "GBp": ("GBP", 100),
    "GBX": ("GBP", 100),
    "ZAc": ("ZAR", 100),
    "ILA": ("ILS", 100),
}


MIN_COMMON_DAYS = 20  # about one month: below this, returns and correlations mean little


class DataError(ValueError):
    """Raised when the data cannot be built from the given parameters."""


def compute_period(n_years, end=None):
    """Return (start, end) dates for a rolling period of n_years."""
    end = end or date.today()
    start = end - timedelta(days=round(n_years * 365))
    return start, end


def get_currencies(tickers):
    """Return {ticker: currency} using Yahoo Finance."""
    currency_by_ticker = {}
    invalid = []
    for ticker in tickers:
        try:
            currency_by_ticker[ticker] = yf.Ticker(ticker).fast_info["currency"]
        except Exception:
            invalid.append(ticker)
    if invalid:
        raise DataError(
            f"Could not find the currency of: {', '.join(invalid)}. "
            "Check the tickers on finance.yahoo.com (Yahoo may also be rate limiting requests)."
        )
    return currency_by_ticker


SEARCHABLE_TYPES = {"EQUITY", "ETF", "CRYPTOCURRENCY", "MUTUALFUND", "INDEX"}


def search_assets(query, max_results=10):
    """Search Yahoo Finance by name or ticker.

    Returns a list of dicts: symbol, name, exchange, type.
    """
    query = query.strip()
    if len(query) < 2:
        return []
    quotes = yf.Search(query, max_results=max_results, news_count=0).quotes
    results = []
    for quote in quotes:
        if quote.get("quoteType") not in SEARCHABLE_TYPES or not quote.get("symbol"):
            continue
        results.append({
            "symbol": quote["symbol"],
            "name": (quote.get("longname") or quote.get("shortname") or quote["symbol"]).strip(),
            "exchange": quote.get("exchDisp") or quote.get("exchange") or "",
            "type": quote.get("typeDisp") or quote.get("quoteType", "").title(),
        })
    return results


def get_asset_names(tickers):
    """Return {ticker: short name}, falling back to the ticker itself."""
    name_by_ticker = {}
    for ticker in tickers:
        try:
            name_by_ticker[ticker] = yf.Ticker(ticker).info.get("shortName") or ticker
        except Exception:
            name_by_ticker[ticker] = ticker
    return name_by_ticker


def build_fx_tickers(currency_by_ticker, base_currency):
    """Return {currency: exchange rate ticker}, e.g. {"EUR": "EURUSD=X"}.

    Sub-unit currencies (e.g. GBp) are mapped to their main currency.
    """
    currencies = set()
    for currency in currency_by_ticker.values():
        main_currency = SUBUNIT_CURRENCIES.get(currency, (currency, 1))[0]
        currencies.add(main_currency)
    currencies.discard(base_currency)
    return {currency: f"{currency}{base_currency}=X" for currency in sorted(currencies)}


def download_prices(tickers, start, end):
    """Download adjusted closing prices for the given tickers."""
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if raw is None or raw.empty:
        raise DataError("Yahoo Finance returned no data for this request.")
    close = raw["Close"]
    if isinstance(close, pd.Series):  # a single ticker returns a Series
        close = close.to_frame(name=tickers[0])
    return close


def clean_prices(raw_close):
    """Keep only the days when every column has a price.

    Returns the clean DataFrame and the number of rows before / after.
    """
    empty_columns = [col for col in raw_close.columns if raw_close[col].isna().all()]
    if empty_columns:
        raise DataError(
            f"No price data for: {', '.join(empty_columns)}. "
            "The ticker or the exchange rate may not exist on Yahoo Finance."
        )
    clean = raw_close.dropna()
    if len(clean) < MIN_COMMON_DAYS:
        raise DataError(
            f"Only {len(clean)} common trading day{'s' if len(clean) != 1 else ''} left after removing missing "
            f"values (at least {MIN_COMMON_DAYS} are needed). One asset may be too recent or rarely traded: "
            "try a longer period or different assets."
        )
    return clean, len(raw_close), len(clean)


def convert_to_base_currency(prices, currency_by_ticker, fx_ticker_by_currency):
    """Multiply each asset by its exchange rate, then drop the rate columns."""
    converted = prices.copy()
    for ticker, currency in currency_by_ticker.items():
        main_currency, divisor = SUBUNIT_CURRENCIES.get(currency, (currency, 1))
        converted[ticker] = converted[ticker] / divisor
        if main_currency in fx_ticker_by_currency:
            converted[ticker] = converted[ticker] * converted[fx_ticker_by_currency[main_currency]]
    return converted.drop(columns=list(fx_ticker_by_currency.values()))


def build_dataset(tickers, base_currency="USD", n_years=5, end=None):
    """Run the whole notebook 01 pipeline.

    Returns:
        prices: DataFrame of prices in the base currency, indexed by date
        info: dict with the currencies, FX tickers, period and row counts
    """
    tickers = list(dict.fromkeys(t.strip().upper() for t in tickers if t.strip()))
    if not tickers:
        raise DataError("Enter at least one ticker.")

    start, end = compute_period(n_years, end)
    currency_by_ticker = get_currencies(tickers)
    fx_ticker_by_currency = build_fx_tickers(currency_by_ticker, base_currency)
    fx_tickers = list(fx_ticker_by_currency.values())

    raw_close = download_prices(tickers + fx_tickers, start, end)
    missing = [t for t in tickers + fx_tickers if t not in raw_close.columns]
    if missing:
        raise DataError(f"No data returned for: {', '.join(missing)}.")

    clean, rows_before, rows_after = clean_prices(raw_close[tickers + fx_tickers])
    prices = convert_to_base_currency(clean, currency_by_ticker, fx_ticker_by_currency)

    info = {
        "currency_by_ticker": currency_by_ticker,
        "fx_tickers": fx_tickers,
        "start": start,
        "end": end,
        "rows_before": rows_before,
        "rows_after": rows_after,
    }
    return prices, info

"""Part 2 – Descriptive statistics by asset (logic of notebook 02)."""

import pandas as pd


def compute_n_years(prices):
    """Actual length of the period covered by the data, in years."""
    return (prices.index.max() - prices.index.min()).days / 365.25


def normalise_prices(prices):
    """Start every price series at 100."""
    return prices / prices.iloc[0] * 100


def compute_returns(prices):
    """Return between two consecutive rows (daily, weekly... depending on the data)."""
    previous_prices = prices.shift(1)
    returns = (prices - previous_prices) / previous_prices
    return returns.dropna()


def compute_total_returns(returns):
    """Compounded return over the whole period."""
    return (1 + returns).prod() - 1


def compute_annual_returns(total_returns, n_years):
    """Constant yearly growth rate giving the total return over n_years."""
    return (1 + total_returns) ** (1 / n_years) - 1


def compute_annual_volatility(returns, rows_per_year):
    """Standard deviation of returns, annualised with the measured rows per year."""
    return returns.std() * rows_per_year ** 0.5


def compute_return_risk_ratio(annual_returns, annual_volatility):
    """Annual return / annual volatility (no risk-free rate, so not a Sharpe ratio)."""
    return annual_returns / annual_volatility


def compute_drawdown(prices):
    """How far each price is below its previous peak."""
    return prices / prices.cummax() - 1


def build_summary(prices):
    """Run the whole notebook 02 pipeline and return the summary table.

    Columns are expressed in % (except the ratio), sorted by return / risk ratio.
    """
    n_years = compute_n_years(prices)
    rows_per_year = len(prices) / n_years

    returns = compute_returns(prices)
    total_returns = compute_total_returns(returns)
    annual_returns = compute_annual_returns(total_returns, n_years)
    annual_volatility = compute_annual_volatility(returns, rows_per_year)
    ratio = compute_return_risk_ratio(annual_returns, annual_volatility)
    max_drawdown = compute_drawdown(prices).min()

    summary = pd.DataFrame({
        "Total return (%)": total_returns * 100,
        "Annual return (%)": annual_returns * 100,
        "Annual volatility (%)": annual_volatility * 100,
        "Return / risk ratio": ratio,
        "Max drawdown (%)": max_drawdown * 100,
    })
    return summary.sort_values("Return / risk ratio", ascending=False)

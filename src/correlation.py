"""Part 3 – Correlations between assets (logic of notebook 03)."""

import numpy as np
import pandas as pd

from src.analysis import compute_returns

REFERENCE_TICKER = "IWDA.AS"  # MSCI World: the "global market" used in notebook 03
ROLLING_WINDOW = 60           # trading days, about 3 months
EXTREME_SHARE = 0.05          # 5% worst / best days of the reference


def compute_weekly_returns(prices):
    """Returns from the last price of each week (reduces the trading-hours effect)."""
    return compute_returns(prices.resample("W").last())


def compute_correlation(returns):
    """Correlation matrix of the returns (+1 together, 0 independent, -1 opposite)."""
    return returns.corr()


def compute_rolling_correlation(returns, reference, window=ROLLING_WINDOW):
    """Correlation of every asset with the reference, on a moving window of `window` rows."""
    others = returns.drop(columns=reference)
    return others.rolling(window).corr(returns[reference]).dropna(how="all")


def compute_extreme_days(returns, reference, share=EXTREME_SHARE):
    """Worst and best days of the reference, with the correlation matrix of each.

    Comparing worst days with best days removes the selection bias (both samples
    are extreme days, where the reference moves little from one day to the next).
    """
    worst_threshold = returns[reference].quantile(share)
    best_threshold = returns[reference].quantile(1 - share)
    worst_returns = returns[returns[reference] <= worst_threshold]
    best_returns = returns[returns[reference] >= best_threshold]
    worst_corr = worst_returns.corr()
    best_corr = best_returns.corr()
    return {
        "worst_threshold": worst_threshold,
        "best_threshold": best_threshold,
        "n_worst": len(worst_returns),
        "n_best": len(best_returns),
        "worst_corr": worst_corr,
        "best_corr": best_corr,
        "worst_minus_best": worst_corr - best_corr,
    }


def correlation_pairs(matrix):
    """Every pair once (no diagonal), as a Series indexed by (asset A, asset B)."""
    keep = np.tril(np.ones(matrix.shape, dtype=bool), k=-1)
    return matrix.where(keep).stack().dropna()


def compute_average_correlation(corr_matrix):
    """Average correlation of each asset with all the others, lowest first (best diversifier first).

    The diagonal (an asset with itself = 1) is removed with `== 1`, as in notebook 03:
    two identical assets would also be removed.
    """
    corr_without_diag = corr_matrix.mask(corr_matrix == 1)
    return corr_without_diag.mean().sort_values()


def compute_portfolio_average_correlation(corr_matrix):
    """Average of all the pairs: one score for the whole portfolio (every asset with the same weight)."""
    return compute_average_correlation(corr_matrix).mean()

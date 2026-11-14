# Portfolio Diversification Analysis

Analysis of the effect of diversification on a portfolio of nine assets,
from data collection to risk analysis.

> Work in progress: the data preparation, individual asset analysis and correlation analysis are done.

## Objective
This project analyses how diversification affects the risk and return of an investment portfolio.

It has three goals:
- Build a complete data analysis project, from data collection to final conclusions
- Practise working with real financial data
- Get a data-driven view of a personal investment portfolio

## Assets
These nine assets are the ones held in the personal portfolio studied in this project.

| Ticker | Asset | Category |
|---|---|---|
| GLD | SPDR Gold Shares | Gold |
| BTC-USD | Bitcoin | Cryptocurrency |
| ASML.AS | ASML | European equity |
| TTE.PA | TotalEnergies | European equity |
| AI.PA | Air Liquide | European equity |
| MC.PA | LVMH | European equity |
| IWDA.AS | iShares Core MSCI World | Global equity ETF |
| EXS1.DE | iShares Core DAX | German equity ETF |
| NVDA | NVIDIA | US equity |

## Method
- Data from Yahoo Finance, via `yfinance`
- Rolling 5-year period
- Adjusted closing prices, converted to USD
- Only the days when all assets have a price are kept
- Conversion checked by hand on several portfolios, and tested with a stock quoted in CNY

## Project structure
```text
notebooks/
├── 01_data_collection.ipynb       Download, clean and convert the data
├── 02_asset_analysis.ipynb        Returns, volatility and drawdown by asset
└── 03_correlation_analysis.ipynb  Correlations: daily, weekly, rolling and during market stress
requirements.txt                   Python dependencies
```

## Getting started
```bash
git clone https://github.com/elouennael19-dev/portfolio-diversification.git
cd portfolio-diversification
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run the notebooks in order. Notebook 01 downloads the data and creates
`Data/Processed/dataset_clean.csv`, which the following notebooks use.

## Roadmap
- [x] Data collection and preparation
- [x] Individual asset analysis
- [x] Correlations between assets
- [ ] Portfolio construction
- [ ] Markowitz optimisation
- [ ] Risk analysis (VaR, CVaR)
- [ ] Robustness testing
- [ ] Conclusion and user interface

## Disclaimer
This project is for educational purposes only and is not investment advice.

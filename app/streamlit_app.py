"""Web interface for parts 1 and 2 of the project.

Two screens:
  1. Portfolio - search assets (or pick popular ones), review the list, choose currency and period.
  2. Report    - portfolio panel on the left, analysis in tabs on the right.
The parameters live in the URL, so a link reopens the same report.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR.parent))  # project root, for `src`
sys.path.insert(0, str(APP_DIR))         # app folder, for `charts` and `style`

import charts  # noqa: E402
import style  # noqa: E402
import timeline  # noqa: E402
import author  # noqa: E402
from src.analysis import build_summary, compute_drawdown, normalise_prices  # noqa: E402
from src.data import DataError, build_dataset, get_asset_names, search_assets  # noqa: E402

EXAMPLE_PORTFOLIO = {
    "GLD": "SPDR Gold Shares", "ASML.AS": "ASML", "TTE.PA": "TotalEnergies", "AI.PA": "Air Liquide",
    "MC.PA": "LVMH", "IWDA.AS": "iShares Core MSCI World", "BTC-USD": "Bitcoin", "NVDA": "NVIDIA",
    "EXS1.DE": "iShares Core DAX",
}
POPULAR = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "SPY": "S&P 500",
    "IWDA.AS": "MSCI World", "GLD": "Gold", "BTC-USD": "Bitcoin", "MC.PA": "LVMH",
    "AIR.PA": "Airbus", "TTE.PA": "TotalEnergies", "ASML.AS": "ASML", "ETH-USD": "Ethereum",
}
CURRENCIES = ["USD", "EUR", "GBP", "CHF", "JPY"]
PERIODS = [1, 3, 5, 10]
MAX_HIGHLIGHT = 3
SECTIONS = ["Overview", "Performance", "Risk", "Data"]
SECTION_ICONS = {"Overview": ":material/dashboard:", "Performance": ":material/trending_up:",
                 "Risk": ":material/waterfall_chart:", "Data": ":material/table_rows:"}
MIN_ASSETS = 2


# ================================================================= helpers
@st.cache_data(ttl=6 * 3600, show_spinner=False)
def load_data(tickers, base_currency, n_years):
    prices, info = build_dataset(list(tickers), base_currency, n_years)
    names = get_asset_names(prices.columns)
    return prices, info, names


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def search(query):
    return search_assets(query, max_results=8)


def html(markup, target=st):
    target.markdown(markup, unsafe_allow_html=True)


def show(chart, height=None):
    st.altair_chart(charts.styled(chart, height), theme=None, width="stretch")


def title(text, sub=None, label=None):
    html((f'<div class="label">{style.esc(label)}</div>' if label else "")
         + f'<div class="h">{style.esc(text)}</div>' + (f'<div class="sub">{style.esc(sub)}</div>' if sub else ""))


def stable_colors(selected, key="color_by_asset"):
    """A highlighted asset keeps its colour while selected; a new one takes the first free colour."""
    previous = st.session_state.get(key, {})
    kept = {a: c for a, c in previous.items() if a in selected}
    free = [c for c in style.SERIES if c not in kept.values()]
    for asset in selected:
        if asset not in kept:
            kept[asset] = free.pop(0)
    st.session_state[key] = kept
    return kept


def init_state():
    if "portfolio" in st.session_state:
        return
    st.session_state.update(portfolio={}, currency="USD", years=5, step="build")
    params = st.query_params
    if "tickers" in params:  # a shared link opens the report directly
        tickers = [t.strip().upper() for t in params["tickers"].split(",") if t.strip()]
        st.session_state["portfolio"] = {t: EXAMPLE_PORTFOLIO.get(t) or POPULAR.get(t, "") for t in tickers}
        if params.get("currency", "").upper() in CURRENCIES:
            st.session_state["currency"] = params["currency"].upper()
        try:
            st.session_state["years"] = min(10, max(1, int(params.get("years", 5))))
        except ValueError:
            pass
        if len(tickers) >= MIN_ASSETS:
            st.session_state["step"] = "report"


# ================================================================= callbacks
def add_asset(symbol, name):
    st.session_state["portfolio"][symbol] = name
    st.session_state["query"] = ""


def remove_asset(symbol):
    st.session_state["portfolio"].pop(symbol, None)


def use_example():
    st.session_state["portfolio"] = dict(EXAMPLE_PORTFOLIO)


def go_report():
    st.session_state["currency"] = st.session_state.get("currency_choice") or st.session_state["currency"]
    st.session_state["years"] = st.session_state.get("years_choice") or st.session_state["years"]
    st.session_state["step"] = "report"
    st.query_params.update(tickers=",".join(st.session_state["portfolio"]),
                           currency=st.session_state["currency"], years=str(st.session_state["years"]))


def go_build():
    st.session_state["step"] = "build"
    st.query_params.clear()


def go_project():
    st.session_state["step"] = "project"
    st.query_params.clear()


NAV = ["00 Project", "01 Portfolio", "02 Report"]
STEP_INDEX = {"project": 0, "build": 1, "report": 2}


def navigate():
    """Called when a tab of the top navigation is clicked."""
    choice = st.session_state.get("nav")
    if choice == NAV[0]:
        go_project()
    elif choice == NAV[1]:
        go_build()
    elif choice == NAV[2]:
        if len(st.session_state["portfolio"]) >= MIN_ASSETS:
            go_report()
        else:
            st.session_state["nav"] = NAV[STEP_INDEX[st.session_state["step"]]]
            st.toast(f"Add at least {MIN_ASSETS} assets to see the report.")


def app_bar(step, meta=""):
    """Top bar: mark on the left, clickable navigation in the middle, context on the right.
    step: 0 = project, 1 = portfolio, 2 = report."""
    st.session_state["nav"] = NAV[step]
    left, middle, right = st.columns([1, 1.5, 1], vertical_alignment="center")
    html(style.mark(), left)
    middle.segmented_control("Navigation", NAV, key="nav", on_change=navigate, label_visibility="collapsed")
    html(f'<div class="appmeta">{style.esc(meta)}</div>', right)


# ================================================================= screen 0: project timeline
def project_page():
    done = sum(s["status"] == "done" for s in timeline.STEPS)
    app_bar(0, f"{done} of {len(timeline.STEPS)} steps done")
    with st.container(key="page_project"):
        main, side = st.columns([2.3, 1], gap="large")
        html(style.timeline(timeline.INTRO, timeline.STEPS), main)
        with side, st.container(key="profile"):
            html(style.profile_card(author.NAME, author.HANDLE, author.PRONOUNS, author.PHOTO,
                                    author.BIO, author.STATUS, author.LINKS))


# ================================================================= screen 1: portfolio
def build_page():
    portfolio = st.session_state["portfolio"]
    app_bar(1, f"{len(portfolio)} asset{'s' if len(portfolio) != 1 else ''} selected")
    with st.container(key="page_build"):
        left, right = st.columns([3, 2], gap="large")

        with left:
            title("Add assets", "Search by company, fund or ticker.", label="Search")
            query = st.text_input("Search", key="query", placeholder="Try “Airbus”, “MSCI World” or “BTC”",
                                  label_visibility="collapsed", icon=":material/search:")
            if query.strip():
                try:
                    results = search(query)
                except Exception:
                    results = None
                if results is None:
                    st.caption("Search is unavailable right now. Try again in a moment.")
                elif not results:
                    st.caption(f"Nothing found for “{query.strip()}”. Try another name or the exact ticker.")
                else:
                    grid = st.columns(2)
                    for i, r in enumerate(results):
                        with grid[i % 2].container(border=True):
                            html(style.asset_row(r["name"], r["symbol"], f"{r['symbol']} · {r['exchange']} · {r['type']}"))
                            added = r["symbol"] in portfolio
                            st.button("Added" if added else "Add", key=f"add_{r['symbol']}", disabled=added,
                                      icon=":material/check:" if added else ":material/add:", width="stretch",
                                      on_click=add_asset, args=(r["symbol"], r["name"]))
                    st.caption("A company can be listed on several markets: pick the one where you bought it.")
            else:
                html('<div class="cap">Popular</div>')
                grid = st.columns(4)
                for i, (symbol, name) in enumerate(POPULAR.items()):
                    added = symbol in portfolio
                    grid[i % 4].button(name, key=f"pop_{symbol}", disabled=added, width="stretch",
                                       icon=":material/check:" if added else ":material/add:",
                                       on_click=add_asset, args=(symbol, name), help=symbol)

        with right, st.container(border=True):
            title("Your portfolio", f"{len(portfolio)} asset{'s' if len(portfolio) != 1 else ''}", label="Selection")
            if not portfolio:
                html('<div class="empty"><b>Nothing here yet</b>Add assets on the left, or load an example.</div>')
                st.write("")
                st.button("Load example portfolio", icon=":material/auto_awesome:", on_click=use_example,
                          width="stretch")
            for symbol, name in list(portfolio.items()):
                a, b = st.columns([6, 1], vertical_alignment="center")
                html(style.asset_row(name, symbol), a)
                b.button("", key=f"rm_{symbol}", type="tertiary", icon=":material/close:",
                         on_click=remove_asset, args=(symbol,), help=f"Remove {name or symbol}")

            html('<div class="cap">Compare in</div>')
            st.segmented_control("Currency", CURRENCIES, key="currency_choice", default=st.session_state["currency"],
                                 label_visibility="collapsed")
            html('<div class="cap">Over the last</div>')
            st.segmented_control("Period", PERIODS, key="years_choice", default=st.session_state["years"],
                                 format_func=lambda y: f"{y} yr" + ("s" if y > 1 else ""), label_visibility="collapsed")
            st.write("")
            ready = len(portfolio) >= MIN_ASSETS
            st.button("Analyse portfolio", type="primary", icon=":material/arrow_forward:", disabled=not ready,
                      on_click=go_report, width="stretch")
            if not ready:
                st.caption(f"Add at least {MIN_ASSETS} assets to compare them.")


# ================================================================= screen 2: report
def report_page():
    tickers = tuple(st.session_state["portfolio"])
    currency, years = st.session_state["currency"], st.session_state["years"]

    try:
        with st.spinner("Fetching prices…"):
            prices, info, names = load_data(tickers, currency, years)
    except Exception as error:  # DataError, network problems, Yahoo rate limiting...
        app_bar(2)
        st.error(str(error) if isinstance(error, DataError) else f"Something went wrong while downloading the data: {error}")
        st.button("Back to my portfolio", icon=":material/arrow_back:", on_click=go_build)
        return

    for t, n in names.items():  # keep readable names for screen 1
        if not st.session_state["portfolio"].get(t):
            st.session_state["portfolio"][t] = n

    display = prices.rename(columns=names)
    summary = build_summary(prices).rename(index=names)
    summary.index.name = "Asset"
    assets = list(display.columns)
    period = f"{prices.index.min():%b %Y} – {prices.index.max():%b %Y}"
    app_bar(2, f"{currency} · {period}")
    with st.container(key="page_report"):
        # Full-width navigation bar, right under the top bar (sticks to the top while scrolling)
        with st.container(key="reportnav"):
            nav_left, nav_right = st.columns([2, 1], vertical_alignment="center")
            section = nav_left.segmented_control(
                "Section", SECTIONS, key="section", default=SECTIONS[0], label_visibility="collapsed",
                format_func=lambda s: f"{SECTION_ICONS[s]} {s}") or SECTIONS[0]
            html(f'<div class="navctx">{len(assets)} assets · {years}Y · {info["rows_after"]:,} trading days</div>',
                 nav_right)

        side, main = st.columns([1.3, 2.7], gap="large")

        # --- Portfolio panel
        with side, st.container(border=True):
            title("Portfolio", f"Ranked by annual return, in {currency}", label="Holdings")
            normalised = normalise_prices(prices)
            by_return = summary.sort_values("Annual return (%)", ascending=False)
            for ticker in by_return.rename(index={v: k for k, v in names.items()}).index:
                name = names.get(ticker, ticker)
                right = style.sparkline(normalised[ticker]) + style.change_chip(summary.loc[name, "Annual return (%)"])
                html(style.asset_row(name, ticker, right=right))
                st.write("")
            st.button("Edit portfolio", icon=":material/edit:", on_click=go_build, width="stretch")

        with main:
            best_ret = summary["Annual return (%)"].idxmax()
            best_ratio = summary["Return / risk ratio"].idxmax()
            most_vol = summary["Annual volatility (%)"].idxmax()
            worst_dd = summary["Max drawdown (%)"].idxmin()

            with st.container(key=f"sec_{section.lower()}"):  # new key per section -> fade-in
                if section == "Overview":
                    html(style.cards([
                        ("up", "Best return", f"{summary.loc[best_ret, 'Annual return (%)']:+.1f}%", best_ret, "per year"),
                        ("target", "Best for risk", f"{summary.loc[best_ratio, 'Return / risk ratio']:.2f}",
                         best_ratio, "return ÷ volatility"),
                        ("pulse", "Most volatile", f"{summary.loc[most_vol, 'Annual volatility (%)']:.0f}%", most_vol,
                         "typical move per year"),
                        ("down", "Deepest fall", f"{summary.loc[worst_dd, 'Max drawdown (%)']:.0f}%", worst_dd,
                         "from a previous peak"),
                    ]))
                    title("Return vs risk", "Top left is best: more return for less volatility. "
                          "Bigger bubbles fell further from their peak.", label="Chart")
                    show(charts.return_risk_bubbles(summary), height=440)
                    st.write("")
                    title("Return per unit of risk", "Annual return divided by annual volatility (not a Sharpe ratio: "
                                                      "no risk-free rate).")
                    show(charts.lollipops(summary, "Return / risk ratio", ".2f", signed=True))

                if section == "Performance":
                    title("Growth of 100", "Every asset starts at 100 at the beginning of the period. "
                          "Pick up to three to compare; the rest stay grey.", label="Chart")
                    default = list(dict.fromkeys([best_ratio, summary.index[-1]]))
                    highlighted = st.pills("Highlight", assets, selection_mode="multi", default=default, key="highlight",
                                           label_visibility="collapsed")
                    if len(highlighted) > MAX_HIGHLIGHT:
                        st.caption(f"Only the first {MAX_HIGHLIGHT} are coloured.")
                        highlighted = highlighted[:MAX_HIGHLIGHT]
                    windows = [w for w in (1, 3, 5) if w < years] + ["All"]
                    c1, c2 = st.columns([3, 1], vertical_alignment="center")
                    window = c1.segmented_control("Window", windows, default="All", key="window",
                                                  format_func=lambda w: w if w == "All" else f"{w}Y",
                                                  label_visibility="collapsed") or "All"
                    log = c2.toggle("Log scale", key="log", help="Equal distances mean equal % changes: "
                                    "useful when one asset dwarfs the others.")
                    shown = display if window == "All" else display[display.index >= display.index.max() - pd.DateOffset(years=window)]
                    show(charts.comparison_lines(normalise_prices(shown), highlighted, stable_colors(highlighted), log=log),
                         height=440)
                    st.caption("× = value at the end divided by the value at the start of the window.")
                    with st.expander("Each asset on its own scale"):
                        show(charts.small_multiples(normalise_prices(shown), "Growth of 100", ",.0f", independent_y=True))

                if section == "Risk":
                    a, b = st.columns(2, gap="medium")
                    with a:
                        title("Deepest fall", "Worst drop from a previous peak, in %.", label="Ranking")
                        falls = summary[["Max drawdown (%)"]].abs().rename(columns={"Max drawdown (%)": "Deepest fall (%)"})
                        show(charts.lollipops(falls, "Deepest fall (%)", ".0f"))
                    with b:
                        title("Volatility", "Typical size of the moves, in % per year.", label="Ranking")
                        show(charts.lollipops(summary, "Annual volatility (%)", ".0f"))
                    st.write("")
                    title("Under water", "How far each asset sat below its previous peak, day after day. "
                          "The worst point is marked.", label="Chart")
                    dd_default = list(dict.fromkeys([worst_dd, summary["Max drawdown (%)"].idxmax()]))
                    dd_highlighted = st.pills("Highlight drawdown", assets, selection_mode="multi", default=dd_default,
                                              key="dd_highlight", label_visibility="collapsed")[:MAX_HIGHLIGHT]
                    show(charts.underwater(compute_drawdown(display), dd_highlighted,
                                           stable_colors(dd_highlighted, "dd_colors")), height=380)

                if section == "Data":
                    title("All figures", "Annualised with the number of common trading days actually observed.")
                    st.dataframe(summary, width="stretch", column_config={
                        "Total return (%)": st.column_config.NumberColumn(format="%.1f %%"),
                        "Annual return (%)": st.column_config.NumberColumn(format="%.1f %%"),
                        "Annual volatility (%)": st.column_config.NumberColumn(format="%.1f %%"),
                        "Return / risk ratio": st.column_config.NumberColumn(format="%.2f"),
                        "Max drawdown (%)": st.column_config.NumberColumn(format="%.1f %%"),
                    })
                    st.write("")
                    title("Currencies", None)
                    st.dataframe(pd.DataFrame({
                        "Asset": [names.get(t, t) for t in info["currency_by_ticker"]],
                        "Ticker": list(info["currency_by_ticker"]),
                        "Quoted in": list(info["currency_by_ticker"].values()),
                    }), hide_index=True, width="stretch")
                    fx = ", ".join(info["fx_tickers"]) if info["fx_tickers"] else "none needed"
                    st.caption(f"Adjusted closing prices converted to {currency} (rates: {fx}). Only days when every "
                               f"market was open are kept: {info['rows_before'] - info['rows_after']:,} removed.")
                    st.download_button("Download dataset (CSV)", prices.to_csv().encode("utf-8"),
                                       file_name="dataset_clean.csv", mime="text/csv", icon=":material/download:")
            html('<div class="foot">Past performance does not predict future returns. '
                 'Educational project, not investment advice.</div>')


# ================================================================= page
st.set_page_config(page_title="Portfolio analysis", page_icon=":material/donut_large:", layout="wide",
                   initial_sidebar_state="collapsed")
html(style.CSS)
init_state()

if st.session_state["step"] == "project":
    project_page()
elif st.session_state["step"] == "report" and len(st.session_state["portfolio"]) >= MIN_ASSETS:
    report_page()
else:
    build_page()

"""Web interface for parts 1 to 3 of the project.

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
from src.analysis import build_summary, compute_drawdown, compute_returns, normalise_prices  # noqa: E402
from src.correlation import (EXTREME_SHARE, REFERENCE_TICKER, ROLLING_WINDOW,  # noqa: E402
                             compute_average_correlation, compute_correlation, compute_extreme_days,
                             compute_portfolio_average_correlation, compute_rolling_correlation,
                             compute_weekly_returns, correlation_pairs)
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
SECTIONS = ["Overview", "Performance", "Risk", "Correlations", "Data"]
SECTION_ICONS = {"Overview": ":material/dashboard:", "Performance": ":material/trending_up:",
                 "Risk": ":material/waterfall_chart:", "Correlations": ":material/grid_on:",
                 "Data": ":material/table_rows:"}
CORR_VIEWS = ["Weekly", "Daily", "Weekly − daily"]
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


def show(chart, height=None, stretch=True, key=None):
    target = st.container(key=key) if key else st
    target.altair_chart(charts.styled(chart, height), theme=None, width="stretch" if stretch else "content")


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


def set_focus(ticker):
    """Click on an asset in the portfolio panel: show its detail; click again to go back."""
    st.session_state["focus"] = None if st.session_state.get("focus") == ticker else ticker


def clear_focus():
    st.session_state["focus"] = None


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


def close_nudge():
    st.session_state["nudge_closed"] = True


def open_project_from_nudge():
    st.session_state["nudge_closed"] = True
    go_project()


def project_nudge():
    """Small floating card (bottom right) inviting visitors to look at the project page."""
    with st.container(key="nudge"):
        html(style.nudge(author.PHOTO, "Hi, I'm Elouen 👋",
                         "Your future data intern. Curious how I built this? Take a look at my process."))
        a, b = st.columns([3, 1], vertical_alignment="center")
        a.button("See my process", key="nudge_go", type="primary", icon=":material/arrow_forward:",
                 on_click=open_project_from_nudge, width="stretch")
        b.button("Later", key="nudge_close", type="tertiary", on_click=close_nudge)


def app_bar(step, meta=""):
    """Top bar: mark on the left, clickable navigation in the middle, context on the right.
    step: 0 = project, 1 = portfolio, 2 = report."""
    st.session_state["nav"] = NAV[step]
    if step in (1, 2) and not st.session_state.get("nudge_closed"):
        project_nudge()
    left, middle, right = st.columns([1, 1.5, 1], vertical_alignment="center")
    html(style.mark(), left)
    middle.segmented_control("Navigation", NAV, key="nav", on_change=navigate, label_visibility="collapsed")
    html(f'<div class="appmeta">{style.esc(meta)}</div>', right)


# ================================================================= report helpers
def asset_grid(df, value_name, y_format):
    """One small chart per asset, two per row, each with its own scale (fits any width)."""
    columns = list(df.columns)
    for start in range(0, len(columns), 2):
        cols = st.columns(2, gap="medium")
        for col, asset in zip(cols, columns[start:start + 2]):
            with col:
                show(charts.small_chart(df[[asset]], value_name, y_format), height=150)


def asset_detail(ticker, names, summary, display, info, currency, period):
    """Analysis of one asset only: the same indicators as the portfolio view (notebook 02)."""
    name = names.get(ticker, ticker)
    row = summary.loc[name]
    head, close = st.columns([5, 1], vertical_alignment="center")
    html(style.asset_header(name, ticker, info["currency_by_ticker"].get(ticker, ""), currency, period), head)
    close.button("Close", key="close_focus", type="tertiary", icon=":material/close:", on_click=clear_focus)
    html(style.cards([
        ("up", "Total return", f"{row['Total return (%)']:+.1f}%", "whole period", ""),
        ("up", "Annual", f"{row['Annual return (%)']:+.1f}%", "per year", ""),
        ("pulse", "Volatility", f"{row['Annual volatility (%)']:.1f}%", "per year", ""),
        ("target", "Ratio", f"{row['Return / risk ratio']:.2f}", "return ÷ risk", ""),
        ("down", "Deepest fall", f"{row['Max drawdown (%)']:.1f}%", "from a peak", ""),
    ], "five"))
    title("Growth of 100", "The asset starts at 100 at the beginning of the period.", label="Chart")
    one = {name: style.SERIES[0]}
    show(charts.comparison_lines(normalise_prices(display[[name]]), [name], one), height=360)
    st.write("")
    title("Under water", "How far the asset sat below its previous peak, day after day.", label="Chart")
    show(charts.underwater(compute_drawdown(display[[name]]), [name], one), height=300)


def reading(markup, warning=""):
    """Short automatic reading under a chart (computed, so it follows the data)."""
    html(f'<div class="read">{markup}' + (f'<span class="warn">{style.esc(warning)}</span>' if warning else "")
         + "</div>")


def pair_name(pair):
    return f"{pair[0]} & {pair[1]}"


def correlation_section(prices, names):
    """Part 3 (notebook 03): how the assets move together."""
    display = prices.rename(columns=names)
    short = {names.get(t, t): t for t in prices.columns}  # tickers on the heatmap axes
    returns = compute_returns(display)
    daily = compute_correlation(returns)
    weekly = compute_correlation(compute_weekly_returns(display))
    pairs = correlation_pairs(weekly)  # weekly by default: fairer between markets with different hours
    average = compute_average_correlation(weekly)  # weekly, as in notebook 03
    portfolio_average = compute_portfolio_average_correlation(weekly)

    # Reference = MSCI World when it is in the portfolio, otherwise chosen by the user
    if REFERENCE_TICKER in prices.columns:
        reference = names.get(REFERENCE_TICKER, REFERENCE_TICKER)
        ref_note = f"Reference: {reference}, used as the global market."
    else:
        ref_note = ""
        reference = st.selectbox(
            "Reference asset (the market)", list(display.columns), key="corr_ref",
            help="The MSCI World (IWDA.AS) is used when it is in the portfolio. Otherwise, pick the asset that best "
                 "represents the market for you: the rolling and stress charts compare everything with it.")
    extreme = compute_extreme_days(returns, reference)
    worst_minus_best = extreme["worst_minus_best"]
    stress_pairs = correlation_pairs(worst_minus_best)
    others = [a for a in display.columns if a != reference]

    html(style.cards([
        ("target", "Most linked", f"{pairs.max():.2f}", pair_name(pairs.idxmax()), "weekly correlation"),
        ("pulse", "Best diversifier", f"{average.iloc[0]:.2f}", average.index[0], "weekly, average with the others")
        if len(average) > 2 else ("pulse", "Least linked", f"{pairs.min():.2f}", pair_name(pairs.idxmin()),
                                  "weekly correlation"),
        ("up", "Portfolio score", f"{portfolio_average:.2f}", f"{len(pairs)} pairs", "weekly average correlation"),
        ("down", "In falls", f"{(stress_pairs > 0).sum()} / {len(stress_pairs)}", "pairs more linked",
         "worst vs best days"),
    ]))

    # --- 1. Correlation matrix
    title("Correlation matrix", "Every pair of assets (the diagonal is each asset with itself). +1: they move together. 0: independent, which already reduces "
          "risk. -1: opposite moves.", label="Chart")
    view = st.segmented_control("Matrix", CORR_VIEWS, key="corr_view", default=CORR_VIEWS[0],
                                label_visibility="collapsed") or CORR_VIEWS[0]
    if view == "Weekly − daily":
        diff = weekly - daily
        show(charts.correlation_heatmap(diff, limit=0.4, short=short), stretch=False, key="matrix_diff")
        biggest = correlation_pairs(diff)
        reading(f"Red: more linked with weekly returns. The biggest increase is <b>{style.esc(pair_name(biggest.idxmax()))}"
                f"</b> ({biggest.max():+.2f}). Markets close at different times (Europe 17:30, New York 22:00, "
                "crypto never): a move after the European close shows up the next day, which lowers daily "
                "correlations between markets. Weekly returns reduce this effect.")
    else:
        matrix = daily if view == "Daily" else weekly
        view_pairs, view_average = correlation_pairs(matrix), compute_average_correlation(matrix)
        show(charts.correlation_heatmap(matrix, value_format=".2f", short=short), stretch=False, key="matrix_main")
        top = view_pairs.max()
        text = f"Most linked: <b>{style.esc(pair_name(view_pairs.idxmax()))}</b> ({top:.2f})"
        text += ", so holding both adds little diversification." if top >= 0.6 else "."
        if len(view_average) > 2:
            text += (f" Least linked to the rest: <b>{style.esc(view_average.index[0])}</b> "
                     f"({view_average.iloc[0]:.2f} on average).")
        reading(text,
                "Daily returns: markets close at different times, which lowers the links between them."
                if view == "Daily" else "Weekly returns (last price of each week): fairer between markets that close at "
                "different times. Computed on returns, not prices.")

    # --- 2. Rolling correlation
    title(f"Correlation with {reference} over time", f"Moving window of {ROLLING_WINDOW} trading days (about 3 "
          "months). One number over the whole period is an average: this shows whether the link holds. Daily returns: "
          "weekly ones would leave too few points in each window.",
          label="Chart")
    if ref_note:
        st.caption(ref_note)
    if len(returns) < ROLLING_WINDOW * 2:
        st.info(f"The period is too short for a {ROLLING_WINDOW}-day rolling correlation. Choose a longer period.")
    else:
        rolling = compute_rolling_correlation(returns, reference)
        spread = (rolling.max() - rolling.min()).sort_values()
        default = list(dict.fromkeys([rolling.mean().idxmax(), rolling.mean().abs().idxmin(), spread.index[-1]]))
        highlighted = st.pills("Highlight correlation", others, selection_mode="multi", default=default,
                               key="corr_highlight", label_visibility="collapsed")[:MAX_HIGHLIGHT]
        show(charts.rolling_lines(rolling, highlighted, stable_colors(highlighted, "corr_colors")), height=380)
        stable, swing = spread.index[0], spread.index[-1]
        if stable == swing:
            text = (f"<b>{style.esc(stable)}</b> moves between {rolling[stable].min():+.2f} and "
                    f"{rolling[stable].max():+.2f}.")
        else:
            text = (f"Most stable: <b>{style.esc(stable)}</b> (between {rolling[stable].min():+.2f} and "
                    f"{rolling[stable].max():+.2f}). Biggest swing: <b>{style.esc(swing)}</b> (from "
                    f"{rolling[swing].min():+.2f} to {rolling[swing].max():+.2f}).")
        reading(text + " A correlation is not fixed over time: the average alone is not enough.")

    # --- 3. Market stress
    share = f"{EXTREME_SHARE:.0%}"
    title(f"When {reference} falls", f"Correlation on its {share} worst days minus its {share} best days. Red: the "
          "pair moves together more when the market falls. Daily returns: weekly ones would leave too few weeks.",
          label="Chart")
    show(charts.correlation_heatmap(worst_minus_best, limit=0.5, short=short), stretch=False, key="matrix_stress")
    worst_with_ref = extreme["worst_corr"][reference].drop(reference).sort_values(key=abs)
    n_up, n_pairs = int((stress_pairs > 0).sum()), len(stress_pairs)
    text = (f"{extreme['n_worst']} worst days (at most {extreme['worst_threshold']:.1%}) against {extreme['n_best']} "
            "best days. Comparing the two removes a bias: keeping only extreme days lowers every correlation. ")
    if n_pairs == 1:
        text += f"This pair is <b>{'more' if n_up else 'less'} linked</b> when the market falls."
    else:
        text += f"<b>{n_up} of {n_pairs}</b> pairs are more linked when the market falls."
    least, least_value = worst_with_ref.index[0], worst_with_ref.iloc[0]
    if len(worst_with_ref) > 1 and abs(least_value) < 0.3:
        text += (f" On the worst days, the least linked to {style.esc(reference)} is <b>{style.esc(least)}</b> "
                 f"({least_value:+.2f}): it still diversifies when it is needed most.")
    reading(text)


# ================================================================= screen 0: project timeline
def project_page():
    done = sum(s["status"] == "done" for s in timeline.STEPS)
    app_bar(0, f"{done} of {len(timeline.STEPS)} steps done")
    with st.container(key="page_project"):
        html('<div class="p-top"><div>' + style.timeline_head(timeline.INTRO, timeline.CREDITS, timeline.STEPS)
             + '</div>' + style.profile_card(author.NAME, author.HANDLE, author.PRONOUNS, author.PHOTO,
                                             author.BIO, author.STATUS, author.LINKS) + '</div>')
        html(style.timeline_steps(timeline.STEPS))


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
                "Section", SECTIONS, key="section", default=SECTIONS[0], label_visibility="collapsed", on_change=clear_focus,
                format_func=lambda s: f"{SECTION_ICONS[s]} {s}") or SECTIONS[0]
            html(f'<div class="navctx">{len(assets)} assets · {years}Y · {info["rows_after"]:,} trading days</div>',
                 nav_right)

        side, main = st.columns([1.3, 2.7], gap="large")

        # --- Portfolio panel
        with side, st.container(border=True):
            title("Portfolio", f"Ranked by annual return, in {currency}", label="Holdings")
            normalised = normalise_prices(prices)
            by_return = summary.sort_values("Annual return (%)", ascending=False)
            focus = st.session_state.get("focus")
            for i, ticker in enumerate(by_return.rename(index={v: k for k, v in names.items()}).index):
                name = names.get(ticker, ticker)
                right = style.sparkline(normalised[ticker]) + style.change_chip(summary.loc[name, "Annual return (%)"])
                with st.container(key=f"assetrow_{'on' if ticker == focus else 'off'}_{i}"):
                    html(style.asset_row(name, ticker, right=right))
                    st.button(f"Details for {name}", key=f"focus_{ticker}", on_click=set_focus, args=(ticker,))
            st.caption("Click an asset to see its own analysis.")
            st.button("Edit portfolio", icon=":material/edit:", on_click=go_build, width="stretch")

        with main:
            best_ret = summary["Annual return (%)"].idxmax()
            best_ratio = summary["Return / risk ratio"].idxmax()
            most_vol = summary["Annual volatility (%)"].idxmax()
            worst_dd = summary["Max drawdown (%)"].idxmin()
            portfolio_corr = compute_portfolio_average_correlation(compute_correlation(compute_weekly_returns(prices)))

            focus = st.session_state.get("focus")
            if focus in prices.columns:
                with st.container(key=f"sec_asset_{list(prices.columns).index(focus)}"):
                    asset_detail(focus, names, summary, display, info, currency, period)
                section = None  # the analysis sections are hidden while an asset is open

            with st.container(key=f"sec_{(section or 'none').lower()}"):  # new key per section -> fade-in
                if section == "Overview":
                    html(style.cards([
                        ("up", "Best return", f"{summary.loc[best_ret, 'Annual return (%)']:+.1f}%", best_ret, "per year"),
                        ("target", "Best for risk", f"{summary.loc[best_ratio, 'Return / risk ratio']:.2f}",
                         best_ratio, "return ÷ volatility"),
                        ("pulse", "Most volatile", f"{summary.loc[most_vol, 'Annual volatility (%)']:.0f}%", most_vol,
                         "typical move per year"),
                        ("down", "Deepest fall", f"{summary.loc[worst_dd, 'Max drawdown (%)']:.0f}%", worst_dd,
                         "from a previous peak"),
                        ("target", "Correlation", f"{portfolio_corr:.2f}", "portfolio score",
                         "weekly average of all pairs"),
                    ], "five"))
                    title("Return vs risk", "Top left is best: more return for less volatility.", label="Chart")
                    show(charts.return_risk_scatter(summary), height=440)
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
                    show(charts.comparison_lines(normalise_prices(display), highlighted, stable_colors(highlighted)),
                         height=440)
                    st.caption("× = value at the end divided by the value at the start of the period.")
                    with st.expander("Each asset on its own scale"):
                        asset_grid(normalise_prices(display), "Growth of 100", ",.0f")

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
                    title("Under water", "How far each asset sat below its previous peak, day after day.",
                          label="Chart")
                    dd_default = list(dict.fromkeys([worst_dd, summary["Max drawdown (%)"].idxmax()]))
                    dd_highlighted = st.pills("Highlight drawdown", assets, selection_mode="multi", default=dd_default,
                                              key="dd_highlight", label_visibility="collapsed")[:MAX_HIGHLIGHT]
                    show(charts.underwater(compute_drawdown(display), dd_highlighted,
                                           stable_colors(dd_highlighted, "dd_colors")), height=380)

                if section == "Correlations":
                    correlation_section(prices, names)

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

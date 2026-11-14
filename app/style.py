"""Design tokens and UI building blocks.

Direction: a mix of a bold personal-portfolio look (huge Black-weight headlines with an
ink-to-blue gradient, monospace labels, a blinking blue cursor, neutral zinc palette)
and a calm product UI (hairline cards, panels, tabs, a warm off-white page).
"""

import base64
import html
from pathlib import Path

import numpy as np

# Surfaces & ink
PAGE = "#fafaf8"
SURFACE = "#ffffff"
SUNKEN = "#f4f4f2"
INK = "#09090b"
INK_2 = "#52525b"
MUTED = "#a1a1aa"
LINE = "#e4e4e7"
GRID = "#efeff1"
AXIS = "#d4d4d8"
CONTEXT_LINE = "#dcdce0"
ACCENT = "#2563eb"
ACCENT_INK = "#1d4fd8"

# Chart colours, validated for colour-blind separation and >= 3:1 on SURFACE (all pairs)
SERIES = ["#2563eb", "#c8562c", "#2f9672"]
POSITIVE = "#2563eb"
NEGATIVE = "#c8562c"
POSITIVE_TEXT = "#1d4fd8"
NEGATIVE_TEXT = "#a8461f"

FONT = '"Fira Sans", system-ui, -apple-system, "Segoe UI", sans-serif'
MONO = '"Fira Code", ui-monospace, "Cascadia Code", Consolas, monospace'

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600;700;800;900&family=Fira+Code:wght@400;500&display=swap');
:root {{
  --page:{PAGE}; --surface:{SURFACE}; --sunken:{SUNKEN}; --ink:{INK}; --ink-2:{INK_2}; --muted:{MUTED};
  --line:{LINE}; --accent:{ACCENT}; --accent-ink:{ACCENT_INK}; --sans:{FONT}; --mono:{MONO};
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}}
html, body, .stApp, .stMarkdown, button, input, textarea {{ font-family: var(--sans); -webkit-font-smoothing: antialiased; }}
.stApp {{ background: var(--page); color: var(--ink); }}
::selection {{ background: var(--ink); color: var(--page); }}
.block-container {{ max-width: 1240px; padding-top: 1.2rem; padding-bottom: 4rem; }}
header[data-testid="stHeader"] {{ background: transparent; height: 0; }}
section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {{ display: none; }}
h1, h2, h3, h4 {{ font-family: var(--sans) !important; color: var(--ink); }}

/* Report navigation: frosted-glass bar that stays at the top while scrolling */
/* Streamlit wraps the container in a box of its own height: the sticky element is that wrapper */
div:has(> .st-key-reportnav) {{ position: sticky; top: .75rem; z-index: 50; }}
.st-key-reportnav {{ margin-bottom: 1.4rem;
  background: linear-gradient(115deg, rgba(37,99,235,.07), rgba(255,255,255,.55) 45%, rgba(255,255,255,.55));
  -webkit-backdrop-filter: blur(16px) saturate(160%); backdrop-filter: blur(16px) saturate(160%);
  border: 1px solid rgba(228,228,231,.9); border-radius: 18px; padding: .45rem .6rem .45rem .45rem;
  box-shadow: 0 10px 30px rgba(9,9,11,.06), inset 0 1px 0 rgba(255,255,255,.8); }}
.st-key-reportnav [data-testid="stHorizontalBlock"] {{ gap: .5rem; }}
.st-key-reportnav button {{ background: transparent !important; border: 1px solid transparent !important;
  border-radius: 12px !important; color: var(--ink-2) !important; font-weight: 500 !important;
  padding: .45rem .85rem !important; transition: background .2s ease, color .2s ease; }}
.st-key-reportnav button:hover {{ background: rgba(255,255,255,.7) !important; color: var(--ink) !important; }}
.st-key-reportnav button[aria-checked="true"] {{ background: #ffffff !important; color: var(--accent) !important;
  border-color: rgba(37,99,235,.18) !important; box-shadow: 0 2px 10px rgba(37,99,235,.12); }}
.navctx {{ text-align: right; margin-top: -10px; font-family: var(--mono); font-size: .7rem; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-2); }}
@media (max-width: 760px) {{ .navctx {{ display: none; }} }}

/* Logo sits on the text baseline and is exactly as tall as the capitals (Fira Code cap height = 0.69 em) */
.mark .logo {{ height: .7em; width: auto; display: inline-block; vertical-align: baseline; margin-left: .1em; }}
.mark .mdot {{ color: var(--accent); font-weight: 600; letter-spacing: 0; margin-left: -.32em; }}

/* Section switch inside the report: soft fade + rise */
@keyframes sectionIn {{ from {{ opacity: 0; transform: translateY(12px); filter: blur(3px); }}
                        to {{ opacity: 1; transform: none; filter: none; }} }}
[class*="st-key-sec_"] {{ animation: sectionIn .42s var(--ease-out) both; }}

/* Chart toolbar off (download lives in the Data section) */
[data-testid="stVegaLiteChart"] [data-testid="stElementToolbar"], .stElementContainer:has([data-testid="stVegaLiteChart"]) [data-testid="stElementToolbar"] {{ display: none !important; }}

/* Chart tooltip, in the house style */
#vg-tooltip-element.vg-tooltip {{ font-family: var(--sans) !important; font-size: 12px !important; color: var(--ink) !important;
  background: rgba(255,255,255,.9) !important; -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
  border: 1px solid var(--line) !important; border-radius: 12px !important; padding: .55rem .75rem !important;
  box-shadow: 0 12px 32px rgba(9,9,11,.10) !important; }}
#vg-tooltip-element.vg-tooltip td.key {{ font-family: var(--mono) !important; font-size: 10px !important; letter-spacing: .1em;
  text-transform: uppercase; color: var(--muted) !important; text-align: left !important; padding-right: 1rem !important; }}
#vg-tooltip-element.vg-tooltip td.value {{ font-family: var(--mono) !important; font-weight: 500; text-align: right !important; color: var(--ink) !important; }}

/* Option controls (period, currency, years): separate rounded chips in mono */
.st-key-window [data-testid="stButtonGroup"], .st-key-currency_choice [data-testid="stButtonGroup"],
.st-key-years_choice [data-testid="stButtonGroup"] {{ gap: .35rem; flex-wrap: wrap; }}
.st-key-window button, .st-key-currency_choice button, .st-key-years_choice button {{
  border-radius: 999px !important; border: 1px solid var(--line) !important; background: var(--surface) !important;
  font-family: var(--mono) !important; font-size: .74rem !important; letter-spacing: .08em; color: var(--ink-2) !important;
  padding: .35rem .85rem !important; box-shadow: none !important; transition: border-color .2s ease, color .2s ease, background .2s ease; }}
.st-key-window button p, .st-key-currency_choice button p, .st-key-years_choice button p {{ font-family: var(--mono) !important; font-size: .74rem !important; }}
.st-key-window button:hover, .st-key-currency_choice button:hover, .st-key-years_choice button:hover {{ border-color: var(--ink-2) !important; color: var(--ink) !important; }}
.st-key-window button[aria-checked="true"], .st-key-currency_choice button[aria-checked="true"],
.st-key-years_choice button[aria-checked="true"] {{ background: var(--ink) !important; border-color: var(--ink) !important; color: #fff !important; }}

/* Asset pills (highlight on charts): quiet chips, selected ones tinted with the accent and a dot */
.st-key-highlight [data-testid="stButtonGroup"], .st-key-dd_highlight [data-testid="stButtonGroup"] {{ gap: .35rem; flex-wrap: wrap; }}
.st-key-highlight button, .st-key-dd_highlight button {{ border-radius: 999px !important; border: 1px solid var(--line) !important;
  background: var(--surface) !important; color: var(--ink-2) !important; font-size: .82rem !important; font-weight: 500 !important;
  padding: .3rem .8rem !important; box-shadow: none !important; transition: all .2s ease; }}
.st-key-highlight button p, .st-key-dd_highlight button p {{ font-size: .82rem !important; }}
.st-key-highlight button:hover, .st-key-dd_highlight button:hover {{ border-color: var(--ink-2) !important; color: var(--ink) !important; }}
.st-key-highlight button[aria-pressed="true"], .st-key-dd_highlight button[aria-pressed="true"] {{
  background: rgba(37,99,235,.07) !important; border-color: rgba(37,99,235,.35) !important; color: var(--accent-ink) !important; }}

/* Toggle label in mono */
.st-key-log label p {{ font-family: var(--mono) !important; font-size: .72rem !important; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-2); }}

/* Project timeline (page 00) */
.st-key-page_project {{ animation: slideFromLeft .5s var(--ease-out) both; }}
.tl-intro {{ max-width: 680px; color: var(--ink-2); font-size: 1rem; line-height: 1.65; margin: .4rem 0 2.6rem; }}
.tl-progress {{ display:flex; align-items:center; gap:.8rem; margin: -1.6rem 0 2.8rem; max-width: 680px; }}
.tl-bar {{ flex:1; height: 4px; border-radius: 999px; background: var(--sunken); overflow:hidden; }}
.tl-bar span {{ display:block; height:100%; background: var(--ink); border-radius: 999px; }}
.tl-progress .lbl {{ font-family: var(--mono); font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color: var(--muted); white-space:nowrap; }}
.tl {{ position: relative; max-width: 760px; margin-left: .4rem; }}
.tl::before {{ content:""; position:absolute; left: 11px; top: 6px; bottom: 6px; width: 1px; background: var(--line); }}
.tl-item {{ position: relative; padding: 0 0 2.2rem 3rem; animation: sectionIn .5s var(--ease-out) both; }}
.tl-item:nth-child(2) {{ animation-delay: .05s; }} .tl-item:nth-child(3) {{ animation-delay: .1s; }}
.tl-item:nth-child(4) {{ animation-delay: .15s; }} .tl-item:nth-child(5) {{ animation-delay: .2s; }}
.tl-item:nth-child(6) {{ animation-delay: .25s; }} .tl-item:nth-child(7) {{ animation-delay: .3s; }}
.tl-item:nth-child(8) {{ animation-delay: .35s; }} .tl-item:nth-child(9) {{ animation-delay: .4s; }}
.tl-node {{ position:absolute; left: 4px; top: 4px; width: 15px; height: 15px; border-radius: 50%;
  background: var(--page); border: 1.5px solid {AXIS}; box-sizing: border-box; }}
.tl-item.done .tl-node {{ background: var(--ink); border-color: var(--ink); }}
.tl-item.progress .tl-node {{ border-color: var(--accent); background: var(--page); box-shadow: 0 0 0 4px rgba(37,99,235,.12); }}
.tl-item.progress .tl-node::after {{ content:""; position:absolute; inset: 3px; border-radius: 50%; background: var(--accent); }}
.tl-head {{ display:flex; align-items: baseline; gap: .7rem; flex-wrap: wrap; }}
.tl-num {{ font-family: var(--mono); font-size: .72rem; letter-spacing: .14em; color: var(--muted); }}
.tl-title {{ font-size: 1.3rem; font-weight: 800; letter-spacing: -0.02em; color: var(--ink); }}
.tl-item.planned .tl-title {{ color: var(--muted); }}
.tl-status {{ font-family: var(--mono); font-size: .64rem; letter-spacing: .12em; text-transform: uppercase;
  padding: .12rem .5rem; border-radius: 999px; border: 1px solid var(--line); color: var(--muted); }}
.tl-item.done .tl-status {{ color: var(--ink); border-color: var(--ink); }}
.tl-item.progress .tl-status {{ color: var(--accent-ink); border-color: rgba(37,99,235,.35); background: rgba(37,99,235,.06); }}
.tl-where {{ font-family: var(--mono); font-size: .72rem; color: var(--muted); margin: .3rem 0 .45rem; }}
.tl-summary {{ color: var(--ink-2); margin: 0 0 .5rem; max-width: 640px; }}
.tl-points {{ margin: 0; padding-left: 1rem; max-width: 640px; }}
.tl-points li {{ color: var(--ink-2); font-size: .9rem; margin: .2rem 0; line-height: 1.55; }}
.tl-points li::marker {{ color: {AXIS}; }}

/* Author card (page 00) */
div:has(> .st-key-profile) {{ position: sticky; top: 1.2rem; }}
.pc {{ background: var(--surface); border: 1px solid var(--line); border-radius: 18px; padding: 1.4rem 1.3rem 1.1rem; }}
.pc-photo {{ width: 104px; height: 104px; border-radius: 50%; padding: 6px; margin-bottom: 1rem;
  border: 1px solid rgba(37,99,235,.18); box-shadow: 0 0 0 8px var(--surface), 0 0 0 9px rgba(37,99,235,.08); }}
.pc-photo img {{ width: 100%; height: 100%; border-radius: 50%; object-fit: cover; display: block; }}
.pc-name {{ font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em; color: var(--ink); line-height: 1.15; }}
.pc-handle {{ font-family: var(--mono); font-size: .74rem; color: var(--muted); margin: .25rem 0 .8rem; }}
.pc-bio {{ color: var(--ink-2); font-size: .9rem; line-height: 1.55; margin: 0 0 .9rem; }}
.pc-status {{ display: inline-flex; align-items: center; gap: .45rem; font-family: var(--mono); font-size: .66rem;
  letter-spacing: .1em; text-transform: uppercase; color: var(--accent-ink); background: rgba(37,99,235,.06);
  border: 1px solid rgba(37,99,235,.25); border-radius: 999px; padding: .25rem .65rem; margin-bottom: 1rem; }}
.pc-status .dot {{ width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }}
.pc-links {{ border-top: 1px solid var(--line); }}
.pc-link {{ display: flex; justify-content: space-between; align-items: center; padding: .65rem .1rem;
  border-bottom: 1px solid var(--line); font-family: var(--mono); font-size: .74rem; letter-spacing: .12em;
  text-transform: uppercase; color: var(--ink) !important; text-decoration: none !important; transition: color .2s ease, padding .3s var(--ease-out); }}
.pc-link:last-child {{ border-bottom: none; }}
.pc-link .arr {{ color: var(--muted); transition: transform .3s var(--ease-out), color .2s ease; }}
.pc-link:hover {{ color: var(--accent) !important; padding-left: .35rem; }}
.pc-link:hover .arr {{ color: var(--accent); transform: translate(2px, -2px); }}

/* Page transitions: the new screen slides in from the side it comes from */
@keyframes slideFromRight {{ from {{ opacity: 0; transform: translateX(48px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes slideFromLeft  {{ from {{ opacity: 0; transform: translateX(-48px); }} to {{ opacity: 1; transform: none; }} }}
.st-key-page_report {{ animation: slideFromRight .5s var(--ease-out) both; }}
.st-key-page_build  {{ animation: slideFromLeft .5s var(--ease-out) both; }}
.stApp {{ overflow-x: clip; }}

/* App bar (clickable navigation = a segmented control styled as mono tabs) */
.st-key-nav {{ display:flex; justify-content:center; transform: translateY(8px); }}
[data-testid="stHorizontalBlock"]:has(.st-key-nav) {{ margin-bottom: 2.2rem; }}
.st-key-nav [data-testid="stButtonGroup"] {{ justify-content:center; }}
.st-key-nav button {{ font-family: var(--mono) !important; font-size:.72rem !important; letter-spacing:.14em; text-transform:uppercase;
  background: transparent !important; border: 1px solid transparent !important; border-radius: 999px !important;
  color: var(--muted) !important; padding: .35rem .9rem !important; box-shadow:none !important; cursor:pointer; }}
.st-key-nav button p {{ font-family: var(--mono) !important; font-size:.72rem !important; }}
.st-key-nav button:hover {{ color: var(--ink) !important; }}
.st-key-nav button[aria-checked="true"] {{ background: var(--surface) !important; color: var(--ink) !important; border-color: var(--line) !important; }}
/* "00 Project" blinks softly while another page is open, to invite a visit */
@keyframes navCall {{ 0%, 100% {{ color: var(--muted); }} 50% {{ color: var(--accent); }} }}
@keyframes navDot {{ 0%, 100% {{ opacity: .25; transform: scale(.8); }} 50% {{ opacity: 1; transform: scale(1); }} }}
.st-key-nav button:first-of-type[aria-checked="false"] p {{ animation: navCall 1.6s ease-in-out infinite; }}
.st-key-nav button:first-of-type[aria-checked="false"]::before {{ content: ""; width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent); margin-right: .45rem; display: inline-block; animation: navDot 1.6s ease-in-out infinite; }}
.st-key-nav button:first-of-type[aria-checked="false"]:hover p {{ animation: none; color: var(--ink); }}
.appmeta {{ text-align:right; font-family: var(--mono); font-size:.72rem; letter-spacing:.08em; color: var(--muted); }}
@media (max-width: 760px) {{ .appmeta {{ display:none; }} }}
/* App bar */
.appbar {{ display:flex; align-items:center; justify-content:space-between; padding:.4rem 0 1rem; margin-bottom: 2.4rem; }}
.mark {{ display:flex; align-items:baseline; gap:.6rem; font-family: var(--mono); font-size:.72rem; letter-spacing:.2em;
  text-transform:uppercase; color: var(--muted); }}
.nav {{ display:flex; gap:.25rem; font-family: var(--mono); font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; }}
.nav span {{ padding:.35rem .8rem; border-radius:999px; color: var(--muted); }}
.nav span.on {{ color: var(--ink); background: var(--surface); box-shadow: 0 0 0 1px var(--line); }}
.appbar .meta {{ font-family: var(--mono); font-size:.72rem; letter-spacing:.08em; color: var(--muted); }}
@media (max-width: 760px) {{ .appbar .meta {{ display:none; }} }}

/* Hero */
.eyebrow {{ font-family: var(--mono); font-size:.78rem; letter-spacing:.2em; text-transform:uppercase; color: var(--muted); margin-bottom: 1rem; }}
.stApp h1.hero {{ font-weight: 900 !important; font-size: clamp(2.8rem, 6.4vw, 5.6rem) !important; line-height: .95 !important;
  letter-spacing: -0.05em !important; margin: 0 0 1.1rem !important; padding: 0 0 .08em !important;
  background: linear-gradient(100deg, {INK} 0%, {INK} 45%, #3f3f46 78%, {ACCENT} 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent; padding-bottom: .08em; }}
.hero .dot {{ color: {ACCENT}; -webkit-text-fill-color: {ACCENT}; }}
.tagline {{ font-size: 1.25rem; color: var(--ink); margin: 0 0 .35rem; }}
.cursor {{ color: var(--accent); font-weight: 600; animation: blink 1.1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.byline {{ color: var(--ink-2); font-size: .9rem; margin: 0 0 2.6rem; }}

/* Panel headings */
.label {{ font-family: var(--mono); font-size:.7rem; letter-spacing:.18em; text-transform:uppercase; color: var(--muted); margin:.2rem 0 .45rem; }}
.h {{ font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em; color: var(--ink); margin: 0 0 .2rem; }}
.sub {{ color: var(--ink-2); font-size: .9rem; margin: 0 0 1rem; }}
.cap {{ font-family: var(--mono); font-size:.68rem; letter-spacing:.16em; text-transform:uppercase; color: var(--muted); margin: 1.3rem 0 .5rem; }}

/* Asset rows */
.row {{ display:flex; align-items:center; gap:.7rem; min-width:0; }}
.avatar {{ flex:0 0 34px; height:34px; border-radius: 50%; background: var(--sunken); color: var(--ink);
  display:flex; align-items:center; justify-content:center; font-size:.7rem; font-weight:800; letter-spacing:-.01em;
  box-shadow: 0 0 0 1px var(--line); }}
.who {{ min-width:0; flex:1 1 auto; }}
.who .n {{ font-weight:600; color:var(--ink); font-size:.92rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.who .t {{ font-family: var(--mono); color:var(--muted); font-size:.7rem; letter-spacing:.06em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.spark {{ flex:0 0 auto; }}
.chip {{ flex:0 0 auto; font-family: var(--mono); font-size:.74rem; font-weight:500; padding:.14rem .5rem; border-radius:999px; background: var(--sunken); }}
.chip.up {{ color: {POSITIVE_TEXT}; }} .chip.down {{ color: {NEGATIVE_TEXT}; }}

/* Insight cards */
.cards {{ display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:.8rem; margin-bottom: 1.6rem; }}
@media (max-width: 980px) {{ .cards {{ grid-template-columns: repeat(2, minmax(0,1fr)); }} }}
.card {{ background: var(--surface); border:1px solid var(--line); border-radius: 16px; padding: 1.05rem 1.1rem;
  transition: transform .35s var(--ease-out), border-color .2s ease; }}
.card:hover {{ transform: translateY(-2px); border-color: {AXIS}; }}
.card .top {{ display:flex; align-items:center; gap:.5rem; white-space:nowrap; font-family: var(--mono); font-size:.64rem; letter-spacing:.1em; text-transform:uppercase; color: var(--muted); }}
.card .ic {{ width:26px; height:26px; border-radius:50%; background: var(--sunken); color: var(--ink);
  display:flex; align-items:center; justify-content:center; }}
.card .v {{ font-size: clamp(1.5rem, 2.3vw, 2.2rem); white-space: nowrap; font-weight: 900; letter-spacing: -0.04em; line-height:1; margin:.85rem 0 .4rem; color: var(--ink); }}
.card .a {{ font-size:.86rem; color: var(--ink); font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.card .d {{ font-size:.8rem; color: var(--ink-2); margin-top:.1rem; }}

/* Empty state */
.empty {{ border:1px dashed {AXIS}; border-radius:16px; padding:1.4rem; text-align:center; color: var(--ink-2); font-size:.9rem; }}
.empty b {{ display:block; color: var(--ink); font-weight:800; font-size:1rem; margin-bottom:.2rem; letter-spacing:-.01em; }}

/* Streamlit widgets */
[data-testid="stVerticalBlockBorderWrapper"] {{ border-color: var(--line) !important; border-radius: 18px !important; background: var(--surface); }}
.stTextInput input {{ background: var(--surface); border-radius: 14px; font-size: 1.05rem; padding: .85rem 1rem; }}
.stButton button, .stDownloadButton button {{ border-radius: 999px; font-weight: 600;
  transition: background .2s ease, border-color .2s ease, color .2s ease, transform .35s var(--ease-out); }}
.stButton button:hover {{ transform: translateY(-1px); }}
.stButton button[kind="primary"] {{ background: var(--ink); border-color: var(--ink); }}
.stButton button[kind="primary"]:hover {{ background: var(--accent); border-color: var(--accent); }}
.stButton button[kind="primary"]:disabled {{ background: var(--sunken); border-color: var(--line); color: var(--muted); transform: none; }}
.stButton button[kind="secondary"], .stDownloadButton button {{ background: var(--surface); border:1px solid var(--line); color: var(--ink); }}
.stButton button[kind="secondary"]:hover, .stDownloadButton button:hover {{ border-color: var(--ink); color: var(--ink); }}
.stButton button[kind="tertiary"] {{ color: var(--muted); }}
.stButton button[kind="tertiary"]:hover {{ color: var(--accent); }}
.stTabs [data-baseweb="tab-list"] {{ gap: .3rem; border-bottom: 1px solid var(--line); }}
.stTabs [data-baseweb="tab"] {{ padding: .6rem .9rem; font-family: var(--mono); font-size: .74rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }}
.stTabs [aria-selected="true"] {{ color: var(--ink); }}
.stTabs [data-baseweb="tab-highlight"] {{ background: var(--accent); }}
[data-testid="stVegaLiteChart"] {{ background: var(--surface); border:1px solid var(--line); border-radius: 16px;
  padding: .9rem .6rem .4rem; overflow:hidden; box-sizing:border-box; }}
[data-testid="stExpander"] details {{ border-color: var(--line); border-radius: 16px; background: var(--surface); }}
:focus-visible {{ outline: 2px solid var(--accent) !important; outline-offset: 3px; }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; animation: none !important; }} }}
.foot {{ margin-top: 3rem; font-family: var(--mono); font-size: .7rem; letter-spacing: .08em; color: var(--muted); }}
</style>
"""

# Small line icons (24px grid, stroke = currentColor)
ICONS = {
    "up": '<polyline points="3 17 9 11 13 15 21 7"/><polyline points="15 7 21 7 21 13"/>',
    "down": '<polyline points="3 7 9 13 13 9 21 17"/><polyline points="15 17 21 17 21 11"/>',
    "pulse": '<polyline points="2 12 6 12 9 4 15 20 18 12 22 12"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>',
}
LOGO = ('<svg width="22" height="22" viewBox="0 0 26 26" aria-hidden="true">'
        f'<circle cx="13" cy="13" r="11" fill="none" stroke="{INK}" stroke-width="1.8"/>'
        f'<path d="M13 2 A11 11 0 0 1 24 13 L13 13 Z" fill="{ACCENT}"/>'
        f'<path d="M13 13 L13 24 A11 11 0 0 1 4.5 20 Z" fill="{INK}"/></svg>')


def esc(text):
    return html.escape(str(text))


def icon(name, size=14):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def appbar(step, meta=""):
    nav = "".join(f'<span class="{"on" if i == step else ""}">{label}</span>'
                  for i, label in [(1, "01 Portfolio"), (2, "02 Report")])
    return (f'<div class="appbar"><div class="mark">{LOGO}Portfolio analysis</div>'
            f'<div class="nav">{nav}</div><div class="meta">{esc(meta)}</div></div>')


_LOGO_FILE = Path(__file__).resolve().parent / "assets" / "logo-nc.png"
_LOGO_B64 = base64.b64encode(_LOGO_FILE.read_bytes()).decode() if _LOGO_FILE.exists() else ""


def mark():
    logo = (f'<img class="logo" src="data:image/png;base64,{_LOGO_B64}" alt="NC">' if _LOGO_B64 else "")
    return f'<div class="mark">Portfolio analysis{logo}</div>'


def timeline(intro, steps):
    """Vertical timeline of the project steps."""
    labels = {"done": "Done", "progress": "In progress", "planned": "Planned"}
    done = sum(st["status"] == "done" for st in steps)
    progress = sum(st["status"] == "progress" for st in steps)
    pct = round((done + 0.5 * progress) / len(steps) * 100)
    items = []
    for step in steps:
        points = "".join(f"<li>{esc(p)}</li>" for p in step["points"])
        items.append(
            f'<div class="tl-item {step["status"]}"><span class="tl-node"></span>'
            f'<div class="tl-head"><span class="tl-num">{esc(step["num"])}</span>'
            f'<span class="tl-title">{esc(step["title"])}</span>'
            f'<span class="tl-status">{labels[step["status"]]}</span></div>'
            + (f'<div class="tl-where">{esc(step["where"])}</div>' if step["where"] else '<div class="tl-where"></div>')
            + f'<p class="tl-summary">{esc(step["summary"])}</p>'
            + (f'<ul class="tl-points">{points}</ul>' if points else "")
            + "</div>"
        )
    return (f'<p class="tl-intro">{esc(intro)}</p>'
            f'<div class="tl-progress"><div class="tl-bar"><span style="width:{pct}%"></span></div>'
            f'<span class="lbl">{pct}% complete</span></div>'
            f'<div class="tl">{"".join(items)}</div>')


def profile_card(name, handle, pronouns, photo_path, bio, status, links):
    """Small author card: photo in thin rings, name, handle, bio, status and links."""
    photo = Path(__file__).resolve().parent / photo_path
    img = (f'<img src="data:image/jpeg;base64,{base64.b64encode(photo.read_bytes()).decode()}" alt="{esc(name)}">'
           if photo.exists() else "")
    rows = "".join(
        f'<a class="pc-link" href="{esc(url)}" target="_blank" rel="noopener">'
        f'<span>{esc(label)}</span><span class="arr">↗</span></a>'
        for label, url in links if url
    )
    who = f"{esc(handle)}" + (f" · {esc(pronouns)}" if pronouns else "")
    return (f'<div class="pc"><div class="pc-photo">{img}</div>'
            f'<div class="pc-name">{esc(name)}</div><div class="pc-handle">{who}</div>'
            f'<p class="pc-bio">{esc(bio)}</p>'
            + (f'<div class="pc-status"><span class="dot"></span>{esc(status)}</div>' if status else "")
            + f'<div class="pc-links">{rows}</div></div>')


def hero(eyebrow, words, tagline, byline=""):
    """Big headline; the final full stop is drawn in the accent colour."""
    return (f'<div class="eyebrow">{esc(eyebrow)}</div>'
            f'<h1 class="hero">{esc(words)}<span class="dot">.</span></h1>'
            f'<p class="tagline">{esc(tagline)}<span class="cursor">_</span></p>'
            + (f'<p class="byline">{esc(byline)}</p>' if byline else '<p class="byline"></p>'))


def initials(name, ticker):
    words = [w for w in str(name or ticker).replace("-", " ").split() if w[:1].isalnum()]
    letters = "".join(w[0] for w in words[:2]).upper()
    return letters or str(ticker)[:2].upper()


def sparkline(values, width=60, height=24):
    """Tiny inline SVG: soft gradient area, line, and a dot on the last value."""
    v = np.asarray(values, dtype=float)
    if len(v) < 2:
        return ""
    idx = np.linspace(0, len(v) - 1, min(60, len(v))).astype(int)
    v = v[idx]
    lo, hi = v.min(), v.max()
    span = (hi - lo) or 1
    xs = np.linspace(1, width - 4, len(v))
    ys = height - 3 - (v - lo) / span * (height - 6)
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    color = POSITIVE if v[-1] >= v[0] else NEGATIVE
    gid = f"g{abs(hash((round(float(v[0]), 6), round(float(v[-1]), 6), len(v)))) % 10**8}"
    area = f"{xs[0]:.1f},{height} {pts} {xs[-1]:.1f},{height}"
    return (f'<svg class="spark" width="{width}" height="{height}" viewBox="0 0 {width} {height}" aria-hidden="true">'
            f'<defs><linearGradient id="{gid}" x1="0" x2="0" y1="0" y2="1">'
            f'<stop offset="0" stop-color="{color}" stop-opacity=".22"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>'
            f'</linearGradient></defs><polygon points="{area}" fill="url(#{gid})"/>'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="2.2" fill="{color}"/></svg>')


def asset_row(name, ticker, sub=None, right=""):
    return (f'<div class="row"><div class="avatar">{esc(initials(name, ticker))}</div>'
            f'<div class="who"><div class="n">{esc(name or ticker)}</div>'
            f'<div class="t">{esc(sub or ticker)}</div></div>{right}</div>')


def change_chip(pct):
    cls = "up" if pct >= 0 else "down"
    return f'<span class="chip {cls}">{pct:+.1f}%</span>'


def cards(items):
    """items: list of (icon, label, value, asset, detail)."""
    out = "".join(
        f'<div class="card"><div class="top"><span class="ic">{icon(ic)}</span>{esc(label)}</div>'
        f'<div class="v">{esc(value)}</div><div class="a" title="{esc(asset)}">{esc(asset)}</div>'
        f'<div class="d">{esc(detail)}</div></div>'
        for ic, label, value, asset, detail in items
    )
    return f'<div class="cards">{out}</div>'

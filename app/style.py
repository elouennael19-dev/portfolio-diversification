"""Design tokens and UI building blocks.

Direction: a mix of a bold personal-portfolio look (huge Black-weight headlines with an
ink-to-blue gradient, monospace labels, a blinking blue cursor, neutral zinc palette)
and a calm product UI (hairline cards, panels, tabs, a warm off-white page).
"""

import base64
import html
import re
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
div:has(> .st-key-reportnav) {{ position: sticky; top: 0; z-index: 50; padding: .7rem 0 .2rem; margin-top: -.7rem;
  background: var(--page); box-shadow: 0 10px 14px -10px var(--page); }}
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
[class*="st-key-sec_"] {{ animation: sectionIn .42s var(--ease-out) backwards; }}

/* Chart toolbar off (download lives in the Data section) */
[data-testid="stVegaLiteChart"] [data-testid="stElementToolbar"], .stElementContainer:has([data-testid="stVegaLiteChart"]) [data-testid="stElementToolbar"] {{ display: none !important; }}

/* Chart tooltip, in the house style */
#vg-tooltip-element:not(.visible) {{ display: none !important; }}
body:has(.st-key-page_build) #vg-tooltip-element, body:has(.st-key-page_project) #vg-tooltip-element {{ display: none !important; }}
#vg-tooltip-element.vg-tooltip {{ width: auto !important; max-width: 340px !important; font-family: var(--sans) !important; font-size: 12px !important; color: var(--ink) !important;
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
.st-key-page_project {{ animation: slideFromLeft .5s var(--ease-out) backwards; }}
.tl-intro {{ max-width: 640px; color: var(--ink); font-size: 1.25rem; font-weight: 600; letter-spacing: -0.01em; line-height: 1.4; margin: .4rem 0 1.2rem; }}
.credits {{ display: grid; gap: .45rem; margin: 0 0 2.4rem; max-width: 640px; }}
.cr {{ display: grid; grid-template-columns: 6.5rem max-content 1fr; align-items: baseline; gap: 1rem; }}
.cr-who, .cr-role {{ white-space: nowrap; }}
.cr-role {{ font-family: var(--mono); font-size: .68rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }}
.cr-who {{ font-weight: 700; color: var(--ink); }}
.cr-what {{ color: var(--ink-2); font-size: .9rem; }}
.cr:last-child .cr-who {{ color: #c15f3c; }}  /* Claude Code in orange */
.tl-progress {{ display:flex; align-items:center; gap:.8rem; margin: -1rem 0 2.6rem; max-width: 640px; }}
.tl-bar {{ flex:1; height: 4px; border-radius: 999px; background: var(--sunken); overflow:hidden; }}
.tl-bar span {{ display:block; height:100%; background: var(--ink); border-radius: 999px; }}
.tl-progress .lbl {{ font-family: var(--mono); font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color: var(--muted); white-space:nowrap; }}
.tl {{ position: relative; }}
body:has(.st-key-page_project) .block-container {{ max-width: 1560px; }}
.tl-item {{ display: grid; grid-template-columns: 300px minmax(380px, 1fr) minmax(0, 520px); gap: 2.4rem; padding: 0 0 2.4rem 0 !important; }}
.tl-main {{ position: relative; min-width: 0; padding-left: 2.6rem; }}
.tl-main::before {{ content: ""; position: absolute; left: 11px; top: 0; bottom: -2.4rem; width: 1px; background: var(--line); }}
.tl-item:last-child .tl-main::before {{ bottom: 0; }}
.tl::before {{ display: none; }}
.tl-node {{ left: 4px !important; z-index: 1; }}
.tl-hint {{ font-family: var(--mono); font-size: .66rem; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-top: .6rem; }}
.tl-main:hover .tl-hint {{ color: var(--accent); }}
/* left: permanent photo pile */
.tl-photos {{ position: relative; min-height: 0; }}
.tl-photos:not(.none) {{ height: 300px; }}
.tl-photos .ph {{ position: absolute; width: 170px; padding: 6px 6px 16px; background: #fff; border-radius: 6px; cursor: zoom-in;
  box-shadow: 0 1px 2px rgba(9,9,11,.06), 0 8px 24px rgba(9,9,11,.10); transform: rotate(var(--r));
  transition: transform .35s var(--ease-out), box-shadow .35s var(--ease-out); }}
.tl-photos .ph img {{ width: 100%; display: block; border-radius: 2px; }}
.ph-n {{ position: absolute; left: 7px; bottom: 2px; font-family: var(--mono); font-size: .55rem; letter-spacing: .08em; color: var(--muted); }}
.tl-photos .ph:hover {{ transform: rotate(0deg) scale(1.1); z-index: 20 !important; box-shadow: 0 16px 40px rgba(9,9,11,.18); }}
.lb-toggle {{ position: absolute; opacity: 0; pointer-events: none; }}
.lb {{ display: none; position: fixed; inset: 0; z-index: 1000; align-items: center; justify-content: center; }}
.lb-toggle:checked + .ph + .lb {{ display: flex; animation: sectionIn .3s var(--ease-out) backwards; }}
.lb-bg {{ position: absolute; inset: 0; background: rgba(9,9,11,.55); -webkit-backdrop-filter: blur(6px); backdrop-filter: blur(6px); cursor: zoom-out; }}
.lb figure {{ position: relative; margin: 0; max-width: min(1000px, 92vw); background: #fff; border-radius: 14px; padding: 12px;
  box-shadow: 0 30px 80px rgba(9,9,11,.35); }}
.lb figure img {{ display: block; max-width: 100%; max-height: 78vh; border-radius: 6px; }}
.lb figcaption {{ display: flex; justify-content: space-between; align-items: center; padding: .7rem .3rem .2rem;
  font-family: var(--mono); font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; color: var(--ink-2); }}
.lb-close {{ cursor: pointer; color: var(--muted); }}
.lb-close:hover {{ color: var(--accent); }}
/* right: code card, revealed on the first hover of the step, then it stays
   (the "hide" transition has a very long delay, so it never plays back) */
.tl-codecol {{ position: relative; min-width: 0; }}
.tl-code {{ background: #0d0d10; color: #e4e4e7; border-radius: 14px; box-shadow: 0 24px 60px rgba(9,9,11,.22); overflow: hidden;
  opacity: 0; transform: translateX(18px); visibility: hidden;
  transition: opacity .45s var(--ease-out) 99999s, transform .55s var(--ease-out) 99999s, visibility 0s 99999s; }}
.tl-item:hover .tl-code {{ opacity: 1; transform: none; visibility: visible;
  transition: opacity .45s var(--ease-out), transform .55s var(--ease-out), visibility 0s; }}
.tl-code-bar {{ display: flex; align-items: center; gap: 6px; padding: .55rem .8rem; border-bottom: 1px solid rgba(255,255,255,.08); }}
.tl-code-bar span {{ width: 9px; height: 9px; border-radius: 50%; background: #3f3f46; }}
.tl-code-bar span:first-child {{ background: #ef4444; }}
.tl-code-bar span:nth-child(2) {{ background: #eab308; }}
.tl-code-bar span:nth-child(3) {{ background: #22c55e; }}
.tl-code-bar em {{ margin-left: .5rem; font-style: normal; font-family: var(--mono); font-size: .68rem; color: #a1a1aa; }}
a.tl-code {{ display: block; text-decoration: none !important; color: #e4e4e7 !important; cursor: pointer; }}
.tl-code-bar b {{ margin-left: auto; font-weight: 500; font-family: var(--mono); font-size: .64rem; letter-spacing: .08em;
  text-transform: uppercase; color: #71717a; transition: color .2s ease; }}
a.tl-code:hover {{ box-shadow: 0 24px 60px rgba(9,9,11,.22), 0 0 0 1px rgba(147,180,255,.45); }}
a.tl-code:hover .tl-code-bar b {{ color: #93b4ff; }}
.tl-code .tl-pre, .tl-code .tl-pre * {{ font-family: var(--mono) !important; }}
.tl-code .tl-pre {{ margin: 0; padding: .8rem .95rem 1rem; font-size: .62rem; line-height: 1.55; max-height: 380px; overflow: auto;
  color: #e4e4e7; overflow-wrap: anywhere; }}
.tl-code .c {{ color: #71717a; }}
.tl-code .k {{ color: #93b4ff; }}
.tl-code .s {{ color: #86efac; }}
@media (max-width: 1200px) {{ .tl-item {{ grid-template-columns: 1fr; gap: 1rem; }} .tl-photos:not(.none) {{ height: 280px; max-width: 360px; }}
  .tl-photos.none {{ display: none; }} .tl-code {{ display: none; }} .tl-hint {{ display: none; }} }}

.tl-item {{ position: relative; animation: sectionIn .5s var(--ease-out) backwards; }}
.tl-item:nth-child(2) {{ animation-delay: .05s; }} .tl-item:nth-child(3) {{ animation-delay: .1s; }}
.tl-item:nth-child(4) {{ animation-delay: .15s; }} .tl-item:nth-child(5) {{ animation-delay: .2s; }}
.tl-item:nth-child(6) {{ animation-delay: .25s; }} .tl-item:nth-child(7) {{ animation-delay: .3s; }}
.tl-item:nth-child(8) {{ animation-delay: .35s; }} .tl-item:nth-child(9) {{ animation-delay: .4s; }}
.tl-node {{ position:absolute; left: 4px; top: 4px; width: 15px; height: 15px; border-radius: 50%;
  background: var(--page); border: 1.5px solid {AXIS}; box-sizing: border-box; }}
.tl-item.done .tl-node {{ background: #0ca30c; border-color: #0ca30c; }}
.tl-item.progress .tl-node {{ border-color: var(--accent); background: var(--page); box-shadow: 0 0 0 4px rgba(37,99,235,.12); }}
.tl-item.progress .tl-node::after {{ content:""; position:absolute; inset: 3px; border-radius: 50%; background: var(--accent); }}
.tl-head {{ display:flex; align-items: baseline; gap: .7rem; flex-wrap: wrap; }}
.tl-num {{ font-family: var(--mono); font-size: .72rem; letter-spacing: .14em; color: var(--muted); }}
.tl-title {{ font-size: 1.3rem; font-weight: 800; letter-spacing: -0.02em; color: var(--ink); }}
.tl-item.planned .tl-title {{ color: var(--muted); }}
.tl-status {{ font-family: var(--mono); font-size: .64rem; letter-spacing: .12em; text-transform: uppercase;
  padding: .12rem .5rem; border-radius: 999px; border: 1px solid var(--line); color: var(--muted); }}
.tl-item.done .tl-status {{ color: #006300; border-color: rgba(12,163,12,.45); background: rgba(12,163,12,.07); }}
.tl-item.progress .tl-status {{ color: var(--accent-ink); border-color: rgba(37,99,235,.35); background: rgba(37,99,235,.06); }}
.tl-where {{ font-family: var(--mono); font-size: .72rem; color: var(--muted); margin: .3rem 0 .45rem; }}
.tl-summary {{ color: var(--ink-2); margin: 0 0 .5rem; max-width: 640px; }}
.tl-points {{ margin: 0; padding-left: 1rem; max-width: 640px; }}
.tl-points li {{ color: var(--ink-2); font-size: .88rem; margin: .1rem 0; line-height: 1.45; }}
.tl-points li::marker {{ color: {AXIS}; }}

/* Top of page 00: intro + credits on the left, compact author card on the right */
.p-top {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 600px); gap: 2.4rem; align-items: start; margin-bottom: 2.6rem; }}
@media (max-width: 1000px) {{ .p-top {{ grid-template-columns: 1fr; }} }}
.p-top .tl-progress {{ margin: .4rem 0 0; }}
.p-top .credits {{ margin-bottom: 1.6rem; }}
.p-top .pc.pc-h {{ grid-template-columns: 74px minmax(0, 1fr) auto; gap: .4rem 1.1rem; padding: 1rem 1.1rem; margin: 0; align-items: start; }}
.p-top .pc.pc-h .pc-photo {{ width: 74px; height: 74px; padding: 4px; box-shadow: 0 0 0 5px var(--surface), 0 0 0 6px rgba(37,99,235,.08); }}
.p-top .pc-name {{ font-size: 1.1rem; }}
.p-top .pc-handle {{ font-size: .68rem; margin: .1rem 0 .4rem; }}
.p-top .pc-bio {{ font-size: .8rem; line-height: 1.45; margin: 0 0 .5rem; }}
.p-top .pc-status {{ font-size: .6rem; padding: .2rem .55rem; }}
.p-top .pc.pc-h .pc-links {{ flex-direction: column; justify-content: center; gap: .35rem; align-self: stretch;
  border-top: none; border-left: 1px solid var(--line); padding: 0 0 0 1rem; margin: 0; }}
.p-top .pc-link {{ border-bottom: none; padding: .2rem 0; font-size: .66rem; gap: .35rem; justify-content: flex-start; }}

/* Author card (page 00), horizontal, under the credits */
.pc.pc-h {{ display: grid; grid-template-columns: auto 1fr 220px; gap: 1.6rem; align-items: center; max-width: 980px;
  padding: 1.2rem 1.4rem; margin: 0 0 2.4rem; }}
.pc.pc-h .pc-photo {{ margin: 0; }}
.pc.pc-h .pc-handle {{ margin: .2rem 0 .5rem; }}
.pc.pc-h .pc-bio {{ margin: 0 0 .6rem; }}
.pc.pc-h .pc-status {{ margin: 0; }}
.pc.pc-h .pc-links {{ border-top: none; border-left: 1px solid var(--line); padding-left: 1.2rem; align-self: stretch;
  display: flex; flex-direction: column; justify-content: center; }}
@media (max-width: 820px) {{ .pc.pc-h {{ grid-template-columns: 1fr; }} .pc.pc-h .pc-links {{ border-left: none; padding-left: 0; border-top: 1px solid var(--line); }} }}
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

/* Clickable asset rows in the portfolio panel (an invisible button covers each row) */
[class*="st-key-assetrow_"] {{ position: relative; }}
[class*="st-key-assetrow_"] .row {{ border-radius: 12px; padding: .45rem .55rem; margin: 0 -.55rem;
  transition: background .2s ease, box-shadow .2s ease; }}
[class*="st-key-assetrow_"]:hover .row {{ background: var(--sunken); }}
[class*="st-key-assetrow_on"] .row {{ background: rgba(37,99,235,.07); box-shadow: inset 0 0 0 1px rgba(37,99,235,.28); }}
[class*="st-key-assetrow_"] [data-testid="stElementContainer"]:has(button) {{ position: absolute; inset: 0; z-index: 2; margin: 0; }}
[class*="st-key-assetrow_"] .stButton, [class*="st-key-assetrow_"] .stButton button {{ width: 100%; height: 100%; }}
[class*="st-key-assetrow_"] .stButton button {{ opacity: 0; cursor: pointer; border: none; }}
[class*="st-key-assetrow_"]:has(button:focus-visible) {{ outline: 2px solid var(--accent); outline-offset: 2px; }}

/* Five key figures on one row in the asset detail */
.cards.five {{ grid-template-columns: repeat(5, minmax(0, 1fr)); }}
.cards.five .v {{ font-size: clamp(1.2rem, 1.8vw, 1.75rem); }}
.cards.five {{ margin-top: 1rem; gap: .6rem; }}
.cards.five .card {{ padding: .9rem .85rem; min-width: 0; }}
.cards.five .top {{ font-size: .58rem; letter-spacing: .06em; gap: .4rem; overflow: hidden; }}
.cards.five .top > span:last-child, .cards.five .top {{ text-overflow: ellipsis; }}
.cards.five .ic {{ flex-basis: 22px; width: 22px; height: 22px; }}
.cards.five .v {{ margin: .65rem 0 .3rem; }}
.cards.five .a {{ white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500; font-size: .78rem; color: var(--ink-2); }}
@media (max-width: 980px) {{ .cards.five {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}

/* Asset detail header */
.ad-head {{ display:flex; align-items:center; gap:.9rem; }}
.ad-head .avatar {{ flex-basis: 48px; height: 48px; font-size: .85rem; }}
.ad-name {{ font-size: 1.7rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; color: var(--ink); }}
.ad-sub {{ font-family: var(--mono); font-size: .72rem; letter-spacing: .08em; color: var(--muted); margin-top: .2rem; }}

/* Toast (nudge towards 00 Project), in the house style */
[data-testid="stToast"] {{ background: rgba(255,255,255,.92) !important; -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
  border: 1px solid rgba(37,99,235,.25) !important; border-radius: 14px !important; box-shadow: 0 16px 40px rgba(9,9,11,.12) !important; }}
[data-testid="stToast"] p {{ font-size: .85rem !important; color: var(--ink) !important; }}
[data-testid="stToast"] [data-testid="stToastDynamicIcon"], [data-testid="stToast"] [data-testid="stToastDynamicIcon"] * {{ color: var(--accent) !important; }}

/* Floating invitation to the project page */
@keyframes nudgeIn {{ from {{ opacity: 0; transform: translateY(16px) scale(.98); }} to {{ opacity: 1; transform: none; }} }}
.st-key-nudge {{ position: fixed !important; right: 1.4rem; bottom: 1.4rem; z-index: 999; width: 330px !important;
  background: rgba(255,255,255,.94); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px);
  border: 1px solid rgba(37,99,235,.22); border-radius: 18px; padding: 1rem 1rem .7rem;
  box-shadow: 0 20px 50px rgba(9,9,11,.16); animation: nudgeIn .6s var(--ease-out) 1.2s backwards; gap: .6rem !important; }}
.nd {{ display: flex; gap: .8rem; align-items: flex-start; padding-bottom: .4rem; }}
.nd img {{ width: 42px; height: 42px; border-radius: 50%; object-fit: cover; flex: 0 0 42px;
  box-shadow: 0 0 0 3px #fff, 0 0 0 4px rgba(37,99,235,.25); }}
.nd b {{ display: block; font-size: .95rem; font-weight: 800; letter-spacing: -0.01em; color: var(--ink); margin-bottom: .15rem; }}
.nd p {{ margin: 0; font-size: .82rem; line-height: 1.45; color: var(--ink-2); }}
.st-key-nudge .stButton button {{ font-size: .8rem !important; padding: .35rem .8rem !important; min-height: 0 !important; }}
@media (max-width: 640px) {{ .st-key-nudge {{ left: .8rem; right: .8rem; width: auto !important; }} }}

/* Page transitions: the new screen slides in from the side it comes from */
@keyframes slideFromRight {{ from {{ opacity: 0; transform: translateX(48px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes slideFromLeft  {{ from {{ opacity: 0; transform: translateX(-48px); }} to {{ opacity: 1; transform: none; }} }}
.st-key-page_report {{ animation: slideFromRight .5s var(--ease-out) backwards; }}
.st-key-page_build  {{ animation: slideFromLeft .5s var(--ease-out) backwards; }}
.stApp {{ overflow-x: clip; }}

/* App bar (clickable navigation = a segmented control styled as mono tabs) */
.st-key-nav {{ display:flex; justify-content:center; transform: translateY(8px); }}
[data-testid="stHorizontalBlock"]:has(.st-key-nav) {{ margin-bottom: 2.2rem; }}
.st-key-nav [data-testid="stButtonGroup"] {{ justify-content:center; }}
.st-key-nav [data-testid="stButtonGroup"] > div {{ column-gap: .5rem !important; }}
.st-key-nav button {{ margin: 0 !important; }}
.st-key-nav button {{ font-family: var(--mono) !important; font-size:.72rem !important; letter-spacing:.14em; text-transform:uppercase;
  background: transparent !important; border: 1px solid transparent !important; border-radius: 999px !important;
  color: var(--muted) !important; padding: .35rem .9rem !important; box-shadow:none !important; cursor:pointer; }}
.st-key-nav button p {{ font-family: var(--mono) !important; font-size:.72rem !important; }}
.st-key-nav button:hover {{ color: var(--ink) !important; }}
.st-key-nav button[aria-checked="true"] {{ background: var(--surface) !important; color: var(--ink) !important; border-color: var(--line) !important; }}
/* "00 Project" blinks softly while another page is open, to invite a visit */
/* "00 Project" stands out while another page is open: a tinted accent pill,
   a "live" dot that sends out a ring, and a soft halo. Solid accent on hover. */
@keyframes navPing {{ 0% {{ box-shadow: 0 0 0 0 rgba(37,99,235,.55); }} 70%, 100% {{ box-shadow: 0 0 0 7px rgba(37,99,235,0); }} }}
@keyframes navHalo {{ 0%, 100% {{ opacity: 0; transform: scale(.96); }} 50% {{ opacity: 1; transform: scale(1); }} }}
.st-key-nav button:first-of-type[aria-checked="false"] {{ position: relative; color: var(--accent-ink) !important;
  background: rgba(37,99,235,.07) !important; border-color: rgba(37,99,235,.32) !important; }}
.st-key-nav button:first-of-type[aria-checked="false"]::before {{ content: ""; width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent); margin-right: .5rem; display: inline-block; animation: navPing 1.8s ease-out infinite; }}
.st-key-nav button:first-of-type[aria-checked="false"]::after {{ content: ""; position: absolute; inset: -4px; border-radius: 999px;
  border: 1px solid rgba(37,99,235,.18); pointer-events: none; animation: navHalo 2.4s ease-in-out infinite; }}
.st-key-nav button:first-of-type[aria-checked="false"]:hover {{ background: var(--accent) !important; border-color: var(--accent) !important;
  color: #fff !important; }}
.st-key-nav button:first-of-type[aria-checked="false"]:hover::before {{ background: #fff; animation: none; }}
.st-key-nav button:first-of-type[aria-checked="false"]:hover::after {{ animation: none; opacity: 0; }}
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
.cards {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap:.8rem; margin-bottom: 1.6rem; }}
@media (max-width: 980px) {{ .cards {{ grid-template-columns: repeat(2, minmax(0,1fr)); }} }}
.card {{ background: var(--surface); border:1px solid var(--line); border-radius: 16px; padding: 1.05rem 1.1rem;
  transition: transform .35s var(--ease-out), border-color .2s ease; }}
.card:hover {{ transform: translateY(-2px); border-color: {AXIS}; }}
.card .top {{ display:flex; align-items:center; gap:.5rem; white-space:nowrap; font-family: var(--mono); font-size:.64rem; letter-spacing:.1em; text-transform:uppercase; color: var(--muted); }}
.card .ic {{ flex: 0 0 26px; width:26px; height:26px; border-radius:50%; background: var(--sunken); color: var(--ink);
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


def timeline_head(intro, credits, steps):
    """Headline, who did what, and the progress bar."""
    done = sum(st["status"] == "done" for st in steps)
    progress = sum(st["status"] == "progress" for st in steps)
    pct = round((done + 0.5 * progress) / len(steps) * 100)
    rows = "".join(f'<div class="cr"><span class="cr-role">{esc(r)}</span><span class="cr-who">{esc(w)}</span>'
                   f'<span class="cr-what">{esc(x)}</span></div>' for r, w, x in credits)
    return (f'<p class="tl-intro">{esc(intro)}</p><div class="credits">{rows}</div>'
            f'<div class="tl-progress"><div class="tl-bar"><span style="width:{pct}%"></span></div>'
            f'<span class="lbl">{pct}% complete</span></div>')


_PHOTO_SPOTS = [(-5, 0, 6), (4, 120, 0), (-2, 36, 92), (6, 168, 84), (-7, 8, 178), (3, 132, 168)]


def _highlight(code):
    """Tiny highlighter: comments, strings and a few keywords (input is escaped first)."""
    out = []
    for line in esc(code).split("\n"):
        if line.lstrip().startswith("#"):
            out.append(f'<span class="c">{line}</span>')
            continue
        line = re.sub(r"(&quot;[^&]*?&quot;|&#x27;[^&]*?&#x27;)", r'<span class="s">\1</span>', line)
        line = re.sub(r"\b(def|for|in|return|import|from)\b", r'<span class="k">\1</span>', line)
        out.append(line)
    # Streamlit's markdown drops newlines and leading spaces: keep them explicitly
    return "<br>".join(re.sub(r"^( +)", lambda m: "&nbsp;" * len(m.group(1)), line) for line in out)


def timeline_steps(steps, static_url="app/static/notebooks",
                   repo_url="https://github.com/elouennael19-dev/portfolio-diversification"):
    """Vertical timeline. On the right: a pile of notebook screenshots (click to enlarge)
    and, while the step text is hovered, a card with the notebook code."""
    labels = {"done": "Done", "progress": "In progress", "planned": "Planned"}
    items = []
    for step in steps:
        points = "".join(f"<li>{esc(p)}</li>" for p in step["points"])
        main = (f'<div class="tl-main"><span class="tl-node"></span>'
                f'<div class="tl-head"><span class="tl-num">{esc(step["num"])}</span>'
                f'<span class="tl-title">{esc(step["title"])}</span>'
                f'<span class="tl-status">{labels[step["status"]]}</span></div>'
                + (f'<div class="tl-where">{esc(step["where"])}</div>' if step["where"] else '<div class="tl-where"></div>')
                + f'<p class="tl-summary">{esc(step["summary"])}</p>'
                + (f'<ul class="tl-points">{points}</ul>' if points else "")
                + ('<div class="tl-hint">‹/› hover to reveal the code →</div>' if step.get("code") else "")
                + "</div>")
        photos = ""
        for i, (file, caption) in enumerate(step.get("images", [])):
            rot, left, top = _PHOTO_SPOTS[i % len(_PHOTO_SPOTS)]
            uid = f'lb-{step["num"]}-{i}'
            src = f"{static_url}/{file}"
            photos += (f'<input type="checkbox" id="{uid}" class="lb-toggle">'
                       f'<label for="{uid}" class="ph" style="--r:{rot}deg; left:{left}px; top:{top}px; z-index:{i + 1}" '
                       f'title="{esc(caption)}"><img src="{src}" alt="{esc(caption)}"><span class="ph-n">{i + 1:02d}</span></label>'
                       f'<div class="lb"><label for="{uid}" class="lb-bg"></label>'
                       f'<figure><img src="{src}" alt="{esc(caption)}"><figcaption>{i + 1:02d} · {esc(caption)}'
                       f'<label for="{uid}" class="lb-close">Close ✕</label></figcaption></figure></div>')
        side = ""
        if photos or step.get("code"):
            side = '<div class="tl-side">'
            if photos:
                side += f'<div class="tl-photos">{photos}</div>'
            if step.get("code"):
                side += (f'<div class="tl-code"><div class="tl-code-bar"><span></span><span></span><span></span>'
                         f'<em>{esc(step["where"])}</em></div><div class="tl-pre">{_highlight(step["code"])}</div></div>')
            side += "</div>"
        left = f'<div class="tl-photos">{photos}</div>' if photos else '<div class="tl-photos none"></div>'
        url = f"{repo_url}/blob/main/notebooks/{step['where']}" if step["where"].endswith(".ipynb") else repo_url
        code = (f'<a class="tl-code" href="{esc(url)}" target="_blank" rel="noopener" title="Open the notebook on GitHub">'
                f'<div class="tl-code-bar"><span></span><span></span><span></span>'
                f'<em>{esc(step["where"])}</em><b>Open on GitHub ↗</b></div>'
                f'<div class="tl-pre">{_highlight(step["code"])}</div></a>'
                if step.get("code") else "")
        items.append(f'<div class="tl-item {step["status"]}">{left}{main}<div class="tl-codecol">{code}</div></div>')
    return f'<div class="tl">{"".join(items)}</div>'


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
    return (f'<div class="pc pc-h"><div class="pc-photo">{img}</div><div class="pc-body">'
            f'<div class="pc-name">{esc(name)}</div><div class="pc-handle">{who}</div>'
            f'<p class="pc-bio">{esc(bio)}</p>'
            + (f'<div class="pc-status"><span class="dot"></span>{esc(status)}</div>' if status else "")
            + f'</div><div class="pc-links">{rows}</div></div>')


def nudge(photo_path, title, text):
    photo = Path(__file__).resolve().parent / photo_path
    img = (f'<img src="data:image/jpeg;base64,{base64.b64encode(photo.read_bytes()).decode()}" alt="">'
           if photo.exists() else "")
    return f'<div class="nd">{img}<div><b>{esc(title)}</b><p>{esc(text)}</p></div></div>'


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


def asset_header(name, ticker, quoted_in, base_currency, period):
    conv = f"quoted in {quoted_in}, shown in {base_currency}" if quoted_in and quoted_in != base_currency else f"in {base_currency}"
    return (f'<div class="ad-head"><div class="avatar">{esc(initials(name, ticker))}</div>'
            f'<div><div class="ad-name">{esc(name)}</div>'
            f'<div class="ad-sub">{esc(ticker)} · {esc(conv)} · {esc(period)}</div></div></div>')


def cards(items, extra_class=""):
    """items: list of (icon, label, value, asset, detail)."""
    out = "".join(
        f'<div class="card"><div class="top"><span class="ic">{icon(ic)}</span>{esc(label)}</div>'
        f'<div class="v">{esc(value)}</div><div class="a" title="{esc(asset)}">{esc(asset)}</div>'
        f'<div class="d">{esc(detail)}</div></div>'
        for ic, label, value, asset, detail in items
    )
    return f'<div class="cards {extra_class}">{out}</div>'

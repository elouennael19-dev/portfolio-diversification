"""Altair charts for the Streamlit interface."""

import altair as alt
import pandas as pd

from style import (ACCENT, AXIS, CONTEXT_LINE, FONT, GRID, INK, INK_2, MONO, MUTED, NEGATIVE,
                   POSITIVE, SERIES, SURFACE)



def _escape(field):
    """Altair reads '.' and brackets in field names as nested access."""
    return field.replace("\\", "\\\\").replace(".", "\\.").replace("[", "\\[").replace("]", "\\]")


def _rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _fade(color, top=0.22, bottom=0.0):
    """Vertical gradient of one colour (alpha `top` at the top, `bottom` at the bottom)."""
    return alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0,
                        stops=[alt.GradientStop(color=_rgba(color, bottom), offset=0),
                               alt.GradientStop(color=_rgba(color, top), offset=1)])


def styled(chart, height=None, pad_right=16):
    """Shared look: recessive hairline grid and axes, Fira Sans for text, Fira Code for ticks."""
    if height is not None:
        chart = chart.properties(height=height)
    return (
        chart.properties(background="transparent", padding={"left": 8, "right": pad_right, "top": 12, "bottom": 8})
        .configure_view(stroke=None)
        .configure_axis(
            gridColor=GRID, gridWidth=1, domainColor=AXIS, tickColor=AXIS, tickSize=4,
            labelColor=MUTED, titleColor=INK_2, labelFont=MONO, titleFont=FONT,
            labelFontSize=10, titleFontSize=11, titleFontWeight="normal", labelPadding=6,
        )
        .configure_legend(labelFont=FONT, titleFont=MONO, labelColor=INK_2, titleColor=MUTED,
                          titleFontSize=10, titleFontWeight="normal", orient="bottom",
                          symbolType="stroke", symbolStrokeWidth=2.5, symbolSize=180)
        .configure_header(labelFont=FONT, labelColor=INK, labelFontSize=12, labelFontWeight=600,
                          labelAnchor="start", title=None)
        .configure_text(font=FONT)
    )


def to_long(df, value_name):
    return df.reset_index(names="Date").melt("Date", var_name="Asset", value_name=value_name)


def _year_axis(start, end):
    return alt.Axis(format="%Y", values=[pd.Timestamp(year=y, month=1, day=1).isoformat()
                                         for y in range(start.year + 1, end.year + 1)])


def _focus_layers(data, x_scale, value_name, y_format, highlighted, color_by_asset, baseline, end_text,
                  below=False):
    """Coloured lines with a soft gradient towards the baseline, line styles, end markers,
    end labels and a crosshair tooltip, for the highlighted assets."""
    domain = list(highlighted)
    color = alt.Color("Asset:N", scale=alt.Scale(domain=domain, range=[color_by_asset[a] for a in domain]),
                      legend=alt.Legend(title=None))
    focus = alt.Chart(data).transform_filter(alt.FieldOneOfPredicate(field="Asset", oneOf=domain))
    x = alt.X("Date:T", scale=x_scale)
    layers = []
    for asset in domain:  # one gradient per asset, from the line to the baseline
        layers.append(
            alt.Chart(data[data["Asset"] == asset]).mark_area(
                color=_fade(color_by_asset[asset], *((0.0, 0.2) if below else (0.2, 0.0))), line=False)
            .encode(x=x, y=f"{value_name}:Q", y2=alt.datum(baseline))
        )
    lines = focus.mark_line(strokeWidth=2).encode(x=x, y=f"{value_name}:Q", color=color)
    last = data[data["Asset"].isin(domain)].groupby("Asset").tail(1).copy()
    last["end"] = [end_text(a, v) for a, v in zip(last["Asset"], last[value_name])]
    end_points = alt.Chart(last).mark_circle(size=70, stroke=SURFACE, strokeWidth=2, opacity=1).encode(
        x=x, y=f"{value_name}:Q", color=color)
    end_labels = alt.Chart(last).mark_text(align="left", dx=9, fontSize=11, fontWeight=600, color=INK).encode(
        x=x, y=f"{value_name}:Q", text="end:N")

    hover = alt.selection_point(nearest=True, on="pointerover", fields=["Date"], empty=False, clear="pointerout")
    rule = focus.transform_pivot("Asset", value=value_name, groupby=["Date"]).mark_rule(
        color=INK, strokeWidth=1, opacity=0.25).encode(
        x=x, opacity=alt.condition(hover, alt.value(0.35), alt.value(0)),
        tooltip=[alt.Tooltip("Date:T", format="%d %b %Y")]
        + [alt.Tooltip(f"{_escape(a)}:Q", title=a, format=y_format) for a in domain],
    ).add_params(hover)
    dots = focus.mark_circle(size=55, stroke=SURFACE, strokeWidth=2, opacity=1).encode(
        x=x, y=f"{value_name}:Q", color=color, opacity=alt.condition(hover, alt.value(1), alt.value(0)))
    return layers + [lines, rule, dots, end_points, end_labels]


def comparison_lines(df, highlighted, color_by_asset):
    """Growth of 100: every asset in light grey for context, highlighted ones in colour."""
    value_name = "Growth of 100"
    data = to_long(df, value_name)
    start, end = df.index.min(), df.index.max()
    x_scale = alt.Scale(domain=[start.isoformat(), (end + (end - start) * 0.2).isoformat()])
    y_scale = alt.Scale(zero=False)
    y = alt.Y(f"{value_name}:Q", title=None, scale=y_scale, axis=alt.Axis(format=",.0f", tickCount=6))

    baseline = alt.Chart(pd.DataFrame({"y": [100]})).mark_rule(color=AXIS, strokeWidth=1).encode(y=alt.Y("y:Q", scale=y_scale))
    context = alt.Chart(data).transform_filter(~alt.FieldOneOfPredicate(field="Asset", oneOf=list(highlighted))).mark_line(
        strokeWidth=1, color=CONTEXT_LINE).encode(
        x=alt.X("Date:T", title=None, scale=x_scale, axis=_year_axis(start, end)), y=y, detail="Asset:N",
        tooltip=[alt.Tooltip("Asset:N"), alt.Tooltip("Date:T", format="%d %b %Y"),
                 alt.Tooltip(f"{value_name}:Q", format=",.0f")])
    layers = [baseline, context]
    if highlighted:
        layers += _focus_layers(data, x_scale, value_name, ",.0f", highlighted, color_by_asset, 100,
                                lambda a, v: f"{a}  ×{v / 100:.1f}")
    return alt.layer(*layers).resolve_scale(y="shared")


def underwater(drawdown_df, highlighted, color_by_asset):
    """Drawdown 'under water': how far each asset sits below its previous peak."""
    value_name = "Drawdown"
    data = to_long(drawdown_df, value_name)
    start, end = drawdown_df.index.min(), drawdown_df.index.max()
    x_scale = alt.Scale(domain=[start.isoformat(), (end + (end - start) * 0.2).isoformat()])
    y = alt.Y(f"{value_name}:Q", title=None, axis=alt.Axis(format=".0%", tickCount=5))
    surface = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=INK_2, strokeWidth=1).encode(y="y:Q")
    context = alt.Chart(data).transform_filter(~alt.FieldOneOfPredicate(field="Asset", oneOf=list(highlighted))).mark_line(
        strokeWidth=1, color=CONTEXT_LINE).encode(
        x=alt.X("Date:T", title=None, scale=x_scale, axis=_year_axis(start, end)), y=y, detail="Asset:N")
    layers = [context, surface]
    if highlighted:
        layers += _focus_layers(data, x_scale, value_name, ".1%", highlighted, color_by_asset, 0,
                                lambda a, v: f"{a}  {v:.0%}", below=True)
    return alt.layer(*layers)


def small_multiples(df, value_name, y_format, columns=3, independent_y=False):
    """One small chart per asset, one colour, soft gradient under the line."""
    data = to_long(df, value_name)
    base = alt.Chart(data).encode(
        x=alt.X("Date:T", title=None, axis=alt.Axis(format="%Y", tickCount="year", labelOverlap=True)),
        y=alt.Y(f"{value_name}:Q", title=None, scale=alt.Scale(zero=False), axis=alt.Axis(format=y_format, tickCount=3)),
        tooltip=[alt.Tooltip("Asset:N"), alt.Tooltip("Date:T", format="%d %b %Y"),
                 alt.Tooltip(f"{value_name}:Q", format=y_format)],
    )
    chart = alt.layer(
        base.mark_area(color=_fade(SERIES[0], 0.18), line={"color": SERIES[0], "strokeWidth": 1.5}),
    ).properties(width=250, height=110)
    return chart.facet(facet=alt.Facet("Asset:N", title=None, sort=list(df.columns)), columns=columns).resolve_axis(
        x="independent").resolve_scale(y="independent" if independent_y else "shared")


def small_chart(df, value_name, y_format):
    """Small single-asset chart with a soft gradient, titled with the asset name."""
    asset = df.columns[0]
    data = to_long(df, value_name)
    return alt.Chart(data, title=alt.TitleParams(asset, anchor="start", font=FONT, fontSize=12, fontWeight=600,
                                                 color=INK, offset=8)).mark_area(
        color=_fade(SERIES[0], 0.18), line={"color": SERIES[0], "strokeWidth": 1.5}).encode(
        x=alt.X("Date:T", title=None, axis=alt.Axis(format="%Y", tickCount="year", labelOverlap=True)),
        y=alt.Y(f"{value_name}:Q", title=None, scale=alt.Scale(zero=False), axis=alt.Axis(format=y_format, tickCount=3)),
        tooltip=[alt.Tooltip("Date:T", format="%d %b %Y"), alt.Tooltip(f"{value_name}:Q", format=y_format)],
    )


def return_risk_scatter(summary):
    """Annual return vs annual volatility, one point per asset (as in notebook 02)."""
    data = summary.reset_index(names="Asset")
    xv, yv = data["Annual volatility (%)"], data["Annual return (%)"]
    x_lo, x_hi = max(0, xv.min() - 4), xv.max() + (xv.max() - xv.min()) * 0.38 + 2
    y_lo, y_hi = min(0, yv.min()) - 4, yv.max() + 5
    x_scale = alt.Scale(domain=[x_lo, x_hi], nice=False)
    y_scale = alt.Scale(domain=[y_lo, y_hi], nice=False)
    x = alt.X("Annual volatility (%):Q", title="Annual volatility (%)", scale=x_scale, axis=alt.Axis(tickCount=8))
    y = alt.Y("Annual return (%):Q", title="Annual return (%)", scale=y_scale)
    zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=AXIS).encode(y=alt.Y("y:Q", scale=y_scale))
    points = alt.Chart(data).mark_circle(size=120, color=SERIES[0], opacity=1, stroke=SURFACE, strokeWidth=2).encode(
        x=x, y=y,
        tooltip=["Asset", alt.Tooltip("Annual return (%):Q", format=".1f"),
                 alt.Tooltip("Annual volatility (%):Q", format=".1f"),
                 alt.Tooltip("Return / risk ratio:Q", format=".2f"),
                 alt.Tooltip("Max drawdown (%):Q", format=".1f")])
    labels = alt.Chart(_label_positions(data, (x_lo, x_hi))).mark_text(
        align="left", dx=0, fontSize=11, fontWeight=500, color=INK).encode(
        x=alt.X("label_x:Q", scale=x_scale), y=alt.Y("label_y:Q", scale=y_scale), text="Asset:N")
    return alt.layer(zero, points, labels)


def _label_positions(data, x_domain, x="Annual volatility (%)", y="Annual return (%)",
                     plot_width=640, plot_height=380):
    """Place each label to the right of its bubble, nudged up or down by a line when it
    would overlap another label or bubble (simple greedy layout)."""
    data = data.sort_values(y, ascending=False).copy()
    y_span = (data[y].max() - min(0, data[y].min()) + 9) or 1
    x_per_px = (x_domain[1] - x_domain[0]) / plot_width
    line = y_span / plot_height * 14
    char = x_per_px * 6.4
    radius_px = pd.Series(7.0, index=data.index)  # points of size 120 -> radius about 6 px
    boxes = [(r[x] - rp * x_per_px, r[x] + rp * x_per_px, r[y]) for (_, r), rp in zip(data.iterrows(), radius_px)]
    label_x, label_y = [], []
    for (_, row), rp in zip(data.iterrows(), radius_px):
        x0 = row[x] + (rp + 6) * x_per_px
        x1 = x0 + len(str(row["Asset"])) * char
        for step in (0, -1, 1, -2, 2, -3, 3):
            cy = row[y] + step * line
            if not any(x0 < bx1 and bx0 < x1 and abs(cy - by) < line for bx0, bx1, by in boxes):
                break
        boxes.append((x0, x1, cy))
        label_x.append(x0)
        label_y.append(cy)
    data["label_x"], data["label_y"] = label_x, label_y
    return data


def lollipops(summary, column, value_format, signed=False):
    """Ranked 'lollipops': a thin stem from zero and a dot with its value at the end."""
    data = summary[[column]].reset_index(names="Asset").sort_values(column, ascending=False)
    data["label"] = data[column].map(lambda v: format(v, value_format))
    field = _escape(column)
    color = (alt.condition(alt.datum[column] >= 0, alt.value(POSITIVE), alt.value(NEGATIVE))
             if signed else alt.value(SERIES[0]))
    lo, hi = min(0, data[column].min()), max(0, data[column].max())
    pad = (hi - lo) * 0.2 or 1
    x_scale = alt.Scale(domain=[lo - (pad if lo < 0 else 0), hi + pad], nice=False)
    y = alt.Y("Asset:N", sort=None, title=None,
              axis=alt.Axis(labelLimit=220, domain=False, ticks=False, labelColor=INK_2, labelFont=FONT, labelFontSize=11))
    base = alt.Chart(data).encode(y=y)
    stem = base.mark_rule(strokeWidth=2).encode(x=alt.X("zero:Q", scale=x_scale), x2=f"{field}:Q", color=color).transform_calculate(zero="0")
    dot = base.mark_circle(size=130, opacity=1, stroke=SURFACE, strokeWidth=2).encode(
        x=alt.X(f"{field}:Q", title=None, scale=x_scale, axis=alt.Axis(format=value_format, tickCount=5, grid=True)),
        color=color, tooltip=["Asset", alt.Tooltip(f"{field}:Q", title=column, format=value_format)])
    text_pos = base.transform_filter(alt.datum[column] >= 0).mark_text(align="left", dx=10, font=MONO, fontSize=10, color=INK_2).encode(
        x=alt.X(f"{field}:Q", scale=x_scale), text="label:N")
    text_neg = base.transform_filter(alt.datum[column] < 0).mark_text(align="right", dx=-10, font=MONO, fontSize=10, color=INK_2).encode(
        x=alt.X(f"{field}:Q", scale=x_scale), text="label:N")
    zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=AXIS).encode(x=alt.X("x:Q", scale=x_scale))
    return alt.layer(zero, stem, dot, text_pos, text_neg).properties(height=max(200, 36 * len(data)))

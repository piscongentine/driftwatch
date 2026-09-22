"""The dashboard: accessible colours, a real page skeleton, and the JSON contract with the Python side.

Reads : web/*, the `project` fixture.  Writes: nothing.
"""
import re

import config

WEB = config.ROOT / "web"


def theme(block_start):
    css = (WEB / "tokens.css").read_text()
    body = css.split(block_start, 1)[1].split("\n}", 1)[0]
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", body))


def luminance(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


PAIRS = [("text", "bg"), ("text", "surface"), ("text-2", "surface"), ("muted", "bg"), ("muted", "surface"), ("muted", "surface-2"),
         ("accent", "surface"), ("accent", "accent-soft"), ("on-accent", "accent"),
         ("ok", "ok-soft"), ("warn", "warn-soft"), ("alert", "alert-soft"), ("ok", "surface"), ("warn", "surface"), ("alert", "surface")]


def test_colours_pass_wcag_aa_in_both_themes():
    for name, block in (("light", ":root {"), ("dark", ':root[data-theme="dark"] {')):
        t = theme(block)
        for fg, bg in PAIRS:
            assert ratio(t[fg], t[bg]) >= 4.5, (name, fg, bg, round(ratio(t[fg], t[bg]), 2))


def test_dark_theme_is_defined_for_the_system_setting_and_for_the_toggle():
    css = (WEB / "tokens.css").read_text()
    assert "prefers-color-scheme: dark" in css and ':root[data-theme="dark"]' in css
    assert theme(':root[data-theme="dark"] {') == theme("@media (prefers-color-scheme: dark) {\n  :root:not([data-theme=\"light\"]) {")


def test_page_has_the_basics():
    html = (WEB / "index.html").read_text()
    assert '<html lang="en">' in html and "viewport" in html and 'href="#main"' in html
    for src in re.findall(r'<script src="([^"]+)"', html):
        assert (WEB / src).exists(), src
    assert "prefers-reduced-motion" in (WEB / "style.css").read_text()


def test_json_has_everything_the_page_reads(project):
    s = project.json("summary.json")
    assert {"generated_at", "versions", "reference_rows", "model", "columns", "batches", "detection", "freshness"} <= set(s)
    assert {"name", "method", "limit", "constant"} <= set(s["columns"][0])
    ok = [b for b in s["batches"] if b["status"] == "ok"][0]
    assert {"index", "rows", "share", "columns", "gate", "timestamp"} <= set(ok)
    assert {"p", "level", "drifted"} <= set(ok["columns"]["temperature"])
    assert {"accuracy", "baseline_accuracy", "precision", "recall", "auc"} <= set(s["model"])
    a = project.json("alerts.json")
    assert {"limits", "counts", "alerts"} <= set(a) and {"level", "rule", "title", "detail", "batch"} <= set(a["alerts"][0])

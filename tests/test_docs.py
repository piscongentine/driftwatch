"""The written explanations agree with the tracker, with each other, and with the files they point at.

Reads : README.md, ABOUT.md, CONTRIBUTING.md, web/about.html, sprint/*.md, issues/README.md.  Writes: nothing.
"""
import re
import sys

import config

sys.path.insert(0, str(config.ISSUES_DIR))
import check_all  # noqa: E402

ROOT = config.ROOT
NUMBERS = sorted(str(n) for n in check_all.tracker())
DOCS = ["README.md", "ABOUT.md", "CONTRIBUTING.md", "sprint/SPRINT.md", "sprint/ISSUES.md", "issues/README.md"]
HEADING = "### What each Lab result means, and how it can be fixed"


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def slug(title):
    """GitHub's rule for heading anchors: lower case, drop punctuation, spaces become hyphens."""
    return re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")


def test_readme_explains_every_issue_in_five_cells():
    rows = [line for line in read("README.md").split(HEADING, 1)[1].split("\n## ", 1)[0].splitlines() if line.startswith("| [#")]
    assert sorted(re.match(r"\| \[#(\d+)\]", r).group(1) for r in rows) == NUMBERS
    for row in rows:
        cells = [c.strip() for c in row.strip("| ").split(" | ")]
        assert len(cells) == 5 and all(cells), row[:60]   # issue, reason, what it means, trouble, how to solve it


def test_about_page_and_about_md_explain_every_issue_in_short():
    for name, parts in (("web/about.html", r"<b>Why:</b>.*?<b>Means:</b>.*?<b>Trouble:</b>.*?<b>Fix:</b>"), ("ABOUT.md", r"Why:.*?Means:.*?Trouble:.*?Fix:")):
        text = read(name)
        assert len(re.findall(parts, text)) == len(NUMBERS), name
        for n in NUMBERS:
            assert text.count(f"/issues/{n}") == 1, (name, n)


def test_links_to_files_and_headings_are_not_broken():
    readme = read("README.md")
    anchors = {slug(h) for h in re.findall(r"^#{1,6} (.+)$", readme, flags=re.M)}
    assert slug(HEADING.lstrip("# ")) in anchors
    for target in re.findall(r"\]\(#([\w-]+)\)", readme) + re.findall(r"README\.md#([\w-]+)", read("ABOUT.md")):
        assert target in anchors, target
    for name in DOCS:
        for target in re.findall(r'(?:\]\(|src="|href=")([^)"#\s]+)', read(name)):
            if not re.match(r"[a-z]+:", target) and target != "url":   # "url" is the tracker's own format example
                assert ((ROOT / name).parent / target).exists(), (name, target)

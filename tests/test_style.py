"""House rules from the brief, checked by a test so nobody has to remember them.

Reads : the repo's own files.  Writes: nothing.
Rules: short files with a header, only the allowed libraries, Python 3.10 syntax, no emoji, no missing Makefile step.
"""
import ast
import re
from pathlib import Path

import pytest

import config

ROOT = config.ROOT
SKIP = {"out", ".git", "__pycache__", ".pytest_cache", "venv", ".venv"}
MAX_LINES = 160   # "about 150"
ALLOWED = {"feast", "evidently", "pandas", "sklearn", "pytest", "numpy", "pyarrow", "fastapi", "google", "click"}   # numpy, pyarrow, fastapi, google, click come with the five; the Issue Lab and tests import them directly
EMOJI_RANGES = [(0x2600, 0x27BF), (0x2B50, 0x2B50), (0x1F300, 0x1FAFF)]   # symbols, dingbats, pictographs; ints keep this file ASCII


def has_emoji(text):
    return any(lo <= ord(c) <= hi for c in text for lo, hi in EMOJI_RANGES)


def files(*patterns):
    return [p for pat in patterns for p in ROOT.rglob(pat) if not SKIP & set(p.relative_to(ROOT).parts)]


PY = files("*.py")
CODE = files("*.py", "*.js", "*.css", "*.html")
TEXT = files("*.py", "*.js", "*.css", "*.html", "*.md", "*.yml", "*.yaml", "*.svg", "Makefile", "*.txt")


@pytest.mark.parametrize("path", CODE, ids=lambda p: str(p.relative_to(ROOT)))
def test_file_is_short(path):
    assert len(path.read_text(encoding="utf-8").splitlines()) <= MAX_LINES


@pytest.mark.parametrize("path", [p for p in PY if p.name != "__init__.py"], ids=lambda p: str(p.relative_to(ROOT)))
def test_python_file_has_a_header_and_uses_python_310_syntax(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 10))
    header = ast.get_docstring(tree) or ""
    assert header, "top of the file must say what it does"
    if path.parts[-2] in ("src", "feature_repo") or path.name in ("config.py", "check_all.py", "count.py", "lab.py"):
        assert "Reads" in header and "Writes" in header, "header must say what it reads and writes"


def test_only_allowed_libraries_are_imported():
    local = {p.stem for p in PY} | {"config", "feature_repo", "views", "entities", "lab", "check_all", "make_data", "model", "store", "workarounds", "train", "live", "check_drift", "alerts"}
    stdlib = set(__import__("sys").stdlib_module_names)
    seen = set()
    for path in PY:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) and node.module else []
            seen |= {n.split(".")[0] for n in names}
    assert not (seen - stdlib - local - ALLOWED), seen - stdlib - local - ALLOWED


def test_no_emoji_anywhere():
    bad = [str(p.relative_to(ROOT)) for p in TEXT if has_emoji(p.read_text(encoding="utf-8", errors="ignore"))]
    assert not bad, bad


def test_every_makefile_step_from_the_brief_exists():
    make = (ROOT / "Makefile").read_text(encoding="utf-8")
    for step in ("setup", "data", "train", "live", "drift", "ui", "test", "issues"):
        assert re.search(rf"^{step}:", make, re.M), step


def test_requirements_list_only_the_allowed_libraries():
    names = {re.split(r"[\[<>=~ ]", line.strip())[0].lower() for line in (ROOT / "requirements.txt").read_text().splitlines() if line.strip() and not line.startswith("#")}
    assert names == {"feast", "evidently", "pandas", "scikit-learn", "pytest"}


def test_views_paths_match_config():
    import sys

    sys.path.insert(0, str(config.REPO))
    import views

    assert views.history_source.path == Path(__import__("os").path.relpath(config.HISTORY, config.REPO)).as_posix()
    assert views.service_source.path == Path(__import__("os").path.relpath(config.SERVICE, config.REPO)).as_posix()

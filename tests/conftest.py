"""Test setup.

The `project` fixture runs the real pipeline once, in a temporary copy of the repo, so tests never touch out/.
Reads : config.py, feature_repo/, src/ (copied).  Writes: a temp folder, removed by pytest.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True  # keep __pycache__ out of the repo
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

STEPS = ["make_data", "train", "live", "check_drift", "alerts"]


class Project:
    def __init__(self, path):
        self.path = path

    def run(self, script, *args):
        env = {**os.environ, "FEAST_USAGE": "False", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([sys.executable, f"src/{script}.py", *args], cwd=self.path, capture_output=True, text=True, env=env)

    def json(self, name):
        def refuse(constant):  # NaN and Infinity are not valid JSON: the dashboard could not read them
            raise ValueError(f"invalid JSON constant {constant} in {name}")
        return json.loads((self.path / "out" / name).read_text(), parse_constant=refuse)


@pytest.fixture(scope="session")
def project(tmp_path_factory):
    dest = tmp_path_factory.mktemp("dw") / "driftwatch"
    dest.mkdir()
    shutil.copy(ROOT / "config.py", dest)
    for folder in ("feature_repo", "src"):
        shutil.copytree(ROOT / folder, dest / folder, ignore=shutil.ignore_patterns("__pycache__"))
    proj = Project(dest)
    for step in STEPS:
        done = proj.run(step)
        assert done.returncode == 0, f"{step} failed:\n{done.stdout[-1500:]}\n{done.stderr[-2500:]}"
    return proj

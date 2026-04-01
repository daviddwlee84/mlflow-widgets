"""Verify built wheel contains all expected files."""

from __future__ import annotations

import subprocess
import tempfile
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def built_wheel() -> Path:
    """Build the wheel once per test module and return its path."""
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            ["uv", "build", "--wheel", "--no-sources", "--out-dir", tmp],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"uv build failed:\n{result.stderr}"
        wheels = list(Path(tmp).glob("*.whl"))
        assert len(wheels) == 1, f"Expected 1 wheel, got {len(wheels)}"
        yield wheels[0]


def test_wheel_contains_py_typed(built_wheel: Path):
    with zipfile.ZipFile(built_wheel) as zf:
        names = zf.namelist()
    assert any("py.typed" in n for n in names), f"py.typed not in wheel: {names}"


def test_wheel_contains_static_js(built_wheel: Path):
    expected_js = {"mlflow-chart.js", "mlflow-table.js", "mlflow-parallel.js"}
    with zipfile.ZipFile(built_wheel) as zf:
        names = zf.namelist()
    found_js = {Path(n).name for n in names if n.endswith(".js")}
    missing = expected_js - found_js
    assert not missing, f"Missing JS files in wheel: {missing}"


def test_wheel_contains_license(built_wheel: Path):
    with zipfile.ZipFile(built_wheel) as zf:
        names = zf.namelist()
    assert any("LICENSE" in n for n in names), f"LICENSE not in wheel: {names}"


def test_wheel_contains_metadata(built_wheel: Path):
    with zipfile.ZipFile(built_wheel) as zf:
        names = zf.namelist()
    assert any("METADATA" in n for n in names), f"METADATA not in wheel: {names}"

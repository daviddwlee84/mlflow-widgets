"""Verify all example scripts are syntactically valid Python."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def _example_files():
    return sorted(EXAMPLES_DIR.glob("*.py"))


@pytest.mark.parametrize("path", _example_files(), ids=lambda p: p.name)
def test_example_parses(path: Path):
    source = path.read_text(encoding="utf-8")
    ast.parse(source, filename=str(path))

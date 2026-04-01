from __future__ import annotations

import ast
from pathlib import Path


def test_examples_parse() -> None:
    for path in sorted(Path("examples").glob("*.py")):
        ast.parse(path.read_text(encoding="utf-8"))

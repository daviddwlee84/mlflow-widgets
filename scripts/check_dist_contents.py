from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path


DIST_DIR = Path("dist")
REQUIRED_PACKAGE_FILES = [
    "mlflow_widgets/py.typed",
    "mlflow_widgets/static/mlflow-chart.js",
    "mlflow_widgets/static/mlflow-table.js",
    "mlflow_widgets/static/mlflow-parallel.js",
]


def _require_entry(names: list[str], label: str, predicate) -> None:
    if any(predicate(name) for name in names):
        return
    available = "\n".join(sorted(names))
    raise AssertionError(f"Missing {label}. Available entries:\n{available}")


def _check_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()

    for relative_path in REQUIRED_PACKAGE_FILES:
        _require_entry(
            names,
            relative_path,
            lambda name, suffix=relative_path: name.endswith(suffix),
        )

    _require_entry(
        names,
        "wheel license file",
        lambda name: name.endswith("LICENSE"),
    )


def _check_sdist(path: Path) -> None:
    with tarfile.open(path) as archive:
        names = archive.getnames()

    for relative_path in [
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "src/mlflow_widgets/py.typed",
        "src/mlflow_widgets/static/mlflow-chart.js",
        "src/mlflow_widgets/static/mlflow-table.js",
        "src/mlflow_widgets/static/mlflow-parallel.js",
    ]:
        _require_entry(
            names,
            relative_path,
            lambda name, suffix=relative_path: name.endswith(suffix),
        )


def main() -> int:
    wheel_paths = sorted(DIST_DIR.glob("*.whl"))
    sdist_paths = sorted(DIST_DIR.glob("*.tar.gz"))

    if len(wheel_paths) != 1 or len(sdist_paths) != 1:
        raise AssertionError(
            f"Expected exactly one wheel and one sdist in {DIST_DIR}, "
            f"found {len(wheel_paths)} wheel(s) and {len(sdist_paths)} sdist(s)"
        )

    _check_wheel(wheel_paths[0])
    _check_sdist(sdist_paths[0])
    print(f"Distribution contents look good for {wheel_paths[0].name} and {sdist_paths[0].name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

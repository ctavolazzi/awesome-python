from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from examples.awesome_viewer.generate_site import main


SAMPLE_README = """
# Awesome Python

## Web Frameworks
* [Flask](https://flask.palletsprojects.com/) - A simple framework.

## Visualization
* [Matplotlib](https://matplotlib.org/) - Plotting library.
""".strip()


@pytest.fixture()
def sample_readme(tmp_path: Path) -> Path:
    readme = tmp_path / "README.md"
    readme.write_text(SAMPLE_README, encoding="utf-8")
    return readme


def test_main_defaults_to_build(tmp_path: Path, sample_readme: Path) -> None:
    output_dir = tmp_path / "site"
    main(
        [
            "--readme",
            str(sample_readme),
            "--output",
            str(output_dir),
            "--preview-limit",
            "0",
        ]
    )

    assert (output_dir / "index.html").exists()
    assert (output_dir / "catalog.json").exists()
    assert (output_dir / "manifest.json").exists()


def test_module_entry_point_runs_build(tmp_path: Path, sample_readme: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_dir = tmp_path / "module-site"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "python",
            "--readme",
            str(sample_readme),
            "--output",
            str(output_dir),
            "--preview-limit",
            "0",
        ],
    )

    runpy.run_module("examples.awesome_viewer", run_name="__main__", alter_sys=True)

    assert (output_dir / "index.html").exists()
    assert (output_dir / "catalog.json").exists()
    assert (output_dir / "manifest.json").exists()

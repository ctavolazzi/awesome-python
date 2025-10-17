from __future__ import annotations

from pathlib import Path

import pytest

from examples.awesome_viewer.viewer.data import Entry, parse_readme, summarize_categories


SAMPLE_README = """
# Awesome Python

## Web Frameworks
* [Flask](https://flask.palletsprojects.com/) - A simple framework.
* [Django](https://www.djangoproject.com/) - A batteries-included framework.

## Resources
* [Some Resource](https://example.com) - Should be ignored.

## Visualization
* [Matplotlib](https://matplotlib.org/) - Plotting library.
    * [Seaborn](https://seaborn.pydata.org/) - Statistical plots.
""".strip()


def test_parse_readme_filters_and_groups(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(SAMPLE_README, encoding="utf-8")

    categories = parse_readme(readme)
    assert [category.title for category in categories] == ["Web Frameworks", "Visualization"]
    assert categories[0].items[0] == Entry(
        name="Flask",
        url="https://flask.palletsprojects.com/",
        description="A simple framework.",
    )
    assert len(categories[1].items) == 2


def test_summarize_categories_counts_entries(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(SAMPLE_README, encoding="utf-8")

    categories = parse_readme(readme)
    totals = summarize_categories(categories)
    assert totals == (2, 4)


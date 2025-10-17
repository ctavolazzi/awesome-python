from __future__ import annotations

import json
from pathlib import Path

from examples.awesome_viewer.viewer import BuildResult, Category, Entry, SiteBuilder


def test_site_builder_writes_assets(tmp_path: Path) -> None:
    template_dir = Path(__file__).resolve().parents[1] / "templates"
    asset_dir = Path(__file__).resolve().parents[1] / "assets"
    output_dir = tmp_path / "build"

    categories = [
        Category(
            title="Example",
            items=(
                Entry(name="Library", url="https://example.com", description="Helpful library"),
            ),
        )
    ]

    builder = SiteBuilder(template_dir=template_dir, asset_dir=asset_dir, output_dir=output_dir)
    result = builder.build(categories, metadata={"source_readme": "README.md"})

    assert isinstance(result, BuildResult)

    html = result.index_path.read_text(encoding="utf-8")
    assert "Example" in html
    assert "Library" in html

    css_path = output_dir / "style.css"
    js_path = output_dir / "app.js"
    assert css_path.exists()
    assert js_path.exists()

    catalog = json.loads(result.catalog_path.read_text(encoding="utf-8"))
    assert catalog[0]["title"] == "Example"
    assert catalog[0]["items"][0]["name"] == "Library"

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["totals"] == {"total_categories": 1, "total_entries": 1}
    assert manifest["metadata"]["source_readme"] == "README.md"


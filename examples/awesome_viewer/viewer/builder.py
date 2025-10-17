"""Site building utilities for the Awesome Viewer MVP."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .data import Category, summarize_categories


@dataclass(frozen=True)
class BuildResult:
    """Paths produced by :meth:`SiteBuilder.build`."""

    index_path: Path
    catalog_path: Path
    manifest_path: Path


class SiteBuilder:
    """Render the Awesome Viewer static site."""

    def __init__(
        self,
        *,
        template_dir: Path,
        asset_dir: Path,
        output_dir: Path,
    ) -> None:
        self.template_dir = template_dir
        self.asset_dir = asset_dir
        self.output_dir = output_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.filters.setdefault("tojson", json.dumps)

    def build(
        self,
        categories: Sequence[Category],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> BuildResult:
        """Render the HTML, copy assets, and emit JSON payloads."""

        totals = summarize_categories(categories)
        totals_payload = {
            "total_categories": totals[0],
            "total_entries": totals[1],
        }

        self.output_dir.mkdir(parents=True, exist_ok=True)

        template = self.env.get_template("index.html.j2")
        data_payload = [
            {
                "title": category.title,
                "slug": category.slug,
                "items": [
                    {
                        "name": entry.name,
                        "url": entry.url,
                        "description": entry.description,
                    }
                    for entry in category.items
                ],
            }
            for category in categories
        ]

        html = template.render(
            data=data_payload,
            totals=totals_payload,
        )
        index_path = self.output_dir / "index.html"
        index_path.write_text(html, encoding="utf-8")

        catalog_path = self.output_dir / "catalog.json"
        catalog_path.write_text(
            json.dumps(data_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        manifest_path = self.output_dir / "manifest.json"
        manifest_payload: dict[str, Any] = {
            "totals": totals_payload,
            "metadata": dict(metadata or {}),
        }
        manifest_path.write_text(
            json.dumps(manifest_payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        self._copy_assets()
        return BuildResult(
            index_path=index_path,
            catalog_path=catalog_path,
            manifest_path=manifest_path,
        )

    def _copy_assets(self) -> None:
        asset_output = self.output_dir
        asset_output.mkdir(parents=True, exist_ok=True)
        for asset in self.asset_dir.glob("*"):
            target = asset_output / asset.name
            if asset.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(asset, target)
            else:
                shutil.copy2(asset, target)


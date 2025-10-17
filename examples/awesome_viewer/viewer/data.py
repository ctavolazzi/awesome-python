"""Data parsing and preview helpers for the Awesome Viewer MVP."""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator, List, Sequence, Tuple

CATEGORY_HEADING_RE = re.compile(r"^## (?P<title>.+)")
ENTRY_RE = re.compile(
    r"^\* \[(?P<name>[^\]]+)\]\((?P<url>[^\)]+)\)\s*-\s*(?P<description>.+)$"
)
INDENTED_ENTRY_RE = re.compile(
    r"^\s{4}\* \[(?P<name>[^\]]+)\]\((?P<url>[^\)]+)\)\s*-\s*(?P<description>.+)$"
)

IGNORED_TITLES = {"awesome python", "resources", "contributing"}


@dataclass(frozen=True)
class Entry:
    """A single Awesome Python entry."""

    name: str
    url: str
    description: str


@dataclass(frozen=True)
class Category:
    """A rendered category containing zero or more entries."""

    title: str
    items: Tuple[Entry, ...]

    @property
    def slug(self) -> str:
        return slugify(self.title)


def slugify(value: str) -> str:
    """Return a URL-safe slug for the provided value."""

    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")


def parse_readme(readme_path: Path) -> List[Category]:
    """Parse the Awesome Python README into structured category data."""

    if not readme_path.exists():
        raise FileNotFoundError(f"README not found: {readme_path}")

    categories: List[Category] = []
    current_title: str | None = None
    current_entries: List[Entry] = []

    def flush_current() -> None:
        nonlocal current_title, current_entries
        if current_title and current_entries:
            categories.append(Category(current_title, tuple(current_entries)))
        current_title = None
        current_entries = []

    for raw_line in readme_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip("\n")
        heading_match = CATEGORY_HEADING_RE.match(line)
        if heading_match:
            flush_current()
            title = heading_match.group("title").strip()
            if not title or title.lower() in IGNORED_TITLES:
                continue
            current_title = title
            continue

        if not current_title:
            continue

        entry_match = ENTRY_RE.match(line) or INDENTED_ENTRY_RE.match(raw_line)
        if entry_match:
            current_entries.append(
                Entry(
                    name=entry_match.group("name"),
                    url=entry_match.group("url"),
                    description=entry_match.group("description"),
                )
            )

    flush_current()
    return categories


def summarize_categories(categories: Sequence[Category]) -> Tuple[int, int]:
    """Return counts of categories and entries."""

    total_categories = len(categories)
    total_entries = sum(len(category.items) for category in categories)
    return total_categories, total_entries


def iter_preview(
    categories: Sequence[Category],
    *,
    limit: int,
) -> Iterator[Tuple[int, int, Category]]:
    """Yield a slice of categories for preview output."""

    if limit <= 0:
        return iter(())
    return (
        (index, len(categories), category)
        for index, category in enumerate(categories[:limit], start=1)
    )


def print_category_preview(
    categories: Sequence[Category],
    *,
    limit: int,
    mode: str = "list",
    interactive: bool | None = None,
    input_func: Callable[[str], str] = input,
) -> None:
    """Print a preview of the parsed categories and entries."""

    preview = list(iter_preview(categories, limit=limit))
    if not preview:
        return

    if interactive is None:
        interactive = sys.stdin.isatty()

    stepwise = mode == "step" and interactive
    print("Parsed categories:")
    for index, total, category in preview:
        header = f"[{index}/{total}] {category.title} ({len(category.items)} entries)"
        print(header)
        for entry in category.items[:3]:
            print(f"  - {entry.name}: {entry.description}")
        remaining = len(category.items) - 3
        if remaining > 0:
            print(f"    …and {remaining} more entries")
        if stepwise and index < len(preview):
            try:
                response = input_func("Press Enter for next category (or q to quit): ")
            except EOFError:
                break
            if response.strip().lower() == "q":
                break


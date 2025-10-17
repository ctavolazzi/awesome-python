"""Generate and serve the Awesome Viewer MVP static site."""
"""Generate and serve a lightweight viewer for the Awesome Python catalog."""
from __future__ import annotations

import argparse
import http.server
import socketserver
import sys
from datetime import datetime, timezone
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from examples.awesome_viewer.viewer import (  # noqa: E402
    SiteBuilder,
    parse_readme,
    print_category_preview,
)

DEFAULT_OUTPUT_DIR = THIS_DIR / "build"
DEFAULT_README = PROJECT_ROOT / "README.md"


def build_command(args: argparse.Namespace) -> None:
    readme_path = Path(args.readme)
    output_dir = Path(args.output)

    categories = parse_readme(readme_path)
    if not categories:
        raise SystemExit("No categories found in README; aborting build.")

    if not args.quiet:
        print(f"Parsed {len(categories)} categories from {readme_path}")

    if args.preview_limit:
        print_category_preview(
            categories,
            limit=args.preview_limit,
            mode=args.preview_mode,
            interactive=sys.stdin.isatty(),
        )

    builder = SiteBuilder(
        template_dir=THIS_DIR / "templates",
        asset_dir=THIS_DIR / "assets",
        output_dir=output_dir,
    )
    metadata = {
        "source_readme": str(readme_path.resolve()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_limit": args.preview_limit,
        "preview_mode": args.preview_mode,
    }
    result = builder.build(categories, metadata=metadata)

    if not args.quiet:
        for path in (result.index_path, result.catalog_path, result.manifest_path):
            try:
                display_path = path.relative_to(Path.cwd())
            except ValueError:
                display_path = path
            print(f"Wrote {display_path}")


class SilentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Simple handler that hides noisy log output unless verbose."""

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        if getattr(self.server, "verbose", False):
            super().log_message(format, *args)


def serve_command(args: argparse.Namespace) -> None:
    output_dir = Path(args.output)
    if not args.no_build:
        build_command(args)

    handler = lambda *handler_args, **handler_kwargs: SilentHTTPRequestHandler(  # type: ignore[arg-type]
        *handler_args,
        directory=str(output_dir),
        **handler_kwargs,
    )

    with socketserver.TCPServer(("0.0.0.0", args.port), handler) as httpd:
        httpd.verbose = args.verbose  # type: ignore[attr-defined]
        url = f"http://localhost:{args.port}"
        print(f"Serving {output_dir} at {url} (press Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped")


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--readme",
        default=str(DEFAULT_README),
        help="Path to the Awesome Python README to parse.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where the static site will be written.",
    )
    parser.add_argument(
        "--preview-limit",
        type=int,
        default=5,
        help="Number of categories to print during preview (0 to disable).",
    )
    parser.add_argument(
        "--preview-mode",
        choices=("list", "step"),
        default="list",
        help="Preview categories all at once or step through interactively.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress build progress output.",
    )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.set_defaults(func=build_command, command="build")
    _add_common_arguments(parser)

    common = argparse.ArgumentParser(add_help=False)
    _add_common_arguments(common)

    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser(
        "build",
        help="Generate the static site.",
        parents=[common],
    )
    build_parser.set_defaults(func=build_command, command="build")

    serve_parser = subparsers.add_parser(
        "serve",
        help="Serve the static site for local testing.",
        parents=[common],
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the development server.",
    )
    serve_parser.add_argument(
        "--no-build",
        action="store_true",
        help="Skip rebuilding the site before serving.",
    )
    serve_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log every HTTP request handled by the development server.",
    )
    serve_parser.set_defaults(func=serve_command, command="serve")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = create_parser()
    args = parser.parse_args(argv)

    args.func(args)
import json
import os
import re
import socketserver
import textwrap
from pathlib import Path
from typing import Dict, Iterable, List, Optional

THIS_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = THIS_DIR / "site"
DEFAULT_README = Path(__file__).resolve().parents[2] / "README.md"

CATEGORY_HEADING_RE = re.compile(r"^## (.+)")
ENTRY_RE = re.compile(r"^\* \[(?P<name>[^\]]+)\]\((?P<url>[^\)]+)\)\s*-\s*(?P<description>.+)$")
INDENTED_ENTRY_RE = re.compile(r"^\s{4}\* \[(?P<name>[^\]]+)\]\((?P<url>[^\)]+)\)\s*-\s*(?P<description>.+)$")


def parse_readme(readme_path: Path) -> List[Dict[str, object]]:
    """Parse the Awesome Python README into structured category data."""
    categories: List[Dict[str, object]] = []
    current: Optional[Dict[str, object]] = None

    for raw_line in readme_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip("\n")

        heading_match = CATEGORY_HEADING_RE.match(line)
        if heading_match:
            title = heading_match.group(1).strip()
            if not title or title.lower() in {"awesome python", "resources", "contributing"}:
                current = None
                continue
            current = {"title": title, "items": []}
            categories.append(current)
            continue

        if current is None:
            continue

        entry_match = ENTRY_RE.match(line) or INDENTED_ENTRY_RE.match(raw_line)
        if entry_match:
            current["items"].append(
                {
                    "name": entry_match.group("name"),
                    "url": entry_match.group("url"),
                    "description": entry_match.group("description"),
                }
            )

    # Filter out categories without items to avoid empty sections.
    return [cat for cat in categories if cat["items"]]


def build_html(categories: Iterable[Dict[str, object]]) -> str:
    data_json = json.dumps(list(categories))
    return textwrap.dedent(
        f"""
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\" />
            <title>Awesome Python Viewer</title>
            <style>
                :root {{
                    color-scheme: light dark;
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: #f6f6f6;
                    color: #222;
                }}
                body {{
                    margin: 0;
                    padding: 2rem;
                    line-height: 1.5;
                }}
                header {{
                    max-width: 960px;
                    margin: 0 auto 1.5rem;
                    text-align: center;
                }}
                header h1 {{
                    margin-bottom: 0.25rem;
                }}
                #search {{
                    width: min(640px, 90vw);
                    padding: 0.75rem 1rem;
                    font-size: 1rem;
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    outline: none;
                    box-shadow: 0 0 0 rgba(0, 0, 0, 0.05);
                    transition: box-shadow 0.2s ease;
                }}
                #search:focus {{
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.35);
                }}
                main {{
                    max-width: 960px;
                    margin: 0 auto;
                }}
                section {{
                    margin-bottom: 2rem;
                    padding-bottom: 1rem;
                    border-bottom: 1px solid #e2e8f0;
                }}
                h2 {{
                    margin-top: 1.5rem;
                    font-size: 1.5rem;
                }}
                ul {{
                    list-style: none;
                    padding-left: 0;
                }}
                li {{
                    margin: 0.75rem 0;
                }}
                a {{
                    color: #2563eb;
                    text-decoration: none;
                    font-weight: 600;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .description {{
                    display: block;
                    color: #4b5563;
                    margin-top: 0.25rem;
                }}
                .hidden {{
                    display: none !important;
                }}
                @media (prefers-color-scheme: dark) {{
                    :root {{ background: #0f172a; color: #e2e8f0; }}
                    #search {{
                        background: #1e293b;
                        color: inherit;
                        border-color: #334155;
                    }}
                    section {{ border-color: #1e293b; }}
                    a {{ color: #60a5fa; }}
                    .description {{ color: #cbd5f5; }}
                }}
            </style>
        </head>
        <body>
            <header>
                <h1>Awesome Python Viewer</h1>
                <p>Search and browse curated Python libraries from the Awesome Python list.</p>
                <input id=\"search\" type=\"search\" placeholder=\"Filter by library name, category, or description...\" aria-label=\"Search entries\" />
            </header>
            <main id=\"content\"></main>
            <script>
                const data = {data_json};

                const container = document.getElementById('content');
                const searchInput = document.getElementById('search');

                const render = (items) => {{
                    container.innerHTML = '';
                    for (const category of items) {{
                        const section = document.createElement('section');
                        const heading = document.createElement('h2');
                        heading.textContent = category.title;
                        section.appendChild(heading);

                        const list = document.createElement('ul');
                        for (const entry of category.items) {{
                            const listItem = document.createElement('li');
                            const link = document.createElement('a');
                            link.href = entry.url;
                            link.target = '_blank';
                            link.rel = 'noopener noreferrer';
                            link.textContent = entry.name;
                            listItem.appendChild(link);

                            const description = document.createElement('span');
                            description.className = 'description';
                            description.textContent = entry.description;
                            listItem.appendChild(description);

                            list.appendChild(listItem);
                        }}
                        section.appendChild(list);
                        container.appendChild(section);
                    }}
                }};

                const matches = (entry, query) => {{
                    const haystack = `${{entry.name}} ${{entry.description}}`.toLowerCase();
                    return haystack.includes(query);
                }};

                const filterData = (query) => {{
                    if (!query) return data;
                    const lowerQuery = query.toLowerCase();
                    return data
                        .map(category => {{
                            const filteredItems = category.items.filter(item => matches(item, lowerQuery) || category.title.toLowerCase().includes(lowerQuery));
                            return filteredItems.length ? {{ ...category, items: filteredItems }} : null;
                        }})
                        .filter(Boolean);
                }};

                searchInput.addEventListener('input', (event) => {{
                    render(filterData(event.target.value));
                }});

                render(data);
            </script>
        </body>
        </html>
        """
    ).strip()


def write_site(output_dir: Path, categories: Iterable[Dict[str, object]]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    html = build_html(categories)
    destination = output_dir / "index.html"
    destination.write_text(html, encoding="utf-8")
    return destination


def serve_directory(directory: Path, port: int) -> None:
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving Awesome Python Viewer at http://127.0.0.1:{port}")
        print("Press Ctrl+C to stop the server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=False)

    build_parser = subparsers.add_parser("build", help="Generate the static viewer")
    build_parser.add_argument("--readme", type=Path, default=DEFAULT_README, help="Path to the README file to parse")
    build_parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory for the static site")

    serve_parser = subparsers.add_parser("serve", help="Serve the viewer locally")
    serve_parser.add_argument("--readme", type=Path, default=DEFAULT_README, help="Path to the README file to parse")
    serve_parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory for the static site")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port for the local HTTP server")
    serve_parser.add_argument("--no-build", action="store_true", help="Skip rebuilding before serving")

    parser.set_defaults(command="build")
    args = parser.parse_args(argv)

    if args.command == "build":
        categories = parse_readme(args.readme)
        destination = write_site(args.output, categories)
        print(f"Wrote viewer to {destination}")
    elif args.command == "serve":
        if not args.no_build:
            categories = parse_readme(args.readme)
            write_site(args.output, categories)
        serve_directory(args.output, args.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

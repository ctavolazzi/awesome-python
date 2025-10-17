"""Generate and serve a lightweight viewer for the Awesome Python catalog."""
from __future__ import annotations

import argparse
import http.server
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

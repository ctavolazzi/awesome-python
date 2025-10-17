"""Generate and serve the Awesome Viewer MVP static site."""
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


if __name__ == "__main__":
    main()

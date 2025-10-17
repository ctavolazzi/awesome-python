# Awesome Python Viewer

This example project generates a tiny static site that lets you browse the categories and entries from the root `README.md` file. It is meant to be a lightweight way to visualize the curated list without requiring extra dependencies.

## Usage

Install the minimal dependency (Jinja2) if it is not already available:

```bash
pip install -r examples/awesome_viewer/requirements.txt
```

```bash
# From the repository root
python examples/awesome_viewer/generate_site.py       # defaults to `build`
python examples/awesome_viewer/generate_site.py serve --port 8000
# Alternatively, run as a module if you prefer
python -m examples.awesome_viewer --output /tmp/viewer
# Or use the provided Makefile shortcuts
make viewer_install
make viewer_build
make viewer_serve
```

The `build` command creates `examples/awesome_viewer/build/index.html` alongside the compiled CSS and JavaScript bundles, reporting how many categories and entries were parsed from the README. It also emits `catalog.json` (all rendered categories and entries) and `manifest.json` (totals plus build metadata such as the source README path and preview settings) next to the HTML. These files make it trivial to smoke test the output in CI or wire the catalog data into other experiments. The `serve` command rebuilds the page (unless you pass `--no-build`) and then serves the generated site locally using Python's built-in HTTP server. Open the reported URL in your browser to explore the list with live filtering. The refreshed interface keeps the quick stats and instant search, but also adds a left-hand category navigator, keyboard shortcuts, and a step-through preview panel so you can click—or press `[` and `]`—to move through the visible categories.

You can also supply a custom output directory or a different README file if you want to experiment with alternative data sources. Run `python examples/awesome_viewer/generate_site.py --help` to see the available options.

By default the commands preview each parsed category in the console so you can confirm the entries that will appear in the viewer. Use `--preview-limit` to change how many entries are shown (or pass `--preview-limit 0` to disable the preview entirely). When you'd like to step through the results, add `--preview-mode step` so the CLI pauses after each category—matching the new in-browser preview panel—and lets you continue (or quit) interactively.
In non-interactive environments (like CI) the CLI automatically falls back to the list preview so that builds never block waiting for input.

Running the script with no subcommand now performs a build automatically, so `python examples/awesome_viewer/generate_site.py --output /tmp/site` produces artifacts immediately. The same behavior is available when launching the module directly (`python -m examples.awesome_viewer`), which keeps CI invocations short and mirrors how other Python CLIs behave.

## Capturing a quick screenshot

If you just want to confirm that the generated page renders correctly without browsing through every category, you can grab a screenshot of the viewer's hero section after starting the development server:

```bash
# Build the site and start the dev server on port 8765
python examples/awesome_viewer/generate_site.py build
python examples/awesome_viewer/generate_site.py serve --port 8765
```

Then open `http://127.0.0.1:8765` in your browser and capture the visible portion of the page. The screenshot in the pull request description was produced with that flow and shows the header plus the first category rendered by the viewer. If you are debugging in a terminal-only environment, inspect the freshly written `build/catalog.json` and `build/manifest.json`—they contain the exact data and metadata used by the UI.
```bash
# From the repository root
python examples/awesome_viewer/generate_site.py build
python examples/awesome_viewer/generate_site.py serve --port 8000
```

The `build` command creates `examples/awesome_viewer/site/index.html`. The `serve` command rebuilds the page (unless you pass `--no-build`) and then serves the generated site locally using Python's built-in HTTP server. Open the reported URL in your browser to explore the list with live filtering.

You can also supply a custom output directory or a different README file if you want to experiment with alternative data sources. Run `python examples/awesome_viewer/generate_site.py --help` to see the available options.

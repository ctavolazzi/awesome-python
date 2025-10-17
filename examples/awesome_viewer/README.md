# Awesome Python Viewer

This example project generates a tiny static site that lets you browse the categories and entries from the root `README.md` file. It is meant to be a lightweight way to visualize the curated list without requiring extra dependencies.

## Usage

```bash
# From the repository root
python examples/awesome_viewer/generate_site.py build
python examples/awesome_viewer/generate_site.py serve --port 8000
```

The `build` command creates `examples/awesome_viewer/site/index.html`. The `serve` command rebuilds the page (unless you pass `--no-build`) and then serves the generated site locally using Python's built-in HTTP server. Open the reported URL in your browser to explore the list with live filtering.

You can also supply a custom output directory or a different README file if you want to experiment with alternative data sources. Run `python examples/awesome_viewer/generate_site.py --help` to see the available options.

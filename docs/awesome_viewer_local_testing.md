# Awesome Viewer Local Testing Guide

Follow these steps to exercise the Awesome Viewer MVP on your machine before shipping changes:

1. **Install dependencies**
   ```bash
   pip install -r examples/awesome_viewer/requirements.txt
   ```
2. **Run the automated tests**
   ```bash
   pytest examples/awesome_viewer/tests
   ```
3. **Build the static site**
   ```bash
   python examples/awesome_viewer/generate_site.py build
   ```
   Review the printed preview and confirm that `index.html`, `catalog.json`, and `manifest.json` exist in the chosen output directory.
4. **Serve the site locally**
   ```bash
   python examples/awesome_viewer/generate_site.py serve --port 8765 --no-build
   ```
   Then open `http://127.0.0.1:8765` to browse the refreshed interface. Use the search box, category chips, and step-through preview panel to verify the interactive behaviour.
5. **Optional Makefile shortcuts**
   ```bash
   make viewer_install
   make viewer_build
   make viewer_serve
   ```
   These commands wrap the same workflow and are helpful for repeat runs in CI or documentation.

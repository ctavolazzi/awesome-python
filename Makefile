site_install:
	pip install -r requirements.txt

site_link:
	ln -sf $(CURDIR)/README.md $(CURDIR)/docs/index.md

site_preview: site_link
	mkdocs serve

site_build: site_link
	mkdocs build

site_deploy: site_link
	mkdocs gh-deploy --clean

viewer_install:
	pip install -r examples/awesome_viewer/requirements.txt

viewer_build:
	python examples/awesome_viewer/generate_site.py build

viewer_serve:
	python examples/awesome_viewer/generate_site.py serve --port 8765

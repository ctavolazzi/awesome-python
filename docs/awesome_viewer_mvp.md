# Awesome Viewer MVP Plan

## Overview
The Awesome Viewer example has evolved from a static catalog listing to a richer browsing experience with category previews, interactive filtering, and a responsive interface. To ship an MVP that is easy to maintain and deploy, we should focus on a tightly scoped set of capabilities that demonstrate the value of the catalog without over-engineering the workflow.

## Target Audience
- Maintainers of the Awesome Python catalog who want a quick way to review curated entries.
- Curious developers exploring Python libraries, frameworks, and learning resources.
- Contributors evaluating whether their additions render correctly and contain the expected metadata.

## MVP Goals
1. **Surface the catalog quickly** so visitors can discover categories and entries without reading raw Markdown.
2. **Support lightweight exploration** with search, filtering, and detail previews that work on desktop and mobile devices.
3. **Remain simple to host** by producing static assets that can be uploaded to any static hosting provider or served locally.

## MVP Feature Scope
- Generate a static site from the existing catalog data via a single CLI command (`python generate_site.py build`).
- Provide category navigation and live search over entries with minimal client-side JavaScript.
- Display entry metadata (name, description, GitHub stats when available) in a concise card layout.
- Offer an optional CLI preview mode that steps through categories and a quiet mode for automation.
- Include responsive styling that keeps the layout readable on common viewport sizes (mobile, tablet, desktop).

## Technical Requirements
- **Build Pipeline**: Python 3.9+ script that parses `README.md`, extracts categories and entries, and writes pre-rendered HTML, CSS, JS bundles, and machine-readable JSON payloads (catalog + manifest) to a `build/` directory.
- **Templates**: Jinja2 or similar templating approach with reusable partials for sidebar navigation, entry cards, and hero statistics.
- **Client Logic**: Vanilla JavaScript modules for search indexing (e.g., lunr.js or Fuse.js) and hash-aware navigation; keep bundle under 100 KB uncompressed.
- **Styling**: PostCSS or Sass optional; default to a single compiled CSS file emphasizing accessibility (WCAG AA contrast, keyboard focus states).
- **Testing**: CLI unit tests for parser and generator functions, plus a smoke test that verifies the build output contains the expected sections.
- **Documentation**: README updates covering build, preview, and deploy workflows; inline code comments for key parsing and rendering functions.

## Out of Scope for MVP
- Server-side APIs or dynamic content fetching.
- User authentication or personalization features.
- Advanced analytics, bookmarking, or export capabilities.
- Automated screenshot capture beyond manual guidance.

## Risks & Mitigations
- **Parsing Drift**: Changes to the root catalog format could break extraction. Mitigate with regression tests that assert expected category counts.
- **Bundle Bloat**: Extra libraries could inflate load times. Track bundle size during build and enforce a budget through CI checks.
- **Accessibility Regressions**: Rapid UI iteration may degrade a11y. Run automated audits (axe) and document manual testing steps.

## Next Steps Toward MVP
1. Stabilize the parser into reusable modules with unit tests and clear error handling.
2. Modularize the template structure so layout changes do not require editing inline strings.
3. Introduce a lightweight search index (e.g., Fuse.js) with debounce to improve discoverability.
4. Add CI automation that runs the build, tests, and bundle size check on pull requests.
5. Provide a simple deployment recipe (GitHub Pages or Netlify) with environment-agnostic instructions.

## Expert Recommendations
- **Focus on maintainability**: Extract data parsing, template rendering, and asset management into dedicated modules. This separation will make future UI iterations safer.
- **Invest in testing early**: A small suite of parser and build tests will catch regressions as the catalog evolves and contributors add new categories.
- **Keep tooling lean**: Avoid introducing heavyweight frontend frameworks until we outgrow static templating. The MVP can rely on progressive enhancement.
- **Plan for contributions**: Document the CLI options and preview capabilities, and provide clear guidelines for adding new visual components without breaking the build.
- **Monitor feedback loops**: After shipping the MVP, gather feedback from catalog maintainers and developers to prioritize enhancements such as advanced filtering or offline support.

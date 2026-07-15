"""Sphinx configuration."""

import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "splinenorm"
copyright = "2026, Dario Gonzalez Picos"
author = "Dario Gonzalez Picos"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_nb",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

nb_execution_mode = "off"
nb_render_markdown_format = "commonmark"

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

html_theme = "pydata_sphinx_theme"
html_title = "splinenorm"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_favicon = "_static/favicon.svg"

html_baseurl = os.environ.get(
    "DOCS_BASE_URL", "https://dgonzalezpicos.github.io/splinenorm/"
)

html_theme_options = {
    "github_url": "https://github.com/DGonzalezPicos/splinenorm",
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "show_prev_next": True,
    "show_nav_level": 2,
    "navigation_depth": 3,
    "header_links_before_dropdown": 4,
    "pygments_light_style": "default",
    "pygments_dark_style": "monokai",
    "footer_start": ["copyright"],
    "footer_end": [],
}

html_context = {
    "github_user": "DGonzalezPicos",
    "github_repo": "splinenorm",
    "github_version": "main",
    "doc_path": "docs",
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False

NOTEBOOK_PAGES = {
    "examples/getting_started",
    "examples/fit_continuum",
    "examples/fit_fringing",
}


def setup(app):
    """Inject GitHub / Colab toolbar on rendered notebook pages."""

    def _add_notebook_toolbar(app, pagename, templatename, context, doctitle):
        if pagename in NOTEBOOK_PAGES:
            context["notebook_ipynb"] = f"{pagename}.ipynb"

    app.connect("html-page-context", _add_notebook_toolbar)

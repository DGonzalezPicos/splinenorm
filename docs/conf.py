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
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_title = "splinenorm"

# GitHub Pages serves from a subdirectory when using project pages; leave empty
# for user/organization pages or when using the default github.io repo root.
html_baseurl = os.environ.get("DOCS_BASE_URL", "")

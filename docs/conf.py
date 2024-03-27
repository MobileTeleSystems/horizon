# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.


import os
import sys
from pathlib import Path

from packaging import version as Version

PROJECT_ROOT_DIR = Path(__file__).parent.parent.resolve()

sys.path.insert(0, os.fspath(PROJECT_ROOT_DIR))

# -- Project information -----------------------------------------------------

project = "horizon"
copyright = "2023-2024 MTS (Mobile Telesystems)"
author = "DataOps.ETL"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.

# this value is updated automatically by `poetry version ...` and poetry-bumpversion plugin
ver = Version.parse("0.1.1")
version = ver.base_version
# The full version, including alpha/beta/rc tags.
release = ver.public

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "numpydoc",
    "sphinx_copybutton",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.autodoc_pydantic",
    "sphinxcontrib.towncrier",  # provides `towncrier-draft-entries` directive
    "sphinx_issues",
    "sphinx_design",  # provides `dropdown` directive
    "sphinxcontrib.plantuml",
    "sphinx_favicon",
    "sphinxarg.ext",
]
swagger = [
    {
        "name": "Horizon REST API",
        "page": "openapi",
        "id": "horizon-api",
        "options": {
            "url": "_static/openapi.json",
        },
    }
]
numpydoc_show_class_members = True
autodoc_pydantic_model_show_config = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_config_member = False
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_validator_members = False
autodoc_pydantic_model_member_order = "bysource"
autodoc_pydantic_settings_show_config = False
autodoc_pydantic_settings_show_config_summary = True
autodoc_pydantic_settings_show_config_member = False
autodoc_pydantic_settings_show_json = False
autodoc_pydantic_settings_show_validator_summary = False
autodoc_pydantic_settings_show_validator_members = False
autodoc_pydantic_settings_member_order = "bysource"
autodoc_pydantic_field_list_validators = False
sphinx_tabs_disable_tab_closing = True

# prevent >>>, ... and doctest outputs from copying
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_copy_empty_lines = False
copybutton_only_copy_prompt_lines = True

towncrier_draft_autoversion_mode = "draft"
towncrier_draft_include_empty = False
towncrier_draft_working_directory = PROJECT_ROOT_DIR

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = "furo"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "sidebar_hide_name": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_extra_path = ["robots.txt"]
html_css_files = [
    "custom.css",
]

html_logo = "./_static/logo_no_title.svg"
favicons = [
    {"rel": "icon", "href": "icon.svg", "type": "image/svg+xml"},
]

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "horizon-doc"


# which is the equivalent to:
issues_uri = "https://github.com/MobileTeleSystems/horizon/issues/{issue}"
issues_pr_uri = "https://github.com/MobileTeleSystems/horizon/pulls/{pr}"
issues_commit_uri = "https://github.com/MobileTeleSystems/horizon/commit/{commit}"
issues_user_uri = "https://github.com/{user}"

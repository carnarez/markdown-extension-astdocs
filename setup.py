"""Make `markdown-astdocs` installable (via `pip install git+https://...`)."""

import setuptools

setuptools.setup(
    author="carnarez",
    description="Add support for astdocs output %%% markers to Python-Markdown.",
    install_requires = ["markdown"],
    name="markdown-astdocs",
    py_modules=["markdown_astdocs"],
    url="https://github.com/carnarez/markdown-astdocs",
    version="0.0.1",
)

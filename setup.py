"""Make `markdown-astdocs` installable (via `pip install git+https://...`)."""

import setuptools  # type: ignore

setuptools.setup(
    author="carnarez",
    description="Add support for astdocs output %%% markers to Python-Markdown.",
    install_requires=["markdown"],
    name="markdown-astdocs",
    packages=["markdown_astdocs"],
    package_data={"markdown_astdocs": ["*.pyi", "py.typed"]},
    url="https://github.com/carnarez/markdown-astdocs",
    version="0.0.1",
)

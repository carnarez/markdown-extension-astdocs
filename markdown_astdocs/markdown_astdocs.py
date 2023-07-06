'''Python-Markdown extension catching the `%%%` markers from `astdocs` output.

`pip install git+https://github.com/carnarez/markdown-astdocs` and refer to the
brilliant [`Python` implementation](https://github.com/Python-Markdown/markdown).
See [this repo](https://github.com/carnarez/astdocs) for `astdocs`.

* `ASTDOCS_BOUND_OBJECTS` adds `%%%START ...` and `%%%END ...` markers to indicate the
  beginning/end of an object; replaced by `<div class="...-object">...</div>` logic.
* `ASTDOCS_WITH_LINENOS` shows the line numbers of the object in the code source;
  replaced by `<details><summary>source</summary>...</details>` logic.

Example:
-------
````python
import markdown

src = """
%%%START FUNCTIONDEF package.module.main
# `package.module.main`

```python
main():
```

Process CLI calls.

%%%SOURCE package/module.py:10:22
%%%END FUNCTIONDEF package.module.main
"""

markdown.markdown(src, extensions=[AstdocsExtension(path="./package")])
````

'''

import pathlib
import re
from xml.etree.ElementTree import Element, SubElement

from markdown.blockparser import BlockParser
from markdown.blockprocessors import BlockProcessor
from markdown.core import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

SOURCE_RE: str = r"%%%SOURCE (.*):([0-9]+):([0-9]+)"
START_RE: str = r"%%%START ([A-Z]+) (.*)"
END_RE: str = r"%%%END ([A-Z]+) (.*)"


class AstdocsSourcePreprocessor(Preprocessor):
    """Catch and replace the `%%%SOURCE ...` markers."""

    def __init__(self, md: Markdown, path: str) -> None:
        """All methods inherited, but the `run()` one below.

        Parameters
        ----------
        md : markdown.core.Markdown
            Internal `Markdown` object to process.
        path : str
            Extra path prefix to add when fishing for the source.

        Attributes
        ----------
        path : str
            Path prefix.
        """
        super().__init__(md)
        self.path = path

    @staticmethod
    def percent_source(
        path: str,
        lineno: int = 1,
        lineno_end: int | None = None,
    ) -> str:
        """Read code from source file and substitute the `%%%SOURCE ...` marker.

        Parameters
        ----------
        path : str
            Path to the source file to extract code.
        lineno : int
            Beginning of the code block. Defaults to `1`.
        lineno_end : int
            End of the code block. Defaults to `None`.

        Returns
        -------
        : str
            HTML replacement.

        Notes
        -----
        Line numbers are expected to start at 1.
        """
        with pathlib.Path(path).open() as f:
            src = "".join(f.readlines()[lineno - 1 : lineno_end]).strip()

        if "```" in src:
            fences = sorted(re.findall(r"`+", src), key=len)
            fence = "`" * (len(fences[-1]) + 1)
        else:
            fence = "```"

        return (
            "<details>"
            "<summary>source</summary>"
            "\n\n"
            f"{fence}python"
            "\n"
            f"{src}"
            "\n"
            f"{fence}"
            "\n\n"
            "</details>"
        )

    @staticmethod
    def percent_start() -> str:
        """Substitute a `%%%START ...` marker.

        Returns
        -------
        : str
            HTML replacement.
        """
        return '<div class="objectdef">'

    @staticmethod
    def percent_end() -> str:
        """Substitute a `%%%END ...` marker.

        Returns
        -------
        : str
            HTML replacement.
        """
        return "</div>"

    def run(self, lines: list[str]) -> list[str]:
        r"""Overwritten method to process the input `Markdown` lines.

        Parameters
        ----------
        lines : list[str]
            `Markdown` content (split by `\n`).

        Returns
        -------
        : list[str]
            Same list of lines, processed.
        """
        escaped = 0

        for i, line in enumerate(lines):
            if line.startswith("```"):
                escaped = line.count("`")

            if escaped and line == escaped * "`":
                escaped = 0

            if not escaped:
                for m in re.finditer(SOURCE_RE, line):
                    lines[i] = line.replace(
                        m.group(0),
                        self.percent_source(
                            f"{self.path}/{m.group(1)}",
                            int(m.group(2)),
                            int(m.group(3)),
                        ),
                    )

        return lines


class AstdocsStartEndBlockProcessor(BlockProcessor):
    """Process `%%%START ...` to `%%%END ...` blocks."""

    def __init__(self, parser: BlockParser) -> None:
        """All methods inherited, but the `test()` and `run()` ones below.

        Parameters
        ----------
        parser: markdown.blockparser.BlockParser
            Parser of the `Markdown` object to process.
        """
        super().__init__(parser)

    def test(self, parent: Element, block: str) -> bool:
        """Check if the `run()` method should be called to process the block.

        Parameters
        ----------
        parent : xml.etree.ElementTree.Element
            Parent element that will host the tree of the current block, once rendered.
        block : str
            Current block to process.

        Returns
        -------
        : bool
            `True` if pattern is found, `False` otherwise.
        """
        return re.match(START_RE, block) is not None

    def run(self, parent: Element, blocks: list[str]) -> None:
        """Bound the block within the remaining blocks and render it.

        Parameters
        ----------
        parent : xml.etree.ElementTree.Element
            Parent element that will host the tree of the current block, once rendered.
        blocks : list[str]
            List of the remaining lines to process.
        """
        block = blocks[0]
        blocks[0] = re.sub(START_RE, "", blocks[0])

        for i, b in enumerate(blocks):
            if re.search(END_RE, b):
                blocks[i] = re.sub(END_RE, "", b)

                e = SubElement(parent, "div", attrib={"class": "objectdef"})
                self.parser.parseBlocks(e, blocks[0 : i + 1])

                for _ in range(0, i + 1):
                    blocks.pop(0)

                return  # we done here

        blocks[0] = block


class AstdocsExtension(Extension):
    """Extension to be imported when calling for the renderer."""

    def __init__(self, path: str = ".", **kwargs) -> None:
        """Make the extension configurable.

        Parameters
        ----------
        path : str
            Extra path prefix to add when fishing for the source. Defaults to `.`.

        Notes
        -----
        We want to take care of the `%%%` markers as early as possible to avoid any
        HTML noise around them, hence the high priority.
        """
        self.config = {
            "path": [path, "Extra path prefix to add when fishing for the source"],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        """Overwritten method to process the content.

        Parameters
        ----------
        md : markdown.core.Markdown
            Internal `Markdown` object to process.
        """
        md.preprocessors.register(
            AstdocsSourcePreprocessor(md, self.getConfig("path")),
            name="astdocs-source",
            priority=100,
        )
        md.parser.blockprocessors.register(
            AstdocsStartEndBlockProcessor(md.parser),
            name="astdocs-objectdef",
            priority=175,
        )

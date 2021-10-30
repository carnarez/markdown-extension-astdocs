# Module `markdown_astdocs`

Python-Markdown extension catching the `%%%` markers from `astdocs` output.

`pip install git+https://github.com/carnarez/markdown-astdocs` and refer to the
brilliant [`Python` implementation](https://github.com/Python-Markdown/markdown). See
[this repo](https://github.com/carnarez/astdocs) for `astdocs`.

- `ASTDOCS_BOUND_OBJECTS` adds `%%%START ...` and `%%%END ...` markers to indicate the
  beginning/end of an object; replaced by `<div class="...-object">...</div>` logic.
- `ASTDOCS_WITH_LINENOS` shows the line numbers of the object in the code source;
  replaced by `<details><summary>source</summary>...</details>` logic.

**Example:**

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

**Functions:**

- [`percent_source()`](#markdown_astdocspercent_source)
- [`percent_start()`](#markdown_astdocspercent_start)
- [`percent_end()`](#markdown_astdocspercent_end)

**Classes:**

- [`AstdocsSourcePreprocessor`](#markdown_astdocsastdocssourcepreprocessor)
- [`AstdocsStartEndBlockProcessor`](#markdown_astdocsastdocsstartendblockprocessor)
- [`AstdocsExtension`](#markdown_astdocsastdocsextension)

## Functions

### `markdown_astdocs.percent_source`

```python
percent_source(path: str, lineno: int, lineno_end: int) -> str:
```

Read code from source file and substitute the associated `%%%SOURCE ...` marker.

**Parameters:**

- `path` \[`str`\]: Path to the source file to extract code.
- `lineno` \[`int`\]: Beginning of the code block. Defaults to `None`.
- `lineno_end` \[`int`\]: End of the code block. Defaults to `None`.

**Returns:**

- \[`str`\]: HTML replacement.

**Notes:**

Line numbers are expected to start at 1.

### `markdown_astdocs.percent_start`

```python
percent_start() -> str:
```

Substitute a `%%%START ...` marker.

**Returns:**

- \[`str`\]: HTML replacement.

### `markdown_astdocs.percent_end`

```python
percent_end() -> str:
```

Substitute a `%%%END ...` marker.

**Returns:**

- \[`str`\]: HTML replacement.

## Classes

### `markdown_astdocs.AstdocsSourcePreprocessor`

Catch and replace the `%%%SOURCE ...` markers.

**Methods:**

- [`run()`](#markdown_astdocsastdocssourcepreprocessorrun)

#### Constructor

```python
AstdocsSourcePreprocessor(md: Markdown, path: str)
```

All methods inherited, but the `run()` one below.

**Parameters:**

- `md` \[`markdown.core.Markdown`\]: Internal `Markdown` object to process.
- `path` \[`str`\]: Extra path prefix to add when fishing for the source.

**Attributes:**

- `path` \[`str`\]: Path prefix.

#### Methods

##### `markdown_astdocs.AstdocsSourcePreprocessor.run`

```python
run(lines: typing.List[str]) -> typing.List[str]:
```

Overwritten method to process the input `Markdown` lines.

**Paramaters:**

- `lines` \[`typing.List[str]`\]: `Markdown` content (split by `\n`).

**Returns:**

- \[`typing.List[str]`\]: Same list of lines, processed.

### `markdown_astdocs.AstdocsStartEndBlockProcessor`

Process `%%%START ...` to `%%%END ...` blocks.

**Methods:**

- [`test()`](#markdown_astdocsastdocsstartendblockprocessortest)
- [`run()`](#markdown_astdocsastdocsstartendblockprocessorrun)

#### Constructor

```python
AstdocsStartEndBlockProcessor(parser)
```

All methods inherited, but the `test()` and `run()` ones below.

**Parameters:**

- \[`parser`\]: Parser of the `Markdown` object to process.

#### Methods

##### `markdown_astdocs.AstdocsStartEndBlockProcessor.test`

```python
test(parent: Element, block: str) -> re.Match:
```

Check if the `run()` method should be called to process the block.

**Parameters:**

- `parent` \[`xml.etree.ElementTree.Element`\]: Parent element that will host the tree
  of the current block, once rendered.
- `block` \[`str`\]: Current block to process.

**Returns:**

- \[`re.Match`\]: Match object if pattern is found, `None` otherwise.

##### `markdown_astdocs.AstdocsStartEndBlockProcessor.run`

```python
run(parent: Element, blocks: typing.List[str]) -> None:
```

Bound the block within the remaining blocks and render it.

**Parameters:**

- `parent` \[`xml.etree.ElementTree.Element`\]: Parent element that will host the tree
  of the current block, once rendered.
- `blocks` \[`typing.List[str]`\]: List of the remaining lines to process.

### `markdown_astdocs.AstdocsExtension`

Extension to be imported when calling for the renderer.

**Methods:**

- [`extendMarkdown()`](#markdown_astdocsastdocsextensionextendmarkdown)

#### Constructor

```python
AstdocsExtension(**kwargs)
```

Make the extension configurable.

**Parameters:**

- `path` \[`str`\]: Extra path prefix to add when fishing for the source. Defaults to
  `.`.

**Notes:**

We want to take care of the `%%%` markers as early as possible to avoid any HTML noise
around them, hence the high priority.

#### Methods

##### `markdown_astdocs.AstdocsExtension.extendMarkdown`

```python
extendMarkdown(md: Markdown):
```

Overwritten method to process the content.

**Parameters:**

- `md` \[`markdown.core.Markdown`\]: Internal `Markdown` object to process.

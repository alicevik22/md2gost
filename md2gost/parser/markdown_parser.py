import logging
import os
from collections.abc import Generator

from docx import Document
from marko.block import BlankLine, Paragraph, CodeBlock, FencedCode, \
    BlockElement
from marko.inline import Image
from uuid import uuid4

from md2gost.extended_markdown import markdown, Caption
from md2gost.renderable.caption import CaptionInfo
from md2gost.renderable.renderable import Renderable
from md2gost.renderable_factory import RenderableFactory

from .parser import Parser


class MarkdownParser(Parser):
    """Parses given markdown string and returns Renderable elements"""

    def __init__(self, document: Document):
        self._document = document
        self._factory = RenderableFactory(self._document._body)

    @staticmethod
    def resolve_paths(marko_element: BlockElement, relative_dir_path: str):
        """Resolves relative paths in Marko elements"""
        if isinstance(marko_element, Paragraph):
            for child in marko_element.children:
                if isinstance(child, Image) and\
                        not child.dest.startswith("http"):
                    child.dest = os.path.join(
                        relative_dir_path, os.path.expanduser(child.dest))
        if isinstance(marko_element, (CodeBlock, FencedCode))\
                and marko_element.extra:
            path = os.path.abspath(os.path.expanduser(os.path.join(
                relative_dir_path, marko_element.extra.strip())))

            try:
                with open(path, encoding="utf-8") as f:
                    marko_element.children[0].children += \
                        f.read()
            except FileNotFoundError:
                logging.warning(
                    f"Файл с кодом не найден: {path}")

    def parse(self, text, relative_dir_path: str)\
            -> Generator[Renderable, None, None]:
        marko_parsed = markdown.parse(text)
        caption_info = CaptionInfo(uuid4().hex, None)
        for marko_element in marko_parsed.children:
            self.resolve_paths(marko_element, relative_dir_path)

            if isinstance(marko_element, BlankLine):
                continue

            if isinstance(marko_element, Caption):
                caption_info =\
                    CaptionInfo(marko_element.unique_name, marko_element.text)
                continue

            yield from self._factory.create(marko_element, caption_info)
            caption_info = CaptionInfo(uuid4().hex, None)

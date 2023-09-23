import logging
import os.path
import sys

import docx
from docx.document import Document
from docx.shared import Cm

from .debugger import Debugger
from .layout_tracker import LayoutTracker
from .numberer import NumberingPreProcessor
from .parser import ParserFactory
from .renderable import Renderable
from .title_appender import DocumentMerger
from .toc_processor import TocPreProcessor, TocPostProcessor
from .renderer import Renderer

BOTTOM_MARGIN = Cm(1.86)


class Converter:
    """Converts markdown file to docx file"""

    def __init__(self, input_paths: list[str], output_path: str,
                 template_path: str = None, title_path: str | None = None, title_pages: int = 1, debug: bool = False):
        self._output_path = output_path
        self._document: Document = docx.Document(template_path)
        self._pages_offset = 0
        self._document._body.clear_content()
        self._debugger = Debugger(self._document) if debug else None
        self._renderables: list[Renderable] = []
        parser_factory = ParserFactory()
        for path in input_paths:
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            except FileNotFoundError:
                print(f"Файл {path} не найден!")
                exit(-3)

            extension = path.split(".")[-1]
            parser = parser_factory.create_by_extension(
                extension, self._document)
            if not parser:
                logging.critical(f"Формат входных файлов {extension} не поддерживается")
                sys.exit(-1)

            self._renderables += list(parser.parse(text, os.path.dirname(path)))

        max_height = self._document.sections[-1].page_height - self._document.sections[0] \
            .top_margin - BOTTOM_MARGIN  # - ((136 / 2) * (Pt(1)*72/96))  # todo add bottom margin detection with footer
        max_width = self._document.sections[-1].page_width - self._document.sections[-1].left_margin \
            - self._document.sections[-1].right_margin

        self._layout_tracker = LayoutTracker(max_height, max_width)

        if title_path:
            title_document: Document = docx.Document(title_path)
            self._pages_offset = title_pages
            merger = DocumentMerger(self._document)
            merger.append(title_document, title_pages)

    def convert(self):
        processors = [
            TocPreProcessor(),
            NumberingPreProcessor(),
            Renderer(self._document, self._layout_tracker, self._debugger),
            TocPostProcessor(self._pages_offset),
        ]

        for processor in processors:
            processor.process(self._renderables)

    @property
    def document(self) -> Document:
        return self._document

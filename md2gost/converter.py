import logging
import os.path
import sys
from io import BytesIO

import docx
from docx.document import Document
from docx.oxml import CT_P, CT_Tbl, CT_Blip
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.styles.style import _ParagraphStyle
from docx.text.paragraph import Paragraph

from .debugger import Debugger
from .layout_tracker import LayoutTracker
from .numberer import NumberingPreProcessor
from md2gost.parser.markdown_parser import MarkdownParser
from .parser import ParserFactory
from .renderable import Renderable
from .toc_processor import TocPreProcessor, TocPostProcessor
from .renderer import Renderer
from .util import merge_objects

BOTTOM_MARGIN = Cm(1.86)


class Converter:
    """Converts markdown file to docx file"""

    def __init__(self, input_paths: list[str], output_path: str,
                 template_path: str = None, title_path: str | None = None, title_pages: int = 1, debug: bool = False):
        self._output_path = output_path
        self._title_document: Document = docx.Document(title_path)
        self._title_pages = title_pages if title_path else 0
        self._document: Document = docx.Document(template_path)
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
            self.append_title()

    def append_title(self):
        # copy element styles to element
        default_style_element = type("DefaultStyle", (), {})
        default_style_element.rPr = \
            self._document.styles.element.xpath(
                'w:docDefaults/w:rPrDefault/w:rPr')[0]
        default_style_element.pPr = \
            self._document.part.document.styles.element.xpath(
                'w:docDefaults/w:pPrDefault/w:pPr')[0]
        default_style = _ParagraphStyle(default_style_element)

        for element in self._title_document._body._element.iter():
            if isinstance(element, CT_P):
                p = Paragraph(element, self._title_document._body)
                styles = [p.style]
                while styles[-1].base_style:
                    styles.append(styles[-1].base_style)
                styles.append(default_style)
                pf = merge_objects(*[style.paragraph_format for style in styles][::-1], p.paragraph_format)
                for attr, value in pf.__dict__.items():
                    try:
                        p.paragraph_format.__setattr__(attr, value if value is not None else 0)
                    except AttributeError:
                        pass
            elif isinstance(element, CT_Blip):
                r_id = element.attrib[qn("r:embed")]
                image_blob = BytesIO(self._title_document.part.related_parts[r_id].image.blob)
                r_id, _ = self._document.part.get_or_add_image(image_blob)
                element.set(qn("r:embed"), r_id)

        # copy elements from title to document
        self._document.add_section().is_linked_to_previous = True  # todo: copy footer

        self._document.sections[1].page_width = self._document.sections[0].page_width
        self._document.sections[1].page_height = self._document.sections[0].page_height
        self._document.sections[1].left_margin = self._document.sections[0].left_margin
        self._document.sections[1].top_margin = self._document.sections[0].top_margin
        self._document.sections[1].right_margin = self._document.sections[0].right_margin
        self._document.sections[1].bottom_margin = self._document.sections[0].bottom_margin

        self._document.sections[0].page_width = self._title_document.sections[0].page_width
        self._document.sections[0].page_height = self._title_document.sections[0].page_height
        self._document.sections[0].left_margin = self._title_document.sections[0].left_margin
        self._document.sections[0].top_margin = self._title_document.sections[0].top_margin
        self._document.sections[0].right_margin = self._title_document.sections[0].right_margin
        self._document.sections[0].bottom_margin = self._title_document.sections[0].bottom_margin


        i = 0
        for element in self._title_document._body._element.getchildren():
            if isinstance(element, (CT_P,  CT_Tbl)):
                self.document._body._element.insert(i, element)
                i += 1

        self._document.sections[-1].footer.is_linked_to_previous = False
        self._document._body._element.xpath("w:sectPr/w:pgNumType")[0].set(qn("w:start"), str(self._title_pages+1))

    def convert(self):
        processors = [
            TocPreProcessor(),
            NumberingPreProcessor(),
            Renderer(self._document, self._layout_tracker, self._debugger),
            TocPostProcessor(self._title_pages),
        ]

        for processor in processors:
            processor.process(self._renderables)

    @property
    def document(self) -> Document:
        return self._document

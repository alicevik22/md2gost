from copy import copy

import docx
from docx.document import Document
from docx.oxml import CT_P, CT_Tbl, CT_SectPr
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.text.paragraph import Paragraph

from .debugger import Debugger
from .layout_tracker import LayoutTracker
from .numberer import NumberingPreProcessor
from .parser_ import Parser
from .toc_processor import TocPreProcessor, TocPostProcessor
from .renderer import Renderer
from .util import merge_objects

BOTTOM_MARGIN = Cm(1.86)


class Converter:
    """Converts markdown file to docx file"""

    def __init__(self, input_path: str, output_path: str,
                 template_path: str = None, title_path: str | None = None, debug: bool = False):
        self._output_path = output_path
        self._title_document: Document = docx.Document(title_path)
        self._document: Document = docx.Document(template_path)
        self._document._body.clear_content()
        self._debugger = Debugger(self._document) if debug else None
        with open(input_path, encoding="utf-8") as f:
            self.parser = Parser(self._document, f.read())

        max_height = self._document.sections[-1].page_height - self._document.sections[
            0].top_margin - BOTTOM_MARGIN  # - ((136 / 2) * (Pt(1)*72/96))  # todo add bottom margin detection with footer
        max_width = self._document.sections[-1].page_width - self._document.sections[-1].left_margin \
                    - self._document.sections[-1].right_margin

        self._layout_tracker = LayoutTracker(max_height, max_width)

        if title_path:
            self.append_title()

    def append_title(self):
        # copy element styles to element
        for element in self._title_document._body._element.iter():
            if isinstance(element, CT_P):
                p = Paragraph(element, self._title_document._body)
                styles = [p.style]
                while styles[-1].base_style:
                    styles.append(styles[-1].base_style)
                pf = merge_objects(*[style.paragraph_format for style in styles][::-1], p.paragraph_format)
                for attr, value in pf.__dict__.items():
                    try:
                        p.paragraph_format.__setattr__(attr, value if value is not None else 0)
                    except AttributeError:
                        pass

        # copy elements from title to document
        title_sect = self._document.add_section()
        title_sect.page_width = self._title_document.sections[0].page_width
        title_sect.page_height = self._title_document.sections[0].page_height
        title_sect.left_margin = self._title_document.sections[0].left_margin
        title_sect.top_margin = self._title_document.sections[0].top_margin
        title_sect.right_margin = self._title_document.sections[0].right_margin
        title_sect.bottom_margin = self._title_document.sections[0].bottom_margin

        title_sect.is_linked_to_previous = True  # todo: copy footer
        i = 0
        for element in self._title_document._body._element.getchildren():
            if isinstance(element, (CT_P,  CT_Tbl)):
                self.document._body._element.insert(i, element)
                i += 1

        self._document.sections[-1].footer.is_linked_to_previous = False
        self._document._body._element.xpath("w:sectPr/w:pgNumType")[0].set(qn("w:start"), "2")

    def convert(self):
        renderables = list(self.parser.parse())

        processors = [
            TocPreProcessor(),
            NumberingPreProcessor(),
            Renderer(self._document, self._layout_tracker, self._debugger),
            TocPostProcessor(),
        ]

        for processor in processors:
            processor.process(renderables)

    @property
    def document(self) -> Document:
        return self._document

from copy import copy
from dataclasses import dataclass
from typing import Generator
from uuid import uuid4

from docx.shared import Parented, Cm
from docx.text.paragraph import Paragraph as DocxParagraph
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.table import Table

from md2gost.layout_tracker import LayoutState
from md2gost.renderable import Renderable
from md2gost.rendered_info import RenderedInfo
from .paragraph_sizer import ParagraphSizer
from ..util import create_element


@dataclass
class CaptionInfo:
    unique_name: str
    text: str | None


class Caption(Renderable):
    def __init__(self, parent: Parented, category: str, caption_info: CaptionInfo | None,
                 number: int = None, before=True):
        self._parent = parent
        self._before = before
        self._docx_paragraph = DocxParagraph(create_element("w:p"), parent)

        uid = uuid4().hex

        self._docx_paragraph.style = "Caption"
        self._docx_paragraph.add_run(f"{category} ")
        if caption_info and caption_info.unique_name:
            self._docx_paragraph._p.append(create_element("w:bookmarkStart", {
                "w:id": uid,
                "w:name": caption_info.unique_name
            }))
        self._numbering_run = create_element("w:r", str(number) if number else "?")
        self._docx_paragraph._p.append(create_element("w:fldSimple", {
                    "w:instr": f"SEQ {category} \\* ARABIC"
                }, [self._numbering_run]))
        if caption_info and caption_info.unique_name:
            self._docx_paragraph._p.append(create_element("w:bookmarkEnd", {
                "w:id": uid
            }))
        if caption_info and caption_info.text:
            self._docx_paragraph.add_run(f" - {caption_info.text}")

    def center(self):
        self._docx_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    def render(self, previous_rendered: RenderedInfo, layout_state: LayoutState) -> Generator[
            "RenderedInfo | Renderable", None, None]:
        if previous_rendered and isinstance(previous_rendered.docx_element, Table) \
                and not (layout_state.current_page_height == 0 and layout_state.page != 1):
            self._docx_paragraph.paragraph_format.space_before = Cm(0.45)
        else:
            self._docx_paragraph.paragraph_format.space_before = None

        height_data = ParagraphSizer(
            self._docx_paragraph,
            previous_rendered.docx_element
            if previous_rendered and isinstance(previous_rendered.docx_element, DocxParagraph) else None,
            layout_state.max_width
        ).calculate_height()

        # if three more lines don't fit, move it to the next page (so there is no only caption on the end of the page)
        if self._before and ((height_data.lines + 3 - 1) * height_data.line_spacing + 1) * height_data.line_height \
                > layout_state.remaining_page_height:
            self._docx_paragraph.paragraph_format.page_break_before = True
            self._docx_paragraph.paragraph_format.space_before = None
            height_data = ParagraphSizer(
                self._docx_paragraph,
                None,
                layout_state.max_width
            ).calculate_height()

        yield RenderedInfo(
            self._docx_paragraph,
            height_data.full +
            (layout_state.remaining_page_height
                if self._docx_paragraph.paragraph_format.page_break_before else 0))

from typing import TYPE_CHECKING

from docx.document import Document
from docx.shared import Length, Cm, Parented, Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from .renderable import Renderable
from .util import create_element
from .layout_tracker import LayoutTracker

if TYPE_CHECKING:
    from .debugger import Debugger


class Renderer:
    """Renders Renderable elements to docx file"""

    def __init__(self, document: Document, layout_tracker: LayoutTracker, debugger: "Debugger | None" = None):
        self._document: Document = document
        self._debugger = debugger
        self._layout_tracker = layout_tracker

        # add page numbering to the footer
        paragraph = self._document.sections[-1].footer.paragraphs[0]
        paragraph.paragraph_format.first_line_indent = 0
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        paragraph._p.append(create_element("w:fldSimple", {
            "w:instr": "PAGE \\* MERGEFORMAT"
        }))

        self.previous_rendered = None

    def process(self, renderables: list[Renderable]):
        for i in range(len(renderables)):
            self.render(renderables[i])

        if self._debugger:
            self._debugger.after_rendered()

    def render(self, renderable: Renderable, flush=True):
        infos = renderable.render(self.previous_rendered, self._layout_tracker.current_state)

        for info in infos:
            if isinstance(info, Renderable):
                raise NotImplementedError()
            else:
                self._add(info.docx_element, info.height)
                self.previous_rendered = info

    def _add(self, element: Parented, height: Length):
        self._document._body._element.append(
            element._element
        )
        self._layout_tracker.add_height(height)

        if self._debugger:
            self._debugger.add(element, height)

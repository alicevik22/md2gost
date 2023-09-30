from dataclasses import dataclass
from functools import cached_property
from uniseg.linebreak import line_break_units

from docx.enum.text import WD_LINE_SPACING
from docx.oxml import CT_R
from docx.text.run import Run
from freetype import Face

from docx.text.paragraph import Paragraph
from docx.text.font import Font as DocxFont
from docx.shared import Length, Pt, Inches
from docx.text.parfmt import ParagraphFormat
from docx.styles.style import _ParagraphStyle

from PIL import Image, ImageDraw, ImageFont

from .find_font import find_font
from ..util import merge_objects


class Font:
    def __init__(self, name: str, bold: bool, italic: bool, size_pt: int):
        path = find_font(name, bold, italic)
        self._freetypefont = ImageFont.truetype(path, size_pt)
        self._draw = ImageDraw.Draw(Image.new("RGB", (1000, 1000)))

        self._face = Face(path)
        self._face.set_char_size(int(size_pt * 64))

    def get_text_width(self, text: str) -> Length:
        if not self.is_mono:
            bbox = self._draw.textbbox((0, 0), text, self._freetypefont)
            return Pt(bbox[2] - bbox[0])
        else:
            return Pt(len(text) * self._face.glyph.advance.x / 64)

    def get_line_height(self) -> Length:
        # TODO: make it work for all fonts
        # if "Times" in str(self._face.family_name) and self._freetypefont.size == 14:
        #     return Pt(16.05)
        if "Courier" in str(self._face.family_name) and self._freetypefont.size == 12:
            return Pt(13.62)
        # else:
        return Pt(self._face.size.height / 64)

    @cached_property
    def is_mono(self):
        self._face.load_char("i")
        i_width = self._face.glyph.advance.x
        self._face.load_char("m")
        return i_width == self._face.glyph.advance.x
        # return self._face.glyph.bitmap.width



@dataclass
class ParagraphSizerResult:
    before: Length
    lines: int
    line_height: Length
    line_spacing: float
    after: Length

    @property
    def base(self) -> Length:
        return self.before + ((self.lines - 1) * self.line_spacing + 1) * self.line_height

    @property
    def full(self) -> Length:
        return Length(self.before + self.line_height * self.line_spacing * self.lines + self.after)


class ParagraphSizer:
    def __init__(self, paragraph: Paragraph, previous_paragraph: Paragraph | None, 
                 max_width: Length, tabs_size: Length = 0):  # todo: remove tabs_size and resolve tabs here
        self.previous_paragraph = previous_paragraph
        self.max_width = max_width
        self.paragraph = paragraph
        self._tabs_size = tabs_size

        self.same_style_as_previous = (paragraph.style == previous_paragraph.style) if previous_paragraph else False

        # Load properties
        self.docx_font: DocxFont = merge_objects(
            *[style.font for style in self._styles[::-1] if style.font],
            self.paragraph.style.font)

        self.paragraph_format: ParagraphFormat = merge_objects(
            *[style.paragraph_format for style in self._styles[::-1]
              if style.paragraph_format],
            self.paragraph.paragraph_format
        )

        self.font = Font(self.docx_font.name, self.docx_font.bold, self.docx_font.italic, self.docx_font.size.pt)

        # here self.paragraph.runs is not used because it does not always return
        # all runs (e.g. if they are inside hyperlink)
        self.runs = []
        for element in self.paragraph._element.getiterator():
            if isinstance(element, CT_R):
                self.runs.append(Run(element, self.paragraph))

        self.max_width -= (self.paragraph_format.left_indent or 0) + \
            (self.paragraph_format.right_indent or 0)


    @cached_property
    def _default_style(self):

        default_style_element = type("DefaultStyle", (), {})
        default_style_element.rPr = \
            self.paragraph.part.document.styles.element.xpath(
                'w:docDefaults/w:rPrDefault/w:rPr')[0]
        default_style_element.pPr = \
            self.paragraph.part.document.styles.element.xpath(
                'w:docDefaults/w:pPrDefault/w:pPr')[0]
        default_style = _ParagraphStyle(default_style_element)
        return default_style

    @cached_property
    def _styles(self) -> list[_ParagraphStyle]:
        styles = [self.paragraph.style]
        while styles[-1].base_style:
            styles.append(styles[-1].base_style)
        styles.append(self._default_style)
        return styles

    @cached_property
    def _is_contextual_spacing(self) -> bool:
        contextual_spacing = False
        pPrs = [self.paragraph.paragraph_format._element.pPr] + \
               [style._element.pPr for style in self._styles]
        for pPr in pPrs:
            if pPr.xpath("./w:contextualSpacing"):
                contextual_spacing = True
                break
        return contextual_spacing

    def get_text_width(self, start: int, end: int):
        width = 0
        pos = 0
        for i, run in enumerate(self.runs):
            if pos > end:
                return width
            run_font_size = run.font.size.pt if run.font.size else None
            font = Font(
                run.font.name or self.docx_font.name,
                run.font.bold or self.docx_font.bold,
                run.font.italic or self.docx_font.italic,
                run_font_size or self.docx_font.size.pt)
            if pos + len(run.text) >= start:
                width += font.get_text_width(run.text[max(0, start-pos):end-pos])
            pos += len(run.text)
        return width

    def split_lines(self):
        space_width = self.font.get_text_width(" ")
        if not self.font.is_mono:
            space_width *= 0.83

        text = "".join([run.text for run in self.runs])

        def tailor(s, breakables):
            breakables = list(breakables)
            for i in range(1, len(s)-1):
                if s[i] in ("/", ):
                    if s[i-1] == " ":
                        breakables[i] = 1
                    breakables[i+1] = 0
                if s[i] in ("$",) and s[i-1] not in {" ", "-", "—", "–"}:
                    breakables[i] = 0
            return breakables

        line_width = self.paragraph_format.first_line_indent or 0
        lines = [""]
        pos = 0
        for unit in line_break_units(text, tailor=tailor):
            spaces = len(unit) - len(unit.rstrip())
            no_spaces_width = self.get_text_width(pos, pos+len(unit)-spaces)
            full_width = no_spaces_width + spaces*space_width
            if no_spaces_width <= self.max_width - line_width:
                line_width += full_width
                lines[-1] += unit
            elif no_spaces_width > self.max_width:
                if lines[-1] == "":
                    lines.pop(-1)
                i = 0
                for j in range(len(unit)+1):
                    part_width = self.get_text_width(pos+i, pos+j)
                    if not self.font.is_mono:
                        part_width *= 1.001  # word compresses characters
                        # to fit one more character into the line
                    if part_width > (self.max_width if len(lines) != 0 else self.max_width-(self.paragraph_format.first_line_indent or 0)):
                        lines.append(unit[i:j-1])
                        i = j-1
                lines.append(unit[i:])
                line_width = self.font.get_text_width(unit[i:])
            else:
                lines.append(unit)
                line_width = full_width
            pos += len(unit)

        return [line.rstrip() for line in lines]

    def calculate_height(self) -> ParagraphSizerResult:
        lines = len(self.split_lines())

        previous_paragraph_format: ParagraphFormat = None
        if self.previous_paragraph:
            previous_paragraph_styles = [self.previous_paragraph.style]
            while previous_paragraph_styles[-1].base_style:
                previous_paragraph_styles.append(
                    previous_paragraph_styles[-1].base_style
                )
            previous_paragraph_styles.append(self._default_style)
            previous_paragraph_format = merge_objects(
                *[style.paragraph_format for style in previous_paragraph_styles[::-1]
                    if style.paragraph_format],
                self.previous_paragraph.paragraph_format
            )

        if self._is_contextual_spacing and self.same_style_as_previous:
            before = (previous_paragraph_format.space_after or 0)
        else:
            before = (self.paragraph_format.space_before or 0)
            if previous_paragraph_format:
                before = max(0, before - (previous_paragraph_format.space_after or 0))

        after = (self.paragraph_format.space_after or 0)

        line_height = self.font.get_line_height()
        line_spacing = self.paragraph_format.line_spacing
        if self.paragraph_format.line_spacing_rule == WD_LINE_SPACING.EXACTLY:
            line_spacing /= line_height
            # raise NotImplementedError("Line spacing rule AT_LEAST is not supported")
        elif self.paragraph_format.line_spacing_rule == WD_LINE_SPACING.AT_LEAST:
            raise NotImplementedError("Line spacing rule AT_LEAST is not supported")

        return ParagraphSizerResult(before, lines, line_height, line_spacing, after)

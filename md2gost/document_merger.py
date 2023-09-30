from io import BytesIO

from docx.document import Document
from docx.oxml.ns import qn
from docx.oxml import CT_P, CT_Tbl, CT_Blip
from docx.styles.style import _ParagraphStyle
from docx.text.paragraph import Paragraph

from md2gost.util import merge_objects


class DocumentMerger:
    def __init__(self, target_document: Document):
        self._document = target_document

    def append(self, other_document: Document, pages: int = None):
        # copy element styles to element
        default_style_element = type("DefaultStyle", (), {})
        default_style_element.rPr = \
            self._document.styles.element.xpath(
                'w:docDefaults/w:rPrDefault/w:rPr')[0]
        default_style_element.pPr = \
            self._document.part.document.styles.element.xpath(
                'w:docDefaults/w:pPrDefault/w:pPr')[0]
        default_style = _ParagraphStyle(default_style_element)

        for element in other_document._body._element.iter():
            if isinstance(element, CT_P):
                p = Paragraph(element, other_document._body)
                styles = [p.style]
                while styles[-1].base_style:
                    styles.append(styles[-1].base_style)
                styles.append(default_style)
                pf = merge_objects(
                    *[style.paragraph_format for style in styles][::-1],
                    p.paragraph_format)
                for attr, value in pf.__dict__.items():
                    try:
                        p.paragraph_format.__setattr__(
                            attr, value if value is not None else 0)
                    except AttributeError:
                        pass
            elif isinstance(element, CT_Blip):
                r_id = element.attrib[qn("r:embed")]
                image_blob = BytesIO(
                    other_document.part.related_parts[r_id].image.blob)
                r_id, _ = self._document.part.get_or_add_image(image_blob)
                element.set(qn("r:embed"), r_id)

        # copy elements from title to document
        self._document.add_section().is_linked_to_previous = True

        # todo: copy footer

        self._document.sections[1].page_width =\
            self._document.sections[0].page_width
        self._document.sections[1].page_height =\
            self._document.sections[0].page_height
        self._document.sections[1].left_margin =\
            self._document.sections[0].left_margin
        self._document.sections[1].top_margin =\
            self._document.sections[0].top_margin
        self._document.sections[1].right_margin =\
            self._document.sections[0].right_margin
        self._document.sections[1].bottom_margin =\
            self._document.sections[0].bottom_margin

        self._document.sections[0].page_width =\
            other_document.sections[0].page_width
        self._document.sections[0].page_height =\
            other_document.sections[0].page_height
        self._document.sections[0].left_margin =\
            other_document.sections[0].left_margin
        self._document.sections[0].top_margin =\
            other_document.sections[0].top_margin
        self._document.sections[0].right_margin =\
            other_document.sections[0].right_margin
        self._document.sections[0].bottom_margin =\
            other_document.sections[0].bottom_margin

        i = 0
        for element in other_document._body._element.getchildren():
            if isinstance(element, (CT_P, CT_Tbl)):
                self._document._body._element.insert(i, element)
                i += 1

        self._document.sections[-1].footer.is_linked_to_previous = False

        if pages:
            self._document._body._element.xpath("w:sectPr/w:pgNumType")[0].set(
                qn("w:start"), str(pages + 1))

import unittest

from md2gost.renderable.paragraph_sizer import Font, ParagraphSizer
from md2gost.renderable.listing import LISTING_OFFSET

from . import _create_test_document, _EMUS_PER_PX

delta = 10 / 29


class TestFont(unittest.case.TestCase):
    def test_get_text_width(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertAlmostEqual(37.5,
                               font.get_text_width("hello") / _EMUS_PER_PX,
                               delta=delta)

    def test_get_text_width_short(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertAlmostEqual(15, font.get_text_width("in") / _EMUS_PER_PX,
                               delta=delta)

    def test_get_text_width_long(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertAlmostEqual(245, font.get_text_width(
            "Электроэнцефалографический") / _EMUS_PER_PX, delta=delta)

    def test_get_text_width_bold(self):
        font = Font("Times New Roman", True, False, 14)
        self.assertAlmostEqual(39, font.get_text_width("hello") / _EMUS_PER_PX,
                               delta=delta)

    def test_get_text_width_italic(self):
        font = Font("Times New Roman", False, True, 14)
        self.assertAlmostEqual(37.5,
                               font.get_text_width("hello") / _EMUS_PER_PX,
                               delta=delta)

    def test_get_text_width_bold_italic(self):
        font = Font("Times New Roman", True, True, 14)
        self.assertAlmostEqual(38.5,
                               font.get_text_width("hello") / _EMUS_PER_PX,
                               delta=delta)

    def test_get_line_height_times(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertAlmostEqual(21.4, font.get_line_height() / _EMUS_PER_PX,
                               delta=delta)

    def test_get_line_height_times_large(self):
        font = Font("Times New Roman", False, False, 50)
        self.assertAlmostEqual(77, font.get_line_height() / _EMUS_PER_PX,
                               delta=delta)

    def test_get_line_height_calibri(self):
        font = Font("Calibri", False, False, 14)
        self.assertAlmostEqual(23, font.get_line_height() / _EMUS_PER_PX,
                               delta=delta)

    def test_get_line_height_consolas(self):
        font = Font("Consolas", False, False, 20)
        self.assertAlmostEqual(31, font.get_line_height() / _EMUS_PER_PX,
                               delta=delta)

    def test_get_line_height_courier(self):
        font = Font("Courier New", False, False, 12)
        self.assertAlmostEqual(18.3, font.get_line_height() / _EMUS_PER_PX,
                               delta=delta)

    def test_is_mono_courier(self):
        font = Font("Courier New", False, False, 12)
        self.assertTrue(font.is_mono)

    def test_is_mono_times(self):
        font = Font("Times New Roman", False, False, 12)
        self.assertFalse(font.is_mono)


class TestParagraphSizer(unittest.TestCase):
    def setUp(self):
        self._document, self._max_height, self._max_width = _create_test_document()

    def test_count_lines1(self):
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam lacinia fringilla lectus, nec euismod odio convallis sed. Nunc ac libero ultricies, condimentum neque et, fermentum urna. Donec feugiat diam sed nulla rutrum, sit amet accumsan odio tempor. Sed fermentum urna. Donec feugiat diam sed nulla rutrum, sit amet accumsan odio tempor. Sed mattis. In porta convallis ipsum eget dignissim. Ut orci ante, bibendum ut lorem quis, gravida molestie neque. Nulla vitae sapien sed risus gravida elementum non eu lorem. Quisque ac turpis nisl."
        expected = [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam lacinia fringilla",
            "lectus, nec euismod odio convallis sed. Nunc ac libero ultricies, condimentum neque et,",
            "fermentum urna. Donec feugiat diam sed nulla rutrum, sit amet accumsan odio tempor.",
            "Sed fermentum urna. Donec feugiat diam sed nulla rutrum, sit amet accumsan odio",
            "tempor. Sed mattis. In porta convallis ipsum eget dignissim. Ut orci ante, bibendum ut",
            "lorem quis, gravida molestie neque. Nulla vitae sapien sed risus gravida elementum non",
            "eu lorem. Quisque ac turpis nisl."
        ]

        paragraph = self._document.add_paragraph()
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines2(self):
        text = "Ordered lists are useful when you want to present items in a specific order. This is additional text for illustration. Ordered lists are useful when you want to present items in a specific order. This is additional text for illustration. Ordered lists are useful when you want to present items in a specific order. This is additional text for illustration."
        expected = [
            "Ordered lists are useful when you want to present items in a specific order. This is",
            "additional text for illustration. Ordered lists are useful when you want to present items",
            "in a specific order. This is additional text for illustration. Ordered lists are useful when",
            "you want to present items in a specific order. This is additional text for illustration."
        ]

        paragraph = self._document.add_paragraph()
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines3(self):
        text = "OpenAI is a leading artificial intelligence research organization, known for advancements in language models like GPT. Click the link to learn more. Hello world a b"
        expected = [
            "OpenAI is a leading artificial intelligence research organization, known for",
            "advancements in language models like GPT. Click the link to learn more. Hello world a",
            "b"
        ]

        paragraph = self._document.add_paragraph()
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines4(self):
        text = "Markdown supports rendering mathematical formulas using LaTeX syntax. This allows you to include complex equations and mathematical notation in your documents."
        expected = [
            "Markdown supports rendering mathematical formulas using LaTeX syntax. This",
            "allows you to include complex equations and mathematical notation in your documents."
        ]

        paragraph = self._document.add_paragraph()
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines5(self):
        text = "verylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongword"
        expected = [
            "verylongwordverylongwordverylongwordverylongwordverylongwordverylongwo",
            "rdverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordv",
            "erylongword"
        ]

        paragraph = self._document.add_paragraph()
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines6(self):
        text = "someword verylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylongword"
        expected = [
            "someword",
            "verylongwordverylongwordverylongwordverylongwordverylongwordverylongwordver",
            "ylongwordverylongwordverylongwordverylongwordverylongwordverylongwordverylo",
            "ngword"
        ]

        paragraph = self._document.add_paragraph()
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing1(self):
        text = "            table._cells[0]._element.append(paragraph_rendered_info.docx_element._element)"
        expected = [
            "",
            "table._cells[0]._element.append(paragraph_rendered_info.docx_element",
            "._element)",
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing2(self):
        text = "                continuation_paragraph = Paragraph(self.parent)"
        expected = [
            "                continuation_paragraph = Paragraph(self.parent)",
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing3(self):
        text = "ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"
        expected = [
            "oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
            "o"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing4(self):
        text = "    def add_link(self, text: str, url: str, is_bold: bool = None, is_italic: bool = None):"
        expected = [
            "    def add_link(self, text: str, url: str, is_bold: bool = None,",
            "is_italic: bool = None):"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing5(self):
        text = "                self._docx_paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY"
        expected = [
            "",
            "self._docx_paragraph.paragraph_format.line_spacing_rule =",
            "WD_LINE_SPACING.EXACTLY"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing6(self):
        text = """            #         and "Heading" in previous_rendered.docx_element.style.name\\"""
        expected = [
            """            #         and "Heading" in""",
            "previous_rendered.docx_element.style.name\\",
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing7(self):
        text = """        run = DocxRun(create_element("w:r"), self._docx_paragraph)"""
        expected = [
            """        run = DocxRun(create_element("w:r"), self._docx_paragraph)"""
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing8(self):
        text = """            #         and ((min(2, height_data.lines) - 1) * height_data.line_spacing + 1) * height_data.line_height\\"""
        expected = [
            """            #         and ((min(2, height_data.lines) - 1) *""",
            """height_data.line_spacing + 1) * height_data.line_height\\"""
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing9(self):
        text = "        return self._docx_paragraph.paragraph_format.first_line_indent"
        expected = [
            "        return",
            "self._docx_paragraph.paragraph_format.first_line_indent"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing10(self):
        text = "01-01 12:00:29.121  3642  3664 W Looper  : Slow dispatch took 696ms android.fg h=android.os.Handler c=com.android.server.am.-$$Lambda$UserController$o6oQFjGYYIfx-I94cSakTLPLt6s@78bae1c m=0"
        expected = [
            "01-01 12:00:29.121  3642  3664 W Looper  : Slow dispatch took 696ms",
            "android.fg h=android.os.Handler c=com.android.server.am.-",
            "$$Lambda$UserController$o6oQFjGYYIfx-I94cSakTLPLt6s@78bae1c m=0"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing11(self):
        text = "        return self._docx_paragraph.paragraph_format.first_line_indent"
        expected = [
            "        return",
            "self._docx_paragraph.paragraph_format.first_line_indent"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing12(self):
        text = "        self._docx_paragraph.paragraph_format.first_line_indent = value"
        expected = [
            "        self._docx_paragraph.paragraph_format.first_line_indent =",
            "value"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing13(self):
        text = "                if previous_rendered and isinstance(previous_rendered.docx_element, DocxParagraph) else None,"
        expected = [
            "                if previous_rendered and",
            "isinstance(previous_rendered.docx_element, DocxParagraph) else None,"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing14(self):
        text = '        System.out.printf("Square: %f%n", circle.calculateSquare());'
        expected = [
            '        System.out.printf("Square: %f%n", circle.calculateSquare());'
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing15(self):
        text = '        System.out.printf("circle radius: %f%n", circle.getRadius());'
        expected = [
            '        System.out.printf("circle radius: %f%n",',
            'circle.getRadius());'
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing16(self):
        text = "01-01 12:00:31.238  3642  3659 I ActivityManager: Start proc 4414:com.google.android.deskclock/u0a13 for broadcast com.google.android.deskclock/com.android.deskclock.AlarmInitReceiver"
        expected = [
            "01-01 12:00:31.238  3642  3659 I ActivityManager: Start proc",
            "4414:com.google.android.deskclock/u0a13 for broadcast",
            "com.google.android.deskclock/com.android.deskclock.AlarmInitReceiver"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing17(self):
        text = "01-01 12:03:22.019  3642  3819 W BroadcastQueue: Background execution not allowed: receiving Intent { act=android.intent.action.DROPBOX_ENTRY_ADDED flg=0x10 (has extras) } to com.google.android.gms/.stats.service.DropBoxEntryAddedReceiver"
        expected = [
            "01-01 12:03:22.019  3642  3819 W BroadcastQueue: Background",
            "execution not allowed: receiving Intent",
            "{ act=android.intent.action.DROPBOX_ENTRY_ADDED flg=0x10 (has",
            "extras) } to",
            "com.google.android.gms/.stats.service.DropBoxEntryAddedReceiver"
        ]

        paragraph = self._document.add_paragraph(style="Code")
        paragraph.add_run(text)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

    def test_count_lines_listing18(self):
        runs = ['', '        ', 'run', ' ', '=', ' ', 'DocxRun', '(',
                'create_element', '(', '"', 'w:r', '"', ')', ',', ' ',
                'self', '.', '_docx_paragraph', ')']
        expected = [
            '        run = DocxRun(create_element("w:r"), self._docx_paragraph)'
        ]

        paragraph = self._document.add_paragraph(style="Code")
        for run in runs:
            paragraph.add_run(run)
        ps = ParagraphSizer(paragraph, None, self._max_width - LISTING_OFFSET)

        self.assertEqual(expected, ps.split_lines())

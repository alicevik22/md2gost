import unittest

from md2gost.renderable.paragraph_sizer import Font, ParagraphSizer
from md2gost.renderable.listing import LISTING_OFFSET

from . import _create_test_document, _EMUS_PER_PX

delta = 10/29


class TestFont(unittest.case.TestCase):
    def test_get_text_width(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertAlmostEqual(37.5, font.get_text_width("hello") / _EMUS_PER_PX, delta=delta)

    def test_get_text_width_short(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertAlmostEqual(15, font.get_text_width("in") / _EMUS_PER_PX, delta=delta)

    def test_get_text_width_long(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertAlmostEqual(245, font.get_text_width("Электроэнцефалографический") / _EMUS_PER_PX, delta=delta)

    def test_get_text_width_bold(self):
        font = Font("Times New Roman", True, False, 14)
        self.assertAlmostEqual(39, font.get_text_width("hello") / _EMUS_PER_PX, delta=delta)

    def test_get_text_width_italic(self):
        font = Font("Times New Roman", False, True, 14)
        self.assertAlmostEqual(37.5, font.get_text_width("hello") / _EMUS_PER_PX, delta=delta)

    def test_get_text_width_bold_italic(self):
        font = Font("Times New Roman", True, True, 14)
        self.assertAlmostEqual(38.5, font.get_text_width("hello") / _EMUS_PER_PX, delta=delta)

    def test_get_line_height_times(self):
        font = Font("Times New Roman", False, False, 14)
        self.assertAlmostEqual(21.4, font.get_line_height() / _EMUS_PER_PX, delta=delta)

    def test_get_line_height_times_large(self):
        font = Font("Times New Roman", False, False, 50)
        self.assertAlmostEqual(77, font.get_line_height() / _EMUS_PER_PX, delta=delta)

    def test_get_line_height_calibri(self):
        font = Font("Calibri", False, False, 14)
        self.assertAlmostEqual(23, font.get_line_height() / _EMUS_PER_PX, delta=delta)

    def test_get_line_height_consolas(self):
        font = Font("Consolas", False, False, 20)
        self.assertAlmostEqual(31, font.get_line_height() / _EMUS_PER_PX, delta=delta)

    def test_get_line_height_courier(self):
        font = Font("Courier New", False, False, 12)
        self.assertAlmostEqual(18.3, font.get_line_height() / _EMUS_PER_PX, delta=delta)

    def test_is_mono_courier(self):
        font = Font("Courier New", False, False, 12)
        self.assertTrue(font.is_mono)

    def test_is_mono_times(self):
        font = Font("Times New Roman", False, False, 12)
        self.assertFalse(font.is_mono)


class TestParagraphSizer(unittest.TestCase):
    def setUp(self):
        self._document, self._max_height, self._max_width = _create_test_document()

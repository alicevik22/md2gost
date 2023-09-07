import logging
from collections import defaultdict

from md2gost.renderable import Renderable, Paragraph
from md2gost.renderable.requires_numbering import RequiresNumbering


class NumberingPreProcessor:
    def __init__(self):
        self._categories: dict[str, int] = defaultdict(lambda: 0)
        self._reference_data: dict[str, int] = dict()

    def process(self, renderables: list[Renderable]):
        for requires_numbering in filter(lambda x: isinstance(x, RequiresNumbering), renderables):
            requires_numbering.set_number(self._categories[requires_numbering.numbering_category] + 1)
            self._categories[requires_numbering.numbering_category] += 1
            if requires_numbering.numbering_unique_name in self._reference_data:
                logging.warning(f"Дублирование названия подписи: {requires_numbering.numbering_unique_name}. Ссылки будут созданы некорректно")
            self._reference_data[requires_numbering.numbering_unique_name] =\
                self._categories[requires_numbering.numbering_category]

        for paragraph in filter(lambda x: isinstance(x, Paragraph), renderables):
            for reference in paragraph.references:
                if reference.unique_name in self._reference_data:
                    reference.set_number(self._reference_data[reference.unique_name])
                else:
                    logging.warning(f"Неверная ссылка: {reference.unique_name} не существует")

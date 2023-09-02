from collections import defaultdict

from md2gost.renderable import Renderable
from md2gost.renderable.requires_numbering import RequiresNumbering


class NumberingPreProcessor:
    def __init__(self):
        self.categories: dict[str, list[str]] = defaultdict(lambda: [])

    def process(self, renderables: list[Renderable]):
        requires_numberings = filter(lambda x: isinstance(x, RequiresNumbering), renderables)

        for requires_numberings in requires_numberings:
            requires_numberings.set_number(len(self.categories[requires_numberings.numbering_category]) + 1)
            self.categories[requires_numberings.numbering_category].append("unique name")

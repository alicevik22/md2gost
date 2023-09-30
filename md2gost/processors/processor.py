from abc import ABC, abstractmethod

from md2gost.renderable import Renderable


class Processor(ABC):
    @abstractmethod
    def process(self, renderables: list[Renderable]):
        pass

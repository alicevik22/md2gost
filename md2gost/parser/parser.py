from abc import ABC, abstractmethod
from typing import Generator

from md2gost.renderable import Renderable


class Parser:
    @abstractmethod
    def parse(self, text: str, relative_dir_path: str)\
            -> Generator[Renderable, None, None]:
        """Parses provided text"""

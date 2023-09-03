from abc import ABC, abstractmethod


class RequiresNumbering:
    def __init__(self, category: str, unique_name: str):
        self.numbering_category = category
        self.numbering_unique_name = unique_name

    @abstractmethod
    def set_number(self, number: int):
        pass

from marko.inline import InlineElement
from re import Match


class Reference(InlineElement):
    """Represents Reference element

    Syntax: @Type:label"""

    pattern = r"\@(\w+)"

    def __init__(self, match: Match[str]):
        self.unique_name = match.group(1)

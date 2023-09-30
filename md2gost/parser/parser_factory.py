from docx import Document

from .parser import Parser
from .markdown_parser import MarkdownParser

class ParserFactory:
    def create_by_extension(self, extension: str, document: Document)\
            -> Parser | None:
        """Creates suitable parser for file based on its extension.
        Returns None if there is no parser for the extension."""

        if extension in ("md", "markdown"):
            return MarkdownParser(document)

        return None

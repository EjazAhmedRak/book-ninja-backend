from pydantic import BaseModel
from typing import Literal


class ParsedQuery(BaseModel):
    """Structured output of the parse_query tool."""
    title:  str | None = None
    genre:  str | None = None
    year:   str | None = None
    author: str | None = None
    intent: Literal["search", "purchase", "ebook", "audiobook"] | None = None
    format: Literal["ebook", "audiobook"] | None = None

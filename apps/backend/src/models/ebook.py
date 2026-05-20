from pydantic import BaseModel
from typing import Literal


class EbookLink(BaseModel):
    """A download link for an ebook file."""
    source: str  # e.g. "Anna's Archive"
    format: Literal["epub", "mobi"]
    url:    str


class EbookQuery(BaseModel):
    """Input for the find_ebook_link tool."""
    title:      str
    author:     str
    year:       str | None = None
    mirror_url: str  # current Anna's Archive URL from search_current_mirror

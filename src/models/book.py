from pydantic import BaseModel


class BookResult(BaseModel):
    """A single book returned by the Search Books tool."""
    title:         str
    author:        str
    year:          str | None = None
    summary:       str
    hardcover_url: str
    rating:        float = 0.0

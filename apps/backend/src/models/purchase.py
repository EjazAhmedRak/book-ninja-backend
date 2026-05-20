from pydantic import BaseModel


class PurchaseLink(BaseModel):
    """A single purchase option for an ebook or audiobook."""
    store: str
    url:   str


class PurchaseQuery(BaseModel):
    """Input for the find_purchase_links tool."""
    title:  str
    author: str
    year:   str | None = None
    format: str  # 'ebook' or 'audiobook'

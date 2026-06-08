from pydantic import BaseModel

from models.audiobook import AudiobookLink
from models.book import BookResult
from models.ebook import EbookLink
from models.purchase import PurchaseLink
from models.query import ParsedQuery


class AgentState(BaseModel):
    """Shared state passed between all nodes in the LangGraph agent."""
    prompt:       str
    user_id:      str
    thread_id:    str
    parsed_query: ParsedQuery | None     = None
    intent:       str | None             = None
    books:        list[BookResult]       = []
    links:        list[PurchaseLink]     = []
    ebook_links:  list[EbookLink]        = []
    audio_links:  list[AudiobookLink]    = []
    mirror_url:   str | None             = None
    output:       str | None             = None

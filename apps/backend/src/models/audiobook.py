from pydantic import BaseModel


class AudiobookLink(BaseModel):
    """A download link for an audiobook."""
    source: str  # e.g. "AudiobookBay"
    title:  str
    url:    str


class AudiobookQuery(BaseModel):
    """Input for the find_audiobook_link tool."""
    title:      str
    author:     str
    mirror_url: str  # current AudiobookBay URL from search_current_mirror

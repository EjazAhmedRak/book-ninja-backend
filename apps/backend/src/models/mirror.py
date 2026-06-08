from typing import Literal

from pydantic import BaseModel


class MirrorQuery(BaseModel):
    """Input for the search_current_mirror tool."""
    source: Literal["annas_archive", "audiobookbay"]


class MirrorResult(BaseModel):
    """Output of the search_current_mirror tool."""
    source: str
    url:    str  # current working mirror URL

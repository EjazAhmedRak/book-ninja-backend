from pydantic import BaseModel
from typing import Literal


class MirrorQuery(BaseModel):
    """Input for the search_current_mirror tool."""
    source: Literal["annas_archive", "audiobookbay"]


class MirrorResult(BaseModel):
    """Output of the search_current_mirror tool."""
    source: str
    url:    str  # current working mirror URL

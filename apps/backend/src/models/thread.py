from datetime import datetime

from pydantic import BaseModel


class ThreadRecord(BaseModel):
    """A single thread entry shown in the sidebar."""
    thread_id: str
    preview:   str       # first 100 characters of the opening user message
    timestamp: datetime


class ThreadsResponse(BaseModel):
    """Response body for /latestThreads."""
    threads: list[ThreadRecord]

from collections.abc import AsyncIterator
from typing import Any


async def collect_stream(stream: AsyncIterator[Any]) -> Any:
    """
    Collects an async stream into a single result.

    For chunked LangChain messages, chunks are combined via `+`.
    For non-chunked outputs (e.g. structured models), the latest chunk is returned.
    """
    chunks: list[Any] = []
    async for chunk in stream:
        chunks.append(chunk)

    if not chunks:
        raise ValueError("LLM stream produced no chunks")

    if len(chunks) == 1:
        return chunks[0]

    combined = chunks[0]
    for chunk in chunks[1:]:
        try:
            combined = combined + chunk
        except TypeError:
            combined = chunk
    return combined

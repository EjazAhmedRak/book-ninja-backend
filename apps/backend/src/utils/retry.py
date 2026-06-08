import httpx
from tenacity import retry, retry_if_exception_type, stop_after_delay, wait_exponential


@retry(
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    stop=stop_after_delay(30),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
async def call_with_retry(fn, *args, **kwargs):
    """Wraps an async callable with exponential backoff (1s→10s, max 30s total)."""
    return await fn(*args, **kwargs)

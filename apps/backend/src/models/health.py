from typing import Literal

from pydantic import BaseModel

IntegrationStatus = Literal["ok", "degraded", "unavailable"]


class HealthResponse(BaseModel):
    """Response body for /health."""
    status:       Literal["ok", "degraded"]
    integrations: dict[str, IntegrationStatus]
    # Keys: hardcover, mongodb, tavily, langsmith

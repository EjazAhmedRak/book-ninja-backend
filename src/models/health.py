from pydantic import BaseModel
from typing import Literal

IntegrationStatus = Literal["ok", "degraded", "unavailable"]


class HealthResponse(BaseModel):
    """Response body for /health."""
    status:       Literal["ok", "degraded"]
    integrations: dict[str, IntegrationStatus]
    # Keys: hardcover, mongodb, tavily, langsmith

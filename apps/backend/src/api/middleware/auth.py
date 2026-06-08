import asyncio

from fastapi import Header, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel

from config import APP_ENV, GOOGLE_CLIENT_ID


class GoogleUser(BaseModel):
    """Decoded Google ID token payload fields used by the app."""
    sub:   str   # Google user ID — used as user_id throughout the app
    email: str


async def validate_google_token(
    authorization: str | None = Header(default=None),
    x_debug_email: str | None = Header(default=None),
) -> GoogleUser:
    """
    Validates the Bearer token from the Authorization header.
    Returns a typed GoogleUser. Raises 401 if the token is invalid or expired.

    In dev/qa environments, passing X-Debug-Email skips Google token validation
    and uses the provided email as both the user email and sub (user ID).
    """
    if APP_ENV != "prod" and x_debug_email:
        return GoogleUser(sub=x_debug_email, email=x_debug_email)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format.")
    token = authorization.split(" ")[1]
    try:
        # id_token.verify_oauth2_token is synchronous — wrap to avoid blocking the event loop
        payload = await asyncio.to_thread(
            id_token.verify_oauth2_token,
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
        return GoogleUser(sub=payload["sub"], email=payload["email"])
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.middleware.auth import GoogleUser, validate_google_token
from db.mongo import save_user
from models.user import UserRecord

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)


class AuthMeResponse(BaseModel):
    sub: str
    email: str


@router.get(
    "/me",
    response_model=AuthMeResponse,
    summary="Verify current Google session",
    response_description="Authenticated Google user",
)
async def auth_me(user: GoogleUser = Depends(validate_google_token)):
    """Return the authenticated Google user associated with the bearer token."""
    try:
        await save_user(UserRecord(email=user.email, google_id=user.sub))
    except Exception:
        logger.exception("Unable to persist authenticated user during /auth/me")
        raise HTTPException(status_code=503, detail="Unable to create or update user session.")
    return AuthMeResponse(sub=user.sub, email=user.email)

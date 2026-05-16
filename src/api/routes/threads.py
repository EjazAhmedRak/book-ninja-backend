from fastapi import APIRouter, Depends
from api.middleware.auth import validate_google_token, GoogleUser
from models.thread import ThreadsResponse
from db.mongo import get_latest_threads

router = APIRouter()


@router.get("/latestThreads", response_model=ThreadsResponse)
async def latest_threads(user: GoogleUser = Depends(validate_google_token)):
    """Returns the 5 most recent threads for the authenticated user."""
    threads = await get_latest_threads(user_id=user.sub, limit=5)
    return ThreadsResponse(threads=threads)

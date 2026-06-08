from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URI
from models.thread import ThreadRecord
from models.user import UserRecord

client      = AsyncIOMotorClient(MONGO_URI)
db          = client["book_ninja"]
users_col   = db["users"]
threads_col = db["threads"]


async def ping_mongo() -> bool:
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False


async def save_user(user: UserRecord) -> None:
    """Upsert user by google_id — safe to call on every authenticated request."""
    await users_col.update_one(
        {"google_id": user.google_id},
        {"$set": user.model_dump()},
        upsert=True
    )


async def save_thread(user_id: str, thread_id: str, prompt: str) -> None:
    """Upsert a thread record. Preview and thread_id are set only on insert; timestamp is always refreshed."""
    preview = prompt[:100]
    await threads_col.update_one(
        {"thread_id": thread_id},
        {
            "$set": {"user_id": user_id, "timestamp": datetime.now(UTC)},
            "$setOnInsert": {"thread_id": thread_id, "preview": preview},
        },
        upsert=True,
    )


async def get_latest_threads(user_id: str, limit: int = 5) -> list[ThreadRecord]:
    cursor = threads_col.find(
        {"user_id": user_id},
        {"_id": 0, "thread_id": 1, "preview": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(limit)
    raw = await cursor.to_list(length=limit)
    return [ThreadRecord(**r) for r in raw]

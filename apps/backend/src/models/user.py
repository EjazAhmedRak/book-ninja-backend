from pydantic import BaseModel, EmailStr


class UserRecord(BaseModel):
    """A user stored in MongoDB."""
    email:     EmailStr
    google_id: str

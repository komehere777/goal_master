from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class ProgressLogBase(BaseModel):
    log_type: Literal["progress", "milestone", "setback", "note"]
    value: Optional[float] = None
    description: str
    mood_score: Optional[int] = Field(None, ge=1, le=10)


class ProgressLogCreate(ProgressLogBase):
    goal_id: str


class ProgressLogUpdate(BaseModel):
    log_type: Optional[Literal["progress", "milestone", "setback", "note"]] = None
    value: Optional[float] = None
    description: Optional[str] = None
    mood_score: Optional[int] = Field(None, ge=1, le=10)


class ProgressLogInDB(ProgressLogBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    goal_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class ProgressLog(ProgressLogBase):
    id: str
    user_id: str
    goal_id: str
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True
    ) 
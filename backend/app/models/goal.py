from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class AIAnalysis(BaseModel):
    difficulty_score: float = Field(ge=0, le=10)
    estimated_duration: int  # days
    success_probability: float = Field(ge=0, le=1)


class GoalBase(BaseModel):
    title: str
    description: str
    category: Literal["health", "education", "career", "personal", "finance"]
    target_value: float
    current_value: float = 0
    unit: str
    deadline: datetime
    priority: Literal["high", "medium", "low"] = "medium"


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Literal["health", "education", "career", "personal", "finance"]] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    unit: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[Literal["high", "medium", "low"]] = None
    status: Optional[Literal["active", "completed", "paused", "cancelled"]] = None


class GoalInDB(GoalBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    status: Literal["active", "completed", "paused", "cancelled"] = "active"
    ai_analysis: Optional[AIAnalysis] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class Goal(GoalBase):
    id: str
    user_id: str
    status: Literal["active", "completed", "paused", "cancelled"]
    ai_analysis: Optional[AIAnalysis] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True
    ) 
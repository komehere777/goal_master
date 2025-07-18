from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class ActionStep(BaseModel):
    step_number: int
    title: str
    description: str
    estimated_time: int  # minutes
    is_completed: bool = False
    completed_at: Optional[datetime] = None


class ActionPlanBase(BaseModel):
    title: str
    description: str
    steps: List[ActionStep] = Field(default_factory=list)


class ActionPlanCreate(ActionPlanBase):
    goal_id: str


class ActionPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[ActionStep]] = None


class ActionPlanInDB(ActionPlanBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    goal_id: PyObjectId
    user_id: PyObjectId
    ai_generated: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class ActionPlan(ActionPlanBase):
    id: str
    goal_id: str
    user_id: str
    ai_generated: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True
    ) 
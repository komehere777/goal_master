from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Annotated
from datetime import datetime

from app.models.progress import ProgressLogCreate, ProgressLogUpdate, ProgressLog, ProgressLogInDB
from app.models.user import User
from app.routers.auth import get_current_user
from app.core.database import get_database

router = APIRouter()


@router.get("/goal/{goal_id}", response_model=List[ProgressLog])
async def get_progress_logs(
    goal_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
):
    """특정 목표의 진도 기록을 조회합니다."""
    logs_cursor = db.progress_logs.find({
        "goal_id": goal_id,
        "user_id": str(current_user.id)
    }).sort("created_at", -1)
    
    logs = []
    async for log_doc in logs_cursor:
        logs.append(ProgressLog(
            id=str(log_doc["_id"]),
            user_id=str(log_doc["user_id"]),
            goal_id=str(log_doc["goal_id"]),
            log_type=log_doc["log_type"],
            value=log_doc.get("value"),
            description=log_doc["description"],
            mood_score=log_doc.get("mood_score"),
            created_at=log_doc["created_at"]
        ))
    
    return logs


@router.post("/", response_model=ProgressLog)
async def create_progress_log(
    progress_data: ProgressLogCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
):
    """새 진도 기록을 생성합니다."""
    # 목표 존재 확인
    goal_doc = await db.goals.find_one({
        "_id": ObjectId(progress_data.goal_id),
        "user_id": str(current_user.id)
    })
    
    if not goal_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목표를 찾을 수 없습니다."
        )
    
    # 진도 기록 생성
    progress_in_db = ProgressLogInDB(
        user_id=str(current_user.id),
        goal_id=progress_data.goal_id,
        log_type=progress_data.log_type,
        value=progress_data.value,
        description=progress_data.description,
        mood_score=progress_data.mood_score
    )
    
    result = await db.progress_logs.insert_one(progress_in_db.dict(by_alias=True))
    
    # 목표의 current_value 업데이트 (progress 타입인 경우)
    if progress_data.log_type == "progress" and progress_data.value is not None:
        await db.goals.update_one(
            {"_id": ObjectId(progress_data.goal_id)},
            {"$set": {"current_value": progress_data.value, "updated_at": datetime.utcnow()}}
        )
    
    # 생성된 기록 조회
    log_doc = await db.progress_logs.find_one({"_id": result.inserted_id})
    
    return ProgressLog(
        id=str(log_doc["_id"]),
        user_id=str(log_doc["user_id"]),
        goal_id=str(log_doc["goal_id"]),
        log_type=log_doc["log_type"],
        value=log_doc.get("value"),
        description=log_doc["description"],
        mood_score=log_doc.get("mood_score"),
        created_at=log_doc["created_at"]
    ) 
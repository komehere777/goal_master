from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Dict, Any

from app.models.user import User
from app.routers.auth import get_current_user
from app.core.database import get_database

router = APIRouter()


@router.get("/users/similar-goals")
async def find_similar_users(
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> List[Dict[str, Any]]:
    """유사한 목표를 가진 사용자를 찾습니다."""
    # 현재 사용자의 활성 목표 조회
    user_goals = []
    async for goal in db.goals.find({
        "user_id": ObjectId(current_user.id),
        "status": "active"
    }):
        user_goals.append(goal)
    
    if not user_goals:
        return []
    
    # 유사한 카테고리의 목표를 가진 다른 사용자 찾기
    categories = [goal["category"] for goal in user_goals]
    
    similar_users = []
    async for goal in db.goals.find({
        "category": {"$in": categories},
        "status": "active",
        "user_id": {"$ne": ObjectId(current_user.id)}
    }).limit(10):
        # 사용자 정보 조회
        user_doc = await db.users.find_one({"_id": goal["user_id"]})
        if user_doc:
            similar_users.append({
                "user_id": str(user_doc["_id"]),
                "name": user_doc["profile"]["name"],
                "avatar_url": user_doc["profile"].get("avatar_url"),
                "goal_title": goal["title"],
                "goal_category": goal["category"]
            })
    
    return similar_users


@router.get("/posts")
async def get_community_posts(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> List[Dict[str, Any]]:
    """커뮤니티 게시글을 조회합니다."""
    # 간단한 더미 데이터 반환
    return [
        {
            "id": "1",
            "title": "다이어트 목표 달성 팁 공유",
            "content": "3개월 동안 10kg 감량에 성공했습니다!",
            "author": "건강한사람",
            "category": "health",
            "created_at": "2024-01-15T10:00:00"
        }
    ] 
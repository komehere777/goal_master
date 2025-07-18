from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional, Dict, Any, Annotated
from datetime import datetime

from app.models.goal import GoalCreate, GoalUpdate, Goal, GoalInDB
from app.models.user import User, PyObjectId
from app.routers.auth import get_current_user
from app.core.database import get_database

router = APIRouter()


@router.get("/", response_model=List[Goal])
async def get_goals(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
    status: Optional[str] = Query(None, description="목표 상태 필터"),
    category: Optional[str] = Query(None, description="카테고리 필터")
):
    """사용자의 목표 목록을 조회합니다."""
    print("--------------------------------")
    print(f"목표 조회 요청 - 사용자 ID: {current_user.id}")
    print(f"필터 조건 - status: {status}, category: {category}")
    
    # user_id를 문자열로 검색 (저장할 때 문자열로 저장되므로)
    user_id_str = str(current_user.id)
    filter_query: Dict[str, Any] = {"user_id": user_id_str}
    
    if status:
        filter_query["status"] = status
    if category:
        filter_query["category"] = category
    
    print(f"MongoDB 쿼리: {filter_query}")
    
    # 전체 목표 수 확인
    total_goals = await db.goals.count_documents({})
    user_goals_count_str = await db.goals.count_documents({"user_id": user_id_str})
    user_goals_count_obj = await db.goals.count_documents({"user_id": ObjectId(current_user.id)})
    print(f"데이터베이스 전체 목표 수: {total_goals}")
    print(f"현재 사용자 목표 수 (문자열 검색): {user_goals_count_str}")
    print(f"현재 사용자 목표 수 (ObjectId 검색): {user_goals_count_obj}")
    
    goals_cursor = db.goals.find(filter_query).sort("created_at", -1)
    goals = []
    
    async for goal_doc in goals_cursor:
        goals.append(Goal(
            id=str(goal_doc["_id"]),
            user_id=str(goal_doc["user_id"]),
            title=goal_doc["title"],
            description=goal_doc["description"],
            category=goal_doc["category"],
            target_value=goal_doc["target_value"],
            current_value=goal_doc["current_value"],
            unit=goal_doc["unit"],
            deadline=goal_doc["deadline"],
            priority=goal_doc["priority"],
            status=goal_doc["status"],
            ai_analysis=goal_doc.get("ai_analysis"),
            created_at=goal_doc["created_at"],
            updated_at=goal_doc["updated_at"]
        ))
    
    print(f"최종 반환할 목표 수: {len(goals)}")
    return goals


@router.get("/debug/all")
async def get_all_goals_debug(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)]
):
    """디버깅용: 모든 목표 조회"""
    print(f"디버깅: 현재 사용자 ID: {current_user.id}, 타입: {type(current_user.id)}")
    
    all_goals_cursor = db.goals.find({})
    all_goals = []
    async for goal_doc in all_goals_cursor:
        all_goals.append({
            "_id": str(goal_doc["_id"]),
            "user_id": str(goal_doc["user_id"]),
            "user_id_type": str(type(goal_doc["user_id"])),
            "title": goal_doc["title"],
            "created_at": goal_doc["created_at"]
        })
    
    print(f"데이터베이스의 모든 목표: {all_goals}")
    return {"current_user_id": str(current_user.id), "all_goals": all_goals}


@router.post("/", response_model=Goal)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """새 목표를 생성합니다."""
    print(f"목표 생성 요청 - 사용자 ID: {current_user.id}")
    print(f"목표 데이터: {goal_data}")
    
    # user_id를 문자열로 확실히 변환한 후 PyObjectId로 생성
    user_id_str = str(current_user.id)
    print(f"사용자 ID 문자열: {user_id_str}")
    
    goal_in_db = GoalInDB(
        user_id=PyObjectId(user_id_str),
        title=goal_data.title,
        description=goal_data.description,
        category=goal_data.category,
        target_value=goal_data.target_value,
        current_value=goal_data.current_value,
        unit=goal_data.unit,
        deadline=goal_data.deadline,
        priority=goal_data.priority
    )
    
    goal_dict = goal_in_db.dict(by_alias=True)
    print(f"데이터베이스 저장용 데이터: {goal_dict}")
    print(f"저장할 user_id 타입: {type(goal_dict.get('user_id'))}")
    print(f"저장할 user_id 값: {goal_dict.get('user_id')}")
    
    result = await db.goals.insert_one(goal_dict)
    print(f"MongoDB 삽입 결과 ID: {result.inserted_id}")
    
    # 방금 생성된 목표를 바로 조회해서 확인
    created_goal = await db.goals.find_one({"_id": result.inserted_id})
    print(f"생성된 목표의 user_id: {created_goal.get('user_id')}")
    print(f"생성된 목표의 user_id 타입: {type(created_goal.get('user_id'))}")
    
    # 생성된 목표 조회
    goal_doc = await db.goals.find_one({"_id": result.inserted_id})
    
    return Goal(
        id=str(goal_doc["_id"]),
        user_id=str(goal_doc["user_id"]),
        title=goal_doc["title"],
        description=goal_doc["description"],
        category=goal_doc["category"],
        target_value=goal_doc["target_value"],
        current_value=goal_doc["current_value"],
        unit=goal_doc["unit"],
        deadline=goal_doc["deadline"],
        priority=goal_doc["priority"],
        status=goal_doc["status"],
        ai_analysis=goal_doc.get("ai_analysis"),
        created_at=goal_doc["created_at"],
        updated_at=goal_doc["updated_at"]
    )


@router.get("/{goal_id}", response_model=Goal)
async def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """특정 목표를 조회합니다."""
    goal_doc = await db.goals.find_one({
        "_id": ObjectId(goal_id),
        "user_id": str(current_user.id)
    })
    
    if not goal_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목표를 찾을 수 없습니다."
        )
    
    return Goal(
        id=str(goal_doc["_id"]),
        user_id=str(goal_doc["user_id"]),
        title=goal_doc["title"],
        description=goal_doc["description"],
        category=goal_doc["category"],
        target_value=goal_doc["target_value"],
        current_value=goal_doc["current_value"],
        unit=goal_doc["unit"],
        deadline=goal_doc["deadline"],
        priority=goal_doc["priority"],
        status=goal_doc["status"],
        ai_analysis=goal_doc.get("ai_analysis"),
        created_at=goal_doc["created_at"],
        updated_at=goal_doc["updated_at"]
    )


@router.put("/{goal_id}", response_model=Goal)
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """목표를 수정합니다."""
    print(f"목표 수정 요청 - goal_id: {goal_id}, user_id: {current_user.id}")
    print(f"수정 데이터: {goal_update}")
    
    # 먼저 목표가 존재하는지 확인
    goal_with_objectid = await db.goals.find_one({"_id": ObjectId(goal_id)})
    goal_with_string = await db.goals.find_one({"_id": goal_id})
    
    print(f"ObjectId로 검색한 목표: {goal_with_objectid is not None}")
    print(f"문자열로 검색한 목표: {goal_with_string is not None}")
    
    if goal_with_objectid:
        print(f"ObjectId로 찾은 목표의 user_id: {goal_with_objectid.get('user_id')}, 타입: {type(goal_with_objectid.get('user_id'))}")
    if goal_with_string:
        print(f"문자열로 찾은 목표의 user_id: {goal_with_string.get('user_id')}, 타입: {type(goal_with_string.get('user_id'))}")
    
    # 기존 목표 확인 - ObjectId 방식 시도
    existing_goal = await db.goals.find_one({
        "_id": ObjectId(goal_id),
        "user_id": str(current_user.id)
    })
    
    # ObjectId 방식으로 찾지 못했다면 문자열 방식 시도
    if not existing_goal:
        existing_goal = await db.goals.find_one({
            "_id": goal_id,
            "user_id": str(current_user.id)
        })
        print(f"문자열 방식으로 찾은 목표: {existing_goal is not None}")
    
    if not existing_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목표를 찾을 수 없습니다."
        )
    
    # 업데이트할 필드만 추출
    update_data = goal_update.dict(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        # 문자열 _id로 업데이트 시도
        result = await db.goals.update_one(
            {"_id": goal_id},
            {"$set": update_data}
        )
        
        # 문자열 방식으로 업데이트되지 않았다면 ObjectId 방식 시도
        if result.modified_count == 0:
            await db.goals.update_one(
                {"_id": ObjectId(goal_id)},
                {"$set": update_data}
            )
        
        print(f"업데이트 결과: {result.modified_count}개 수정됨")
    
    # 업데이트된 목표 조회 - 문자열 방식 먼저 시도
    goal_doc = await db.goals.find_one({"_id": goal_id})
    
    # 문자열 방식으로 찾지 못했다면 ObjectId 방식 시도
    if not goal_doc:
        goal_doc = await db.goals.find_one({"_id": ObjectId(goal_id)})
        
    print(f"업데이트 후 목표 재조회 성공: {goal_doc is not None}")
    
    return Goal(
        id=str(goal_doc["_id"]),
        user_id=str(goal_doc["user_id"]),
        title=goal_doc["title"],
        description=goal_doc["description"],
        category=goal_doc["category"],
        target_value=goal_doc["target_value"],
        current_value=goal_doc["current_value"],
        unit=goal_doc["unit"],
        deadline=goal_doc["deadline"],
        priority=goal_doc["priority"],
        status=goal_doc["status"],
        ai_analysis=goal_doc.get("ai_analysis"),
        created_at=goal_doc["created_at"],
        updated_at=goal_doc["updated_at"]
    )


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """목표를 삭제합니다."""
    print(f"목표 삭제 요청 - goal_id: {goal_id}, user_id: {current_user.id}")
    
    # 먼저 목표가 존재하는지 확인
    goal_with_objectid = await db.goals.find_one({"_id": ObjectId(goal_id)})
    goal_with_string = await db.goals.find_one({"_id": goal_id})
    
    print(f"ObjectId로 검색한 목표: {goal_with_objectid is not None}")
    print(f"문자열로 검색한 목표: {goal_with_string is not None}")
    
    if goal_with_objectid:
        print(f"ObjectId로 찾은 목표의 user_id: {goal_with_objectid.get('user_id')}, 타입: {type(goal_with_objectid.get('user_id'))}")
    if goal_with_string:
        print(f"문자열로 찾은 목표의 user_id: {goal_with_string.get('user_id')}, 타입: {type(goal_with_string.get('user_id'))}")
    
    # 삭제 시도 - ObjectId 방식
    result_objectid = await db.goals.delete_one({
        "_id": ObjectId(goal_id),
        "user_id": str(current_user.id)
    })
    
    # 삭제 시도 - 문자열 방식  
    result_string = await db.goals.delete_one({
        "_id": goal_id,
        "user_id": str(current_user.id)
    })
    
    print(f"ObjectId 삭제 결과: {result_objectid.deleted_count}")
    print(f"문자열 삭제 결과: {result_string.deleted_count}")
    
    total_deleted = result_objectid.deleted_count + result_string.deleted_count
    
    if total_deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목표를 찾을 수 없습니다."
        )
    
    return {"message": "목표가 삭제되었습니다."} 
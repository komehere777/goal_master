from fastapi import APIRouter, Depends, HTTPException, status, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import Dict, Any
import openai

from app.models.user import User
from app.routers.auth import get_current_user
from app.core.database import get_database
from app.core.config import settings

router = APIRouter()

# OpenAI 클라이언트 설정
openai.api_key = settings.OPENAI_API_KEY


@router.post("/get-coaching")
async def get_coaching_message_post(
    goal_id: str = Query(..., description="목표 ID"),
    message_type: str = Query("daily", description="메시지 타입"),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Dict[str, Any]:
    """개인화된 코칭 메시지를 생성합니다."""
    # 목표 조회 - 문자열 방식 먼저 시도
    goal_doc = await db.goals.find_one({
        "_id": goal_id,
        "user_id": str(current_user.id)
    })
    
    # 문자열 방식으로 찾지 못했다면 ObjectId 방식 시도
    if not goal_doc:
        try:
            goal_doc = await db.goals.find_one({
                "_id": ObjectId(goal_id),
                "user_id": str(current_user.id)
            })
        except:
            pass
    
    if not goal_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목표를 찾을 수 없습니다."
        )
    
    # 최근 진도 기록 조회
    recent_progress = []
    async for log in db.progress_logs.find({
        "goal_id": goal_id,
        "user_id": str(current_user.id)
    }).sort("created_at", -1).limit(5):
        recent_progress.append(log)
    
    # 코칭 메시지 생성 프롬프트
    progress_rate = (goal_doc['current_value'] / goal_doc['target_value']) * 100
    
    prompt = f"""
    다음 사용자에게 {message_type} 코칭 메시지를 작성해주세요:
    
    목표: {goal_doc['title']}
    진도율: {progress_rate:.1f}%
    현재값: {goal_doc['current_value']} {goal_doc['unit']}
    목표값: {goal_doc['target_value']} {goal_doc['unit']}
    마감일: {goal_doc['deadline']}
    
    최근 활동이 있다면 이를 참고하여 격려하고, 구체적인 다음 단계를 제안해주세요.
    따뜻하고 동기부여가 되는 톤으로 작성해주세요.
    """
    
    try:
        # OpenAI API 대신 임시 메시지 생성 (개발용)
        coaching_messages = [
            f"안녕하세요! '{goal_doc['title']}' 목표에 대한 현재 진도율이 {progress_rate:.1f}%입니다. 꾸준히 잘 하고 계시네요! 💪",
            f"목표 달성을 위해 오늘도 한 걸음씩 나아가고 계시는군요! {goal_doc['title']} 목표까지 {goal_doc['target_value'] - goal_doc['current_value']:.1f}{goal_doc['unit']} 남았습니다.",
            f"훌륭합니다! 현재 {progress_rate:.1f}% 달성하셨어요. 이 속도라면 목표 달성이 충분히 가능할 것 같습니다! 🎯",
            f"매일 조금씩이라도 진전을 보이는 것이 중요해요. {goal_doc['title']} 목표를 향해 꾸준히 노력하고 계시는 모습이 보기 좋습니다! ✨"
        ]
        
        import random
        coaching_message = random.choice(coaching_messages)
        
        # AI 상호작용 기록 저장
        await db.ai_interactions.insert_one({
            "user_id": str(current_user.id),
            "goal_id": goal_id,
            "interaction_type": "coaching",
            "user_input": prompt,
            "ai_response": coaching_message,
            "tokens_used": 0,  # 임시 메시지이므로 0
            "created_at": datetime.utcnow()
        })
        
        return {
            "message": coaching_message,
            "type": message_type,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"코칭 메시지 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/get-coaching/{goal_id}")
async def get_coaching_message_get(
    goal_id: str,
    message_type: str = Query("daily", description="메시지 타입"),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Dict[str, Any]:
    """개인화된 코칭 메시지를 생성합니다 (GET 방식)."""
    print(f"AI 코칭 메시지 요청 - goal_id: {goal_id}, message_type: {message_type}, user_id: {current_user.id}")
    print(f"API 엔드포인트 호출됨: /get-coaching/{goal_id}")
    
    # 목표 조회 - 문자열 방식 먼저 시도 (POST 방식과 동일)
    goal_doc = await db.goals.find_one({
        "_id": goal_id,
        "user_id": str(current_user.id)
    })
    
    # 문자열 방식으로 찾지 못했다면 ObjectId 방식 시도
    if not goal_doc:
        try:
            goal_doc = await db.goals.find_one({
                "_id": ObjectId(goal_id),
                "user_id": str(current_user.id)
            })
        except:
            pass
    
    if not goal_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목표를 찾을 수 없습니다."
        )
    
    # 최근 진도 기록 조회
    recent_progress = []
    async for log in db.progress_logs.find({
        "goal_id": goal_id,
        "user_id": str(current_user.id)
    }).sort("created_at", -1).limit(5):
        recent_progress.append(log)
    
    # 코칭 메시지 생성
    progress_rate = (goal_doc['current_value'] / goal_doc['target_value']) * 100
    
    try:
        # 개인화된 격려 메시지 생성
        coaching_messages = [
            f"안녕하세요! '{goal_doc['title']}' 목표에 대한 현재 진도율이 {progress_rate:.1f}%입니다. 꾸준히 잘 하고 계시네요! 💪",
            f"목표 달성을 위해 오늘도 한 걸음씩 나아가고 계시는군요! {goal_doc['title']} 목표까지 {goal_doc['target_value'] - goal_doc['current_value']:.1f}{goal_doc['unit']} 남았습니다.",
            f"훌륭합니다! 현재 {progress_rate:.1f}% 달성하셨어요. 이 속도라면 목표 달성이 충분히 가능할 것 같습니다! 🎯",
            f"매일 조금씩이라도 진전을 보이는 것이 중요해요. {goal_doc['title']} 목표를 향해 꾸준히 노력하고 계시는 모습이 보기 좋습니다! ✨"
        ]
        
        import random
        coaching_message = random.choice(coaching_messages)
        
        # AI 상호작용 기록 저장
        await db.ai_interactions.insert_one({
            "user_id": str(current_user.id),
            "goal_id": goal_id,
            "interaction_type": "coaching",
            "user_input": f"목표: {goal_doc['title']}, 진도율: {progress_rate:.1f}%",
            "ai_response": coaching_message,
            "tokens_used": 0,  # 임시 메시지이므로 0
            "created_at": datetime.utcnow()
        })
        
        return {
            "message": coaching_message,
            "type": message_type,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"코칭 메시지 생성 중 오류가 발생했습니다: {str(e)}"
        ) 
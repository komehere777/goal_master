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


@router.get("/test")
async def test_ai_router():
    """AI 라우터 테스트용 엔드포인트"""
    return {"message": "AI 라우터가 정상 작동 중입니다", "status": "ok"}


@router.get("/test-coaching/{goal_id}")
async def test_coaching_route(goal_id: str):
    """코칭 라우터 테스트용 엔드포인트"""
    print(f"테스트 코칭 라우터 호출됨 - goal_id: {goal_id}")
    return {"message": f"테스트 코칭 라우터 - goal_id: {goal_id}", "status": "ok"}


@router.post("/analyze-goal")
async def analyze_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Dict[str, Any]:
    """목표를 AI로 분석합니다."""
    # 목표 조회
    goal_doc = await db.goals.find_one({
        "_id": ObjectId(goal_id),
        "user_id": str(current_user.id)
    })
    
    if not goal_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목표를 찾을 수 없습니다."
        )
    
    # AI 분석 프롬프트 생성
    prompt = f"""
    다음 목표를 분석해주세요:
    
    제목: {goal_doc['title']}
    설명: {goal_doc['description']}
    카테고리: {goal_doc['category']}
    목표값: {goal_doc['target_value']} {goal_doc['unit']}
    현재값: {goal_doc['current_value']} {goal_doc['unit']}
    마감일: {goal_doc['deadline']}
    우선순위: {goal_doc['priority']}
    
    다음 관점에서 분석하고 JSON 형태로 응답해주세요:
    1. 목표의 구체성 및 달성 가능성 (1-10점)
    2. 예상 소요 기간 (일 단위)
    3. 성공 확률 (0-1 사이의 값)
    4. 개선 제안 사항
    
    응답 형식:
    {{
        "difficulty_score": 숫자,
        "estimated_duration": 숫자,
        "success_probability": 숫자,
        "suggestions": "제안사항 텍스트"
    }}
    """
    
    try:
        # OpenAI API 호출
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 개인 목표 달성을 돕는 전문 코치입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # AI 분석 결과를 데이터베이스에 저장
        ai_analysis = {
            "difficulty_score": 7.0,  # 실제로는 AI 응답을 파싱해야 함
            "estimated_duration": 30,
            "success_probability": 0.75
        }
        
        await db.goals.update_one(
            {"_id": ObjectId(goal_id)},
            {"$set": {"ai_analysis": ai_analysis, "updated_at": datetime.utcnow()}}
        )
        
        # AI 상호작용 기록 저장
        await db.ai_interactions.insert_one({
            "user_id": ObjectId(current_user.id),
            "goal_id": ObjectId(goal_id),
            "interaction_type": "planning",
            "user_input": prompt,
            "ai_response": ai_response,
            "tokens_used": response.usage.total_tokens,
            "created_at": datetime.utcnow()
        })
        
        return {
            "analysis": ai_analysis,
            "suggestions": ai_response,
            "message": "목표 분석이 완료되었습니다."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 분석 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/generate-plan")
async def generate_action_plan(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Dict[str, Any]:
    """목표를 위한 실행 계획을 AI로 생성합니다."""
    # 목표 조회
    goal_doc = await db.goals.find_one({
        "_id": ObjectId(goal_id),
        "user_id": str(current_user.id)
    })
    
    if not goal_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="목표를 찾을 수 없습니다."
        )
    
    # 실행 계획 생성 프롬프트
    prompt = f"""
    다음 목표를 위한 상세한 실행 계획을 단계별로 작성해주세요:
    
    목표: {goal_doc['title']}
    설명: {goal_doc['description']}
    목표값: {goal_doc['target_value']} {goal_doc['unit']}
    마감일: {goal_doc['deadline']}
    
    다음 형식으로 응답해주세요:
    1. 각 단계별 제목과 설명
    2. 예상 소요 시간 (분 단위)
    3. 구체적인 실행 방법
    
    JSON 형태로 응답:
    {{
        "title": "실행 계획 제목",
        "description": "계획 설명",
        "steps": [
            {{
                "step_number": 1,
                "title": "단계 제목",
                "description": "단계 설명",
                "estimated_time": 소요시간(분)
            }}
        ]
    }}
    """
    
    try:
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 실행 계획 수립 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # 실행 계획을 데이터베이스에 저장
        action_plan = {
            "goal_id": ObjectId(goal_id),
            "user_id": ObjectId(current_user.id),
            "title": f"{goal_doc['title']} 실행 계획",
            "description": "AI가 생성한 맞춤형 실행 계획",
            "steps": [],  # 실제로는 AI 응답을 파싱해야 함
            "ai_generated": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.action_plans.insert_one(action_plan)
        
        # AI 상호작용 기록 저장
        await db.ai_interactions.insert_one({
            "user_id": ObjectId(current_user.id),
            "goal_id": ObjectId(goal_id),
            "interaction_type": "planning",
            "user_input": prompt,
            "ai_response": ai_response,
            "tokens_used": response.usage.total_tokens,
            "created_at": datetime.utcnow()
        })
        
        return {
            "plan_id": str(result.inserted_id),
            "plan": ai_response,
            "message": "실행 계획이 생성되었습니다."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"실행 계획 생성 중 오류가 발생했습니다: {str(e)}"
        )


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
    
    사용자의 개인설정: {current_user.profile.preferences}
    
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
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


@router.post("/generate-plan")
async def generate_action_plan(
    goal_id: str = Query(..., description="목표 ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Dict[str, Any]:
    """목표를 위한 실행 계획을 AI로 생성합니다."""
    print(f"AI 실행 계획 요청 - goal_id: {goal_id}, user_id: {current_user.id}")
    
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
        print(f"목표를 찾을 수 없음 - goal_id: {goal_id}, user_id: {str(current_user.id)}")
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
        print(f"실행 계획 OpenAI API 호출 시작")
        
        # OpenAI API 호출 (실제 API가 없으면 fallback 사용)
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 실행 계획 수립 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            print(f"실행 계획 OpenAI API 호출 성공")
        except Exception as openai_error:
            print(f"실행 계획 OpenAI API 호출 실패: {openai_error}")
            
            # 목표 내용 기반 맞춤형 실행 계획 생성
            progress_rate = (goal_doc['current_value'] / goal_doc['target_value']) * 100
            goal_title = goal_doc['title']
            category = goal_doc.get('category', '기본')
            
            # 카테고리별 맞춤 실행 계획
            category_plans = {
                "건강": {
                    "title": f"{goal_title} 건강 실행 계획",
                    "description": "건강한 습관 형성을 위한 단계별 계획",
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "기초 체력 평가",
                            "description": f"현재 상태를 파악하고 {goal_doc['target_value']}{goal_doc['unit']} 목표 달성을 위한 기초 체력을 측정합니다.",
                            "estimated_time": 30
                        },
                        {
                            "step_number": 2,
                            "title": "점진적 강도 증가",
                            "description": "몸에 무리가 가지 않도록 천천히 강도를 높여가며 꾸준한 습관을 만듭니다.",
                            "estimated_time": 45
                        },
                        {
                            "step_number": 3,
                            "title": "진도 추적 및 조정",
                            "description": "매주 진도를 체크하고 몸의 변화에 맞춰 계획을 조정합니다.",
                            "estimated_time": 20
                        }
                    ]
                },
                "학습": {
                    "title": f"{goal_title} 학습 실행 계획",
                    "description": "효과적인 학습을 위한 체계적 접근법",
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "학습 자료 정리",
                            "description": f"{goal_title} 목표 달성을 위한 필요한 자료와 커리큘럼을 정리합니다.",
                            "estimated_time": 60
                        },
                        {
                            "step_number": 2,
                            "title": "일일 학습 루틴",
                            "description": "매일 일정한 시간에 집중적으로 학습할 수 있는 루틴을 만듭니다.",
                            "estimated_time": 90
                        },
                        {
                            "step_number": 3,
                            "title": "복습 및 실습",
                            "description": "배운 내용을 복습하고 실제로 적용해볼 수 있는 시간을 확보합니다.",
                            "estimated_time": 60
                        }
                    ]
                },
                "업무": {
                    "title": f"{goal_title} 업무 실행 계획",
                    "description": "업무 효율성 극대화를 위한 전략적 계획",
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "작업 분석 및 우선순위",
                            "description": f"{goal_title} 달성을 위해 필요한 업무들을 분석하고 우선순위를 정합니다.",
                            "estimated_time": 45
                        },
                        {
                            "step_number": 2,
                            "title": "시간 관리 시스템",
                            "description": "효율적인 시간 배분과 집중력 향상을 위한 시스템을 구축합니다.",
                            "estimated_time": 30
                        },
                        {
                            "step_number": 3,
                            "title": "성과 측정 및 개선",
                            "description": "정기적으로 성과를 측정하고 개선점을 찾아 적용합니다.",
                            "estimated_time": 40
                        }
                    ]
                },
                "취미": {
                    "title": f"{goal_title} 취미 실행 계획",
                    "description": "즐거운 취미 생활을 위한 단계별 접근",
                    "steps": [
                        {
                            "step_number": 1,
                            "title": "기초 준비 및 환경 조성",
                            "description": f"{goal_title} 활동을 위한 필요한 도구나 환경을 준비합니다.",
                            "estimated_time": 30
                        },
                        {
                            "step_number": 2,
                            "title": "기본기 익히기",
                            "description": "부담 없이 기본기부터 차근차근 익혀가며 재미를 찾습니다.",
                            "estimated_time": 60
                        },
                        {
                            "step_number": 3,
                            "title": "실력 향상 및 도전",
                            "description": "점차 실력을 향상시키며 새로운 도전을 시도합니다.",
                            "estimated_time": 90
                        }
                    ]
                }
            }
            
            # 기본 계획
            default_plan = {
                "title": f"{goal_title} 실행 계획",
                "description": "목표 달성을 위한 체계적 접근법",
                "steps": [
                    {
                        "step_number": 1,
                        "title": "현재 상황 분석",
                        "description": f"현재 {progress_rate:.1f}% 달성 상태를 분석하고 남은 과제를 파악합니다.",
                        "estimated_time": 45
                    },
                    {
                        "step_number": 2,
                        "title": "단계별 실행",
                        "description": "목표를 작은 단위로 나누어 단계적으로 실행합니다.",
                        "estimated_time": 60
                    },
                    {
                        "step_number": 3,
                        "title": "지속적인 관리",
                        "description": "꾸준한 진도 체크와 동기 부여를 통해 목표를 완성합니다.",
                        "estimated_time": 30
                    }
                ]
            }
            
            # 카테고리에 맞는 계획 선택
            plan = category_plans.get(category, default_plan)
            
            # OpenAI API 실패 시 더미 응답 생성
            class DummyResponse:
                def __init__(self):
                    self.choices = [DummyChoice()]
                    self.usage = DummyUsage()
            
            class DummyChoice:
                def __init__(self):
                    self.message = DummyMessage()
            
            class DummyMessage:
                def __init__(self):
                    import json
                    self.content = json.dumps(plan, ensure_ascii=False)
            
            class DummyUsage:
                def __init__(self):
                    self.total_tokens = 0
            
            response = DummyResponse()
            print(f"맞춤형 실행 계획 사용 - 카테고리: {category}")
        
        ai_response = response.choices[0].message.content
        
        # 실행 계획을 데이터베이스에 저장
        action_plan = {
            "goal_id": goal_id,
            "user_id": str(current_user.id),
            "title": f"{goal_doc['title']} 실행 계획",
            "description": "AI가 생성한 맞춤형 실행 계획",
            "steps": [],  # 실제로는 AI 응답을 파싱해야 함
            "ai_generated": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.action_plans.insert_one(action_plan)
        
        # AI 상호작용 기록 저장
        tokens_used = 0
        try:
            if hasattr(response, 'usage') and response.usage and hasattr(response.usage, 'total_tokens'):
                tokens_used = response.usage.total_tokens
        except:
            tokens_used = 0
            
        await db.ai_interactions.insert_one({
            "user_id": str(current_user.id),
            "goal_id": goal_id,
            "interaction_type": "planning",
            "user_input": prompt,
            "ai_response": ai_response,
            "tokens_used": tokens_used,
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
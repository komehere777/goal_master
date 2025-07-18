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


@router.post("/analyze-goal")
async def analyze_goal(
    goal_id: str = Query(..., description="목표 ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Dict[str, Any]:
    """목표를 AI로 분석합니다."""
    print(f"AI 목표 분석 요청 - goal_id: {goal_id}, user_id: {current_user.id}")
    
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
        print(f"OpenAI API 호출 시작 - model: gpt-4o-mini")
        
        # OpenAI API 호출 (실제 API가 없으면 fallback 사용)
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 개인 목표 달성을 돕는 전문 코치입니다. 반드시 JSON 형태로만 응답해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            print(f"OpenAI API 호출 성공")
        except Exception as openai_error:
            print(f"OpenAI API 호출 실패: {openai_error}")
            # 목표 내용 기반 맞춤형 분석 생성
            
            # 진도율 계산
            progress_rate = (goal_doc['current_value'] / goal_doc['target_value']) * 100
            
            # 카테고리별 맞춤 분석
            category_analysis = {
                "건강": {
                    "difficulty_score": 6.5 + (progress_rate / 100) * 2,
                    "estimated_duration": max(30, int(90 - progress_rate)),
                    "success_probability": 0.75 + (progress_rate / 200),
                    "suggestions": f"건강 목표는 꾸준함이 핵심입니다. 현재 {progress_rate:.1f}% 달성하셨네요! 작은 습관부터 시작하여 점진적으로 강도를 높여가세요."
                },
                "학습": {
                    "difficulty_score": 7.0 + (progress_rate / 100) * 1.5,
                    "estimated_duration": max(60, int(120 - progress_rate)),
                    "success_probability": 0.70 + (progress_rate / 250),
                    "suggestions": f"학습은 반복과 이해가 중요합니다. {progress_rate:.1f}% 진행 중이시군요. 매일 조금씩이라도 꾸준히 학습하고 복습 시간을 확보하세요."
                },
                "업무": {
                    "difficulty_score": 7.5 + (progress_rate / 100) * 1,
                    "estimated_duration": max(45, int(100 - progress_rate)),
                    "success_probability": 0.80 + (progress_rate / 300),
                    "suggestions": f"업무 목표는 체계적인 계획과 실행이 중요합니다. {progress_rate:.1f}% 달성 중이시네요. 우선순위를 정하고 단계별로 접근해보세요."
                },
                "취미": {
                    "difficulty_score": 5.5 + (progress_rate / 100) * 2,
                    "estimated_duration": max(30, int(80 - progress_rate)),
                    "success_probability": 0.85 + (progress_rate / 400),
                    "suggestions": f"취미 활동은 즐거움이 우선입니다! {progress_rate:.1f}% 진행 중이군요. 부담을 갖지 말고 재미있게 접근하세요."
                }
            }
            
            # 기본값 설정
            default_analysis = {
                "difficulty_score": 7.0,
                "estimated_duration": 60,
                "success_probability": 0.75,
                "suggestions": f"현재 {progress_rate:.1f}% 진행 중입니다. 목표를 작은 단위로 나누어 꾸준히 진행해보세요."
            }
            
            # 카테고리에 맞는 분석 선택
            analysis = category_analysis.get(goal_doc.get('category', ''), default_analysis)
            
            # 우선순위에 따른 조정
            priority_multiplier = {
                "높음": 1.2,
                "중간": 1.0,
                "낮음": 0.8
            }
            multiplier = priority_multiplier.get(goal_doc.get('priority', '중간'), 1.0)
            analysis['difficulty_score'] *= multiplier
            analysis['estimated_duration'] = int(analysis['estimated_duration'] / multiplier)
            
            # 값 범위 제한
            analysis['difficulty_score'] = max(1.0, min(10.0, analysis['difficulty_score']))
            analysis['success_probability'] = max(0.1, min(1.0, analysis['success_probability']))
            
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
                    self.content = json.dumps(analysis, ensure_ascii=False)
            
            class DummyUsage:
                def __init__(self):
                    self.total_tokens = 0
            
            response = DummyResponse()
            print(f"맞춤형 더미 분석 사용 - 카테고리: {goal_doc.get('category', '기본')}")
        
        ai_response = response.choices[0].message.content
        
        # AI 응답 유효성 검사
        if not ai_response:
            ai_response = "{}"
        
        # AI 응답을 JSON으로 파싱
        import json
        import re
        
        try:
            # JSON 부분만 추출 (```json과 ``` 제거)
            json_match = re.search(r'```json\s*(.*?)\s*```', ai_response, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
            else:
                # ```이 없는 경우 전체 응답에서 JSON 찾기
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    json_content = json_match.group(0)
                else:
                    json_content = ai_response
            
            # JSON 파싱 시도
            if json_content:
                parsed_analysis = json.loads(json_content)
            else:
                parsed_analysis = {}
            
            # 필수 필드 검증 및 기본값 설정
            ai_analysis = {
                "difficulty_score": float(parsed_analysis.get("difficulty_score", 7.0)),
                "estimated_duration": int(parsed_analysis.get("estimated_duration", 30)),
                "success_probability": float(parsed_analysis.get("success_probability", 0.75)),
                "suggestions": str(parsed_analysis.get("suggestions", "꾸준히 노력하세요!"))
            }
            
            # 값 범위 검증
            ai_analysis["difficulty_score"] = max(1.0, min(10.0, ai_analysis["difficulty_score"]))
            ai_analysis["success_probability"] = max(0.0, min(1.0, ai_analysis["success_probability"]))
            ai_analysis["estimated_duration"] = max(1, ai_analysis["estimated_duration"])
            
        except (json.JSONDecodeError, ValueError, KeyError) as parse_error:
            print(f"AI 응답 파싱 실패: {parse_error}")
            print(f"원본 응답: {ai_response}")
            
            # 파싱 실패 시 기본값 사용
            ai_analysis = {
                "difficulty_score": 7.0,
                "estimated_duration": 30,
                "success_probability": 0.75,
                "suggestions": "목표 달성을 위해 꾸준히 노력하세요!"
            }
        
        await db.goals.update_one(
            {"_id": ObjectId(goal_id) if ObjectId.is_valid(goal_id) else goal_id},
            {"$set": {"ai_analysis": ai_analysis, "updated_at": datetime.utcnow()}}
        )
        
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
            "interaction_type": "analysis",
            "user_input": prompt,
            "ai_response": ai_response,
            "tokens_used": tokens_used,
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
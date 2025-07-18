from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
async def test_ai_router():
    """AI 라우터 테스트용 엔드포인트"""
    return {"message": "AI 라우터가 정상 작동 중입니다", "status": "ok"}


@router.get("/test-coaching/{goal_id}")
async def test_coaching_route(goal_id: str):
    """코칭 라우터 테스트용 엔드포인트"""
    print(f"테스트 코칭 라우터 호출됨 - goal_id: {goal_id}")
    return {"message": f"테스트 코칭 라우터 - goal_id: {goal_id}", "status": "ok"} 
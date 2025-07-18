from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import motor.motor_asyncio
import os

from app.routers import auth, goals, progress, ai_coach, community
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    app.state.mongodb_client = mongodb_client
    app.state.mongodb = mongodb_client.goalmaster
    try:
        yield
    finally:
        mongodb_client.close()


app = FastAPI(
    title="GoalMaster AI",
    description="AI 기반 개인 목표 달성 코칭 플랫폼",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(ai_coach.router, prefix="/api/ai", tags=["ai_coach"])
app.include_router(community.router, prefix="/api/community", tags=["community"])


@app.get("/")
async def root():
    return {"message": "GoalMaster AI - 개인 목표 달성 코치"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "서비스가 정상적으로 실행 중입니다."} 
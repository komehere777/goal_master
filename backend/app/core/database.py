from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import Request


def get_database(request: Request) -> AsyncIOMotorDatabase:
    """FastAPI 요청에서 MongoDB 데이터베이스 인스턴스를 가져옵니다."""
    return request.app.state.mongodb 
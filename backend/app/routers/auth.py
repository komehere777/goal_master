from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId
from typing import Optional

from app.core.security import create_access_token, verify_password, get_password_hash, verify_token
from app.models.user import UserCreate, UserInDB, User
from app.core.database import get_database
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> User:
    """현재 인증된 사용자 정보를 가져옵니다."""
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증되지 않은 사용자입니다."
        )
    
    # ObjectId와 문자열 모두 시도하여 사용자 조회
    user_doc = None
    
    # 먼저 ObjectId로 시도
    try:
        object_id = ObjectId(user_id)
        user_doc = await db.users.find_one({"_id": object_id})
    except Exception:
        pass
    
    # ObjectId로 찾지 못했으면 문자열로 시도
    if not user_doc:
        user_doc = await db.users.find_one({"_id": user_id})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    
    return User(
        id=str(user_doc["_id"]),
        email=user_doc["email"],
        profile=user_doc["profile"],
        created_at=user_doc["created_at"],
        updated_at=user_doc["updated_at"]
    )


@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """새 사용자를 등록합니다."""
    # 이메일 중복 검사
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다."
        )
    
    # 사용자 생성
    user_in_db = UserInDB(
        email=user_data.email,
        profile=user_data.profile,
        password_hash=get_password_hash(user_data.password)
    )
    
    # 데이터베이스에 저장
    result = await db.users.insert_one(user_in_db.model_dump(by_alias=True))
    
    # JWT 토큰 생성
    access_token = create_access_token(subject=str(result.inserted_id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "회원가입이 완료되었습니다."
    }


@router.post("/login", response_model=dict)
async def login(
    login_data: LoginRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """사용자 로그인을 처리합니다."""
    # 사용자 조회
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc or not verify_password(login_data.password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )
    
    # JWT 토큰 생성
    access_token = create_access_token(subject=str(user_doc["_id"]))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "로그인이 완료되었습니다."
    }


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """현재 사용자의 정보를 조회합니다."""
    return current_user


@router.post("/refresh", response_model=dict)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """토큰을 갱신합니다."""
    access_token = create_access_token(subject=current_user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "토큰이 갱신되었습니다."
    } 
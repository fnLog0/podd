import hashlib
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.jwt import create_access_token, create_refresh_token, decode_token
from src.database import get_db
from src.models.refresh_token import RefreshToken
from src.models.user import User
from src.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def _store_refresh_token(db: AsyncSession, user_id: str, refresh_token: str) -> None:
    payload = decode_token(refresh_token)
    if payload and "exp" in payload:
        expires_at = datetime.fromtimestamp(payload["exp"])
    else:
        expires_at = datetime.utcnow()
    token_record = RefreshToken(
        token_hash=_token_hash(refresh_token),
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(token_record)
    await db.commit()


async def _revoke_refresh_token(db: AsyncSession, refresh_token: str) -> None:
    await db.execute(delete(RefreshToken).where(RefreshToken.token_hash == _token_hash(refresh_token)))
    await db.commit()


async def _is_refresh_token_valid(db: AsyncSession, refresh_token: str) -> bool:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == _token_hash(refresh_token))
    )
    return result.scalar_one_or_none() is not None


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=body.email,
        password_hash=pwd_context.hash(body.password),
        name=body.name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    await _store_refresh_token(db, str(user.id), refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user is None or not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    await _store_refresh_token(db, str(user.id), refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout")
async def logout(body: LogoutRequest, db: AsyncSession = Depends(get_db)):
    await _revoke_refresh_token(db, body.refresh_token)
    return {"message": "logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if not await _is_refresh_token_valid(db, body.refresh_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    await _revoke_refresh_token(db, body.refresh_token)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    await _store_refresh_token(db, str(user.id), refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

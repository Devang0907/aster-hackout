from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.config import Settings, get_settings
from app.core.database import get_database
from app.schemas.user import UserContext, UserRole
from app.security.authentication import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
Database = Annotated[Any, Depends(get_database)]
SettingsDependency = Annotated[Settings, Depends(get_settings)]


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    fullName: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.factory_owner


class AuthResponse(BaseModel):
    token: str
    user: UserContext


@router.post("/signin")
async def signin(
    payload: SignInRequest, database: Database, settings: SettingsDependency
) -> AuthResponse:
    """Sign in user with email and password (development mode)."""
    # Find user by email
    user = await database.user.find_first(where={"email": payload.email.lower()})
    
    if not user or not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    # In production, this should use proper password hashing and verification
    # For development, we'll accept any password if user exists
    # TODO: Replace with proper password hashing (bcrypt/argon2)
    
    # Generate JWT token
    token_data = {
        "sub": str(user.id),
        "exp": settings.jwt_secret.get_secret_value(),  # This is wrong, should use expiration
    }
    
    # Proper JWT generation with expiration
    import time
    expiration = int(time.time()) + 86400  # 24 hours
    token = jwt.encode(
        {"sub": str(user.id), "exp": expiration},
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    
    user_context = UserContext(
        id=UUID(str(user.id)),
        fullName=user.fullName,
        email=user.email,
        role=UserRole(str(user.role)),
        isActive=user.isActive,
    )
    
    return AuthResponse(token=token, user=user_context)


@router.post("/register", status_code=201)
async def register(
    payload: RegisterRequest, database: Database, settings: SettingsDependency
) -> AuthResponse:
    """Register a new user (development mode)."""
    # Check if email already exists
    existing = await database.user.find_first(
        where={"email": payload.email.lower()}
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    # In production, password should be hashed before storage
    # For development, we're not storing passwords per spec
    import uuid
    user_id = uuid.uuid4()
    
    user = await database.user.create(
        data={
            "id": str(user_id),
            "fullName": payload.fullName,
            "email": payload.email.lower(),
            "role": str(payload.role),
            "isActive": True,
        }
    )
    
    # Generate JWT token
    import time
    expiration = int(time.time()) + 86400  # 24 hours
    token = jwt.encode(
        {"sub": str(user.id), "exp": expiration},
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    
    user_context = UserContext(
        id=UUID(str(user.id)),
        fullName=user.fullName,
        email=user.email,
        role=UserRole(str(user.role)),
        isActive=user.isActive,
    )
    
    return AuthResponse(token=token, user=user_context)


@router.get("/me")
async def get_me(current_user: Annotated[UserContext, Depends(get_current_user)]) -> UserContext:
    """Get current authenticated user."""
    return current_user

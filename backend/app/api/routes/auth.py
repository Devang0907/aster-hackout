import asyncio
import base64
import hashlib
import hmac
import secrets
import smtplib
import ssl
import time
from email.message import EmailMessage
from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

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
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.factory_owner
    emailVerificationToken: str


class EmailOtpRequest(BaseModel):
    email: EmailStr


class EmailOtpVerificationRequest(BaseModel):
    email: EmailStr
    code: str
    challengeToken: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    email: EmailStr
    code: str
    challengeToken: str
    newPassword: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    token: str
    user: UserContext


class EmailOtpResponse(BaseModel):
    challengeToken: str
    expiresIn: int


class EmailVerificationResponse(BaseModel):
    emailVerificationToken: str


PASSWORD_HASH_ITERATIONS = 600_000


def _hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_HASH_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def _verify_password(password: str, encoded_hash: str | None) -> bool:
    if not encoded_hash:
        return False
    try:
        algorithm, iterations, encoded_salt, encoded_digest = encoded_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
        expected_digest = base64.urlsafe_b64decode(encoded_digest.encode("ascii"))
        actual_digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, int(iterations)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual_digest, expected_digest)


def _otp_hash(email: str, code: str, settings: Settings) -> str:
    secret = settings.jwt_secret.get_secret_value() if settings.jwt_secret else ""
    value = f"{email.lower()}:{code}:{secret}".encode()
    return hashlib.sha256(value).hexdigest()


def _send_otp_email(
    email: str, code: str, settings: Settings, subject: str = "Your CarbonWise verification code"
) -> None:
    if not settings.smtp_username or not settings.smtp_password:
        raise RuntimeError("SMTP_USERNAME and SMTP_PASSWORD are required")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email or settings.smtp_username
    message["To"] = email
    message.set_content(
        f"Your CarbonWise verification code is {code}. It expires in "
        f"{settings.email_otp_expiry_seconds // 60} minutes."
    )

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.starttls(context=context)
        server.login(settings.smtp_username, settings.smtp_password.get_secret_value())
        server.send_message(message)


@router.post("/request-email-otp", response_model=EmailOtpResponse)
async def request_email_otp(
    payload: EmailOtpRequest, database: Database, settings: SettingsDependency
) -> EmailOtpResponse:
    """Send a verification code only for a new email address."""
    if settings.jwt_secret is None:
        raise HTTPException(status_code=503, detail="JWT_SECRET is not configured")

    email = str(payload.email).lower()
    existing = await database.user.find_first(where={"email": email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Use password reset instead.",
        )

    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge_token = jwt.encode(
        {
            "type": "email_otp_challenge",
            "sub": email,
            "otpHash": _otp_hash(email, code, settings),
            "exp": int(time.time()) + settings.email_otp_expiry_seconds,
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    try:
        await asyncio.to_thread(_send_otp_email, email, code, settings)
    except (OSError, smtplib.SMTPException, RuntimeError) as exc:
        raise HTTPException(
            status_code=503, detail="Unable to send verification email"
        ) from exc

    return EmailOtpResponse(
        challengeToken=challenge_token,
        expiresIn=settings.email_otp_expiry_seconds,
    )


@router.post("/request-password-reset", response_model=EmailOtpResponse)
async def request_password_reset(
    payload: PasswordResetRequest, database: Database, settings: SettingsDependency
) -> EmailOtpResponse:
    """Send a password reset code without revealing whether an account exists."""
    if settings.jwt_secret is None:
        raise HTTPException(status_code=503, detail="JWT_SECRET is not configured")

    email = str(payload.email).lower()
    user = await database.user.find_first(where={"email": email, "isActive": True})
    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge_token = jwt.encode(
        {
            "type": "password_reset_challenge",
            "sub": email,
            "otpHash": _otp_hash(email, code, settings),
            "exp": int(time.time()) + settings.email_otp_expiry_seconds,
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    if user:
        try:
            await asyncio.to_thread(
                _send_otp_email,
                email,
                code,
                settings,
                "Reset your CarbonWise password",
            )
        except (OSError, smtplib.SMTPException, RuntimeError) as exc:
            raise HTTPException(
                status_code=503, detail="Unable to send password reset email"
            ) from exc

    return EmailOtpResponse(
        challengeToken=challenge_token,
        expiresIn=settings.email_otp_expiry_seconds,
    )


@router.post("/confirm-password-reset")
async def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    database: Database,
    settings: SettingsDependency,
) -> dict[str, str]:
    """Verify a reset code and replace the account password."""
    if settings.jwt_secret is None:
        raise HTTPException(status_code=503, detail="JWT_SECRET is not configured")

    email = str(payload.email).lower()
    try:
        challenge = jwt.decode(
            payload.challengeToken,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=400, detail="Reset code expired or invalid") from exc

    expected_hash = challenge.get("otpHash")
    if (
        challenge.get("type") != "password_reset_challenge"
        or challenge.get("sub") != email
        or len(payload.code) != 6
        or not payload.code.isdigit()
        or not isinstance(expected_hash, str)
        or not hmac.compare_digest(_otp_hash(email, payload.code, settings), expected_hash)
    ):
        raise HTTPException(status_code=400, detail="Reset code expired or invalid")

    user = await database.user.find_first(where={"email": email, "isActive": True})
    if not user:
        raise HTTPException(status_code=400, detail="Reset code expired or invalid")

    await database.user.update(
        where={"id": str(user.id)},
        data={"passwordHash": _hash_password(payload.newPassword)},
    )
    return {"message": "Password reset successfully"}


@router.post("/verify-email-otp", response_model=EmailVerificationResponse)
async def verify_email_otp(
    payload: EmailOtpVerificationRequest, settings: SettingsDependency
) -> EmailVerificationResponse:
    """Verify the code and issue a token that permits registration."""
    if settings.jwt_secret is None:
        raise HTTPException(status_code=503, detail="JWT_SECRET is not configured")

    email = str(payload.email).lower()
    try:
        challenge = jwt.decode(
            payload.challengeToken,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=400, detail="Verification code expired or invalid") from exc

    expected_hash = challenge.get("otpHash")
    if (
        challenge.get("type") != "email_otp_challenge"
        or challenge.get("sub") != email
        or len(payload.code) != 6
        or not payload.code.isdigit()
        or not isinstance(expected_hash, str)
        or not hmac.compare_digest(_otp_hash(email, payload.code, settings), expected_hash)
    ):
        raise HTTPException(status_code=400, detail="Verification code expired or invalid")

    verification_token = jwt.encode(
        {
            "type": "email_verified",
            "sub": email,
            "exp": int(time.time()) + settings.email_otp_expiry_seconds,
        },
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    return EmailVerificationResponse(emailVerificationToken=verification_token)


@router.post("/signin")
async def signin(
    payload: SignInRequest, database: Database, settings: SettingsDependency
) -> AuthResponse:
    """Sign in a user after verifying the stored password hash."""
    user = await database.user.find_first(where={"email": payload.email.lower()})
    
    if not user or not user.isActive:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    if not _verify_password(payload.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
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
    if settings.jwt_secret is None:
        raise HTTPException(status_code=503, detail="JWT_SECRET is not configured")

    try:
        verification = jwt.decode(
            payload.emailVerificationToken,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=400, detail="Email verification is required") from exc

    if (
        verification.get("type") != "email_verified"
        or verification.get("sub") != str(payload.email).lower()
    ):
        raise HTTPException(status_code=400, detail="Email verification is required")

    # Check if email already exists
    existing = await database.user.find_first(
        where={"email": payload.email.lower()}
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    import uuid
    user_id = uuid.uuid4()
    
    user = await database.user.create(
        data={
            "id": str(user_id),
            "fullName": payload.fullName,
            "email": payload.email.lower(),
            "passwordHash": _hash_password(payload.password),
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

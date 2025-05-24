import jwt
import uuid
import bcrypt
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Annotated
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import delete, update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_async_session
from src.auth.schemas import Role, TokenData, UserBase, UserCreate, UserInDB
from src.auth.models import User, VerificationToken, PasswordResetToken
from src.core.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class SecurityService:
    @staticmethod
    def get_password_hash(password: str, cost: int = 12) -> str:
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(cost)).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def _create_token(data: dict, token_type: str, secret_key: str,
                    default_expire: timedelta,  expires_delta: timedelta | None = None) -> str:
        expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else default_expire
        )
        payload = {
            **data,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
            "sub": str(data.get("email")),
            "role": str(data["role"].value) if isinstance(data["role"], Role) else str(data["role"]),
            "token_type": token_type,
        }
        return jwt.encode(payload, secret_key, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        return SecurityService._create_token(
            data=data,
            token_type="access",
            secret_key=settings.ACCESS_SECRET_KEY,
            default_expire=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            expires_delta=expires_delta
        )

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
        return SecurityService._create_token(
            data=data,
            token_type="refresh",
            secret_key=settings.REFRESH_SECRET_KEY,
            default_expire=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            expires_delta=expires_delta
        )
    
    @staticmethod
    def _decode_token(token: str, secret_key: str, expected_token_type: str | None = None, expected_roles: list[Role] | None = None) -> dict:
        try:
            payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
            required_claims = {
                'exp': (lambda x: x is not None, "Token has no expiration"),
                'iat': (lambda x: x is not None, "Token has no issued at time"),
                'jti': (lambda x: x is not None, "Token has no JWT ID"),
                'sub': (lambda x: x is not None, "Token has no subject"),
                'role': (lambda x: x is not None, "Token has no role"),
                'token_type': (lambda x: x is not None, "Token has no type"),
            }
        
            for claim, (validator, error_msg) in required_claims.items():
                if not validator(payload.get(claim)):
                    raise InvalidTokenError(error_msg)
            
            if datetime.now(timezone.utc) > datetime.fromtimestamp(payload['exp'], timezone.utc):
                raise ExpiredSignatureError("Token expired")
            
            if expected_token_type and payload['token_type'] != expected_token_type:
                raise InvalidTokenError(f"Expected {expected_token_type} token, got {payload['token_type']}")
            
            if expected_roles:
                try:
                    token_role = Role(payload['role']) if not isinstance(payload['role'], Role) else payload['role']
                    if token_role not in expected_roles:
                        raise InvalidTokenError(f"Role {token_role} not in allowed roles")
                except ValueError:
                    raise InvalidTokenError("Invalid role in token")
        
            return payload
    
        except (ExpiredSignatureError, InvalidTokenError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def decode_access_token(token: str, expected_roles: list[Role] | None = None) -> dict:
        return SecurityService._decode_token(
            token, 
            settings.ACCESS_SECRET_KEY,
            expected_token_type="access",
            expected_roles=expected_roles
        )

    @staticmethod
    def decode_refresh_token(token: str) -> dict:
        return SecurityService._decode_token(
            token, 
            settings.REFRESH_SECRET_KEY,
            expected_token_type="refresh"
        )
    
class EmailService:
    @staticmethod
    async def send_email(to: str, subject: str, body: str, is_html: bool = False):
        try:
            if not all([
                settings.SMTP_HOST,
                settings.SMTP_PORT,
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD
                ]):
                    return False
            
            message = MIMEMultipart()
            message["From"] = settings.SMTP_USERNAME
            message["To"] = to
            message["Subject"] = subject
            message.attach(MIMEText(body, "html" if is_html else "plain"))

            await aiosmtplib.send(
                message,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                use_tls=settings.USE_TLS,
                start_tls=settings.START_TLS,
                timeout=10
            )
            print(f"Email sent successfully to {to}")
            return True
        
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    async def send_verification_email(db: AsyncSession, user: User):
        token = await EmailTokenService.create_verification_token(db, user.id)
        
        subject = "Подтверждение email"
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"
        body = f"Перейдите по ссылке для подтверждения: {verification_url}"
        
        return await EmailService.send_email(
            to=user.email,
            subject=subject,
            body=body
        )
    
    @staticmethod
    async def send_password_reset_email(db: AsyncSession, email: str) -> bool:
        user = await AuthService.get_user_by_email(db, email)
        if not user:
            return False
            
        token = await EmailTokenService.create_password_reset_token(db, user.id)
        
        subject = "Сброс пароля"
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token.token}"
        body = f"Для сброса пароля перейдите по ссылке: {reset_url}"
        
        return await EmailService.send_email(
            to=user.email,
            subject=subject,
            body=body
        )

class EmailTokenService:
    @staticmethod
    async def create_verification_token(db: AsyncSession, user_id: int) -> VerificationToken:
        await db.execute(
            delete(VerificationToken)
            .where(VerificationToken.user_id == user_id)
        )
        token = VerificationToken(
            token=str(uuid.uuid4()),
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS),
            is_used=False
        )
        
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token
    
    @staticmethod
    async def create_password_reset_token(db: AsyncSession, user_id: int) -> PasswordResetToken:
        token = PasswordResetToken(
            token=str(uuid.uuid4()),
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
            is_used=False
        )
        
        db.add(token)
        await db.commit()
        await db.refresh(token)
        return token

    @staticmethod
    async def verify_token(db: AsyncSession, token: str, token_type: str) -> bool:
        if token_type == 'verification':
            result = await db.execute(
                select(VerificationToken)
                .where(
                    VerificationToken.token == token,
                    VerificationToken.expires_at > datetime.now(timezone.utc),
                    VerificationToken.is_used == False
                )
            )
            return result.scalars().first() is not None
        
        elif token_type == 'password_reset':
            result = await db.execute(
                select(PasswordResetToken)
                .where(
                    PasswordResetToken.token == token,
                    PasswordResetToken.expires_at > datetime.now(timezone.utc),
                    PasswordResetToken.is_used == False
                )
            )
            return result.scalars().first() is not None
        
        return False
    
    @staticmethod
    async def mark_token_as_used(db: AsyncSession, token: str, token_type: str):
        if token_type == 'verification':
            await db.execute(
                update(VerificationToken)
                .where(VerificationToken.token == token)
                .values(is_used=True)
            )
        elif token_type == 'password_reset':
            await db.execute(
                update(PasswordResetToken)
                .where(PasswordResetToken.token == token)
                .values(is_used=True)
            )
        
        await db.commit()


class AuthService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str):
        user = await AuthService.get_user_by_email(db, email)
        if not user:
            return False
        if not SecurityService.verify_password(password, user.hashed_password):
            return False
        return user
    
    @staticmethod
    async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_async_session),
        required_roles: list[Role] | None = None,
) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = SecurityService.decode_access_token(token)
            if not all(key in payload for key in ['sub', 'role', 'token_type']):
                raise InvalidTokenError("Missing required token fields")
                
            if payload['token_type'] != 'access':
                raise InvalidTokenError("Invalid token type")
            
            if required_roles and Role(payload['role']) not in required_roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            user = await AuthService.get_user_by_email(db, email=payload['sub'])
            if user is None:
                raise credentials_exception
                
            return user
        except HTTPException:
            raise
        except Exception:
            raise credentials_exception
    
    @staticmethod
    async def get_current_active_user(
        current_user: Annotated[UserInDB, Depends(get_current_user)]
    ):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate):
        existing_user = await AuthService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        hashed_password = SecurityService.get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            disabled=True
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
        await EmailService.send_verification_email(db, user)

        return user

class RoleChecker:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(AuthService.get_current_active_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return current_user
    
allow_superadmin = RoleChecker([Role.superadmin, Role.admin, Role.teacher, Role.student])
allow_admin = RoleChecker([Role.admin, Role.teacher, Role.student])
allow_teacher = RoleChecker([Role.teacher])
allow_student = RoleChecker([Role.student])
import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.database import get_async_session
from src.auth.models import User
from src.config import settings
import smtplib
from email.mime.text import MIMEText

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_by_email(db_session: AsyncSession, email: str) -> User:
    query = select(User).filter(User.email == email)
    result = await db_session.execute(query)
    user = result.scalars().first()
    return user


def send_verification_email(email: str, token: str):
    verification_link = f"http://127.0.0.1:8000/auth/verify-email?token={token}"
    
    msg = MIMEText(f'Please click the following link to verify your email: {verification_link}')
    msg['Subject'] = 'Email Verification'
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, [email], msg.as_string())


async def create_user(db_session: AsyncSession, email: str, password: str, role: str) -> User:
    hashed_password = get_password_hash(password)
    verification_token = create_access_token(data={"email": email}, expires_delta=timedelta(days=1))
    
    new_user = User(
        email=email,
        hashed_password=hashed_password,
        role=role,
        verification_token=verification_token,
        disabled=True,
        is_verified=False
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    
    send_verification_email(email, verification_token)
    return new_user


async def verify_email(db_session: AsyncSession, token: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid verification token",
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_email(db_session, email)
    if user is None:
        raise credentials_exception
    
    if user.verification_token != token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    user.is_verified = True
    user.disabled = False
    user.verification_token = None
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


async def authenticate_user(db_session: AsyncSession, email: str, password: str):
    db_user = await get_user_by_email(db_session, email)
    if not db_user:
        return False
    if not verify_password(password, db_user.hashed_password):
        return False
    return db_user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_session: AsyncSession = Depends(get_async_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = await get_user_by_email(db_session, email)
    if user is None:
        raise credentials_exception
    return user


async def verify_refresh_token(token: str, db_session: AsyncSession) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_email(db_session, email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def request_password_reset(db_session: AsyncSession, user: User):
    reset_token = create_access_token(data={"email": user.email}, expires_delta=timedelta(hours=settings.RESET_TOKEN_EXPIRE_MINUTES))
    user.reset_token = reset_token
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    send_reset_email(user.email, reset_token)


async def reset_password(db_session: AsyncSession, token: str, new_password: str) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_by_email(db_session, email)
    if user is None:
        raise credentials_exception
    if user.reset_token != token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user.hashed_password = get_password_hash(new_password)
    user.reset_token = None
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user

def send_reset_email(email: str, token: str):

    reset_link = f"http://127.0.0.1:8000/docs#/default/reset_password_endpoint_reset_password_post?token={token}"

    msg = MIMEText(f'Use this link to reset your password: {reset_link}')
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, [email], msg.as_string())
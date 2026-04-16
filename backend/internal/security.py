import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext


load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))


def hash_password(password: str) -> str:
	return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str) -> str:
	now = datetime.now(timezone.utc)
	expire = now + timedelta(minutes=JWT_EXPIRE_MINUTES)
	payload: Dict[str, Any] = {
		"sub": subject,
		"role": role,
		"iat": int(now.timestamp()),
		"exp": int(expire.timestamp()),
	}
	return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
	return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
from datetime import datetime

from fastapi import HTTPException, status

from config.db import get_db
from internal.schemas.auth import LoginRequest, RegisterRequest
from internal.security import create_access_token, hash_password, verify_password
from internal.token_blacklist import blacklist_token
from models.models import User


def register_user(payload: RegisterRequest):
	with get_db() as db:
		existing_user = db.query(User).filter(User.email == payload.email).first()
		if existing_user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Email is already registered.",
			)

		user = User(
			name=payload.name,
			email=payload.email,
			phone=payload.phone,
			password_hash=hash_password(payload.password),
			role=payload.role,
		)
		db.add(user)
		db.commit()
		db.refresh(user)

		return {
			"id": user.id,
			"name": user.name,
			"email": user.email,
			"phone": user.phone,
			"role": user.role,
			"ngo_id": user.ngo_id,
			"location_id": user.location_id,
			"created_at": user.created_at,
		}


def login_user(payload: LoginRequest):
	with get_db() as db:
		user = db.query(User).filter(User.email == payload.email).first()
		if not user or not verify_password(payload.password, user.password_hash):
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid email or password.",
			)

		access_token = create_access_token(subject=str(user.id), role=user.role)
		return {
			"access_token": access_token,
			"token_type": "bearer",
			"expires_in": 60 * 60 * 24,
		}


def get_profile(user: User):
	return {
		"id": user.id,
		"name": user.name,
		"email": user.email,
		"phone": user.phone,
		"role": user.role,
		"ngo_id": user.ngo_id,
		"location_id": user.location_id,
		"created_at": user.created_at,
	}


def logout_user(user: User, token: str):
	payload = {
		"sub": str(user.id),
		"logout_at": datetime.utcnow().isoformat(),
	}
	blacklist_token(token, payload)
	return {"message": "Logged out successfully."}
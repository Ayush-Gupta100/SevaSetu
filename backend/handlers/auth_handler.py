from datetime import datetime
from fastapi import HTTPException, status
from config.db import get_db
from internal.schemas.auth import ChangePasswordRequest, LoginRequest, RegisterRequest, RegisterNgoRequest
from internal.security import create_access_token, hash_password, verify_password
from internal.token_blacklist import blacklist_token
from internal.geo_utils import pseudo_geocode
from models.models import Location, User, Ngo, NgoMember


TEMP_MEMBER_PASSWORD = "Welcome@123"


def register_user(payload: RegisterRequest):
	with get_db() as db:
		existing_user = db.query(User).filter(User.email == payload.email).first()
		if existing_user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Email is already registered.",
			)

		location_id = None
		if payload.role == "volunteer":
			if payload.location_latitude is None or payload.location_longitude is None:
				raise HTTPException(
					status_code=status.HTTP_400_BAD_REQUEST,
					detail="Volunteer location is mandatory. Please allow browser location access.",
				)

			location = Location(
				latitude=payload.location_latitude,
				longitude=payload.location_longitude,
				address=payload.location_address or "Browser location",
				country="India",
			)
			db.add(location)
			db.flush()
			location_id = location.id

		user = User(
			name=payload.name,
			email=payload.email,
			phone=payload.phone,
			password_hash=hash_password(payload.password),
			role=payload.role,
			location_id=location_id,
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


def register_ngo_with_admin(payload: RegisterNgoRequest):
	with get_db() as db:
		# Check existing user
		if db.query(User).filter(User.email == payload.admin_email).first():
			raise HTTPException(status_code=400, detail="Admin email already registered.")
		
		# Check existing NGO
		if db.query(Ngo).filter((Ngo.registration_number == payload.registration_number) | (Ngo.email == payload.ngo_email)).first():
			raise HTTPException(status_code=400, detail="NGO with this registration number or email already exists.")

		# 1. Create NGO
		hq_lat, hq_lon = pseudo_geocode(payload.address or payload.ngo_name)
		hq_location = Location(
			latitude=hq_lat,
			longitude=hq_lon,
			address=payload.address,
			country="India",
		)
		db.add(hq_location)
		db.flush()

		ngo = Ngo(
			name=payload.ngo_name,
			registration_number=payload.registration_number,
			email=payload.ngo_email,
			address=payload.address
		)
		db.add(ngo)
		db.flush()

		# 2. Create Admin User
		user = User(
			name=payload.admin_name,
			email=payload.admin_email,
			password_hash=hash_password(payload.admin_password),
			role="ngo_admin",
			ngo_id=ngo.id,
			location_id=hq_location.id,
		)
		db.add(user)
		db.flush()

		# 3. Add to NgoMember table
		member = NgoMember(user_id=user.id, ngo_id=ngo.id, role="admin")
		db.add(member)

		db.commit()
		return {"message": "NGO and Admin registered successfully.", "ngo_id": ngo.id}


def login_user(payload: LoginRequest):
	with get_db() as db:
		user = db.query(User).filter(User.email == payload.email).first()
		if not user or not verify_password(payload.password, user.password_hash):
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid email or password.",
			)

		access_token = create_access_token(subject=str(user.id), role=user.role)
		must_change_password = verify_password(TEMP_MEMBER_PASSWORD, user.password_hash)
		return {
			"access_token": access_token,
			"token_type": "bearer",
			"expires_in": 60 * 60 * 24,
			"must_change_password": must_change_password,
		}


def get_profile(user: User):
	must_change_password = verify_password(TEMP_MEMBER_PASSWORD, user.password_hash)
	return {
		"id": user.id,
		"name": user.name,
		"email": user.email,
		"phone": user.phone,
		"role": user.role,
		"ngo_id": user.ngo_id,
		"location_id": user.location_id,
		"must_change_password": must_change_password,
		"created_at": user.created_at,
	}


def change_password(current_user: User, payload: ChangePasswordRequest):
	if not verify_password(payload.current_password, current_user.password_hash):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Current password is incorrect.",
		)

	if payload.current_password == payload.new_password:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="New password must be different from current password.",
		)

	with get_db() as db:
		user = db.query(User).filter(User.id == current_user.id).first()
		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

		user.password_hash = hash_password(payload.new_password)
		db.add(user)
		db.commit()

	return {"message": "Password updated successfully."}


def logout_user(user: User, token: str):
	payload = {
		"sub": str(user.id),
		"logout_at": datetime.utcnow().isoformat(),
	}
	blacklist_token(token, payload)
	return {"message": "Logged out successfully."}
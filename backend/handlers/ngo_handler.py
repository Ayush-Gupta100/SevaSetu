from fastapi import HTTPException, status

from config.db import get_db
from internal.schemas.ngo import AddNgoMemberRequest, NgoCreateRequest, NgoVerificationRequest
from models.models import Ngo, NgoMember, User


def register_ngo(payload: NgoCreateRequest, current_user: User):
	with get_db() as db:
		existing = db.query(Ngo).filter(
			(Ngo.registration_number == payload.registration_number) | (Ngo.email == payload.email)
		).first()
		if existing:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="NGO with this registration number or email already exists.",
			)

		ngo = Ngo(
			name=payload.name,
			registration_number=payload.registration_number,
			email=payload.email,
			phone=payload.phone,
			address=payload.address,
			city=payload.city,
			state=payload.state,
		)
		db.add(ngo)
		db.flush()

		if current_user.role in ("ngo_admin", "ngo_member"):
			current_user.ngo_id = ngo.id
			db.add(current_user)

		db.commit()
		db.refresh(ngo)
		return ngo


def list_ngos(page: int, limit: int):
	offset = (page - 1) * limit
	with get_db() as db:
		return db.query(Ngo).order_by(Ngo.created_at.desc()).offset(offset).limit(limit).all()


def get_ngo_details(ngo_id: int):
	with get_db() as db:
		ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
		if not ngo:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NGO not found.")
		return ngo


def verify_ngo(ngo_id: int, payload: NgoVerificationRequest):
	with get_db() as db:
		ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
		if not ngo:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NGO not found.")

		ngo.verified = payload.verified
		if payload.trust_score is not None:
			ngo.trust_score = payload.trust_score

		db.add(ngo)
		db.commit()
		db.refresh(ngo)
		return ngo


def add_ngo_member(ngo_id: int, payload: AddNgoMemberRequest, current_user: User):
	with get_db() as db:
		ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
		if not ngo:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NGO not found.")

		if current_user.ngo_id != ngo_id:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="You can add members only to your own NGO.",
			)

		user = db.query(User).filter(User.id == payload.user_id).first()
		if not user:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

		existing_member = db.query(NgoMember).filter(
			NgoMember.user_id == user.id,
			NgoMember.ngo_id == ngo_id,
		).first()
		if existing_member:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="User is already a member of this NGO.",
			)

		member = NgoMember(user_id=user.id, ngo_id=ngo_id, role=payload.role)
		user.ngo_id = ngo_id

		db.add(member)
		db.add(user)
		db.commit()

		return {"message": "NGO member added successfully."}
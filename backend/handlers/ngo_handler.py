from fastapi import HTTPException, status

from config.db import get_db
from handlers.skills_survey_handler import upsert_user_skills
from internal.schemas.ngo import AddNgoMemberByEmailRequest, AddNgoMemberRequest, NgoCreateRequest, NgoVerificationRequest
from internal.security import hash_password
from models.models import Ngo, NgoMember, Notification, Skill, User, UserSkill


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
			db.add(db.merge(current_user))

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


def add_ngo_member_by_email(ngo_id: int, payload: AddNgoMemberByEmailRequest, current_user: User):
	with get_db() as db:
		ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
		if not ngo:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NGO not found.")

		if current_user.ngo_id != ngo_id:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="You can add members only to your own NGO.",
			)

		user = db.query(User).filter(User.email == payload.email).first()
		created_new_user = False
		temporary_password = None

		if not user:
			if not payload.create_if_missing:
				raise HTTPException(
					status_code=status.HTTP_404_NOT_FOUND,
					detail="User with this email does not exist.",
				)

			temporary_password = "Welcome@123"
			user = User(
				name=payload.name or payload.email.split("@")[0],
				email=payload.email,
				phone=payload.phone,
				password_hash=hash_password(temporary_password),
				role="ngo_member",
				ngo_id=ngo_id,
			)
			db.add(user)
			db.flush()
			created_new_user = True

		if user.ngo_id and user.ngo_id != ngo_id:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="User already belongs to another NGO.",
			)

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
		if user.role in ("community", "volunteer"):
			user.role = "ngo_member"

		db.add(member)
		db.add(user)

		if payload.skills:
			upsert_user_skills(db, user.id, payload.skills)

		notification_message = f"You have been added to NGO '{ngo.name}' as {payload.role}."
		if temporary_password:
			notification_message += " Please login and change your temporary password immediately."

		notification = Notification(
			user_id=user.id,
			type="push",
			title="NGO Membership Added",
			message=notification_message,
			status="sent",
		)
		db.add(notification)

		db.commit()

		return {
			"message": "NGO member added successfully.",
			"user_id": user.id,
			"created_new_user": created_new_user,
			"temporary_password": temporary_password,
		}


def list_ngo_members(ngo_id: int):
	with get_db() as db:
		members = db.query(NgoMember).filter(NgoMember.ngo_id == ngo_id).all()
		result = []
		for member in members:
			user = db.query(User).filter(User.id == member.user_id).first()
			skill_rows = db.query(UserSkill).filter(UserSkill.user_id == member.user_id).all()
			skill_names = []
			for us in skill_rows:
				skill = db.query(Skill).filter(Skill.id == us.skill_id).first()
				if skill:
					skill_names.append(skill.name)

			result.append(
				{
					"id": member.id,
					"user_id": member.user_id,
					"user_name": user.name if user else None,
					"user_email": user.email if user else None,
					"role": member.role,
					"joined_at": member.joined_at,
					"skills": skill_names,
				}
			)

		return result
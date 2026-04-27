import uuid

from fastapi import HTTPException, status

from config.db import get_db
from handlers.skills_survey_handler import upsert_user_skills
from internal.geo_utils import pseudo_geocode
from internal.notifications import create_notification
from internal.schemas.ngo import AddNgoMemberByEmailRequest, AddNgoMemberRequest, NgoCreateRequest, NgoHqLocationRequest, NgoVerificationRequest
from internal.security import hash_password
from models.models import Location, Ngo, NgoMember, Skill, User, UserSkill


_NGO_MEMBER_IMPORT_STORE: dict[str, dict] = {}
_ALLOWED_IMPORT_FIELDS = ["name", "email", "phone", "role", "skills"]
_REQUIRED_IMPORT_FIELDS = ["name", "email"]
_DEFAULT_MEMBER_PASSWORD = "Welcome@123"


def _normalize_import_key(raw_key: str) -> str:
	return "".join(ch for ch in raw_key.lower() if ch.isalnum())


def _as_str(value) -> str:
	if value is None:
		return ""
	return str(value).strip()


def _parse_member_role(raw_role: str) -> str:
	value = _as_str(raw_role).lower().replace("-", "_").replace(" ", "_")
	role_map = {
		"": "field_worker",
		"field_worker": "field_worker",
		"fieldworker": "field_worker",
		"worker": "field_worker",
		"manager": "manager",
		"admin": "admin",
	}
	if value not in role_map:
		raise ValueError("Role must be one of admin, manager, field_worker")
	return role_map[value]


def _extract_convertible_member_row(raw_row: dict, row_number: int) -> tuple[dict | None, str | None]:
	if not isinstance(raw_row, dict):
		return None, "Row is not an object"

	normalized = {_normalize_import_key(k): v for k, v in raw_row.items()}

	name = _as_str(
		normalized.get("name")
		or normalized.get("fullname")
		or normalized.get("membername")
		or normalized.get("username")
	)
	email = _as_str(
		normalized.get("email")
		or normalized.get("mail")
		or normalized.get("emailaddress")
	)
	phone = _as_str(
		normalized.get("phone")
		or normalized.get("mobilenumber")
		or normalized.get("mobile")
		or normalized.get("contact")
	)
	skills_raw = _as_str(
		normalized.get("skills")
		or normalized.get("skill")
		or normalized.get("tags")
	)

	if not name:
		return None, "Missing required field: name"
	if not email or "@" not in email:
		return None, "Missing or invalid required field: email"

	try:
		role = _parse_member_role(_as_str(normalized.get("role") or normalized.get("memberrole")))
	except ValueError as exc:
		return None, str(exc)

	skills = [skill.strip() for skill in skills_raw.split(",") if skill.strip()]

	return {
		"row_number": row_number,
		"name": name,
		"email": email.lower(),
		"phone": phone or None,
		"role": role,
		"skills": skills,
	}, None


def _add_ngo_member_by_email_internal(
	db,
	ngo: Ngo,
	email: str,
	name: str | None,
	phone: str | None,
	role: str,
	skills: list[str] | None,
	create_if_missing: bool,
):
	user = db.query(User).filter(User.email == email).first()
	created_new_user = False
	temporary_password = None

	if not user:
		if not create_if_missing:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="User with this email does not exist.",
			)

		temporary_password = _DEFAULT_MEMBER_PASSWORD
		user = User(
			name=name or email.split("@")[0],
			email=email,
			phone=phone,
			password_hash=hash_password(temporary_password),
			role="ngo_member",
			ngo_id=ngo.id,
		)
		db.add(user)
		db.flush()
		created_new_user = True

	if user.ngo_id and user.ngo_id != ngo.id:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="User already belongs to another NGO.",
		)

	existing_member = db.query(NgoMember).filter(
		NgoMember.user_id == user.id,
		NgoMember.ngo_id == ngo.id,
	).first()
	if existing_member:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="User is already a member of this NGO.",
		)

	member = NgoMember(user_id=user.id, ngo_id=ngo.id, role=role)
	user.ngo_id = ngo.id
	if user.role in ("community", "volunteer"):
		user.role = "ngo_member"

	db.add(member)
	db.add(user)

	if skills:
		skill_payload = [
			{"skill_name": skill_name, "category": "ngo", "proficiency_level": "intermediate"}
			for skill_name in skills
		]
		upsert_user_skills(db, user.id, skill_payload)

	notification_message = f"You have been added to NGO '{ngo.name}' as {role}."
	if temporary_password:
		notification_message += " Please login and change your temporary password immediately."

	create_notification(
		db,
		user_id=user.id,
		title="NGO Membership Added",
		message=notification_message,
		notification_type="push",
		priority="high",
	)

	return {
		"message": "NGO member added successfully.",
		"user_id": user.id,
		"created_new_user": created_new_user,
		"temporary_password": temporary_password,
	}


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


def update_ngo_hq_location(ngo_id: int, payload: NgoHqLocationRequest, current_user: User):
	with get_db() as db:
		ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
		if not ngo:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NGO not found.")

		if current_user.ngo_id != ngo_id:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="You can update headquarters only for your own NGO.",
			)

		lat, lon = pseudo_geocode(
			", ".join(
				[
					payload.address,
					payload.city or "",
					payload.state or "",
					payload.country or "India",
					payload.pincode or "",
				]
			)
		)

		location = (
			db.query(Location)
			.filter(
				Location.address == payload.address,
				Location.city == payload.city,
				Location.state == payload.state,
				Location.country == payload.country,
				Location.pincode == payload.pincode,
			)
			.first()
		)

		if not location:
			location = Location(
				latitude=lat,
				longitude=lon,
				address=payload.address,
				city=payload.city,
				state=payload.state,
				country=payload.country,
				pincode=payload.pincode,
			)
			db.add(location)
			db.flush()

		ngo.address = payload.address
		ngo.city = payload.city
		ngo.state = payload.state
		db.add(ngo)

		ngo_users = db.query(User).filter(User.ngo_id == ngo_id).all()
		for user in ngo_users:
			if user.location_id is None:
				user.location_id = location.id
				db.add(user)

		db.commit()
		return {"message": "NGO headquarters location updated successfully."}


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

		result = _add_ngo_member_by_email_internal(
			db,
			ngo=ngo,
			email=str(payload.email).lower(),
			name=payload.name,
			phone=payload.phone,
			role=payload.role,
			skills=[item.skill_name for item in payload.skills],
			create_if_missing=payload.create_if_missing,
		)
		db.commit()
		return result


def list_ngo_members(ngo_id: int, current_user: User):
	with get_db() as db:
		if current_user.ngo_id != ngo_id:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="You can only view members of your own NGO.",
			)

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


def upload_ngo_member_import(ngo_id: int, file_name: str, rows: list[dict], current_user: User):
	if current_user.ngo_id != ngo_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="You can import members only to your own NGO.",
		)

	normalized_rows = []
	invalid_rows = []

	for idx, row in enumerate(rows, start=2):
		normalized, error = _extract_convertible_member_row(row, idx)
		if error:
			invalid_rows.append({"row_number": idx, "reason": error, "raw": row})
			continue
		normalized_rows.append(normalized)

	import_id = uuid.uuid4().hex[:12]
	_NGO_MEMBER_IMPORT_STORE[import_id] = {
		"ngo_id": ngo_id,
		"uploaded_by": current_user.id,
		"file_name": file_name,
		"total_rows": len(rows),
		"valid_rows": normalized_rows,
		"invalid_rows": invalid_rows,
		"confirmed": False,
	}

	return {
		"import_id": import_id,
		"file_name": file_name,
		"total_rows": len(rows),
		"valid_rows": len(normalized_rows),
		"invalid_rows": len(invalid_rows),
	}


def preview_ngo_member_import(ngo_id: int, import_id: str, current_user: User):
	entry = _NGO_MEMBER_IMPORT_STORE.get(import_id)
	if not entry:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import batch not found.")

	if entry["ngo_id"] != ngo_id or current_user.ngo_id != ngo_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="You can preview imports only for your own NGO.",
		)

	return {
		"import_id": import_id,
		"file_name": entry["file_name"],
		"total_rows": entry["total_rows"],
		"valid_rows": len(entry["valid_rows"]),
		"invalid_rows": len(entry["invalid_rows"]),
		"accepted_fields": _ALLOWED_IMPORT_FIELDS,
		"required_fields": _REQUIRED_IMPORT_FIELDS,
		"preview": entry["valid_rows"][:20],
		"invalid_entries": entry["invalid_rows"][:20],
	}


def confirm_ngo_member_import(ngo_id: int, import_id: str, current_user: User):
	entry = _NGO_MEMBER_IMPORT_STORE.get(import_id)
	if not entry:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import batch not found.")

	if entry["ngo_id"] != ngo_id or current_user.ngo_id != ngo_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="You can confirm imports only for your own NGO.",
		)

	if entry["confirmed"]:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This import is already confirmed.")

	created_members = 0
	already_members = 0
	temporary_passwords = []
	failures = []

	with get_db() as db:
		ngo = db.query(Ngo).filter(Ngo.id == ngo_id).first()
		if not ngo:
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NGO not found.")

		for row in entry["valid_rows"]:
			try:
				result = _add_ngo_member_by_email_internal(
					db,
					ngo=ngo,
					email=row["email"],
					name=row["name"],
					phone=row["phone"],
					role=row["role"],
					skills=row["skills"],
					create_if_missing=True,
				)
				created_members += 1
				if result.get("temporary_password"):
					temporary_passwords.append(
						{
							"row_number": row["row_number"],
							"email": row["email"],
							"temporary_password": result["temporary_password"],
						}
					)
			except HTTPException as exc:
				message = str(exc.detail)
				if "already a member" in message.lower():
					already_members += 1
				else:
					failures.append(
						{
							"row_number": row["row_number"],
							"email": row["email"],
							"reason": message,
						}
					)

		db.commit()

	entry["confirmed"] = True

	return {
		"message": "NGO member import completed.",
		"import_id": import_id,
		"processed_rows": len(entry["valid_rows"]),
		"created_members": created_members,
		"already_members": already_members,
		"failed_rows": len(failures),
		"temporary_passwords": temporary_passwords,
		"failures": failures,
	}
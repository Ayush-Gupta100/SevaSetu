from fastapi import HTTPException, status

from config.db import get_db
from internal.schemas.skills_survey import AddUserSkillsRequest, SurveyRequest
from models.models import Skill, Survey, User, UserSkill


def upsert_user_skills(db, user_id: int, skills: list):
	for item in skills:
		skill = db.query(Skill).filter(Skill.name == item.skill_name).first()
		if not skill:
			skill = Skill(name=item.skill_name, category=item.category)
			db.add(skill)
			db.flush()

		existing = db.query(UserSkill).filter(
			UserSkill.user_id == user_id,
			UserSkill.skill_id == skill.id,
		).first()

		if existing:
			existing.proficiency_level = item.proficiency_level
			db.add(existing)
		else:
			user_skill = UserSkill(
				user_id=user_id,
				skill_id=skill.id,
				proficiency_level=item.proficiency_level,
			)
			db.add(user_skill)


def add_user_skills(payload: AddUserSkillsRequest, current_user: User):
	with get_db() as db:
		upsert_user_skills(db, current_user.id, payload.skills)

		db.commit()
		return {"message": "Skills updated successfully."}


def get_skills():
	with get_db() as db:
		return db.query(Skill).order_by(Skill.name.asc()).all()


def submit_survey(payload: SurveyRequest, current_user: User):
	with get_db() as db:
		survey = Survey(user_id=current_user.id, availability=payload.availability, interests=payload.interests)
		db.add(survey)
		db.commit()
		db.refresh(survey)
		return survey
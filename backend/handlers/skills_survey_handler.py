from fastapi import HTTPException, status
from sqlalchemy import func

from config.db import get_db
from internal.schemas.skills_survey import AddUserSkillsRequest, SurveyRequest
from models.models import Skill, Survey, User, UserSkill


DEFAULT_SKILLS: dict[str, list[str]] = {
	"Health": [
		"First Aid",
		"CPR",
		"Medical Support",
		"Nursing Assistance",
		"Public Health Outreach",
		"Mental Health Support",
	],
	"Logistics": [
		"Logistics Planning",
		"Supply Chain Coordination",
		"Inventory Management",
		"Route Planning",
		"Warehouse Operations",
	],
	"Infrastructure": [
		"Plumbing",
		"Electrical Repair",
		"Civil Work",
		"Masonry",
		"Carpentry",
		"Water Distribution",
	],
	"Emergency": [
		"Disaster Response",
		"Rescue Operations",
		"Fire Safety",
		"Evacuation Coordination",
		"Emergency Communication",
	],
	"Operations": [
		"Field Operations",
		"Task Coordination",
		"Team Leadership",
		"Volunteer Management",
		"Stakeholder Coordination",
	],
	"Community": [
		"Community Outreach",
		"Public Speaking",
		"Conflict Resolution",
		"Counseling",
		"Awareness Campaigns",
	],
	"Data": [
		"Data Entry",
		"Survey Collection",
		"Excel Reporting",
		"GIS Mapping",
		"Documentation",
	],
	"Technology": [
		"IT Support",
		"Mobile App Assistance",
		"System Troubleshooting",
		"Digital Communication",
	],
	"Environment": [
		"Waste Management",
		"Sanitation",
		"Water Quality Monitoring",
		"Tree Plantation",
		"Environmental Cleanup",
	],
	"Finance": [
		"Budget Tracking",
		"Expense Verification",
		"Donation Management",
		"Financial Documentation",
	],
}


def _ensure_default_skills(db):
	existing_names = {row[0] for row in db.query(Skill.name).all()}
	added = False

	for category, skills in DEFAULT_SKILLS.items():
		for skill_name in skills:
			if skill_name in existing_names:
				continue
			db.add(Skill(name=skill_name, category=category))
			added = True

	if added:
		db.commit()


def upsert_user_skills(db, user_id: int, skills: list):
	for item in skills:
		skill = db.query(Skill).filter(Skill.name == item.skill_name).first()
		if not skill:
			skill = Skill(name=item.skill_name, category=item.category)
			db.add(skill)
			db.flush()
		elif item.category and item.category != skill.category:
			skill.category = item.category
			db.add(skill)

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
		_ensure_default_skills(db)
		return db.query(Skill).order_by(Skill.name.asc()).all()


def get_user_skills(current_user: User):
	with get_db() as db:
		rows = (
			db.query(Skill.name, Skill.category, UserSkill.proficiency_level)
			.join(Skill, Skill.id == UserSkill.skill_id)
			.filter(UserSkill.user_id == current_user.id)
			.order_by(Skill.name.asc())
			.all()
		)

		return [
			{
				"skill_name": name,
				"category": category,
				"proficiency_level": proficiency_level,
			}
			for name, category, proficiency_level in rows
		]


def get_skill_categories():
	with get_db() as db:
		_ensure_default_skills(db)
		rows = (
			db.query(func.distinct(Skill.category))
			.filter(Skill.category.isnot(None), Skill.category != "")
			.order_by(Skill.category.asc())
			.all()
		)

		return [{"name": row[0]} for row in rows if row[0]]


def submit_survey(payload: SurveyRequest, current_user: User):
	with get_db() as db:
		survey = Survey(user_id=current_user.id, availability=payload.availability, interests=payload.interests)
		db.add(survey)
		db.commit()
		db.refresh(survey)
		return survey
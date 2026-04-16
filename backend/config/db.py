import os
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()


DATABASE_URL = os.getenv("NEON_DB", os.getenv("DATABASE_URL", "sqlite:///backend.db"))

engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
	engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def init_db() -> None:
	try:
		from backend.models.models import Base
	except ImportError:
		from models.models import Base

	Base.metadata.create_all(bind=engine)

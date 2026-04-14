import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL = os.getenv("NEON_DB", os.getenv("DATABASE_URL", "sqlite:///backend.db"))

engine = create_engine(
	DATABASE_URL,
	pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def init_db() -> None:
	from models.models import Base

	Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import Session
from config.db import engine, SessionLocal
from models.models import User, Ngo

db1 = SessionLocal()
u = db1.query(User).first()
if not u:
    u = User(name="test", email="test@test.com", password_hash="hash", role="ngo_admin")
    db1.add(u)
    db1.commit()
    db1.refresh(u)
db1.close()

# u is now detached
db2 = SessionLocal()
ngo = Ngo(name="test ngo", registration_number="123", email="ngo@test.com")
db2.add(ngo)
db2.flush()
u.ngo_id = ngo.id
try:
    db2.add(u)
    db2.commit()
    print("SUCCESS")
except Exception as e:
    print("ERROR:", type(e).__name__)
db2.close()

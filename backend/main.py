from fastapi import FastAPI

from config.db import init_db
from routes.routes import api_router


app = FastAPI(title="Community Coordination API", version="1.0.0")
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def startup_event() -> None:
	init_db()


@app.get("/")
def healthcheck() -> dict:
	return {"status": "ok", "service": "community-coordination-backend"}

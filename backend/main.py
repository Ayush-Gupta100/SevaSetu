from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from config.db import init_db
from routes.routes import api_router


load_dotenv()


def get_allowed_origins() -> list[str]:
	origins_env = os.getenv("FRONTEND_ORIGINS", "").strip()
	if origins_env:
		return [origin.strip() for origin in origins_env.split(",") if origin.strip()]

	return [
		"http://localhost:5173",
		"http://127.0.0.1:5173",
		"http://localhost:4173",
		"http://127.0.0.1:4173",
		"http://localhost:3000",
		"http://127.0.0.1:3000",
	]


@asynccontextmanager
async def lifespan(_: FastAPI):
	init_db()
	yield


app = FastAPI(title="Community Coordination API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
	CORSMiddleware,
	allow_origins=get_allowed_origins(),
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def healthcheck() -> dict:
	return {"status": "ok", "service": "community-coordination-backend"}


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

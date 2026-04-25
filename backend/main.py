from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.db import init_db
from routes.routes import api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
	init_db()
	yield


app = FastAPI(title="Community Coordination API", version="1.0.0", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def healthcheck() -> dict:
	return {"status": "ok", "service": "community-coordination-backend"}


if __name__ == "__main__":
	import uvicorn

	uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

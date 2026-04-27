from contextlib import asynccontextmanager, suppress
import asyncio
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from config.db import init_db
from internal.problem_bootstrap import seed_and_assign_problems_on_startup
from handlers.task_handler import run_pending_auto_assignment_checks
from routes.routes import api_router


load_dotenv()


logger = logging.getLogger(__name__)


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


async def _auto_assignment_worker(interval_seconds: int) -> None:
	while True:
		try:
			result = await asyncio.to_thread(run_pending_auto_assignment_checks)
			if result.get("assigned"):
				logger.info(
					"Auto-assignment cycle complete: checked=%s assigned=%s",
					result.get("checked", 0),
					result.get("assigned", 0),
				)
		except Exception:
			logger.exception("Auto-assignment cycle failed")

		await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
	init_db()
	try:
		seed_result = seed_and_assign_problems_on_startup()
		logger.info(
			"Problem startup bootstrap: reset=%s created=%s assigned=%s",
			seed_result.get("reset"),
			seed_result.get("created"),
			seed_result.get("assigned"),
		)
	except Exception:
		logger.exception("Problem startup bootstrap failed")

	try:
		startup_reassign_result = await asyncio.to_thread(run_pending_auto_assignment_checks)
		logger.info(
			"Startup reassignment pass: checked=%s assigned=%s",
			startup_reassign_result.get("checked", 0),
			startup_reassign_result.get("assigned", 0),
		)
	except Exception:
		logger.exception("Startup reassignment pass failed")

	interval_seconds = int(os.getenv("AUTO_ASSIGN_INTERVAL_SECONDS", "60"))
	worker = asyncio.create_task(_auto_assignment_worker(max(10, interval_seconds)))
	try:
		yield
	finally:
		worker.cancel()
		with suppress(asyncio.CancelledError):
			await worker


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

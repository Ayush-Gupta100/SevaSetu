# EVERYTHING.md

Complete technical context for the `google_solution` project.
This file is designed so any LLM can understand the system quickly and reason about changes safely.

## 1) What This Project Is

SevaSetu is a full-stack NGO/community coordination platform.

Core goals:
- Let users report community problems.
- Verify problems and convert them into actionable tasks.
- Assign tasks to volunteers (manual + AI-assisted auto-assignment).
- Track resources, donations, wallet, and ledger movement.
- Notify users in-app and attempt email notifications.

## 2) Tech Stack

Backend:
- FastAPI
- SQLAlchemy ORM
- Pydantic schemas
- JWT auth (PyJWT)
- Passlib/bcrypt password hashing

Frontend:
- React + TypeScript + Vite
- React Router
- TanStack Query
- Axios
- Tailwind CSS + Framer Motion + Recharts

Database:
- Primary: Postgres via `NEON_DB`/`DATABASE_URL`
- Fallback: SQLite (`sqlite:///backend.db`)

AI/automation:
- Groq Chat Completions API (`llama-3.1-8b-instant` default)
- Rule-based fallback inference
- Background auto-assignment worker

## 3) High-Level Architecture

Data flow:
1. User reports problem.
2. Backend geocodes location (deterministic pseudo geocode in current implementation).
3. AI infers category + confidence + required skills.
4. Priority score is computed.
5. Task is auto-created from the problem.
6. Task is auto-assigned (if suitable available volunteer found).
7. Notifications are created (DB), and mail send is attempted.

Startup flow (`backend/main.py`):
1. Initialize DB schema.
2. Seed and reset startup problems/tasks (configurable).
3. Run one immediate reassignment pass.
4. Start background worker to auto-assign open tasks periodically.

## 4) Backend Structure

`backend/main.py`
- FastAPI app + CORS + lifecycle management.

`backend/routes/`
- Route layer only; delegates to handlers.

`backend/handlers/`
- Business logic by module (auth, problems, tasks, resources, finance, etc.).

`backend/internal/`
- Cross-cutting internals: security, auth dependencies, AI assignment, mailing, notifications, geoutils, token blacklist, startup bootstrap.

`backend/internal/schemas/`
- Pydantic request/response contracts.

`backend/models/models.py`
- SQLAlchemy models and relationships.

## 5) Core Data Model (Important Entities)

Identity and org:
- `User` (roles: `community`, `volunteer`, `ngo_member`, `ngo_admin`)
- `Ngo`
- `NgoMember`
- `Location`

Problems and execution:
- `Problem`
- `ProblemProof`
- `ProblemVerification`
- `Task`
- `TaskAssignment`
- `TaskProof`

Skills/survey:
- `Skill`
- `UserSkill`
- `Survey`

Resource management:
- `ResourceType`
- `ResourceInventory`
- `ResourceRequirement`
- `ResourceAllocation`

Finance:
- `Donation`
- `PaymentTransaction`
- `NgoWallet`
- `LedgerEntry`
- `FinancialLedger` (defined, not central in current flows)
- `TaskExpense`

AI/ops:
- `AiMatch`
- `Notification`
- `ErrorAnalytics`

## 6) Authentication and Authorization

Auth style:
- Bearer JWT in `Authorization: Bearer <token>`.
- JWT payload includes `sub` (user id) and `role`.

Session handling:
- Stateless JWT validation.
- In-memory token blacklist for logout (`internal/token_blacklist.py`).
	- Important: blacklist resets on server restart.

Role checks:
- `require_roles(...)` dependency blocks unauthorized role access.

Password handling:
- Bcrypt via passlib.
- Temporary NGO member password flow uses `Welcome@123` and forces change on login.

## 7) AI and Auto-Assignment (Critical)

Main file: `backend/internal/auto_assignment.py`

### 7.1 Inference strategy

Step 1: Try Groq model
- Endpoint: `https://api.groq.com/openai/v1/chat/completions`
- Default model: `llama-3.1-8b-instant`
- Prompt asks for strict JSON with keys:
	- `category`
	- `confidence` (0..1)
	- `required_skills` (array)

Step 2: Fallback rules if Groq fails/unavailable
- Keyword rules map problem text to skill lists.
- Confidence fixed at `0.4` in fallback.

### 7.2 Assignment scoring

Only open tasks are considered.
Constraints:
- Skip if task already has assignment.
- Skip volunteers who are busy on `assigned`/`in_progress` tasks.

Scoring:
- Skill exact match: +3 each
- Skill fuzzy containment match: +2 each
- Category overlap bonus: +1

Outcome:
- If best score <= 0: keep task unassigned (`open`).
- If match found: create `TaskAssignment`, set task `assigned`, create notification.

### 7.3 Priority score logic

Used in problem creation and startup seeding.
Formula combines:
- AI confidence contribution
- category weight (`emergency` highest, `general` lower)
- location signal (`Pan India` gets lower local urgency weight)

Score is clamped to `[1.0, 10.0]`.

### 7.4 Background worker behavior

In `main.py`:
- Repeats every `AUTO_ASSIGN_INTERVAL_SECONDS` (min enforced 10s).
- Calls `run_pending_auto_assignment_checks()` to process all open tasks.

## 8) Startup Seed/Bootstrap Behavior

Main file: `backend/internal/problem_bootstrap.py`

If `RESET_PROBLEMS_ON_STARTUP` is true-like:
- Clears existing problems/tasks and dependent tables.
- Seeds 5 default scenario problems (including `Pan India` general case).
- Creates tasks for each.
- Runs auto-assignment per task.

This is useful for demo consistency but can reset data in dev environments.

## 9) Notifications and Mailing

Notifications:
- `internal/notifications.py` creates DB notification records.
- Status is `pending` by default and set to `failed` if email send fails.

Email:
- `internal/mailing.py` sends SMTP mail with fixed subject:
	- `Community Coordination Notification`
- Uses env vars `MAIL_*`.
- Has password normalization to tolerate quoted/spaced app passwords.

## 10) API Reference (Complete)

Base prefix: `/api/v1`

### 10.1 Auth

- `POST /auth/register`
	- Public
	- Create user (`community|volunteer|ngo_member|ngo_admin`).
	- Volunteer registration requires browser lat/lon.

- `POST /auth/register-ngo`
	- Public
	- Atomic NGO + admin user creation.

- `POST /auth/login`
	- Public
	- Returns bearer token + `must_change_password`.

- `GET /auth/me`
	- Auth required
	- Returns profile.

- `POST /auth/logout`
	- Auth required
	- Blacklists token in-memory.

- `POST /auth/change-password`
	- Auth required
	- Changes current user password.

### 10.2 NGOs

- `POST /ngos`
	- Auth required
	- Register NGO entity.

- `GET /ngos`
	- Auth required
	- List NGOs with pagination.

- `GET /ngos/{ngo_id}`
	- Auth required
	- NGO details.

- `PATCH /ngos/{ngo_id}/verify`
	- `ngo_admin`
	- Verify NGO + optional trust score.

- `PATCH /ngos/{ngo_id}/hq-location`
	- `ngo_admin|ngo_member`
	- Update NGO HQ location and propagate `location_id` to NGO users missing it.

- `POST /ngos/{ngo_id}/members`
	- `ngo_admin`
	- Add existing user to NGO.

- `POST /ngos/{ngo_id}/members/by-email`
	- `ngo_admin`
	- Add existing user by email or create new NGO member with temporary password.

- `GET /ngos/{ngo_id}/members`
	- Auth required
	- List members + member skills.

### 10.3 Locations

- `POST /locations/geocode`
	- Auth required
	- Normalizes/creates location and returns location id + coordinates.

- `POST /locations/reverse`
	- Auth required
	- Finds nearest known location within max radius.

### 10.4 Problems

- `POST /problems`
	- Auth required
	- Create problem, infer AI profile, compute priority, auto-create task, attempt auto-assignment.

- `POST /problems/{problem_id}/proofs`
	- Auth required
	- Upload problem proof metadata.

- `GET /problems`
	- Auth required
	- List/filter problems (`status`, `category`, `nearby`, pagination).
	- Response includes assigned user info and location address.

- `GET /problems/{problem_id}`
	- Auth required
	- Single problem details.

- `PATCH /problems/{problem_id}/verify`
	- `ngo_member|ngo_admin`
	- Approve/reject problem and notify reporter.

### 10.5 Tasks

- `POST /tasks`
	- `ngo_member|ngo_admin`
	- Create task and immediately try auto-assignment.

- `GET /tasks`
	- Auth required
	- List/filter tasks (`status`, `nearby`, `mine`, pagination).

- `POST /tasks/{task_id}/assign`
	- `ngo_member|ngo_admin`
	- Manual assignment to user id.

- `PATCH /tasks/{task_id}/accept`
	- `volunteer`
	- Accept assigned task.

- `POST /tasks/{task_id}/proofs`
	- Auth required
	- Upload task proof metadata.

- `PATCH /tasks/{task_id}/complete`
	- `ngo_member|ngo_admin`
	- Mark task complete.

### 10.6 Skills and Surveys

- `POST /users/skills`
	- Auth required
	- Upsert user skills.

- `GET /skills`
	- Auth required
	- List skill catalog (auto-seeds defaults if empty).

- `GET /users/skills/me`
	- Auth required
	- Get current user skills.

- `GET /skills/categories`
	- Auth required
	- Distinct skill categories.

- `POST /surveys`
	- Auth required
	- Submit availability/interests survey.

### 10.7 Resources

- `GET /resource-types`
	- Auth required
	- Resource type catalog (auto-seeded defaults).

- `POST /resources/inventory`
	- Auth required
	- Add inventory item; location required (explicit or resolved fallback).

- `GET /resources/inventory`
	- Auth required
	- Inventory for current NGO/user owner context.

- `POST /tasks/{task_id}/requirements`
	- Auth required
	- Add task resource requirement.

- `POST /resources/allocate`
	- Auth required
	- Allocate inventory against requirement.

### 10.8 Finance

- `POST /donations`
	- Auth required
	- Create donation record (`pending`).

- `POST /payments/initiate`
	- Auth required
	- Create payment transaction (`initiated`).

- `POST /payments/webhook`
	- Public (no auth dependency)
	- Mark payment success/failure, update donation status, credit NGO wallet, append ledger on first success.

- `GET /donations`
	- Auth required
	- NGO users see NGO donations; others see own donations.

- `GET /ngos/{ngo_id}/wallet`
	- Auth required
	- Return/create wallet.

- `GET /ngos/{ngo_id}/ledger`
	- Auth required
	- List NGO ledger entries.

### 10.9 Misc, AI, Notifications, Import, Public

- `GET /ai/matches`
	- Auth required
	- Returns persisted matches if no `problem_id`; else computes top mock matches on the fly.

- `GET /ai/insights`
	- Auth required
	- Aggregate metrics for problems/tasks/AI matches.

- `GET /notifications`
	- Auth required
	- User notifications feed.

- `PATCH /notifications/{notification_id}/read`
	- Auth required
	- Marks notification status as `sent`.

- `POST /import/upload`
	- Auth required
	- Upload parsed rows into in-memory import store.

- `GET /import/{import_id}/preview`
	- Auth required
	- Preview first rows.

- `POST /import/{import_id}/confirm`
	- Auth required
	- Mark import batch confirmed.

- `GET /public/stats`
	- Public
	- Counts for NGOs/problems/tasks/volunteers.

- `GET /public/problems`
	- Public
	- Recent non-rejected problems.

- `POST /public/join`
	- Public
	- Volunteer join/upgrade flow.

- `POST /public/volunteer-opt-in`
	- Auth required
	- Convert eligible user to volunteer.

## 11) Request/Response Schema Notes

Important validations:
- Volunteer registration requires `location_latitude` and `location_longitude`.
- Many create endpoints enforce `min_length` and positive quantity checks.
- Role literals and enum-like fields are strict in Pydantic schemas.

Main schema files:
- `backend/internal/schemas/auth.py`
- `backend/internal/schemas/ngo.py`
- `backend/internal/schemas/location.py`
- `backend/internal/schemas/problem.py`
- `backend/internal/schemas/task.py`
- `backend/internal/schemas/resource.py`
- `backend/internal/schemas/skills_survey.py`
- `backend/internal/schemas/finance.py`
- `backend/internal/schemas/misc.py`

## 12) Frontend Architecture

App shell:
- Router in `frontend/src/App.tsx`.
- Protected routes based on JWT + role from localStorage.

Session handling:
- Axios instance in `frontend/src/lib/api.ts`.
- Request interceptor injects bearer token.
- 401 response interceptor clears local auth storage.

State/data fetching:
- TanStack Query per feature page.
- Local form state for modals and submissions.

Feedback:
- Toast system in `frontend/src/lib/feedback.tsx`.

Theme:
- Light/dark with `ThemeProvider` and localStorage persistence.

## 13) Frontend Pages and What They Do

- `Landing.tsx`
	- Public stats/problem feed.
	- Contribute modal: donation + volunteer flow.

- `Login.tsx`
	- Login, token save, profile fetch, role-based redirect.

- `Register.tsx`
	- Volunteer registration requires browser geolocation.
	- NGO registration is atomic via `/auth/register-ngo`.

- `Problems.tsx`
	- Report problem with mandatory location.
	- General category enforces `Pan India`.
	- NGO roles can verify + create task in one action.

- `Tasks.tsx`
	- Kanban-style view (`open`, `assigned`, `in_progress`).
	- Manual assign modal.
	- Volunteer accept + NGO complete actions.

- `MemberDashboard.tsx`
	- My task counters, recent notifications.
	- Skills view/edit/add from standardized catalog + categories.

- `Dashboard.tsx`
	- NGO wallet/donation charts + recent notifications.
	- Add NGO member by user id.
	- Compact NGO HQ location update form.

- `Inventory.tsx`
	- Resource inventory list.
	- Add inventory with mandatory address -> geocode -> location id.

- `Notifications.tsx`
	- Notification center + mark read.

- `Finance.tsx`, `Insights.tsx`, `Import.tsx`, `Team.tsx`
	- Finance ledger/wallet, AI insight display, import workflow, NGO team management.

## 14) Environment Variables

Backend:
- `NEON_DB` (preferred DB URL)
- `DATABASE_URL` (fallback DB URL)
- `JWT_SECRET`
- `JWT_ALGORITHM` (default `HS256`)
- `JWT_EXPIRE_MINUTES` (default `1440`)
- `GROQ_API_KEY`
- `GROQ_MODEL` (default `llama-3.1-8b-instant`)
- `MAIL_SERVER`
- `MAIL_PORT` (default `587`)
- `MAIL_USE_TLS` (default true)
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `FRONTEND_ORIGINS` (comma-separated CORS allowlist)
- `AUTO_ASSIGN_INTERVAL_SECONDS` (default `60`, min `10`)
- `RESET_PROBLEMS_ON_STARTUP` (default true-like)

Frontend:
- `VITE_API_BASE_URL` (default `http://127.0.0.1:8000/api/v1`)

## 15) Operational Notes and Caveats

1. Token blacklist is in-memory
- Logout revocation does not survive backend restart.

2. Import store is in-memory
- Import upload/preview/confirm data is not persistent.

3. Geocoding is deterministic pseudo geocode
- Not a real geocoding API; useful for stable dev/demo behavior.

4. AI matches endpoint has mixed behavior
- Without `problem_id`: returns persisted `AiMatch` rows.
- With `problem_id`: computes top matches in-memory with placeholder distance logic.

5. Startup reset can wipe problems/tasks
- Controlled by `RESET_PROBLEMS_ON_STARTUP`.

6. Email delivery depends on SMTP credentials
- Code handles transport, but provider account/app-password settings must be valid.

## 16) Local Run Quick Guide

Backend:
1. Create/activate venv.
2. Install `backend/requirements.txt`.
3. Set env vars (`DATABASE_URL`/`NEON_DB`, JWT, optional Groq and mail vars).
4. Run `python backend/main.py` (or uvicorn equivalent).

Frontend:
1. `cd frontend`
2. `npm install`
3. Optional: set `VITE_API_BASE_URL`
4. `npm run dev`

Build check:
- Frontend production build currently passes with `npm run build`.

## 17) LLM Working Guidance

If you are an LLM making code changes in this repo:
- Respect role and auth dependencies in route design.
- Keep schema updates in sync with handler logic and frontend API calls.
- For assignment logic changes, update both startup bootstrap and runtime auto-assignment paths.
- If changing location behavior, review `auth_handler`, `resource_handler`, `problem_handler`, and `ngo_handler` together.
- If changing notification flow, update both DB status and mail behavior expectations.

## 18) Canonical Source Files to Read First

Backend:
- `backend/main.py`
- `backend/routes/routes.py`
- `backend/models/models.py`
- `backend/internal/auto_assignment.py`
- `backend/internal/problem_bootstrap.py`
- `backend/handlers/problem_handler.py`
- `backend/handlers/task_handler.py`

Frontend:
- `frontend/src/App.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/components/Problems.tsx`
- `frontend/src/components/Tasks.tsx`
- `frontend/src/components/Dashboard.tsx`
- `frontend/src/components/MemberDashboard.tsx`

This document reflects the codebase state as of 27 April 2026.
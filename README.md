# Executive Analytics — Team Workspace

A team chat app for running the executive analytics pipeline: drop CSVs and notes in an ongoing chat, get a validated dashboard back, browse past runs as dated tabs.

Full architecture and phased build plan: [`.claude/plans/pure-sprouting-dawn.md`](.claude/plans/pure-sprouting-dawn.md) (or ask your assistant to recap it).

## Layout

- **`reusable_analytics_workflow/`** — the original pandas pipeline (validation, analysis, report/dashboard generation). Reused as-is by the backend; only `build_dashboard.py`'s `build_report()` gains an additive `narrative` argument (Phase D).
- **`backend/`** — FastAPI service. Orchestrates the pipeline, talks to Claude for column mapping + narrative generation, and to Supabase for auth/db/storage.
- **`frontend/`** — Next.js app. Invite-only sign-in, then a 3-pane workspace: run history (left) | ongoing team chat (middle) | live dashboard (right).

## Local development

### 1. Supabase project

Create a project at [supabase.com](https://supabase.com), then run the SQL in `backend/supabase/migrations/` (in order) via the Supabase SQL editor or CLI. Invite teammates from the Supabase dashboard (Authentication → Users → Invite) — signup is invite-only, there is no public signup form.

Copy your project's URL, anon key, and service-role key (Project Settings → API) into the env files below. The backend verifies user tokens by calling Supabase Auth directly (`auth.get_user`), so no separate JWT secret is needed.

**Auth is passwordless** (magic link only — no password step). In Supabase → **Authentication → URL Configuration**, set **Site URL** to your deployed frontend origin, and add `<your-origin>/auth/confirm` to **Redirect URLs**. For local dev, `http://localhost:3000` / `http://localhost:3000/auth/confirm`.

### 2. Backend

```bash
cd backend
python3.11 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY + SUPABASE_* values
./.venv/bin/uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # fill in NEXT_PUBLIC_SUPABASE_* values
npm run dev
```

Or use the Claude Code preview launcher configs in `.claude/launch.json` (`frontend`, `backend`).

Visit `http://localhost:3000` — you'll land on `/login`. Sign in with an account you invited via Supabase.

## Status

Phase A (scaffold, auth, static 3-pane shell) is complete. See the plan file for the remaining phases (chat/run pipeline wiring, Claude column mapping, Claude narrative generation, deploy configs).

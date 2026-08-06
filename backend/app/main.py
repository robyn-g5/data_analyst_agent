from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_chat, routes_runs
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Analytics Chat Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_chat.router)
app.include_router(routes_runs.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# TEMPORARY diagnostic — never exposes the actual secret values, only shape
# info, to debug an env var mismatch on the hosting dashboard. Remove once
# the Supabase connectivity issue is confirmed fixed.
@app.get("/debug/env-shape")
def debug_env_shape() -> dict:
    def shape(value: str) -> dict:
        return {
            "length": len(value),
            "starts_with": value[:6] if value else None,
            "ends_with": value[-6:] if value else None,
            "dot_count": value.count("."),
        }

    return {
        "supabase_url": shape(settings.supabase_url),
        "supabase_service_role_key": shape(settings.supabase_service_role_key),
    }

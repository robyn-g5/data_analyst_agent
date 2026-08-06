from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent
PIPELINE_SCRIPTS_DIR = REPO_ROOT / "reusable_analytics_workflow" / "scripts"
PIPELINE_CONFIG_EXAMPLE = REPO_ROOT / "reusable_analytics_workflow" / "config" / "analysis_config.example.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_ROOT / ".env", extra="ignore")

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-5"

    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_uploads_bucket: str = "chat-uploads"
    supabase_storage_outputs_bucket: str = "run-outputs"

    backend_cors_origins: str = "http://localhost:3000"
    pipeline_workspace_dir: Path = BACKEND_ROOT / "app" / "workspace"
    port: int = 8000
    log_level: str = "info"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_prefix="LEASENS_",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "LeaseLens AI"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/leaselens"
    database_pool_size: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    llm_api_key: str = ""
    llm_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    llm_model: str = "glm-4.1v-thinking-flash"
    llm_timeout_seconds: int = 120

    # Google Places (server-side only)
    google_places_api_key: str = ""
    google_places_search_radius_meters: int = 500

    # Demo auth
    demo_auth_enabled: bool = False
    demo_auth_username: str | None = None
    demo_auth_password: str | None = None
    demo_auth_secret: str | None = None
    demo_auth_cookie_name: str = "leaselens_demo_session"

    # Agent concurrency
    max_concurrent_agents: int = 4
    agent_log_buffer_size: int = 50

    # SSE
    sse_heartbeat_interval: int = 15

    @model_validator(mode="after")
    def validate_demo_auth(self) -> "Settings":
        if not self.demo_auth_enabled:
            return self

        missing = [
            name
            for name, value in (
                ("LEASENS_DEMO_AUTH_USERNAME", self.demo_auth_username),
                ("LEASENS_DEMO_AUTH_PASSWORD", self.demo_auth_password),
                ("LEASENS_DEMO_AUTH_SECRET", self.demo_auth_secret),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                "Demo auth is enabled but required settings are missing: "
                + ", ".join(missing)
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

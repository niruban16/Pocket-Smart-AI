from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default))

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _origins() -> list[str]:
    raw = os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:8000,http://localhost:8000",
    )

    return [
        item.strip()
        for item in raw.split(",")
        if item.strip()
    ]


@dataclass(frozen=True)
class Settings:

    app_name: str = os.getenv(
        "APP_NAME",
        "PocketSmart AI",
    )

    app_env: str = os.getenv(
        "APP_ENV",
        "development",
    )

    secret_key: str = os.getenv(
        "SECRET_KEY",
        "dev-only-change-me",
    )

    database_path: Path = (
        BASE_DIR
        / os.getenv(
            "DATABASE_PATH",
            "data/pocketsmart.db",
        )
    )

    gemini_api_key: str = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    gemini_model: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.8-flash",
    )

    enable_gemini: bool = _bool(
        "ENABLE_GEMINI",
        True,
    )

    cors_origins: list[str] = None  # type: ignore

    access_token_expire_minutes: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "120",
        )
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "cors_origins",
            _origins(),
        )


settings = Settings()

settings.database_path.parent.mkdir(
    parents=True,
    exist_ok=True,
)
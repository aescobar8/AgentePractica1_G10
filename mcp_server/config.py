from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv


REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_ENV = REPO_ROOT / "persona4" / "sog2_postgres_local" / ".env"
SERVER_ENV = Path(__file__).resolve().parent / ".env"


def load_configuration() -> None:
    load_dotenv(SHARED_ENV)
    load_dotenv(SERVER_ENV, override=True)


def get_connection() -> psycopg.Connection:
    parameters: dict[str, Any] = {
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "dbname": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }
    missing = [name for name, value in parameters.items() if not value]
    if missing:
        raise ValueError(
            "Faltan variables de PostgreSQL en mcp_server/.env: "
            + ", ".join(missing)
        )

    sslmode = os.getenv("POSTGRES_SSLMODE")
    if sslmode:
        parameters["sslmode"] = sslmode

    return psycopg.connect(**parameters)

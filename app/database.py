from __future__ import annotations

import json
import sqlite3

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

from app.config import settings


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:

    conn = sqlite3.connect(
        settings.database_path,
        check_same_thread=False,
    )

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA foreign_keys=ON"
    )

    try:
        yield conn
        conn.commit()

    finally:
        conn.close()


def init_db() -> None:

    with get_conn() as conn:

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                request_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );
            """
        )


def create_user(
    name: str,
    email: str,
    password_hash: str,
) -> int:

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_conn() as conn:

        cursor = conn.execute(
            """
            INSERT INTO users(
                name,
                email,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name.strip(),
                email.strip().lower(),
                password_hash,
                now,
            ),
        )

        return int(cursor.lastrowid)


def get_user_by_email(
    email: str,
) -> dict[str, Any] | None:

    with get_conn() as conn:

        row = conn.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (
                email.strip().lower(),
            ),
        ).fetchone()

    return dict(row) if row else None


def get_user_by_id(
    user_id: int,
) -> dict[str, Any] | None:

    with get_conn() as conn:

        row = conn.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    return dict(row) if row else None


def save_recommendation(
    user_id: int,
    category: str,
    request_data: dict[str, Any],
    result: dict[str, Any],
) -> int:

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_conn() as conn:

        cursor = conn.execute(
            """
            INSERT INTO recommendations(
                user_id,
                category,
                request_json,
                result_json,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                category,
                json.dumps(request_data),
                json.dumps(result),
                now,
            ),
        )

        return int(cursor.lastrowid)


def list_recommendations(
    user_id: int,
    limit: int = 25,
) -> list[dict[str, Any]]:

    with get_conn() as conn:

        rows = conn.execute(
            """
            SELECT *
            FROM recommendations
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                user_id,
                limit,
            ),
        ).fetchall()

    output = []

    for row in rows:

        item = dict(row)

        item["request"] = json.loads(
            item.pop("request_json")
        )

        item["result"] = json.loads(
            item.pop("result_json")
        )

        output.append(item)

    return output


def get_recommendation(
    user_id: int,
    recommendation_id: int,
) -> dict[str, Any] | None:

    with get_conn() as conn:

        row = conn.execute(
            """
            SELECT *
            FROM recommendations
            WHERE id = ?
              AND user_id = ?
            """,
            (
                recommendation_id,
                user_id,
            ),
        ).fetchone()

    if not row:
        return None

    item = dict(row)

    item["request"] = json.loads(
        item.pop("request_json")
    )

    item["result"] = json.loads(
        item.pop("result_json")
    )

    return item
from __future__ import annotations

import base64
import hashlib
import hmac
import os

from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


ALGORITHM = "HS256"

PBKDF2_ITERATIONS = 310_000


def hash_password(
    password: str,
) -> str:

    salt = os.urandom(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    return (
        "pbkdf2_sha256$"
        f"{PBKDF2_ITERATIONS}$"
        f"{base64.urlsafe_b64encode(salt).decode('ascii')}$"
        f"{base64.urlsafe_b64encode(digest).decode('ascii')}"
    )


def verify_password(
    password: str,
    encoded: str,
) -> bool:

    try:

        scheme, iterations, salt_b64, digest_b64 = (
            encoded.split("$", 3)
        )

        if scheme != "pbkdf2_sha256":
            return False

        salt = base64.urlsafe_b64decode(
            salt_b64.encode("ascii")
        )

        expected = base64.urlsafe_b64decode(
            digest_b64.encode("ascii")
        )

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )

        return hmac.compare_digest(
            actual,
            expected,
        )

    except (
        ValueError,
        TypeError,
    ):
        return False


def create_access_token(
    user_id: int,
    email: str,
) -> str:

    expires = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(
    token: str,
) -> dict:

    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM],
    )
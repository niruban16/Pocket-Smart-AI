from __future__ import annotations

from fastapi import HTTPException, Request

from app.database import get_user_by_id


def current_user_or_none(request: Request):

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:
        return None

    return get_user_by_id(
        int(user_id)
    )


def require_user(request: Request):

    user = current_user_or_none(request)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Please sign in first.",
        )

    return user
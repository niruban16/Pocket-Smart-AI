from __future__ import annotations

import sqlite3

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from app.database import (
    create_user,
    get_user_by_email,
)

from app.services.auth import (
    create_access_token,
    hash_password,
    verify_password,
)

from app.web import templates


router = APIRouter()


@router.get(
    "/register",
    response_class=HTMLResponse,
)
def register_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "error": None
        },
    )


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):

    if (
        len(name.strip()) < 2
        or len(password) < 8
        or "@" not in email
    ):

        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": (
                    "Enter a valid name, email "
                    "and password of at least "
                    "8 characters."
                )
            },
            status_code=400,
        )

    try:

        user_id = create_user(
            name,
            email,
            hash_password(password),
        )

    except sqlite3.IntegrityError:

        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": (
                    "An account with that "
                    "email already exists."
                )
            },
            status_code=400,
        )

    request.session["user_id"] = user_id

    return RedirectResponse(
        "/dashboard",
        status_code=303,
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None
        },
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):

    user = get_user_by_email(
        email
    )

    if (
        not user
        or not verify_password(
            password,
            user["password_hash"],
        )
    ):

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error":
                    "Invalid email or password."
            },
            status_code=401,
        )

    request.session["user_id"] = user["id"]

    return RedirectResponse(
        "/dashboard",
        status_code=303,
    )


@router.post("/logout")
def logout(
    request: Request,
):

    request.session.clear()

    return RedirectResponse(
        "/",
        status_code=303,
    )


@router.post("/token")
def token(
    email: str = Form(...),
    password: str = Form(...),
):

    user = get_user_by_email(
        email
    )

    if (
        not user
        or not verify_password(
            password,
            user["password_hash"],
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token":
            create_access_token(
                user["id"],
                user["email"],
            ),

        "token_type":
            "bearer",
    }
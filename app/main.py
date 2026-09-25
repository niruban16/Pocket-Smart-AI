from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from fastapi.responses import (
    JSONResponse,
    RedirectResponse,
)

from fastapi.staticfiles import (
    StaticFiles,
)

from starlette.middleware.sessions import (
    SessionMiddleware,
)

from app.config import settings
from app.database import init_db

from app.routes.api_routes import (
    router as api_router,
)

from app.routes.auth_routes import (
    router as auth_router,
)

from app.routes.planner_routes import (
    router as planner_router,
)


BASE = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):

    init_db()

    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    same_site="lax",
    https_only=(
        settings.app_env == "production"
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            BASE / "static"
        )
    ),
    name="static",
)


app.include_router(
    auth_router
)

app.include_router(
    planner_router
)

app.include_router(
    api_router
)


@app.get("/health")
def health():

    return {
        "status": "ok",

        "app":
            settings.app_name,

        "gemini_configured":
            bool(
                settings.gemini_api_key
                and settings.enable_gemini
            ),
    }


@app.get("/startup")
def startup_status():

    return {
        "initialized": True,

        "database":
            str(settings.database_path),

        "gemini_model":
            settings.gemini_model,
    }


@app.exception_handler(401)
async def unauthorized(
    request: Request,
    exc,
):

    if request.url.path.startswith(
        "/api/"
    ):

        return JSONResponse(
            {
                "detail":
                    "Authentication required"
            },
            status_code=401,
        )

    return RedirectResponse(
        "/login",
        status_code=303,
    )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
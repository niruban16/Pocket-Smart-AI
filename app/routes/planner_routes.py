from __future__ import annotations

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from app.database import (
    get_recommendation,
    list_recommendations,
    save_recommendation,
)

from app.dependencies import (
    current_user_or_none,
    require_user,
)

from app.services.recommendations import (
    home_recommendations,
    jewelry_recommendations,
    party_recommendations,
)

from app.web import templates


router = APIRouter()


def _validate_budget(
    value: float,
) -> float:

    if (
        value <= 0
        or value > 10_000_000
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Budget must be between "
                "1 and 10,000,000."
            ),
        )

    return value


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "user":
                current_user_or_none(request)
        },
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(
    request: Request,
):

    user = require_user(
        request
    )

    recent = list_recommendations(
        user["id"],
        limit=5,
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "recent": recent,
        },
    )


@router.get(
    "/home-planner",
    response_class=HTMLResponse,
)
def home_planner(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="home_planner.html",
        context={
            "user":
                require_user(request)
        },
    )


@router.post("/generate-home")
def generate_home(
    request: Request,
    budget: float = Form(...),
    room_type: str = Form(...),
    style: str = Form("modern"),
    city: str = Form(""),
    needs: str = Form(""),
):

    user = require_user(
        request
    )

    data = {
        "budget":
            _validate_budget(budget),

        "room_type":
            room_type.strip(),

        "style":
            style.strip(),

        "city":
            city.strip(),

        "needs":
            needs.strip(),
    }

    result = home_recommendations(
        data
    )

    recommendation_id = save_recommendation(
        user["id"],
        "home",
        data,
        result,
    )

    return RedirectResponse(
        f"/recommendations-details/{recommendation_id}",
        status_code=303,
    )


@router.get(
    "/party-planner",
    response_class=HTMLResponse,
)
def party_planner(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="party_planner.html",
        context={
            "user":
                require_user(request)
        },
    )


@router.post("/generate-party")
def generate_party(
    request: Request,
    budget: float = Form(...),
    event_type: str = Form(...),
    guests: int = Form(...),
    city: str = Form(""),
    preferences: str = Form(""),
):

    user = require_user(
        request
    )

    if (
        guests <= 0
        or guests > 10000
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Guest count must be "
                "between 1 and 10,000."
            ),
        )

    data = {
        "budget":
            _validate_budget(budget),

        "event_type":
            event_type.strip(),

        "guests":
            guests,

        "city":
            city.strip(),

        "preferences":
            preferences.strip(),
    }

    result = party_recommendations(
        data
    )

    recommendation_id = save_recommendation(
        user["id"],
        "party",
        data,
        result,
    )

    return RedirectResponse(
        f"/recommendations-details/{recommendation_id}",
        status_code=303,
    )


@router.get(
    "/jewelry-planner",
    response_class=HTMLResponse,
)
def jewelry_planner(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="jewelry_planner.html",
        context={
            "user":
                require_user(request)
        },
    )


@router.post("/generate-jewelry")
async def generate_jewelry(
    request: Request,
    budget: float = Form(...),
    occasion: str = Form(...),
    outfit_description: str = Form(""),
    metal_preference: str = Form("any"),
    outfit_image: UploadFile | None = File(None),
):

    user = require_user(
        request
    )

    image_bytes = None

    if (
        outfit_image
        and outfit_image.filename
    ):

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if outfit_image.content_type not in allowed_types:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Upload a JPG, PNG "
                    "or WebP image."
                ),
            )

        image_bytes = (
            await outfit_image.read()
        )

        if len(image_bytes) > 5 * 1024 * 1024:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Image must be "
                    "5 MB or smaller."
                ),
            )

    data = {
        "budget":
            _validate_budget(budget),

        "occasion":
            occasion.strip(),

        "outfit_description":
            outfit_description.strip(),

        "metal_preference":
            metal_preference.strip(),
    }

    result = jewelry_recommendations(
        data,
        image_bytes=image_bytes,
    )

    recommendation_id = save_recommendation(
        user["id"],
        "jewelry",
        data,
        result,
    )

    return RedirectResponse(
        f"/recommendations-details/{recommendation_id}",
        status_code=303,
    )


@router.get(
    "/recommendations-details/{recommendation_id}",
    response_class=HTMLResponse,
)
def recommendation_details(
    request: Request,
    recommendation_id: int,
):

    user = require_user(
        request
    )

    recommendation = get_recommendation(
        user["id"],
        recommendation_id,
    )

    if not recommendation:

        raise HTTPException(
            status_code=404,
            detail="Recommendation not found.",
        )

    return templates.TemplateResponse(
        request=request,
        name="recommendations.html",
        context={
            "user": user,
            "rec": recommendation,
        },
    )


@router.get(
    "/history",
    response_class=HTMLResponse,
)
def history(
    request: Request,
):

    user = require_user(
        request
    )

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "user": user,
            "history":
                list_recommendations(
                    user["id"],
                    limit=50,
                ),
        },
    )


@router.get("/session-info")
def session_info(
    request: Request,
):

    user = current_user_or_none(
        request
    )

    return {
        "logged_in":
            bool(user),

        "user": (
            {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
            }
            if user
            else None
        ),
    }


@router.get("/session-data")
def session_data(
    request: Request,
):

    user = require_user(
        request
    )

    history = list_recommendations(
        user["id"],
        limit=10,
    )

    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },

        "recent_recommendations":
            history,
    }
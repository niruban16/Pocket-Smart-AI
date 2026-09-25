from __future__ import annotations

import jwt

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.database import get_user_by_id

from app.models.schemas import (
    HomePlannerInput,
    JewelryPlannerInput,
    PartyPlannerInput,
)

from app.services.auth import (
    decode_access_token,
)

from app.services.recommendations import (
    home_recommendations,
    jewelry_recommendations,
    party_recommendations,
)


router = APIRouter(
    prefix="/api",
    tags=["api"],
)


bearer = HTTPBearer(
    auto_error=False
)


def api_user(
    request: Request,
    credentials:
        HTTPAuthorizationCredentials | None =
        Depends(bearer),
):

    user_id = request.session.get(
        "user_id"
    )

    if not user_id and credentials:

        try:

            payload = decode_access_token(
                credentials.credentials
            )

            user_id = int(
                payload["sub"]
            )

        except (
            jwt.PyJWTError,
            ValueError,
            KeyError,
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

    user = (
        get_user_by_id(
            int(user_id)
        )
        if user_id
        else None
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    return user


@router.post("/home")
def api_home(
    payload: HomePlannerInput,
    user=Depends(api_user),
):

    return home_recommendations(
        payload.model_dump()
    )


@router.post("/party")
def api_party(
    payload: PartyPlannerInput,
    user=Depends(api_user),
):

    return party_recommendations(
        payload.model_dump()
    )


@router.post("/jewelry")
def api_jewelry(
    payload: JewelryPlannerInput,
    user=Depends(api_user),
):

    return jewelry_recommendations(
        payload.model_dump()
    )
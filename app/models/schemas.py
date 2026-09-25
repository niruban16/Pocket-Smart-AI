from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=80,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class HomePlannerInput(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    room_type: str = Field(
        min_length=2,
        max_length=80,
    )

    style: str = Field(
        default="modern",
        max_length=80,
    )

    city: str = Field(
        default="",
        max_length=100,
    )

    needs: str = Field(
        default="",
        max_length=800,
    )


class PartyPlannerInput(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    event_type: str = Field(
        min_length=2,
        max_length=80,
    )

    guests: int = Field(
        gt=0,
        le=10000,
    )

    city: str = Field(
        default="",
        max_length=100,
    )

    preferences: str = Field(
        default="",
        max_length=800,
    )


class JewelryPlannerInput(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    occasion: str = Field(
        min_length=2,
        max_length=80,
    )

    outfit_description: str = Field(
        default="",
        max_length=800,
    )

    metal_preference: str = Field(
        default="any",
        max_length=80,
    )


class RecommendationItem(BaseModel):

    name: str

    category: str

    estimated_price: float

    platform: str

    reason: str

    search_url: str


class RecommendationResult(BaseModel):

    planner: Literal[
        "home",
        "party",
        "jewelry",
    ]

    summary: str

    budget: float

    estimated_total: float

    budget_remaining: float

    items: list[
        RecommendationItem
    ]

    tips: list[str]

    ai_used: bool = False

    image_insight: str | None = None
from __future__ import annotations

from typing import Any

from app.services.gemini_utils import gemini
from app.services.marketplace import search_url


def _item(
    name: str,
    category: str,
    price: float,
    platform: str,
    reason: str,
) -> dict[str, Any]:

    return {
        "name": name,
        "category": category,
        "estimated_price": round(
            max(price, 0),
            2,
        ),
        "platform": platform,
        "reason": reason,
        "search_url": search_url(
            platform,
            name,
        ),
    }


def _normalize(
    planner: str,
    budget: float,
    raw: dict[str, Any] | None,
    fallback: dict[str, Any],
) -> dict[str, Any]:

    source = (
        raw
        if isinstance(raw, dict)
        else fallback
    )

    normalized = []

    running = 0.0

    for entry in source.get(
        "items",
        [],
    )[:8]:

        try:

            price = max(
                0.0,
                float(
                    entry.get(
                        "estimated_price",
                        0,
                    )
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            continue

        if (
            running + price > budget
            and normalized
        ):
            continue

        platform = str(
            entry.get(
                "platform",
                "Amazon",
            )
        )

        name = str(
            entry.get(
                "name",
                "Recommended option",
            )
        )

        normalized.append(
            _item(
                name,
                str(
                    entry.get(
                        "category",
                        planner.title(),
                    )
                ),
                price,
                platform,
                str(
                    entry.get(
                        "reason",
                        "Fits the plan and budget.",
                    )
                ),
            )
        )

        running += price

    if not normalized:

        if source is not fallback:

            return _normalize(
                planner,
                budget,
                fallback,
                fallback,
            )

        return {
            "planner": planner,
            "summary": (
                "No suitable recommendations "
                "were generated."
            ),
            "budget": budget,
            "estimated_total": 0.0,
            "budget_remaining": budget,
            "items": [],
            "tips": [],
            "ai_used": False,
            "image_insight": None,
        }

    return {
        "planner": planner,

        "summary": str(
            source.get(
                "summary",
                fallback.get(
                    "summary",
                    "Budget-aware recommendations.",
                ),
            )
        ),

        "budget": round(
            budget,
            2,
        ),

        "estimated_total": round(
            running,
            2,
        ),

        "budget_remaining": round(
            max(
                0.0,
                budget - running,
            ),
            2,
        ),

        "items": normalized,

        "tips": [
            str(t)
            for t in source.get(
                "tips",
                fallback.get(
                    "tips",
                    [],
                ),
            )
        ][:6],

        "ai_used": raw is not None,

        "image_insight": source.get(
            "image_insight"
        ),
    }


def _home_fallback(
    data: dict[str, Any],
) -> dict[str, Any]:

    budget = float(
        data["budget"]
    )

    room = data.get(
        "room_type",
        "room",
    )

    style = data.get(
        "style",
        "modern",
    )

    allocations = [

        (
            "Core furniture",
            0.42,
            "IKEA",
            f"{style} {room} essential furniture",
        ),

        (
            "Storage solution",
            0.18,
            "Amazon",
            f"space-saving storage for {room}",
        ),

        (
            "Lighting",
            0.14,
            "Flipkart",
            f"{style} ambient lighting",
        ),

        (
            "Soft furnishing",
            0.14,
            "Amazon",
            f"{style} cushions curtains rug",
        ),

        (
            "Wall decor",
            0.08,
            "IKEA",
            f"{style} wall decor",
        ),
    ]

    items = []

    for (
        name,
        percentage,
        platform,
        query,
    ) in allocations:

        items.append(
            _item(
                name,
                name,
                budget * percentage,
                platform,
                (
                    f"Allocates about "
                    f"{int(percentage * 100)}% "
                    f"of the budget to "
                    f"{name.lower()}."
                ),
            )
        )

    return {
        "summary": (
            f"A balanced {style} plan for "
            f"your {room} with priority "
            f"on useful essentials first."
        ),

        "items": items,

        "tips": [
            "Measure the room before ordering large furniture.",
            "Keep a small contingency for delivery or installation.",
            "Compare material, dimensions and return policies before purchase.",
        ],
    }


def _party_fallback(
    data: dict[str, Any],
) -> dict[str, Any]:

    budget = float(
        data["budget"]
    )

    event = data.get(
        "event_type",
        "event",
    )

    guests = int(
        data.get(
            "guests",
            1,
        )
    )

    per_guest = (
        budget /
        max(guests, 1)
    )

    allocations = [

        (
            "Food & catering",
            "Catering",
            0.48,
            "Zomato",
            f"{event} catering for {guests} guests",
        ),

        (
            "Venue / stay option",
            "Venue",
            0.20,
            "OYO",
            f"{event} venue for {guests} guests",
        ),

        (
            "Decor package",
            "Decoration",
            0.18,
            "Amazon",
            f"{event} decoration kit",
        ),

        (
            "Cake / snacks add-on",
            "Food",
            0.09,
            "Swiggy",
            f"{event} cake snacks",
        ),
    ]

    items = []

    for (
        name,
        category,
        percentage,
        platform,
        query,
    ) in allocations:

        items.append(
            _item(
                name,
                category,
                budget * percentage,
                platform,
                (
                    "Estimated allocation for "
                    f"{category.lower()} while keeping "
                    "the whole plan within budget."
                ),
            )
        )

    return {
        "summary": (
            f"A practical {event} plan for "
            f"{guests} guests "
            f"(roughly ₹{per_guest:,.0f} "
            "available per guest overall)."
        ),

        "items": items,

        "tips": [
            "Confirm taxes, delivery and venue deposits before finalizing.",
            "Request final catering quantities based on confirmed RSVPs.",
            "Keep 5–10% unspent for last-minute changes.",
        ],
    }


def _jewelry_fallback(
    data: dict[str, Any],
    has_image: bool,
) -> dict[str, Any]:

    budget = float(
        data["budget"]
    )

    occasion = data.get(
        "occasion",
        "occasion",
    )

    metal = data.get(
        "metal_preference",
        "any",
    )

    allocations = [

        (
            "Statement necklace / chain",
            "Neckwear",
            0.48,
            "Tanishq",
        ),

        (
            "Matching earrings",
            "Earrings",
            0.30,
            "Myntra",
        ),

        (
            "Bracelet / bangle",
            "Wristwear",
            0.17,
            "Amazon",
        ),
    ]

    items = []

    for (
        name,
        category,
        percentage,
        platform,
    ) in allocations:

        items.append(
            _item(
                name,
                category,
                budget * percentage,
                platform,
                (
                    f"Chosen as a coordinated "
                    f"{metal} option for a "
                    f"{occasion} look."
                ),
            )
        )

    return {
        "summary": (
            f"A coordinated jewelry set "
            f"for {occasion}, weighted "
            "toward one focal piece and "
            "supporting accessories."
        ),

        "items": items,

        "tips": [
            "Match jewelry scale to the neckline and outfit detailing.",
            "Check plating/material details and skin-sensitivity information.",
            "Treat listed prices as estimates and verify current seller pricing.",
        ],

        "image_insight": (
            "An outfit image was supplied; "
            "AI image analysis will be used "
            "when a Gemini API key is configured."
            if has_image
            else None
        ),
    }


def home_recommendations(
    data: dict[str, Any],
) -> dict[str, Any]:

    raw = gemini.recommend(
        "home",
        data,
    )

    return _normalize(
        "home",
        float(data["budget"]),
        raw,
        _home_fallback(data),
    )


def party_recommendations(
    data: dict[str, Any],
) -> dict[str, Any]:

    raw = gemini.recommend(
        "party",
        data,
    )

    return _normalize(
        "party",
        float(data["budget"]),
        raw,
        _party_fallback(data),
    )


def jewelry_recommendations(
    data: dict[str, Any],
    image_bytes: bytes | None = None,
) -> dict[str, Any]:

    raw = gemini.recommend(
        "jewelry",
        data,
        image_bytes=image_bytes,
    )

    return _normalize(
        "jewelry",
        float(data["budget"]),
        raw,
        _jewelry_fallback(
            data,
            bool(image_bytes),
        ),
    )
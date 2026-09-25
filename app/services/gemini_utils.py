from __future__ import annotations

import json

from io import BytesIO
from typing import Any

from PIL import Image

from app.config import settings


class GeminiService:

    def __init__(self) -> None:

        self.enabled = bool(
            settings.enable_gemini
            and settings.gemini_api_key
        )

        self.client = None

        self.types = None

        if self.enabled:

            try:

                from google import genai
                from google.genai import types

                self.client = genai.Client(
                    api_key=settings.gemini_api_key
                )

                self.types = types

            except ImportError:

                self.enabled = False

    def _call(
        self,
        prompt: str,
        image_bytes: bytes | None = None,
    ) -> dict[str, Any] | None:

        if not self.client or not self.types:
            return None

        contents: list[Any] = [
            prompt
        ]

        if image_bytes:

            try:

                image = Image.open(
                    BytesIO(image_bytes)
                )

                contents.append(image)

            except Exception:
                pass

        try:

            response = (
                self.client.models.generate_content(
                    model=settings.gemini_model,
                    contents=contents,
                    config=(
                        self.types.GenerateContentConfig(
                            temperature=0.35,
                            response_mime_type="application/json",
                        )
                    ),
                )
            )

            if not response.text:
                return None

            return json.loads(
                response.text
            )

        except Exception:

            return None

    @staticmethod
    def prompt(
        planner: str,
        data: dict[str, Any],
    ) -> str:

        return f"""
You are PocketSmart AI, a budget-aware recommendation
assistant for users in India.

Planner:
{planner}

User data:
{json.dumps(data, ensure_ascii=False)}

Return ONLY valid JSON using this exact structure:

{{
  "summary": "short practical summary",

  "items": [
    {{
      "name": "...",
      "category": "...",
      "estimated_price": 1234,
      "platform": "Amazon|Flipkart|IKEA|Swiggy|Zomato|OYO|Myntra|Tanishq",
      "reason": "..."
    }}
  ],

  "tips": [
    "...",
    "..."
  ],

  "image_insight": null
}}

Rules:

1. Keep the total estimated_price at or below the supplied budget.

2. Prefer 4 to 7 concrete,
   category-relevant suggestions.

3. Prices are estimates.
   Never claim real-time prices or availability.

4. For party planning distribute the budget sensibly
   among food/catering, venue, decoration and entertainment.

5. For home planning cover useful
   furniture, decor and lighting based on room,
   style and needs.

6. For jewelry use occasion, outfit and optional image cues.

7. Do not identify people in uploaded images.

8. Do not fabricate product IDs.

9. Do not fabricate discounts.

10. Make suggestions platform-aware.
""".strip()

    def recommend(
        self,
        planner: str,
        data: dict[str, Any],
        image_bytes: bytes | None = None,
    ) -> dict[str, Any] | None:

        prompt = self.prompt(
            planner,
            data,
        )

        return self._call(
            prompt,
            image_bytes=image_bytes,
        )


gemini = GeminiService()
from __future__ import annotations

from urllib.parse import quote_plus


PLATFORM_SEARCH = {

    "Amazon":
        "https://www.amazon.in/s?k={q}",

    "Flipkart":
        "https://www.flipkart.com/search?q={q}",

    "IKEA":
        "https://www.ikea.com/in/en/search/?q={q}",

    "Swiggy":
        "https://www.swiggy.com/search?query={q}",

    "Zomato":
        "https://www.zomato.com/search?q={q}",

    "OYO":
        "https://www.oyorooms.com/search/?q={q}",

    "Myntra":
        "https://www.myntra.com/{q}",

    "Tanishq":
        "https://www.tanishq.co.in/search?q={q}",
}


def search_url(
    platform: str,
    query: str,
) -> str:

    template = PLATFORM_SEARCH.get(
        platform,
        "https://www.google.com/search?q={q}",
    )

    return template.format(
        q=quote_plus(query.strip())
    )
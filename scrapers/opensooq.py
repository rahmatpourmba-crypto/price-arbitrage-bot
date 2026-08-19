import asyncio
import re
import urllib.parse
from core import Supplier
from config import USER_AGENT
from .http import curl_get


def _parse_opensooq_sync(query: str, limit: int = 10, country: str = "jo") -> list[Supplier]:
    base = f"https://{country}.opensooq.com"
    encoded = urllib.parse.quote(query)
    url = f"{base}/en/find/search?q={encoded}"
    html = curl_get(url, headers=["Accept-Language: en-US,en;q=0.9,ar;q=0.8"])
    if not html:
        return []

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    suppliers = []
    cards = soup.select(
        "[class*='listing'], [class*='post'], [data-listing-id], a[href*='/post/']"
    )
    for card in cards[:limit]:
        title_el = card.select_one("h2, h3, [class*='title'], [class*='name']")
        price_el = card.select_one("[class*='price'], [class*='Price']")
        title = title_el.get_text(strip=True) if title_el else ""
        price = 0
        if price_el:
            nums = re.findall(r"\d+", price_el.get_text(strip=True).replace(",", ""))
            if nums:
                try:
                    price = int(nums[0])
                except ValueError:
                    pass
        link = card.get("href", "")
        if not link:
            link_el = card.select_one("a[href]")
            if link_el:
                link = link_el.get("href", "")
        if link and not link.startswith("http"):
            link = f"{base}{link}"
        if title:
            suppliers.append(Supplier(name=title, price=price, site="opensooq", url=link))
    return suppliers


async def search_opensooq(query: str, limit: int = 10, country: str = "jo") -> list[Supplier]:
    try:
        return await asyncio.to_thread(_parse_opensooq_sync, query, limit, country)
    except Exception as e:
        print(f"[opensooq] error: {e}")
        return []

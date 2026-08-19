import asyncio
import re
from bs4 import BeautifulSoup
from core import Supplier
from config import BUSKOOL_BASE
from .http import curl_get


def _parse_buskool_sync(query: str, limit: int = 10) -> list[Supplier]:
    import urllib.parse
    encoded = urllib.parse.quote(query)
    url = f"{BUSKOOL_BASE}/product-list/search?query={encoded}"
    html = curl_get(url, headers=["Accept-Language: fa-IR,fa;q=0.9"])
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    suppliers = []
    cards = soup.select("[class*='product'], [class*='card'], [class*='item']")
    for card in cards[:limit]:
        title_el = card.select_one("h2, h3, h4, [class*='title'], [class*='name']")
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
        link = ""
        link_el = card.select_one("a[href]")
        if link_el:
            link = link_el.get("href", "")
        if link and not link.startswith("http"):
            link = f"{BUSKOOL_BASE}{link}"
        if title:
            suppliers.append(Supplier(name=title, price=price, site="buskool", url=link))
    return suppliers


async def search_buskool(query: str, limit: int = 10) -> list[Supplier]:
    try:
        return await asyncio.to_thread(_parse_buskool_sync, query, limit)
    except Exception as e:
        print(f"[buskool] error: {e}")
        return []

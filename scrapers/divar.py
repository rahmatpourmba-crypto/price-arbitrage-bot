import asyncio
import re
from core import Supplier, Buyer
from config import DIVAR_BASE, DIVAR_CITIES
from .http import curl_post_json


def _parse_price_text(text: str) -> int | None:
    if not text:
        return None
    nums = re.findall(r"\d+", text.replace(",", "").replace("\u060c", ""))
    if nums:
        try:
            return int(nums[0])
        except ValueError:
            return None
    return None


def _divar_search_sync(query: str, city: str = "tehran", category: str = "ROOT",
                       limit: int = 10, min_price: int = 0, for_buyers: bool = False) -> dict:
    city_code = DIVAR_CITIES.get(city, DIVAR_CITIES["tehran"])
    url = f"{DIVAR_BASE}/web-search/{city_code}/{category}"
    payload = {
        "json_schema": {
            "category": {"value": category},
            "cities": [city_code],
            "query": query,
        },
        "last-post-date": 0,
        "page": 1,
    }
    if min_price:
        payload["json_schema"]["price"] = {"min": min_price}
    return curl_post_json(url, payload) or {}


def _parse_divar_posts(data: dict, limit: int, for_buyers: bool = False):
    results = []

    ww = data.get("web_widgets", {})
    for p in ww.get("post_list", [])[:limit]:
        pd = p.get("data", {})
        token = pd.get("token", "")
        title = pd.get("title", "")
        price_text = pd.get("middle_description_text", "")
        price = _parse_price_text(price_text)
        results.append({"token": token, "title": title, "price": price, "price_text": price_text})

    wl = data.get("widget_list", [])
    for w in wl:
        wt = w.get("widget_type", "")
        if "POST" in wt.upper():
            posts = w.get("data", {}).get("post_list", [])
            if isinstance(posts, list):
                for p in posts[:limit]:
                    pd = p.get("data", p)
                    token = pd.get("token", "")
                    title = pd.get("title", "")
                    price_text = pd.get("middle_description_text", "")
                    price = _parse_price_text(price_text)
                    results.append({"token": token, "title": title, "price": price, "price_text": price_text})

    return results[:limit]


async def search_divar(query: str, city: str = "tehran", category: str = "ROOT",
                       limit: int = 10, min_price: int = 0) -> list[Supplier]:
    try:
        data = await asyncio.to_thread(_divar_search_sync, query, city, category, limit, min_price)
        posts = _parse_divar_posts(data, limit)
        return [
            Supplier(
                name=p["title"],
                price=p["price"] or 0,
                site="divar",
                url=f"https://divar.ir/v/{p['token']}" if p["token"] else "",
                shop_name=p["price_text"],
            )
            for p in posts
        ]
    except Exception as e:
        print(f"[divar] error: {e}")
        return []


async def search_divar_buyers(query: str, city: str = "tehran",
                              category: str = "ROOT", limit: int = 10) -> list[Buyer]:
    try:
        search_query = f"\u062e\u0631\u06cc\u062f\u0627\u0631\u0645 {query}"
        data = await asyncio.to_thread(_divar_search_sync, search_query, city, category, limit)
        posts = _parse_divar_posts(data, limit)
        return [
            Buyer(
                title=p["title"],
                price=p["price"],
                site="divar",
                url=f"https://divar.ir/v/{p['token']}" if p["token"] else "",
                description=p["price_text"],
                post_id=p["token"],
            )
            for p in posts
        ]
    except Exception as e:
        print(f"[divar-buyers] error: {e}")
        return []

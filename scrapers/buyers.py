import json
import re
from .http import http_get, http_get_json


def search_divar_buyers(query: str, city: str = "tehran", limit: int = 10) -> list[dict]:
    import urllib.parse
    encoded = urllib.parse.quote(f"خریدار {query}")
    url = f"https://divar.ir/s/{city}/?q={encoded}"
    r = http_get(url)
    if not r:
        return []

    html = r.text
    m = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});?\s*</script>',
        html, re.DOTALL,
    )
    if not m:
        return []

    try:
        state = json.loads(m.group(1))
    except Exception:
        return []

    posts = []
    seen_tokens = set()

    def extract(obj, depth=0):
        if depth > 12:
            return
        if isinstance(obj, dict):
            title = obj.get("title", "")
            token = obj.get("token", "") or obj.get("post_token", "")
            action = obj.get("action", {})

            if not token and isinstance(action, dict):
                open_post = action.get("open_post", {})
                if isinstance(open_post, dict):
                    token = open_post.get("post_token", "")

            if title and token and token not in seen_tokens:
                seen_tokens.add(token)
                district = ""
                if isinstance(obj.get("district"), dict):
                    district = obj["district"].get("name", "")
                elif isinstance(obj.get("district"), str):
                    district = obj["district"]

                price_val = obj.get("price", "")
                red_text = obj.get("red_text", "")
                green_text = obj.get("green_text", "")
                top_desc = obj.get("top_description_text", "")
                mid_desc = obj.get("middle_description_text", "")
                badge = obj.get("badge", "")
                is_store = "فروشگاه" in str(obj.get("price", "")) or "فروشگاه" in str(badge)

                desc = top_desc or mid_desc or ""

                posts.append({
                    "title": title,
                    "token": token,
                    "url": f"https://divar.ir/v/{token}",
                    "district": district,
                    "price": price_val if price_val else red_text,
                    "condition": green_text,
                    "description": desc,
                    "is_store": is_store,
                    "badge": badge,
                })

            for v in obj.values():
                extract(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, depth + 1)

    extract(state)
    return posts[:limit]


def search_sheypoor_buyers(query: str, limit: int = 10) -> list[dict]:
    import urllib.parse
    encoded = urllib.parse.quote(f"خریدار {query}")
    url = f"https://www.sheypoor.com/search?q={encoded}"
    r = http_get(url)
    if not r:
        return []

    html = r.text
    posts = []

    titles = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html)
    for t in titles[:limit]:
        clean = re.sub(r'<[^>]+>', '', t).strip()
        if clean and len(clean) > 5:
            posts.append({
                "title": clean,
                "url": url,
                "platform": "sheypoor",
            })

    phones = list(set(re.findall(r'09\d{9}', html)))
    if phones:
        posts.append({"phones": phones[:5], "platform": "sheypoor_contacts"})

    return posts


def search_google_buyers(query: str, limit: int = 10) -> list[dict]:
    import urllib.parse
    encoded = urllib.parse.quote(f"خریدارم {query}")
    url = f"https://www.google.com/search?q={encoded}&hl=fa&num={limit}&gl=ir"
    r = http_get(url)
    if not r:
        return []

    html = r.text
    results = []

    links = re.findall(r'<a[^>]*href="/url\?q=([^&"]+)', html)
    titles_raw = re.findall(r'<h3[^>]*>(.*?)</h3>', html)

    for link, title in zip(links[:limit], titles_raw[:limit]):
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        if clean_title:
            results.append({
                "title": clean_title,
                "url": link,
                "platform": "google",
            })

    return results


def search_divar_products(query: str, city: str = "tehran", limit: int = 10) -> list[dict]:
    """Search Divar for product listings (sellers), not buyer posts."""
    import urllib.parse
    encoded = urllib.parse.quote(query)
    url = f"https://divar.ir/s/{city}/?q={encoded}"
    r = http_get(url)
    if not r:
        return []

    html = r.text
    m = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});?\s*</script>',
        html, re.DOTALL,
    )
    if not m:
        return []

    try:
        state = json.loads(m.group(1))
    except Exception:
        return []

    posts = []
    seen_tokens = set()

    def extract(obj, depth=0):
        if depth > 12:
            return
        if isinstance(obj, dict):
            title = obj.get("title", "")
            token = obj.get("token", "") or obj.get("post_token", "")
            action = obj.get("action", {})
            if not token and isinstance(action, dict):
                open_post = action.get("open_post", {})
                if isinstance(open_post, dict):
                    token = open_post.get("post_token", "")

            if title and token and token not in seen_tokens:
                seen_tokens.add(token)
                district = ""
                if isinstance(obj.get("district"), dict):
                    district = obj["district"].get("name", "")
                elif isinstance(obj.get("district"), str):
                    district = obj["district"]

                price_val = obj.get("price", "")
                red_text = obj.get("red_text", "")
                green_text = obj.get("green_text", "")
                badge = obj.get("badge", "")
                is_store = "فروشگاه" in str(price_val) or "فروشگاه" in str(badge)

                posts.append({
                    "title": title,
                    "token": token,
                    "url": f"https://divar.ir/v/{token}",
                    "district": district,
                    "price": price_val if price_val else red_text,
                    "condition": green_text,
                    "is_store": is_store,
                    "badge": badge,
                })

            for v in obj.values():
                extract(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, depth + 1)

    extract(state)
    return posts[:limit]


def search_international_buyers(query: str) -> list[dict]:
    import urllib.parse
    encoded = urllib.parse.quote(query)
    links = [
        {"title": "علی‌بابا (B2B بین‌المللی)", "url": f"https://www.alibaba.com/trade/search?SearchText={encoded}", "platform": "alibaba"},
        {"title": "آمازون (تقاضای بازار)", "url": f"https://www.amazon.com/s?k={encoded}", "platform": "amazon"},
        {"title": "eBay (تقاضای بازار)", "url": f"https://www.ebay.com/sch/i.html?_nkw={encoded}", "platform": "ebay"},
        {"title": "AliExpress (خریداران جهانی)", "url": f"https://www.aliexpress.com/wholesale?SearchText={encoded}", "platform": "aliexpress"},
    ]
    return links

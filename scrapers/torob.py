from .http import curl_get_json
import urllib.parse

TOROB_API = "https://api.torob.com/v4/base-product"


def search_torob_raw(query: str, limit: int = 10) -> list[dict]:
    encoded = urllib.parse.quote(query)
    url = f"{TOROB_API}/search/?q={encoded}&page=0&sort_by=price_asc&size={limit}"
    data = curl_get_json(url, extra_headers=["Referer: https://torob.com/"])
    if not data:
        return []
    return data.get("results", [])


def get_torob_suppliers(query: str, limit: int = 5) -> list[dict]:
    results = search_torob_raw(query, limit)
    if not results:
        return []

    suppliers = []
    for item in results[:limit]:
        prk = item.get("random_key", "")
        product_name = item.get("name1", "")
        lowest_price = item.get("price", 0)
        url_path = item.get("web_client_absolute_url", "")
        product_url = f"https://torob.com{url_path}" if url_path else ""

        sellers = []
        if prk:
            detail_url = (
                f"{TOROB_API}/details/?source=torob_search"
                f"&discover_method=search&prk={prk}&rank=0&cities="
            )
            detail_data = curl_get_json(detail_url, extra_headers=["Referer: https://torob.com/"])
            if detail_data:
                pi = detail_data.get("products_info", {})
                raw_sellers = pi.get("result", [])
                for s in raw_sellers[:8]:
                    seller = {
                        "name": s.get("shop_name", "") or s.get("name1", "")[:40],
                        "city": s.get("shop_name2", ""),
                        "price": s.get("price", 0),
                        "price_text": s.get("price_text", ""),
                        "score": s.get("shop_score", 0),
                        "warranty": s.get("guarantee_info", {}).get("status") == "enabled",
                        "shipping": s.get("postage_fee", ""),
                        "url": s.get("page_url", ""),
                        "shop_id": s.get("shop_id", ""),
                    }
                    more = s.get("more_info", {})
                    if more:
                        if more.get("same_day_delivery"):
                            seller["delivery"] = True
                        if more.get("free_shipping"):
                            seller["free_shipping"] = True
                    sellers.append(seller)

        suppliers.append({
            "product_name": product_name,
            "lowest_price": lowest_price,
            "product_url": product_url,
            "shop_count": item.get("shop_text", ""),
            "sellers": sellers,
        })

    return suppliers

import json
import re
import urllib.parse
from .http import http_get, http_get_json


IRAN_CITIES = {
    "tehran": "تهران",
    "tabriz": "تبریز",
    "isfahan": "اصفهان",
    "mashhad": "مشهد",
    "ahvaz": "اهواز",
    "shiraz": "شیراز",
    "kermanshah": "کرمانشاه",
    "sanandaj": "سنندج",
    "urumia": "ارومیه",
    "rasht": "رشت",
    "kerman": "کرمان",
    "yazd": "یزد",
    "zanjan": "زنجان",
    "bandar_abbas": "بندرعباس",
    "kish": "کیش",
}

KURDISTAN_IRQ = {
    "name": "اقلیم کوردستان عراق",
    "cities": {
        "erbil": {
            "name": "اربیل (هولیر)",
            "flag": "🇮🇶",
            "platforms": {
                "haraj": "https://haraj.com.sa/en/search?q={q}+erbil",
                "bazar1": "https://bazar1.com/en/search?q={q}+erbil",
                "opensooq": "https://iq.opensooq.com/en/find/search?q={q}",
                "facebook_marketplace": "https://www.facebook.com/marketplace/erbil/search/?query={q}",
                "facebook_groups": "https://www.facebook.com/search/groups/?q=buy+{q}+erbil",
                "instagram": "https://www.instagram.com/explore/tags/buy{q}erbil/",
            },
        },
        "sulaymaniyah": {
            "name": "سلیمانیه",
            "flag": "🇮🇶",
            "platforms": {
                "haraj": "https://haraj.com.sa/en/search?q={q}+sulaymaniyah",
                "bazar1": "https://bazar1.com/en/search?q={q}+sulaymaniyah",
                "opensooq": "https://iq.opensooq.com/en/find/search?q={q}",
                "facebook_marketplace": "https://www.facebook.com/marketplace/sulaymaniyah/search/?query={q}",
                "facebook_groups": "https://www.facebook.com/search/groups/?q=buy+{q}+sulaymaniyah",
            },
        },
        "duhok": {
            "name": "دهوک",
            "flag": "🇮🇶",
            "platforms": {
                "haraj": "https://haraj.com.sa/en/search?q={q}+duhok",
                "bazar1": "https://bazar1.com/en/search?q={q}+duhok",
                "facebook_marketplace": "https://www.facebook.com/marketplace/duhok/search/?query={q}",
                "facebook_groups": "https://www.facebook.com/search/groups/?q=buy+{q}+duhok",
            },
        },
    },
}

GULF_COUNTRIES = {
    "uae": {
        "name": "امارات متحده عربی",
        "flag": "🇦🇪",
        "platforms": {
            "dubizzle": "https://www.dubizzle.com/en/search?q={q}",
            "opensooq": "https://ae.opensooq.com/en/find/search?q={q}",
            "bayan": "https://www.bayan.com/search?q={q}",
            "facebook_marketplace": "https://www.facebook.com/marketplace/dubai/search/?query={q}",
            "instagram": "https://www.instagram.com/explore/tags/buy{q}uae/",
            "amazon_ae": "https://www.amazon.ae/s?k={q}",
        },
    },
    "saudi": {
        "name": "عربستان سعودی",
        "flag": "🇸🇦",
        "platforms": {
            "haraj": "https://haraj.com.sa/en/search?q={q}",
            "opensooq": "https://sa.opensooq.com/en/find/search?q={q}",
            "extra": "https://www.extra.com/search?q={q}",
            "facebook_marketplace": "https://www.facebook.com/marketplace/riyadh/search/?query={q}",
            "instagram": "https://www.instagram.com/explore/tags/buy{q}saudi/",
            "amazon_sa": "https://www.amazon.sa/s?k={q}",
        },
    },
    "kuwait": {
        "name": "کویت",
        "flag": "🇰🇼",
        "platforms": {
            "opensooq": "https://kw.opensooq.com/en/find/search?q={q}",
            "4sale": "https://4sale.com.kw/en/search?q={q}",
            "facebook_marketplace": "https://www.facebook.com/marketplace/kuwait/search/?query={q}",
            "instagram": "https://www.instagram.com/explore/tags/buy{q}kuwait/",
        },
    },
    "qatar": {
        "name": "قطر",
        "flag": "🇶🇦",
        "platforms": {
            "opensooq": "https://qa.opensooq.com/en/find/search?q={q}",
            "qatarliving": "https://www.qatarliving.com/classifieds?search={q}",
            "facebook_marketplace": "https://www.facebook.com/marketplace/doha/search/?query={q}",
        },
    },
    "bahrain": {
        "name": "بحرین",
        "flag": "🇧🇭",
        "platforms": {
            "opensooq": "https://bh.opensooq.com/en/find/search?q={q}",
            "facebook_marketplace": "https://www.facebook.com/marketplace/manama/search/?query={q}",
        },
    },
    "oman": {
        "name": "عمان",
        "flag": "🇴🇲",
        "platforms": {
            "opensooq": "https://om.opensooq.com/en/find/search?q={q}",
            "facebook_marketplace": "https://www.facebook.com/marketplace/muscat/search/?query={q}",
        },
    },
}


def search_divar_multi_city(query: str, cities: list[str] | None = None, limit_per_city: int = 5) -> list[dict]:
    if cities is None:
        cities = ["tehran", "tabriz", "sanandaj", "ahvaz", "mashhad", "kermanshah"]

    all_posts = []
    buyer_query = f"خریدار {query}"

    for city in cities:
        encoded = urllib.parse.quote(buyer_query)
        url = f"https://divar.ir/s/{city}/?q={encoded}"
        r = http_get(url)
        if not r:
            continue

        html = r.text
        m = re.search(
            r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});?\s*</script>',
            html, re.DOTALL,
        )
        if not m:
            continue

        try:
            state = json.loads(m.group(1))
        except Exception:
            continue

        seen = set()

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

                if title and token and token not in seen:
                    seen.add(token)
                    district = ""
                    if isinstance(obj.get("district"), dict):
                        district = obj["district"].get("name", "")
                    elif isinstance(obj.get("district"), str):
                        district = obj["district"]

                    all_posts.append({
                        "title": title,
                        "token": token,
                        "url": f"https://divar.ir/v/{token}",
                        "city": IRAN_CITIES.get(city, city),
                        "district": district,
                        "price": obj.get("price", "") or obj.get("red_text", ""),
                        "condition": obj.get("green_text", ""),
                        "is_store": "فروشگاه" in str(obj.get("price", "")),
                    })

                for v in obj.values():
                    extract(v, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, depth + 1)

        extract(state)

    return all_posts[:limit_per_city * len(cities)]


def get_all_regional_links(query: str) -> dict[str, list[dict]]:
    q_en = urllib.parse.quote(query)
    q_fa_buyer = urllib.parse.quote(f"خریدار {query}")
    links = {}

    links["kurdistan_iraq"] = []
    for city_key, city_cfg in KURDISTAN_IRQ["cities"].items():
        for platform, url_template in city_cfg["platforms"].items():
            url = url_template.replace("{q}", q_en)
            links["kurdistan_iraq"].append({
                "region": city_cfg["name"],
                "flag": city_cfg.get("flag", ""),
                "platform": platform,
                "url": url,
            })

    links["gulf"] = []
    for country_key, country_cfg in GULF_COUNTRIES.items():
        for platform, url_template in country_cfg["platforms"].items():
            url = url_template.replace("{q}", q_en)
            links["gulf"].append({
                "region": country_cfg["name"],
                "flag": country_cfg.get("flag", ""),
                "platform": platform,
                "url": url,
            })

    links["iran_divar"] = []
    for city_code, city_name in IRAN_CITIES.items():
        links["iran_divar"].append({
            "city": city_name,
            "url": f"https://divar.ir/s/{city_code}/?q={q_fa_buyer}",
        })

    links["international"] = [
        {"platform": "OLX Pakistan", "url": f"https://www.olx.com.pk/items/q-{q_en}"},
        {"platform": "OLX India", "url": f"https://www.olx.in/items/q-{q_en}"},
        {"platform": "Alibaba B2B", "url": f"https://www.alibaba.com/trade/search?SearchText={q_en}"},
        {"platform": "Amazon US", "url": f"https://www.amazon.com/s?k={q_en}"},
        {"platform": "eBay", "url": f"https://www.ebay.com/sch/i.html?_nkw={q_en}"},
        {"platform": "AliExpress", "url": f"https://www.aliexpress.com/wholesale?SearchText={q_en}"},
        {"platform": "Etsy", "url": f"https://www.etsy.com/search?q={q_en}"},
    ]

    return links

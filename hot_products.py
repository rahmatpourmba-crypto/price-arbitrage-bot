import asyncio
import urllib.parse
from telegram_bot import TelegramBot
from config import TELEGRAM_USER_IDS
from scrapers.buyers import search_divar_products
from scrapers.regional import get_all_regional_links


DEMAND_CATEGORIES = {
    "elektronik": {
        "name": "لوازم الکترونیکی",
        "items": ["موبایل", "لپتاپ", "تبلت", "لوازم جانبی موبایل", "هدفون", "اسپیکر"],
    },
    "khanegi": {
        "name": "لوازم خانگی",
        "items": ["یخچال", "ماشین لباسشویی", "اجاق گاز", "مایکروفر", "جاروبرقی", "پنکه"],
    },
    "lebas": {
        "name": "پوشاک و کفش",
        "items": ["کفش مردانه", "کفش زنانه", "پیراهن مردانه", "شلوار مردانه", "مانتو"],
    },
    "khodro": {
        "name": "لوازم خودرو",
        "items": ["لاستیک خودرو", "روغن موتور", "لنت ترمز", "فیلتر", "باطری خودرو"],
    },
    "sakhteman": {
        "name": "مصالح ساختمانی",
        "items": ["سیمان", "کاشی", "سرامیک", "شیرآلات", "لوله"],
    },
    "ghaza": {
        "name": "مواد غذایی",
        "items": ["برنج", "روغن", "شکر", "ادویه", "چای", "قهوه", "خشکبار"],
    },
    "pezeshki": {
        "name": "تجهیزات پزشکی",
        "items": ["فشارسنج", "تب‌سنج", "ماسک", "دستکش"],
    },
    "sanati": {
        "name": "لوازم صنعتی",
        "items": ["پمپ", "موتور", "اینورتر", "کابل برق", "فیوز"],
    },
    "bazi": {
        "name": "لوازم بازی و سرگرمی",
        "items": ["پلی‌استیشن", "ایکس‌باکس", "عروسک", "بازی فکری"],
    },
    "zibaii": {
        "name": "لوازم آرایشی و بهداشتی",
        "items": ["شامپو", "کرم", "عطر", "لاک", "لوازم آرایشی"],
    },
}


def find_hot_products(category: str | None = None, max_items: int = 5) -> list[dict]:
    results = []

    if category and category in DEMAND_CATEGORIES:
        items = DEMAND_CATEGORIES[category]["items"]
    else:
        items = []
        for cat_cfg in DEMAND_CATEGORIES.values():
            items.extend(cat_cfg["items"][:2])

    for item in items[:max_items]:
        search_results = search_divar_products(item, "tehran", limit=5)
        if not search_results:
            continue

        with_price = [p for p in search_results if p.get("price")]
        if not with_price:
            continue

        results.append({
            "item": item,
            "count": len(with_price),
            "posts": with_price[:3],
        })

    return results


async def handle_hot_products(bot: TelegramBot, chat_id: int, category: str | None = None):
    await bot.send_typing(chat_id)

    if not category:
        msg = "🔍 در حال بررسی پرتقاضاترین کالاها..."
    else:
        msg = f"🔍 در حال بررسی «{category}»..."

    await bot.send_message(chat_id, msg)

    results = await asyncio.to_thread(find_hot_products, category, 6)

    if not results:
        await bot.send_message(chat_id, "⚠️ نتیجه‌ای یافت نشد")
        return

    resp = "🔥 پرتقاضاترین کالاها (بازار ایران)\n"
    resp += "=" * 35 + "\n\n"

    for i, r in enumerate(results, 1):
        resp += f"{i}. 📦 {r['item']}\n"
        resp += f"   تعداد آگهی: {r['count']}\n"
        for p in r["posts"][:2]:
            resp += f"   • {p['title'][:45]} | {p['price']}\n"
        resp += "\n"

    links = get_all_regional_links(results[0]["item"] if results else "laptop")
    kurd = links.get("kurdistan_iraq", [])
    if kurd:
        resp += "🌍 لینک خریداران کردستان عراق:\n"
        by_city = {}
        for l in kurd:
            c = l["region"]
            if c not in by_city:
                by_city[c] = []
            by_city[c].append(l)
        for city, city_links in by_city.items():
            resp += f"  🇮🇶 {city}:\n"
            for l in city_links[:2]:
                resp += f"    • {l['platform']}: {l['url'][:60]}\n"

    gulf = links.get("gulf", [])
    if gulf:
        resp += "\n🏜️ لینک خریداران خلیج:\n"
        by_country = {}
        for l in gulf:
            c = l["region"]
            if c not in by_country:
                by_country[c] = []
            by_country[c].append(l)
        for country, country_links in by_country.items():
            flag = country_links[0]["flag"]
            resp += f"  {flag} {country}:\n"
            for l in country_links[:2]:
                resp += f"    • {l['platform']}: {l['url'][:60]}\n"

    await bot.send_message(chat_id, resp)

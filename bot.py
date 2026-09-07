import asyncio
import urllib.parse
from telegram_bot import TelegramBot
from config import TELEGRAM_USER_IDS
from scrapers.buyers import search_divar_buyers, search_divar_products, search_sheypoor_buyers, search_google_buyers
from scrapers.regional import search_divar_multi_city, get_all_regional_links, IRAN_CITIES
from scrapers.http import make_search_links
from hot_products import handle_hot_products, DEMAND_CATEGORIES


def _auth(user_id: int) -> bool:
    if not TELEGRAM_USER_IDS:
        return True
    return user_id in TELEGRAM_USER_IDS


def _extract_query(text: str) -> str:
    parts = text.strip().split(None, 1)
    return parts[1] if len(parts) > 1 else ""


def _format_sellers(products: list[dict], max_products: int = 5, max_sellers: int = 5) -> str:
    if not products:
        return "نتیجه‌ای یافت نشد"
    lines = []
    for i, p in enumerate(products[:max_products], 1):
        badge = " 🏪" if p.get("is_store") else ""
        cond = f" | {p['condition']}" if p.get("condition") else ""
        price = f" | {p['price']}" if p.get("price") else ""
        lines.append(f"{i}. {p['title'][:60]}{badge}{cond}{price}")
        lines.append(f"   🔗 {p['url']}")
    return "\n".join(lines)


def _format_regional_buyers(posts: list, query: str) -> str:
    lines = [f"\n{'='*30}", f"🔍 خریداران «{query}» از شهرهای ایران:"]

    if not posts:
        lines.append("  آگهی خریدار یافت نشد")
        return "\n".join(lines)

    by_city = {}
    for p in posts:
        city = p.get("city", "نامشخص")
        if city not in by_city:
            by_city[city] = []
        by_city[city].append(p)

    idx = 0
    for city, city_posts in by_city.items():
        lines.append(f"\n📍 {city} ({len(city_posts)} آگهی):")
        for p in city_posts[:3]:
            idx += 1
            badge = " 🏪" if p.get("is_store") else ""
            cond = f" | {p['condition']}" if p.get("condition") else ""
            lines.append(f"  {idx}. {p['title'][:50]}{badge}{cond}")
            lines.append(f"     🔗 {p['url']}")

    return "\n".join(lines)


def _format_regional_links(links: dict, query: str) -> str:
    lines = [f"\n{'='*30}", f"🌍 لینک خریداران منطقه‌ای برای «{query}»:"]

    kurd = links.get("kurdistan_iraq", [])
    if kurd:
        lines.append(f"\n🏔️ اقلیم کوردستان عراق:")
        by_city = {}
        for l in kurd:
            c = l["region"]
            if c not in by_city:
                by_city[c] = []
            by_city[c].append(l)
        for city, city_links in by_city.items():
            flag = city_links[0]["flag"]
            lines.append(f"  {flag} {city}:")
            for l in city_links:
                lines.append(f"    • {l['platform']}: {l['url'][:65]}")

    gulf = links.get("gulf", [])
    if gulf:
        lines.append(f"\n🏜️ کشورهای حوزه خلیج:")
        by_region = {}
        for l in gulf:
            r = l["region"]
            if r not in by_region:
                by_region[r] = []
            by_region[r].append(l)
        for region, region_links in by_region.items():
            flag = region_links[0]["flag"]
            lines.append(f"  {flag} {region}:")
            for l in region_links:
                lines.append(f"    • {l['platform']}: {l['url'][:65]}")

    iran = links.get("iran_divar", [])
    if iran:
        lines.append(f"\n🇮🇷 شهرهای ایران (دیوار):")
        for l in iran[:10]:
            lines.append(f"  • {l['city']}: {l['url'][:65]}")

    intl = links.get("international", [])
    if intl:
        lines.append(f"\n🌐 بین‌المللی (B2B):")
        for l in intl:
            lines.append(f"  • {l['platform']}: {l['url'][:65]}")

    return "\n".join(lines)


def _format_links_text(query: str) -> str:
    encoded = urllib.parse.quote(query)
    buyer_encoded = urllib.parse.quote(f"خریدار {query}")
    lines = [
        "",
        "🔗 لینک‌های مستقیم:",
        f"📱 دیوار (خریداران): https://divar.ir/s/tehran/?q={buyer_encoded}",
        f"📱 دیوار (فروشندگان): https://divar.ir/s/tehran/?q={encoded}",
        f"🔍 شیپور: https://www.sheypoor.com/search?q={encoded}",
        f"🌐 Alibaba: https://www.alibaba.com/trade/search?SearchText={encoded}",
        f"🛒 Amazon: https://www.amazon.com/s?k={encoded}",
    ]
    return "\n".join(lines)


async def handle_message(bot: TelegramBot, msg: dict):
    chat_id = msg["chat"]["id"]
    user_id = msg.get("from", {}).get("id", 0)
    text = msg.get("text", "")

    if not _auth(user_id):
        return

    if text.startswith("/start"):
        await bot.send_message(chat_id,
            "🤖 ربات آربیتراژ ایران ↔ عراق/خلیج\n\n"
            "📋 دستورات:\n\n"
            "🔥 /hot - پرتقاضاترین کالاها (فروشندگان ایران + لینک خریداران خارج)\n"
            "🔥 /hot الکترونیک - کالاهای یک دسته خاص\n\n"
            "💰 /cheap لپتاپ - فروشندگان ارزان دیوار\n"
            "💰 /cheap آیفون - فروشندگان یک محصول خاص\n\n"
            "🛒 /buyers لپتاپ - خریداران تهران + لینک خارج\n"
            "🌍 /regions لپتاپ - خریداران کردستان + خلیج + بین‌الملل\n\n"
            "📊 /arb لپتاپ - تحلیل آربیتراژ (اختلاف قیمت)\n"
            "🔗 /links لپتاپ - همه لینک‌ها\n\n"
            "💡 نمونه:\n"
            "/hot\n"
            "/cheap لپتاپ\n"
            "/buyers آیفون\n"
            "/regions تبلت"
        )
        return

    elif text.startswith("/hot"):
        query = _extract_query(text)
        cat_key = None
        if query:
            query_lower = query.lower()
            for k, v in DEMAND_CATEGORIES.items():
                if query_lower in v["name"].lower() or query_lower == k:
                    cat_key = k
                    break
            if not cat_key:
                cat_key = query
        await handle_hot_products(bot, chat_id, cat_key)
        return

    elif text.startswith("/regions"):
        query = _extract_query(text)
        if not query:
            await bot.send_message(chat_id, "نام کالا را بنویسید\nمثال: /regions لپتاپ")
            return
        await bot.send_typing(chat_id)
        await bot.send_message(chat_id, f"🌍 در حال جستجوی خریداران «{query}» در کردستان، خلیج و بین‌الملل...")

        posts = await asyncio.to_thread(
            search_divar_multi_city, query,
            ["sanandaj", "kermanshah", "tabriz", "ahvaz", "tehran", "mashhad", "urumia"],
            5,
        )
        links = get_all_regional_links(query)

        resp = _format_regional_buyers(posts, query)
        resp += _format_regional_links(links, query)

        if not posts:
            resp += "\n\n💡 روی لینک‌های بالا کلیک کنید تا مستقیماً خریداران را ببینید"

        await bot.send_message(chat_id, resp)

    elif text.startswith("/buyers"):
        query = _extract_query(text)
        if not query:
            await bot.send_message(chat_id, "نام کالا را بنویسید\nمثال: /buyers لپتاپ")
            return
        await bot.send_typing(chat_id)
        await bot.send_message(chat_id, f"🔍 در حال جستجوی خریداران «{query}»...")

        divar, sheypoor, google = await asyncio.gather(
            asyncio.to_thread(search_divar_buyers, query, "tehran", 10),
            asyncio.to_thread(search_sheypoor_buyers, query, 5),
            asyncio.to_thread(search_google_buyers, query, 5),
        )

        resp = f"📱 خریداران «{query}» از تهران:\n"
        if divar:
            for i, p in enumerate(divar[:8], 1):
                badge = " 🏪" if p.get("is_store") else ""
                cond = f" | {p['condition']}" if p.get("condition") else ""
                resp += f"  {i}. {p['title'][:50]}{badge}{cond}\n     🔗 {p['url']}\n"
        else:
            resp += "  آگهی‌ای یافت نشد\n"

        if sheypoor:
            resp += "\n📱 شیپور:\n"
            for p in sheypoor[:5]:
                if p.get("platform") == "sheypoor_contacts":
                    for ph in p.get("phones", []):
                        resp += f"  📞 {ph}\n"
                else:
                    resp += f"  • {p['title'][:50]}\n     🔗 {p['url']}\n"

        links = get_all_regional_links(query)
        resp += _format_regional_links(links, query)

        await bot.send_message(chat_id, resp)

    elif text.startswith("/cheap"):
        query = _extract_query(text)
        if not query:
            await bot.send_message(chat_id, "نام کالا را بنویسید\nمثال: /cheap لپتاپ")
            return
        await bot.send_typing(chat_id)
        await bot.send_message(chat_id, f"🔍 در حال جستجوی «{query}» در دیوار...")

        products = await asyncio.to_thread(search_divar_products, query, "tehran", 10)

        resp = f"📦 فروشندگان «{query}» از دیوار:\n"
        resp += _format_sellers(products, max_products=8)
        resp += "\n"
        resp += _format_links_text(query)

        await bot.send_message(chat_id, resp)

    elif text.startswith("/links"):
        query = _extract_query(text)
        if not query:
            await bot.send_message(chat_id, "نام کالا را بنویسید\nمثال: /links آیفون")
            return
        await bot.send_typing(chat_id)
        links = get_all_regional_links(query)
        resp = f"🔗 همه لینک‌ها برای «{query}»:"
        resp += _format_regional_links(links, query)
        await bot.send_message(chat_id, resp)

    elif text.startswith("/arb"):
        query = _extract_query(text)
        if not query:
            await bot.send_message(chat_id, "نام کالا را بنویسید\nمثال: /arb لپتاپ")
            return
        await bot.send_typing(chat_id)
        await bot.send_message(chat_id, f"💰 تحلیل آربیتراژ «{query}»...")

        products = await asyncio.to_thread(search_divar_products, query, "tehran", 10)

        if products:
            with_price = [p for p in products if p.get("price") and "تومان" in str(p["price"])]
            if with_price:
                resp = f"💰 تحلیل آربیتراژ «{query}»:\n\n"
                resp += f"📊 تعداد آگهی فروش: {len(with_price)}\n\n"

                resp += "📊 فروشندگان:\n"
                for i, p in enumerate(with_price[:8], 1):
                    badge = " 🏪" if p.get("is_store") else ""
                    resp += f"  {i}. {p['price']} | {p['title'][:40]}{badge}\n"
                    resp += f"     🔗 {p['url']}\n"
            else:
                resp = "⚠️ قیمتی در آگهی‌ها یافت نشد"
        else:
            resp = "⚠️ محصولی یافت نشد"

        resp += "\n"
        links = get_all_regional_links(query)
        resp += _format_regional_links(links, query)

        await bot.send_message(chat_id, resp)

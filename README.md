# ربات آربیتراژ ایران ↔ عراق/خلیج

## نحوه روشن کردن ربات

### روش آسان (پیشنهادی):
فایل `start_bot.bat` رو پیدا کن و **دوبار کلیک** کن.

مسیر فایل:
```
C:\Users\Admin\Documents\Default Project\price_arbitrage_bot\start_bot.bat
```

### روش دستی:
```bash
cd "C:\Users\Admin\Documents\Default Project\price_arbitrage_bot"
set PYTHONPATH=C:\Users\Admin\Documents\Default Project\price_arbitrage_bot
python main.py
```

### نحوه خاموش کردن:
پنجره cmd رو ببند یا `Ctrl+C` بزن.

---

## دستورات ربات

| دستور | توضیح |
|-------|--------|
| `/start` | راهنما |
| `/hot` | پرتقاضاترین کالاها (فروشندگان ایران + لینک خریداران خارج) |
| `/cheap لپتاپ` | فروشندگان ارزان دیوار |
| `/buyers لپتاپ` | خریداران تهران |
| `/regions لپتاپ` | خریداران کردستان + خلیج + بین‌الملل |
| `/arb لپتاپ` | تحلیل آربیتراژ (اختلاف قیمت) |
| `/links لپتاپ` | همه لینک‌ها |

---

## منابع اطلاعاتی

### اسکرپ مستقیم (داده واقعی)
- **دیوار** - فروشندگان و خریداران ایران

### لینک‌های مستقیم
- **کردستان عراق**: Haraj, Bazar1, Facebook Marketplace (اربیل، سلیمانیه، دهوک)
- **خلیج**: Dubizzle, Amazon AE, Haraj, OpenSooq (امارات، عربستان، کویت، قطر، بحرین، عمان)
- **بین‌المللی**: OLX Pakistan, OLX India, Alibaba, Amazon, eBay, AliExpress, Etsy
- **ایران**: دیوار (15 شهر)

---

## نصب و راه‌اندازی

```bash
# نیازمندی‌ها
pip install httpx aiohttp beautifulsoup4

# اجرا
python main.py
```

## ساختار پروژه

```
price_arbitrage_bot/
├── main.py              # نقطه شروع
├── bot.py               # هندلرهای دستورات تلگرام
├── hot_products.py      # دستور /hot
├── config.py            # تنظیمات (توکن تلگرام)
├── telegram_bot.py      # کلاینت تلگرام
├── core.py              # داده‌ساختارها
├── start_bot.bat        # فایل اجرای سریع
└── scrapers/
    ├── __init__.py
    ├── http.py          # لایه HTTP (httpx + curl)
    ├── torob.py         # ترب (غیرفعال - بلاک شده)
    ├── buyers.py        # جستجوی خریداران دیوار
    └── regional.py      # لینک‌های منطقه‌ای
```

---

## لایسنس

MIT

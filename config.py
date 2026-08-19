import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_USER_IDS = [
    int(x.strip())
    for x in os.getenv("TELEGRAM_USER_IDS", "").split(",")
    if x.strip()
]

TOROB_BASE = "https://api.torob.com/v4/base-product"
DIVAR_BASE = "https://api.divar.ir/v8"
BUSKOOL_BASE = "https://www.buskool.com"
OPENSOOQ_BASE = "https://jo.opensooq.com"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

DIVAR_CITIES = {
    "tehran": "1",
    "mashhad": "2",
    "karaj": "11",
    "shiraz": "4",
    "isfahan": "14",
    "ahvaz": "13",
    "tabriz": "3",
    "tabriz2": "2",
    "kerman": "7",
}

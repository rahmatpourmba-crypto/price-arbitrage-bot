import sys
import asyncio
import logging

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from config import TELEGRAM_BOT_TOKEN
from telegram_bot import TelegramBot
from bot import handle_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error(
            "TELEGRAM_BOT_TOKEN set nashode! "
            ".env.example ra be .env copy konid va token ra por konid."
        )
        return

    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    await bot.drop_pending()
    logger.info("Bot shoru shod... polling!")

    try:
        while True:
            updates = await bot.get_updates(timeout=30)
            for update in updates:
                msg = update.get("message")
                if msg:
                    try:
                        await handle_message(bot, msg)
                    except Exception as e:
                        logger.error("handle error: %s", e, exc_info=True)
    except KeyboardInterrupt:
        logger.info("Bot carpet shod.")
    finally:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())

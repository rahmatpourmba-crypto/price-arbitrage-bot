import httpx
import logging
import asyncio

logger = logging.getLogger(__name__)

BASE = "https://api.telegram.org/bot"


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.url = f"{BASE}{token}"
        self.offset = 0
        self.client = httpx.AsyncClient(timeout=60.0)

    async def drop_pending(self):
        try:
            all_ids = []
            while True:
                resp = await self.client.get(
                    f"{self.url}/getUpdates",
                    params={"offset": self.offset, "timeout": 0, "limit": 100},
                )
                data = resp.json()
                if not data.get("ok"):
                    break
                results = data.get("result", [])
                if not results:
                    break
                for u in results:
                    all_ids.append(u["update_id"])
                self.offset = results[-1]["update_id"] + 1
            if all_ids:
                logger.info("Dropped %d pending updates (last_id=%d)", len(all_ids), all_ids[-1])
            else:
                logger.info("No pending updates")
        except Exception as e:
            logger.error("drop_pending error: %s", e)

    async def get_updates(self, timeout: int = 30):
        try:
            resp = await self.client.get(
                f"{self.url}/getUpdates",
                params={
                    "offset": self.offset,
                    "timeout": timeout,
                    "allowed_updates": '["message"]',
                },
            )
            data = resp.json()
            if resp.status_code == 409:
                logger.warning("409 Conflict - another instance polling, waiting 10s")
                await asyncio.sleep(10)
                return []
            if not data.get("ok"):
                logger.warning("getUpdates not ok: %s", data.get("description", ""))
                return []
            results = data.get("result", [])
            if results:
                logger.info("Got %d updates", len(results))
            for u in results:
                self.offset = u["update_id"] + 1
            return results
        except Exception as e:
            logger.error("get_updates error: %s", e)
            return []

    async def send_message(self, chat_id: int, text: str, disable_preview: bool = True):
        try:
            chunks = self._split(text, 4000)
            for chunk in chunks:
                resp = await self.client.post(
                    f"{self.url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": chunk,
                        "disable_web_page_preview": disable_preview,
                    },
                )
                if resp.status_code != 200:
                    logger.error("sendMessage failed: %s", resp.text[:200])
        except Exception as e:
            logger.error("send_message error: %s", e)

    async def send_typing(self, chat_id: int):
        try:
            await self.client.post(
                f"{self.url}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"},
            )
        except Exception:
            pass

    async def close(self):
        await self.client.aclose()

    @staticmethod
    def _split(text: str, max_len: int = 4000) -> list[str]:
        if len(text) <= max_len:
            return [text]
        parts = []
        while text:
            if len(text) <= max_len:
                parts.append(text)
                break
            idx = text.rfind("\n", 0, max_len)
            if idx == -1:
                idx = max_len
            parts.append(text[:idx])
            text = text[idx:].lstrip("\n")
        return parts

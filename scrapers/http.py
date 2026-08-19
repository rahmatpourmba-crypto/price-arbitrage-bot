import httpx
import json
import subprocess
import urllib.parse

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

_client: httpx.Client | None = None

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.5",
}


def _get_client() -> httpx.Client:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.Client(
            timeout=15,
            headers=_HEADERS,
            follow_redirects=True,
            http2=False,
        )
    return _client


def http_get(url: str, headers: dict | None = None) -> httpx.Response | None:
    try:
        c = _get_client()
        r = c.get(url, headers=headers or {})
        return r
    except Exception:
        return None


def http_get_json(url: str, headers: dict | None = None) -> dict | None:
    r = http_get(url, headers)
    if r and r.status_code == 200:
        try:
            return r.json()
        except Exception:
            pass
    return None


def http_post_json(url: str, payload: dict, headers: dict | None = None) -> dict | None:
    try:
        c = _get_client()
        h = {"Content-Type": "application/json"}
        if headers:
            h.update(headers)
        r = c.post(url, json=payload, headers=h)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def http_get_html(url: str, headers: dict | None = None) -> str | None:
    r = http_get(url, headers)
    if r and r.status_code == 200:
        return r.text
    return None


def make_search_links(query: str) -> dict[str, str]:
    encoded = urllib.parse.quote(query)
    return {
        "divar_buyers": f"https://divar.ir/s/tehran/?q={urllib.parse.quote('خریدار ' + query)}",
        "divar_sellers": f"https://divar.ir/s/tehran/?q={encoded}",
        "sheypoor": f"https://www.sheypoor.com/search?q={encoded}",
        "torob": f"https://torob.com/search?q={encoded}",
        "instagram": f"https://www.instagram.com/explore/tags/{encoded.replace('%20', '').replace('+', '')}/",
        "alibaba": f"https://www.alibaba.com/trade/search?SearchText={encoded}",
        "amazon": f"https://www.amazon.com/s?k={encoded}",
    }


def curl_get_json(url: str, extra_headers: list[str] | None = None, timeout: int = 20) -> dict | None:
    cmd = ["curl.exe", "-s", "--max-time", str(timeout), url, "-H", f"User-Agent: {_UA}"]
    for h in (extra_headers or []):
        cmd.extend(["-H", h])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5, encoding="utf-8", errors="replace")
        if r.returncode != 0 or not r.stdout.strip():
            return None
        return json.loads(r.stdout)
    except Exception:
        return None

import time
import subprocess
import os
import sys

BOT_DIR = r"C:\Users\Admin\Documents\Default Project\price_arbitrage_bot"
LOG_FILE = os.path.join(BOT_DIR, "watchdog.log")
INTERVAL = 15


def is_bot_running():
    try:
        check = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe"],
            capture_output=True, text=True, timeout=10,
        )
        if "python.exe" not in check.stdout.lower():
            return False
        result = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'", "get", "CommandLine"],
            capture_output=True, text=True, timeout=10,
        )
        return "main.py" in result.stdout
    except Exception:
        return True


def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")


if __name__ == "__main__":
    log("Watchdog started")
    while True:
        try:
            if not is_bot_running():
                log("Bot is DOWN - restarting...")
                subprocess.Popen(
                    [sys.executable, "main.py"],
                    cwd=BOT_DIR,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=open(os.path.join(BOT_DIR, "bot_stdout.log"), "a"),
                    stderr=open(os.path.join(BOT_DIR, "bot_stderr.log"), "a"),
                )
                log("Bot restarted")
        except Exception as e:
            log(f"Watchdog error: {e}")
        time.sleep(INTERVAL)
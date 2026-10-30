"""Post to @FComo1907 from the owner's own Telegram account (Telethon).

Usage (run with .venv\\Scripts\\python.exe):
  tg.py [--channel NAME] <command>              commands work on @FComo1907 unless --channel (or TG_CHANNEL) is set
  tg.py login                                  one-time sign-in (asks phone + code)
  tg.py export-session                          sign in as a NEW device and copy its session string to the
                                                clipboard (for cloud secrets; run once per cloud service)
  tg.py recent [N]                              print the last N channel posts (default 20)
  tg.py post --caption-file F --photo URL|PATH  post a photo with an HTML caption
  tg.py post --caption-file F                   post text only

Captions are HTML; premium emoji are written as
  <tg-emoji emoji-id="5229073990835804268">🇮🇹</tg-emoji>
"""
import argparse
import asyncio
import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

from telethon import TelegramClient, types
from telethon.sessions import StringSession

HERE = Path(__file__).resolve().parent
CHANNEL = os.environ.get("TG_CHANNEL", "FComo1907")
CONFIG = HERE / "config.json"
SESSION = str(HERE / "fcomo")


def load_config():
    # In the cloud the credentials come from secrets (env vars); locally from config.json.
    if os.environ.get("TG_API_ID") and os.environ.get("TG_API_HASH"):
        return int(os.environ["TG_API_ID"]), os.environ["TG_API_HASH"]
    if not CONFIG.exists():
        sys.exit(f"config.json not found in {HERE}. Copy config.example.json to config.json and fill api_id/api_hash.")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    return int(cfg["api_id"]), cfg["api_hash"]


def client():
    api_id, api_hash = load_config()
    session = StringSession(os.environ["TG_SESSION"]) if os.environ.get("TG_SESSION") else SESSION
    return TelegramClient(session, api_id, api_hash)


async def cmd_export_session(gh_secret):
    import subprocess

    api_id, api_hash = load_config()
    c = TelegramClient(StringSession(), api_id, api_hash)
    await c.start()  # a separate device login, so each cloud service has its own session
    s = c.session.save()
    await c.disconnect()
    if gh_secret:
        subprocess.run(["gh", "secret", "set", "TG_SESSION"], input=s.encode(), check=True)
        print("Saved as GitHub secret TG_SESSION.")
        return
    subprocess.run("clip", input=s.encode("utf-16-le"), check=True, shell=True)
    print("Session string copied to the clipboard. Paste it into the secret field (Ctrl+V). Do not share it.")


async def cmd_login():
    async with client() as c:
        await c.start()  # prompts for phone, code and 2FA password in the terminal
        me = await c.get_me()
        print(f"Signed in as {me.first_name} (@{me.username}). Session saved.")


async def cmd_recent(n, channel=None):
    async with client() as c:
        if not await c.is_user_authorized():
            sys.exit("Not signed in. Run: tg.py login")
        async for m in c.iter_messages(channel or CHANNEL, limit=n):
            text = (m.message or "").replace("\n", " ")
            print(f"[{m.id}] {m.date:%Y-%m-%d %H:%M} {'(photo) ' if m.photo else ''}{text[:300]}")


def fetch_photo(src):
    if not src.lower().startswith(("http://", "https://")):
        return src
    req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=30).read()
    ext = os.path.splitext(src.split("?")[0])[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg"
    fd, path = tempfile.mkstemp(suffix=ext)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return path


async def send(caption, photo=None, channel=None):
    """Post an HTML caption (optionally with a photo URL/path) to the channel; returns a result dict."""
    channel = channel or CHANNEL
    async with client() as c:
        if not await c.is_user_authorized():
            sys.exit("Not signed in. Run: tg.py login")
        c.parse_mode = "html"  # Telethon's HTML parser understands <tg-emoji emoji-id>.
        if photo:
            msg = await c.send_file(channel, fetch_photo(str(photo)), caption=caption)
        else:
            msg = await c.send_message(channel, caption, link_preview=False)
        custom = sum(isinstance(e, types.MessageEntityCustomEmoji) for e in (msg.entities or []))
        result = {"ok": True, "message_id": msg.id, "url": f"https://t.me/{channel}/{msg.id}",
                  "photo": bool(msg.photo), "custom_emoji": custom}
        print(json.dumps(result, ensure_ascii=False), flush=True)
        return result


async def cmd_post(caption_file, photo, channel=None):
    await send(Path(caption_file).read_text(encoding="utf-8").strip(), photo, channel)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--channel", help="channel username (default: FComo1907 or TG_CHANNEL)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login")
    ex = sub.add_parser("export-session")
    ex.add_argument("--gh-secret", action="store_true", help="store it as the repo's TG_SESSION secret via gh")
    r = sub.add_parser("recent")
    r.add_argument("n", nargs="?", type=int, default=20)
    po = sub.add_parser("post")
    po.add_argument("--caption-file", required=True)
    po.add_argument("--photo")
    a = p.parse_args()
    if a.cmd == "login":
        asyncio.run(cmd_login())
    elif a.cmd == "export-session":
        asyncio.run(cmd_export_session(a.gh_secret))
    elif a.cmd == "recent":
        asyncio.run(cmd_recent(a.n, a.channel))
    else:
        asyncio.run(cmd_post(a.caption_file, a.photo, a.channel))


if __name__ == "__main__":
    main()

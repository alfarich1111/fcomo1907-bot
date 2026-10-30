"""Publish queued posts from outbox/ (used by the GitHub Actions "Outbox" workflow).

The Claude cloud routines can't reach Telegram directly, so they commit a post to branch
claude/outbox as outbox/<name>.json:
  {"caption": "<HTML caption with <tg-emoji ...>>", "photo": "outbox/<name>.png" | "https://..." | "",
   "channel": "CHELSI_CHELSEAUZ_CFCUZ"}   (channel is optional; default @FComo1907)
This script posts every given JSON file in order, via tg.py (the owner's account).

Usage: outbox.py outbox/a.json [outbox/b.json ...]
"""
import asyncio
import json
import sys
from pathlib import Path

import tg


async def main(paths):
    for p in sorted(paths):
        post = json.loads(Path(p).read_text(encoding="utf-8-sig"))
        caption = (post.get("caption") or "").strip()
        if not caption:
            print(f"{p}: empty caption, skipped")
            continue
        await tg.send(caption, post.get("photo") or None, post.get("channel") or None)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main([a for a in sys.argv[1:] if a.endswith(".json")]))

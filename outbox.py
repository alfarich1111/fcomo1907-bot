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

CHELSEA = "CHELSI_CHELSEAUZ_CFCUZ"


def stamped(post):
    """CHELSEA UZ photos carry the channel name; its own posters already have it, so they are left alone."""
    photo, channel = post.get("photo") or None, post.get("channel") or ""
    caption = post.get("caption") or ""
    if not photo or channel not in (CHELSEA, "me") or "#MatchDay" in caption or "Keyingi o'yin" in caption:
        return photo
    try:
        from stamp import stamp

        return stamp(tg.fetch_photo(str(photo)))
    except Exception as e:
        print(f"stamp failed, posting the photo as it is: {e}", flush=True)
        return photo


async def main(paths):
    for p in sorted(paths):
        post = json.loads(Path(p).read_text(encoding="utf-8-sig"))
        caption = (post.get("caption") or "").strip()
        if not caption:
            print(f"{p}: empty caption, skipped")
            continue
        await tg.send(caption, stamped(post), post.get("channel") or None)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    asyncio.run(main([a for a in sys.argv[1:] if a.endswith(".json")]))

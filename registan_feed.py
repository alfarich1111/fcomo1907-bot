"""Recent public posts of the other Registan branches, grouped so posts shared by several branches come first.

Usage: registan_feed.py [days] [max_posts]   (default 3 days, 40 posts; no Telegram login needed)
Prints: how many branches posted it, branch/post id, date, views, photo URL, text.
"""
import concurrent.futures as cf
import datetime as dt
import html
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

BRANCHES = (Path(__file__).resolve().parent / "data" / "registan" / "branches.txt").read_text(encoding="utf-8").split()


def fetch(name):
    req = urllib.request.Request(f"https://t.me/s/{name}", headers={"User-Agent": "Mozilla/5.0"})
    try:
        page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception:
        return []
    out = []
    for block in re.split(r'(?=<div class="tgme_widget_message_wrap)', page)[1:]:
        pid = re.search(r'data-post="[^/"]+/(\d+)"', block)
        when = re.search(r'<time datetime="([^"]+)"', block)
        text = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', block, re.S)
        photo = re.search(r"tgme_widget_message_photo_wrap[^>]*background-image:url\('([^']+)'", block)
        views = re.search(r'tgme_widget_message_views">([^<]+)', block)
        body = re.sub(r"<br\s*/?>", "\n", text.group(1)) if text else ""
        body = html.unescape(re.sub(r"<[^>]+>", "", body)).strip()
        if pid and when:
            out.append({"branch": name, "id": pid.group(1), "when": when.group(1), "text": body,
                         "photo": photo.group(1) if photo else "", "views": views.group(1) if views else "",
                         "video": "video_player" in block})
    return out


def key(text):
    return re.sub(r"\W+", "", text.lower())[:80]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)
    with cf.ThreadPoolExecutor(8) as ex:
        posts = [p for batch in ex.map(fetch, BRANCHES) for p in batch]
    groups = defaultdict(list)
    for p in posts:
        if dt.datetime.fromisoformat(p["when"]) >= since and len(p["text"]) > 40:
            groups[key(p["text"])].append(p)
    ranked = sorted(groups.values(), key=lambda g: (-len({p["branch"] for p in g}), g[0]["when"]), reverse=False)
    print(f"{len(posts)} posts read, {len(groups)} different texts in the last {days} days")
    for g in ranked[:limit]:
        p = max(g, key=lambda x: bool(x["photo"]))
        print(f"\n=== {len({x['branch'] for x in g})} branches | t.me/{p['branch']}/{p['id']} | {p['when'][:16]} | views {p['views']}"
              f"{' | video' if p['video'] else ''}{' | photo ' + p['photo'] if p['photo'] else ''}\n{p['text']}")


if __name__ == "__main__":
    main()

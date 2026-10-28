"""Print the channel's latest public posts from https://t.me/s/FComo1907 (no Telegram login needed).

Used by the Claude cloud routines, which can't connect to Telegram itself, to avoid duplicates.
Usage: recent_web.py [N]   (default 30; each page holds ~20 posts, older pages are fetched as needed)
"""
import html
import re
import sys
import urllib.request

URL = "https://t.me/s/FComo1907"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def posts(page):
    for block in re.split(r'(?=<div class="tgme_widget_message_wrap)', page)[1:]:
        pid = re.search(r'data-post="FComo1907/(\d+)"', block)
        when = re.search(r'<time datetime="([^"]+)"', block)
        text = re.search(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', block, re.S)
        body = re.sub(r"<br\s*/?>", " ", text.group(1)) if text else ""
        body = html.unescape(re.sub(r"<[^>]+>", "", body)).strip()
        photo = "photo_wrap" in block
        if pid:
            yield int(pid.group(1)), when.group(1)[:16] if when else "", photo, body


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    seen, url = {}, URL
    while len(seen) < n:
        batch = list(posts(fetch(url)))
        if not batch:
            break
        for p in batch:
            seen[p[0]] = p
        url = f"{URL}?before={min(p[0] for p in batch)}"
    for pid in sorted(seen, reverse=True)[:n]:
        _, when, photo, body = seen[pid]
        print(f"[{pid}] {when} {'(photo) ' if photo else ''}{body[:300]}")


if __name__ == "__main__":
    main()

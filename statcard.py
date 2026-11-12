"""Statistics card image for a channel post: a photo on top, a ranked list with bars below.

Usage: statcard.py spec.json out.png

spec.json (UTF-8):
{
  "channel": "chelsea" | "como",           # picks the tag and the highlight colour
  "photo": "<url or path>",                # recent photo of the player/team the stat is about
  "title": "Palmer — 21,6% моментов «Челси»",
  "subtitle": "Доля созданных моментов команды, Премьер-лига 2026/27",
  "rows": [{"name": "Pascal Groß", "logo": "<crest url or path, optional>", "detail": "118 · 881 мин",
            "value": 24.6, "label": "24.6", "highlight": false}, ...],
  "source": "Premier League 2026/27 · Opta"
}
Bars are drawn relative to the largest value. Mark your club's player with "highlight": true.
"""
import html
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from poster import browser, fetch

STYLE = {
    "chelsea": {"tag": "@CFC_UZ", "accent": "#034694"},
    "como": {"tag": "@fcomo1907", "accent": "#1E5BB8"},
}

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#F2EEE7;font-family:Inter,sans-serif;color:#141414;overflow:hidden}
.ph{height:420px;background:url('%(photo)s') center 25%%/cover;position:relative}
.ph:after{content:"";position:absolute;left:0;right:0;bottom:0;height:7px;background:%(accent)s}
.tag{position:absolute;top:30px;right:36px;color:#fff;font:800 30px Inter;text-shadow:0 2px 12px rgba(0,0,0,.6)}
.card{padding:42px 64px 0}
h1{font:800 50px/1.12 Inter;letter-spacing:-.5px}
.sub{font:500 25px Inter;color:#6b6b6b;margin:16px 0 26px}
.row{display:grid;grid-template-columns:44px 64px 1fr 150px;align-items:center;gap:14px;padding:16px 0;border-top:1px solid #dcd6cc}
.rk{font:600 26px Inter;color:#777}
.lg{width:54px;height:54px;border-radius:50%%;background:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(0,0,0,.12)}
.lg img{width:40px;height:40px;object-fit:contain}
.nm{font:700 29px Inter}
.dt{font:500 19px Inter;color:#888;margin-top:3px}
.bar{height:9px;background:#d9d3c8;border-radius:5px;margin-top:10px;overflow:hidden}
.bar i{display:block;height:100%%;background:#9a958c}
.hl .nm{color:%(accent)s}.hl .bar i{background:%(accent)s}
.val{font:800 40px Inter;text-align:right}
.hl .val{color:%(accent)s}
.src{position:absolute;left:64px;bottom:34px;font:500 22px Inter;color:#888}
</style></head><body>
<div class="ph"><div class="tag">%(tag)s</div></div>
<div class="card"><h1>%(title)s</h1><div class="sub">%(subtitle)s</div>%(rows)s</div>
<div class="src">%(source)s</div>
</body></html>"""


def as_uri(src):
    return Path(fetch(src)).resolve().as_uri() if src else ""


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2]).resolve()
    st = STYLE[spec.get("channel", "chelsea")]
    top = max(float(r["value"]) for r in spec["rows"]) or 1
    rows = []
    for i, r in enumerate(spec["rows"][:6], 1):
        logo = f'<img src="{as_uri(r["logo"])}">' if r.get("logo") else ""
        pct = max(4, round(float(r["value"]) / top * 100))
        rows.append(
            f'<div class="row{" hl" if r.get("highlight") else ""}"><div class="rk">{i}</div>'
            f'<div class="lg">{logo}</div><div><div class="nm">{html.escape(r["name"])}</div>'
            f'<div class="dt">{html.escape(r.get("detail", ""))}</div><div class="bar"><i style="width:{pct}%"></i></div></div>'
            f'<div class="val">{html.escape(str(r.get("label", r["value"])))}</div></div>')
    page = PAGE % {"photo": as_uri(spec["photo"]), "accent": st["accent"], "tag": st["tag"],
                   "title": html.escape(spec["title"]), "subtitle": html.escape(spec.get("subtitle", "")),
                   "rows": "".join(rows), "source": html.escape(spec.get("source", ""))}
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "card.html"
        f.write_text(page, encoding="utf-8")
        subprocess.run([browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1080,1350",
                        "--force-device-scale-factor=1", "--virtual-time-budget=8000", f"--screenshot={out}", f.as_uri()],
                       check=True, capture_output=True, timeout=120)
    print(out)


if __name__ == "__main__":
    main()

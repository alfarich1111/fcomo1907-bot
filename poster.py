"""Render match posters (1600x2000 PNG) from a JSON spec, in the @FComo1907 style.

Usage (run with .venv\\Scripts\\python.exe):
  poster.py matchday spec.json out.png
  poster.py result   spec.json out.png
  poster.py cutout   <image url|path> out.png     cut a player out of a photo (transparent PNG)
  poster.py table    "<subtitle>" out.png [profile] league standings from ESPN, e.g. subtitle "после 10 тура";
                                                   profile = data/profiles/<name>.json (default: Como)

Every spec may set "lang" ("ru" default, "uz") for the poster's fixed wording and "tag" for the channel tag.
matchday spec keys: weekday, date, kicker, home, away, home_color, away_color, time, tz,
  left_img, right_img (cutout PNG paths, optional), hl1, hl2, stadium, table, form (e.g. "DLWWW", oldest first)
result spec keys: weekday, date, kicker, home, away, home_logo, away_logo, score, winner ("home"|"away"|""),
  right_img, k2, hl1, hl2, goals [{"min": "81'", "who": "Хакобо Рамон", "como": true}], table, series, form
"""
import html
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent
TPL = HERE / "templates"
BROWSERS = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"]


def browser():
    """Headless browser for rendering: Edge on Windows, Chrome/Chromium on Linux (cloud), else Playwright's."""
    import glob
    import shutil

    for b in BROWSERS + [shutil.which("google-chrome") or "", shutil.which("chromium") or ""]:
        if b and os.path.exists(b):
            return b
    found = sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")))
    if found:
        return found[-1]
    sys.exit("No Chrome/Edge found. Install one (e.g. `pip install playwright && playwright install chromium`).")


# Poster wording per channel language; a spec picks one with "lang" (default "ru").
LABELS = {
    "ru": {"l_home": "хозяева", "l_away": "гости", "l_stadium": "Стадион", "l_table": "В таблице",
           "l_form": "Форма Комо", "l_final": "Финал", "l_goals": "Голы", "l_series": "Серия",
           "l_title": "Таблица", "l_club": "Клуб", "l_p": "И", "l_gd": "РМ", "l_pts": "О",
           "l_cl": "Лига чемпионов", "l_el": "Лига Европы", "l_rel": "Вылет", "tag": "@fcomo1907", "tz": "по мск",
           "form": {"W": "В", "D": "Н", "L": "П"},
           "weekdays": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]},
    "uz": {"l_home": "mezbon", "l_away": "mehmon", "l_stadium": "Stadion", "l_table": "Jadvalda",
           "l_form": "Chelsea formasi", "l_final": "Final", "l_goals": "Gollar", "l_series": "Seriya",
           "l_title": "Jadval", "l_club": "Klub", "l_p": "O", "l_gd": "TF", "l_pts": "Ochko",
           "l_cl": "Chempionlar ligasi", "l_el": "Yevropa ligasi", "l_rel": "Quyi liga", "tag": "@cfc_uz",
           "tz": "Toshkent", "form": {"W": "G", "D": "D", "L": "M"},
           "weekdays": ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]},
}
FORM_RU = LABELS["ru"]["form"]


def profile(name):
    """Channel profile (team, league, language, poster tag) from data/profiles/<name>.json."""
    return json.loads((HERE / "data" / "profiles" / f"{name}.json").read_text(encoding="utf-8"))


def fetch(src):
    """Return a local path for a URL or path (downloads URLs to a temp file)."""
    if not str(src).lower().startswith(("http://", "https://")):
        return str(Path(src).resolve())
    req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=30).read()
    ext = os.path.splitext(src.split("?")[0])[1].lower() or ".png"
    fd, path = tempfile.mkstemp(suffix=ext)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return path


def uri(src):
    return Path(fetch(src)).as_uri() if src else ""


def esc(s):
    return html.escape(str(s or ""))


def form_html(form, letters=FORM_RU):
    return "".join(f'<span class="{c}">{letters[c]}</span>' for c in (form or "").upper() if c in letters)


def headline_size(text, width=1408, base=170, min_size=90):
    """Shrink big headlines so they fit on one line (rough width estimate for Inter Tight Black caps)."""
    est = len(text) * base * 0.66
    return f"{max(min_size, int(base * min(1, width / est)))}px" if est else f"{base}px"


def name_size(name, base=76):
    """Team names on the score board: long ones (LIVERPOOL, MAN UNITED) get a smaller font."""
    n = len(name or "")
    return f"{base if n <= 7 else max(44, int(base * 7.5 / n))}px"


def img_tag(cls, src):
    return f'<img class="cut {cls}" src="{uri(src)}">' if src else ""


def build(kind, spec):
    lab = LABELS.get(spec.get("lang", "ru"), LABELS["ru"])
    s = {k: esc(v) for k, v in lab.items() if isinstance(v, str)}
    s.update({k: esc(v) for k, v in spec.items() if isinstance(v, (str, int, float))})
    s["form"] = form_html(spec.get("form"), lab["form"])
    s["home_fs"], s["away_fs"] = name_size(spec.get("home")), name_size(spec.get("away"))
    if kind == "matchday":
        s.setdefault("home_color", "#d23a3a")
        s.setdefault("away_color", "#6fb3ff")
        s["left_img"] = img_tag("l", spec.get("left_img"))
        s["right_img"] = img_tag("r", spec.get("right_img"))
        s["hl_size"] = headline_size(f"{spec.get('hl1', '')} {spec.get('hl2', '')}")
    else:
        s["home_logo"] = uri(spec.get("home_logo"))
        s["away_logo"] = uri(spec.get("away_logo"))
        w = spec.get("winner", "")
        s["home_dim"] = "dim" if w == "away" else ""
        s["away_dim"] = "dim" if w == "home" else ""
        s["right_img"] = img_tag("r", spec.get("right_img"))
        s["hl_size"] = headline_size(spec.get("hl1", ""), width=860, base=190, min_size=110)
        s["hl2_size"] = headline_size(spec.get("hl2", ""), width=800, base=104, min_size=60)
        longest = max((len(g.get("who", "")) for g in spec.get("goals", [])), default=0)
        s["who_fs"] = "42px" if longest <= 15 else f"{max(28, int(42 * 15 / longest))}px"
        s["goals"] = "".join(
            f'<div class="goal{"" if g.get("como") else " opp"}"><span class="dot" style="background:'
            f'{"#6fb3ff" if g.get("como") else "#e0353b"}"></span><span class="min">{esc(g["min"])}</span>'
            f'<span class="who">{esc(g["who"])}</span></div>' for g in spec.get("goals", [])
        ) or '<div class="goal"><span class="who">—</span></div>'
    return Template((TPL / f"{kind}.html").read_text(encoding="utf-8")).safe_substitute(s)


def table_html(subtitle, prof=None):
    import datetime as dt

    prof = prof or {"league": "ita.1", "team_id": "2572", "lang": "ru", "teams_file": "teams_ru.json", "tz_hours": 3}
    lab = LABELS[prof["lang"]]
    req = urllib.request.Request(f"https://site.api.espn.com/apis/v2/sports/soccer/{prof['league']}/standings",
                                 headers={"User-Agent": "Mozilla/5.0"})
    st = json.loads(urllib.request.urlopen(req, timeout=30).read())
    teams = json.loads((HERE / "data" / prof["teams_file"]).read_text(encoding="utf-8"))
    entries = []
    for e in st["children"][0]["standings"]["entries"]:
        s = {x["name"]: x.get("value") for x in e["stats"]}
        entries.append((int(s.get("rank") or 0), e["team"], s))
    rows = []
    for rank, team, s in sorted(entries, key=lambda x: x[0]):
        tid = str(team["id"])
        name = teams.get(tid, {}).get("name", team["displayName"])
        zone = "cl" if rank <= 4 else "el" if rank <= 6 else "rel" if rank >= 18 else ""
        gd = int(s.get("pointDifferential") or 0)
        rows.append(f'<div class="row {zone}{" como" if tid == str(prof["team_id"]) else ""}"><div class="pos">{rank}</div>'
                    f'<img src="https://a.espncdn.com/i/teamlogos/soccer/500/{tid}.png"><div>{esc(name)}</div>'
                    f'<div class="num">{int(s.get("gamesPlayed") or 0)}</div><div class="num">{f"{gd:+d}" if gd else "0"}</div>'
                    f'<div class="pts">{int(s.get("points") or 0)}</div></div>')
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=prof.get("tz_hours", 3))))
    words = {k: esc(v) for k, v in lab.items() if isinstance(v, str)}
    return Template((TPL / "table.html").read_text(encoding="utf-8")).safe_substitute(
        words, weekday=lab["weekdays"][now.weekday()], date=now.strftime("%d.%m.%Y"), subtitle=esc(subtitle),
        rows="".join(rows))


def render(kind, spec_path, out, prof_name=None):
    page = TPL / f"_render_{kind}.html"
    if kind == "table":
        # spec_path is the subtitle here
        page.write_text(table_html(spec_path, profile(prof_name) if prof_name else None), encoding="utf-8")
    else:
        spec = json.loads(Path(spec_path).read_text(encoding="utf-8-sig"))
        page.write_text(build(kind, spec), encoding="utf-8")
    out = str(Path(out).resolve())
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([browser(), "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1",
                        f"--user-data-dir={prof}", "--window-size=1600,2000", "--virtual-time-budget=10000",
                        f"--screenshot={out}", page.as_uri()], check=True, capture_output=True, timeout=120)
    print(out)


def cutout(src, out):
    from PIL import Image
    from rembg import new_session, remove

    img = Image.open(fetch(src)).convert("RGBA")
    cut = remove(img, session=new_session("isnet-general-use"))
    bbox = cut.getchannel("A").point(lambda a: 255 if a > 20 else 0).getbbox()
    if bbox:
        cut = cut.crop(bbox)
    cut.save(out)
    print(str(Path(out).resolve()), cut.size)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    kind, a, b = sys.argv[1:4]
    if kind == "cutout":
        cutout(a, b)
    else:
        render(kind, a, b, sys.argv[4] if len(sys.argv) > 4 else None)


if __name__ == "__main__":
    main()

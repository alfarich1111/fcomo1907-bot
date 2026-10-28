"""Live match commentary for @FComo1907 (data: ESPN public API, posting: owner's account via tg.py).

Usage (run with .venv\\Scripts\\python.exe):
  live.py <espn_event_id> [--league ita.1] [--dry]

Waits until ~70 min before kickoff, posts Como's starting XI, then every goal, Como substitution,
card, half time and full time in the channel's chat style. After the final whistle it renders and
posts the result poster (poster.py) and exits. --dry replays a finished match: prints every message
and renders the poster to work/ without posting anything.
State lives in work/live_<id>.json, so a restarted run never posts the same event twice.
"""
import argparse
import asyncio
import datetime as dt
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

import poster
import tg

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"
DATA = HERE / "data"
COMO_ID = "2572"
MSK = dt.timezone(dt.timedelta(hours=3))
API = "https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/summary?event={event}"
SCHEDULE = "https://site.api.espn.com/apis/site/v2/sports/soccer/all/teams/2572/schedule"
STANDINGS = "https://site.api.espn.com/apis/v2/sports/soccer/{league}/standings"
LEAGUE_RU = {"ita.1": "Серия А", "uefa.champions": "Лига чемпионов", "ita.coppa_italia": "Кубок Италии"}
WEEKDAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

# Premium emoji from the channel's own posts.
E = {
    "goal": "5226842334418736150", "out": "5210952531676504517", "in": "5427009714745517609",
    "flash": "5456140674028019486", "live": "5411225014148014586", "eyes": "5424885441100782420",
    "bullet": "5220069935497097998",
}
FALLBACK = {"goal": "⚽️", "out": "❌", "in": "✅", "flash": "⚡️", "live": "🔴", "eyes": "👀", "bullet": "🔹"}

TEAMS = {k: v for k, v in json.loads((DATA / "teams_ru.json").read_text(encoding="utf-8")).items() if k[0] != "_"}
NAMES = {k: v for k, v in json.loads((DATA / "names_ru.json").read_text(encoding="utf-8")).items() if k[0] != "_"}


def em(key):
    return f'<tg-emoji emoji-id="{E[key]}">{FALLBACK[key]}</tg-emoji>'


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


# ---------- names ----------

_TR = [("sch", "ш"), ("shch", "щ"), ("sh", "ш"), ("ch", "ч"), ("zh", "ж"), ("kh", "х"), ("ts", "ц"), ("yu", "ю"),
       ("ya", "я"), ("yo", "ё"), ("gn", "нь"), ("gli", "льи"), ("ll", "лл"), ("ou", "у"), ("ph", "ф"), ("th", "т"),
       ("w", "в"), ("x", "кс"), ("q", "к"), ("j", "дж"), ("c", "к"), ("y", "и"), ("a", "а"), ("b", "б"), ("d", "д"),
       ("e", "е"), ("f", "ф"), ("g", "г"), ("h", "х"), ("i", "и"), ("k", "к"), ("l", "л"), ("m", "м"), ("n", "н"),
       ("o", "о"), ("p", "п"), ("r", "р"), ("s", "с"), ("t", "т"), ("u", "у"), ("v", "в"), ("z", "з")]


def translit(word):
    w = unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode().lower()
    out, i = "", 0
    while i < len(w):
        for lat, cyr in _TR:
            if w.startswith(lat, i):
                out += cyr
                i += len(lat)
                break
        else:
            out += w[i]
            i += 1
    return out[:1].upper() + out[1:]


def name_ru(display, full=False):
    if not display:
        return ""
    if display in NAMES:
        return NAMES[display][0 if full else 1]
    parts = [translit(p) for p in re.split(r"[\s]+", display) if p]
    return " ".join(parts) if full else parts[-1]


def team_ru(team_id, display=""):
    return TEAMS.get(str(team_id), {"name": translit(display) if display else "?", "with": display, "vs": f"«{display}»"})


def plural(n, one, few, many):
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def minute(ev):
    v = (ev.get("clock") or {}).get("displayValue", "")
    return v.replace("'+", "+").replace("'", "") + "’" if v else ""


# ---------- match model ----------

class Match:
    def __init__(self, event_id, league):
        self.id, self.league = str(event_id), league
        self.state_path = WORK / f"live_{self.id}.json"
        self.state = json.loads(self.state_path.read_text(encoding="utf-8")) if self.state_path.exists() else {
            "posted": [], "lineup": False, "result": False, "trailed": False, "goals": []}
        self.data = {}

    def save(self):
        WORK.mkdir(exist_ok=True)
        self.state_path.write_text(json.dumps(self.state, ensure_ascii=False, indent=1), encoding="utf-8")

    def refresh(self):
        self.data = get_json(API.format(league=self.league, event=self.id))
        comp = self.data["header"]["competitions"][0]
        self.status = comp["status"]["type"]
        self.kickoff = dt.datetime.fromisoformat(comp["date"].replace("Z", "+00:00"))
        sides = {c["homeAway"]: c for c in comp["competitors"]}
        self.home, self.away = sides["home"], sides["away"]
        self.como_home = str(self.home["team"]["id"]) == COMO_ID
        self.opp = self.away if self.como_home else self.home
        self.score = [int(self.home.get("score") or 0), int(self.away.get("score") or 0)]

    def logo(self, side, left):
        t = side["team"]
        info = team_ru(t["id"], t.get("displayName", ""))
        if info.get("emoji"):
            fb = "🇮🇹" if str(t["id"]) == COMO_ID else "⚽️"
            return f'<tg-emoji emoji-id="{info["emoji"]}">{fb}</tg-emoji>'
        return f'«{info["name"]}» ' if left else f' «{info["name"]}»'

    def footer(self, score=None):
        # Running score from the goals posted so far, so replays and lagging feeds stay consistent.
        h, a = score or self.state.get("score") or self.score
        return f"@FComo1907 | {self.logo(self.home, True)}{h}:{a}{self.logo(self.away, False)}"

    def score_from_text(self, text):
        hn, an = re.escape(self.home["team"]["displayName"]), re.escape(self.away["team"]["displayName"])
        m = re.search(rf"{hn} (\d+), {an} (\d+)", text or "")
        return [int(m.group(1)), int(m.group(2))] if m else None


# ---------- messages ----------

def lineup_msg(m):
    for r in m.data.get("rosters") or []:
        if str(r["team"]["id"]) != COMO_ID:
            continue
        starters = [p for p in r.get("roster", []) if p.get("starter")]
        if len(starters) < 11:
            return None
        names = ", ".join(name_ru(p["athlete"]["displayName"]) for p in starters)
        formation = f" ({r['formation']})" if r.get("formation") else ""
        return f"{em('flash')} <b>Стартовый состав «Комо»{formation}</b>\n\n{names}\n\n{m.footer()}"
    return None


def event_msgs(m, events):
    """Turn new ESPN key events into channel messages (Como subs at the same minute are grouped)."""
    msgs, subs = [], {}
    for ev in events:
        typ = (ev.get("type") or {}).get("type", "")
        team_id = str((ev.get("team") or {}).get("id", ""))
        como = team_id == COMO_ID
        people = [p["athlete"]["displayName"] for p in ev.get("participants") or [] if p.get("athlete")]
        mn = minute(ev)
        if typ == "kickoff":
            m.state["score"] = [0, 0]
            msgs.append(f"<b>1’ | Матч начался</b>\n\n{m.footer()}")
        elif "goal" in typ or typ == "penalty---scored":
            sc = m.score_from_text(ev.get("text")) or m.score
            m.state["score"] = sc
            own = "own" in typ
            scorer = name_ru(people[0]) if people else ""
            assist = name_ru(people[1], full=True) if len(people) > 1 and not own else ""
            como_scored = como != own if team_id else False
            pen = " с пенальти" if "penalty" in typ else ""
            if como_scored:
                body = f"<b>{mn} | Гол! {scorer}!</b>" if not own else f"<b>{mn} | Автогол! Мы забиваем!</b>"
                if pen:
                    body += f"\n\nРеализует пенальти"
                if assist:
                    body += f"\n\n{em('bullet')} Ассист — {assist}"
            else:
                body = f"<b>{mn} | Пропускаем…</b>\n\n" + (f"Автогол — {scorer}" if own else f"Гол{pen} — {scorer}")
            ch, ca = (sc[0], sc[1]) if m.como_home else (sc[1], sc[0])
            if ch < ca:
                m.state["trailed"] = True
            poster_name = name_ru(people[0], full=como and not own) if people else ""
            m.state["goals"].append({"min": mn, "who": (f"Автогол ({scorer})" if own else poster_name + (" (пен.)" if pen else "")),
                                     "como": como_scored})
            msgs.append(f"{em('goal') if como_scored else ''} {body}\n\n{m.footer(sc)}".strip())
        elif typ == "substitution" and como and len(people) >= 2:
            subs.setdefault(mn, []).append((name_ru(people[0], full=True), name_ru(people[1], full=True)))
        elif typ == "yellow-card" and como and people:
            msgs.append(f"🟨 <b>{mn} | Жёлтая карточка</b>\n\n{name_ru(people[0], full=True)}\n\n{m.footer()}")
        elif typ in ("red-card", "yellow-red-card") and people:
            who = name_ru(people[0], full=True)
            team = "у нас" if como else f"у {team_ru(team_id)['name']}"
            msgs.append(f"🟥 <b>{mn} | Удаление {team}!</b>\n\n{who}\n\n{m.footer()}")
        elif typ == "penalty---missed" and people:
            who = name_ru(people[0], full=True)
            msgs.append(f"<b>{mn} | {'Не забиваем' if como else 'Соперник не забивает'} пенальти!</b>\n\n{who}\n\n{m.footer()}")
        elif typ == "halftime":
            msgs.append(f"<b>Перерыв</b>\n\n{m.footer()}")
        elif typ == "start-2nd-half":
            msgs.append(f"<b>46’ | Второй тайм начался</b>\n\n{m.footer()}")
    for mn, pairs in subs.items():
        n = len(pairs)
        title = "Замена" if n == 1 else f"{['', '', 'Две', 'Три', 'Четыре', 'Пять'][min(n, 5)]} замены"
        title += " в перерыве" if mn.startswith("45") or mn.startswith("46") else f" ({mn})"
        outs = "\n".join(f"{em('out')} {o}" for _, o in pairs)
        ins = "\n".join(f"{em('in')} {i}" for i, _ in pairs)
        msgs.append(f"<b>{title}:</b>\n\n{outs}\n\n{ins}\n\n{m.footer()}")
    return msgs


# ---------- result poster ----------

def recent_form(event_id):
    sched = get_json(SCHEDULE)
    res = []
    for ev in sorted(sched.get("events", []), key=lambda e: e["date"]):
        comp = ev["competitions"][0]
        if not comp["status"]["type"].get("completed"):
            continue
        if ev.get("league", {}).get("slug", "").startswith("club.friendly"):
            continue
        cs = {str(c["team"]["id"]): c for c in comp["competitors"]}
        como = cs.get(COMO_ID)
        if not como:
            continue
        opp = next(c for k, c in cs.items() if k != COMO_ID)
        a, b = int(como["score"]["value"] if isinstance(como["score"], dict) else como["score"]), \
            int(opp["score"]["value"] if isinstance(opp["score"], dict) else opp["score"])
        res.append("W" if a > b else "D" if a == b else "L")
    return res


def series_text(res):
    if not res:
        return "—"
    last, n = res[-1], 0
    for r in reversed(res):
        if r != last:
            break
        n += 1
    if last == "W" and n >= 2:
        return f"{n} {plural(n, 'победа', 'победы', 'побед')} подряд"
    unbeaten = 0
    for r in reversed(res):
        if r == "L":
            break
        unbeaten += 1
    if unbeaten >= 2:
        return f"{unbeaten} {plural(unbeaten, 'матч', 'матча', 'матчей')} без поражений"
    if last == "L" and n >= 2:
        return f"{n} {plural(n, 'поражение', 'поражения', 'поражений')} подряд"
    return {"W": "Победа", "D": "Ничья", "L": "Поражение"}[last] + " в последнем"


def table_text(league):
    if league != "ita.1":
        return "—"
    st = get_json(STANDINGS.format(league=league))
    for e in st["children"][0]["standings"]["entries"]:
        if str(e["team"]["id"]) == COMO_ID:
            stats = {s["name"]: s.get("value") for s in e["stats"]}
            pts = int(stats.get("points") or 0)
            return f"{int(stats.get('rank') or 0)}-е, {pts} {plural(pts, 'очко', 'очка', 'очков')}"
    return "—"


def league_round(league):
    """Serie A round = games Como has played (the finished match included)."""
    if league != "ita.1":
        return None
    try:
        st = get_json(STANDINGS.format(league=league))
        for e in st["children"][0]["standings"]["entries"]:
            if str(e["team"]["id"]) == COMO_ID:
                return int({s["name"]: s.get("value") for s in e["stats"]}.get("gamesPlayed") or 0) or None
    except Exception:
        return None


def kicker(m, done, meta=None):
    # ESPN has no round number; the match-day task stores e.g. "Серия А · 10 тур" in match_<id>.json.
    base = (meta or {}).get("kicker")
    if not base:
        week = m.data.get("header", {}).get("week") or league_round(m.league)
        base = " · ".join(p for p in [LEAGUE_RU.get(m.league, ""), f"{week} тур" if week else ""] if p)
    return " · ".join(p for p in (["Матч окончен"] if done else []) + [base] if p)


def remote_meta(event_id):
    """In the cloud the match-day task publishes match_<id>.json on the repo's data branch."""
    tpl = os.environ.get("FCOMO_META_URL")  # e.g. https://raw.githubusercontent.com/<user>/<repo>/<branch>/data/matches/{id}.json
    if not tpl:
        return {}
    try:
        return get_json(tpl.format(id=event_id))
    except Exception as e:
        print("no remote match meta:", e, flush=True)
        return {}


def default_como_img():
    """Fallback poster image when the match-day task left no player cutout (e.g. in the cloud)."""
    for p in sorted((HERE / "players").glob("*.png")):
        return str(p)
    return f"https://a.espncdn.com/i/teamlogos/soccer/500/{COMO_ID}.png"


def result_post(m, dry):
    WORK.mkdir(exist_ok=True)
    ch, ca = (m.score if m.como_home else m.score[::-1])
    opp = team_ru(m.opp["team"]["id"], m.opp["team"]["displayName"])
    win, draw = ch > ca, ch == ca
    local = m.kickoff.astimezone(MSK)
    meta_path = WORK / f"match_{m.id}.json"   # written by the match-day task: player cutouts etc.
    meta = json.loads(meta_path.read_text(encoding="utf-8-sig")) if meta_path.exists() else remote_meta(m.id)
    img = meta.get("result_img") or meta.get("como_img") or ""
    if img.startswith("http"):
        # The cloud match-day task stores the photo URL; cut the player out here.
        try:
            out = WORK / f"como_{m.id}.png"
            poster.cutout(img, out)
            meta["como_img"], meta["result_img"] = str(out), ""
        except Exception as e:
            print("cutout failed:", e, flush=True)
            meta["como_img"] = meta["result_img"] = ""
    home_t, away_t = m.home["team"], m.away["team"]
    form = recent_form(m.id)
    spec = {
        "weekday": WEEKDAYS[local.weekday()], "date": local.strftime("%d.%m.%Y"), "kicker": kicker(m, True, meta),
        "home": team_ru(home_t["id"], home_t["displayName"])["name"],
        "away": team_ru(away_t["id"], away_t["displayName"])["name"],
        "home_logo": f"https://a.espncdn.com/i/teamlogos/soccer/500/{home_t['id']}.png",
        "away_logo": f"https://a.espncdn.com/i/teamlogos/soccer/500/{away_t['id']}.png",
        "score": f"{m.score[0]}:{m.score[1]}",
        "winner": "" if draw else ("home" if (m.score[0] > m.score[1]) else "away"),
        "right_img": meta.get("result_img") or meta.get("como_img") or default_como_img(),
        "k2": ("Победа дома" if m.como_home else "Победа в гостях") if win else ("Ничья" if draw else "Поражение"),
        "hl1": ("Камбэк" if m.state.get("trailed") else "Победа") if win else ("Ничья" if draw else "Поражение"),
        "hl2": f"над {opp['with']}" if win else (f"с {opp['with']}" if draw else f"в матче с {opp['with']}"),
        "goals": m.state["goals"], "table": table_text(m.league), "series": series_text(form),
        "form": "".join(form[-5:]),
    }
    if win and m.state.get("trailed"):
        spec["k2"] = "Волевая победа"
    spec_path = WORK / f"result_{m.id}.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    png = WORK / f"result_{m.id}.png"
    poster.render("result", spec_path, png)

    head = ("Победа!" if not m.state.get("trailed") else "Волевая победа!") if win else ("Ничья" if draw else "Поражение")
    line = (f"«Комо» обыгрывает {opp['vs']} со счётом {ch}:{ca}" if win else
            f"Ничья {ch}:{ca} в матче с {opp['vs']}" if draw else
            f"«Комо» уступает в матче с {opp['vs']} — {ch}:{ca}")
    goals = "\n".join(f"{em('goal') if g['como'] else '▫️'} {g['min']} — {g['who']}" for g in m.state["goals"])
    caption = f"{em('flash')} <b>{head}</b>\n\n{line}\n\n{goals}\n\n{m.footer()}".replace("\n\n\n\n", "\n\n")
    return caption, png


# ---------- runner ----------

async def run(event_id, league, dry):
    m = Match(event_id, league)
    sent = 0

    async def send(text, photo=None):
        nonlocal sent
        sent += 1
        if dry:
            print(f"--- message {sent}{' [photo ' + str(photo) + ']' if photo else ''}\n{text}\n")
            return
        await tg.send(text, photo)

    m.refresh()
    if not dry:
        # The cloud match-day routine can ship extra Russian names / team forms with the match meta.
        meta = remote_meta(m.id)
        NAMES.update(meta.get("names") or {})
        TEAMS.update(meta.get("teams") or {})
    fresh = not m.state["posted"] and not m.state["lineup"]
    if not dry and fresh and m.status.get("state") == "post":
        # A late duplicate run (e.g. a queued cloud job) must not repost the whole match.
        print("match already finished and nothing recorded here; not posting", flush=True)
        return
    if not dry and fresh and m.status.get("state") == "in":
        # Restarted mid-match without state: skip what already happened, continue from now.
        m.state["posted"] = [str(ev.get("id")) for ev in m.data.get("keyEvents") or []]
        m.state["lineup"] = True
        m.state["score"] = m.score
        m.save()
        print(f"resumed mid-match, skipped {len(m.state['posted'])} earlier events", flush=True)
    if not dry:
        wait = (m.kickoff - dt.datetime.now(dt.timezone.utc)).total_seconds() - 70 * 60
        if wait > 0:
            print(f"kickoff {m.kickoff:%Y-%m-%d %H:%M}Z, sleeping {int(wait // 60)} min", flush=True)
            time.sleep(wait)
    while True:
        try:
            m.refresh()
        except Exception as e:  # network hiccup: try again shortly
            print("refresh failed:", e, flush=True)
            time.sleep(30)
            continue
        if not m.state["lineup"]:
            msg = lineup_msg(m)
            if msg:
                await send(msg)
                m.state["lineup"] = True
                m.save()
        new = [ev for ev in m.data.get("keyEvents") or [] if str(ev.get("id")) not in m.state["posted"]]
        if new:
            for msg in event_msgs(m, new):
                await send(msg)
            m.state["posted"] += [str(ev.get("id")) for ev in new]
            m.save()
        if m.status.get("completed") or m.status.get("state") == "post":
            if not m.state["result"]:
                caption, png = result_post(m, dry)
                await send(caption, png)
                m.state["result"] = True
                m.save()
            print(f"done, {sent} messages", flush=True)
            return
        if dry:
            print("match not finished yet; --dry only replays finished matches")
            return
        time.sleep(20 if m.status.get("state") == "in" else 60)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("event")
    p.add_argument("--league", default="ita.1")
    p.add_argument("--dry", action="store_true")
    a = p.parse_args()
    if a.dry:
        # Dry runs keep their own state so they never mark a real match as posted.
        global WORK
        WORK = HERE / "work" / "dry"
        WORK.mkdir(parents=True, exist_ok=True)
        (WORK / f"live_{a.event}.json").unlink(missing_ok=True)
    asyncio.run(run(a.event, a.league, a.dry))


if __name__ == "__main__":
    main()

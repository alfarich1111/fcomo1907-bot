"""Live match commentary for CHELSEA UZ (@CHELSI_CHELSEAUZ_CFCUZ) in Uzbek, in that channel's style.

Usage (run with .venv\\Scripts\\python.exe):
  live_chelsea.py <espn_event_id> [--league eng.1] [--dry]

Same engine as live.py (ESPN feed, state in work/live_<id>.json, restart-safe); only the team, the channel,
the language and the post templates differ. Kickoff times are Tashkent time (UTC+5), like the channel's posts.
"""
import argparse
import asyncio
import datetime as dt
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import live
import poster
import tg

PROFILE = poster.profile("chelsea")
TEAM_ID = PROFILE["team_id"]
CHANNEL = PROFILE["channel"]
TZ = dt.timezone(dt.timedelta(hours=PROFILE["tz_hours"]))
SIGN = PROFILE["signature"]
EMO = PROFILE["emoji"]
LEAGUE_UZ = {"eng.1": "Premer-liga", "uefa.champions": "Chempionlar ligasi", "uefa.europa": "Yevropa ligasi",
             "uefa.europa.conf": "Konferensiya ligasi", "eng.fa": "Angliya kubogi", "eng.league_cup": "Carabao Cup",
             "fifa.cwc": "Klublar o'rtasidagi jahon chempionati"}
TEAMS = {k: v for k, v in json.loads((live.DATA / PROFILE["teams_file"]).read_text(encoding="utf-8")).items() if k[0] != "_"}
NAMES = {k: v for k, v in json.loads((live.DATA / PROFILE["names_file"]).read_text(encoding="utf-8")).items() if k[0] != "_"}

# The shared engine (Match, recent_form, remote_meta) reads these module globals.
live.COMO_ID = TEAM_ID
live.SCHEDULE = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/teams/{TEAM_ID}/schedule"


def em(key):
    eid, fb = EMO[key]
    return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>'


def plain(s):
    """The channel writes names without accents (Joao Pedro, Estevao)."""
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode() or (s or "")


def name(display, full=True):
    if display in NAMES:
        return NAMES[display][0 if full else 1]
    return plain(display) if full else plain(display).split()[-1]


def team(t):
    tid = str(t["id"])
    info = TEAMS.get(tid, {})
    return {"name": info.get("name") or plain(t.get("shortDisplayName") or t.get("displayName", "")),
            "emoji": info.get("emoji"), "color": info.get("color")}


def badge(t):
    info = team(t)
    return f'<tg-emoji emoji-id="{info["emoji"]}">🇬🇧</tg-emoji>' if info["emoji"] else "⚽️"


def score_line(m, score=None):
    h, a = score or m.state.get("score") or m.score
    hn, an = team(m.home["team"])["name"], team(m.away["team"])["name"]
    return f'{badge(m.home["team"])}<b> "{hn}" {h}-{a} "{an}" </b>{badge(m.away["team"])}'


# ---------- messages ----------

def lineup_msg(m):
    for r in m.data.get("rosters") or []:
        if str(r["team"]["id"]) != TEAM_ID:
            continue
        starters = [p for p in r.get("roster", []) if p.get("starter")]
        if len(starters) < 11:
            return None
        names = "\n".join(name(p["athlete"]["displayName"]) for p in starters)
        formation = f" ({r['formation']})" if r.get("formation") else ""
        kick = m.kickoff.astimezone(TZ).strftime("%H:%M")
        return (f"{em('lineup')}<b> \"Chelsea\"ning asosiy tarkibi{formation}:</b>\n\n{names}\n\n"
                f"{em('clock')}<b> Boshlanish vaqti - {kick}</b>\n\n{SIGN}")
    return None


def event_msgs(m, events):
    msgs, subs = [], {}
    for ev in events:
        typ = (ev.get("type") or {}).get("type", "")
        team_id = str((ev.get("team") or {}).get("id", ""))
        ours = team_id == TEAM_ID
        people = [p["athlete"]["displayName"] for p in ev.get("participants") or [] if p.get("athlete")]
        mn = live.minute(ev).replace("’", "'")
        if typ == "kickoff":
            m.state["score"] = [0, 0]
            msgs.append(f"{em('check')}<b> Uchrashuv boshlandi!</b>\n\n{SIGN}")
        elif "goal" in typ or typ == "penalty---scored":
            prev = m.state.get("score") or [0, 0]
            sc = m.score_from_text(ev.get("text")) or m.score
            m.state["score"] = sc
            own = "own" in typ
            pen = "penalty" in typ
            scorer = name(people[0]) if people else ""
            assist = name(people[1]) if len(people) > 1 and not own else ""
            # Whose goal it is comes from the score change (ESPN's team on own goals is ambiguous).
            if sc[0] != prev[0] or sc[1] != prev[1]:
                we_scored = (sc[0] > prev[0]) == m.como_home
            else:
                we_scored = ours != own if team_id else False
            ch, ca = (sc[0], sc[1]) if m.como_home else (sc[1], sc[0])
            if ch < ca:
                m.state["trailed"] = True
            who = f"{scorer} (avtogol)" if own else scorer + (" (pen)" if pen else "")
            m.state["goals"].append({"min": mn, "who": who, "como": we_scored})
            if we_scored:
                body = f"{em('goal')}<b> 🇬 🇴 🇴 🇴 🇱</b>\n\n{score_line(m, sc)}\n{em('scorer')} {who} {mn}"
                if assist:
                    body += f"\n🅰️ Assist: {assist}"
            else:
                opp = team(m.opp["team"])["name"]
                body = f"{mn} | \"{opp}\" gol urdi. {who}\n\n{score_line(m, sc)}"
            msgs.append(f"{body}\n\n{SIGN}")
        elif typ == "substitution" and ours and len(people) >= 2:
            subs.setdefault(mn, []).append((name(people[0]), name(people[1])))
        elif typ == "yellow-card" and ours and people:
            msgs.append(f"{mn} | 🟨 {name(people[0])} sariq kartochka oldi")
        elif typ in ("red-card", "yellow-red-card") and people:
            whose = "Jamoamiz" if ours else f"\"{team(m.opp['team'])['name']}\""
            msgs.append(f"{em('red')}<b> {mn} | {whose} futbolchisi {name(people[0])} maydondan chetlatildi!</b>\n\n"
                        f"{score_line(m)}\n\n{SIGN}")
        elif typ == "penalty---missed" and people:
            whose = "Bizning" if ours else f"\"{team(m.opp['team'])['name']}\""
            msgs.append(f"{em('pen_miss')} {mn} | {whose} {name(people[0])} penaltini amalga oshira olmadi!")
        elif typ == "halftime":
            msgs.append(f"{em('check')}<b> Birinchi bo'lim yakunlandi!</b>\n\n{score_line(m)}\n\n{SIGN}")
        elif typ == "start-2nd-half":
            msgs.append(f"{em('check')}<b> Ikkinchi bo'lim boshlandi!</b>\n\n{SIGN}")
    for mn, pairs in subs.items():
        lines = "\n\n".join(f"{em('in')}{i}\n{em('out')}{o}" for i, o in pairs)
        msgs.append(f"{mn}<b> | </b>{em('sub')}<b> Jamoamiz safida o'zgarish:</b>\n\n{lines}\n\n{SIGN}")
    return msgs


# ---------- result poster ----------

def league_round(league):
    try:
        st = live.get_json(live.STANDINGS.format(league=league))
        for e in st["children"][0]["standings"]["entries"]:
            if str(e["team"]["id"]) == TEAM_ID:
                stats = {s["name"]: s.get("value") for s in e["stats"]}
                return int(stats.get("gamesPlayed") or 0) or None, int(stats.get("rank") or 0), int(stats.get("points") or 0)
    except Exception:
        pass
    return None, None, None


def series_uz(res):
    if not res:
        return "—"
    last, n = res[-1], 0
    for r in reversed(res):
        if r != last:
            break
        n += 1
    if last == "W" and n >= 2:
        return f"{n} ta g'alaba ketma-ket"
    unbeaten = next((i for i, r in enumerate(reversed(res)) if r == "L"), len(res))
    if unbeaten >= 2:
        return f"{unbeaten} o'yin mag'lubiyatsiz"
    if last == "L" and n >= 2:
        return f"{n} ta mag'lubiyat ketma-ket"
    return {"W": "G'alaba", "D": "Durang", "L": "Mag'lubiyat"}[last]


def result_post(m, dry):
    live.WORK.mkdir(exist_ok=True)
    ch, ca = (m.score if m.como_home else m.score[::-1])
    opp = team(m.opp["team"])["name"]
    win, draw = ch > ca, ch == ca
    local = m.kickoff.astimezone(TZ)
    meta = live.remote_meta(m.id) if not dry else {}
    img = meta.get("como_img") or ""
    if img.startswith("http"):
        try:
            out = live.WORK / f"chelsea_{m.id}.png"
            poster.cutout(img, out)
            img = str(out)
        except Exception as e:
            print("cutout failed:", e, flush=True)
            img = ""
    rnd, rank, pts = league_round(m.league) if m.league == "eng.1" else (None, None, None)
    base = meta.get("kicker") or " · ".join(p for p in [LEAGUE_UZ.get(m.league, ""), f"{rnd}-tur" if rnd else ""] if p)
    form = live.recent_form(m.id)
    spec = {
        "lang": "uz", "tag": "@cfc_uz", "theme": PROFILE.get("theme", ""),
        "weekday": poster.LABELS["uz"]["weekdays"][local.weekday()], "date": local.strftime("%d.%m.%Y"),
        # The themed poster has its own "Uchrashuv yakunlandi" banner, so the kicker is just the competition.
        "kicker": base if PROFILE.get("theme") else (f"Uchrashuv yakunlandi · {base}" if base else "Uchrashuv yakunlandi"),
        "home": team(m.home["team"])["name"], "away": team(m.away["team"])["name"],
        "home_logo": f"https://a.espncdn.com/i/teamlogos/soccer/500/{m.home['team']['id']}.png",
        "away_logo": f"https://a.espncdn.com/i/teamlogos/soccer/500/{m.away['team']['id']}.png",
        "score": f"{m.score[0]}:{m.score[1]}",
        "winner": "" if draw else ("home" if m.score[0] > m.score[1] else "away"),
        "right_img": img or f"https://a.espncdn.com/i/teamlogos/soccer/500/{TEAM_ID}.png",
        "k2": ("Uyda g'alaba" if m.como_home else "Safarda g'alaba") if win else ("Hisob teng" if draw else "Afsuski"),
        "hl1": ("Kambek" if m.state.get("trailed") else "G'alaba") if win else ("Durang" if draw else "Mag'lubiyat"),
        "hl2": f"{opp} ustidan" if win else (f"{opp} bilan" if draw else f"{opp}ga qarshi"),
        "goals": m.state["goals"],
        "table": f"{rank}-o'rin, {pts} ochko" if rank else "—",
        "series": series_uz(form), "form": "".join(form[-5:]),
    }
    spec_path = live.WORK / f"result_{m.id}.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    png = live.WORK / f"result_{m.id}.png"
    poster.render("result", spec_path, png)
    goals = "\n".join(f"{em('scorer') if g['como'] else '▫️'} {g['who']} {g['min']}" for g in m.state["goals"])
    caption = f"{em('final')}<b> Uchrashuv yakunlandi!</b>\n\n{score_line(m)}" + (f"\n{goals}" if goals else "")
    shoot = [m.home.get("shootoutScore"), m.away.get("shootoutScore")]
    if all(s is not None for s in shoot):
        caption += f"\n🧤 <b>Penaltilar - {int(float(shoot[0]))}:{int(float(shoot[1]))}</b>"
    caption += f"\n\n{SIGN}"
    return caption, png


# ---------- runner (same flow as live.py) ----------

async def run(event_id, league, dry):
    m = live.Match(event_id, league)
    sent = 0

    async def send(text, photo=None):
        nonlocal sent
        sent += 1
        if dry:
            print(f"--- message {sent}{' [photo ' + str(photo) + ']' if photo else ''}\n{text}\n")
            return
        await tg.send(text, photo, CHANNEL)

    m.refresh()
    if not dry:
        meta = live.remote_meta(m.id)
        NAMES.update(meta.get("names") or {})
        TEAMS.update(meta.get("teams") or {})
    fresh = not m.state["posted"] and not m.state["lineup"]
    if not dry and fresh and m.status.get("state") == "post":
        print("match already finished and nothing recorded here; not posting", flush=True)
        return
    if not dry and fresh and m.status.get("state") == "in":
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
        except Exception as e:
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
    p.add_argument("--league", default=PROFILE["league"])
    p.add_argument("--dry", action="store_true")
    a = p.parse_args()
    if a.dry:
        live.WORK = live.HERE / "work" / "dry"
        live.WORK.mkdir(parents=True, exist_ok=True)
        (live.WORK / f"live_{a.event}.json").unlink(missing_ok=True)
    asyncio.run(run(a.event, a.league, a.dry))


if __name__ == "__main__":
    main()

"""Official Premier League studio portraits for the matchday posters.

  python players.py squad <PL team id | team name>   squad with portrait URLs (e.g. "Man Utd", 8)
  python players.py chelsea                          Chelsea players in rotation order for today's matchday

The rotation moves one player forward with every official Chelsea match played this season,
so each matchday poster shows a different Chelsea player (skip anyone injured and take the next).
"""
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
API = "https://sdp-prem-prod.premier-league-prod.pulselive.com/api"
PHOTO = "https://resources.premierleague.com/premierleague25/photos/players/500x500/{}.png"
HEADERS = {"User-Agent": "Mozilla/5.0", "Origin": "https://www.premierleague.com"}


def get(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30).read())


def season():
    today = dt.date.today()
    return today.year if today.month >= 7 else today.year - 1


def has_photo(pid):
    try:
        req = urllib.request.Request(PHOTO.format(pid), headers=HEADERS, method="HEAD")
        return urllib.request.urlopen(req, timeout=20).status == 200
    except Exception:
        return False


def team_id(arg):
    if arg.isdigit():
        return arg
    teams = get(f"{API}/v1/competitions/8/seasons/{season()}/teams?_limit=40")["data"]
    q = arg.lower().replace("utd", "united").replace("man ", "manchester ").replace("spurs", "tottenham")
    for t in teams:
        if q in (t["name"].lower(), t["shortName"].lower(), t["abbr"].lower()) or q in t["name"].lower():
            return t["id"]
    sys.exit(f"no Premier League team matches {arg!r}: " + ", ".join(t["name"] for t in teams))


def squad(tid):
    return get(f"{API}/v2/competitions/8/seasons/{season()}/teams/{tid}/squad")["players"]


def chelsea_matches_played():
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/teams/363/schedule?season={season()}"
    events = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30).read())["events"]
    return sum(1 for e in events if e.get("league", {}).get("slug") != "club.friendly"
               and e["competitions"][0].get("status", {}).get("type", {}).get("completed"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "squad" and len(sys.argv) > 2:
        for p in squad(team_id(" ".join(sys.argv[2:]))):
            print(p["id"], p.get("shirtNum") or "-", p["position"], p["name"]["display"], PHOTO.format(p["id"]), sep=" | ")
    elif cmd == "chelsea":
        names = json.loads((HERE / "data" / "chelsea_rotation.json").read_text(encoding="utf-8"))
        current = {p["name"]["display"]: p["id"] for p in squad("8")}
        names = [n for n in names if n in current]
        start = chelsea_matches_played() % len(names)
        for n in names[start:] + names[:start]:
            pid = current[n]
            if has_photo(pid):
                print(n, PHOTO.format(pid), sep=" | ")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()

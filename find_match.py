"""Print `event=<id>` and `league=<slug>` (GitHub Actions output format) when a Como match
kicks off within the next 3 hours or is in progress; print nothing otherwise."""
import datetime as dt
import json
import sys
import urllib.request

URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/all/teams/2572/schedule?fixture=true"


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    now = dt.datetime.now(dt.timezone.utc)
    for ev in data.get("events", []):
        slug = ev.get("league", {}).get("slug", "")
        if slug.startswith("club.friendly"):
            continue
        kickoff = dt.datetime.fromisoformat(ev["date"].replace("Z", "+00:00"))
        state = ev["competitions"][0]["status"]["type"].get("state")
        minutes = (kickoff - now).total_seconds() / 60
        if state != "post" and -240 <= minutes <= 180:
            print(f"event={ev['id']}")
            print(f"league={slug}")
            print(f"{ev['name']} at {kickoff:%Y-%m-%d %H:%M}Z ({state})", file=sys.stderr)
            return
    print("no Como match soon", file=sys.stderr)


if __name__ == "__main__":
    main()

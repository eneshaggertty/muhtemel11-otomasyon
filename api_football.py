"""API-Football (v3) istemcisi."""
import os
import requests

BASE = "https://v3.football.api-sports.io"


class PlanHatasi(RuntimeError):
    """Ücretsiz/mevcut planın izin vermediği istek."""


class ApiFootball:
    def __init__(self, key=None):
        self.key = (key or os.environ["FOOTBALL_API_KEY"]).strip()
        self.calls = 0

    def get(self, path, **params):
        self.calls += 1
        r = requests.get(BASE + path, params=params,
                         headers={"x-apisports-key": self.key}, timeout=30)
        r.raise_for_status()
        data = r.json()
        err = data.get("errors")
        if err:
            if isinstance(err, dict) and "plan" in err:
                raise PlanHatasi(f"API-Football plan sınırı ({path}): {err['plan']}")
            raise RuntimeError(f"API-Football hata ({path}): {err}")
        return data.get("response", [])

    def fixtures_by_date(self, date, tz):
        return self.get("/fixtures", date=date, timezone=tz)

    def fixtures_team(self, team, tz, next_=None, last=None):
        p = {"team": team, "timezone": tz}
        if next_:
            p["next"] = next_
        if last:
            p["last"] = last
        return self.get("/fixtures", **p)

    def fixtures_team_season(self, team, season, tz):
        return self.get("/fixtures", team=team, season=season, timezone=tz)

    def fixture(self, fixture_id, tz):
        r = self.get("/fixtures", id=fixture_id, timezone=tz)
        return r[0] if r else None

    def lineups(self, fixture_id):
        return self.get("/fixtures/lineups", fixture=fixture_id)

    def events(self, fixture_id):
        return self.get("/fixtures/events", fixture=fixture_id)

    def standings(self, league, season):
        r = self.get("/standings", league=league, season=season)
        return r[0]["league"]["standings"][0] if r else []

    def round_fixtures(self, league, season, round_name, tz):
        return self.get("/fixtures", league=league, season=season, round=round_name, timezone=tz)

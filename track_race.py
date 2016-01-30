# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Tracks race records and posts them to QLRace.com.
"""

import minqlx
import minqlx.database
import requests
import json
from datetime import datetime

RECORDS_KEY = "minqlx:race_records"


class track_race(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_hook("stats", self.handle_stats)
        self.add_hook("map", self.handle_map)

        # QLRace.com API key.
        self.set_cvar_once("qlx_raceKey", "api_key_goes_here")
        self.mode = self.get_cvar("qlx_raceMode", int)
        self.enabled = False
        self.map_name = ""

    def handle_stats(self, stats):
        """Gets ZMQ stats."""
        if stats["TYPE"] == "PLAYER_RACECOMPLETE" and self.mode in (0, 2):
            self.enabled = True
            self.map_name = self.game.map.lower()
        elif stats["TYPE"] == "PLAYER_STATS":
            self.update_pb(stats)

    def handle_map(self, map_name, factory):
        """Checks whether the current game mode is race."""
        if self.game.type_short == "race" and self.mode in (0, 2):
            self.enabled = True
        else:
            self.enabled = False

    @minqlx.thread
    def update_pb(self, stats):
        """Updates a players pb.
        :param stats: ZMQ PLAYER_STATS
        """
        if not self.enabled:
            return

        time = stats["DATA"]["SCORE"]
        if time == -1 or time == 2147483647 or time == 0:
            return

        mode = self.get_mode(stats["DATA"]["WEAPONS"])
        player_id = int(stats["DATA"]["STEAM_ID"])
        name = self.clean_text(stats["DATA"]["NAME"])
        match_guid = stats["DATA"]["MATCH_GUID"]
        payload = {"map": self.map_name, "mode": mode, "player_id": player_id, "name": name,
                   "time": time, "match_guid": match_guid}
        record = self.post_data(payload)
        if record:
            if mode % 2 != 0:
                strafe = " ^2(strafe)"
            else:
                strafe = ""

            time = time_string(abs(record["time_diff"]))
            if record["rank"] == 1:
                time_diff = "^0[^2-{}^0]".format(time)
                self.msg("^7{} ^2just set a new ^3world record! {}{}".format(name, time_diff, strafe))
            else:
                time_diff = "^0[^1+{}^0]".format(time)
                self.msg("^7{} ^2set a new pb and is now rank ^3{} {}{}".format(name, record["rank"], time_diff, strafe))

    def get_mode(self, weapon_stats):
        """Returns the race mode of a player. 0 or 2 for weapons
        and 1 or 3 for strafe.
        :param weapon_stats: ZMQ weapon stats
        """
        knockback_weapons = ("ROCKET", "PLASMA", "GRENADE", "BFG", "PROXMINE")
        for weapon in knockback_weapons:
            if weapon_stats[weapon]["S"] != 0:
                return self.mode

        return self.mode + 1

    def post_data(self, payload):
        """Posts record to QLRace.com. If there's any records
        in redis list and qlrace.com is online it will recursively
        call itself until all the records have been posted.
        :param payload: record data
        """
        headers = {"X-Api-Key": self.get_cvar("qlx_raceKey")}
        try:
            r = requests.post("https://qlrace.com/api/new", data=payload, headers=headers)
            r.raise_for_status()

            if self.db.llen(RECORDS_KEY) != 0:
                payload = json.loads(self.db.rpop(RECORDS_KEY))
                self.post_data(payload)

            if r.status_code == 200:
                return r.json()
        except requests.exceptions.RequestException as e:
            self.push_db(payload)
            self.msg("^2Error, {}".format(e))

    def push_db(self, payload):
        """Pushes record to redis list
        :param payload: record data
        """
        payload["date"] = str(datetime.utcnow())
        record = json.dumps(payload)
        self.db.lpush(RECORDS_KEY, record)


def time_string(time):
    """Returns a time string in the format s.ms or m:s.ms if time is more than
    or equal to 1 minute.
    :param time: Time in milliseconds
    """
    time = int(time)
    s, ms = divmod(time, 1000)
    ms = str(ms).zfill(3)
    if s < 60:
        return "{}.{}".format(s, ms)
    m, s = divmod(s, 60)
    s = str(s).zfill(2)
    return "{}:{}.{}".format(m, s, ms)

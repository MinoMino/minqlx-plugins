# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Tracks race records and posts them to QLRace.com.
"""

import minqlx
import minqlx.database
import json
import re
import requests
from datetime import datetime

RECORDS_KEY = "minqlx:race_records"


class track_race(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_hook("map", self.handle_map)
        self.add_hook("stats", self.handle_stats, minqlx.PRI_LOW)

        # QLRace.com API key.
        self.set_cvar_once("qlx_raceKey", "api_key_goes_here")
        self.mode = self.get_cvar("qlx_raceMode", int)

        try:
            self.map_name = self.game.map.lower()
            self.enabled = self.valid_mode()
        except minqlx.NonexistentGameError:
            self.map_name = ""
            self.enabled = False

    def handle_map(self, map_name, factory):
        """Checks race mode on map change."""
        self.enabled = self.valid_mode()

    def handle_stats(self, stats):
        """Gets ZMQ stats."""
        if stats["TYPE"] == "PLAYER_RACECOMPLETE" and self.mode in (0, 2):
            self.enabled = True
            self.map_name = self.game.map.lower()
            if stats["DATA"]["WEAPONS_USED"]:
                player = self.player(int(stats["DATA"]["STEAM_ID"]))
                if player.score == stats["DATA"]["RACE_TIME"]:
                    self.post_data(self.get_payload(stats["DATA"], self.mode, player.score))
        elif stats["TYPE"] == "PLAYER_STATS" and self.enabled:
            if stats["DATA"]["SCORE"] in (-1, 0, 2147483647):
                return

            weapons = track_race.weapons_used(stats["DATA"]["WEAPONS"])
            mode = self.mode if weapons else self.mode + 1
            self.post_data(self.get_payload(stats["DATA"], mode, stats["DATA"]["SCORE"]))

    def valid_mode(self):
        """Returns whether the current game type and race mode is valid."""
        if self.game.type_short == "race" and self.mode in (0, 2):
            return True
        else:
            return False

    @staticmethod
    def weapons_used(weapon_stats):
        """Returns whether the player used any knockback weapons.
        :param weapon_stats: ZMQ weapon stats
        """
        knockback_weapons = ("ROCKET", "PLASMA", "GRENADE", "BFG", "PROXMINE")
        for weapon in knockback_weapons:
            if weapon_stats[weapon]["S"] != 0:
                return True
        return False

    def get_payload(self, data, mode, time):
        """Returns payload to post to QLRace.com."""
        player_id = int(data["STEAM_ID"])
        name = re.sub(r"\^[0-9]", "", data["NAME"])
        return {"map": self.map_name, "mode": mode, "player_id": player_id, "name": name,
                "time": time, "match_guid": data["MATCH_GUID"], "date": str(datetime.utcnow())}

    @minqlx.thread
    def post_data(self, payload):
        """Posts record to QLRace.com. If there's any records
        in redis list and QLRace.com is online it will recursively
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
                self.callback_pb(r.json())
        except requests.exceptions.RequestException as e:
            self.push_db(payload)
            self.logger.error(e)
            self.msg("^2Error, connecting to qlrace.com")

    def push_db(self, payload):
        """Pushes payload to redis list."""
        self.db.lpush(RECORDS_KEY, json.dumps(payload))

    def callback_pb(self, record):
        """Outputs new pb text to chat."""
        strafe = " ^2(strafe)" if record["mode"] % 2 != 0 else ""

        time = self.plugins["race"].time_string(abs(record["time_diff"]))
        if record["rank"] == 1:
            time_diff = "^0[^2-{}^0]".format(time)
            self.msg("^7{} ^2just set a new ^3world record! {}{}".format(record["name"], time_diff, strafe))
        else:
            time_diff = "^0[^1+{}^0]".format(time)
            self.msg("^7{} ^2set a new pb and is now rank ^3{} {}{}"
                     .format(record["name"], record["rank"], time_diff, strafe))

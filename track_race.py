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
import requests
from datetime import datetime

RECORDS_KEY = "minqlx:race_records"


class track_race(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_hook("map", self.handle_map)
        self.add_hook("stats", self.handle_stats)
        self.add_command("posttimes", self.cmd_posttimes, 5)

        # QLRace.com API key.
        self.set_cvar_once("qlx_raceKey", "api_key_goes_here")
        self.mode = self.get_cvar("qlx_raceMode", int)
        self.enabled = False
        self.map_name = ""

    def handle_map(self, map_name, factory):
        """Checks whether the current game mode is race."""
        if self.game.type_short == "race" and self.mode in (0, 2):
            self.enabled = True
        else:
            self.enabled = False

    def handle_stats(self, stats):
        """Gets ZMQ stats."""
        if stats["TYPE"] == "PLAYER_RACECOMPLETE" and self.mode in (0, 2):
            self.enabled = True
            self.map_name = self.game.map.lower()
        elif stats["TYPE"] == "PLAYER_STATS":
            try:
                if int(stats["DATA"]["STEAM_ID"]) in self.plugins['race'].goto:
                    return
            except KeyError:
                self.logger.error("Race plugin is not loaded.")
                return
            except AttributeError:
                self.logger.warning("You are an old versions of race plugin.")
            self.update_pb(stats)

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

            time = self.plugins["race"].time_string(abs(record["time_diff"]))
            if record["rank"] == 1:
                time_diff = "^0[^2-{}^0]".format(time)
                self.msg("^7{} ^2just set a new ^3world record! {}{}".format(name, time_diff, strafe))
            else:
                time_diff = "^0[^1+{}^0]".format(time)
                self.msg(
                    "^7{} ^2set a new pb and is now rank ^3{} {}{}".format(name, record["rank"], time_diff, strafe))

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
            self.logger.error(e)
            self.msg("^2Error, connecting to qlrace.com")

    def push_db(self, payload):
        """Pushes record to redis list
        :param payload: record data
        """
        payload["date"] = str(datetime.utcnow())
        record = json.dumps(payload)
        self.db.lpush(RECORDS_KEY, record)

    def cmd_posttimes(self, player, msg, channel):
        """Posts times to QLRace.com if there's any in minqlx:race_records"""
        if self.db.llen(RECORDS_KEY) != 0:
            payload = json.loads(self.db.rpop(RECORDS_KEY))
            self.post_data(payload)
        else:
            channel.reply("No times in minqlx:race_records")

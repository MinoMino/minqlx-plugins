"""
Tracks race records and posts them to QLRace.com.
"""

import minqlx
import minqlx.database
import requests
import threading
import json
from datetime import datetime
import importlib
race = importlib.import_module("minqlx-plugins.race")


class track_race(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_hook("stats", self.handle_stats)
        self.set_cvar_once("qlx_raceKey", "api_key_goes_here")

        if self.game:
            self.map_name = self.game.map.lower()

    def handle_stats(self, stats):
        """Gets zmq stats"""
        if stats["TYPE"] == "PLAYER_RACECOMPLETE":
            self.map_name = self.game.map.lower()
        elif stats["TYPE"] == "PLAYER_STATS":
            threading.Thread(target=self.update_pb, args=(stats,)).start()

    def update_pb(self, stats):
        """Updates a players pb. If no knockback weapons were fired
        it sets mode to strafe.
        :param stats: ZMQ PLAYER_STATS
        """
        if self.game.type_short != "race":
            return

        time = stats["DATA"]["SCORE"]
        if time == -1 or time == 2147483647 or time == 0:
            return

        mode = self.get_cvar("qlx_raceMode", int)
        weapon_stats = stats["DATA"]["WEAPONS"]
        # if no knockback weapons fired, set mode to strafe
        if weapon_stats["PLASMA"]["S"] == 0 and weapon_stats["ROCKET"]["S"] == 0 and weapon_stats["PROXMINE"]["S"] == 0\
                and weapon_stats["GRENADE"]["S"] == 0 and weapon_stats["BFG"]["S"] == 0:
            mode += 1

        player_id = int(stats["DATA"]["STEAM_ID"])
        name = self.clean_text(stats["DATA"]["NAME"])
        match_guid = stats["DATA"]["MATCH_GUID"]
        payload = {"map": self.map_name, "mode": mode, "player_id": player_id, "name": name,
                   "time": time, "match_guid": match_guid}
        pb = self.post_data(payload)
        if pb:
            records = race.RaceRecords(self.map_name, mode)
            rank, time = records.pb(player_id)
            out = records.output(name, rank, time)
            out = out.replace(" ^2is rank ^3", " ^2is now rank ^3")
            self.msg(out)

    def post_data(self, payload):
        """Posts record to QLRace.com. If there's any records
        in redis list and qlrace.com is online it will recursively
        call itself until all the records have been posted.
        :param payload: record data
        """
        headers = {"X-Api-Key": self.get_cvar("qlx_raceKey")}
        try:
            r = requests.post("https://qlrace.com/api/new", data=payload, headers=headers)
            if r.status_code == 200:
                pb = True
            elif r.status_code == 304:
                pb = False
            elif r.status_code == 401:
                self.push_db(payload)
                self.msg("Invalid api key, ^2Your time has been saved locally")
                return
            if self.db.llen("minqlx:race_records") != 0:
                payload = json.loads(self.db.rpop("minqlx:race_records"))
                self.post_data(payload)
            return pb
        except:
            self.push_db(payload)
            self.msg("^2QLRace.com is down ^6:( ^2Your time has been saved locally")

    def push_db(self, payload):
        """Add record to redis list
        :param payload: record data
        """
        payload["date"] = str(datetime.utcnow())
        record = json.dumps(payload)
        self.db.lpush("minqlx:race_records", record)

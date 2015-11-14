"""
Tracks race records and posts them to QLRace.com.
"""

import minqlx
import requests
import threading
import sqlite3
from datetime import datetime
import importlib
race = importlib.import_module("minqlx-plugins.race")


class track_race(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("stats", self.handle_stats)
        self.server_mode = self.get_cvar("qlx_race_mode", int)
        self.key = self.get_cvar("qlx_race_key")

        if self.game:
            self.map_name = self.game.map.lower()

    def handle_stats(self, stats):
        """Gets zmq stats"""
        if stats["TYPE"] == "PLAYER_RACECOMPLETE":
            self.map_name = self.game.map.lower()
        elif stats["TYPE"] == "PLAYER_STATS":
            threading.Thread(target=self.update_pb, args=(stats,)).start()

    def update_pb(self, stats):
        """Updates a players pb. Checks if any knockback weapons was fired.
        :param stats:
        """
        time = stats["DATA"]["SCORE"]
        if time == -1 or time == 2147483647 or time == 0:
            return

        mode = self.server_mode
        weapon_stats = stats["DATA"]["WEAPONS"]
        # if no knockback weapons fired, set mode to strafe
        if weapon_stats["PLASMA"]["S"] == 0 and weapon_stats["ROCKET"]["S"] == 0 and weapon_stats["PROXMINE"]["S"] == 0\
                and weapon_stats["GRENADE"]["S"] == 0 and weapon_stats["BFG"]["S"] == 0:
            mode += 1

        player_id = int(stats["DATA"]["STEAM_ID"])
        name = self.clean_text(stats["DATA"]["NAME"])
        match_guid = stats["DATA"]["MATCH_GUID"]
        pb = self.post_data(self.map_name, mode, player_id, name, time, match_guid)
        if pb is None:
            self.msg("^2QLRace.com is down ^6:( ^2Your time has been saved locally and will be updated "
                     "when QLRace.com is back online")
        if pb:
            records = race.RaceRecords(self.map_name, mode)
            rank, time = records.pb(player_id)
            out = records.output(name, rank, time)
            out = out.replace(" ^2is rank ^3", " ^2is now rank ^3")
            self.msg(out)

    def post_data(self, map_name, mode, player_id, name, time, match_guid):
        """Posts record to QLRace.com.
        :param map_name: The name of the map
        :param mode: The mode(0-3)
        :param player_id: Steam ID
        :param name: The players name on steam
        :param time: The time they set
        :param match_guid: The guid of the match
        :return: True if a new pb, false otherwise
        """
        payload = {"map": map_name, "mode": mode, "player_id": player_id, "name": name,
                   "time": time, "match_guid": match_guid}
        headers = {"X-Api-Key": self.key}
        try:
            r = requests.post("https://qlrace.com/api/new", data=payload, headers=headers)
            if r.status_code == 200:
                return True
            else:
                return False
        except:
            self.insert_db(map_name, mode, player_id, name, time, match_guid)

    def insert_data(self, map_name, mode, player_id, name, time, match_guid):
        """Adds record to SQLite database if QLRace.com is down.
        :param map_name: The name of the map
        :param mode: The mode(0-3)
        :param player_id: Steam ID
        :param name: The players name on steam
        :param time: The time they set
        :param match_guid: The guid of the match
        """
        connection = sqlite3.connect("lost_stats.db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS stats "
                       "(mapname TEXT, mode INTEGER, player_id TEXT, name TEXT, "
                       "time INTEGER, match_guid TEXT, date DATETIME)")
        cursor.execute("INSERT INTO stats VALUES (?,?,?,?,?,?,?)",
                       (map_name, mode, player_id, name, time, match_guid, str(datetime.now())))
        connection.commit()
        connection.close()

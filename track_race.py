import minqlx
import requests
import threading
import sqlite3
from datetime import datetime
import sys
sys.path.append("minqlx-plugins")
import race


class track_race(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("stats", self.handle_stats)
        self.add_command("mapname", self.cmd_mapname)
        self.server_mode = self.get_cvar("qlx_race_mode", int)
        self.key = self.get_cvar("qlx_race_key")

        if self.game:
            self.mapname = self.game.map.lower()

    def cmd_mapname(self, player, msg, channel):
        channel.reply(self.mapname)

    def handle_stats(self, stats):
        if stats["TYPE"] == "PLAYER_RACECOMPLETE":
            self.mapname = self.game.map.lower()
        elif stats["TYPE"] == "PLAYER_STATS":
            threading.Thread(target=self.update_pb, args=(stats,)).start()

    def update_pb(self, stats):
        time = stats["DATA"]["SCORE"]
        if time == -1 or time == 2147483647:
            return

        mode = self.server_mode
        weapons = stats["DATA"]["WEAPONS"]
        # if no knockback weapons fired, set mode to strafe
        if weapons["PLASMA"]["S"] == 0 and weapons["ROCKET"]["S"] == 0 and weapons["PROXMINE"]["S"] == 0 and \
                        weapons["GRENADE"]["S"] == 0 and weapons["BFG"]["S"] == 0:
            mode += 1

        if not stats['DATA']['ABORTED']:
            self.mapname = self.game.map.lower()
        player_id = int(stats["DATA"]["STEAM_ID"])
        name = self.clean_text(stats["DATA"]["NAME"])
        match_guid = stats["DATA"]["MATCH_GUID"]
        pb = self.post_data(self.mapname, mode, player_id, name, time, match_guid)
        if pb is None:
            self.msg("^2QLRace.com is down ^6:( ^2Your time has been saved locally and will be updated "
                     "when QLRace.com is back online")
        if pb:
            records = race.RaceRecords(self.mapname, mode)
            rank, time = records.pb(player_id)
            out = records.output(name, rank, time)
            out = out.replace(" ^2is rank ^3", " ^2is now rank ^3")
            self.msg(out)

    def post_data(self, mapname, mode, player_id, name, time, match_guid):
        payload = {"map": mapname, "mode": mode, "player_id": player_id, "name": name,
                   "time": time, "match_guid": match_guid}
        headers = {"X-Api-Key": self.key}
        try:
            r = requests.post("https://qlrace.com/api/new", data=payload, headers=headers)
            if r.status_code == 200:
                return True
            else:
                return False
        except:
            self.insert_db(mapname, mode, player_id, name, time, match_guid)

    def insert_data(self, mapname, mode, player_id, name, time, match_guid):
        connection = sqlite3.connect("lost_stats.db")
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS stats "
                       "(mapname TEXT, mode INTEGER, player_id TEXT, name TEXT, "
                       "time INTEGER, match_guid TEXT, date DATETIME)")
        cursor.execute("INSERT INTO stats VALUES (?,?,?,?,?,?,?)",
                       (mapname, mode, player_id, name, time, match_guid, str(datetime.now())))
        connection.commit()
        connection.close()

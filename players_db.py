# players_db.py is a plugin for minqlx to:
# This will save permissions on the server to a text file so the file can be moved to another
#  server and loaded onto that database.
# It will also list the players who have permissions on the server, banned players, and silenced players
# created by BarelyMiSSeD on 11-10-15
#
"""
!getperms - This will get the permissions on the server and store it in the PERMS_FILE in the fs_homepath directory
!addperms - This will read the PERMS_FILE in the fs_homepath directory and put those perms into the database
!perms - This will list the players with permissions on the server
!bans - This will list the banned players on the server
!silenced - This will list the silenced players on the server
"""

import minqlx
import os
import time
import datetime


PLAYER_KEY = "minqlx:players:{}"
PLAYER_DB_KEY = "minqlx:players:{}:{}"
PERMS_FILE = "server_perms.txt"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DB_FILE = "server_db.txt"

VERSION = "1.9"


class players_db(minqlx.Plugin):
    def __init__(self):
        self.add_command("getperms", self.get_perms, 5)
        self.add_command("getdb", self.get_db, 5)
        self.add_command("addperms", self.add_perms, 5)
        self.add_command("savedb", self.add_db, 5)
        self.add_command(("perms", "listperms"), self.list_perms, 3)
        self.add_command(("bans", "banned", "listbans"), self.list_bans, 3)
        self.add_command(("silenced", "silences", "listsilenced"), self.list_silenced, 3)
        self.add_command("leavers", self.list_leavers, 3)
        self.add_command("warned", self.list_warned, 3)
        self.add_command("sid", self.sid_info, 3)

    def get_db_field(self, field):
        try:
            entry_type = self.db.type(field)
            if entry_type == "set":
                return entry_type, self.db.smembers(field)
            elif entry_type == "hash":
                return entry_type, self.db.hgetall(field)
            elif entry_type == "list":
                return entry_type, self.db.lrange(field, 0, -1)
            elif entry_type == "zset":
                # value = self.db.zrange(field, 0, -1)
                return None, None
            else:
                return entry_type, self.db.get(field)
        except Exception as e:
            # minqlx.console_print("^1players_db get_db_field {} Exception: {}".format(self.db.type(field), e))
            return None, None

    def get_db(self, player, msg, channel):
        self.save_db(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def save_db(self, player):
        player.tell("^1Starting DB retrieval and writing to {} (this may take a while).".format(DB_FILE))
        file = os.path.join(self.get_cvar("fs_homepath"), DB_FILE)
        try:
            h = open(file, "w")
        except Exception as e:
            minqlx.console_print("^1ERROR Opening bdm file: {}".format(e))
            return minqlx.RET_STOP_ALL
        db_entries = self.db.keys("minqlx:players:*")
        for entry in db_entries:
            try:
                entry_type, value = self.get_db_field(entry)
                if entry_type:
                    if entry_type == "set":
                        value_list = []
                        for item in value:
                            value_list.append(item)
                        h.write("{}//{}//{}\n".format(entry_type, entry, "//".join(value_list)))
                    elif entry_type == "list":
                        value_list = []
                        for item in value:
                            value_list.append(item)
                        h.write("{}//{}//{}\n".format(entry_type, entry, "//".join(value_list)))
                    elif entry_type == "hash":
                        value_list = []
                        for key, item in value.items():
                            value_list.append(key)
                            value_list.append(item)
                        h.write("{}//{}//{}\n".format(entry_type, entry, "//".join(value_list)))
                    else:
                        h.write("{}//{}//{}\n".format(entry_type, entry, value))
            except:
                continue

        ip_entries = self.db.keys("minqlx:ips:*")
        for entry in ip_entries:
            try:
                entry_type, value = self.get_db_field(entry)
                if entry_type:
                    value_list = []
                    for item in value:
                        value_list.append(item)
                    h.write("{}//{}//{}\n".format(entry_type, entry, "//".join(value_list)))
            except:
                continue

        try:
            value = self.db.smembers("minqlx:players")
            value_list = []
            for item in value:
                value_list.append(item)
            h.write("{}//{}//{}\n".format("set", "minqlx:players", "//".join(value_list)))
        except:
            pass

        try:
            value = self.db.smembers("minqlx:ips")
            value_list = []
            for item in value:
                value_list.append(item)
            h.write("{}//{}//{}\n".format("set", "minqlx:ips", "//".join(value_list)))
            h.close()
            player.tell("^1Finished saving player db to {}".format(DB_FILE))
        except:
            pass

    def add_db(self, player, msg, channel):
        self.enter_db(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def enter_db(self, player):
        player.tell("^1Starting DB entries from {} (this may take a while).".format(DB_FILE))
        file = os.path.join(self.get_cvar("fs_homepath"), DB_FILE)
        try:
            h = open(file, "r")
        except Exception as e:
            player.tell("^1ERROR Opening db file: {}".format(e))
            return minqlx.RET_STOP_ALL
        line = h.readline()
        while line:
            try:
                info = line.rstrip("\n").split("//")
                if info[0] == "string":
                    self.db.set(info[1], info[2])
                elif info[0] == "set":
                    for item in info[2:]:
                        if item not in self.db.smembers(info[1]):
                            self.db.sadd(info[1], item)
                elif info[0] == "list":
                    for item in info[2:]:
                        if item not in self.db.lrange(info[1], 0, -1):
                            self.db.lpush(info[1], item)
                elif info[0] == "hash":
                    db = self.db.pipeline()
                    key = ":".join(info[1].split(":")[0:4])
                    slot = self.db.zcard(key)
                    expires = info[info.index("expires") + 1]
                    db.zadd(key, datetime.datetime.strptime(expires, TIME_FORMAT).timestamp(), slot)
                    data = {"expires": expires, "reason": info[info.index("reason") + 1],
                            "issued": info[info.index("issued") + 1], "issued_by": info[info.index("issued_by") + 1]}
                    db.hmset("{}:{}".format(key, slot), data)
                    db.execute()
            except:
                pass
            line = h.readline()
        player.tell("^1Finished entering information to the database.")
        h.close()

    def get_perms(self, player, msg, channel):
        self.save_perms(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def save_perms(self, player):
        playerlist = self.db.keys(PLAYER_DB_KEY.format("*", "permission"))
        file = os.path.join(self.get_cvar("fs_homepath"), PERMS_FILE)
        try:
            h = open(file, "w")
        except Exception as e:
            player.tell("^1ERROR Opening perms file: {}".format(e))
            return minqlx.RET_STOP_ALL
        for player in playerlist:
            steam_id = player.split(":")[2]
            if len(str(steam_id)) == 17:
                h.write("{}:{}".format(steam_id, self.db.get(player)) + "\n")
        player.tell("^1Finished saving player permissions to {}".format(PERMS_FILE))
        h.close()

        return minqlx.RET_STOP_ALL

    def add_perms(self, player, msg, channel):
        self.enter_perms(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def enter_perms(self, player):
        file = os.path.join(self.get_cvar("fs_homepath"), PERMS_FILE)
        try:
            h = open(file, "r")
        except Exception as e:
            minqlx.console_print("^1ERROR Opening perms file: {}".format(e))
            return minqlx.RET_STOP_ALL
        for player in h.readlines():
            info = player.split(":")
            self.db.set(PLAYER_DB_KEY.format(info[0], "permission"), int(info[1]))
        player.tell("^1Finished entering player permissions to the database.")
        h.close()

        return minqlx.RET_STOP_ALL

    def player_name(self, steam_id):
        try:
            player = self.player(int(steam_id))
            if player is not None:
                name = player.name
            else:
                name = self.db.lindex(PLAYER_KEY.format(steam_id), 0)
        except minqlx.NonexistentPlayerError:
            name = self.db.lindex(PLAYER_KEY.format(steam_id), 0)
        except Exception as e:
            minqlx.console_print("^1players_db player_name Exception {}: {}".format(steam_id, [e]))
            name = self.db.lindex(PLAYER_KEY.format(steam_id), 0)
        return name

    def list_perms(self, player, msg, channel):
        self.show_perms(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_perms(self, asker):
        playerlist = self.db.keys(PLAYER_DB_KEY.format("*", "permission"))
        perms_list1 = []
        perms_list2 = []
        perms_list3 = []
        perms_list4 = []
        perms_list5 = []
        for player in playerlist:
            steam_id = player.split(":")[2]
            if len(str(steam_id)) == 17:
                perms = int(self.db.get(player))
                if perms == 1:
                    perms_list1.append("{0} ^7({1}): ^{2}{2}".format(self.player_name(steam_id), steam_id, perms))
                elif perms == 2:
                    perms_list2.append("{0} ^7({1}): ^{2}{2}".format(self.player_name(steam_id), steam_id, perms))
                elif perms == 3:
                    perms_list3.append("{0} ^7({1}): ^{2}{2}".format(self.player_name(steam_id), steam_id, perms))
                elif perms == 4:
                    perms_list4.append("{0} ^7({1}): ^{2}{2}".format(self.player_name(steam_id), steam_id, perms))
                elif perms == 5:
                    perms_list5.append("{0} ^7({1}): ^{2}{2}".format(self.player_name(steam_id), steam_id, perms))
        owner = minqlx.owner()
        asker.tell("^1Server Owner^7: {} ^7({})".format(self.player_name(owner), owner))
        if len(perms_list5) > 0:
            asker.tell("^5Level 5 Permissions^7:")
            for p in perms_list5:
                asker.tell(p)
        if len(perms_list4) > 0:
            asker.tell("^4Level 4 Permissions^7:")
            for p in perms_list4:
                asker.tell(p)
        if len(perms_list3) > 0:
            asker.tell("^3Level 3 Permissions^7:")
            for p in perms_list3:
                asker.tell(p)
        if len(perms_list2) > 0:
            asker.tell("^2Level 2 Permissions^7:")
            for p in perms_list2:
                asker.tell(p)
        if len(perms_list1) > 0:
            asker.tell("^1Level 1 Permissions^7:")
            for p in perms_list1:
                asker.tell(p)

        return

    def list_bans(self, player, msg, channel):
        self.show_bans(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_bans(self, asker):
        playerlist = self.db.keys(PLAYER_DB_KEY.format("*", "bans"))
        bans_list = []
        for player in playerlist:
            steam_id = player.split(":")[2]
            banned = self.db.zrangebyscore(PLAYER_DB_KEY.format(steam_id, "bans"), time.time(), "+inf", withscores=True)
            if banned:
                longest_ban = self.db.hgetall(PLAYER_DB_KEY.format(steam_id, "bans") + ":{}".format(banned[-1][0]))
                expires = datetime.datetime.strptime(longest_ban["expires"], TIME_FORMAT)
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    bans_list.append("{} ^7({}): ^6Expires: ^7{} ^5Reason: ^7{} ^2Issued By: ^7{}"
                                     .format(self.player_name(steam_id),
                                             steam_id, datetime.datetime.strptime(longest_ban["expires"], TIME_FORMAT),
                                             longest_ban["reason"] if longest_ban["reason"] else "No Saved Reason",
                                             self.player_name(longest_ban["issued_by"])))
        if len(bans_list) > 0:
            asker.tell("^5Bans^7:")
            for ban in bans_list:
                asker.tell(ban)
        else:
            asker.tell("^5No Active bans found.")
        return

    def list_silenced(self, player, msg, channel):
        self.show_silenced(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_silenced(self, asker):
        playerlist = self.db.keys(PLAYER_DB_KEY.format("*", "silences"))
        message = []
        for player in playerlist:
            steam_id = player.split(":")[2]
            silenced = self.db.zrangebyscore(PLAYER_DB_KEY.format(steam_id, "silences"), time.time(), "+inf",
                                             withscores=True)
            if silenced:
                silence_time = self.db.hgetall(PLAYER_DB_KEY.format(steam_id, "silences") + ":{}"
                                               .format(silenced[-1][0]))
                expires = datetime.datetime.strptime(silence_time["expires"], TIME_FORMAT)
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    message.append("{} ^7({}): ^6Expires: ^7{} ^5Reason: ^7{} ^2Issued By: ^7{}"
                                   .format(self.player_name(steam_id),
                                           steam_id, datetime.datetime.strptime(silence_time["expires"], TIME_FORMAT),
                                           silence_time["reason"] if silence_time["reason"] else "No Saved Reason",
                                           self.player_name(silence_time["issued_by"])))
        if len(message) > 0:
            asker.tell("^5Silenced^7:")
            for silence in message:
                asker.tell(silence)
        else:
            asker.tell("^5No Active silences found.")

        return

    def list_leavers(self, player, msg, channel):
        self.show_leavers(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_leavers(self, asker):
        if not self.get_cvar("qlx_leaverBan", bool):
            asker.tell("^5Leaver bans are not enabled on this server.")
        else:
            playerlist = self.db.keys(PLAYER_KEY.format("*"))
            message = []
            for player in playerlist:
                steam_id = player.split(":")[2]
                try:
                    completed = self.db[PLAYER_KEY.format(steam_id) + ":games_completed"]
                    left = self.db[PLAYER_KEY.format(steam_id) + ":games_left"]
                except KeyError:
                    continue
                completed = int(completed)
                left = int(left)
                min_games_completed = self.get_cvar("qlx_leaverBanMinimumGames", int)
                ban_threshold = self.get_cvar("qlx_leaverBanThreshold", float)
                total = completed + left
                if not total:
                    continue
                elif total < min_games_completed:
                    continue
                else:
                    ratio = completed / total
                if ratio <= ban_threshold and total >= min_games_completed:
                    message.append("{} ^7({}): ^6Games Played: ^7{} ^5Left: ^7{} ^4Percent: ^7{}"
                                   .format(self.player_name(steam_id),
                                           steam_id, total, left, ratio))

            if len(message) > 0:
                asker.tell("^5Leaver Banned^7:")
                for leaver in message:
                    asker.tell(leaver)
            else:
                asker.tell("^5No Leaver Bans found.")
        return

    def list_warned(self, player, msg, channel):
        self.show_warned(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_warned(self, asker):
        if not self.get_cvar("qlx_leaverBan", bool):
            asker.tell("^5Leaver bans are not enabled on this server.")
        else:
            playerlist = self.db.keys(PLAYER_KEY.format("*"))
            message = []
            for player in playerlist:
                steam_id = player.split(":")[2]
                try:
                    completed = self.db[PLAYER_KEY.format(steam_id) + ":games_completed"]
                    left = self.db[PLAYER_KEY.format(steam_id) + ":games_left"]
                except KeyError:
                    continue
                completed = int(completed)
                left = int(left)
                min_games_completed = self.get_cvar("qlx_leaverBanMinimumGames", int)
                warn_threshold = self.get_cvar("qlx_leaverBanWarnThreshold", float)
                ban_threshold = self.get_cvar("qlx_leaverBanThreshold", float)
                total = completed + left
                if not total:
                    continue
                elif total < min_games_completed:
                    continue
                else:
                    ratio = completed / total
                if ratio <= warn_threshold and (ratio > ban_threshold or total < min_games_completed):
                    message.append("{} ^7({}): ^6Games Played: ^7{} ^5Left: ^7{} ^4Percent: ^7{}"
                                   .format(self.player_name(steam_id),
                                           steam_id, total, left, ratio))

            if len(message) > 0:
                asker.tell("^5Leaver Warned^7:")
                for leaver in message:
                    asker.tell(leaver)
            else:
                asker.tell("^5No Leaver Warned found.")
        return

    def sid_info(self, player, msg, channel):
        self.show_sid_info(player, msg)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def show_sid_info(self, asker, msg):
        try:
            pid = int(msg[1])
            if 0 <= pid <= 63:
                sid = str(self.player(pid).steam_id)
            else:
                sid = str(pid)
            if len(sid) != 17 or sid[0] == "9":
                asker.tell("^1Please enter a valid player ID or Steam ID.")
                return
        except TypeError:
            asker.tell("^1Include a Steam ID or a connected Player ID.")
            return
        except minqlx.NonexistentPlayerError:
            asker.tell("^1That Player ID is not a connected player.")
            return
        except Exception as e:
            minqlx.console_print("^1players_db show_sid_info Exception: {}".format([e]))
            return
        names = list(self.db.lrange(PLAYER_KEY.format(sid), 0, -1))
        count = 1
        shared_by = {}
        if len(names):
            asker.tell("^6These are the names found for steam id ^7{}^6:".format(sid))
            for name in names:
                asker.tell("^1Name {}^7: {}".format(count, name))
                count += 1
        else:
            asker.tell("^6No information for ^7{} ^6was found.".format(sid))
            return
        ip_list = self.db.smembers(PLAYER_KEY.format(sid) + ":ips")
        count = 0
        ip_line = []
        for ip in ip_list:
            shared = self.db.smembers("minqlx:ips:{}".format(ip))
            if len(shared) > 1:
                shared_by[ip] = shared
            if count == 0 or count % 5:
                ip_line.append(ip)
            else:
                asker.tell("^1IPs: ^2{}".format("^1, ^2".join(ip_line)))
                ip_line = [ip]
            count += 1
        if len(ip_line):
            asker.tell("^1IPs: ^2{}".format("^1, ^2".join(ip_line)))

        if len(shared_by):
            for key, value in shared_by.items():
                ip_list = list(value)
                asker.tell("^1IP ^7{} ^1used by steam IDs^7: ^2{}".format(key, "^1, ^2".join(ip_list[0:3])))
                del ip_list[0:3]
                while len(ip_list):
                    asker.tell("^2{}".format("^1, ^2".join(ip_list[0:5])))
                    del ip_list[0:5]

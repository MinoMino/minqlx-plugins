# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Race plugin for minqlx. Adds commands such as !pb, !top, !all etc
"""

import minqlx
import requests
import threading
import random

params = [{}, {"weapons": "false"}, {"factory": "classic", "weapons": "true"},
          {"factory": "classic", "weapons": "false"}]


class race(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("map", self.handle_map)
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("server_command", self.handle_server_command)
        self.add_command(("slap", "slay"), self.cmd_disabled, priority=minqlx.PRI_HIGH)
        self.add_command("updatemaps", self.cmd_updatemaps)
        self.add_command(("pb", "me", "spb", "sme", "p", "sp"), self.cmd_pb, usage="[map]")
        self.add_command(("rank", "srank", "r", "sr"), self.cmd_rank, usage="[rank] [map]")
        self.add_command(("top", "stop", "t", "st"), self.cmd_top, usage="[amount] [map]")
        self.add_command(("all", "sall", "a", "sa"), self.cmd_all, usage="[map]")
        self.add_command(("ranktime", "sranktime", "rt", "srt"), self.cmd_ranktime, usage="<time> [map]")
        self.add_command(("avg", "savg"), self.cmd_avg, usage="[id]")
        self.add_command("random", self.cmd_random)
        self.add_command(("help", "cmds", "commands"), self.cmd_commands, priority=minqlx.PRI_HIGH)

        # 0 = Turbo/PQL, 2 = Classic/VQL
        self.set_cvar_once("qlx_raceMode", "0")
        self.set_cvar_once("qlx_raceBrand", "QLRace.com")

        self.maps = []
        threading.Thread(target=self.get_maps).start()

    def cmd_disabled(self, player, msg, channel):
        """This is to disable !slap and !slay"""
        player.tell("^6{} ^7is disabled".format(msg[0]))
        return minqlx.RET_STOP_ALL

    def handle_vote_called(self, player, vote, args):
        """Cancels the vote when map called is a duplicate."""
        if vote.lower() == "map":
            disabled_maps = ["q3w2", "q3w3", "q3w5", "q3w7", "q3wcp1", "q3wcp14", "q3wcp17", "q3wcp18",
                             "q3wcp22", "q3wcp23", "q3wcp5", "q3wcp9", "q3wxs1", "q3wxs2"]
            map_name = args.lower().split()[0]
            if map_name in disabled_maps:
                player.tell("^3{} ^2is disabled(duplicate).".format(map_name))
                return minqlx.RET_STOP_ALL

    def handle_new_game(self):
        """Brands server."""
        map_name = self.game.map.lower()
        brand_map = "{} - {}".format(self.get_cvar("qlx_raceBrand"), map_name)
        minqlx.set_configstring(3, brand_map)

    def handle_map(self, map_name, factory):
        """Brands server and updates list of race maps on map change.
        Also sets starting weapons to only mg and gauntlet if strafe map."""
        brand_map = "{} - {}".format(self.get_cvar("qlx_raceBrand"), map_name.lower())
        minqlx.set_configstring(3, brand_map)

        strafe_maps = ["df_bardoklick", "df_bardoklickrevamped", "df_lickagain", "df_lickape", "df_lickcells",
                       "df_lickcells2", "df_lickcorp", "df_lickdead", "df_lickdecease", "df_lickdirt", "df_lickevil",
                       "df_lickfast", "df_lickfudge", "df_lickhossa", "df_lickhq", "df_lickhuar", "df_lickhuar2",
                       "df_lickhuarstyle", "df_lickice", "df_lickmore", "df_lickmore2", "df_lickpads", "df_lickrevived",
                       "df_lickrevived2", "df_licksewage", "df_licksux", "df_licktards", "df_licktunnel",
                       "df_palmslane", "df_enz12", "df_ghostcheerslick", "df_ghostslickthis", "df_liquidazot",
                       "df_pornstarlambaslick", "df_ghostcheerextended", "cpm_1", "cpm_2", "cpm_3", "cpm_4", "cpm_5",
                       "cpm_6", "cpm_7", "cpm_8", "cpm_10", "vanilla_02", "vanilla_03", "vanilla_04", "vanilla_05",
                       "vanilla_06", "vanilla_07", "vanilla_08", "vanilla_08", "vanilla_10", "df_o3jvelocity"]
        if map_name.lower() in strafe_maps:
            minqlx.set_cvar("g_startingWeapons", "3")
        elif "strafe" not in factory:
            minqlx.set_cvar("g_startingWeapons", "147")
        threading.Thread(target=self.get_maps).start()

    def handle_server_command(self, player, cmd):
        """Stops server printing haste message."""
        if "^3 got the Haste!^7" in cmd:
            return minqlx.RET_STOP_EVENT

    def cmd_updatemaps(self, player, msg, channel):
        """Updates list of race maps"""
        threading.Thread(target=self.get_maps).start()

    def cmd_pb(self, player, msg, channel):
        """Outputs the player's personal best time for a map."""
        if len(msg) == 1:
            map_prefix = self.game.map.lower()
        elif len(msg) == 2:
            map_prefix = msg[1]
        else:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        threading.Thread(target=self.pb, args=(map_name, weapons, player, channel)).start()

    def pb(self, map_name, weapons, player, channel):
        records = self.get_records(map_name, weapons)
        rank, time = records.pb(player.steam_id)
        if not weapons:
            map_name += "^2(strafe)"
        if rank:
            channel.reply(records.output(player, rank, time))
        else:
            channel.reply("^2No time found for ^7{} ^2on ^3{}".format(player, map_name))

    def cmd_rank(self, player, msg, channel):
        """Outputs the x rank time for a map. Default rank if none is given is 1."""
        if len(msg) == 1:
            rank = 1
            map_prefix = self.game.map.lower()
        elif len(msg) == 2:
            if msg[1].isdigit():
                rank = int(msg[1])
                map_prefix = self.game.map.lower()
            else:
                rank = 1
                map_prefix = msg[1]
        elif len(msg) == 3:
            rank = int(msg[1])
            map_prefix = msg[2]
        else:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        threading.Thread(target=self.rank, args=(map_name, weapons, rank, channel)).start()

    def rank(self, map_name, weapons, rank, channel):
        records = self.get_records(map_name, weapons)
        name, actual_rank, time = records.rank(rank)
        if not weapons:
            map_name += "^2(strafe)"
        if time:
            if actual_rank != rank:
                tied = True
            else:
                tied = False
            channel.reply(records.output(name, rank, time, tied))
        else:
            channel.reply("^2No rank ^3{} ^2time found on ^3{}".format(rank, map_name))

    def cmd_top(self, player, msg, channel):
        """Outputs top x amount of times for a map. Default amount if none is given is 3.
        Maximum amount is 20."""
        if len(msg) == 1:
            amount = 3
            map_prefix = self.game.map
        elif len(msg) == 2:
            if msg[1].isdigit():
                amount = int(msg[1])
                map_prefix = self.game.map
            else:
                amount = 3
                map_prefix = msg[1]
        elif len(msg) == 3:
            amount = int(msg[1])
            map_prefix = msg[2]
        else:
            return minqlx.RET_USAGE
        if amount > 20:
            channel.reply("^2Please use value <=20")
            return

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        threading.Thread(target=self.top, args=(map_name, weapons, amount, channel)).start()

    def top(self, map_name, weapons, amount, channel):
        records = self.get_records(map_name, weapons)
        if not weapons:
            map_name += "^2(strafe)"
        if not records.records:
            channel.reply("^2No times were found on ^3{}".format(map_name))
            return

        if amount > len(records.records):
            amount = len(records.records)
        times = []
        for i in range(amount):
            try:
                record = records.records[i]
                times.append(" ^3{}. ^4{} ^2{}".format(record['rank'], record['name'], time_string(record['time'])))
            except IndexError:
                break

        self.output_times(map_name, times, channel)

    def cmd_all(self, player, msg, channel):
        """Outputs the ranks and times of everyone on the server for a map."""
        if len(msg) == 1:
            map_prefix = self.game.map
        elif len(msg) == 2:
            map_prefix = msg[1]
        else:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        threading.Thread(target=self.all, args=(map_name, weapons, channel)).start()

    def all(self, map_name, weapons, channel):
        records = self.get_records(map_name, weapons)
        times = {}
        for p in self.players():
            rank, time = records.pb(p.steam_id)
            if rank:
                times[rank] = "^7{} ^2{}".format(p, time_string(time))

        if not weapons:
            map_name += "^2(strafe)"
        if times:
            times_list = []
            for rank, time in sorted(times.items()):
                times_list.append(" ^3{}. {}".format(rank, time))
            self.output_times(map_name, times_list, channel)
        else:
            channel.reply("^2No times were found for anyone on ^3{} ^2:(".format(map_name))

    def cmd_ranktime(self, player, msg, channel):
        """Outputs which rank a time would be."""
        if len(msg) == 1 and player.score != 2147483647:
            time = player.score
            map_prefix = self.game.map
        elif len(msg) == 2:
            time = time_ms(msg[1])
            map_prefix = self.game.map
        elif len(msg) == 3:
            time = time_ms(msg[1])
            map_prefix = msg[2]
        else:
            channel.reply("^7Usage: ^6{0} <time> [map] ^7or just ^6{0} ^7if you have set a time".format(msg[0]))
            return

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        self.ranktime(map_name, weapons, time, channel)

    def ranktime(self, map_name, weapons, time, channel):
        records = self.get_records(map_name, weapons)
        rank = records.rank_from_time(time)
        last_rank = records.last_rank + 1
        if not rank:
            rank = last_rank

        if not weapons:
            map_name += "^2(strafe)"

        channel.reply("^3{} ^2would be rank ^3{} ^2of ^3{} ^2on ^3{}".format(time_string(time), rank,
                                                                             last_rank, map_name))

    def cmd_avg(self, player, msg, channel):
        """Outputs a player average rank."""
        if len(msg) == 2:
            try:
                i = int(msg[1])
                target_player = self.player(i)
                if not (0 <= i < 64) or not target_player:
                    raise ValueError
                player = target_player
            except ValueError:
                player.tell("Invalid ID.")
                return minqlx.RET_STOP_EVENT
        elif len(msg) > 2:
            return minqlx.RET_USAGE

        if "s" in msg[0].lower():
            mode = self.get_cvar("qlx_raceMode", int) + 1
            strafe = "strafe "
        else:
            mode = self.get_cvar("qlx_raceMode", int)
            strafe = ""

        threading.Thread(target=self.avg, args=(player, mode, strafe, channel)).start()

    def avg(self, player, mode, strafe, channel):
        data = requests.get("https://qlrace.com/api/player/{}".format(player.steam_id), params=params[mode]).json()
        name = data["name"]
        total_maps = len(data["records"])
        if name is not None and total_maps > 0:
            avg = data["average"]
            medals = data["medals"]
            channel.reply("^7{} ^2average {}rank: ^3{:.2f}^2({} maps) ^71st: ^3{} ^72nd: ^3{} ^73rd: ^3{}"
                          .format(player, strafe, avg, total_maps, medals[0], medals[1], medals[2]))
        else:
            channel.reply("^7{} ^2has no {}records :(".format(player, strafe))

    def cmd_random(self, player, msg, channel):
        """Callvotes a random map."""
        map_name = random.choice(self.maps)
        minqlx.client_command(player.id, "cv map {}".format(map_name))

    def cmd_commands(self, player, msg, channel):
        """Outputs list of race commands."""
        channel.reply(
            "Commands: ^3!(s)pb !(s)rank !(s)top !(s)all !(s)ranktime !(s)avg !random")
        return minqlx.RET_STOP_ALL

    def output_times(self, map_name, times, channel):
        """Outputs times to the channel. Will split lines so that each
        record is not on 2 different lines.
        :param map_name: The map name
        :param times: List of map times
        :param channel: The channel to reply to
        :return:
        """
        output = ["^2{}:".format(map_name)]
        for time in times:
            if len(output[len(output) - 1]) + len(time) < 100:
                output[len(output) - 1] += time
            else:
                output.append(time)

        for out in output:
            channel.reply(out.lstrip())

    def get_maps(self):
        """Gets the list of race maps from QLRace.com,
        adds current map to the list if it isn't in the list"""
        self.maps = requests.get("https://qlrace.com/api/maps").json()["maps"]
        current_map = self.game.map.lower()
        if current_map not in self.maps:
            self.maps.append(current_map)

    def map_prefix(self, map_prefix):
        """Returns the first map which matches the prefix.
        :param map_prefix: The prefix of a map
        """
        if map_prefix in self.maps:
            return map_prefix

        return next((x for x in self.maps if x.startswith(map_prefix)), None)

    def get_map_name_weapons(self, map_prefix, command, channel):
        """Get map name and weapons boolean.
        :param map_prefix: The prefix of a map
        :param command: The command the player entered
        :param channel: The channel to reply to. Usually chat.
        :return: The map name and weapons boolean.
        """
        map_name = self.map_prefix(map_prefix)
        if not map_name:
            channel.reply("^2No map found for ^3{}. ^2If this is wrong, ^6!updatemaps".format(map_prefix))
            return minqlx.RET_STOP_EVENT
        weapons = False if "s" in command.lower() else True
        return map_name, weapons

    def get_records(self, map_name, weapons):
        """Gets race records
        :param map_name: The map name
        :param weapons: Weapons boolean
        :return: race records
        """
        if weapons:
            mode = self.get_cvar("qlx_raceMode", int)
            return RaceRecords(map_name, mode)
        else:
            mode = self.get_cvar("qlx_raceMode", int) + 1
            return RaceRecords(map_name, mode)


class RaceRecords:
    """Race records object. Gets records using QLRace.com API"""

    def __init__(self, map_name, mode):
        self.map_name = map_name.lower()
        self.mode = mode
        self.weapons = True if mode % 2 == 0 else False
        self.records = self.get_data()
        self.last_rank = len(self.records)
        if self.records:
            self.first_time = self.records[0]["time"]

    def rank(self, rank):
        """Returns name, actual rank and time of the rank.
        :param rank: The rank of the time which will be returned
        """
        try:
            record = self.records[rank - 1]
        except IndexError:
            return None, None, None

        name = record["name"]
        actual_rank = record["rank"]
        time = record["time"]
        return name, actual_rank, time

    def rank_from_time(self, time):
        """Returns the rank the time would be.
        :param time: The time in milliseconds which will be ranked
        """
        for i, record in enumerate(self.records):
            if time <= record["time"]:
                return i + 1

    def pb(self, player_id):
        """Returns a players rank and time.
        :param player_id: The player id
        """
        for record in self.records:
            if player_id == record["player_id"]:
                time = record["time"]
                rank = record["rank"]
                return rank, time
        return None, None

    def output(self, name, rank, time, tied=False):
        """Returns record output with time difference to world record.
        :param name: Name of the player
        :param rank: Rank of the record
        :param time: Time of the record
        :param tied: Whether the record is tied with anyone else
        """
        if rank != 1:
            time_diff = str(time - self.first_time)
            time_diff = time_diff.zfill(3)
            time_diff = "^0[^1+" + time_string(time_diff) + "^0]"
        else:
            time_diff = ""
        time = time_string(time)
        strafe = "^2(strafe)" if not self.weapons else ""
        tied = "tied " if tied else ""
        return "^7{} ^2is {}rank ^3{} ^2of ^3{} ^2with ^3{}{} ^2on ^3{}{}" \
            .format(name, tied, rank, self.last_rank, time, time_diff, self.map_name, strafe)

    def get_data(self):
        """Gets the records for the map and mode from qlrace.com."""
        data = requests.get("https://qlrace.com/api/map/{}".format(self.map_name), params=params[self.mode]).json()
        return data['records']


def time_ms(time_string):
    """Returns time in milliseconds.
    :param time_string: Time as a string, examples 2.300, 1:12.383
    """
    minutes, seconds = (["0"] + time_string.split(":"))[-2:]
    return int(60000 * int(minutes) + round(1000 * float(seconds)))


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
    time //= 1000
    m, s = divmod(time, 60)
    s = str(s).zfill(2)
    return "{}:{}.{}".format(m, s, ms)

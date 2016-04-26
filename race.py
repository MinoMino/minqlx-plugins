# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Race plugin for minqlx. Adds commands such as !pb, !top, !all etc
"""

import minqlx
import random
import re
import requests

PARAMS = ({}, {"weapons": "false"}, {"physics": "classic"}, {"physics": "classic", "weapons": "false"})
OLDTOP_URL = "https://cdn.rawgit.com/QLRace/oldtop/master/oldtop/"

GOTO_DISABLED = ("nqdl", "bounce", "df_coldrun")
HASTE = ("df_handbreaker4", "handbreaker4_long", "handbreaker", "df_piyofunjumps", "funjumpsmap", "df_luna",
         "df_nodown", "df_etleague", "df_extremepkr", "labyrinth", "airmaxjumps", "sarcasmjump", "criclejump",
         "cursed_temple", "skacharohuth", "randommap", "just_jump_3", "criclejump", "eatme")

GAUNTLET_ONLY = ("k4n", "ndql")
NO_WEAPONS = ("df_bardoklick", "df_bardoklickrevamped", "df_lickagain", "df_lickape", "df_lickcells", "df_lickcells2",
              "df_lickcorp", "df_lickdead", "df_lickdecease", "df_lickdirt", "df_lickevil", "df_lickfast",
              "df_lickfudge", "df_lickhossa", "df_lickhq", "df_lickhuar", "df_lickhuar2", "df_lickhuarstyle",
              "df_lickice", "df_lickmore", "df_lickmore2", "df_lickpads", "df_lickrevived", "df_lickrevived2",
              "df_licksux", "df_licktards", "df_licktunnel", "df_palmslane", "df_enz12", "df_ghostcheerslick",
              "df_ghostslickthis", "df_liquidazot", "df_pornstarlambaslick", "df_ghostcheerextended", "cpm_1", "cpm_2",
              "cpm_3", "cpm_4", "cpm_5", "cpm_6", "cpm_7", "cpm_8", "cpm_10", "vanilla_02", "vanilla_03", "vanilla_04",
              "vanilla_05", "vanilla_06", "vanilla_07", "vanilla_08", "vanilla_08", "vanilla_10", "df_o3jvelocity",
              "df_qsnrun", "df_handbreaker4", "df_piyofunjumps", "df_verihard", "df_luna", "df_etleague", "df_nodown",
              "df_extremepkr", "walkathon", "purpletorture", "sodomia", "r7_pyramid", "yellowtorture", "weirdwild",
              "hangtime", "poptart", "blockworld")
PLASMA_ONLY = ("think1", "xproject", "plasmax")
GRENADE_ONLY = ("grenadorade")

_RE_POWERUPS = re.compile(r'print ".+\^3 got the (Haste|Battle Suit|Quad Damage)!\^7\n"')


class race(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("map", self.handle_map)
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("server_command", self.handle_server_command)
        self.add_hook("stats", self.handle_stats)
        self.add_hook("player_spawn", self.handle_player_spawn)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_command(("slap", "slay"), self.cmd_disabled, priority=minqlx.PRI_HIGH)
        self.add_command("updatemaps", self.cmd_updatemaps)
        self.add_command(("pb", "me", "spb", "sme", "p", "sp"), self.cmd_pb, usage="[map]")
        self.add_command(("rank", "srank", "r", "sr"), self.cmd_rank, usage="[rank] [map]")
        self.add_command(("top", "stop", "t", "st", "oldtop", "oldstop", "ot", "ost"), self.cmd_top,
                         usage="[amount] [map]")
        self.add_command(("all", "sall", "a", "sa"), self.cmd_all, usage="[map]")
        self.add_command(("ranktime", "sranktime", "rt", "srt"), self.cmd_ranktime, usage="<time> [map]")
        self.add_command(("avg", "savg"), self.cmd_avg, usage="[id]")
        self.add_command("randommap", self.cmd_random_map)
        self.add_command("recent", self.cmd_recent, usage="[amount]")
        self.add_command(("goto", "tp"), self.cmd_goto, usage="<id>")
        self.add_command(("commands", "cmds", "help"), self.cmd_commands, priority=minqlx.PRI_HIGH)

        self.set_cvar_once("qlx_raceMode", "0")  # 0 = Turbo/PQL, 2 = Classic/VQL
        self.set_cvar_once("qlx_raceBrand", "QLRace.com")

        # dict of players which have used !goto. {steam_id: score}
        self.goto = {}

        self.maps = []
        self.old_maps = []
        self.get_maps()

    def handle_new_game(self):
        """Brands map title on new game."""
        map_name = self.game.map.lower()
        self.brand_map(map_name)

    def handle_map(self, map_name, factory):
        """Brands map title and updates list of race maps on map change.
        Also sets correct starting weapons for the map.
        """
        map_name = map_name.lower()
        self.brand_map(map_name)

        if factory in ("qlrace_turbo", "qlrace_classic"):
            if map_name in NO_WEAPONS:
                self.set_cvar("g_startingWeapons", "3")
                if map_name == "poptart":
                    self.set_cvar("g_infiniteAmmo", "1")
                else:
                    self.set_cvar("g_infiniteAmmo", "0")
            elif map_name in GRENADE_ONLY:
                self.set_cvar("g_startingWeapons", "9")
                self.set_cvar("g_infiniteAmmo", "1")
            elif map_name in GAUNTLET_ONLY:
                self.set_cvar("g_startingWeapons", "1")
                self.set_cvar("g_infiniteAmmo", "0")
            elif map_name in PLASMA_ONLY:
                self.set_cvar("g_startingWeapons", "131")
                self.set_cvar("g_infiniteAmmo", "1")
            elif map_name == "rocketx":
                self.set_cvar("g_startingWeapons", "17")
                self.set_cvar("g_infiniteAmmo", "1")
            elif map_name == "bfgx":
                self.set_cvar("g_startingWeapons", "257")
                self.set_cvar("g_infiniteAmmo", "1")
            else:
                self.set_cvar("g_startingWeapons", "147")
                self.set_cvar("g_infiniteAmmo", "1")

            if map_name == "hangtime":
                self.set_cvar("g_startingAmmo_mg", "1")
            else:
                self.set_cvar("g_startingAmmo_mg", "100")

            if self.get_cvar("qlx_raceMode", int) == 0:
                if map_name == "k4n":
                    self.set_cvar("g_velocity_gl", "700")
                else:
                    self.set_cvar("g_velocity_gl", "800")

            if map_name == "walkathon":
                self.set_cvar("g_respawn_delay_min", "1000")
                self.set_cvar("g_respawn_delay_max", "1000")
            else:
                self.set_cvar("g_respawn_delay_min", "10")
                self.set_cvar("g_respawn_delay_max", "10")

        self.get_maps()

    def handle_vote_called(self, player, vote, args):
        """Cancels the vote when a duplicated map is voted for."""
        if vote.lower() == "map":
            if len(args) > 0:
                disabled_maps = ("q3w2", "q3w3", "q3w5", "q3w7", "q3wcp1", "q3wcp14", "q3wcp17", "q3wcp18",
                                 "q3wcp22", "q3wcp23", "q3wcp5", "q3wcp9", "q3wxs1", "q3wxs2", "wintersedge")
                map_name = args.split()[0]
                if map_name.lower() in disabled_maps:
                    player.tell("^3{} ^2is disabled(duplicate map).".format(map_name))
                    return minqlx.RET_STOP_ALL

    def handle_server_command(self, player, cmd):
        """Stops server printing powerup messages."""
        if _RE_POWERUPS.fullmatch(cmd):
            return minqlx.RET_STOP_EVENT

    def handle_stats(self, stats):
        """Resets a player's score if they used !goto."""
        if stats["TYPE"] == "PLAYER_RACECOMPLETE":
            steam_id = int(stats["DATA"]["STEAM_ID"])
            if steam_id in self.goto:
                player = self.player(steam_id)
                player.score = self.goto[steam_id]
                player.tell("^6Your time does not count because you used !goto.")

    def handle_player_spawn(self, player):
        """Removes player from goto dict when they spawn."""
        try:
            del self.goto[player.steam_id]
        except KeyError:
            return

    def handle_player_disconnect(self, player, reason):
        """Removes player from goto dict when they disconnect"""
        try:
            del self.goto[player.steam_id]
        except KeyError:
            return

    def cmd_disabled(self, player, msg, channel):
        """Disables !slap and !slay."""
        player.tell("^6{} ^7is disabled".format(msg[0]))
        return minqlx.RET_STOP_ALL

    def cmd_updatemaps(self, player, msg, channel):
        """Updates list of race maps"""
        self.get_maps()

    def cmd_pb(self, player, msg, channel):
        """Outputs the player's personal best time for a map."""
        if len(msg) == 1:
            map_prefix = self.game.map.lower()
        elif len(msg) == 2:
            map_prefix = msg[1]
        else:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        self.pb(map_name, weapons, player, channel)

    @minqlx.thread
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
        """Outputs the x rank time for a map. Default rank
        if none is given is 1.
        """
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
        self.rank(map_name, weapons, rank, channel)

    @minqlx.thread
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
        """Outputs top x amount of times for a map. Default amount
        if none is given is 3. Maximum amount is 20.
        """
        amount = 3
        map_prefix = self.game.map
        if len(msg) == 2:
            try:
                amount = int(msg[1])
            except ValueError:
                map_prefix = msg[1]
        elif len(msg) == 3:
            try:
                amount = int(msg[1])
            except ValueError:
                return minqlx.RET_USAGE
            map_prefix = msg[2]
        elif len(msg) > 3:
            return minqlx.RET_USAGE

        if amount > 20:
            channel.reply("^2Please use value <=20")
            return

        if "!o" in msg[0] or msg[0].startswith("o"):
            map_name = self.map_prefix(map_prefix, old=True)
            if map_name not in self.old_maps:
                channel.reply("^3{} ^2has no times on ql.leeto.fi".format(map_prefix))
            else:
                self.old_top(map_name, msg[0], amount, channel)
        else:
            map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
            self.top(map_name, weapons, amount, channel)

    @minqlx.thread
    def top(self, map_name, weapons, amount, channel):
        records = self.get_records(map_name, weapons)
        if not weapons:
            map_name += "^2(strafe)"
        if not records.records:
            channel.reply("^2No times were found on ^3{}".format(map_name))
            return

        times = []
        for i in range(amount):
            try:
                record = records.records[i]
                times.append(
                    " ^3{}. ^4{} ^2{}".format(record['rank'], record['name'], race.time_string(record['time'])))
            except IndexError:
                break

        self.output_times(map_name, times, channel)

    @minqlx.thread
    def old_top(self, map_name, command, amount, channel):  #
        if "s" in command:
            weapons = False
            mode = self.get_cvar("qlx_raceMode", int) + 1
        else:
            weapons = True
            mode = self.get_cvar("qlx_raceMode", int)

        try:
            records = requests.get("{}/{}/{}.json".format(OLDTOP_URL, map_name, mode)).json()["records"]
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
            return

        if not weapons:
            map_name += "^2(strafe)"
        if not records:
            channel.reply("^2No old times were found on ^3{}".format(map_name))
            return

        times = []
        for i in range(amount):
            try:
                record = records[i]
                times.append(
                    " ^3{}. ^4{} ^2{}".format(record['rank'], record['name'], race.time_string(record['time'])))
            except IndexError:
                break

        self.output_times(map_name, times, channel)

    def cmd_all(self, player, msg, channel):
        """Outputs the ranks and times of everyone on
        the server for a map.
        """
        if len(msg) == 1:
            map_prefix = self.game.map
        elif len(msg) == 2:
            map_prefix = msg[1]
        else:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        self.all(map_name, weapons, channel)

    @minqlx.thread
    def all(self, map_name, weapons, channel):
        records = self.get_records(map_name, weapons)
        times = {}
        for p in self.players():
            rank, time = records.pb(p.steam_id)
            if rank:
                times[rank] = "^7{} ^2{}".format(p, race.time_string(time))

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
        if len(msg) == 1 and player.score != 2147483647 and player.score != 0:
            time = player.score
            map_prefix = self.game.map
        elif len(msg) == 2:
            time = race.time_ms(msg[1])
            map_prefix = self.game.map
        elif len(msg) == 3:
            time = race.time_ms(msg[1])
            map_prefix = msg[2]
        else:
            channel.reply("^7Usage: ^6{0} <time> [map] ^7or just ^6{0} ^7if you have set a time".format(msg[0]))
            return

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        self.ranktime(map_name, weapons, time, channel)

    @minqlx.thread
    def ranktime(self, map_name, weapons, time, channel):
        records = self.get_records(map_name, weapons)
        rank = records.rank_from_time(time)
        last_rank = records.last_rank + 1
        if not rank:
            rank = last_rank

        if not weapons:
            map_name += "^2(strafe)"

        channel.reply("^3{} ^2would be rank ^3{} ^2of ^3{} ^2on ^3{}".format(race.time_string(time), rank,
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
                return minqlx.RET_STOP_ALL
            except minqlx.NonexistentPlayerError:
                player.tell("Invalid ID.")
                return minqlx.RET_STOP_ALL
        elif len(msg) > 2:
            return

        if "s" in msg[0].lower():
            mode = self.get_cvar("qlx_raceMode", int) + 1
            strafe = "strafe "
        else:
            mode = self.get_cvar("qlx_raceMode", int)
            strafe = ""

        self.avg(player, mode, strafe, channel)

    @minqlx.thread
    def avg(self, player, mode, strafe, channel):
        """API Doc: https://qlrace.com/apidoc/1.0/records/player.html"""
        try:
            data = requests.get("https://qlrace.com/api/player/{}".format(player.steam_id), params=PARAMS[mode]).json()
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
            return

        name = data["name"]
        total_maps = len(data["records"])
        if name is not None and total_maps > 0:
            avg = data["average"]
            medals = data["medals"]
            channel.reply("^7{} ^2average {}rank: ^3{:.2f}^2({} maps) ^71st: ^3{} ^72nd: ^3{} ^73rd: ^3{}"
                          .format(player, strafe, avg, total_maps, medals[0], medals[1], medals[2]))
        else:
            channel.reply("^7{} ^2has no {}records :(".format(player, strafe))

    def cmd_random_map(self, player, msg, channel):
        """Callvotes a random map."""
        map_name = random.choice(self.maps)
        minqlx.client_command(player.id, "cv map {}".format(map_name))

    def cmd_recent(self, player, msg, channel):
        """Outputs the most recent maps from QLRace.com"""
        amount = 10
        if len(msg) == 2:
            try:
                amount = int(msg[1])
                if not (0 <= amount <= 30):
                    raise ValueError
            except ValueError:
                player.tell("amount must be positive integer <= 30")
                return minqlx.RET_STOP_ALL
        elif len(msg) > 2:
            return minqlx.RET_USAGE

        self.recent(channel, amount)

    @minqlx.thread
    def recent(self, channel, amount):
        """API Doc: https://qlrace.com/apidoc/1.0/Maps/maps.html"""
        try:
            data = requests.get("https://qlrace.com/api/maps?sort=recent").json()
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
            return

        maps = '^7, ^3'.join(data["maps"][:amount])
        channel.reply("Most recent maps(by first record date): ^3{}".format(maps))

    def cmd_goto(self, player, msg, channel):
        """Go to a player's location.
        Player needs to kill themselves/rejoin for a time to count."""
        map_name = self.game.map.lower()
        if map_name in GOTO_DISABLED:
            player.tell("!goto is disabled on {}".format(map_name))
            return minqlx.RET_STOP_ALL

        if len(msg) == 2:
            try:
                i = int(msg[1])
                target_player = self.player(i)
                if not (0 <= i < 64) or not target_player or not self.player(i).is_alive or i == player.id:
                    raise ValueError
            except ValueError:
                player.tell("Invalid ID.")
                return minqlx.RET_STOP_ALL
            except minqlx.NonexistentPlayerError:
                player.tell("Invalid ID.")
                return minqlx.RET_STOP_ALL
        elif len(msg) != 2:
            return minqlx.RET_USAGE

        if player.team == "spectator":
            player.team = "free"

        # respawn player so he can't cheat by touching the start flag then !goto finish
        minqlx.player_spawn(player.id)
        minqlx.set_position(player.id, target_player.position())

        # add player to goto dict
        self.goto[player.steam_id] = player.score
        player.tell("^6Your time won't count, unless you kill yourself")

        if self.game.map.lower() == "kraglejump":
            # some stages need haste and some don't, so 60 is a compromise...
            player.powerups(haste=60)
        elif self.game.map.lower() in HASTE:
            player.powerups(haste=999)

    def cmd_commands(self, player, msg, channel):
        """Outputs list of race commands."""
        channel.reply(
            "Commands: ^3!(s)pb !(s)rank !(s)top !old(s)top !(s)all !(s)ranktime !(s)avg !randommap !recent !goto")

    def output_times(self, map_name, times, channel):
        """Outputs times to the channel. Will split
        lines so that each record is not on 2 separate lines.
        :param map_name: Map name
        :param times: List of map times
        :param channel: Channel to reply to
        """
        output = ["^2{}:".format(map_name)]
        for time in times:
            if len(output[len(output) - 1]) + len(time) < 100:
                output[len(output) - 1] += time
            else:
                output.append(time)

        for out in output:
            channel.reply(out.lstrip())

    @minqlx.thread
    def get_maps(self):
        """Gets the list of race maps from QLRace.com and
        adds current map to the list if it isn't already.
        API Doc: https://qlrace.com/apidoc/1.0/Maps/maps.html
        """
        try:
            self.maps = requests.get("https://qlrace.com/api/maps").json()["maps"]
            self.old_maps = requests.get("{}/maps.json".format(OLDTOP_URL)).json()["maps"]
        except requests.exceptions.RequestException as e:
            self.logger.error(e)

        current_map = self.game.map.lower()
        if current_map not in self.maps:
            self.maps.append(current_map)

    def map_prefix(self, map_prefix, old=False):
        """Returns the first map which matches the prefix.
        :param map_prefix: Prefix of a map
        :param old: Optional, whether to use old maps list.
        """
        if old:
            maps = self.old_maps
        else:
            maps = self.maps

        if map_prefix.lower() in maps:
            return map_prefix.lower()

        return next((x for x in maps if x.startswith(map_prefix.lower())), None)

    def get_map_name_weapons(self, map_prefix, command, channel):
        """Returns map name and weapons boolean.
        :param map_prefix: Prefix of a map
        :param command: Command the player entered
        :param channel: Channel to reply to.
        """
        map_name = self.map_prefix(map_prefix)
        if not map_name:
            channel.reply("^2No map found for ^3{}. ^2If this is wrong, ^6!updatemaps".format(map_prefix))
            return minqlx.RET_STOP_EVENT
        weapons = False if "s" in command.lower() else True
        return map_name, weapons

    def get_records(self, map_name, weapons):
        """Returns race records from QLRace.com
        :param map_name: Map name
        :param weapons: Weapons boolean
        """
        if weapons:
            mode = self.get_cvar("qlx_raceMode", int)
            return RaceRecords(map_name, mode)
        else:
            mode = self.get_cvar("qlx_raceMode", int) + 1
            return RaceRecords(map_name, mode)

    def brand_map(self, map_name):
        """Brands map title with "<qlx_raceBrand> - map name".
        :param map_name: Current map
        """
        brand_map = "{} - {}".format(self.get_cvar("qlx_raceBrand"), map_name)
        minqlx.set_configstring(3, brand_map)

    @staticmethod
    def time_ms(time_string):
        """Returns time in milliseconds.
        :param time_string: Time as a string, examples 2.300, 1:12.383
        """
        minutes, seconds = (["0"] + time_string.split(":"))[-2:]
        return int(60000 * int(minutes) + round(1000 * float(seconds)))

    @staticmethod
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


class RaceRecords:
    """Race records object. Gets records using QLRace.com API."""

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
        :param rank: Rank of a record
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
        :param time: Time in milliseconds
        """
        for i, record in enumerate(self.records):
            if time <= record["time"]:
                return i + 1

    def pb(self, player_id):
        """Returns a players rank and time.
        :param player_id: Player id
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
            time_diff = "^0[^1+" + race.time_string(time_diff) + "^0]"
        else:
            time_diff = ""
        time = race.time_string(time)
        strafe = "^2(strafe)" if not self.weapons else ""
        tied = "tied " if tied else ""
        return "^7{} ^2is {}rank ^3{} ^2of ^3{} ^2with ^3{}{} ^2on ^3{}{}" \
            .format(name, tied, rank, self.last_rank, time, time_diff, self.map_name, strafe)

    def get_data(self):
        """Returns the records for the map and mode from QLRace.com
        API Doc: https://qlrace.com/apidoc/1.0/records/map.html"""
        try:
            r = requests.get("https://qlrace.com/api/map/{}".format(self.map_name), params=PARAMS[self.mode])
            r.raise_for_status()
            return r.json()["records"]
        except requests.exceptions.RequestException:
            return []

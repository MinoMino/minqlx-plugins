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
import time

PARAMS = ({}, {"weapons": "false"}, {"physics": "classic"}, {"physics": "classic", "weapons": "false"})
OLDTOP_URL = "https://cdn.rawgit.com/QLRace/oldtop/master/oldtop/"

GOTO_DISABLED = ("ndql", "bounce", "df_coldrun", "wernerjump", "puzzlemap")
HASTE = ("df_handbreaker4", "handbreaker4_long", "handbreaker", "df_piyofunjumps", "funjumpsmap", "df_luna", "insane1",
         "bounce", "df_nodown", "df_etleague", "df_extremepkr", "labyrinth", "airmaxjumps", "sarcasmjump", "criclejump",
         "df_verihard", "cursed_temple", "skacharohuth", "randommap", "just_jump_2", "just_jump_3", "criclejump",
         "eatme", "wernerjump", "bloodydave", "tranquil", "et_map2", "et_map3", "et_map4", "et_map5", "zeel_ponpon",
         "snorjumpb1", "snorjump2", "piyojump2", "woftct", "apex")

GAUNTLET_ONLY = ("k4n", "ndql")
GAUNTLET_AND_MG = ("blockworld", "caep4", "climbworld", "df_etleague", "df_extremepkr", "df_handbreaker4", "df_lickape",
                   "df_lickcells""df_lickcells2", "df_lickfudge", "df_lickhq", "df_lickrevived", "df_lickrevived2",
                   "df_licksux", "df_nodown", "df_o3jvelocity", "df_palmslane", "df_piyofunjumps", "df_qsnrun",
                   "df_verihard", "drtrixiipro", "hangtime", "ingus", "marvin", "northrun", "pea_impostor", "poptart",
                   "purpletorture", "r7_pyramid", "raveroll", "sl1k_tetris_easy", "snorjumpb1", "sodomia", "timelock2",
                   "timelock4", "vanilla_03", "vanilla_04", "vanilla_07", "vanilla_10", "walkathon", "weirdwild",
                   "wraiths", "yellowtorture", "run139", "inder_inder", "quartz", "timelock3")
PLASMA = ("think1", "xproject", "plasmax", "wub_junk")
ROCKET = ("runstolfer", "charon", "charon_bw", "kozmini1", "kozmini2", "kozmini3", "kozmini4", "kozmini5", "kozmini6",
          "kozmini7", "kozmini8", "jumpspace")
GRENADE = ("grenadorade")

_RE_POWERUPS = re.compile(r'print ".+\^3 got the (Haste|Battle Suit|Quad Damage)!\^7\n"')


class race(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("map", self.handle_map)
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("server_command", self.handle_server_command)
        self.add_hook("stats", self.handle_stats, priority=minqlx.PRI_HIGHEST)
        self.add_hook("player_spawn", self.handle_player_spawn, priority=minqlx.PRI_HIGHEST)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("client_command", self.handle_client_command)
        self.add_hook("frame", self.handle_frame)
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
        self.add_command("savepos", self.cmd_savepos)
        self.add_command("loadpos", self.cmd_loadpos)
        self.add_command("maps", self.cmd_maps, priority=minqlx.PRI_HIGH)
        self.add_command(("haste", "removehaste"), self.cmd_haste)
        self.add_command(("timer", "starttimer", "stoptimer"), self.cmd_timer)
        self.add_command(("commands", "cmds", "help"), self.cmd_commands, priority=minqlx.PRI_HIGH)

        self.set_cvar_once("qlx_raceMode", "0")  # 0 = Turbo/PQL, 2 = Classic/VQL
        self.set_cvar_once("qlx_raceBrand", "QLRace.com")

        self.move_player = {}  # Queued !goto/!loadto positions. {steam_id: position}
        self.goto = {}  # Players which have used !goto/!loadpos. {steam_id: score}
        self.savepos = {}  # Saved player positions. {steam_id: player.state.position}
        self.frame = {}  # The frame when player used !timer. {steam_id: frame}
        self.current_frame = 0  # Number of frames the map has been playing for.

        self.maps = []
        self.old_maps = []
        self.get_maps()

    def handle_new_game(self):
        """Brands map title on new game."""
        map_name = self.game.map.lower()
        self.brand_map(map_name)

    def handle_map(self, map_name, factory):
        """Brands map title and updates list of race maps on map change.
        Also sets correct starting weapons for the map and clears savepos
        and move_player dicts.
        """
        map_name = map_name.lower()
        self.brand_map(map_name)
        self.get_maps()
        self.savepos = {}
        self.move_player = {}
        self.current_frame = 0

        if factory in ("qlrace_turbo", "qlrace_classic"):
            if map_name in GAUNTLET_AND_MG:
                self.set_cvar("g_startingWeapons", "3")
                if map_name in ("poptart", "climbworld"):
                    self.set_cvar("g_infiniteAmmo", "1")
                else:
                    self.set_cvar("g_infiniteAmmo", "0")
            elif map_name in GRENADE:
                self.set_cvar("g_startingWeapons", "9")
                self.set_cvar("g_infiniteAmmo", "1")
            elif map_name in GAUNTLET_ONLY:
                self.set_cvar("g_startingWeapons", "1")
                self.set_cvar("g_infiniteAmmo", "0")
            elif map_name in PLASMA:
                self.set_cvar("g_startingWeapons", "131")
                self.set_cvar("g_infiniteAmmo", "1")
            elif map_name in ROCKET:
                self.set_cvar("g_startingWeapons", "19")
                self.set_cvar("g_infiniteAmmo", "1")
            elif map_name == "rocketx":
                self.set_cvar("g_startingWeapons", "17")
                self.set_cvar("g_infiniteAmmo", "1")
            elif map_name == "bfgx":
                self.set_cvar("g_startingWeapons", "257")
                self.set_cvar("g_infiniteAmmo", "1")
            elif map_name == "nmn":
                self.set_cvar("g_startingWeapons", "16")
                self.set_cvar("g_infiniteAmmo", "1")
            elif map_name == "wsm":
                self.set_cvar("g_startingWeapons", "129")
                self.set_cvar("g_infiniteAmmo", "0")
                self.set_cvar("g_startingAmmo_pg", "1")
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
            elif self.get_cvar("qlx_raceMode", int) == 2:
                if map_name == "dontlookdown":
                    self.set_cvar("pmove_RampJump", "1")
                else:
                    self.set_cvar("pmove_RampJump", "0")

            if map_name == "puzzlemap":
                self.set_cvar("g_infiniteAmmo", "1")
                self.set_cvar("g_startingWeapons", "3")
                minqlx.load_plugin("puzzlemap")
            else:
                try:
                    minqlx.unload_plugin("puzzlemap")
                except minqlx.PluginUnloadError:
                    pass

            if map_name == "walkathon":
                self.set_cvar("g_respawn_delay_min", "1000")
                self.set_cvar("g_respawn_delay_max", "1000")
            else:
                self.set_cvar("g_respawn_delay_min", "10")
                self.set_cvar("g_respawn_delay_max", "10")

            if map_name == "pornstarghost3":
                self.set_cvar("g_maxFlightFuel", "10000")
            else:
                self.set_cvar("g_maxFlightFuel", "16000")

    def handle_vote_called(self, player, vote, args):
        """Cancels the vote when a duplicated map is voted for."""
        if vote.lower() == "map" and len(args) > 0:
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
        """Resets a player's score if they used !goto or !loadpos."""
        if stats["TYPE"] == "PLAYER_RACECOMPLETE":
            steam_id = int(stats["DATA"]["STEAM_ID"])
            if steam_id in self.goto:
                player = self.player(steam_id)
                player.score = self.goto[steam_id]
                player.tell("^7Your time does not count because you used ^6!goto ^7or ^6!loadpos.")

    def handle_player_spawn(self, player):
        """Spawns player instantly and gives quad/haste on some maps.
        Moves player to position if they used !goto or !loadpos.
        Removes player from frame dict."""
        map_name = self.game.map.lower()
        if player.team == "free":
            player.is_alive = True

            if map_name == "wsm":
                player.powerups(quad=999999)
            elif map_name in HASTE:
                player.powerups(haste=999999)
        if player.steam_id in self.move_player and player.is_alive:
            if player.steam_id not in self.goto:
                player.tell("^6Your time will not count, unless you kill yourself.")
                self.goto[player.steam_id] = player.score

            minqlx.set_position(player.id, self.move_player.pop(player.steam_id))

            if map_name == "kraglejump":
                player.powerups(haste=60)  # some stages need haste and some don't, so 60 is a compromise...

        self.frame.pop(player.steam_id, None)

    def handle_player_disconnect(self, player, reason):
        """Removes player from goto, savepos and move_player dicts when
        they disconnect."""
        self.goto.pop(player.steam_id, None)
        self.savepos.pop(player.steam_id, None)
        self.move_player.pop(player.steam_id, None)
        self.frame.pop(player.steam_id, None)

    def handle_team_switch(self, player, old_team, new_team):
        """Removes player from goto, move_player and frame dicts when
        they spectate."""
        if new_team == "spectator":
            self.goto.pop(player.steam_id, None)
            self.move_player.pop(player.steam_id, None)
            self.frame.pop(player.steam_id, None)

    def handle_client_command(self, player, cmd):
        """Spawns player right away if they use /kill and
        removes them from goto and frame dicts."""
        if cmd == "kill" and player.team == "free":
            minqlx.player_spawn(player.id)
            self.goto.pop(player.steam_id, None)
            self.frame.pop(player.steam_id, None)
            return minqlx.RET_STOP_EVENT

    def handle_frame(self):
        """Increments current frame and center_prints timer to all
        player who used !timer. Also removes player from goto
        dict if they died(death event wasn't getting triggered)."""
        self.current_frame += 1

        for p in self.frame:
            ms = (self.current_frame - self.frame[p]) * 25
            self.player(p).center_print(race.time_string(ms))

        # makes new dict with dead players removed
        self.goto = {p: score for p, score in self.goto.items() if self.player(p).health > 0}

    def cmd_disabled(self, player, msg, channel):
        """Disables !slap and !slay."""
        player.tell("^6{} ^7is disabled".format(msg[0]))
        return minqlx.RET_STOP_ALL

    def cmd_updatemaps(self, player, msg, channel):
        """Updates list of race maps"""
        self.get_maps()

    def cmd_pb(self, player, msg, channel):
        """Outputs the player's personal best time for a map."""
        @minqlx.thread
        def pb(map_name):
            records = self.get_records(map_name, weapons)
            rank, time = records.pb(player.steam_id)
            if not weapons:
                map_name += "^2(strafe)"
            if rank:
                channel.reply(records.output(player, rank, time))
            else:
                channel.reply("^2No time found for ^7{} ^2on ^3{}".format(player, map_name))

        if len(msg) == 1:
            map_prefix = self.game.map.lower()
        elif len(msg) == 2:
            map_prefix = msg[1]
        else:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        pb(map_name)

    def cmd_rank(self, player, msg, channel):
        """Outputs the x rank time for a map. Default rank
        if none is given is 1.
        """
        @minqlx.thread
        def get_rank(map_name):
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
        get_rank(map_name)

    def cmd_top(self, player, msg, channel):
        """Outputs top x amount of times for a map. Default amount
        if none is given is 3. Maximum amount is 20.
        TODO: More detailed top which uses player.tell. !top vql/classic/pql/turbo.
        Will probably reimplement everything from scratch."""
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

        if msg[0][1].lower() == "o":
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
        if "s" in command.lower():
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
        @minqlx.thread
        def get_all(map_name):
            records = self.get_records(map_name, weapons).records
            players = {p.steam_id for p in self.players()}
            times = []
            for record in records:
                if record["player_id"] in players:
                    times.append(" ^3{}. ^7{} ^2{}".format(record["rank"], record["name"],
                                                           race.time_string(record["time"])))
            if not weapons:
                map_name += "^2(strafe)"
            if times:
                self.output_times(map_name, times, channel)
            else:
                channel.reply("^2No times were found for anyone on ^3{} ^2:(".format(map_name))

        if len(msg) == 1:
            map_prefix = self.game.map
        elif len(msg) == 2:
            map_prefix = msg[1]
        else:
            return minqlx.RET_USAGE

        map_name, weapons = self.get_map_name_weapons(map_prefix, msg[0], channel)
        get_all(map_name)

    def cmd_ranktime(self, player, msg, channel):
        """Outputs which rank a time would be."""
        @minqlx.thread
        def ranktime(map_name):
            records = self.get_records(map_name, weapons)
            rank = records.rank_from_time(time)
            last_rank = records.last_rank + 1
            if not rank:
                rank = last_rank

            if not weapons:
                map_name += "^2(strafe)"

            channel.reply("^3{} ^2would be rank ^3{} ^2of ^3{} ^2on ^3{}"
                          .format(race.time_string(time), rank, last_rank, map_name))

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
        ranktime(map_name)

    def cmd_avg(self, player, msg, channel):
        """Outputs a player average rank."""
        @minqlx.thread
        def avg():
            """API Doc: https://qlrace.com/apidoc/1.0/records/player.html"""
            try:
                data = requests.get("https://qlrace.com/api/player/{}".format(player.steam_id),
                                    params=PARAMS[mode]).json()
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

        if msg[0][1].lower() == "s":
            mode = self.get_cvar("qlx_raceMode", int) + 1
            strafe = "strafe "
        else:
            mode = self.get_cvar("qlx_raceMode", int)
            strafe = ""
        avg()

    def cmd_random_map(self, player, msg, channel):
        """Callvotes a random map."""
        map_name = random.choice(self.maps)
        minqlx.client_command(player.id, "cv map {}".format(map_name))

    def cmd_recent(self, player, msg, channel):
        """Outputs the most recent maps from QLRace.com"""
        @minqlx.thread
        def recent():
            """API Doc: https://qlrace.com/apidoc/1.0/Maps/maps.html"""
            try:
                data = requests.get("https://qlrace.com/api/maps?sort=recent").json()
            except requests.exceptions.RequestException as e:
                self.logger.error(e)
                return

            maps = '^7, ^3'.join(data["maps"][:amount])
            channel.reply("Most recent maps(by first record date): ^3{}".format(maps))

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
        recent()

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
            if 'spec_delay' in self.plugins and player.steam_id in self.plugins['spec_delay'].spec_delays:
                player.tell("^6You must wait 15 seconds before joining after spectating")
                return minqlx.RET_STOP_ALL

            self.move_player[player.steam_id] = target_player.state.position
            player.team = "free"
        else:
            self.move_player[player.steam_id] = target_player.state.position
            minqlx.player_spawn(player.id)  # respawn player so he can't cheat

    def cmd_savepos(self, player, msg, channel):
        """Saves current position."""
        if player.team != "spectator":
            # add player to savepos dict
            self.savepos[player.steam_id] = player.state.position
            player.tell("^6Position saved. Your time won't count if you use !loadpos, unless you kill yourself.")
        else:
            player.tell("Can't save position as spectator.")
        return minqlx.RET_STOP_ALL

    def cmd_loadpos(self, player, msg, channel):
        """Loads saved position."""
        if player.team != "spectator":
            if player.steam_id in self.savepos:
                self.move_player[player.steam_id] = self.savepos[player.steam_id]
                minqlx.player_spawn(player.id)  # respawn player so he can't cheat
            else:
                player.tell("^1You have to save your position first.")
        else:
            player.tell("^1Can't load position as spectator.")
        return minqlx.RET_STOP_ALL

    def cmd_maps(self, player, msg, channel):
        """Tells player list of all maps."""
        @minqlx.thread
        def maps():
            player.tell("List of maps:")
            for count, map_name in enumerate(self.maps, start=1):
                if count % 26 == 0:
                    time.sleep(0.4)
                player.tell(map_name)

        maps()
        return minqlx.RET_STOP_ALL

    def cmd_haste(self, player, msg, channel):
        """Gives/removes haste on haste maps."""
        if player.team == "spectator":
            player.tell("^1You cannot use ^3{} ^1as a spectator!".format(msg[0]))
            return minqlx.RET_STOP_ALL

        if self.game.map.lower() in HASTE:
            duration = 0 if "remove" in msg[0].lower() else 999999
            player.powerups(haste=duration)
        else:
            player.tell("^1You cannot use ^3{} ^1on non haste maps.".format(msg[0]))
        return minqlx.RET_STOP_ALL

    def cmd_timer(self, player, msg, channel):
        """Starts/stops personal timer."""
        if player.team == "spectator":
            player.tell("^1You need to join the game to use this command.")
        else:
            if msg[0].startswith("!stop"):
                try:
                    del self.frame[player.steam_id]
                except KeyError:
                    player.tell("^1There is no timer started.")
            else:
                self.frame[player.steam_id] = self.current_frame
        return minqlx.RET_STOP_ALL

    def cmd_commands(self, player, msg, channel):
        """Outputs list of race commands."""
        channel.reply("Commands: ^3!(s)pb !(s)rank !(s)top !old(s)top !(s)all !(s)ranktime !(s)avg !randommap !recent")
        channel.reply("^3!goto !savepos !loadpos !maps !haste !removehaste !timer !stoptimer")
        return minqlx.RET_STOP_ALL

    def output_times(self, map_name, times, channel):
        """Outputs times to the channel. Will split lines
        so that each record is on one line only.
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
        weapons = False if command[1].lower() == "s" else True
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

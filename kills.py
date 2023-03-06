# This is an extension plugin  for minqlx.
# Copyright (C) 2016 mattiZed (github) aka mattiZed (ql)
# ** This plugin is thanks to mattiZed. Just modified EXTENSIVELY by BarelyMiSSeD
# to expand on the pummel counting and add other kill type monitors.
# It also adds end of match reports for the match,
# and total counts for each of the kill types when called.
#
# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this plugin. If not, see <http://www.gnu.org/licenses/>.

# This is a fun plugin written for Mino's Quake Live Server Mod minqlx.
# It displays "Killer x:y Victim" message when Victim gets a monitored kill
# and stores the information within REDIS DB
#
# Players can display their kill stats with:
#  "pummels" via !pummel or !gauntlet
#  "air gauntlets" via !airgauntlet
#  "grenades" via !grenades or !grenade
#  "air rockets" via !rockets or !rocket
#  "air plasma" via !plasma
#  "air rail" via !airrail
#  "telefrag" via !telefrag
#  "team telefrag" via !teamtele or !teamtelefrag
#  "speed kill" via !speed or !speedkill
# the Total displayed is all of that type kill and it displays kills for
# the victims that are on the server on the same time.
#
#
# **** CVAR Settings ****
# set qlx_killsPlaySounds "1"           : Turns the sound playing when a kill is made On/Off
# set qlx_killsSpeedMinimum "800"       : Sets the minimum speed needed to record a speed kill
# set qlx_killsMonitorKillTypes "511"   : Sets the types of kills that are monitored. See Below for settings.
# set qlx_killsEndGameMsg "1"           : Enable/Disable the end of game kills messages
#
# ******  How to set which kill types are recorded ******
# Add the values for each type of kill listed below and set that value
#  to the qlx_killsMonitorKillTypes in the same location as the rest of
#  your minqlx cvar's.
#
#  ****Kill Monitor Values****
#             Pummel:  1    (records any pummel/gauntlet kill)
#         Air Pummel:  2    (records any pummel/gauntlet kill where killer and victim are airborne)
#     Direct Grenade:  4    (records any kills with direct grenade hits)
#        Air Rockets:  8    (records any Air Rocket kills)
#         Air Plasma:  16   (records any Air Plasma kills)
#          Air Rails:  32   (records any Air Rails kills where both the killer and victim are airborne)
#           Telefrag:  64   (records any enemy telefrag)
#  Telefrag TeamKill:  128  (records any teamkill telefrag)
#         Speed Kill:  256
#
# The Default value is 'set qlx_killsMonitorKillTypes "511"' which enables
#  all the kill monitor types.

import minqlx
import re
from time import sleep

# DB related
PLAYER_KEY = "minqlx:players:{}:kills"

# Add Game types here if this script is not working with your game type. Follow the format.
# Find your gametype in game with the !kgt or !killsgametype command.
SUPPORTED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ffa", "ictf", "ad")

VERSION = 1.19


class kills(minqlx.Plugin):
    def __init__(self):
        self.set_cvar_once("qlx_killsMonitorKillTypes", "511")
        self.set_cvar_once("qlx_killsPlaySounds", "1")
        self.set_cvar_once("qlx_killsSpeedMinimum", "800")
        self.set_cvar_once("qlx_killsEndGameMsg", "1")

        self.add_hook("kill", self.handle_kill)
        self.add_hook("game_end", self.handle_end_game)
        self.add_hook("map", self.handle_map)
        self.add_hook("round_countdown", self.handle_round_count)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)

        self.add_command(("pummel", "gauntlet"), self.cmd_pummel)
        self.add_command(("airpummel", "airgauntlet"), self.cmd_airpummel)
        self.add_command(("grenades", "grenade"), self.cmd_grenades)
        self.add_command(("rockets", "rocket"), self.cmd_rocket)
        self.add_command("plasma", self.cmd_plasma)
        self.add_command(("airrail", "airrails"), self.cmd_airrail)
        self.add_command("telefrag", self.cmd_telefrag)
        self.add_command(("teamtelefrag", "teamtele"), self.cmd_teamtelefrag)
        self.add_command(("speed", "speedkill"), self.cmd_speedkill)
        self.add_command("speedlimit", self.cmd_speedlimit)
        self.add_command("kills_version", self.kills_version)
        self.add_command(("gametypes", "games"), self.supported_games)
        self.add_command("kills", self.kills_recorded)
        self.add_command(("kgt", "killsgametype"), self.cmd_kills_gametype, 3)
        self.add_command(("rkm", "reloadkillsmonitor"), self.cmd_kills_monitor, 3)

        self._pummel = {}
        self._airpummel = {}
        self._grenades = {}
        self._rockets = {}
        self._plasma = {}
        self._airrail = {}
        self._telefrag = {}
        self._teamtelefrag = {}
        self._speed = {}

        self._supported_gametype = False
        self._roundActive = 0

        self._play_sounds = self.get_cvar("qlx_killsPlaySounds", bool)
        self._playing_sound = False
        self._killMonitor = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.cmd_kills_monitor()
        self.convert_old()

    def handle_kill(self, victim, killer, data):
        self.process_kill(victim, killer, data)
        return

    @minqlx.thread
    def process_kill(self, victim, killer, data):
        try:
            if self._supported_gametype:
                mod = data["MOD"]
                msg = None
                killer_steam_id = data["KILLER"]["STEAM_ID"]
                victim_steam_id = data["VICTIM"]["STEAM_ID"]
                if killer_steam_id[0] in ["9", "0"] or victim_steam_id[0] in ["0", "9"]:
                    return
                if data["KILLER"]["SPEED"] > self.get_cvar("qlx_killsSpeedMinimum", int) and self._killMonitor[8]:
                    if self._play_sounds and not self._playing_sound:
                        self._playing_sound = True
                        self.sound_play("sound/feedback/impact4")

                    if self.game.state == "in_progress":
                        self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":speedkill", victim_steam_id)
                        self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":speedkill:" + victim_steam_id)
                        speed_value = PLAYER_KEY.format(killer_steam_id) + ":highspeed"
                        if self.db.exists(speed_value):
                            if int(data["KILLER"]["SPEED"]) > int(self.db[PLAYER_KEY.format(killer_steam_id) +
                                                                          ":highspeed"].split(".")[0]):
                                self.db[PLAYER_KEY.format(killer_steam_id) + ":highspeed"] =\
                                    int(data["KILLER"]["SPEED"])
                        else:
                            self.db[PLAYER_KEY.format(killer_steam_id) + ":highspeed"] = int(data["KILLER"]["SPEED"])

                        killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":speedkill:" +
                                               victim_steam_id]
                        victim_score = 0
                        if self.db.exists(PLAYER_KEY.format(victim_steam_id) + ":speedkill:" + killer_steam_id):
                            victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":speedkill:" +
                                                   killer_steam_id]

                        msg = "^1SPEED ^3{}^1! ^7{} ^1{}^7:^1{}^7 {}".format(int(data["KILLER"]["SPEED"]), killer.name,
                                                                             killer_score, victim_score, victim.name)
                        self.add_killer(str(killer.name), "SPEED")
                    else:
                        msg = "^1SPEED ^3{}^1! ^7{}^7 :^7 {} ^7(^3warmup^7)".format(int(data["KILLER"]["SPEED"]),
                                                                                    killer.name, victim.name)

                if mod == "GAUNTLET" and (self._killMonitor[0] or self._killMonitor[1]):
                    killed = data["VICTIM"]
                    kill = data["KILLER"]
                    if killed["AIRBORNE"] and kill["AIRBORNE"] and not killed["SUBMERGED"] and\
                            not kill["SUBMERGED"] and self._killMonitor[1]:
                        if self._play_sounds and not self._playing_sound:
                            self._playing_sound = True
                            self.sound_play("sound/vo_evil/rampage2")

                        if self.game.state == "in_progress":
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":airpummel", victim_steam_id)
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":airpummel:" + victim_steam_id)

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":airpummel:" +
                                                   victim_steam_id]
                            victim_score = 0
                            if self.db.exists(PLAYER_KEY.format(victim_steam_id) + ":airpummel:" +
                                              killer_steam_id):
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":airpummel:" +
                                                       killer_steam_id]

                            msg = "^1AIR GAUNTLET!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score,
                                                                                 victim_score, victim.name)
                            self.add_killer(str(killer.name), "AIRGAUNTLET")
                        else:
                            msg = "^1AIR GAUNTLET!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                    elif self._killMonitor[0]:
                        if self._play_sounds and not self._playing_sound:
                            self._playing_sound = True
                            self.sound_play("sound/vo_evil/humiliation1")

                        if self.game.state == "in_progress":
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":pummeled", victim_steam_id)
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":pummeled:" + victim_steam_id)

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":pummeled:" +
                                                   victim_steam_id]
                            victim_score = 0
                            if self.db.exists(PLAYER_KEY.format(victim_steam_id) + ":pummeled:" + killer_steam_id):
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":pummeled:" +
                                                       killer_steam_id]

                            msg = "^1PUMMEL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score,
                                                                           victim.name)
                            self.add_killer(str(killer.name), "GAUNTLET")
                        else:
                            msg = "^1PUMMEL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "GRENADE" and self._killMonitor[2]:
                    if self._play_sounds and not self._playing_sound:
                        self._playing_sound = True
                        self.sound_play("sound/vo_female/holy_shit")

                    if self.game.state == "in_progress":
                        self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":grenaded", victim_steam_id)
                        self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":grenaded:" + victim_steam_id)

                        killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":grenaded:" + victim_steam_id]
                        victim_score = 0
                        if self.db.exists(PLAYER_KEY.format(victim_steam_id) + ":grenaded:" + killer_steam_id):
                            victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":grenaded:" +
                                                   killer_steam_id]

                        msg = "^1GRENADE KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score,
                                                                             victim.name)
                        self.add_killer(str(killer.name), "GRENADE")
                    else:
                        msg = "^1GRENADE KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "ROCKET" and self._killMonitor[3]:
                    killed = data["VICTIM"]
                    if killed["AIRBORNE"] and not killed["SUBMERGED"]:
                        if self._play_sounds and not self._playing_sound:
                            self._playing_sound = True
                            self.sound_play("sound/vo_evil/midair1")

                        if self.game.state == "in_progress":
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":rocket", victim_steam_id)
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":rocket:" + victim_steam_id)

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":rocket:" +
                                                   victim_steam_id]
                            victim_score = 0
                            if self.db.exists(PLAYER_KEY.format(victim_steam_id) + ":rocket:" + killer_steam_id):
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":rocket:" +
                                                       killer_steam_id]

                            msg = "^1AIR ROCKET KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score,
                                                                                    victim_score, victim.name)
                            self.add_killer(str(killer.name), "ROCKET")
                        else:
                            msg = "^1AIR ROCKET KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "PLASMA" and self._killMonitor[4]:
                    killed = data["VICTIM"]
                    if killed["AIRBORNE"] and not killed["SUBMERGED"]:
                        if self._play_sounds and not self._playing_sound:
                            self._playing_sound = True
                            self.sound_play("sound/vo_evil/damage")

                        if self.game.state == "in_progress":
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":plasma", victim_steam_id)
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":plasma:" + victim_steam_id)

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":plasma:" +
                                                   victim_steam_id]
                            victim_score = 0
                            if self.db.exists(PLAYER_KEY.format(victim_steam_id) + ":plasma:" + killer_steam_id):
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":plasma:" +
                                                       killer_steam_id]

                            msg = "^1AIR PLASMA KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score,
                                                                                    victim_score, victim.name)
                            self.add_killer(str(killer.name), "PLASMA")
                        else:
                            msg = "^1AIR PLASMA KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif (mod == "RAILGUN" or mod == "RAILGUN_HEADSHOT") and self._killMonitor[5]:
                    killed = data["VICTIM"]
                    kill = data["KILLER"]
                    if killed["AIRBORNE"] and kill["AIRBORNE"] and not killed["SUBMERGED"] and not kill["SUBMERGED"]:
                        if self._play_sounds and not self._playing_sound:
                            self._playing_sound = True
                            self.sound_play("sound/vo_female/midair3")

                        if self.game.state == "in_progress":
                            self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":airrail", victim_steam_id)
                            self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":airrail:" + victim_steam_id)

                            killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":airrail:" +
                                                   victim_steam_id]
                            victim_score = 0
                            if self.db.exists(PLAYER_KEY.format(victim_steam_id) + ":airrail:" + killer_steam_id):
                                victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":airrail:" +
                                                       killer_steam_id]

                            msg = "^1AIR RAIL KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score,
                                                                                  victim_score, victim.name)
                            self.add_killer(str(killer.name), "AIRRAIL")
                        else:
                            msg = "^1AIR RAIL KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "TELEFRAG" and self._killMonitor[6] and not data["TEAMKILL"]:
                    if self._play_sounds and (self._roundActive or self.game.state == "warmup") and\
                            not self._playing_sound:
                        self._playing_sound = True
                        self.sound_play("sound/vo/perforated")

                    if self.game.state == "in_progress" and self._roundActive:
                        self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":telefrag", victim_steam_id)
                        self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":telefrag:" + victim_steam_id)

                        killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":telefrag:" + victim_steam_id]
                        victim_score = 0
                        if self.db.exists(PLAYER_KEY.format(victim_steam_id) + ":telefrag:" + killer_steam_id):
                            victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":telefrag:" +
                                                   killer_steam_id]

                        msg = "^1TELEFRAG KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score, victim_score,
                                                                              victim.name)
                        self.add_killer(str(killer.name), "TELEFRAG")
                    elif self.game.state != "in_progress" and not self._roundActive:
                        msg = "^1TELEFRAG KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                elif mod == "TELEFRAG" and self._killMonitor[7] and data["TEAMKILL"]:
                    if self._play_sounds and (self._roundActive or self.game.state == "warmup") and\
                            not self._playing_sound:
                        self._playing_sound = True
                        self.sound_play("sound/vo_female/perforated")

                    if self.game.state == "in_progress" and self._roundActive:
                        self.db.sadd(PLAYER_KEY.format(killer_steam_id) + ":teamtelefrag", victim_steam_id)
                        self.db.incr(PLAYER_KEY.format(killer_steam_id) + ":teamtelefrag:" + victim_steam_id)

                        killer_score = self.db[PLAYER_KEY.format(killer_steam_id) + ":teamtelefrag:" +
                                               victim_steam_id]
                        victim_score = 0
                        if self.db.exists(PLAYER_KEY.format(victim_steam_id) + ":teamtelefrag:" + killer_steam_id):
                            victim_score = self.db[PLAYER_KEY.format(victim_steam_id) + ":teamtelefrag:" +
                                                   killer_steam_id]

                        msg = "^6TEAM ^1TELEFRAG KILL!^7 {} ^1{}^7:^1{}^7 {}".format(killer.name, killer_score,
                                                                                     victim_score, victim.name)
                        self.add_killer(str(killer.name), "TEAMTELEFRAG")
                    elif self.game.state != "in_progress" and not self._roundActive:
                        msg = "^6TEAM ^1TELEFRAG KILL!^7 {}^7 :^7 {} ^7(^3warmup^7)".format(killer.name, victim.name)

                if msg:
                    self.msg(msg)
        except Exception as e:
            minqlx.console_print("^1kills process_kill Exception: {}".format([e]))

    def handle_map(self, mapname, factory):
        self.process_map()
        return

    @minqlx.delay(0.3)
    def process_map(self):
        self._supported_gametype = self.game.type_short in SUPPORTED_GAMETYPES
        self._pummel = {}
        self._airpummel = {}
        self._grenades = {}
        self._rockets = {}
        self._plasma = {}
        self._airrail = {}
        self._telefrag = {}
        self._teamtelefrag = {}
        self._speed = {}

    def handle_round_count(self, round_number):
        self._roundActive = 0
        return

    def handle_round_start(self, round_number):
        self._roundActive = 1
        return

    def handle_round_end(self, round_number):
        self._roundActive = 0
        return

    def handle_end_game(self, data):
        if self.get_cvar("qlx_killsEndGameMsg", bool):
            self.process_end_game()
        return

    @minqlx.thread
    def process_end_game(self):
        sleep(2)
        if self._supported_gametype:
            count = 0
            msg = ["^3Pummel ^1Killers^7:"]
            for k, v in self._pummel.items():
                msg.append("{}^7:^1{}".format(k, v))
                count += 1
            if count > 0:
                self.msg("^7 ".join(msg))
                count = 0
            msg = ["^3Air Gauntlet ^1Killers^7:"]
            for k, v in self._airpummel.items():
                msg.append("{}^7:^1{}".format(k, v))
                count += 1
            if count > 0:
                self.msg("^7 ".join(msg))
                count = 0
            msg = ["^3Grenade ^1Killers^7:"]
            for k, v in self._grenades.items():
                msg.append("{}^7:^1{}".format(k, v))
                count += 1
            if count > 0:
                self.msg("^7 ".join(msg))
                count = 0
            msg = ["^3Air Rocket ^1Killers^7:"]
            for k, v in self._rockets.items():
                msg.append("{}^7:^1{}".format(k, v))
                count += 1
            if count > 0:
                self.msg("^7 ".join(msg))
                count = 0
            msg = ["^3Air Plasma ^1Killers^7:"]
            for k, v in self._plasma.items():
                msg.append("{}^7:^1{}".format(k, v))
                count += 1
            if count > 0:
                self.msg("^7 ".join(msg))
                count = 0
            msg = ["^3Air Rail ^1Killers^7:"]
            for k, v in self._airrail.items():
                msg.append("{}^7:^1{}".format(k, v))
                count += 1
            if count > 0:
                self.msg("^7 ".join(msg))
                count = 0
            msg = ["^3Telefrag ^1Killers^7:"]
            for k, v in self._telefrag.items():
                msg.append("{}^7:^1{}".format(k, v))
                count += 1
            if count > 0:
                self.msg("^7 ".join(msg))
                count = 0
            msg = ["^3Team Telefrag ^1Killers^7:"]
            for k, v in self._teamtelefrag.items():
                msg.append("{}^7:^1{}".format(k, v))
                count += 1
            if count > 0:
                self.msg("^7 ".join(msg))
                count = 0
            msg = ["^3Speed ^1Killers^7:"]
            for k, v in self._speed.items():
                msg.append("{}^7:^1{}".format(k, v))
                count += 1
            if count > 0:
                self.msg("^7 ".join(msg))
                # count = 0
        return

    def cmd_kills_gametype(self, player, msg, channel):
        player.tell("^2The current gametype is \'{}\'".format(self.game.type_short))
        return minqlx.RET_STOP_ALL

    def cmd_speedlimit(self, player, msg, channel):
        if self._killMonitor[8]:
            self.msg("^3You need a speed of at least ^1{} ^3to register a speed kill."
                     .format(self.get_cvar("qlx_killsSpeedMinimum")))
        else:
            self.msg("^4Speed Kill ^7stats are not enabled on this server.")
        return

    def cmd_pummel(self, player, msg, channel):
        if not self._killMonitor[0]:
                self.msg("^4Pummel Kill ^7stats are not enabled on this server.")
        else:
            self.exec_cmd_pummel(player, msg)
        return

    @minqlx.thread
    def exec_cmd_pummel(self, player, msg):
        try:
            if len(msg) > 1:
                player = self.player_id(msg[1], player)
            p_steam_id = player.steam_id
            total = 0
            pummels = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":pummeled")
            players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]
            msg = ""
            for p in pummels:
                total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":pummeled:" + str(p)])
                for pl in players:
                    if p == str(pl.steam_id):
                        count = self.db[PLAYER_KEY.format(p_steam_id) + ":pummeled:" + p]
                        msg += pl.name + ": ^1" + count + "^7 "
            if total:
                self.msg("^4Pummel^7 Stats for {}: Total ^4Pummels^7: ^1{}".format(player, total))
                if msg:
                    self.msg("^4Victims^7: {}".format(msg))
            else:
                self.msg("{} ^7has not ^4pummeled^7 anybody on this server.".format(player))
        except Exception as e:
            minqlx.console_print("^kills exec_cmd_pummel Exception: {}".format([e]))

    def cmd_airpummel(self, player, msg, channel):
        if not self._killMonitor[1]:
                self.msg("^4Air Pummel Kill ^7stats are not enabled on this server.")
        else:
            self.exec_cmd_airpummel(player, msg)
        return

    @minqlx.thread
    def exec_cmd_airpummel(self, player, msg):
        try:
            if len(msg) > 1:
                player = self.player_id(msg[1], player)
            p_steam_id = player.steam_id
            total = 0
            pummels = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":airpummel")
            players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]
            msg = ""
            for p in pummels:
                total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":airpummel:" + str(p)])
                for pl in players:
                    if p == str(pl.steam_id):
                        count = self.db[PLAYER_KEY.format(p_steam_id) + ":airpummel:" + p]
                        msg += pl.name + ": ^1" + count + "^7 "
            if total:
                self.msg("^4Air Gauntlet^7 Stats for {}: Total ^4Air Gauntlets^7: ^1{}".format(player, total))
                if msg:
                    self.msg("^4Victims^7: {}".format(msg))
            else:
                self.msg("{} ^7has not ^4air gauntleted^7 anybody on this server.".format(player))
        except Exception as e:
            minqlx.console_print("^kills exec_cmd_airpummel Exception: {}".format([e]))

    def cmd_grenades(self, player, msg, channel):
        if not self._killMonitor[2]:
                self.msg("^4Grenade Kill ^7stats are not enabled on this server.")
        else:
            self.exec_cmd_grenades(player, msg)
        return

    @minqlx.thread
    def exec_cmd_grenades(self, player, msg):
        try:
            if len(msg) > 1:
                player = self.player_id(msg[1], player)
            p_steam_id = player.steam_id
            total = 0
            grenades = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":grenaded")
            players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]
            msg = ""
            for p in grenades:
                total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":grenaded:" + str(p)])
                for pl in players:
                    if p == str(pl.steam_id):
                        count = self.db[PLAYER_KEY.format(p_steam_id) + ":grenaded:" + p]
                        msg += pl.name + ": ^1" + count + "^7 "
            if total:
                self.msg("^4Grenade^7 Stats for {}: Total ^4Grenade^7 Kills: ^1{}".format(player, total))
                if msg:
                    self.msg("^4Victims^7: {}".format(msg))
            else:
                self.msg("{} ^7has not ^4grenade^7 killed anybody on this server.".format(player))
        except Exception as e:
            minqlx.console_print("^kills exec_cmd_grenades Exception: {}".format([e]))

    def cmd_rocket(self, player, msg, channel):
        if not self._killMonitor[3]:
                self.msg("^4Air Rocket Kill ^7stats are not enabled on this server.")
        else:
            self.exec_cmd_rocket(player, msg)
        return

    @minqlx.thread
    def exec_cmd_rocket(self, player, msg):
        try:
            if len(msg) > 1:
                player = self.player_id(msg[1], player)
            p_steam_id = player.steam_id
            total = 0
            rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":rocket")
            players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]
            msg = ""
            for p in rocket:
                total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":rocket:" + str(p)])
                for pl in players:
                    if p == str(pl.steam_id):
                        count = self.db[PLAYER_KEY.format(p_steam_id) + ":rocket:" + p]
                        msg += pl.name + ": ^1" + count + "^7 "
            if total:
                self.msg("^4Air Rocket^7 Stats for {}: Total ^4Air Rocket^7 Kills: ^1{}".format(player, total))
                if msg:
                    self.msg("^4Victims^7: {}".format(msg))
            else:
                self.msg("{} has not ^4air rocket^7 killed anybody on this server.".format(player))
        except Exception as e:
            minqlx.console_print("^kills exec_cmd_rocket Exception: {}".format([e]))

    def cmd_plasma(self, player, msg, channel):
        if not self._killMonitor[4]:
                self.msg("^4Air Plasma Kill ^7stats are not enabled on this server.")
        else:
            self.exec_cmd_plasma(player, msg)
        return

    @minqlx.thread
    def exec_cmd_plasma(self, player, msg):
        try:
            if len(msg) > 1:
                player = self.player_id(msg[1], player)
            p_steam_id = player.steam_id
            total = 0
            rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":plasma")
            players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]
            msg = ""
            for p in rocket:
                total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":plasma:" + str(p)])
                for pl in players:
                    if p == str(pl.steam_id):
                        count = self.db[PLAYER_KEY.format(p_steam_id) + ":plasma:" + p]
                        msg += pl.name + ": ^1" + count + "^7 "
            if total:
                self.msg("^4Air Plasma^7 Stats for {}: Total ^4Air Plasma^7 Kills: ^1{}".format(player, total))
                if msg:
                    self.msg("^4Victims^7: {}".format(msg))
            else:
                self.msg("{} has not ^4air plasma^7 killed anybody on this server.".format(player))
        except Exception as e:
            minqlx.console_print("^kills exec_cmd_plasma Exception: {}".format([e]))

    def cmd_airrail(self, player, msg, channel):
        if not self._killMonitor[5]:
                self.msg("^4Air Rail Kill ^7stats are not enabled on this server.")
        else:
            self.exec_cmd_airrail(player, msg)
        return

    @minqlx.thread
    def exec_cmd_airrail(self, player, msg):
        try:
            if len(msg) > 1:
                player = self.player_id(msg[1], player)
            p_steam_id = player.steam_id
            total = 0
            pummels = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":airrail")
            players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]
            msg = ""
            for p in pummels:
                total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":airrail:" + str(p)])
                for pl in players:
                    if p == str(pl.steam_id):
                        count = self.db[PLAYER_KEY.format(p_steam_id) + ":airrail:" + p]
                        msg += pl.name + ": ^1" + count + "^7 "
            if total:
                self.msg("^4Air Rail^7 Stats for {}: Total ^4Air Rails^7: ^1{}".format(player, total))
                if msg:
                    self.msg("^4Victims^7: {}".format(msg))
            else:
                self.msg("{} ^7has not ^4air railed^7 anybody on this server.".format(player))
        except Exception as e:
            minqlx.console_print("^kills exec_cmd_airrail Exception: {}".format([e]))

    def cmd_telefrag(self, player, msg, channel):
        if not self._killMonitor[6]:
                self.msg("^4Telefrag Kill ^7stats are not enabled on this server.")
        else:
            self.exec_cmd_telefrag(player, msg)
        return

    @minqlx.thread
    def exec_cmd_telefrag(self, player, msg):
        try:
            if len(msg) > 1:
                player = self.player_id(msg[1], player)
            p_steam_id = player.steam_id
            total = 0
            rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":telefrag")
            players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]
            msg = ""
            for p in rocket:
                total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":telefrag:" + str(p)])
                for pl in players:
                    if p == str(pl.steam_id):
                        count = self.db[PLAYER_KEY.format(p_steam_id) + ":telefrag:" + p]
                        msg += pl.name + ": ^1" + count + "^7 "
            if total:
                self.msg("^4Telefrag^7 Stats for {}: Total ^4Telefrag^7 Kills: ^1{}".format(player, total))
                if msg:
                    self.msg("^4Victims^7: {}".format(msg))
            else:
                self.msg("{} has not ^4telefrag^7 killed anybody on this server.".format(player))
        except Exception as e:
            minqlx.console_print("^kills exec_cmd_telefrag Exception: {}".format([e]))

    def cmd_teamtelefrag(self, player, msg, channel):
        if not self._killMonitor[7]:
                self.msg("^4Team Telefrag Kill ^7stats are not enabled on this server.")
        else:
            self.exec_cmd_teamtelefrag(player, msg)
        return

    @minqlx.thread
    def exec_cmd_teamtelefrag(self, player, msg):
        try:
            if len(msg) > 1:
                player = self.player_id(msg[1], player)
            p_steam_id = player.steam_id
            total = 0
            rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":teamtelefrag")
            players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]
            msg = ""
            for p in rocket:
                total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":teamtelefrag:" + str(p)])
                for pl in players:
                    if p == str(pl.steam_id):
                        count = self.db[PLAYER_KEY.format(p_steam_id) + ":teamtelefrag:" + p]
                        msg += pl.name + ": ^1" + count + "^7 "
            if total:
                self.msg("^4Team Telefrag^7 Stats for {}: Total ^4Team Telefrag^7 Kills: ^1{}"
                         .format(player, total))
                if msg:
                    self.msg("^4Victims^7: {}".format(msg))
            else:
                self.msg("{} has not ^4team telefrag^7 killed anybody on this server.".format(player))
        except Exception as e:
            minqlx.console_print("^kills exec_cmd_teamtelefrag Exception: {}".format([e]))

    def cmd_speedkill(self, player, msg, channel):
        if not self._killMonitor[8]:
                self.msg("^4Speed Kill ^7stats are not enabled on this server.")
        else:
            self.exec_cmd_speedkill(player, msg)
        return

    @minqlx.thread
    def exec_cmd_speedkill(self, player, msg):
        try:
            if len(msg) > 1:
                player = self.player_id(msg[1], player)
            p_steam_id = player.steam_id
            total = 0
            rocket = self.db.smembers(PLAYER_KEY.format(p_steam_id) + ":speedkill")
            players = self.teams()["spectator"] + self.teams()["red"] + self.teams()["blue"] + self.teams()["free"]
            msg = ""
            for p in rocket:
                total += int(self.db[PLAYER_KEY.format(p_steam_id) + ":speedkill:" + str(p)])
                for pl in players:
                    if p == str(pl.steam_id):
                        count = self.db[PLAYER_KEY.format(p_steam_id) + ":speedkill:" + p]
                        msg += pl.name + ": ^1" + count + "^7 "
            if total:
                self.msg("^4Speed Kill^7 Stats for {}: Total ^4Speed^7 Kills: ^1{}".format(player, total))
                self.msg("^4Highest Kill Speed^7: ^3{}"
                         .format(self.db[PLAYER_KEY.format(player.steam_id) + ":highspeed"].split(".")[0]))
                if msg:
                    self.msg("^4Victims^7: {}".format(msg))
            else:
                self.msg("{} has not ^4speed^7 killed anybody on this server.".format(player))
        except Exception as e:
            minqlx.console_print("^kills exec_cmd_speedkill Exception: {}".format([e]))

    def add_killer(self, killer, method):
        try:
            if method == "GAUNTLET":
                try:
                    self._pummel[killer] += 1
                except KeyError:
                    self._pummel[killer] = 1
            elif method == "AIRGAUNTLET":
                try:
                    self._airpummel[killer] += 1
                except KeyError:
                    self._airpummel[killer] = 1
            elif method == "GRENADE":
                try:
                    self._grenades[killer] += 1
                except KeyError:
                    self._grenades[killer] = 1
            elif method == "ROCKET":
                try:
                    self._rockets[killer] += 1
                except KeyError:
                    self._rockets[killer] = 1
            elif method == "PLASMA":
                try:
                    self._plasma[killer] += 1
                except KeyError:
                    self._plasma[killer] = 1
            elif method == "AIRRAIL":
                try:
                    self._airrail[killer] += 1
                except KeyError:
                    self._airrail[killer] = 1
            elif method == "TELEFRAG":
                try:
                    self._telefrag[killer] += 1
                except KeyError:
                    self._telefrag[killer] = 1
            elif method == "TEAMTELEFRAG":
                try:
                    self._teamtelefrag[killer] += 1
                except KeyError:
                    self._teamtelefrag[killer] = 1
            elif method == "SPEED":
                try:
                    self._speed[killer] += 1
                except KeyError:
                    self._speed[killer] = 1
        except Exception as e:
            minqlx.console_print("^kills add_killer Exception: {}".format([e]))

    # called inside a thread so no need to start a thread
    def sound_play(self, path):
        try:
            for p in self.players():
                if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                    super().play_sound(path, p)
        except Exception as e:
            minqlx.console_print("^kills sound_play Exception: {}".format([e]))
        self._playing_sound = False

    def supported_games(self, player, msg, channel):
        self.msg("^4Special kills ^7are recorded on this server when playing gateypes:")
        self.msg("^3{}".format(str(SUPPORTED_GAMETYPES)))

    def kills_recorded(self, player, msg, channel):
        self.msg("^4Special kills ^7may be recorded when these kills are made:")
        self.msg("^3Pummel^7, ^3Air Gauntlet^7, ^3Direct Grenade^7, ^3Mid-Air Rocket^7,\n"
                 "^3Mid-Air Plasma^7, ^3Air Rails^7, ^3Telefrags^7, ^3Team Telefrags^7,\n"
                 " and ^3Speed Kills")
        self.msg("^6Commands^7: ^4!pummel^7, ^4!airgauntlet^7, ^4!grenades^7, ^4!rockets^7,\n"
                 " ^4!plasma^7, ^4!airrails^7, ^4!telefrag^7, ^4!teamtelefrag^7, ^4!speed^7,\n"
                 " ^4!speedlimit")

    # called inside a thread so no need to start a thread
    def player_id(self, search, player):
        target_player = None
        try:
            cid = int(search)
            if 0 <= cid <= 63 or len(search) == 17:
                try:
                    target_player = self.player(cid)
                except minqlx.NonexistentPlayerError:
                    target_player, pid = self.find_player(search)
        except ValueError:
            target_player, pid = self.find_player(search)
        except Exception as e:
            minqlx.console_print("^kills player_id Exception: {}".format([e]))
            return minqlx.RET_STOP_ALL
        if target_player == 0:
            player.tell("^1Too Many players matched your player name")
            return minqlx.RET_STOP_ALL
        elif target_player == -1 or target_player is None:
            player.tell("^1No player matching that name found")
            return minqlx.RET_STOP_ALL
        return target_player

    # called inside a thread so no need to start a thread
    # Search for a player name match using the supplied string
    def find_player(self, name):
        try:
            found_player = None
            found_count = 0
            # Remove color codes from the supplied string
            player_name = re.sub(r"\^[0-9]", "", name).lower()
            # search through the list of connected players for a name match
            for player in self.players():
                if player_name in re.sub(r"\^[0-9]", "", player.name).lower():
                    # if match is found return player, player id
                    found_player = player
                    found_count += 1
            # if only one match was found return player, player id
            if found_count == 1:
                return found_player, int(str([found_player]).split(":")[0].split("(")[1])
            # if more than one match is found return 0, -1
            elif found_count > 1:
                return 0, -1
            # if no match is found return -1, -1
            else:
                return -1, -1
        except Exception as e:
            minqlx.console_print("^1specqueue find_player Exception: {}".format([e]))

    def cmd_kills_monitor(self, player=None, msg=None, channel=None):
        try:
            self._supported_gametype = self.game.type_short in SUPPORTED_GAMETYPES
            games = self.get_cvar("qlx_killsMonitorKillTypes", int)
            binary = bin(games)[2:]
            length = len(str(binary))
            count = 0

            while length > 0:
                self._killMonitor[count] = int(binary[length - 1])
                count += 1
                length -= 1

            if player:
                player.tell("Monitor: {}".format(str(self._killMonitor)))
                return minqlx.RET_STOP_ALL
        except Exception as e:
            minqlx.console_print("^kills cmd_kills_monitor Exception: {}".format([e]))

    @minqlx.thread
    def convert_old(self):
        kill_categories = ["speedkill", "highspeed", "airpummel", "pummeled", "grenaded",
                           "rocket", "plasma", "airrail", "telefrag", "teamtelefrag"]
        for kill in kill_categories:
            for key in self.db.keys("minqlx:players:*:{}:*".format(kill)):
                split_key = key.split(":")
                if len(split_key) != 5:
                    continue
                if split_key[2][0] != "9":
                    self.db[PLAYER_KEY.format(split_key[2]) + ":" + kill + ":" + split_key[4]] = self.db[key]
                del self.db[key]
            for old in self.db.keys("minqlx:players:*:{}".format(kill)):
                del self.db[old]

    def kills_version(self, player, msg, channel):
        self.msg("^7This server is running ^4Kills^7 Version^1 {}".format(VERSION))

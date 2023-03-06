# killingspree.py by x0rnn, based on benny/bennz's kspree.lua for Enemy Territory
# Unreal Tournament sound announcements for:
#
# 	5 kills in a row: killing spree
# 	10 kills in a row: rampage
# 	15 kills in a row: dominating
# 	20 kills in a row: unstoppable
# 	25 kills in a row: godlike
# 	30 kills in a row: wicked sick
#
# 	3 kills in 3 second intervals: multikill
# 	4 kills in 4 second intervals: mega kill
# 	5 kills in 4 second intervals: ultra kill
# 	6 kills in 4 second intervals: monster kill
# 	7 kills in 4 second intervals: ludicrous kill
# 	8 kills in 4 second intervals: holy shit
#
# !spree_record will print the current map's killing spree record and the player's name
# !multikills will print your multikill stats (multikills, megakills, ultrakills, etc.)
# !clear_spree_record will clear the current map record (admins only)
#
# Use with: https://steamcommunity.com/sharedfiles/filedetails/?id=701783942
# Add 701783942 to qlx_workshopReferences and workshop.txt

import minqlx
import minqlx.database
import time
from threading import Timer
from collections import defaultdict

SPREE_KEY = "minqlx:spree:{}"
PLAYER_KEY = "minqlx:spree:players:{}"

class timer:
      def startTimer(self, n, func):
        self.stopTimer()
        self.t = Timer(n, func)
        self.t.start()

      def stopTimer(self):
        try:
            if self.t.is_alive():
                self.t.cancel()
        except:
            pass

class killingspree(minqlx.Plugin):
    def __init__(self):
        self.add_hook("death", self.handle_death)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("player_spawn", self.handle_player_spawn)
        self.add_hook("game_countdown", self.handle_game_countdown)
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("map", self.handle_map)
        self.add_command("spree_record", self.cmd_spree_record)
        self.add_command("multikills", self.cmd_multikills)
        self.add_command("clear_spree_record", self.cmd_clear_spree_record, 5)

        self.kspree = {}
        self.dspree = {}
        self.record = 0
        self.longest_spree = {}
        self.multikill = defaultdict(dict)
        self.mtime = defaultdict(dict)
        self.roundFlag = False

    def handle_player_spawn(self, player):
        if self.roundFlag:
            if str(player.steam_id) not in self.kspree:
                self.kspree[str(player.steam_id)] = 0
        else:
            self.kspree[str(player.steam_id)] = 0
        self.multikill[str(player.steam_id)]["time"] = 0
        self.multikill[str(player.steam_id)]["frag_num"] = 0
        self.multikill[str(player.steam_id)]["timer"] = timer()
        try:
            del self.mtime[str(player.steam_id)]
        except KeyError:
            return

    def handle_game_countdown(self):
        self.kspree.clear()
        self.dspree.clear()
        self.longest_spree.clear()

    def handle_round_countdown(self, round_number):
        self.roundFlag = True

    def handle_player_disconnect(self, player, reason):
        if str(player.steam_id) in self.kspree:
            self.kspree[str(player.steam_id)] = 0
        if str(player.steam_id) in self.dspree:
            self.dspree[str(player.steam_id)] = 0
        try:
            del self.multikill[str(player.steam_id)]
            del self.mtime[str(player.steam_id)]
        except KeyError:
            return

    def handle_game_end(self, data):
        map_name = self.game.map.lower()
        for pl in self.players():
            if pl.team != "spectator":
                if str(pl.steam_id) in self.kspree and self.kspree[str(pl.steam_id)] >= 5:
                    if self.kspree[str(pl.steam_id)] > self.record:
                        self.db.zadd(SPREE_KEY.format(map_name), self.kspree[str(pl.steam_id)], "{},{}".format(pl.steam_id, int(time.time())))
                        self.record = self.kspree[str(pl.steam_id)]
                        if not self.longest_spree:
                            self.longest_spree = {'name': pl.name, 'ks': self.kspree[str(pl.steam_id)]}
                        else:
                            if self.kspree[str(pl.steam_id)] > self.longest_spree['ks']:
                                self.longest_spree = {'name': pl.name, 'ks': self.kspree[str(pl.steam_id)]}
                        msg = "{}'s killing spree ended (^1{} ^7kills) by end of game.".format(pl.name, self.kspree[str(pl.steam_id)])
                        self.msg(msg)
                        self.msg("This is a new map record!")
                    else:
                        if not self.longest_spree:
                            self.longest_spree = {'name': pl.name, 'ks': self.kspree[str(pl.steam_id)]}
                        else:
                            if self.kspree[str(pl.steam_id)] > self.longest_spree['ks']:
                                self.longest_spree = {'name': pl.name, 'ks': self.kspree[str(pl.steam_id)]}
                        msg = "{}'s killing spree ended (^1{} ^7kills) by end of game.".format(pl.name, self.kspree[str(pl.steam_id)])
                        self.msg(msg)

        if self.longest_spree:
            spree = self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True)
            spree_record = int(spree[0][1])
            steam_id = spree[0][0].split(",")
            name = self.db.lindex("minqlx:players:{}".format(steam_id[0]), 0)
            self.msg("Longest killing spree: {}, ^1{} ^7kills. Record: {}, ^1{} ^7kills.".format(self.longest_spree['name'], self.longest_spree['ks'], name, spree_record))
        self.kspree.clear()
        self.dspree.clear()
        self.longest_spree.clear()

    def handle_map(self, map_name, factory):
        if self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True):
            self.record = int(self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True)[0][1])
        else:
            self.record = 0

    def handle_death(self, victim, killer, data):
        if self.game.state != 'in_progress':
            return
        else:
            map_name = self.game.map.lower()
            def checkKSpree(id, name):
                players = self.players()
                if self.kspree[id] % 5 == 0:
                    spree_id = self.kspree[id]
                    if spree_id == 5:
                        spree_msg = "is on a killing spree!"
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/killingspree.wav", p)
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id == 10:
                        spree_msg = "is on a rampage!"
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/rampage.wav", p)
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id == 15:
                        spree_msg = "is dominating!"
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/dominating.wav", p)
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id == 20:
                        spree_msg = "is unstoppable!"
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/unstoppable.wav", p)
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id == 25:
                        spree_msg = "is godlike!"
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/godlike.wav", p)
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id >= 30:
                        spree_msg = "is wicked sick!"
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/wickedsick.wav", p)
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)

            def checkKSpreeEnd(id, v_name, k_name, normal_kill):
                if id in self.kspree and self.kspree[id] >= 5:
                    if normal_kill:
                        if self.kspree[id] > self.record:
                            self.db.zadd(SPREE_KEY.format(map_name), self.kspree[id], "{},{}".format(id, int(time.time())))
                            self.record = self.kspree[id]
                            msg = "{}'s killing spree ended (^1{} ^7kills), killed by {}.".format(v_name, self.kspree[id], k_name)
                            self.msg(msg)
                            self.msg("This is a new map record!")
                        else:
                            msg = "{}'s killing spree ended (^1{} ^7kills), killed by {}.".format(v_name, self.kspree[id], k_name)
                            self.msg(msg)
                    else:
                        if data['KILLER'] is None:
                            if self.kspree[id] > self.record:
                                self.db.zadd(SPREE_KEY.format(map_name), self.kspree[id], "{},{}".format(id, int(time.time())))
                                self.record = self.kspree[id]
                                msg = "{}'s killing spree ended (^1{} ^7kills), killed by the world.".format(v_name, self.kspree[id])
                                self.msg(msg)
                                self.msg("This is a new map record!")
                            else:
                                msg = "{}'s killing spree ended (^1{} ^7kills), killed by the world.".format(v_name, self.kspree[id])
                                self.msg(msg)
                        if data['MOD'] == "SWITCHTEAM":
                            if self.kspree[id] > self.record:
                                self.db.zadd(SPREE_KEY.format(map_name), self.kspree[id], "{},{}".format(id, int(time.time())))
                                self.record = self.kspree[id]
                                msg = "{}'s killing spree ended (^1{} ^7kills) by teamswitch.".format(v_name, self.kspree[id])
                                self.msg(msg)
                                self.msg("This is a new map record!")
                            else:
                                msg = "{}'s killing spree ended (^1{} ^7kills) by teamswitch.".format(v_name, self.kspree[id])
                                self.msg(msg)
                        if v_name == k_name:
                            if self.kspree[id] > self.record:
                                self.db.zadd(SPREE_KEY.format(map_name), self.kspree[id], "{},{}".format(id, int(time.time())))
                                self.record = self.kspree[id]
                                msg = "{}'s killing spree ended (^1{} ^7kills), died by suicide.".format(v_name, self.kspree[id])
                                self.msg(msg)
                                self.msg("This is a new map record!")
                            else:
                                msg = "{}'s killing spree ended (^1{} ^7kills), died by suicide.".format(v_name, self.kspree[id])
                                self.msg(msg)
                        else:
                            if self.kspree[id] > self.record:
                                self.db.zadd(SPREE_KEY.format(map_name), self.kspree[id], "{},{}".format(id, int(time.time())))
                                self.record = self.kspree[id]
                                msg = "{}'s killing spree ended (^1{} ^7kills), teamkilled by {}.".format(v_name, self.kspree[id], k_name)
                                self.msg(msg)
                                self.msg("This is a new map record!")
                            else:
                                msg = "{}'s killing spree ended (^1{} ^7kills), teamkilled by {}.".format(v_name, self.kspree[id], k_name)
                                self.msg(msg)
                    if not self.longest_spree:
                        self.longest_spree = {'name': v_name, 'ks': self.kspree[id]}
                    else:
                        if self.kspree[id] > self.longest_spree['ks']:
                            self.longest_spree = {'name': v_name, 'ks': self.kspree[id]}
                self.kspree[id] = 0

            def checkDSpree(id, name):
                if self.dspree[id] % 5 == 0:
                    spree_id = self.dspree[id]
                    if spree_id == 10:
                        msg = "{} is having a bad day, ^1{} ^7deaths without a kill!".format(name, self.dspree[id])
                        self.msg(msg)
                    elif spree_id >= 15:
                        msg = "{} is really getting his ass kicked, ^1{} ^7deaths without a kill!".format(name, self.dspree[id])
                        self.msg(msg)

            def delay_announce(id):
                def playit():
                    players = self.players()
                    k_name = data['KILLER']['NAME']
                    frags = self.multikill[id]["frag_num"]
                    if frags == 3:
                        self.player(int(id)).center_print("^1Multikill!")
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/multikill.wav", p)
                        self.msg("!!! ^1Multi kill ^7> {} < ^1Multi kill ^7!!! ({} kills in {}s)".format(k_name, frags, round(self.mtime[id][2] - self.mtime[id][0])))
                    elif frags == 4:
                        self.player(int(id)).center_print("^1Mega kill!")
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/megakill.ogg", p)
                        self.msg("!!! ^1Mega kill ^7> {} < ^1Mega kill ^7!!! ({} kills in {}s)".format(k_name, frags, round(self.mtime[id][3] - self.mtime[id][0])))
                    elif frags == 5:
                        self.player(int(id)).center_print("^1ULTRA KILL!")
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/ultrakill.ogg", p)
                        self.msg("!!! ^1ULTRA KILL ^7> {} < ^1ULTRA KILL ^7!!! ({} kills in {}s)".format(k_name, frags, round(self.mtime[id][4] - self.mtime[id][0])))
                    elif frags == 6:
                        self.player(int(id)).center_print("^1MONSTER KILL!")
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/monsterkill.wav", p)
                        self.msg("!!! ^1MONSTER KILL ^7> {} < ^1MONSTER KILL^7!!! ({} kills in {}s)".format(k_name, frags, round(self.mtime[id][5] - self.mtime[id][0])))
                    elif frags == 7:
                        self.player(int(id)).center_print("^1LUDICROUS KILL!")
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/ludicrouskill.wav", p)
                        self.msg("!!! ^1LUDICROUS KILL ^7> {} < ^1LUDICROUS KILL ^7!!! ({} kills in {}s)".format(k_name, frags, round(self.mtime[id][6] - self.mtime[id][0])))
                    elif frags >= 8:
                        self.player(int(id)).center_print("^1H O L Y  S H I T!")
                        for p in players:
                            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                                self.play_sound("sound/misc/holyshit.wav", p)
                        self.msg("!!! ^1 H O L Y  S H I T ^7> {} < ^1H O L Y  S H I T ^7!!! ({} kills in {}s)".format(k_name, frags, round(self.mtime[id][7] - self.mtime[id][0])))
                return playit

            def checkMultiKill(id, k_name):
                 t = self.multikill[id]["timer"]
                 current_time = time.time()
                 multikill_threshold_time = current_time - self.multikill[id]["time"]
                 if multikill_threshold_time <= 4:
                     t.stopTimer()
                     self.multikill[id]["frag_num"] = self.multikill[id]["frag_num"] + 1
                     self.mtime[id].update({self.multikill[id]["frag_num"] - 1:time.time()})
                     if multikill_threshold_time <= 3:
                         if self.multikill[id]["frag_num"] == 3:
                             t.startTimer(4.1, delay_announce(id))
                             if not self.db.lrange(PLAYER_KEY.format(id) + ":multikills", 0, -1):
                                 self.db.lpush(PLAYER_KEY.format(id) + ":multikills", 0, 0, 0, 0, 0, 0)
                                 mk = 0
                             else:
                                 mk = int(self.db.lindex(PLAYER_KEY.format(id) + ":multikills", 0))
                             mk = mk + 1
                             self.db.lset(PLAYER_KEY.format(id) + ":multikills", 0, mk)
                     if 4 <= self.multikill[id]["frag_num"] <= 8:
                         t.startTimer(4.1, delay_announce(id))
                         if not self.db.lrange(PLAYER_KEY.format(id) + ":multikills", 0, -1):
                             self.db.lpush(PLAYER_KEY.format(id) + ":multikills", 0, 0, 0, 0, 0, 0)
                             mk = 0
                         else:
                             mk = int(self.db.lindex(PLAYER_KEY.format(id) + ":multikills", self.multikill[id]["frag_num"] - 3))
                         mk = mk + 1
                         self.db.lset(PLAYER_KEY.format(id) + ":multikills", self.multikill[id]["frag_num"] - 3, mk)
                     elif self.multikill[id]["frag_num"] > 8:
                         t.startTimer(4.1, delay_announce(id))
                         mk = int(self.db.lindex(PLAYER_KEY.format(id) + ":multikills", 5))
                         mk = mk + 1
                         self.db.lset(PLAYER_KEY.format(id) + ":multikills", 5, mk)
                 else:
                     self.multikill[id]["frag_num"] = 1
                     try:
                         del self.mtime[id]
                     except KeyError:
                         pass
                     self.mtime[id][0] = time.time()
                 self.multikill[id]["time"] = time.time()

            v_id = data['VICTIM']['STEAM_ID']
            v_name = data['VICTIM']['NAME']
            t = timer()

            if data['SUICIDE']: #team switch
                if data['MOD'] == "SWITCHTEAM":
                    checkKSpreeEnd(v_id, v_name, "switchteam", False)
                    if v_id in self.dspree:
                        if self.dspree[v_id] != 0:
                            self.dspree[v_id] = 0
                else: #selfkill
                    checkKSpreeEnd(v_id, v_name, v_name, False)
                    if v_id not in self.dspree:
                        if v_id != "0":
                            self.dspree[v_id] = 1
                    else:
                        self.dspree[v_id] = self.dspree[v_id] + 1
                        checkDSpree(v_id, v_name)
                return

            if data['KILLER'] is not None and not data['TEAMKILL']: #normal kill
                k_id = data['KILLER']['STEAM_ID']
                k_name = data['KILLER']['NAME']
                if k_id != "0": #ignore bots
                    self.kspree[k_id] = self.kspree[k_id] + 1
                    checkKSpree(k_id, k_name)
                    checkMultiKill(k_id, k_name)
                checkKSpreeEnd(v_id, v_name, k_name, True)
                if k_id in self.dspree:
                    if self.dspree[k_id] != 0:
                        self.dspree[k_id] = 0
                if v_id not in self.dspree:
                    if v_id != "0":
                        self.dspree[v_id] = 1
                else:
                    self.dspree[v_id] = self.dspree[v_id] + 1
                    checkDSpree(v_id, v_name)

            elif data['TEAMKILL']: #teamkill
                k_name = data['KILLER']['NAME']
                checkKSpreeEnd(v_id, v_name, k_name, False)

            elif data['KILLER'] is None: #killed by world
                checkKSpreeEnd(v_id, v_name, "world", False)
                if v_id not in self.dspree:
                    if v_id != "0":
                        self.dspree[v_id] = 1
                else:
                    self.dspree[v_id] = self.dspree[v_id] + 1
                    checkDSpree(v_id, v_name)

    def cmd_spree_record(self, player, msg, channel):
        map_name = self.game.map.lower()
        if self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True):
            spree = self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True)
            spree_record = int(spree[0][1])
            steam_id = spree[0][0].split(",")
            name = self.db.lindex("minqlx:players:{}".format(steam_id[0]), 0)
            msg = "Killing spree record for map '{}': ^1{} ^7kills by {}.".format(map_name, spree_record, name)
            self.msg(msg)
        else:
            self.msg("There is no killing spree record for map '" + map_name + "' yet.")

    def cmd_clear_spree_record(self, player, msg, channel):
        map_name = self.game.map.lower()
        del self.db[SPREE_KEY.format(map_name)]
        self.record = 0
        channel.reply("Killing spree record for map '{}' was cleared.".format(map_name))

    def cmd_multikills(self, player, msg, channel):
        if self.db.lrange(PLAYER_KEY.format(player.steam_id) + ":multikills", 0, -1):
            multikills = self.db.lrange(PLAYER_KEY.format(player.steam_id) + ":multikills", 0, -1)
            self.msg(player.name + " has made: " + multikills[0][0] + " multi, " + multikills[1][0] + " mega, " + multikills[2][0] + " ultra, "
                     + multikills[3][0] + " monster, " + multikills[4][0] + " ludicrous, " + multikills[5][0] + " holy shit kills.")
        else:
            self.msg(player.name + " has made no multikills yet.")

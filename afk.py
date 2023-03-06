# This is a plugin created by iouonegirl(@gmail.com)
# Copyright (c) 2016 iouonegirl
# https://github.com/dsverdlo/minqlx-plugins
#
# You are free to modify this plugin to your custom,
# except for the version command related code.
#
# Its purpose is to detect afk players and provide actions
# to be taken on them. For now only working in team-based
# gametypes.
#
# Uses:
# - qlx_afk_warning_seconds "10"
# - qlx_afk_detection_seconds "20"
# - qlx_afk_put_to_spec "1"


import minqlx
import threading
import time
import os
import requests

VERSION = "v0.15"

VAR_WARNING = "qlx_afk_warning_seconds"
VAR_DETECTION = "qlx_afk_detection_seconds"
VAR_PUT_SPEC = "qlx_afk_put_to_spec"

# Interval for the thread to update positions. Default = 0.33
interval = 0.33

# This code makes sure the required superclass is loaded automatically
try:
    from .iouonegirl import iouonegirlPlugin
except:
    try:
        abs_file_path = os.path.join(os.path.dirname(__file__), "iouonegirl.py")
        res = requests.get("https://raw.githubusercontent.com/dsverdlo/minqlx-plugins/master/iouonegirl.py")
        if res.status_code != requests.codes.ok: raise
        with open(abs_file_path,"a+") as f: f.write(res.text)
        from .iouonegirl import iouonegirlPlugin
    except Exception as e :
        minqlx.CHAT_CHANNEL.reply("^1iouonegirl abstract plugin download failed^7: {}".format(e))
        raise

# Start plugin
class afk(iouonegirlPlugin):

    def __init__(self):
        super().__init__(self.__class__.__name__, VERSION)

        # Set required cvars once. DONT EDIT THEM HERE BUT IN SERVER.CFG
        self.set_cvar_once(VAR_WARNING, "10")
        self.set_cvar_once(VAR_DETECTION, "20")
        self.set_cvar_once(VAR_PUT_SPEC, "1")

        # Get required cvars
        self.warning = int(self.get_cvar(VAR_WARNING))
        self.detection = int(self.get_cvar(VAR_DETECTION))
        self.put_to_spec = int(self.get_cvar(VAR_PUT_SPEC))

        # steamid : [position, seconds]
        self.positions = {}

        # keep looking for AFK players
        self.running = False

        # punished players
        self.punished = []

        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)
        self.add_hook("team_switch", self.handle_player_switch)
        self.add_hook("unload", self.handle_unload)
        self.add_hook("death", self.handle_death)





    def handle_unload(self, plugin):
        if plugin == self.__class__.__name__:
            self.running = False
            self.punished = []

    def handle_round_start(self, round_number):
        teams = self.teams()
        for p in teams['red'] + teams['blue']:
            self.positions[p.steam_id] = [self.help_get_pos(p), 0]

        self.punished = []

        # start checking thread
        self.running = True
        self.help_create_thread()

    def handle_round_end(self, round_number):
        self.running = False
        self.punished = []

    def handle_player_switch(self, player, old, new):
        if new == 'spectator':
            if player.steam_id in self.positions:
                del self.positions[player.steam_id]
            if player in self.punished:
                self.punished.remove(player)

        if new in ['red', 'blue']:
            self.positions[player.steam_id] = [self.help_get_pos(player), 0]

    @minqlx.thread
    def help_create_thread(self):
        while self.running and self.game and self.game.state == 'in_progress':
            teams = self.teams()
            for p in teams['red'] + teams['blue']:
                pid = p.steam_id

                if not p.is_alive: continue

                if pid not in self.positions:
                    self.positions[pid] = [self.help_get_pos(p), 0]

                prev_pos, secs = self.positions[pid]
                curr_pos = self.help_get_pos(p)

                # If position stayed the same, add the time difference and check for thresholds
                if prev_pos == curr_pos:
                    self.positions[pid] = [curr_pos, secs+interval]
                    if secs+interval >= self.warning and secs < self.warning:
                        self.help_warn(p)
                    elif secs+interval >= self.detection and secs < self.detection:
                        self.help_detected_print(p)
                else:
                    self.positions[pid] = [curr_pos, 0]
                    if p in self.punished:
                        # if the player started moving, remove him from punished players
                        self.punished.remove(p)

            time.sleep(interval)

    def handle_death(self, victim, killer, data):
        if victim in self.punished:
            self.punished.remove(victim)
        if victim.steam_id in self.positions:
            del self.positions[victim.steam_id]

    @minqlx.next_frame
    def help_warn(self, player):
        message = "You have been inactive for {} seconds...".format(self.warning)
        minqlx.send_server_command(player.id, "cp \"\n\n\n{}\"".format(message))

    @minqlx.next_frame
    def help_detected_print(self, player):
        self.msg("^1{} ^1has been inactive for {} seconds! Commencing punishment!".format(player.name, int(self.positions[player.steam_id][1])))
        self.punished.append(player)
        self.punish(player)


    @minqlx.thread
    def punish(self, player, pain=10, wait=0.5):
        @minqlx.next_frame
        def spec(_p): _p.put('spectator')
        @minqlx.next_frame
        def subtract_health(_p, _h): _p.health -= _h

        while self.game and self.game.state == 'in_progress' and player in self.punished:
            if not player.is_alive or player.health < pain:
                self.punished.remove(player)
                if self.put_to_spec: spec(player)
                break

            subtract_health(player, pain)
            if player.steam_id in self.positions:
                s = int((self.positions[player.steam_id])[1])
            else:
                s = self.detection
            message = "^1Inactive for {} seconds! \n\n^7Move or keep getting damage!".format(s)
            minqlx.send_server_command(player.id, "cp \"\n\n\n{}\"".format(message))
            time.sleep(wait)


        return


    def help_get_pos(self, player):
        return player.position()
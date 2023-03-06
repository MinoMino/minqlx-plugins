# This is a plugin created by iouonegirl(@gmail.com)
# Copyright (c) 2016 iouonegirl
# https://github.com/dsverdlo/minqlx-plugins
#
# You are free to modify this plugin to your custom,
# except for the version command related code.
#
# It provides a method to !print something in the center of a player's screen,
# or !broadcast it over the whole server (print on everybody's screen)
# and a toggle command (!showlast) to view when there is only one enemy left
#
# Uses
# - qlx_cp_message "One enemy left. Start the hunt"


import minqlx
import datetime
import time
import re
import requests

VERSION = "v0.7"

PLAYER_KEY = "minqlx:players:{}"
NOTIFY_LAST_KEY = PLAYER_KEY + ":notifylast"

class centerprint(minqlx.Plugin):
    def __init__(self):
        super().__init__()

        # Set required cvars once. EDIT THIS IN THE SERVER.CFG
        self.set_cvar_once("qlx_cp_message", "One enemy left. Start the hunt")

        self.add_command(("print", "pprint", "cprint", "centerprint"), self.cmd_center_print, 3, usage="<name>|<id> <message>")
        self.add_command("broadcast", self.cmd_broadcast, 3)
        self.add_command("showlast", self.cmd_toggle_pref)
        self.add_command("v_centerprint", self.cmd_version)
        self.add_hook("death", self.handle_death)
        self.add_hook("player_connect", self.handle_player_connect)

    def handle_player_connect(self, player):
        if self.db.has_permission(player, 5):
            self.check_version(player=player)

    def cmd_version(self, player, msg, channel):
        self.check_version(channel=channel)

    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/dsverdlo/minqlx-plugins/master/{}.py".format(self.__class__.__name__)
        res = requests.get(url)
        last_status = res.status_code
        if res.status_code != requests.codes.ok: return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                # If called manually and outdated
                if channel and VERSION.encode() != line:
                    channel.reply("^7Currently using ^3iou^7one^4girl^7's ^6{}^7 plugin ^1outdated^7 version ^6{}^7.".format(self.__class__.__name__, VERSION))
                # If called manually and alright
                elif channel and VERSION.encode() == line:
                    channel.reply("^7Currently using ^3iou^7one^4girl^7's latest ^6{}^7 plugin version ^6{}^7.".format(self.__class__.__name__, VERSION))
                # If routine check and it's not alright.
                elif player and VERSION.encode() != line:
                    time.sleep(15)
                    try:
                        player.tell("^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and you're using ^6{}^7!".format(self.__class__.__name__, line.decode(), VERSION))
                    except Exception as e: minqlx.console_command("echo {}".format(e))
                return
    def cmd_broadcast(self, player, msg, channel):
        for p in self.players():
            message = " ".join(msg[1:])
            minqlx.send_server_command(p.id, "cp \"\n\n\n{}\"".format(message))
        player.tell("^6Psst^7: Broadcast successful: '{}'".format(message))

    def cmd_center_print(self, player, msg, channel):
        if len(msg) < 3:
            return minqlx.RET_USAGE

        target = self.find_by_name_or_id(player, msg[1])
        if not target:
            return minqlx.RET_STOP_ALL

        message = " ".join(msg[2:])
        minqlx.send_server_command(target.id, "cp \"\n\n\n{}\"".format(message))
        player.tell("^6Psst^7: succesfully printed '{}' on {}'s screen.".format(message, target.name))
        return minqlx.RET_STOP_ALL

    def handle_death(self, victim, killer, data):
        _vic = self.find_player(victim.name)[0]
        _vic_team = _vic.team

        if data['MOD'] == 'SWITCHTEAM':
            _vic_team == "red" if data['VICTIM']['TEAM'] == 2 else "blue"

        if self.game and self.game.state == 'in_progress':
            teams = self.teams()

            if int(data['TEAM_ALIVE']) == 1: # viewpoint of victim
                for _p in teams["red" if _vic_team == "blue" else "blue"]:
                    if self.get_notif_pref(_p.steam_id):
                        minqlx.send_server_command(_p.id, "cp \"\n\n\n{}!\"".format(self.get_cvar("qlx_cp_message")))



    def cmd_toggle_pref(self, player, msg, channel):
        if len(msg) > 2:
            return minqlx.RET_USAGE

        self.set_notif_pref(player.steam_id)

        if self.get_notif_pref(player.steam_id):
            channel.reply("^7{} will now see a message if there is only 1 enemy left.".format(player.name))
        else:
            channel.reply("^7{} will stop seeing '1 enemy left' messages.".format(player.name))


    # ====================================================================
    #                               HELPERS
    # ====================================================================

    def get_notif_pref(self, sid):
        try:
            return int(self.db[NOTIFY_LAST_KEY.format(sid)])
        except:
            return False

    def set_notif_pref(self, sid):
        self.db[NOTIFY_LAST_KEY.format(sid)] = 0 if self.get_notif_pref(sid) else 1



    def find_by_name_or_id(self, player, target):
        # Find players returns a list of name-matching players
        def find_players(query):
            players = []
            for p in self.find_player(query):
                if p not in players:
                    players.append(p)
            return players

        # Tell a player which players matched
        def list_alternatives(players, indent=2):
            player.tell("A total of ^6{}^7 players matched for {}:".format(len(players),target))
            out = ""
            for p in players:
                out += " " * indent
                out += "{}^6:^7 {}\n".format(p.id, p.name)
            player.tell(out[:-1])

        # Get the list of matching players on name
        target_players = find_players(target)

        # even if we get only 1 person, we need to check if the input was meant as an ID
        # if we also get an ID we should return with ambiguity

        try:
            i = int(target)
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
            # Add the found ID if the player was not already found
            if not target_player in target_players:
                target_players.append(target_player)
        except ValueError:
            pass

        # If there were absolutely no matches
        if not target_players:
            player.tell("Sorry, but no players matched your tokens: {}.".format(target))
            return None

        # If there were more than 1 matches
        if len(target_players) > 1:
            list_alternatives(target_players)
            return None

        # By now there can only be one person left
        return target_players.pop()

# This is a plugin created by iouonegirl(@gmail.com)
# Copyright (c) 2016 iouonegirl
# https://github.com/dsverdlo/minqlx-plugins
#
# You are free to modify this plugin to your custom,
# except for the version command related code.
#
# Thanks to Minkyn for his assistance in this plugin.
#
# Its purpose if to force the last player to spectate
# Algorithm: http://i.imgur.com/8P60gRq.png
#
# Uses:
# set qlx_autospec_minplayers "2"
# set qlx_autospec_maxplayers "999"
#     ^ The autospec algorithm will only work for #players within this interval

import minqlx
import requests
import itertools
import threading
import random
import time
import os
import re

VERSION = "v0.19"

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


class autospec(iouonegirlPlugin):
    def __init__(self):
        super().__init__(self.__class__.__name__, VERSION)

        self.jointimes = {}

        self.set_cvar_once("qlx_autospec_minplayers", "2")
        self.set_cvar_once("qlx_autospec_maxplayers", "999")

        self.add_hook("round_countdown", self.handle_round_count)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("player_connect", self.handle_player_connect)
        self.add_hook("player_disconnect", self.handle_player_disconnect)


    def handle_player_connect(self, player):
        self.jointimes[player.steam_id] = time.time()


    def handle_player_disconnect(self, player, reason):
        if player.steam_id in self.jointimes:
            del self.jointimes[player.steam_id]


    def find_time(self, player):
        if not (player.steam_id in self.jointimes):
            self.jointimes[player.steam_id] = time.time()
        return self.jointimes[player.steam_id]


    # When a round starts counting down, we check some conditions
    # and show a comforting message about how we will balance the
    # teams before the round starts
    def handle_round_count(self, round_number):

        # Grab the teams and amount of players in each team
        teams = self.teams()
        player_count = len(teams["red"] + teams["blue"])

        # If not enough players to balance...
        if player_count < self.get_cvar("qlx_autospec_minplayers", int):
            return

        # if so many players that we don't care
        if player_count > self.get_cvar("qlx_autospec_maxplayers", int):
            return

        diff = len(teams['red']) - len(teams['blue'])
        to, fr = ['blue', 'red'] if diff > 0 else ['red','blue']
        last = self.help_get_last()
        n = int(abs(diff) / 2) # amount of players that will be switched

        # If there is a difference in teams of more or equal than 1,
        # Display what is going to happen
        if abs(diff) >= 1:
            if self.is_even(diff):
                n = last.name if n == 1 else "{} players".format(n)
                self.msg("^6Uneven teams detected!^7 Server will move {} to {}".format(n, to))
            else:
                m = 'lowest player' if n == 1 else '{} lowest players'.format(n)
                m = " and move the {} to {}".format(m, to) if n else ''
                self.msg("^6Uneven teams detected!^7 Server will auto spec {}{}.".format(last.name, m))

        # Start counting (in a thread) to just before a round and then balance
        # So that switched players can still participate in the coming round
        self.balance_before_start(round_number)


    # To be sure no one joined in the last millisecond, or in the case that
    # there was no round delay, check again on round start
    def handle_round_start(self, round_number):
        self.balance_before_start(round_number, True)


    # Wait until just before the round starts and then balance
    @minqlx.thread
    def balance_before_start(self, roundnumber, direct = False):

        # Wait until round almost starts
        countdown = int(self.get_cvar('g_roundWarmupDelay'))
        if self.game.type_short == "ft":
            countdown = int(self.get_cvar('g_freezeRoundDelay'))
        if not direct: time.sleep(max(countdown / 1000 - 0.3, 0))

        # Do the thing (game logic) in next frame
        self.balance_before_start_next_frame()


    # Move players around, make the teams even
    @minqlx.next_frame
    def balance_before_start_next_frame(self):

        def red_min_blue():
            t = self.teams()
            return len(t['red']) - len(t['blue'])

        # Grab the teams
        teams = self.teams()
        player_count = len(teams["red"] + teams["blue"])

        # If it is the last player, don't do this and let the game finish normally
        if player_count == 1:
            return

        # If there are less people than wanted, ignore
        if player_count < self.get_cvar("qlx_autospec_minplayers", int):
            return

        # If there are so many players that we don't care:
        if player_count > self.get_cvar("qlx_autospec_maxplayers", int):
            return

        # While there is a difference in teams of more or equal than 1
        while abs(red_min_blue()) >= 1:
            last = self.help_get_last()
            diff = red_min_blue()

            if self.is_even(diff): # one team has an even amount of people more than the other

                to, fr = ['blue','red'] if diff > 0 else ['red', 'blue']
                last.put(to)
                self.msg("^6Uneven teams action^7: Moved {} from {} to {}".format(last.name, fr, to))

            else:

                last.put("spectator")
                self.msg("^6Uneven teams action^7: {} was moved to spec to even teams!".format(last.name))



    # Returns the last player of the team with the largest amount of players
    # Sorted by score. If lowest score is equal, look at jointimes.
    def help_get_last(self):

        teams = self.teams()

        # See which team is bigger than the other
        if len(teams["red"]) < len(teams["blue"]):
            bigger_team = teams["blue"].copy()
        else:
            bigger_team = teams["red"].copy()

        if (self.game.red_score + self.game.blue_score) >= 1:
            minqlx.console_command("echo Autospec: Picking someone to spec based on join times.")
            bigger_team.sort(key = lambda el: self.find_time(el), reverse=True)
            lowest_player = bigger_team[0]
            
        else:

            minqlx.console_command("echo Autospec: Picking someone to spec based on score")
            # Get the last person in that team
            lowest_players = [bigger_team[0]]

            for p in bigger_team:
                if p.stats.score < lowest_players[0].stats.score:
                    lowest_players = [p]
                elif p.stats.score == lowest_players[0].stats.score:
                    lowest_players.append(p)

            # Sort on joining times highest(newest) to lowest(oldest)
            lowest_players.sort(key= lambda el: self.find_time(el), reverse=True )
            lowest_player = lowest_players[0]

        minqlx.console_command("echo Autospec: Picked {} from the {} team.".format(lowest_player.name, lowest_player.team))
        return lowest_player



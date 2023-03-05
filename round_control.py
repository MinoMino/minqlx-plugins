# minqlx - A Quake Live server administrator bot.
# Copyright (C) 2015 Mino <mino@minomino.org>

# This file is part of minqlx.

# minqlx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# minqlx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# Script blocks new players to join the game after ## rounds has been passed.
# Allow players to callvote unlock to let spectators to join.

import minqlx

LOCKED = False
ROUND_COUNT = 5
SUPPORTED_GAMETYPES = ("ad", "ca", "ctf", "dom", "ft", "tdm")

class round_control(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("player_join", self.handle_player_join)
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("vote_ended", self.handle_vote_ended)

        self.add_command(("unlockteams"), self.cmd_unlockteams, 5)
        self.add_command(("lockteams"), self.cmd_lockteams, 5)

        self.set_cvar_once("qlx_minRoundsToLock", "5") # minimum rounds to block new players to join

    def handle_vote_ended(self, votes, vote, args, passed):   
        if passed == True and vote.lower() == "unlockteams":
            gt = self.game.type_short
            if gt not in SUPPORTED_GAMETYPES:
                return

            @minqlx.delay(3.5)
            def f():
                if LOCKED == True:
                    LOCKED = False
                    self.unlock()
                    self.msg("Teams were ^6UNLOCKED^7. Spectators are allowed to join.")
                    return
            f()

    def cmd_lockteams(self, player, msg, channel):
        teams = self.teams()
        players = teams["red"] + teams["blue"]
        if players % 2 != 0:
            self.msg("Teams were ^6NOT^7 balanced due to the total number of players being an odd number.")
            return
        
        self.game.teamsize = teams["red"]
        self.lock()
        LOCKED = True
        self.msg("Teams has been ^6LOCKED^7.")
    
    def cmd_unlockteams(self, player, msg, channel):
        teams = self.teams()
        players = teams["red"]
        self.game.teamsize = teams["red"] + 1
        LOCKED = False
        self.unlock()
        self.msg("Teams were ^6UNLOCKED^7. Spectators are allowed to join.")
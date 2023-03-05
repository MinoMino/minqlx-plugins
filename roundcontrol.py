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

import minqlx
import itertools

LOCKED = False
ROUND_COUNT = 0
SUPPORTED_GAMETYPES = ("ad", "ca", "ctf", "dom", "ft", "tdm")

class roundcontrol(minqlx.Plugin):
    #####
    # Script blocks new players to join the game after ## rounds has been passed.
    # Allow players to callvote unlock to let spectators to join.
    #####

    def __init__(self):
        super().__init__()
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("vote_ended", self.handle_vote_ended)

        self.add_command(("unlockteams"), self.cmd_unlockteams, 5)
        self.add_command(("lockteams"), self.cmd_lockteams, 5)
        self.add_command(("lockstatus"), self.cmd_lockstatus, 1)

        self.set_cvar_once("qlx_minRoundsToLock", "5") # minimum rounds to block new players to join

    def handle_round_start(self):
        self.msg("Round count {}".format(ROUND_COUNT))
        ROUND_COUNT = ROUND_COUNT + 1

        if ROUND_COUNT >= 5:
            self.msg("Game reach round count of {}. ^6Locking teams.".format(self.get_cvar("qlx_minRoundsToLock")))
            return
    
    def handle_vote_called(self, caller, vote, args):
        if vote.lower() == "unlockteams" and LOCKED == False:
            caller.tell("Teams are alread unlocked.")
            return
    
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
                    self.msg("Teams were ^3UNLOCKED^7. Spectators are allowed to join.")
                    return
            f()

    def cmd_lockteams(self, player, msg, channel):
        player.tell("Trying to ^1lock teams.")
        teams = self.teams()
        players = teams["red"] + teams["blue"]
        if players % 2 != 0:
            self.msg("Teams were ^3NOT^7 balanced. Not possible to lock teams.")
            return
        
        n = int(teams["red"])
        self.game.teamsize = n
        self.lock()
        LOCKED = True
        self.msg("Teams has been ^6LOCKED^7.")
    
    def cmd_unlockteams(self, player, msg, channel):
        player.tell("Trying to ^3unlock teams.")
        teams = self.teams()
        players = teams["red"]
        self.game.teamsize = teams["red"] + 1
        self.unlock()
        LOCKED = False
        self.msg("Teams were ^3UNLOCKED^7. Spectators are allowed to join.")

    def cmd_lockstatus(self, player, msg, channel):
        if LOCKED:
            player.tell("Teams are ^1LOCKED^7.")
        else:
            player.tell("Teams are ^3UNLOCKED^7.")
    
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

SUPPORTED_GAMETYPES = ("ad", "ca", "ctf", "dom", "ft", "tdm")

class roundcontrol(minqlx.Plugin):
    #####
    # Script blocks new players to join the game after ## rounds was won by any team.
    # Allow players to callvote unlock to let spectators to join.
    # 
    # Server setup:
    # qlx_minRoundsToLock 5 (default:5)     Minimum rounds won to block new players from joinning
    # qlx_roundsLockEnable 1 (default: 0)   Enable / disable round control
    # qlx_teamslocked 0 (default: 0)        cvar for logic control
    #####

    def __init__(self):
        super().__init__()
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("vote_ended", self.handle_vote_ended)
        self.add_hook("new_game", self.handle_new_game)

        self.add_command(("unlockteams"), self.cmd_unlockteams, 1)
        self.add_command(("lockstatus"), self.cmd_lockstatus, 1)

        self.set_cvar_once("qlx_minRoundsToLock", "5")
        self.set_cvar_once("qlx_roundsLockEnable", "0")
        self.set_cvar_once("qlx_teamslocked", "0")

    def handle_round_countdown(self, *args, **kwargs):
        roundcontrolenabled = (int)(self.get_cvar("qlx_roundsLockEnable"))
        if (roundcontrolenabled == 1):
            total_rounds = max((int)(self.game.red_score), (int)(self.game.blue_score))

            self.msg("Round Control: round count ^3{}".format(total_rounds))

            if total_rounds >= (int)(self.get_cvar("qlx_minRoundsToLock")) and self.get_cvar("qlx_teamslocked", bool) is False:
                self.msg("Game reach round count of {}. ^6Locking teams.".format(self.get_cvar("qlx_minRoundsToLock")))
                self.msg("^3You can callvote unlockteams to unlock.")
                teams = self.teams()
                if len(teams["red"] + teams["blue"]) % 2 != 0:
                    self.msg("Teams were ^3NOT^7 balanced. Not possible to lock teams.")
                    return
                
                self.game.teamsize = len(teams["red"]) # teams are equal anyways ;)
                self.lock()
                self.set_cvar_once("qlx_teamslocked", "1")
                self.msg("Teams has been ^6LOCKED^7.")
                return
            return

    def handle_vote_called(self, caller, vote, args):
        if vote.lower() == "unlockteams" and self.get_cvar("qlx_teamslocked", bool):
            caller.tell("Teams are alread unlocked.")
            return
    
    def handle_vote_ended(self, votes, vote, args, passed):   
        if passed == True and vote.lower() == "unlockteams":
            gt = self.game.type_short
            if gt not in SUPPORTED_GAMETYPES:
                return
            
            @minqlx.delay(3.5)
            def f():
                self.cmd_unlockteams()
            f()
    
    def handle_new_game(self):
        # unlock teams on start
        if self.game.state == "warmup":
            self.unlock()
            return
    
    def cmd_unlockteams(self, player, msg, channel):
        if self.get_cvar("qlx_roundsLockEnable", bool):
            teams = self.teams()
            self.game.teamsize = len(teams["red"]) + 1
            self.unlock()
            self.set_cvar_once("qlx_teamslocked", "0")
            self.msg("Teams were ^3UNLOCKED^7. Spectators are allowed to join.")
        else:
            self.msg("Team locking is disabled. Check server configuration.")
            return

    def cmd_lockstatus(self, player, msg, channel):
        if self.get_cvar("qlx_roundsLockEnable", bool):
            if self.get_cvar("qlx_teamslocked", bool):
                player.tell("Teams are ^1LOCKED^7.")
            else:
                player.tell("Teams are ^3UNLOCKED^7.")
        else:
            self.msg("Team locking is disabled. Check server configuration.")
            return
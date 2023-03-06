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

VERSION = "v1.00"
SUPPORTED_GAMETYPES = ("ad", "ca", "ctf", "dom", "ft", "tdm")

class roundcontrol(minqlx.Plugin):
    #####
    # Script blocks new players to join the game after ## rounds was won by any team.
    # Allow players to say !unlockteams to let spectators to join.
    # 
    # Server setup:
    # qlx_minRoundsToLock 5 (default:5)     Minimum rounds won to block new players from joinning
    # qlx_roundControlEnable 1 (default: 1)   Enable / disable round control
    #####
    teamslocked = False

    def __init__(self):
        super().__init__()
        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("game_end", self.handle_game_end)

        self.add_command(("unlockteams"), self.cmd_unlockteams, 1)
        self.add_command(("lockstatus"), self.cmd_lockstatus, 1)
        self.add_command(("teamlock"), self.cmd_teamlock, 3, usage="<0|1>")

        self.set_cvar_once("qlx_minRoundsToLock", "5")
        self.set_cvar_once("qlx_roundControlEnable", "1")

    def handle_round_start(self, *args, **kwargs):
       if self.get_cvar("qlx_roundControlEnable", bool):
            total_rounds = max((int)(self.game.red_score), (int)(self.game.blue_score))
            #self.msg("Round Control: Round count: ^6{}.".format(total_rounds))

            teams = self.teams()
            if len(teams["red"] + teams["blue"]) % 2 != 0:
                self.msg("Teams were ^3NOT^7 balanced. Not possible to lock teams.")
                return minqlx.RET_STOP_ALL

            if total_rounds >= (int)(self.get_cvar("qlx_minRoundsToLock")) and self.teamslocked is False:
                self.msg("Round Control: Game reach maximum round count. ^6Locking teams.")
                self.msg("Round Control: You can use ^3!unlockteams ^7to unlock.")
                
                self.game.teamsize = len(teams["red"]) # teams are equal anyways ;)
                self.msg("Round Control: Teamsize set to ^3{}.".format(len(teams["red"])))
                self.lock()
                self.teamslocked = True
                return
            return
    
    def handle_game_end(self, data):
        self.unlock()
        self.teamslocked = False
        self.msg("Round Control: Teams were ^3UNLOCKED^7. Spectators are allowed to join.")
        return
    
    def cmd_unlockteams(self, player, msg, channel):
        if self.get_cvar("qlx_roundControlEnable", bool):
            teams = self.teams()
            self.game.teamsize = len(teams["red"]) + 1
            self.unlock()
            self.teamslocked = False
            self.msg("Round Control: Teams were ^3UNLOCKED^7. Spectators are allowed to join.")
        else:
            self.msg("Round Control: Team locking is disabled. Check server configuration.")
            return

    def cmd_lockstatus(self, player, msg, channel):
        if self.get_cvar("qlx_roundControlEnable", bool):
            if self.teamslocked:
                player.tell("Round Control: Teams are ^1LOCKED^7.")
            else:
                player.tell("Round Control: Teams are ^3UNLOCKED^7.")
        else:
            self.msg("Round Control: Team locking is disabled. Check server configuration.")
            return
        
    def cmd_teamlock(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        if (msg[1] == "1"):
            self.lock()
            self.teamslocked = True
            self.msg("Round Control: Teams were ^1LOCKED^7.")
        else:
            self.unlock()
            self.teamslocked = False
            self.msg("Round Control: Teams were ^3UNLOCKED^7. Spectators are allowed to join.")
        return

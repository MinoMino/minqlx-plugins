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
import minqlx.database

MOTD_KEY = "minqlx:server:motd"

class motd(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_hook("player_loaded", self.handle_player_loaded, priority=minqlx.PRI_LOWEST)
        self.add_command(("setmotd", "newmotd"), self.cmd_setmotd, 4, usage="<motd>")
        self.add_command(("getmotd", "motd"), self.cmd_getmotd)
        self.add_command(("clearmotd", "removemotd", "remmmotd"), self.cmd_clearmotd, 4)
        self.add_command("addmotd", self.cmd_addmotd, 4, usage="<more_motd>")

    @minqlx.delay(2)
    def handle_player_loaded(self, player):
        """Send the message of the day to the player in a tell.

        This should be set to lowest priority so that we don't execute anything if "ban" or
        a similar plugin determines the player should be kicked.
        """
        motd = self.db[MOTD_KEY]
        if not motd:
            return
        
        self.play_sound("sound/vo/crash_new/37b_07_alt.wav", player)
        self.send_motd(player, motd)

    def cmd_setmotd(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        
        self.db[MOTD_KEY] = " ".join(msg[1:])
        player.tell("The MOTD has been set.")
        return minqlx.RET_STOP_EVENT
    
    def cmd_getmotd(self, player, msg, channel):
        motd = self.db[MOTD_KEY]
        if not motd:
            player.tell("No MOTD has been set.")
        else:
            self.send_motd(player, motd)
        return minqlx.RET_STOP_EVENT

    def cmd_clearmotd(self, player, msg, channel):
        del self.db[MOTD_KEY]
        player.tell("The MOTD has been cleared.")
        return minqlx.RET_STOP_EVENT

    def cmd_addmotd(self, player, msg, channel):
        motd = self.db[MOTD_KEY]
        if not motd:
            self.db[MOTD_KEY] = " ".join(msg[1:])
            player.tell("No MOTD was set, so a new one was made.")
        else:
            leading_space = "" if len(motd) > 2 and motd[-2:] == "\\n" else " "
            self.db[MOTD_KEY] = motd + leading_space + " ".join(msg[1:])
            player.tell("The MOTD has been updated.")

        return minqlx.RET_STOP_EVENT

    def send_motd(self, player, motd):
        player.tell("^6*** ^7Message of the Day ^6***")
        for line in motd.split("\\n"):
            player.tell(line)


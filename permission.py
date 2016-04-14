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

"""Database agnostic way of getting and setting a player's permissions.

It assumes the database driver interprets integers as SteamID64s and
being able to handle minqlx.Player instances.

"""

import minqlx

class permission(minqlx.Plugin):
    def __init__(self):
        self.add_command("setperm", self.cmd_setperm, 5, usage="<id> <level>")
        self.add_command("getperm", self.cmd_getperm, 5, usage="<id>")
        # myperm can only be used in-game.
        self.add_command("myperm", self.cmd_myperm,
            channels=("chat", "red", "blue", "spectator", "free", "client_command"))

    def cmd_setperm(self, player, msg, channel):
        if len(msg) < 3:
            return minqlx.RET_USAGE
        
        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return
        
        try:
            level = int(msg[2])
            if level < 0 or level > 5:
                raise ValueError
        except ValueError:
            channel.reply("Invalid permission level. Use a level between 0 and 5.")
            return
        
        self.db.set_permission(ident, level)
        name = target_player.name if target_player else str(ident)

        channel.reply("^6{}^7 was given permission level ^6{}^7.".format(name, level))

    def cmd_getperm(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id

            if ident == minqlx.owner():
                channel.reply("That's my master.")
                return
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.".format(msg[1]))
            return
        
        perm = self.db.get_permission(ident)
        if perm is None:
            channel.reply("I do not know ^6{}^7.".format(msg[1]))
        else:
            name = target_player.name if target_player else str(ident)
            channel.reply("^6{}^7 has permission level ^6{}^7.".format(name, perm))

    def cmd_myperm(self, player, msg, channel):
        if player.steam_id == minqlx.owner():
            channel.reply("You can do anything to me, master.")
            return
        
        perm = self.db.get_permission(player)
        if perm is None:
            channel.reply("I do not know you.")
        else:
            channel.reply("You have permission level ^6{}^7.".format(perm))

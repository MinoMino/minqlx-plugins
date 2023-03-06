# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# This is a plugin and command listing script for the minqlx admin bot.
# This plugin will list all the in game commands loaded on the server.
"""
//Server Config cvars
//Set the permission level needed to list the commands
set qlx_commandsAdmin "0"
//Enable to show only the commands the calling player can use, disable to show all commands (0=disable, 1=enable)
set qlx_commandsOnlyEligible "1"
"""

import minqlx
from re import sub

VERSION = "1.0"


class commands(minqlx.Plugin):
    def __init__(self):
        # queue cvars
        self.set_cvar_once("qlx_commandsAdmin", "0")
        self.set_cvar_once("qlx_commandsOnlyEligible", "1")

        # Minqlx bot commands
        self.add_command("plugins", self.list_plugins, self.get_cvar("qlx_commandsAdmin", int))
        self.add_command(("lc", "listcmds", "listcommands"), self.cmd_list, self.get_cvar("qlx_commandsAdmin", int),
                         usage="<plugin_name>")

    def list_plugins(self, player, msg, channel):
        p = self.plugins
        s = set(p)
        message = []
        count = 0
        for i in s:
            count += 1
            if count % 7 or count == 0:
                message.append(i + "^7, ^6")
            else:
                message.append(i + "^7, ^6\n")
        if count:
            message[count - 1] = sub(r"\^[0-9][, \\n]", "", message[count - 1])
            player.tell("^1{} ^3Plugins found:".format(count))
            player.tell("^6{}".format("".join(message)))

    def cmd_list(self, player, msg, channel):
        p = self.plugins
        s = set(p)
        e = self.get_cvar("qlx_commandsOnlyEligible", bool)
        a = self.db.get_permission(player)
        player.tell("^1Plugin^7: ^2Number of Commands")
        count = 0
        search = msg[1].lower() if len(msg) > 1 else None
        for i in s:
            if search and search not in i.lower():
                continue
            message = []
            try:
                c = p[i].commands
                if len(c):
                    for cmd in c:
                        name = cmd.name
                        b = cmd.permission
                        c_list = []
                        if e and a < b:
                            continue
                        for item in name:
                            c_list.append(item)
                        message.append("^7(^2{}^7) ^6{}".format(b, "^7|^6".join(c_list)))
                    m = len(message)
                    if m:
                        player.tell("^1{}^7: {} ^3Command{}".format(i, m, "s" if m > 1 else ""))
                        player.tell("{}".format("^7, ".join(message)))
                        count += 1
            except:
                continue
        if not count:
            player.tell("^3No Plugin matches ^4{}".format(search))

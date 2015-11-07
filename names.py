# minqlx - Extends Quake Live's dedicated server with extra functionality and scripting.
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
import re

_re_remove_excessive_colors = re.compile(r"(?:\^.)+(\^.)")
_name_key = "minqlx:players:{}:colored_name"

class names(minqlx.Plugin):
    def __init__(self):
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_command(("name", "setname"), self.cmd_name, usage="<name>", client_cmd_perm=0)

        self.set_cvar_once("qlx_enforceSteamName", "1")

    def handle_player_loaded(self, player):
        name_key = _name_key.format(player.steam_id)
        if name_key in self.db:
            db_name = self.db[name_key]
            if not self.get_cvar("qlx_enforceSteamName", bool) or self.clean_text(db_name) == player.clean_name:
                info = minqlx.parse_variables(minqlx.player_info(player.id)["userinfo"], ordered=True)
                info["name"] = db_name
                new_info = "".join(["\\{}\\{}".format(key, info[key]) for key in info])
                minqlx.client_command(player.id, "userinfo \"{}\"".format(new_info))

    def cmd_name(self, player, msg, channel):
        name_key = _name_key.format(player.steam_id)
        
        if len(msg) < 2:
            if name_key not in self.db:
                return minqlx.RET_USAGE
            else:
                del self.db[name_key]
                player.tell("Your registered name has been removed.")
                return minqlx.RET_STOP_EVENT
        
        name = self.clean_excessive_colors(" ".join(msg[1:]))
        if len(name.encode()) > 36:
            player.tell("The name is too long. Consider using fewer colors or a shorter name.")
            return minqlx.RET_STOP_EVENT
        elif self.clean_text(name) != player.clean_name and self.get_cvar("qlx_enforceSteamName", bool):
            player.tell("The colored name must match your current Steam name.")
            return minqlx.RET_STOP_EVENT

        info = minqlx.parse_variables(minqlx.player_info(player.id)["userinfo"], ordered=True)
        info["name"] = name
        new_info = "".join(["\\{}\\{}".format(key, info[key]) for key in info])
        minqlx.client_command(player.id, "userinfo \"{}\"".format(new_info))
        self.db[name_key] = name
        player.tell("The name has been registered. To make me forget about it, a simple ^6{}name^7 will do it."
            .format(self.get_cvar("qlx_commandPrefix")))
        return minqlx.RET_STOP_EVENT

    def clean_excessive_colors(self, name):
        """Removes excessive colors and only keeps the ones that matter."""
        def sub_func(match):
            return match.group(1)

        return _re_remove_excessive_colors.sub(sub_func, name)


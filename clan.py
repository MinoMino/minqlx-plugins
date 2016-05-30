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
_tag_key = "minqlx:players:{}:clantag"

class clan(minqlx.Plugin):
    def __init__(self):
        self.add_hook("set_configstring", self.handle_set_configstring)
        self.add_command(("clan", "setclan"), self.cmd_clan, usage="<clan_tag>", client_cmd_perm=0)

    def handle_set_configstring(self, index, value):
        # The engine strips cn and xcn, so we can safely append it
        # without having to worry about duplicate entries.
        if not value: # Player disconnected?
            return
        elif 529 <= index < 529 + 64:
            try:
                player = self.player(index - 529)
            except minqlx.NonexistentPlayerError:
                # This happens when someone connects, but the player
                # has yet to be properly initialized. We can safely
                # skip it because the clan will be set later.
                return
            tag_key = _tag_key.format(player.steam_id)
            if tag_key in self.db:
                return value + "\\cn\\{0}\\xcn\\{0}".format(self.db[tag_key])

    def cmd_clan(self, player, msg, channel):
        index = 529 + player.id
        tag_key = _tag_key.format(player.steam_id)
        
        if len(msg) < 2:
            if tag_key in self.db:
                del self.db[tag_key]
                cs = minqlx.parse_variables(minqlx.get_configstring(index), ordered=True)
                del cs["cn"]
                del cs["xcn"]
                new_cs = "".join(["\\{}\\{}".format(key, cs[key]) for key in cs]).lstrip("\\")
                minqlx.set_configstring(index, new_cs)
                player.tell("The clan tag has been cleared.")
            else:
                player.tell("Usage to set a clan tag: ^6{} <clan_tag>".format(msg[0]))
            return minqlx.RET_STOP_EVENT

        if len(self.clean_text(msg[1])) > 5:
            player.tell("The clan tag can only be at most 5 characters long, excluding colors.")
            return minqlx.RET_STOP_EVENT
        
        # If the player already has a clan, we need to edit the current
        # configstring. We can't just append cn and xcn.
        tag = self.clean_tag(msg[1])
        cs = minqlx.parse_variables(minqlx.get_configstring(index), ordered=True)
        cs["xcn"] = tag
        cs["cn"] = tag
        new_cs = "".join(["\\{}\\{}".format(key, cs[key]) for key in cs])
        self.db[tag_key] = tag
        minqlx.set_configstring(index, new_cs)
        self.msg("{} changed clan tag to {}".format(player, tag))
        return minqlx.RET_STOP_EVENT

    def clean_tag(self, tag):
        """Removes excessive colors and only keeps the one that matters."""
        def sub_func(match):
            return match.group(1)

        return _re_remove_excessive_colors.sub(sub_func, tag)


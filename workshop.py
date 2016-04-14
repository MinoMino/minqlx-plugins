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

class workshop(minqlx.Plugin):
    def __init__(self):
        self.add_hook("map", self.handle_map)

        self.set_cvar_once("qlx_workshopReferences", "")

    def handle_map(self, *args, **kwargs):
        # Reference our custom workshop items.
        self.game.workshop_items += minqlx.Plugin.get_cvar("qlx_workshopReferences", list)

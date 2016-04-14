# minqlbot - A Quake Live server administrator bot.
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

# Used mostly for debug. A potential security issue, since it allows
# level 5 people to execute arbitrary Python code on your server.

import minqlx

class raw(minqlx.Plugin):
    def __init__(self):
        self.add_command(("exec", "pyexec"), self.cmd_exec, 5,
            client_cmd_pass=False, usage="<python_code>")
        self.add_command(("eval", "pyeval"), self.cmd_eval, 5,
            client_cmd_pass=False, usage="<python_code>")

    def cmd_exec(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        else:
            try:
                exec(" ".join(msg[1:]))
            except Exception as e:
                channel.reply("^1{}^7: {}".format(e.__class__.__name__, e))
                raise

    def cmd_eval(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        else:
            try:
                channel.reply(str(eval(" ".join(msg[1:]))))
            except Exception as e:
                channel.reply("^1{}^7: {}".format(e.__class__.__name__, e))
                raise

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
import os.path

class docs(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_command("gencmd", self.cmd_gencmd, permission=5, usage="[excluded_plugins]")

    def cmd_gencmd(self, players, msg, channel):
        """Generate a command list based on currently loaded plugins in markdown."""
        if len(msg) > 1:
            excluded = [s.lower() for s in msg[1:]]
        else:
            excluded = []

        prefix = self.get_cvar("qlx_commandPrefix")
        cmds = {}
        for cmd in minqlx.COMMANDS.commands:
            if cmd.plugin.__class__.__name__ in excluded:  # Skip excluded plugins.
                continue

            if cmd.permission not in cmds:
                cmds[cmd.permission] = [cmd]
            else:
                cmds[cmd.permission].append(cmd)

        out = (
            "### Commands\n"
            "The command system is based on permission levels. A player will have a permission level\n"
            "of **0** by default. A player with level **1** can execute commands for level **1** and\n"
            "below. A level **2** player can execute level **2**, **1** and **0** commands, and so on.\n"
            "\n\n"
            )

        for perm in sorted(cmds.keys()):
            out += "*   Permission level **{}**\n\n".format(perm)
            for cmd in sorted(cmds[perm], key=lambda x: x.plugin.__class__.__name__):
                name = prefix + cmd.name[0] if cmd.prefix else cmd.name[0]
                out += "    *   **`{}`**".format(name)
                if len(cmd.name) > 1:  # Aliases?
                    out += " (alternatively "
                    for alias in cmd.name[1:]:
                        name_alias = prefix + alias if cmd.prefix else alias
                        out += "`{}`, ".format(name_alias)
                    out = out[:-2] + ")"
                out += " from *{}*\n\n".format(cmd.plugin.__class__.__name__)

                # Docstring.
                if cmd.handler.__doc__:
                    out += "        {}\n\n".format(cmd.handler.__doc__)

                # Usage
                if cmd.usage:
                    out += "        *Usage*: `{} {}`\n\n" \
                        .format(name, cmd.usage)

        out += "*Automatically generated by [minqlx {} (with plugins {})](https://github.com/MinoMino/minqlx)*" \
            .format(minqlx.__version__, minqlx.__plugins_version__)

        with open(os.path.join(self.get_cvar("fs_homepath"), "command_list.md"), "w") as f:
            f.write(out)

        channel.reply("^7Command list generated!")

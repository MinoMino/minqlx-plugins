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

from minqlx.database import Redis

class plugin_manager(minqlx.Plugin):
    database = Redis

    def __init__(self):
        self.add_command("load", self.cmd_load, 5, usage="<plugin>")
        self.add_command("unload", self.cmd_unload, 5, usage="<plugin>")
        self.add_command("reload", self.cmd_reload, 5, usage="<plugin>")
        self.add_command(("reload_config", "reloadconfig"), self.cmd_reload_config, 5)
    
    def cmd_load(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.CMD_USAGE
        else:
            try:
                minqlx.load_plugin(msg[1])
                channel.reply("^7Plugin ^6{} ^7has been successfully loaded."
                    .format(msg[1]))
            except Exception as e:
                channel.reply("^7Plugin ^6{} ^7has failed to load: {} - {}"
                    .format(msg[1], e.__class__.__name__, e))
                minqlx.log_exception(self)
    
    def cmd_unload(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.CMD_USAGE
        else:
            try:
                minqlx.unload_plugin(msg[1])
                channel.reply("^7Plugin ^6{} ^7has been successfully unloaded."
                    .format(msg[1]))
            except Exception as e:
                channel.reply("^7Plugin ^6{} ^7has failed to unload: {} - {}"
                    .format(msg[1], e.__class__.__name__, e))
                minqlx.log_exception(self)
    
    def cmd_reload(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.CMD_USAGE
        else:
            try:
                minqlx.reload_plugin(msg[1])
                channel.reply("^7Plugin ^6{} ^7has been successfully reloaded."
                    .format(msg[1]))
            except Exception as e:
                channel.reply("^7Plugin ^6{} ^7has failed to reload: {} - {}"
                    .format(msg[1], e.__class__.__name__, e))
                minqlx.log_exception(self)
    
    def cmd_reload_config(self, player, msg, channel):
        try:
            minqlx.reload_config()
            channel.reply("^7The config file was reloaded successfully.")
        except Exception as e:
            channel.reply("^7The config file has failed to reload: {} - {}"
                    .format(e.__class__.__name__, e))
            minqlx.log_exception(self)
    

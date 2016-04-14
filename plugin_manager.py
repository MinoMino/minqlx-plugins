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

class plugin_manager(minqlx.Plugin):
    def __init__(self):
        self.add_command("load", self.cmd_load, 5, usage="<plugin>")
        self.add_command("unload", self.cmd_unload, 5, usage="<plugin>")
        self.add_command("reload", self.cmd_reload, 5, usage="<plugin>")
        self.add_command("loadall", self.cmd_loadall, 5)
        self.add_command("unloadall", self.cmd_unloadall, 5)
        self.add_command("reloadall", self.cmd_reloadall, 5)
    
    def cmd_load(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        else:
            try:
                minqlx.load_plugin(msg[1])
                channel.reply("Plugin ^6{} ^7has been successfully loaded."
                    .format(msg[1]))
            except Exception as e:
                channel.reply("Plugin ^6{} ^7has failed to load: {} - {}"
                    .format(msg[1], e.__class__.__name__, e))
                minqlx.log_exception(self)
    
    def cmd_unload(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        else:
            try:
                minqlx.unload_plugin(msg[1])
                channel.reply("Plugin ^6{} ^7has been successfully unloaded."
                    .format(msg[1]))
            except Exception as e:
                channel.reply("Plugin ^6{} ^7has failed to unload: {} - {}"
                    .format(msg[1], e.__class__.__name__, e))
                minqlx.log_exception(self)
    
    def cmd_reload(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        else:
            # Wrap in next_frame to avoid the command going off several times due
            # to the plugins dict being modified mid-command execution.
            @minqlx.next_frame
            def f():
                try:
                    minqlx.reload_plugin(msg[1])
                    channel.reply("Plugin ^6{} ^7has been successfully reloaded."
                        .format(msg[1]))
                except Exception as e:
                    channel.reply("Plugin ^6{} ^7has failed to reload: {} - {}"
                        .format(msg[1], e.__class__.__name__, e))
                    minqlx.log_exception(self)

            f()

    def cmd_loadall(self, player, msg, channel):
        # Wrap in next_frame to avoid the command going off several times due
        # to the plugins dict being modified mid-command execution.
        @minqlx.next_frame
        def f():
            try:
                minqlx.load_preset_plugins()
            except Exception as e:
                channel.reply("Plugins failed to load: {} - {}"
                    .format(e.__class__.__name__, e))
                minqlx.log_exception(self)

            channel.reply("Successfully loaded all plugins in ^6qlx_plugins^7.")
        f()

    def cmd_unloadall(self, player, msg, channel):
        for plugin in self.plugins:
            if plugin != self.__class__.__name__:
                try:
                    minqlx.unload_plugin(plugin)
                except Exception as e:
                    channel.reply("Plugin ^6{} ^7has failed to unload: {} - {}"
                        .format(plugin, e.__class__.__name__, e))
                    minqlx.log_exception(self)

        channel.reply("Successfully unloaded all plugins except {}."
            .format(self.__class__.__name__))

    def cmd_reloadall(self, player, msg, channel):
        # Wrap in next_frame to avoid the command going off several times due
        # to the plugins dict being modified mid-command execution.
        @minqlx.next_frame
        def f():
            for plugin in self.plugins:
                if plugin != self.__class__.__name__:
                    try:
                        minqlx.reload_plugin(plugin)
                    except Exception as e:
                        channel.reply("Plugin ^6{} ^7has failed to unload: {} - {}"
                            .format(plugin, e.__class__.__name__, e))
                        minqlx.log_exception(self)

            channel.reply("Successfully reloaded all plugins except {}."
                .format(self.__class__.__name__))

        f()

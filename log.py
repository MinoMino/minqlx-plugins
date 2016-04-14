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
import logging
import os.path
import datetime
import os

from logging.handlers import RotatingFileHandler

class log(minqlx.Plugin):
    def __init__(self):
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_LOWEST)
        self.add_hook("player_disconnect", self.handle_player_disconnect, priority=minqlx.PRI_LOWEST)
        self.add_hook("chat", self.handle_chat, priority=minqlx.PRI_LOWEST)
        self.add_hook("command", self.handle_command, priority=minqlx.PRI_LOWEST)

        self.set_cvar_once("qlx_chatlogs", "3")
        self.set_cvar_once("qlx_chatlogsSize", str(3*10**6)) # 3 MB

        self.chatlog = logging.Logger(__name__)
        file_dir = os.path.join(minqlx.get_cvar("fs_homepath"), "chatlogs")
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        file_path = os.path.join(file_dir, "chat.log")
        maxlogs = minqlx.Plugin.get_cvar("qlx_chatlogs", int)
        maxlogsize = minqlx.Plugin.get_cvar("qlx_chatlogsSize", int)
        file_fmt = logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        file_handler = RotatingFileHandler(file_path, encoding="utf-8", maxBytes=maxlogsize, backupCount=maxlogs)
        file_handler.setFormatter(file_fmt)
        self.chatlog.addHandler(file_handler)
        self.chatlog.info("============================= Logger started @ {} ============================="
            .format(datetime.datetime.now()))

    def handle_player_connect(self, player):
        self.chatlog.info("{}:{}:{} connected.".format(player.clean_name, player.steam_id, player.ip))

    def handle_player_disconnect(self, player, reason):
        if reason and reason[-1] not in ("?", "!", "."):
            reason = reason + "."
        
        self.chatlog.info(self.clean_text("{}:{} {}".format(player, player.steam_id, reason)))

    def handle_chat(self, player, msg, channel):
        channel_name = ""
        if channel != "chat":
            channel_name = "[{}] ".format(str(channel).upper())
        
        self.chatlog.info(self.clean_text("{}<{}:{}> {}"
            .format(channel_name, player, player.steam_id, msg)))

    def handle_command(self, caller, command, args):
        self.chatlog.info(self.clean_text("[CMD] <{}:{}> {}"
            .format(caller, caller.steam_id, args)))

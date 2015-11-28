# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Ban players from voting.
"""

import minqlx
import minqlx.database


class vote_ban(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        self.add_command("voteban", self.cmd_voteban, 2, usage="<id>")
        self.add_command("voteunban", self.cmd_voteunban, 2, usage="<id>")

    def handle_vote_called(self, player, vote, args):
        """Stops a banned player from voting."""
        if self.is_banned(player.steam_id):
            player.tell("You are banned from voting.")
            return minqlx.RET_STOP_ALL

    def cmd_voteban(self, player, msg, channel):
        """Bans a player from voting."""
        if len(msg) < 2:
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

        if target_player:
            name = target_player.name
        else:
            name = ident

        # Players with permissions level 1 or higher cannot be banned from voting.
        if self.db.has_permission(ident, 1):
            channel.reply("^6{}^7 has permission level 1 or higher and cannot be banned from voting.".format(name))
            return

        self.db.sadd("minqlx:vote_ban", ident)
        channel.reply("^6{} ^7has been banned from voting".format(name))

    def cmd_voteunban(self, player, msg, channel):
        """Unbans a player from voting."""
        if len(msg) < 2:
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

        if target_player:
            name = target_player.name
        else:
            name = ident

        if self.is_banned(ident):
            self.db.srem("minqlx:vote_ban", ident)
            channel.reply("{} is now unbanned from voting.".format(name))
        else:
            channel.reply("{} is not banned from voting.".format(name))

    def is_banned(self, steam_id):
        """Returns whether a player is banned"""
        banned = self.db.sismember("minqlx:vote_ban", steam_id)
        if banned == 1:
            return True
        else:
            return False

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# If you have any suggestions or issues/problems with this plugin you can contact me(kanzo) on irc at #minqlbot
# or alternatively you can open an issue at https://github.com/cstewart90/minqlx-plugins/issues

"""
Ban players from voting.
"""

import minqlx
import minqlx.database

BANVOTE_KEY = "minqlx:vote_ban"


class banvote(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_hook("vote_called", self.handle_vote_called, priority=minqlx.PRI_HIGH)
        self.add_command("banvote", self.cmd_banvote, 2, usage="<id>")
        self.add_command("unbanvote", self.cmd_unbanvote, 2, usage="<id>")

    def handle_vote_called(self, player, vote, args):
        """Stops a banned player from voting."""
        if self.db.sismember(BANVOTE_KEY, player.steam_id):
            if len(self.teams()["free"] + self.teams()["red"] + self.teams()["blue"]) > 1:
                player.tell("You are banned from voting.")
                return minqlx.RET_STOP_ALL

    def cmd_banvote(self, player, msg, channel):
        """Bans a player from voting."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        steam_id, name = self.get_player(msg[1], channel)
        if steam_id is None:
            return

        # Players with permissions level 1 or higher cannot be banned from voting.
        if self.db.has_permission(steam_id, 1):
            channel.reply("^7{} ^3has permission level 1 or higher and cannot be banned from voting.".format(name))
            return

        if self.db.sismember(BANVOTE_KEY, steam_id):
            channel.reply("^7{} ^3is already banned from voting".format(name))
        else:
            self.db.sadd(BANVOTE_KEY, steam_id)
            channel.reply("^7{} ^1has been banned from voting".format(name))

    def cmd_unbanvote(self, player, msg, channel):
        """Unbans a player from voting."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        steam_id, name = self.get_player(msg[1], channel)
        if steam_id is None:
            return

        if self.db.sismember(BANVOTE_KEY, steam_id):
            self.db.srem(BANVOTE_KEY, steam_id)
            channel.reply("^7{} ^2is now unbanned from voting.".format(name))
        else:
            channel.reply("^7{} ^3is not banned from voting.".format(name))

    def get_player(self, ident, channel):
        """Gets name and id a of player.
        :param ident: Client or Steam ID.
        :param channel: Channel to reply to.
        """
        try:
            ident = int(ident)
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return None, None
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return None, None

        if target_player:
            name = target_player.name
        else:
            name = ident

        return ident, name

# Based on x0rnns's checkplayers(https://github.com/x0rnn/minqlx-plugins/blob/master/checkplayers.py)
# Completely rewritten to use scan_iter instead of keys.
# http://redis.io/commands/scan
#
# LICENSE PREAMBLE GOES HERE

"""
BETA

!permissions: shows all players with any permission level.
!silenced: shows all silenced players
!banned: shows all banned players
!leaverbanned: shows all players which are banned for leaving
!leaverwarned: shows all players which are warned for leaving
"""

import minqlx
import minqlx.database
import re
import time
from operator import itemgetter

PLAYER_KEY = "minqlx:players:{}"


class checkplayers(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_command("permissions", self.cmd_permissions, 4)
        self.add_command("silenced", self.cmd_silenced, 4)
        self.add_command("banned", self.cmd_banned, 4)
        self.add_command("leaverbanned", self.cmd_leaver_banned, 4)
        self.add_command("leaverwarned", self.cmd_leaver_warned, 4)

    def cmd_permissions(self, player, msg, channel):
        """Outputs all players with any permission level.
        cmd_permission is not threaded so return minqlx.RET_STOP_ALL works."""
        @minqlx.thread
        def permissions():
            players = []
            for key in self.db.scan_iter("minqlx:players:*:permission"):
                steam_id = key.split(":")[2]
                permission = self.db[key]
                name = self.player_name(steam_id)
                players.append(dict(name=name, steam_id=steam_id, permission=permission))

            if not players:
                player.tell("There is no players with any permission level.")
                return

            output = ["^5Owner: ^7{} ^5Name: ^7{}".format(minqlx.owner(), self.player_name(minqlx.owner())),
                      "^5{:^31} ^7| ^5{:^17} ^7| ^5{}".format("Name", "Steam ID", "Permission")]
            for p in sorted(players, key=itemgetter("permission"), reverse=True):
                output.append("{name:31} | {steam_id:17} | {permission}".format(**p))
            tell_large_output(player, output)

        permissions()
        return minqlx.RET_STOP_ALL

    def cmd_silenced(self, player, msg, channel):
        if "silence" in self.plugins:
            self.bans(player, "silence")
        else:
            player.tell("silence plugin is not loaded!")
        return minqlx.RET_STOP_ALL

    def cmd_banned(self, player, msg, channel):
        if "ban" in self.plugins:
            self.bans(player, "ban")
        else:
            player.tell("ban plugin is not loaded!")
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def bans(self, player, ban_type):
        """Outputs all banned/silenced players.
        :param player: player to tell to
        :param ban_type: ban or silence
        """
        output = ["^5{:^31} ^7| ^5{:^17} ^7| ^5{:^19} ^7| ^5{}".format("Name", "Steam ID", "Expires", "Reason")]
        for key in self.db.scan_iter("minqlx:players:*:{}s".format(ban_type)):
            steam_id = key.split(":")[2]

            if ban_type == "ban":
                banned = self.plugins["ban"].is_banned(steam_id)
            else:
                banned = self.plugins["silence"].is_silenced(steam_id)

            if banned:
                if ban_type == "ban":
                    expires, reason = banned
                else:
                    expires, _, reason = banned
                name = self.player_name(steam_id)
                output.append("{:31} | {:17} | {} | {}".format(name, steam_id, expires, reason))

        if len(output) > 1:
            tell_large_output(player, output)
        else:
            if ban_type == "ban":
                player.tell("There is no banned players.")
            else:
                player.tell("There is no silenced players.")

    def cmd_leaver_banned(self, player, msg, channel):
        if not self.get_cvar("qlx_leaverBan", bool):
            player.tell("Leaver ban is not enabled.")
        else:
            self.leavers(player, "ban")
        return minqlx.RET_STOP_ALL

    def cmd_leaver_warned(self, player, msg, channel):
        if not self.get_cvar("qlx_leaverBan", bool):
            player.tell("Leaver ban is not enabled.")
        else:
            self.leavers(player, "warn")
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def leavers(self, player, action):
        """Outputs all leaver banned/warned players.
        :param player: Player to tell to
        :param action: warn or ban
        """
        players = []
        for key in self.db.scan_iter("minqlx:players:*:games_left"):
            steam_id = key.split(":")[2]
            status = self.plugins["ban"].leave_status(steam_id)
            if status and status[0] == action:
                action, ratio = status
                ratio = str(ratio)[:4]  # truncate float instead of rounding.
                name = self.player_name(steam_id)
                left = self.db[key]
                try:
                    completed = self.db[PLAYER_KEY.format(steam_id) + ":games_completed"]
                except KeyError:
                    completed = 0

                players.append(dict(name=name, steam_id=steam_id, left=left, completed=completed, ratio=ratio))

        if len(players) == 0:
            if action == "ban":
                player.tell("There is no players banned for leaving.")
            else:
                player.tell("There is no players warned for leaving.")
            return

        output = ["^5{:^31} ^7| ^5{:^17} ^7| ^5{} ^7| ^5{} ^7| ^5{}"
                  .format("Name", "Steam ID", "Left", "Completed", "Ratio")]
        for p in sorted(players, key=itemgetter("ratio", "left"), reverse=True):
            output.append("{name:31} | {steam_id:17} | ^1{left:4} ^7| ^2{completed:9} ^7| {ratio}".format(**p))

        tell_large_output(player, output)

    def player_name(self, steam_id):
        """Returns the latest name a player has used."""
        try:
            name = self.db.lindex(PLAYER_KEY.format(steam_id), 0)
            if not name:
                raise KeyError
            name = re.sub(r"\^[0-9]", "", name)  # remove colour tags
        except KeyError:
            name = steam_id
        return name


def tell_large_output(player, output):
    """Tells large output in small portions, as not to disconnected the player."""
    for count, line in enumerate(output, start=1):
        if count % 30 == 0:  # decrease if someone getting disconnected
            time.sleep(0.4)  # increase if changing previous line does not help
            player.tell(output[0])
        player.tell(line)

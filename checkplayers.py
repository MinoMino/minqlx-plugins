# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# If you have any suggestions or issues/problems with this plugin you can contact me(kanzo) on irc at #minqlbot
# or alternatively you can open an issue at https://github.com/cstewart90/minqlx-plugins/issues

"""
Based on x0rnns's checkplayers(https://github.com/x0rnn/minqlx-plugins/blob/master/checkplayers.py).
Completely rewritten to use scan_iter instead of keys, and changed output to be a table.
Also fixes IRC flooding and player getting disconnected with large outputs.

Why? http://redis.io/commands/SCAN
"Since these commands allow for incremental iteration, returning only a small number of elements per call,
they can be used in production without the downside of commands like KEYS or SMEMBERS that may block the
server for a long time(even several seconds) when called against big collections of keys or elements"

!permissions   - Shows all players with >= 1 permission level.
!banned        - Shows all banned players.
!silenced      - Shows all silenced players.
!leaverbanned  - Shows all players which are banned for leaving.
!leaverwarned  - Shows all players which are warned for leaving.
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
        self.add_command(("banned", "silenced"), self.cmd_bans, 4)
        self.add_command(("leaverbanned", "leaverwarned"), self.cmd_leavers, 4)

    def cmd_permissions(self, player, msg, channel):
        """Outputs all players with >= 1 permission level.
        cmd_permission is not threaded so return minqlx.RET_STOP_ALL works."""
        @minqlx.thread
        def permissions():
            players = []
            for key in self.db.scan_iter("minqlx:players:765*:permission"):
                steam_id = key.split(":")[2]
                permission = int(self.db[key])
                if permission >= 1:
                    name = self.player_name(steam_id)
                    players.append(dict(name=name, steam_id=steam_id, permission=permission))

            if players:
                output = ["^5Owner: ^7{} ^5Name: ^7{}".format(minqlx.owner(), self.player_name(minqlx.owner())),
                          "^5{:^31} | {:^17} | {}".format("Name", "Steam ID", "Permission")]
                for p in sorted(players, key=itemgetter("permission"), reverse=True):
                    output.append("{name:31} | {steam_id:17} | {permission}".format(**p))
                checkplayers.callback(player, msg[0][1:].lower(), output)
            else:
                checkplayers.callback(player, msg[0][1:].lower(), [])
        permissions()
        return minqlx.RET_STOP_ALL

    def cmd_bans(self, player, msg, channel):
        """Outputs all banned/silenced players."""
        @minqlx.thread
        def bans():
            players = []
            for key in self.db.scan_iter("minqlx:players:765*:{}s".format(ban_type)):
                steam_id = key.split(":")[2]

                if ban_type == "ban":
                    banned = self.plugins["ban"].is_banned(steam_id)
                else:
                    banned = self.plugins["silence"].is_silenced(steam_id)

                if banned:
                    expires = banned[0]
                    reason = banned[-1]
                    name = self.player_name(steam_id)
                    players.append(dict(name=name, steam_id=steam_id, expires=str(expires), reason=reason))

            if players:
                output = ["^5{:^31} | {:^17} | {:^19} | {}".format("Name", "Steam ID", "Expires", "Reason")]
                for p in sorted(players, key=itemgetter("expires")):
                    output.append("{name:31} | {steam_id:17} | {expires:19} | {reason}".format(**p))
                checkplayers.callback(player, command, output)
            else:
                checkplayers.callback(player, command, [])

        command = msg[0][1:].lower()
        ban_type = "ban" if command == "banned" else "silence"
        if ban_type in self.plugins:
            bans()
        else:
            player.tell("{} plugin is not loaded!".format(ban_type))
        return minqlx.RET_STOP_ALL

    def cmd_leavers(self, player, msg, channel):
        """Outputs all leaver banned/warned players."""
        @minqlx.thread
        def leavers():
            players = []
            for key in self.db.scan_iter("minqlx:players:765*:games_left"):
                steam_id = key.split(":")[2]
                status = self.plugins["ban"].leave_status(steam_id)
                if status and status[0] == action:
                    ratio = str(status[1])[:4]  # truncate float instead of rounding.
                    name = self.player_name(steam_id)
                    left = self.db[key]
                    try:
                        completed = self.db[PLAYER_KEY.format(steam_id) + ":games_completed"]
                    except KeyError:
                        completed = 0

                    players.append(dict(name=name, steam_id=steam_id, left=left, completed=completed, ratio=ratio))

            if players:
                output = ["^5{:^31} | {:^17} | {} | {} | {}"
                          .format("Name", "Steam ID", "Left", "Completed", "Ratio")]
                for p in sorted(players, key=itemgetter("ratio", "completed"), reverse=True):
                    output.append("{name:31} | {steam_id:17} | ^1{left:4} ^7| ^2{completed:9} ^7| {ratio}".format(**p))
                checkplayers.callback(player, command, output)
            else:
                checkplayers.callback(player, command, [])

        if not self.get_cvar("qlx_leaverBan", bool):
            player.tell("Leaver ban is not enabled(qlx_leaverBan).")
        else:
            command = msg[0][1:].lower()
            action = "ban" if command == "leaverbanned" else "warn"
            leavers()
        return minqlx.RET_STOP_ALL

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

    @staticmethod
    def callback(player, command, output):
        """Tells player the output of the command.
        If player is a DummyPlayer then decreases max_amount and
        delay as to not disconnect the bot from IRC due to flooding."""
        if output:
            if isinstance(player, minqlx.AbstractDummyPlayer):
                tell_large_output(player, output, max_amount=1, delay=2)
            else:
                tell_large_output(player, output)
        else:
            if command == "permissions":
                player.tell("There are no players with >= 1 permission level.")
            else:
                player.tell("There are no {} players.".format(command))


def tell_large_output(player, output, max_amount=25, delay=0.4):
    """Tells large output in small portions, as not to disconnected the player.
    :param player: Player to tell to.
    :param output: Output to send to player.
    :param max_amount: Max amount of lines to send at once.
    :param delay: Time to sleep between large inputs.
    """
    for count, line in enumerate(output, start=1):
        if count % max_amount == 0:
            time.sleep(delay)
        player.tell(line)

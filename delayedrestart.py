# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Adds !delayedrestart which will restart(quit + supervisor spawns new process) when
no one is playing.
"""

import minqlx


class delayedrestart(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_command("delayedrestart", self.cmd_delayedrestart, 5)

        self.restart = False

    def handle_team_switch(self, player, old_team, new_team):
        """Quits server when no one playing after a player moves to spectator."""
        if self.restart and self.amount_playing() == 0:
            self.msg("Restarting server in 30 seconds if nobody joins.")
            self.quit()

    def handle_player_disconnect(self, player, reason):
        """Quits server when no one playing after a player disconnects."""
        if self.restart and self.amount_playing() <= 1 and player.team != "spectator":
            self.msg("Restarting server in 30 seconds if nobody joins.")
            self.quit()

    def cmd_delayedrestart(self, player, msg, channel):
        """Quits server if no one is playing otherwise server will quit
        the next time no one is playing."""
        if self.amount_playing() == 0:
            channel.reply("restarting server")
            self.quit()
        else:
            player.tell("Server will restart when no one is playing.")
            self.restart = True

    def amount_playing(self):
        """Returns the amount of players which are not spectating."""
        return len(self.teams()["free"]) + len(self.teams()["red"]) + len(self.teams()["blue"])

    @minqlx.delay(20)
    def quit(self):
        """Quits server after 30 second delay if no one is playing."""
        if self.amount_playing() != 0:
            self.restart = True
        else:
            self.msg("Restarting server in 10 seconds.")

            def restart():
                minqlx.console_command("quit")
            restart()

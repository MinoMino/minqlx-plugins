# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Adds !delayedrestart which will restart(quit + supervisor spawns new process) server when
no one is playing.
"""

import minqlx


class delayedrestart(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_command("delayedrestart", self.cmd_delayed_restart, 5)

        self.checking = False
        self.restart = False

    def handle_team_switch(self, player, old_team, new_team):
        """Quits server when no one is playing after a player moves to spectator."""
        if self.restart and self.amount_playing() == 0 and not self.checking:
            self.check_quit()

    def handle_player_disconnect(self, player, reason):
        """Quits server when no one is playing after a player disconnects."""
        if self.restart and self.amount_playing() <= 1 and player.team != "spectator" and not self.checking:
            self.check_quit()

    def cmd_delayed_restart(self, player, msg, channel):
        """Quits server if server is empty. If server is not empty
        but no one is playing a quit is scheduled in 30 seconds. Otherwise
        server will quit when people leave/spectate."""
        if len(self.players()) == 0:
            self.quit_server()
        elif self.amount_playing() == 0:
            self.check_quit()
        else:
            player.tell("Server will restart when no one is playing.")
            self.restart = True

    def amount_playing(self):
        """Returns the amount of players which are playing."""
        return len(self.teams()["free"]) + len(self.teams()["red"]) + len(self.teams()["blue"])

    def check_quit(self):
        """Quits server in 30 seconds if no one is playing.
        If someone joins the game within 20 seconds then the server
        won't be restarted until people leave/spectate."""
        self.checking = True

        @minqlx.delay(20)
        def check():
            if self.amount_playing() > 0:
                self.restart = True
            else:
                self.quit_server()
            self.checking = False

        check()

    def quit_server(self):
        """Quits server after 10 seconds."""
        self.msg("Restarting server in 10 seconds.")

        @minqlx.delay(10)
        def quit_server():
            minqlx.console_command("quit")

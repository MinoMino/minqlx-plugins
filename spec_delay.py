# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Stops people spectating then quickly joining the 'free' team.
This is to stop people firing a rocket, then spectating and joining then
using the knockback from the rocket which would count as a strafe time.
"""

import minqlx


class spec_delay(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("team_switch_attempt", self.handle_team_switch_attempt)
        self.add_hook("team_switch", self.handle_team_switch)
        self.spec_delays = set()

    def handle_player_disconnect(self, player, reason):
        """Sets spec delay when a player disconnects."""
        self.spec_delays.add(player.steam_id)
        self.allow_join(player)

    def handle_team_switch_attempt(self, player, old_team, new_team):
        """Stops the player joining if spec delay is true."""
        if new_team != "spectator" and old_team == "spectator" and player.steam_id in self.spec_delays:
            player.tell("^6You must wait 15 seconds before joining after spectating")
            return minqlx.RET_STOP_EVENT

    def handle_team_switch(self, player, old_team, new_team):
        """Sets a delay on joining when the player joins spectator"""
        if new_team == "spectator" and old_team == "free":
            # Set spec delay
            self.spec_delays.add(player.steam_id)
            self.allow_join(player)
        # This is only needed to stop \team s; team f
        elif new_team == "free" and old_team == "spectator" and player.steam_id in self.spec_delays:
            player.tell("^6You must wait 15 seconds before joining after spectating")
            return minqlx.RET_STOP_EVENT

    @minqlx.delay(15.1)
    def allow_join(self, player):
        """Allows the player to join after 15.1 seconds."""
        try:
            self.spec_delays.remove(player.steam_id)
            player.center_print("^6You can join now")
        except KeyError:
            return
        except AttributeError:
            return

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
        self.spec_delays = {}

    def handle_player_disconnect(self, player, reason):
        """Remove player key when they disconnect."""
        self.spec_delays.pop(player.steam_id, None)

    def handle_team_switch(self, player, old_team, new_team):
        """Sets a delay on joining when the player joins spectator"""
        if new_team == "spectator" and old_team == "free":
            # Set spec delay
            self.spec_delays[player.steam_id] = True
            self.allow_join(player)
        # This is only needed to stop \team s; team f
        elif new_team == "free" and old_team == "spectator":
            if self.spec_delays.get(player.steam_id):
                player.tell("^6You must wait 8 seconds before joining after spectating")
                return minqlx.RET_STOP_EVENT

    def handle_team_switch_attempt(self, player, old_team, new_team):
        """Stops the player joining if spec delay is true."""
        if new_team == "any" and old_team == "spectator":
            if self.spec_delays.get(player.steam_id):
                player.tell("^6You must wait 8 seconds before joining after spectating")
                return minqlx.RET_STOP_EVENT

    @minqlx.delay(8)
    def allow_join(self, player):
        """Allows the player to join after 8 seconds."""
        if self.spec_delays.get(player.steam_id):
            # Remove spec delay
            self.spec_delays[player.steam_id] = False
            player.tell("^6You can join now")

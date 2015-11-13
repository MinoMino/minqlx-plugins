import minqlx


class spec_delay(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("team_switch_attempt", self.handle_team_switch_attempt)
        self.add_hook("team_switch", self.handle_team_switch)
        self.spec_delays = {}

    def handle_player_disconnect(self, player, reason):
        self.spec_delays.pop(player.steam_id, None)

    def handle_team_switch(self, player, old_team, new_team):
        # This is only needed to stop \team s; team f
        if new_team == "spectator" and old_team == "free":
            self.spec_delays[player.steam_id] = True
            self.allow_join(player)
        elif new_team == "free" and old_team == "spectator":
            if self.spec_delays.get(player.steam_id):
                player.tell("^6You must wait  seconds before joining after speccing")
                return minqlx.RET_STOP_EVENT

    def handle_team_switch_attempt(self, player, old_team, new_team):
        if new_team == "any" and old_team == "spectator":
            if self.spec_delays.get(player.steam_id):
                player.tell("^6You must wait 8 seconds before joining after speccing")
                return minqlx.RET_STOP_EVENT

    @minqlx.delay(8)
    def allow_join(self, player):
        if self.spec_delays.get(player.steam_id) is not None:
            player.tell("^6You can join now")
            self.spec_delays[player.steam_id] = False
# mapmonitor.py is a plugin for minqlx to:
# -check on a map change for a change to a bad map
# -If all players are disconnected on a map change it changes to the default map
# -If enabled (default is enabled) the script will also change to the default map when all players disconnect
# created by BarelyMiSSeD on 11-17-2018
#
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
set qlx_mmDefaultMap "almostlost ca"    //set the default map and factory type
set qlx_mmCheckTime "60"                //The amount of time the script will check after a map change for a bad map
set qlx_mmChangeWhenEmpty "1"           //Enable to change to default map when all players disconnect (1=enabled, 0=disabled)
"""

import minqlx
import time

Version = 1.5


class mapmonitor(minqlx.Plugin):
    def __init__(self):
        # cvars
        self.set_cvar_once("qlx_mmDefaultMap", "almostlost ca")
        self.set_cvar_once("qlx_mmCheckTime", "60")
        self.set_cvar_once("qlx_mmChangeWhenEmpty", "1")

        # Minqlx bot Hooks
        self.add_hook("map", self.handle_map)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("console_print", self.handle_console_print)
        self.add_hook("game_end", self.handle_game_end)

        # Minqlx bot commands
        self.add_command("map", self.map_change, 2, usage="<mapname> [factory]")

        # Script Variables
        self._map_change_time = 0.0
        self.map_changed = True
        self.player_count = 0

    def handle_map(self, mapname, factory):
        self._map_change_time = time.time()

        @minqlx.delay(5)
        def check():
            self.check_player_count()

        check()

    def handle_player_disconnect(self, player, reason):
        if len(self.players()) - 1 <= 0 and self.get_cvar("qlx_mmChangeWhenEmpty", bool):
            self.def_change_map()
            self.player_count = 0

    def handle_console_print(self, text):
        if text.startswith("zmq RCON command"):
            args = text.split(":")
            if args[1].startswith(" map "):
                self.player_count = len(self.players())
                self.map_changed = True

    def handle_game_end(self, data):
        self.player_count = len(self.players())

    @minqlx.thread
    def check_player_count(self):
        if self.player_count != 0 or not self.map_changed and self._map_change_time != 0.0:
            loop_time = self.get_cvar("qlx_mmCheckTime", int)
            while time.time() - self._map_change_time < loop_time:
                time.sleep(1)
                if len(self.players()) == 0:
                    self.player_count = 0
                    self.def_change_map()
                    return
        self.map_changed = False
        self.player_count = len(self.players())
        self._map_change_time = 0.0

    @minqlx.next_frame
    def def_change_map(self):
        current_map = "{} {}".format(self.get_cvar("mapname"), self.get_cvar("g_factory"))
        default_map = self.get_cvar("qlx_mmDefaultMap").strip()
        if current_map != default_map:
            minqlx.console_print("^1Changing map to {}".format(default_map))
            self.map_changed = True
            minqlx.console_command("map {}".format(self.get_cvar("qlx_mmDefaultMap")))

    def map_change(self, player, msg, channel):
        if "essentials" not in self._loaded_plugins:
            """Changes the map."""
            if len(msg) < 2:
                return minqlx.RET_USAGE
            self.change_map(msg[1], msg[2] if len(msg) > 2 else None)
        self.map_changed = True
        self.player_count = len(self.players())
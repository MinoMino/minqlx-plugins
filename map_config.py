import os
import minqlx


class map_config(minqlx.Plugin):
    def __init__(self):
        self.set_cvar_once("qlx_map_config_path", "map_configs")
        self.add_hook("new_game", self.handle_new_game)

    @property
    def default_config_filepath(self):
        return os.path.join(self.get_cvar("qlx_map_config_path"), "default.cfg")

    @property
    def config_filepath(self):
        result = os.path.join(
            self.get_cvar("qlx_map_config_path"), self.game.map + ".cfg"
        )
        for path_cvar in ("fs_homepath", "fs_basepath"):
            abs_filepath = os.path.join(self.get_cvar(path_cvar), "baseq3", result)
            if os.path.isfile(abs_filepath):
                return result
        return None

    def handle_new_game(self):
        if self.config_filepath:
            minqlx.console_command("exec {}".format(self.config_filepath))
        else:
            minqlx.console_command("exec {}".format(self.default_config_filepath))

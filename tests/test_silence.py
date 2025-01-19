import unittest
from time import sleep

from mockito import unstub
from silence import silence, minqlx
from minqlx_plugin_test import (
    connected_players,
    fake_player,
    mocked_channel,
    setup_cvars,
    setup_plugin,
)


class TestSilence(unittest.TestCase):
    def setUp(self):
        setup_plugin()
        connected_players()
        setup_cvars(
            {
                "qlx_database": "redis",
                "qlx_redisDatabase": "0",
                "qlx_redisUnixSocket": "0",
                "qlx_redisAddress": "127.0.0.1",
                "qlx_redisPassword": "",
                "qlx_owner": "777",
            }
        )
        minqlx.Plugin.database = minqlx.database.Redis
        self.plugin = silence()

    def tearDown(self):
        unstub()

    def test_silence(self):
        player = fake_player(666, "Woodpecker", _id=4)
        admin = fake_player(777, "Admin", _id=0)
        channel = mocked_channel()
        connected_players(player)
        plugin = self.plugin

        plugin.cmd_silence(admin, ["!silence", "4", "3", "seconds"], channel)

        plugin.handle_client_command(player, "say hey")
        self.assertIn(player.steam_id, plugin.silenced)

        sleep(3.5)

        plugin.handle_client_command(player, "say hey")
        self.assertNotIn(player.steam_id, plugin.silenced)

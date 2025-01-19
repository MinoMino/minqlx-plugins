import unittest
from time import sleep

from ban import ban, minqlx
from mockito import unstub
from minqlx_plugin_test import (
    connected_players,
    fake_player,
    mocked_channel,
    setup_cvars,
    setup_plugin,
)


class TestBan(unittest.TestCase):
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
                "qlx_leaverBan": "0",
            }
        )
        minqlx.Plugin.database = minqlx.database.Redis
        self.plugin = ban()

    def tearDown(self):
        unstub()

    def test_ban(self):
        player = fake_player(666, "Woodpecker")
        admin = fake_player(777, "Admin")
        channel = mocked_channel()
        connected_players(player)

        self.plugin.cmd_ban(admin, ["!ban", "666", "3", "seconds"], channel)

        player_connect_result = self.plugin.handle_player_connect(player)
        self.assertTrue(isinstance(player_connect_result, str))
        self.assertTrue(player_connect_result.startswith("You are banned until"))

        sleep(3.5)

        player_connect_result = self.plugin.handle_player_connect(player)
        self.assertEqual(player_connect_result, None)

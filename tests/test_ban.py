from minqlx_plugin_test import setup_plugin, connected_players, mocked_channel, fake_player, unstub, setup_cvars
import unittest

from ban import ban


class TestBan(unittest.TestCase):
    def setUp(self):
        setup_plugin()
        connected_players()
        setup_cvars({
            "qlx_database": "redis",
        })
        self.plugin = ban()

    def tearDown(self):
        unstub()

    def test_ban(self):
        steam_id = 666
        player = fake_player(steam_id, "Woodpecker")
        channel = mocked_channel()
        connected_players(player)
        self.plugin.cmd_ban(None, ["!ban", "666", "10", "seconds"], channel)
        raise NotImplementedError("Tests to check if ban actually executed")

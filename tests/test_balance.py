from minqlx_plugin_test import setup_plugin, setup_cvar, setup_cvars, setup_game_in_progress, connected_players, fake_player, unstub, setup_game_in_warmup

import unittest

from balance import balance

from time import time


def noop(*args, **kwargs):
    return None


class FakeChannel:
    reply = noop


channel = FakeChannel()


class TestBalance(unittest.TestCase):

    def setUp(self):
        setup_plugin()
        setup_cvars({
            "qlx_balanceUseLocal": "0",
        })
        setup_game_in_progress()
        connected_players()
        self.plugin = balance()

    def tearDown(self):
        unstub()

    def setup_balance_ratings(self, player_elos):
        gametype = self.plugin.game.type_short
        ratings = {}
        for player, elo in player_elos:
            ratings[player.steam_id] = {gametype: {'elo': elo, 'time': time()}}
        self.plugin.ratings = ratings

    def test_float_suggestion_diff(self):
        eugene = fake_player(1, "eugene", "red")
        xaero = fake_player(2, "Xaero", "red")
        fast4you = fake_player(3, "fast4you", "red")
        sugafree = fake_player(4, "sugafree", "red")
        syrumz = fake_player(5, "#Syrumz", "blue")
        indie = fake_player(6, "indie", "blue")
        shazam = fake_player(7, "Sh@z@m", "blue")
        lookaround = fake_player(8, "lookaround", "blue")

        players = [
            eugene, xaero, fast4you, sugafree,
            syrumz, indie, shazam, lookaround,
        ]
        connected_players(*players)

        self.setup_balance_ratings([
            (eugene, 31.44), (xaero, 25.12), (fast4you, 19.41), (sugafree, 16.44),
            (syrumz, 34.11), (indie, 30.57), (shazam, 26.89), (lookaround, 18.34)
        ])

        setup_cvar("qlx_balanceMinimumSuggestionDiff", "1.2")

        exception_raised = None
        try:
            self.plugin.callback_teams(list(range(1, 9)), channel)
        except ValueError as e:
            exception_raised = e

        self.assertIsNone(exception_raised, "Unexpected exception")

    def test_cache_reset(self):
        setup_game_in_warmup()

        player1 = fake_player(1, "Evmoncer", "red")
        player2 = fake_player(2, "FalseMan", "blue")

        self.setup_balance_ratings([
            (player1, 1443),
            (player2, 1394),
        ])

        self.assertIn(1, self.plugin.ratings)
        self.assertIn(2, self.plugin.ratings)

        setup_game_in_warmup()
        self.plugin.handle_new_game()

        self.assertFalse(self.plugin.ratings)

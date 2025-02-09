import functools
from typing import Union, Any

from mockito import mock, when2, verify  # type: ignore

# noinspection PyProtectedMember
from mockito.matchers import Matcher, any_  # type: ignore

from minqlx import Player, Plugin


# Functions for setting up players in the game and verifying interactions with them.

any_team: Matcher = any_(str)


def fake_player(
    steam_id: int,
    name: str,
    team: str = "spectator",
    _id: int = 0,
    score: int = 0,
    ping: int = 0,
) -> Player:
    """A builder for mocked players that assertion can be used to check for certain interactions.

    **Make sure to use :func:`mockito.unstub()` after calling this function to avoid side effects spilling into the
    next test.**

    :param steam_id: the steam_id of this fake_player
    :param name: the name of the fake_player
    :param team: the team the player should be on (default "spectator")
    :param _id: the id on the server of the player (default: 0)
    :param score: the score of the player (default: 0)
    :param ping: the ping that player should have (default: 0)
    :return: a mocked player that might be used to set up the game and interactions can be checked with assertion
    functions afterwards.
    """
    player = mock(spec=Player, strict=False)
    player.id = _id
    player.steam_id = steam_id
    player.name = name
    player.clean_name = name
    player.team = team
    player.ping = ping
    player.score = score
    player.assert_was_put_on = functools.partial(assert_player_was_put_on, player)
    player.assert_was_told = functools.partial(assert_player_was_told, player)
    player.assert_center_print = functools.partial(
        assert_player_received_center_print, player
    )
    return player


def connected_players(*players: Player) -> None:
    """Sets up a plugin with the provided players being connected to the server.

    **Make sure to use :func:`mockito.unstub()` after calling this function to avoid side effects spilling into the
    next test.**

    :param players: the players that are currently on the server, in all possible teams: "red", "blue", "spectator",
    and "free"
    """
    when2(Plugin.players).thenReturn(players)
    for player in players:
        when2(Plugin.player, player.steam_id).thenReturn(player)
        when2(Plugin.player, player).thenReturn(player)
        when2(Plugin.player, player.id).thenReturn(player)


def assert_player_was_put_on(
    player: Player, matcher: Union[str, Matcher], *, times: int = 1
) -> None:
    """Assert that the given player was put on the matching team given.

    **The player needs to be set up via :func:`.fake_player(steam_id, name, team, ping)` before using this assertion.**

    **Make sure to use :func:`mockito.unstub()` after calling this assertion to avoid side effects spilling into the
    next test.**

    :param: player: the player that should have been put on the matching team
    :param: matcher: matches the team the player should have been put on. This might be  :class:`mockito.matchers` to
    check that the player was not put on a different team.
    :param: times: The amount of times the player should have been put on the matching team, set to 0 for team switch
    for that player to have happened. (default: 1).
    """
    verify(player, times=times).put(matcher)


def assert_player_was_told(
    player: Player, matcher: Union[str, Matcher, Any], *, times: int = 1
) -> None:
    """Verify that a certain text was sent to the console by the player.

    **The player needs to be set up via :func:`.fake_player(steam_id, name, team, ping)` before using this assertion.**

    **Make sure to use :func:`mockito.unstub()` after calling this assertion to avoid side effects spilling into the
    next test.**

    :param: player: the player that should have been told the matching message
    :param: matcher: matches the text the player should have told. This might be  :class:`mockito.matchers` to check for
    certain types of messages.
    :param: times: The amount of times the player should have been told the matching message, set to 0 for no message
    told to the player. (default: 1).
    :return:
    """
    verify(player, times=times).tell(matcher)


def assert_player_received_center_print(
    player: Player, matcher: Union[str, Matcher, Any], *, times: int = 1
) -> None:
    """Verify that a certain text was center printed for the player.

    **The player needs to be set up via :func:`.fake_player(steam_id, name, team, ping)` before using this assertion.**

    **Make sure to use :func:`mockito.unstub()` after calling this assertion to avoid side effects spilling into the
    next test.**

    :param: player: the player that should have received the matching center print
    :param: matcher: matches the text the player should have received. This might be :class:`mockito.matchers` to check
    for certain types of messages.
    :param: times: The amount of times the player should have been received the matching message, set to 0 for no
    message center printed to the player. (default: 1).
    :return:
    """
    verify(player, times=times).center_print(matcher)


class PlayerMatcher(Matcher):
    """
    A custom mockito matcher that matches minqlx.Players by their name and steam_id.
    """

    def __init__(self, wanted_player: Player):
        self.wanted_player: Player = wanted_player

    def matches(self, arg: Player) -> bool:
        return (
            self.wanted_player.steam_id == arg.steam_id
            and self.wanted_player.name == arg.name
        )

    def __repr__(self) -> str:
        return f"<Player: id={self.wanted_player.steam_id}, name={self.wanted_player.name}>"


def player_that_matches(player: Player) -> Matcher:
    """
    Matches against a given player by their name and steam_id.
    """
    return PlayerMatcher(player)

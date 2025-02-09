import functools
from typing import Optional

from mockito import when2, mock, verify  # type: ignore

import minqlx
from minqlx import Game, NonexistentGameError

# Functions for setting up the state of the game currently active on the server.


def setup_no_game():
    """Set up the server with no game running currently.

    **Make sure to use :func:`mockito.unstub()` after calling this assertion to avoid side effects spilling into the
    next test.**
    """
    when2(minqlx.Game).thenRaise(
        NonexistentGameError("Tried to instantiate a game while no game is active.")
    )


def setup_game_in_warmup(
    *,
    game_type: str = "ca",
    mapname: str = "campgrounds",
    map_title: Optional[str] = None,
    roundlimit: int = 8,
    maxclients: int = 16,
) -> None:
    """Set up the server with a game currently in warmup mode.

    **Make sure to use :func:`mockito.unstub()` after calling this assertion to avoid side effects spilling into the
    next test.**

    :param: game_type: the game_type currently being played (default: "ca")
    :param: mapname: the map the game is currently running on (default: "campgrounds")
    :param: map_title: the long title of the map (default: None)
    :param: roundlimit: (default: 8)
    :param: maxclients: (default: 16)
    """
    mock_game = mock(spec=Game, strict=False)
    when2(minqlx.Game).thenReturn(mock_game)
    mock_game.state = "warmup"
    mock_game.type_short = game_type
    mock_game.map = mapname
    mock_game.map_title = map_title
    mock_game.roundlimit = roundlimit
    mock_game.maxclients = maxclients
    mock_game.assert_addteamscore = functools.partial(assert_game_addteamscore)


def setup_game_in_progress(
    *,
    game_type: str = "ca",
    mapname: str = "campgrounds",
    map_title: Optional[str] = None,
    roundlimit: int = 8,
    red_score: int = 0,
    blue_score: int = 0,
    maxclients: int = 16,
) -> None:
    """Set up the server with a game currently in progress. You may specify the game_type, roundlimit, and score for
    the red and blue teams with the optional parameters.

    **Make sure to use :func:`mockito.unstub()` after calling this assertion to avoid side effects spilling into the
    next test.**

    :param game_type: the game_type currently being played (default: "ca")
    :param mapname: the map the game is currently running on (default: "campgrounds")
    :param map_title: the long title of the map (default: None)
    :param roundlimit: the current setup roundlimit for the game (default: 8)
    :param red_score: the current score of the red team (default: 0)
    :param blue_score: the current score of the blue team (default: 0)
    :param maxclients: (default: 16)
    """
    mock_game = mock(spec=Game, strict=False)
    when2(minqlx.Game).thenReturn(mock_game)
    mock_game.state = "in_progress"
    mock_game.type_short = game_type
    mock_game.map = mapname
    mock_game.map_title = map_title
    mock_game.roundlimit = roundlimit
    mock_game.red_score = red_score
    mock_game.blue_score = blue_score
    mock_game.maxclients = maxclients
    mock_game.assert_addteamscore = assert_game_addteamscore


def assert_game_addteamscore(*, team: str, score: int, _times: int = 1) -> None:
    """Verify that the score of the team was manipulated by the given amount.

    **The test needs to be set up via :func:`.setUp_game_in_warmup()` or :func:`.setup_game_in_progress()`
    before using this assertion.**

    **Make sure to use :func:`mockito.unstub()` after calling this assertion to avoid side effects spilling into the
    next test.**

    :param: team: the team for which the team score should have been manipualted
    :param: score: the amount that should have been added to the team's score. This may be negative or a matcher.
    :param: times: the amount of times the function addteamscore should have been called. (default: 1)
    """
    verify(minqlx.Game(), times=_times).addteamscore(team, score)

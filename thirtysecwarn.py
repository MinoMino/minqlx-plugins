import time
import random
import threading

import minqlx
from minqlx import Plugin


# noinspection PyPep8Naming
class thirtysecwarn(Plugin):
    """Created by Thomas Jones on 01/09/2016 - thomas@tomtecsolutions.com

    thirtysecwarn.py - a minqlx plugin to play unused VO when a CA game is nearing the round time limit.

    This plugin is released to everyone, for any purpose. It comes with no warranty, no guarantee it works, it's
    released AS IS.

    You can modify everything, except for lines 1-4 and the !tomtec_versions code.
    They're there to indicate I whacked this together originally. Please make it better :D

    Completely rebuild by iouonegirl and Gelenkbusfahrer on 25/09/2017, customization of sounds and unit tests added by
    ShiN0 somewhen in October 2017
    """

    def __init__(self):
        super().__init__()

        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)
        self.add_hook("game_start", self.handle_game_start)

        self.set_cvar_once("qlx_thirtySecondWarnAnnouncer", "standard")

        self.announcerMap = {
            "standard": "sound/vo/30_second_warning.ogg",
            "female": "sound/vo_female/30_second_warning.ogg",
            "evil": "sound/vo_evil/30_second_warning.ogg",
        }

        self.warner_thread_name = None

    def handle_game_start(self, _game):
        self.warner_thread_name = None

    def handle_round_end(self, _data):
        self.warner_thread_name = None

    def handle_round_start(self, _round_number):
        self.warntimer()

    @minqlx.thread
    def warntimer(self):
        warner_thread_name = threading.current_thread().name
        self.warner_thread_name = warner_thread_name
        roundtimelimit = self.get_cvar("roundtimelimit", int) or 150
        timer_delay = roundtimelimit - 30
        time.sleep(timer_delay)
        self.play_thirty_second_warning(warner_thread_name)

    @minqlx.next_frame
    def play_thirty_second_warning(self, warner_thread_name):
        if not self.game:
            return
        if not self.game.type_short == "ca":
            return
        if not self.game.state == "in_progress":
            return
        if not self.warner_thread_name == warner_thread_name:
            return

        # passed all conditions, play sound
        Plugin.play_sound(self.get_announcer_sound())

    def get_announcer_sound(self):
        qlx_thirty_second_warn_announcer = self.get_cvar("qlx_thirtySecondWarnAnnouncer")

        if qlx_thirty_second_warn_announcer == "random":
            return self.random_announcer()

        if qlx_thirty_second_warn_announcer not in self.announcerMap:
            qlx_thirty_second_warn_announcer = "standard"
        return self.announcerMap[qlx_thirty_second_warn_announcer]

    def random_announcer(self):
        key, sound = random.choice(list(self.announcerMap.items()))
        return sound

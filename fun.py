# minqlx - A Quake Live server administrator bot.
# Copyright (C) 2015 Mino <mino@minomino.org>

# This file is part of minqlx.

# minqlx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# minqlx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

import minqlx
import random
import time
import re

from minqlx.database import Redis

_re_hahaha_yeah = re.compile(r"^haha(?:ha)?,? yeah?\W?$", flags=re.IGNORECASE)
_re_haha_yeah_haha = re.compile(r"^haha(?:ha)?,? yeah?,? haha\W?$", flags=re.IGNORECASE)
_re_yeah_hahaha = re.compile(r"^yeah?,? haha(?:ha)\W?$", flags=re.IGNORECASE)
_re_duahahaha = re.compile(r"^duahaha(?:ha)?\W?$", flags=re.IGNORECASE)
_re_hahaha = re.compile(r"hahaha", flags=re.IGNORECASE)
_re_haahaahaa = re.compile(r"haahaahaa", flags=re.IGNORECASE)
_re_glhf = re.compile(r"^(?:gl ?hf\W?)|(?:hf\W?)|(?:gl hf\W?)", flags=re.IGNORECASE)
_re_f3 = re.compile(r"^(?:(?:press )?f3)|ready(?: up)?\W?", flags=re.IGNORECASE)
_re_welcome = re.compile(r"^welcome to (?:ql|quake live)\W?$", flags=re.IGNORECASE)
_re_go = re.compile(r"^go\W?$", flags=re.IGNORECASE)
_re_win = re.compile(r"^you win\W?$", flags=re.IGNORECASE)
_re_lose = re.compile(r"^you lose\W?$", flags=re.IGNORECASE)
_re_beep_boop = re.compile(r"^beep boop\W?$", flags=re.IGNORECASE)
_re_denied = re.compile(r"^denied\W?$", flags=re.IGNORECASE)
_re_balls_out = re.compile(r"^ball'?s out\W?$", flags=re.IGNORECASE)
_re_one = re.compile(r"^one\W?$", flags=re.IGNORECASE)
_re_two = re.compile(r"^two\W?$", flags=re.IGNORECASE)
_re_three = re.compile(r"^three\W?$", flags=re.IGNORECASE)
_re_fight = re.compile(r"^fight\W?$", flags=re.IGNORECASE)
_re_gauntlet = re.compile(r"^gauntlet\W?$", flags=re.IGNORECASE)
_re_humiliation = re.compile(r"^humiliation\W?$", flags=re.IGNORECASE)
_re_perfect = re.compile(r"^perfect\W?$", flags=re.IGNORECASE)
_re_wah = re.compile(r"^wa+h wa+h wa+h wa+h\W?$", flags=re.IGNORECASE)
_re_ah = re.compile(r"^a+h a+h a+h\W?$", flags=re.IGNORECASE)
_re_oink = re.compile(r"^oink\W?$", flags=re.IGNORECASE)
_re_argh = re.compile(r"^a+rgh\W?$", flags=re.IGNORECASE)
_re_hah_haha = re.compile(r"^hah haha\W?$", flags=re.IGNORECASE)
_re_woohoo = re.compile(r"^woo+hoo+\W?$", flags=re.IGNORECASE)
_re_quakelive = re.compile(r"^(?:ql|quake live)\W?$", flags=re.IGNORECASE)
_re_chaching = re.compile(r"(?:\$|€|£)\d+", flags=re.IGNORECASE)
_re_uh_ah = re.compile(r"^uh ah$", flags=re.IGNORECASE)
_re_oohwee = re.compile(r"^ooh+wee\W?$", flags=re.IGNORECASE)
_re_erah = re.compile(r"^erah\W?$", flags=re.IGNORECASE)
_re_yeahhh = re.compile(r"^yeahhh\W?$", flags=re.IGNORECASE)
_re_scream = re.compile(r"^scream\W?$", flags=re.IGNORECASE)
_re_salute = re.compile(r"^salute\W?$", flags=re.IGNORECASE)
_re_squish = re.compile(r"^squish\W?$", flags=re.IGNORECASE)
_re_oh_god = re.compile(r"^oh god\W?$", flags=re.IGNORECASE)
_re_snarl = re.compile(r"^snarl\W?$", flags=re.IGNORECASE)

class fun(minqlx.Plugin):
    database = Redis

    def __init__(self):
        super().__init__()
        self.add_hook("chat", self.handle_chat)
        self.add_command("cookies", self.cmd_cookies)
        self.last_sound = None

        self.set_cvar_once("qlx_funSoundDelay", "3")

    def handle_chat(self, player, msg, channel):
        if channel != "chat":
            return

        msg = self.clean_text(msg)
        if _re_hahaha_yeah.match(msg):
            self.play_sound("sound/player/lucy/taunt.wav")
        elif _re_haha_yeah_haha.match(msg):
            self.play_sound("sound/player/biker/taunt.wav")
        elif _re_yeah_hahaha.match(msg):
            self.play_sound("sound/player/razor/taunt.wav")
        elif _re_duahahaha.match(msg):
            self.play_sound("sound/player/keel/taunt.wav")
        elif _re_hahaha.search(msg):
            self.play_sound("sound/player/santa/taunt.wav")
        elif _re_haahaahaa.search(msg):
            self.play_sound("sound/player/visor/taunt.wav")
        elif _re_glhf.match(msg):
            self.play_sound("sound/vo/crash_new/39_01.wav")
        elif _re_f3.match(msg):
            self.play_sound("sound/vo/crash_new/36_04.wav")
        elif "holy shit" in msg.lower():
            self.play_sound("sound/vo_female/holy_shit")
        elif _re_welcome.match(msg):
            self.play_sound("sound/vo_evil/welcome")
        elif _re_go.match(msg):
            self.play_sound("sound/vo/go")
        elif _re_beep_boop.match(msg):
            self.play_sound("sound/player/tankjr/taunt.wav")
        elif _re_win.match(msg):
            self.play_sound("sound/vo_female/you_win.wav")
        elif _re_lose.match(msg):
            self.play_sound("sound/vo/you_lose.wav")
        elif "impressive" in msg.lower():
            self.play_sound("sound/vo_female/impressive1.wav")
        elif "excellent" in msg.lower():
            self.play_sound("sound/vo_evil/excellent1.wav")
        elif _re_denied.match(msg):
            self.play_sound("sound/vo/denied")
        elif _re_balls_out.match(msg):
            self.play_sound("sound/vo_female/balls_out")
        elif _re_one.match(msg):
            self.play_sound("sound/vo_female/one")
        elif _re_two.match(msg):
            self.play_sound("sound/vo_female/two")
        elif _re_three.match(msg):
            self.play_sound("sound/vo_female/three")
        elif _re_fight.match(msg):
            self.play_sound("sound/vo_evil/fight")
        elif _re_gauntlet.match(msg):
            self.play_sound("sound/vo_evil/gauntlet")
        elif _re_humiliation.match(msg):
            self.play_sound("sound/vo_evil/humiliation1")
        elif _re_perfect.match(msg):
            self.play_sound("sound/vo_evil/perfect")
        elif _re_wah.match(msg):
            self.play_sound("sound/misc/yousuck")
        elif _re_ah.match(msg):
            self.play_sound("sound/player/slash/taunt.wav")
        elif _re_oink.match(msg):
            self.play_sound("sound/player/sorlag/pain50_1.wav")
        elif _re_argh.match(msg):
            self.play_sound("sound/player/doom/taunt.wav")
        elif _re_hah_haha.match(msg):
            self.play_sound("sound/player/hunter/taunt.wav")
        elif _re_woohoo.match(msg):
            self.play_sound("sound/player/janet/taunt.wav")
        elif _re_quakelive.match(msg):
            self.play_sound("sound/vo_female/quake_live")
        elif _re_chaching.search(msg):
            self.play_sound("sound/misc/chaching")
        elif _re_uh_ah.match(msg):
            self.play_sound("sound/player/mynx/taunt.wav")
        elif _re_oohwee.match(msg):
            self.play_sound("sound/player/anarki/taunt.wav")
        elif _re_erah.match(msg):
            self.play_sound("sound/player/bitterman/taunt.wav")
        elif _re_yeahhh.match(msg):
            self.play_sound("sound/player/major/taunt.wav")
        elif _re_scream.match(msg):
            self.play_sound("sound/player/bones/taunt.wav")
        elif _re_salute.match(msg):
            self.play_sound("sound/player/sarge/taunt.wav")
        elif _re_squish.match(msg):
            self.play_sound("sound/player/orb/taunt.wav")
        elif _re_oh_god.match(msg):
            self.play_sound("sound/player/ranger/taunt.wav")
        elif _re_snarl.match(msg):
            self.play_sound("sound/player/sorlag/taunt.wav")

    def play_sound(self, path):
        if not self.last_sound:
            pass
        elif time.time() - self.last_sound < self.get_cvar("qlx_funSoundDelay", int):
            return

        self.last_sound = time.time()
        for p in self.players():
            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                super().play_sound(path, p)

    def cmd_cookies(self, player, msg, channel):
        x = random.randint(0, 100)
        if not x:
            channel.reply("^6♥ ^7Here you go, {}. I baked these just for you! ^6♥".format(player))
        elif x == 1:
            channel.reply("What, you thought ^6you^7 would get cookies from me, {}? Hah, think again.".format(player))
        elif x < 50:
            channel.reply("For me? Thank you, {}!".format(player))
        else:
            channel.reply("I'm out of cookies right now, {}. Sorry!".format(player))

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
import threading
import asyncio
import random
import time
import sys
import re

# Colors using the mIRC color standard palette (which several other clients also comply with).
COLORS = ("\x0301", "\x0304", "\x0303", "\x0308", "\x0302", "\x0311", "\x0306", "\x0300")

class irc(minqlx.Plugin):
    def __init__(self):
        self.add_hook("chat", self.handle_chat, priority=minqlx.PRI_LOWEST)
        self.add_hook("unload", self.handle_unload)
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_LOWEST)
        self.add_hook("player_disconnect", self.handle_player_disconnect, priority=minqlx.PRI_LOWEST)

        self.set_cvar_once("qlx_ircServer", "irc.quakenet.org")
        self.set_cvar_once("qlx_ircRelayChannel", "")
        self.set_cvar_once("qlx_ircIdleChannels", "")
        self.set_cvar_once("qlx_ircNickname", "minqlx-{}".format(random.randint(1000, 9999)))
        self.set_cvar_once("qlx_ircPassword", "")
        self.set_cvar_once("qlx_ircColors", "0")

        self.server = self.get_cvar("qlx_ircServer")
        self.relay = self.get_cvar("qlx_ircRelayChannel")
        self.idle = self.get_cvar("qlx_ircIdleChannels", list)
        self.nickname = self.get_cvar("qlx_ircNickname")
        self.password = self.get_cvar("qlx_ircPassword")

        self.authed = set()
        self.auth_attempts = {}

        if not self.server:
            self.logger.warning("IRC plugin loaded, but no IRC server specified.")
        elif not self.relay and not self.idle and not self.password:
            self.logger.warning("IRC plugin loaded, but no channels or password set. Not connecting.")
        else:
            self.irc = SimpleAsyncIrc(self.server, self.nickname, self.handle_msg, self.handle_perform, self.handle_raw)
            self.irc.start()
            self.logger.info("Connecting to {}...".format(self.server))

    def handle_chat(self, player, msg, channel):
        if self.irc and self.relay and channel == "chat":
            text = "^7<{}> ^2{}".format(player.name, msg)
            self.irc.msg(self.relay, self.translate_colors(text))

    def handle_unload(self, plugin):
        if plugin == self.__class__.__name__ and self.irc and self.irc.is_alive():
            self.irc.quit("Plugin unloaded!")
            self.irc.stop()

    def handle_player_connect(self, player):
        if self.irc and self.relay:
            self.irc.msg(self.relay, self.translate_colors("{} connected.".format(player.name)))

    def handle_player_disconnect(self, player, reason):
        if reason and reason[-1] not in ("?", "!", "."):
            reason = reason + "."
        
        if self.irc and self.relay:
            self.irc.msg(self.relay, self.translate_colors("{} {}".format(player.name, reason)))

    def handle_msg(self, irc, user, channel, msg):
        if channel == self.relay:
            minqlx.CHAT_CHANNEL.reply("[IRC] ^6{}^7:^2 {}".format(user[0], " ".join(msg)))
        elif channel == user[0]: # Is PM?
            if len(msg) > 1 and msg[0].lower() == ".auth":
                if user in self.authed:
                    irc.msg(channel, "You are already authenticated.")
                elif msg[1] == self.password:
                    self.authed.add(user)
                    irc.msg(channel, "You have been successfully authenticated. You can now use .qlx to execute commands.")
                else:
                    # Allow up to 3 attempts for the user's IP to authenticate.
                    if user[2] not in self.auth_attempts:
                        self.auth_attempts[user[2]] = 3
                    self.auth_attempts[user[2]] -= 1
                    if self.auth_attempts[user[2]] > 0:
                        irc.msg(channel, "Wrong password. You have {} attempts left.".format(self.auth_attempts[user[2]]))
            elif len(msg) > 1 and user in self.authed and msg[0].lower() == ".qlx":
                try:
                    minqlx.COMMANDS.handle_input(IrcDummyPlayer(self.irc, user[0]), " ".join(msg[1:]), IrcChannel(self.irc, user[0]))
                except Exception as e:
                    irc.msg(channel, "{}: {}".format(e.__class__.__name__, e))
                    minqlx.log_exception()

    def handle_perform(self, irc):
        self.logger.info("Connected to IRC!".format(self.server))
        for channel in self.idle:
            irc.join(channel)
        if self.relay:
            irc.join(self.relay)

    def handle_raw(self, irc, msg):
        split_msg = msg.split()
        if len(split_msg) > 2 and split_msg[1] == "NICK":
            user = re_user.match(split_msg[0][1:])
            if user and user.groups() in self.authed:
                # Update nick if an authed user changed it.
                self.authed.remove(user.groups())
                self.authed.add((split_msg[2][1:], *user.groups()[1:]))
        elif len(split_msg) > 1 and split_msg[1] == "433":
            irc.nick(irc.nickname + "_")

    @classmethod
    def translate_colors(cls, text):
        if not cls.get_cvar("qlx_ircColors", bool):
            return cls.clean_text(text)

        for i, color in enumerate(COLORS):
            text = text.replace("^{}".format(i), color)

        return text

# ====================================================================
#                     DUMMY PLAYER & IRC CHANNEL
# ====================================================================

class IrcChannel(minqlx.AbstractChannel):
    name = "irc"
    def __init__(self, irc, recipient):
        self.irc = irc
        self.recipient = recipient

    def __repr__(self):
        return "{} {}".format(str(self), self.recipient)

    def reply(self, msg):
        self.irc.msg(self.recipient, irc.translate_colors(msg))

class IrcDummyPlayer(minqlx.AbstractDummyPlayer):
    def __init__(self, irc, user):
        self.irc = irc
        self.user = user
        super().__init__()
    
    @property
    def steam_id(self):
        return minqlx.owner()

    def tell(self, msg):
        self.irc.msg(self.user, irc.translate_colors(msg))

# ====================================================================
#                        SIMPLE ASYNC IRC
# ====================================================================

re_msg = re.compile(r"^:([^ ]+) PRIVMSG ([^ ]+) :(.*)$")
re_user = re.compile(r"^(.+)!(.+)@(.+)$")

class SimpleAsyncIrc(threading.Thread):
    def __init__(self, address, nickname, msg_handler, perform_handler, raw_handler=None, stop_event=threading.Event()):
        split_addr = address.split(":")
        self.host = split_addr[0]
        self.port = int(split_addr[1]) if len(split_addr) > 1 else 6667
        self.nickname = nickname
        self.msg_handler = msg_handler
        self.perform_handler = perform_handler
        self.raw_handler = raw_handler
        self.stop_event = stop_event
        self.reader = None
        self.writer = None
        self.server_options = {}
        super().__init__()

        self._lock = threading.Lock()
        self._old_nickname = self.nickname

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while not self.stop_event.is_set():
            loop.run_until_complete(self.connect())
            # Disconnected. Try reconnecting in 60 seconds.
            time.sleep(60)
        loop.close()

    def stop(self):
        self.stop_event.set()

    def write(self, msg):
        if self.writer:
            with self._lock:
                self.writer.write(msg.encode(errors="ignore"))

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        self.write("NICK {0}\r\nUSER {0} 0 * :{0}\r\n".format(self.nickname))
        
        while not self.stop_event.is_set():
            line = await self.reader.readline()
            if not line:
                break
            line = line.decode("utf-8", errors="ignore").rstrip()
            if line:
                await self.parse_data(line)

        self.write("QUIT Quit by user.\r\n")
        self.writer.close()

    async def parse_data(self, msg):
        split_msg = msg.split()
        if len(split_msg) > 1 and split_msg[0] == "PING":
            self.pong(split_msg[1].lstrip(":"))
        elif len(split_msg) > 3 and split_msg[1] == "PRIVMSG":
            r = re_msg.match(msg)
            user = re_user.match(r.group(1)).groups()
            channel = user[0] if self.nickname == r.group(2) else r.group(2)
            self.msg_handler(self, user, channel, r.group(3).split())
        elif len(split_msg) > 2 and split_msg[1] == "NICK":
            user = re_user.match(split_msg[0][1:])
            if user and user.group(1) == self.nickname:
                self.nickname = split_msg[2][1:]
        elif split_msg[1] == "005":
            for option in split_msg[3:-1]:
                opt_pair = option.split("=", 1)
                if len(opt_pair) == 1:
                    self.server_options[opt_pair[0]] = ""
                else:
                    self.server_options[opt_pair[0]] = opt_pair[1]
        elif len(split_msg) > 1 and split_msg[1] == "433":
            self.nickname = self._old_nickname
        # Stuff to do after we get the MOTD.
        elif re.match(r":[^ ]+ (376|422) .+", msg):
            self.perform_handler(self)

        # If we have a raw handler, let it do its stuff now.
        if self.raw_handler:
            self.raw_handler(self, msg)

    def msg(self, recipient, msg):
        self.write("PRIVMSG {} :{}\r\n".format(recipient, msg))

    def nick(self, nick):
        with self._lock:
            self._old_nickname = self.nickname
            self.nickname = nick
        self.write("NICK {}\r\n".format(nick))

    def join(self, channels):
        self.write("JOIN {}\r\n".format(channels))

    def part(self, channels):
        self.write("PART {}\r\n".format(channels))

    def mode(self, what, mode):
        self.write("MODE {} {}\r\n".format(what, mode))

    def kick(self, channel, nick, reason):
        self.write("KICK {} {}:{}\r\n".format(channel, nick, reason))

    def quit(self, reason):
        self.write("QUIT :{}\r\n".format(reason))

    def pong(self, n):
        self.write("PONG :{}\r\n".format(n))

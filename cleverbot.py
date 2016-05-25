# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# If you have any suggestions or issues/problems with this plugin you can contact me(kanzo) on irc at #minqlbot
# or alternatively you can open an issue at https://github.com/cstewart90/minqlx-plugins/issues

"""
You can talk to cleverbot using !chat and it will respond.
The bot can also respond to chat randomly if you set `qlx_cleverbotChance`.
Uses https://cleverbot.io API.
"""

import minqlx
import requests
import random


class cleverbot(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("chat", self.handle_chat)
        self.add_command("create", self.cmd_create, 2, usage="<nick>")
        self.add_command("chat", self.cmd_chat, usage="<some text>")
        self.add_command("chance", self.cmd_chance, 2, usage="<chance>")

        # Get an API key at cleverbot.io
        self.set_cvar_once("qlx_cleverbotUser", "")
        self.set_cvar_once("qlx_cleverbotKey", "")
        self.set_cvar_once("qlx_cleverbotNick", "Cleverbot")
        # Percentage chance to respond to chat, float between 0 and 1.
        self.set_cvar_limit_once("qlx_cleverbotChance", "0", "0", "1")

        self.created = False
        self.post_data("create")

    def handle_chat(self, player, msg, channel):
        """Responds to chat messages
        `qlx_cleverbotChance` * 100 percent of the time.
        """
        if msg.startswith(self.get_cvar("qlx_commandPrefix")) or channel != "chat":
            return

        try:
            chance = self.get_cvar("qlx_cleverbotChance", float)
        except ValueError:
            self.logger.warning("qlx_cleverbotChance is not a valid float.")
            return

        if random.random() < chance:
            msg = self.clean_text(msg)
            self.post_data("ask", msg, channel)

    def cmd_create(self, player, msg, channel):
        """Creates the bot with the nick given.
        API Doc: https://docs.cleverbot.io/docs/getting-started"""
        if len(msg) == 1:
            return minqlx.RET_USAGE

        nick = ' '.join(msg[1:])
        self.set_cvar("qlx_cleverbotNick", nick)
        self.post_data("create", channel=channel)

    def cmd_chat(self, player, msg, channel):
        """Responds to !chat some text
        Example: !chat Just a small town girl
        cleverbot: Livin' in a lonely world
        API Doc: https://docs.cleverbot.io/docs/querying-cleverbot
        """
        if len(msg) == 1:
            return minqlx.RET_USAGE
        else:
            text = ' '.join(msg[1:])

        if self.created:
            self.post_data("ask", text, channel)
        else:
            channel.reply("^3You need to create the bot or set API key first.")

    def cmd_chance(self, player, msg, channel):
        """Sets chance that the bot responds to chat.
        If you just do !chance with no args it will output current chance."""
        if len(msg) == 1:
            chance = self.get_cvar("qlx_cleverbotChance")
            channel.reply("Chance is currently {}".format(chance))
            return minqlx.RET_STOP_ALL
        elif len(msg) > 2:
            return minqlx.RET_USAGE

        try:
            chance = float(msg[1])
            if not 0 <= chance <= 1:
                raise ValueError
        except ValueError:
            channel.reply("{} is not a valid float between 0 and 1.".format(msg[1]))
            return minqlx.RET_STOP_ALL

        self.set_cvar("qlx_cleverbotChance", str(chance))
        channel.reply("Chance was set to {}".format(chance))
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def post_data(self, path, text='', channel=None):
        """POSTs data to cleverbot.io
        :param path: API path, either ask or create
        :param text: Text to query the the bot with
        :param channel: Channel to reply to(usually chat)
        """
        user = self.get_cvar("qlx_cleverbotUser")
        key = self.get_cvar("qlx_cleverbotKey")
        nick = self.get_cvar("qlx_cleverbotNick")
        if nick == "":
            self.msg("^3Bot nick cannot be blank.")
            return
        if user and key:
            payload = {"user": user, "key": key, "nick": nick, "text": text}
            try:
                r = requests.post("https://cleverbot.io/1.0/{}".format(path), data=payload)
                r.raise_for_status()
                self.callback(r.json(), channel)
                return
            except requests.exceptions.RequestException as e:
                self.logger.error(e)
        else:
            self.msg("^3You need to set qlx_cleverbotUser and qlx_cleverbotKey")

    def callback(self, response, channel=None):
        """Responds to chat with the response from the bot.
        Called after data has been POSTed.
        :param response: JSON data from cleverbot.io
        :param channel: Channel to reply to
        """
        nick = self.get_cvar("qlx_cleverbotNick")
        if "response" in response:
            channel.reply("^6{}^7: {}".format(nick, response["response"]))
        else:
            self.created = True
            msg = "^7Bot called ^6{} ^7was created.".format(nick)
            if channel:
                channel.reply(msg)
            else:
                self.msg(msg)

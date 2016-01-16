# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
You can talk to cleverbot using !chat and it will respond.
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
        self.add_command("chance", self.cmd_chance, 2, usage="<chance (0-1>")

        # Get an API key at cleverbot.io
        self.set_cvar_once("qlx_cleverbotUser", "")
        self.set_cvar_once("qlx_cleverbotKey", "")
        self.set_cvar_once("qlx_cleverbotNick", "cleverbot")
        # Percentage chance to respond to chat, float between 0 and 1.
        self.set_cvar_limit_once("qlx_cleverbotChance", "0", "0", "1")

        self.created = False
        self.create()

    def handle_chat(self, player, msg, channel):
        """Responds to chat message qlx_cleverbotChance * 100 percent of the time"""
        if msg.startswith(self.get_cvar("qlx_commandPrefix")) or channel != "chat":
            return

        try:
            chance = self.get_cvar("qlx_cleverbotChance", float)
        except ValueError:
            self.logger.info("cleverbot: qlx_cleverbotChance is not a valid float.")
            return

        if random.random() < chance:
            msg = self.clean_text(msg)
            self.ask(msg, channel)

    def cmd_create(self, player, msg, channel):
        """Creates the bot with the nick given."""
        if len(msg) != 2:
            return minqlx.RET_USAGE

        self.set_cvar("qlx_cleverbotNick", msg[1])
        self.create()

    def cmd_chat(self, player, msg, channel):
        """Responds to !chat some text
        Example: !chat Just a small town girl
        cleverbot: Livin' in a lonely world
        """
        if len(msg) == 1:
            return minqlx.RET_USAGE
        else:
            text = ' '.join(msg[1:])

        if self.created:
            self.ask(text, channel)
        else:
            channel.reply("^3You need to create the bot or set API key first.")

    def cmd_chance(self, player, msg, channel):
        """Sets the chance that the bot responds to chat."""
        if len(msg) == 1:
            chance = self.get_cvar("qlx_cleverbotChance")
            channel.reply("Chance is currently {}".format(chance))
        if len(msg) > 2:
            return minqlx.RET_USAGE

        chance = 0
        try:
            chance = float(msg[1])
        except ValueError:
            channel.reply("{} is not a valid float.".format(msg[1]))

        if 0 <= chance <= 1:
            self.set_cvar("qlx_cleverbotChance", str(chance))
            channel.reply("Chance was set to {}".format(chance))
        else:
            channel.reply("Chance must be between 0 and 1.")

    @minqlx.thread
    def create(self):
        """Creates the bot.
        Doc: https://docs.cleverbot.io/docs/getting-started
        """
        response = self.post_data("https://cleverbot.io/1.0/create")
        if response:
            nick = self.get_cvar("qlx_cleverbotNick")
            self.msg("^7Bot called ^6{} ^7was created.".format(nick))
            self.created = True

    @minqlx.thread
    def ask(self, text, channel):
        """Doc: https://cleverbot.io/1.0/ask
        :param text: Text to send to the bot.
        :param channel: Channel to reply to.
        """
        response = self.post_data("https://cleverbot.io/1.0/ask", text)
        if response:
            nick = self.get_cvar("qlx_cleverbotNick")
            channel.reply("^6{}^7: {}".format(nick, response["response"]))

    def post_data(self, url, text=''):
        """POSTS data to cleverbot.io
        :param url: The url to POST to, either /ask or /create.
        :param text: The text to send to the bot.
        :return: JSON response.
        """
        user = self.get_cvar("qlx_cleverbotUser")
        key = self.get_cvar("qlx_cleverbotKey")
        nick = self.get_cvar("qlx_cleverbotNick")
        if nick == "":
            self.msg("^3Bot nick cannot be blank.")
            return
        if user and key:
            payload = {"user": user, "key": key, "nick": nick, "text": text}
            r = requests.post(url, data=payload)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 400:
                self.msg("^1Bad request.")
            else:
                self.msg("^1Error: ^7{}, {}".format(r.status_code, r.reason))
        else:
            self.msg("^3You need to set qlx_cleverbotUser and qlx_cleverbotKey")

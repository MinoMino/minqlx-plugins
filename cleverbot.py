# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
You can talk to cleverbot using !chat and it will respond.
"""

import minqlx
import threading
import requests


class cleverbot(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_command("create", self.cmd_chat, usage="<nick>")
        self.add_command("chat", self.cmd_chat, usage="<question>")

        # Get an API key at cleverbot.io
        self.set_cvar_once("qlx_cleverbotUser", "")
        self.set_cvar_once("qlx_cleverbotKey", "")
        self.set_cvar_once("qlx_cleverbotNick", "cleverbot")

        self.created = False
        threading.Thread(target=self.create).start()

    def create(self):
        """Creates the bot.
        Doc: https://docs.cleverbot.io/docs/getting-started"""
        user = self.get_cvar("qlx_cleverbotUser")
        key = self.get_cvar("qlx_cleverbotKey")
        nick = self.get_cvar("qlx_cleverbotNick")
        if nick == "":
            self.msg("Bot nick cannot be blank.")
            return
        if user and key:
            payload = {"user": user, "key": key, "nick": nick}
            r = requests.post("https://cleverbot.io/1.0/create", data=payload)
            if r.status_code == 200:
                self.msg("Bot called {} was created".format(nick))
                self.created = True
            elif r.status_code == 400:
                self.msg("Bad request.")
            else:
                self.msg("Error: {}, Reason: {}".format(r.status_code, r.reason))
        else:
            self.msg("You need to set qlx_cleverbotUser and qlx_cleverbotKey")

    def cmd_create(self, player, msg, channel):
        """Creates the bot with the nick supplied."""
        if len(msg) != 2:
            return minqlx.RET_USAGE

        self.set_cvar("qlx_cleverbotNick", msg[1])
        threading.Thread(target=self.create).start()

    def cmd_chat(self, player, msg, channel):
        """Responds to !chat some text
        Example: !chat Just a small town girl
        cleverbot: Livin' in a lonely world"""
        if len(msg) == 1:
            return minqlx.RET_USAGE
        else:
            text = ' '.join(msg[1:])

        if self.created:
            threading.Thread(target=self.ask(text, channel)).start()
        else:
            channel.reply("You need to create the bot or set API key first.")

    def ask(self, text, channel):
        """Doc: https://cleverbot.io/1.0/ask
        :param text: Question or statement to ask the bot:
        :param channel: Channel to reply to.
        """
        user = self.get_cvar("qlx_cleverbotUser")
        key = self.get_cvar("qlx_cleverbotKey")
        nick = self.get_cvar("qlx_cleverbotNick")

        payload = {"user": user, "key": key, "nick": nick, "text": text}
        r = requests.post("https://cleverbot.io/1.0/ask", data=payload)
        if r.status_code == 200:
            response = r.json()["response"]
            channel.reply("^3{}: ^7{}".format(nick, response))
        elif r.status_code == 400:
            self.msg("Bad request.")
        else:
            self.msg("Error: {}, Reason: {}".format(r.status_code, r.reason))

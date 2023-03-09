#####
# The Telegram BOT
# Relay ingame chat to the chatbot in Telegram
# Requires: 
#   pyTelegramBOTAPI (https://pypi.org/project/pyTelegramBotAPI/)
#   Create a .env file to store your API_KEY
#   Make sure this is installed on your server.
#   Add the module into the minqlx.zip file on the server on the
#   path ~/steamapps/common/qlds
#   
#   Create a new bot using the Bot Father.
#   CHAT_ID is the chat id used in Telegram app.
#   API_KEY is the key token for your bot.
#####

import minqlx
import os
import telebot
import time

VERSION = "v0.1"
#API_KEY = os.getenv('API_KEY')
API_KEY = "6074681084:AAGSjqYnAzXEGBgaYWH11b5S2Zp-_l9-3sc"
CHAT_ID = "-962006238"
CHAT_ID_KEY = "minqlx:telegrambot:chatid:{}"
TELEGRAM_API_KEY = "minqlx:telegrambot:apikey:{}"

bot = telebot.TeleBot(API_KEY)

class telegrambot(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        
        self.add_hook("chat", self.handle_chat)
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_LOWEST)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("client_command", self.handle_client_command, priority=minqlx.PRI_HIGH)
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("unload", self.handle_unload)

        self.set_cvar_once("qlx_chatrelayenabled", "1")
        self.set_cvar_once("qlx_cmdrelayenabled", "0")
        self.set_cvar_once("qlx_plrelayenabled", "1")
        self.set_cvar_once("qlx_voterelayenabled", "1")

        self.add_command("testpl", self.testpl)
        self.add_command("setchatid", self.chatid, 2, usage="<CHAT_ID>")
        self.add_command("setapikey", self.apikey, 2, usage="<API_KEY>")
        self.add_command("showtelegramkeys", self.telebotkey, 2)

        self.running = False
        self.chatidk = ""
        self.apikeyk = ""

        self.loadkeys()

    ###################### DB ######################
    @minqlx.thread
    def loadkeys(self):
        # Get API KEY in DB
        apikeylist = self.db.keys(TELEGRAM_API_KEY.format("*"))
        for k in apikeylist:
            self.apikeyk = k

        if self.apikeyk == "":
            self.msg("No API KEY defined. Telegram Bot will not work.")
            return minqlx.RET_STOP_ALL
        else:
            self.msg("API KEY found: {}".format(self.apikeyk))

        # Get CHAT ID in DB
        chatidkeylist = self.db.keys(CHAT_ID_KEY.format("*"))
        for k in chatidkeylist:
            self.chatidk = k

        if self.chatidk == "":
            self.msg("No Chat ID defined. Telegram Bot will not send any message.")
            return minqlx.RET_STOP_ALL
        else:
            self.msg("CHAT ID found: {}".format(self.chatidk))
        

    def chatid(self, player, msg, channel):
        if len(msg) < 1:
            return minqlx.RET_USAGE
        else:
            self.db.set(CHAT_ID_KEY.format(msg[1]), 0)
            self.msg("Telegram Bot: Chat ID updated.")

    def apikey(self, player, msg, channel):
        if len(msg) < 1:
            return minqlx.RET_USAGE
        else:
            self.db.set(TELEGRAM_API_KEY.format(msg[1]), 0)
            self.msg("Telegram Bot: API KEY updated.")

    def telebotkey(self, player, msg, channel):
        self.msg("Telegram Bot: API KEY: {}".format(self.db.keys(TELEGRAM_API_KEY.format("*")), 0))
        self.msg("Telegram Bot: CHAT ID: {}".format(self.db.keys(CHAT_ID_KEY.format("*")), 0))

    ################### HANDLES ####################
    def handle_new_game(self):
         self.running = True
         self.msg("Telegram bot: Polling chat...")
         self.bot_pool()
         return
    
    def handle_vote_called(self, caller, vote, args):
        self.scan_vote_called(caller, vote, args)
    
    @minqlx.thread
    def scan_vote_called(self, caller, vote, args):
        if self.get_cvar("qlx_voterelayenabled") == "1":
            bot.send_message(CHAT_ID, "{}: callvote {} {}".format(self.clean_text((str)(caller)), vote, args))

    def handle_chat(self, player, msg, channel):
        if self.get_cvar("qlx_chatrelayenabled") == "1":
            self.scan_chat(player, msg, channel)
    
    @minqlx.thread
    def scan_chat(self, player, msg, channel):
        def sub_func(match):
            return match.group(0)
        if channel == "chat":
            p = self.clean_text((str)(player))
            bot.send_message(CHAT_ID, "{}: {}".format(p, msg))

    def handle_player_connect(self, player):
        if self.get_cvar("qlx_plrelayenabled") == "1":
            self.scan_player_connect(player)
    
    @minqlx.thread
    def scan_player_connect(self, player):
        p = self.clean_text((str)(player))
        bot.send_message(CHAT_ID, "{} connected.".format(p))

    def handle_player_disconnect(self, player, reason):
        if self.get_cvar("qlx_plrelayenabled") == "1":
            self.scan_player_disconnect(player)
    
    @minqlx.thread
    def scan_player_disconnect(self, player):
        p = self.clean_text((str)(player))
        bot.send_message(CHAT_ID, "{} disconnected.".format(p))
     
    def handle_client_command(self, player, cmd):
        if self.get_cvar("qlx_cmdrelayenabled") == "1":
            self.scan_client_command(player, cmd)

    @minqlx.thread
    def scan_client_command(self, player, cmd):
        p = self.clean_text((str)(player))
        bot.send_message(CHAT_ID, "{} used command ".format(p, len(cmd)))
    
    def handle_game_end(self, data):
        self.scan_game_end()

    @minqlx.thread
    def scan_game_end(self, data):
        players = self.players()
        if not len(players):
            return minqlx.RET_STOP_ALL
        
        res = "{:^} | {:^}\n".format("Team", "Name")
        teamr = res
        teamb = res
        spec = res
        for p in players:
            if p.team == 'red':
                teamr += "{:^} | {}\n".format(p.team, self.clean_text((str)(p)))
            if p.team == 'blue':
                teamb += "{:^} | {}\n".format(p.team, self.clean_text((str)(p)))
            if p.team == 'spectator':
               spec += "{:^} | {}\n".format(p.team, self.clean_text((str)(p)))
        
        bot.send_message(CHAT_ID, teamr)
        bot.send_message(CHAT_ID, teamb)
        bot.send_message(CHAT_ID, spec)

    def handle_unload(self, plugin):
        if plugin == self.__class__.__name__:
            self.msg("Polling chat disabled.")
            self.running = False

    @minqlx.thread
    def testpl(self, player, msg, channel):
        players = self.players()
        if not len(players):
            player.tell("There are no players connected at the moment.")
            return minqlx.RET_STOP_ALL
        
        res = "{:^}\n"
        teamr = res.format("-- Red --")
        teamb = res.format("-- Blue --")
        spec = res.format("-- Spec --")
        for p in players:
            if p.team == 'red':
                teamr += "{}\n".format(self.clean_text((str)(p)))
            if p.team == 'blue':
                teamb += "{}\n".format(self.clean_text((str)(p)))
            if p.team == 'spectator':
               spec += "{}\n".format(self.clean_text((str)(p)))
        
        bot.send_message(CHAT_ID, teamr)
        bot.send_message(CHAT_ID, teamb)
        bot.send_message(CHAT_ID, spec)

    ##################### BOT ######################
    #Thread to listen for commands from Telegram chat
    @minqlx.thread
    def bot_pool(self):
        while self.running == True and len(self.players()) > 1:
            bot.polling()

    @bot.message_handler(commands=["chatid"])
    def sendchatid(message):
        bot.send_message(message.chat.id, message.chat.id)

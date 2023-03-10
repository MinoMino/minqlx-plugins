#####
# The Telegram BOT
# Relay ingame chat to the chatbot in Telegram
# Requires: 
#   pyTelegramBOTAPI (https://pypi.org/project/pyTelegramBotAPI/)
#   Add the module into the minqlx.zip file on the server on the
#   path ~/steamapps/common/qlds
#   
#   Create a new bot using the Bot Father.
#   Define API_KEY using command !telebotapikey <KEY>
#   Use Telegram app to call command /chatid. Bot will reply with the ID.
#   Define CHAT_ID using command !telebotchatid <ID>
#
#   API_KEY is the key token for your bot.
#   CHAT_ID is the chat id used in Telegram app.
#
#####
#   CVARS
#   qlx_chatrelayenabled <1|0> Enable/Disable chat relay to telegram
#   qlx_cmdrelayenabled <1|0> Enable/Disable commands relay to telegram
#   qlx_plrelayenabled <1|0> Enable/Disable players connect/disconnect relay to telegram
#   qlx_voterelayenabled <1|0> Enable/Disable votes relay to telegram
#   
#####
import minqlx
import telebot

VERSION = "v0.1"
TELEBOT_DB_KEY = "minqlx:telegrambot:{}"

class telegrambot(minqlx.Plugin):

    game_bot = telebot.TeleBot("")

    def __init__(self):
        super().__init__()
        self.add_hook("chat", self.handle_chat)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_LOWEST)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("client_command", self.handle_client_command, priority=minqlx.PRI_LOWEST)
        self.add_hook("vote_called", self.handle_vote_called)

        self.set_cvar_once("qlx_chatrelayenabled", "1")
        self.set_cvar_once("qlx_cmdrelayenabled", "1")
        self.set_cvar_once("qlx_plrelayenabled", "1")
        self.set_cvar_once("qlx_voterelayenabled", "1")

        self.add_command("testpl", self.testpl, 2)
        self.add_command("telebotchatid", self.chatid, 2, usage="<CHAT_ID>")
        self.add_command("telebotapikey", self.apikey, 2, usage="<API_KEY>")
        self.add_command("showtelebotkeys", self.telebotkey, 2)

        self.complete = False # setup complete control flag
        self.apikeyk = ""
        self.chatidk = ""
        minqlx.console_print("Loading Telegram Bot keys from DB...")
        self.loadkeys()

    ###################### DB ######################
    @minqlx.thread
    def loadkeys(self):
        # Get API KEY in DB
        apikey = self.db.get(TELEBOT_DB_KEY.format("apikey"))
        if apikey == "":
            minqlx.console_print("Telegram Bot: No API KEY defined. Telegram Bot will not work.")
            minqlx.console_print("Telegram Bot: Setup using !telebotapikey <API_KEY> from the Bot configuration.")
            return minqlx.RET_STOP_ALL
        else:
            minqlx.console_print("Telegram Bot: API KEY found: {}".format(apikey))
            self.apikeyk = apikey
            self.game_bot = telebot.TeleBot(apikey)
            self.game_bot = telebot.TeleBot(apikey)

        # Get CHAT ID in DB
        chatidkey = self.db.get(TELEBOT_DB_KEY.format("chatid"))
        if chatidkey == "":
            self.msg("Telegram Bot: No Chat ID defined. Telegram Bot will not send any message.")
            self.msg("Telegram Bot: Setup using !telebotchatid <CHAT_ID> from the telegram /chatid comamnd.")
            return minqlx.RET_STOP_ALL
        else:
            minqlx.console_print("Telegram Bot: CHAT ID found: {}".format(chatidkey))
            self.chatidk = chatidkey
            self.complete = True

    ###################### DB SET ######################
    def chatid(self, player, msg, channel):
        if len(msg) < 1:
            return minqlx.RET_USAGE
        else:
            self.db.set(TELEBOT_DB_KEY.format("chatid"), msg[1])
            player.tell("Telegram Bot: Chat ID updated.")

    def apikey(self, player, msg, channel):
        if len(msg) < 1:
            return minqlx.RET_USAGE
        else:
            self.db.set(TELEBOT_DB_KEY.format("apikey"), msg[1])
            player.tell("Telegram Bot: API KEY updated.")

    def telebotkey(self, player, msg, channel):
        player.tell("Telegram Bot: API KEY: {}".format(self.db.get(TELEBOT_DB_KEY.format("apikey"))))
        player.tell("Telegram Bot: CHAT ID: {}".format(self.db.get(TELEBOT_DB_KEY.format("chatid"))))

    ################### HANDLES ####################
    def handle_vote_called(self, caller, vote, args):
        if self.complete: self.scan_vote_called(caller, vote, args)
    
    @minqlx.thread
    def scan_vote_called(self, caller, vote, args):
        if self.get_cvar("qlx_voterelayenabled") == "1":
            self.game_bot.send_message(self.chatidk, "{}: callvote {} {}".format(self.clean_text((str)(caller)), vote, args))

    def handle_chat(self, player, msg, channel):
        if self.get_cvar("qlx_chatrelayenabled") == "1":
            if self.complete: self.scan_chat(player, msg, channel)
    
    @minqlx.thread
    def scan_chat(self, player, msg, channel):
        def sub_func(match):
            return match.group(0)
        if channel == "chat":
            p = self.clean_text((str)(player))
            self.game_bot.send_message(self.chatidk, "{}: {}".format(p, msg))

    def handle_player_connect(self, player):
        if self.get_cvar("qlx_plrelayenabled") == "1":
            if self.complete: self.scan_player_connect(player)
    
    @minqlx.thread
    def scan_player_connect(self, player):
        p = self.clean_text((str)(player))
        self.game_bot.send_message(self.chatidk, "{} connected.".format(p))

    def handle_player_disconnect(self, player, reason):
        if self.get_cvar("qlx_plrelayenabled") == "1":
            if self.complete: self.scan_player_disconnect(player)
    
    @minqlx.thread
    def scan_player_disconnect(self, player):
        p = self.clean_text((str)(player))
        self.game_bot.send_message(self.chatidk, "{} disconnected.".format(p))
     
    def handle_client_command(self, player, cmd):
        if self.get_cvar("qlx_cmdrelayenabled") == "1":
            if self.complete: self.scan_client_command(player, cmd)

    @minqlx.thread
    def scan_client_command(self, player, cmd):
        minqlx.console_print("Comando : {}".format(cmd))
        if cmd == "score" or cmd.find("say") or cmd.find("say_team"):
            return minqlx.RET_STOP_ALL
        else:
            p = self.clean_text((str)(player))
            self.game_bot.send_message(self.chatidk, "{} used command {}.".format(p, cmd))
    
    def handle_game_end(self, data):
        if self.complete: self.scan_game_end()

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
        
        self.game_bot.send_message(self.chatidk, teamr)
        self.game_bot.send_message(self.chatidk, teamb)
        self.game_bot.send_message(self.chatidk, spec)

    @minqlx.thread
    def testpl(self, player, msg, channel):
        if self.complete: 
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
            
            self.game_bot.send_message(self.chatidk, teamr)
            self.game_bot.send_message(self.chatidk, teamb)
            self.game_bot.send_message(self.chatidk, spec)

# voicechat.py is a plugin for minqlx to:
# -this script is to allow players to be able to vote for Global or Team voice chat setting.
# created by BarelyMiSSeD on 3-26-16
#
"""
Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
qlx_voicechatAdminLevel "5" - Sets the minqlx server permisson level needed to use the admin level commands in this script.
qlx_voicechatVoiceChatVoting "1" - Set to "1" to allow players to vote for changing the voice chat option to team/global.
qlx_voicechatJoinMessage "1" - Set to "1" to display the script join message to connecting players.
"""



import minqlx
import requests

VERSION = "v1.00"

class voicechat(minqlx.Plugin):
    def __init__(self):
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("player_loaded", self.player_loaded)

        # Cvars.
        self.set_cvar_once("qlx_voicechatAdminLevel", "5")
        self.set_cvar_once("qlx_voicechatVoiceChatVoting", "1")
        self.set_cvar_once("qlx_voicechatJoinMessage", "1")

        voicechatAdmin = int(self.get_cvar("qlx_voicechatAdminLevel"))

        # Commands: voicechat Admin permission level is set using the qlx_optionsAdminLevel Cvar. See the Cvars descrition at the top of the file.
        self.add_command(("globalvoice", "gvoice"), self.cmd_globalVoice, voicechatAdmin)
        self.add_command(("teamvoice", "tvoice"), self.cmd_teamVoice, voicechatAdmin)
        self.add_command(("voicechatversion", "voicechat_version"), self.voicechat_version, voicechatAdmin)
        self.add_command(("voicechat_status", "status", "settings"), self.voicechat_status, voicechatAdmin)
        self.add_command("voicechat", self.voicechat_list)

    # voicechat.py version checker. Thanks to iouonegirl for most of this section's code.
    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/barelymissed/minqlx-plugins/master/{}.py".format(self.__class__.__name__)
        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                # If called manually and outdated
                if channel and VERSION.encode() != line:
                    channel.reply("^4Server: ^7Currently using  ^4BarelyMiSSeD^7's ^6{}^7 plugin ^1outdated^7 version ^6{}^7. The latest version is ^6{}".format(self.__class__.__name__, VERSION, line.decode()))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If called manually and alright
                elif channel and VERSION.encode() == line:
                    channel.reply("^4Server: ^7Currently using ^4BarelyMiSSeD^7's  latest ^6{}^7 plugin version ^6{}^7.".format(self.__class__.__name__, VERSION))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If routine check and it's not alright.
                elif player and VERSION.encode() != line:
                    try:
                        player.tell("^4Server: ^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and you're using ^6{}^7!".format(self.__class__.__name__, line.decode(), VERSION))
                        player.tell("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                    except Exception as e: minqlx.console_command("echo {}".format(e))
                return

    def voicechat_version(self, player, msg, channel):
        self.check_version(channel=channel)

    # Player Join actions. Version checker and join message.
    @minqlx.delay(6)
    def player_loaded(self, player):
        if player.steam_id == minqlx.owner():
            self.check_version(player=player)
        if self.get_cvar("qlx_voicechatJoinMessage", bool):
            player.tell("^3Callvote ^4globalvoice ^3or ^4teamvoice^3. Try ^2/cv <callvote option> ^3 to vote for changing the server setting."
            "Say ^1{}voicechat ^3to see the voicechat status.".format(self.get_cvar("qlx_commandPrefix")))

    # Handles votes called: Kick protection, Map voting rejection during active matches, AFK voting, and Mute/UnMute voting.
    def handle_vote_called(self, caller, vote, args):
        # Global Voice Chat Vote
        if vote.lower() == "globalvoice" or vote.lower() == "globalchat" or vote.lower() == "gvoice" or vote.lower() == "gchat":
            if not self.get_cvar("qlx_voicechatVoiceChatVoting", bool):
                caller.tell("^3Voting for global voice chatting is not enabled on this server.")
                return minqlx.RET_STOP_ALL
            self.callvote("set g_alltalk 1", "Set voice chatting to GLOBAL?")
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL
        # Team Voice Chat Vote
        if vote.lower() == "teamvoice" or vote.lower() == "teamchat" or vote.lower() == "tvoice" or vote.lower() == "tchat":
            if not self.get_cvar("qlx_voicechatVoiceChatVoting", bool):
                caller.tell("^3Voting for team voice chatting is not enabled on this server.")
                return minqlx.RET_STOP_ALL
            self.callvote("set g_alltalk 0", "Set voice chatting to TEAM ONLY?")
            minqlx.client_command(caller.id, "vote yes")
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL

    #Set voice chat to GLOBAL
    def cmd_globalVoice(self, player, msg, channel):
        minqlx.console_command("set g_alltalk 1")
        channel.reply("^3Voice chatting has been set to ^4GLOBAL^3.")

    #Set voice chat to TEAM
    def cmd_teamVoice(self, player, msg, channel):
        minqlx.console_command("set g_alltalk 0")
        channel.reply("^3Voice chatting has been set to ^4TEAM^3.")

    #Shows the status of voice chat
    def voicechat_status(self, player, msg, channel):
        chat = self.get_cvar("g_alltalk")
        if int(chat) == 1:
            player.tell("^3Voice chatting on the server is set to ^4GLOBAL^3.")
        else:
            player.tell("^3Voice chatting on the server is set to ^4TEAM^3.")
        return minqlx.RET_STOP_ALL

    #Shows the allowed setting votes to the player
    def voicechat_list(self, player, msg, channel):
        player.tell("^3Callvote ^4globalvoice ^3or ^4teamvoice^3. Try ^2/cv <callvote option> ^3 to vote for changing the server setting.")
        self.voicechat_status(player, msg, channel)
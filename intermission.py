# This is a plugin created by iouonegirl(@gmail.com)
# Copyright (c) 2016,2017 iouonegirl
# https://github.com/dsverdlo/minqlx-plugins
#
# You are free to modify this plugin to your custom,
# except for the version command related code.
#
# Original idea from <roasticle>, but edited to support
# a list of sounds which will be played one by one after each match.
#
# Place the sounds files in a PK3 file and upload it to a workshop.
#
# If you have trouble hearing the music, I heard Mino's
# workshop.py plugin helps.


import minqlx
import time
import requests

VERSION = "v0.30"

# These songs will be looped one by one. Don't forget to remove the #'s if you want to use songs
# or set the cvar qlx_intermission_songs to a comma-delimited list of songs in server.cfg, like:
# set qlx_intermission_songs "sound/songname/songtitle1.ogg,sound/songname/songtitle2.ogg,sound/songname/songtitle3.ogg"

SONGS = [
    #"sound/songname/songtitle1.ogg",
    #"sound/songname/songtitle2.ogg",
    #"sound/songname/songtitle3.ogg",
]

# When qlx_intermission_songs has been set, then the value of SONGS is ignored.


class intermission(minqlx.Plugin):
    def __init__(self):
        self.index = 0

        self.set_cvar_once( "qlx_intermission_songs", ",".join(SONGS)  )
        self.songs = self.get_cvar( "qlx_intermission_songs", list )

        if not self.songs:
            self.msg("^1Error: No song list for intermission.^7")
            return

        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("player_connect", self.handle_player_connect)
        self.add_command("v_intermission", self.cmd_version)
        self.add_command("intermission", self.cmd_intermission, 3 )

    def cmd_intermission( self, player, msg, channel):
        for p in self.players():
            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                self.stop_sound(p)
        self.handle_game_end( { "ABORTED":0 }  )

        x = 0
        for x, song in enumerate(self.songs):
            channel.reply(  "{}{}".format( song, " (now playing)" if x == self.index else "" ) )
            x += 1


    @minqlx.delay(0.3)
    def handle_game_end(self, data ):
        # If there are no songs defined, return
        if not self.songs or data["ABORTED"]:
            return

        # If last time the index was incremented too high, loop around
        if self.index >= len(self.songs):
            self.index = 0

        # Try to play sound file
        try:
            for p in self.players():
                if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                    self.stop_music(p)
                    self.play_sound(self.songs[self.index],p)
        except Exception as e:
            self.msg("^1Error: ^7{}".format(e))

        # Increase the counter so next round the next sound will be played
        self.index += 1

    def handle_player_connect(self, player):
        if self.db.has_permission(player, 5):
            self.check_version(player=player)

    def cmd_version(self, player, msg, channel):
        self.check_version(channel=channel)

    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/dsverdlo/minqlx-plugins/master/{}.py".format(self.__class__.__name__)
        res = requests.get(url)
        last_status = res.status_code
        if res.status_code != requests.codes.ok: return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                # If called manually and outdated
                if channel and VERSION.encode() != line:
                    channel.reply("^7Currently using ^3iou^7one^4girl^7's ^6{}^7 plugin ^1outdated^7 version ^6{}^7.".format(self.__class__.__name__, VERSION))
                # If called manually and alright
                elif channel and VERSION.encode() == line:
                    channel.reply("^7Currently using ^3iou^7one^4girl^7's latest ^6{}^7 plugin version ^6{}^7.".format(self.__class__.__name__, VERSION))
                # If routine check and it's not alright.
                elif player and VERSION.encode() != line:
                    time.sleep(15)
                    try:
                        player.tell("^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and you're using ^6{}^7!".format(self.__class__.__name__, line.decode(), VERSION))
                    except Exception as e: minqlx.console_command("echo {}".format(e))
                return

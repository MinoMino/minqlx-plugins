# This is an extension plugin  for minqlx.
# Copyright (C) 2018 BarelyMiSSeD (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# This plugin is a replacement for minqlx's fun.py
# https://github.com/MinoMino/minqlx

# Created by BarelyMiSSeD
# https://github.com/BarelyMiSSeD

# You are free to modify this plugin.
# This plugin comes with no warranty or guarantee.

"""
*** This is my replacement for the minqlx fun.py so if you use this file make sure not to load fun.py ***

This plugin plays sounds for players on the Quake Live server
It plays the sounds included in fun.py and some from other workshop item sound packs.

This can limit sound spamming to the server.
It only allows one sound to be played at a time and each user is limited in the frequency they can play sounds.
If you desire no restriction then set both of the 2 following cvars to "0".
The default qlx_funSoundDelay setting will require 5 seconds from the start of any sound
before another sound can be played by anyone.
The default qlx_funPlayerSoundRepeat setting will require 30 seconds from the start of a player called sound before
that player can call another sound.

To set the time required between any sound add this line to your server.cfg and edit the "5":
set qlx_funSoundDelay "5"

To set the time a player has to wait after playing a sound add this like to your server.cfg and edit the "30":
set qlx_funPlayerSoundRepeat "30"

 The amount of seconds an admin has to wait before using the !playsound command again (0 will effectively disable)
 This is to keep admins from being able to totally bypass the sound call restrictions by using !playsound
set qlx_funAdminSoundCall "5"

#Play Join Sound when players connect (set to "path/file" like below example to play sound)
#  *** Disable the MOTD sound to use this with set qlx_motdSound "0" ****
set qlx_funJoinSound "sound/feedback/welcome_02.wav"

#Play Join Sound even if players have sounds disabled
set qlx_funJoinSoundForEveryone "0"

#Play Join Sound on every map change (set to "1" to play join sound every map change)
set qlx_funJoinSoundEveryMap "0"

#Join sound path/file
set qlx_funJoinSound "sound/feedback/welcome_02.wav"

# Play Sound when last 2 players alive (should set to "3" to play sounds always)
# 0 = don't play sound for anyone when the last 2 (or  1 on either team of a team based game) remains
# 1 = play sound for all except those alive when the last 2 (or  1 on either team of a team based game) remains
# 2 = only play sounds for people who are dead/spectating when game is active
# 3 = play sound for everyone with sounds enabled
set qlx_funLast2Sound "3"

# Enable to use a dictionary to store sounds, faster responses to trigger text (0=disable, 1=enable)
#  Enabling will cause the server to use more memory, only enable if memory is available.
#  Must be enabled on server startup or it will not work.
set qlx_funFastSoundLookup "1"

These extra workshop items need to be loaded on the server for it to work correctly if all sound packs are enabled:
(put the workshop item numbers in your workshop.txt file)
#Prestige Worldwide Soundhonks
585892371
#Funny Sounds Pack for Minqlx
620087103
#Duke Nukem Voice Sound Pack for minqlx
572453229
#Warp Sounds for Quake Live
1250689005
#West Coast Crew Sound
1733859113

The minqlx 'workshop' plugin needs to be loaded and the required workshop
items added to the set qlx_workshopReferences line
(This example shows only these required workshop items):
set qlx_workshopReferences "585892371, 620087103, 572453229, 1250689005, 1733859113"
(Only include the sound pack workshop item numbers that you decide to enable on the server)
(The Default sounds use sounds already available as part of the Quake Live install)

Soundpacks:
1) The Default soundpack uses sounds that are already included in the Quake Live install.
2) The Prestige Worldwide Soundhonks soundpack can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=585892371
3) The Funny Sounds Pack for Minqlx can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=620087103
4) The Duke Nukem Voice Sound Pack for minqlx soundpack can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=572453229
5) The Warp Sounds for Quake Live soundpack can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=1250689005
6) The West Coast Crew Sound soundpack can be seen Here: http://steamcommunity.com/sharedfiles/filedetails/?id=1733859113

The soundpacks are all enabled by default. Which soundpacks are enabled can be set.
set qlx_funEnableSoundPacks "63" : Enables all sound packs.
****** How to set which sound packs are enabled ******
Add the values for each sound pack listed below and set that value to the
 qlx_funEnableSoundPacks in the same location as the rest of your minqlx cvar's.

 ****Sound Pack Values****
                               Default:  1
         Prestige Worldwide Soundhonks:  2
          Funny Sounds Pack for Minqlx:  4
Duke Nukem Voice Sound Pack for minqlx:  8
            Warp Sounds for Quake Live:  16
                 West Coast Crew Sound:  32

   Duke Nukem Soundpack Disabled Example: set qlx_funEnableSoundPacks "55"

When a player issues the !listsounds command it wil list all of the sounds available on the server with
 the sounds displayed in a tabbed format to help enable the redability of the sounds without requiring
  the use of pages or exessie scrolling. Only the soundpacks that are enabled will be shown. Any disabled
   soundpacks will not be displayed and will not be searchable.

If !listsounds is issued with a search term it will search for sounds that contain that term and display
 each enabled soundpack and the sounds found in them.

Example: !listsounds yeah would list all the sound phrases containing 'yeah'
and would print this to the player's console (assuming all sound packs are enabled):

SOUNDS: Type these words/phrases in normal chat to play a sound on the server.
Default
haha yeah haha hahaha yeah yeah hahaha yeahhh
Prestige Worldwide Soundhonks
No Matches
Funny Sounds Pack for Minqlx
No Matches
Duke Nukem Voice Sound Pack for minqlx
No Matches
Warp Sounds for Quake Live
No Matches
West Coast Crew Sound
No Matches
4 SOUNDS: Type these words/phrases in normal chat to play a sound on the server.

If !listsounds is issued with a sound pack limiting value it will only search that soundpack for sounds.
!listsounds #Default would only list the sounds in the Default soundpack, if it is enabled.

Example: '!listsounds #Default yeah' would list all the sounds containing 'yeah' but limit that search to
just the Default sounds and produce the following output:

SOUNDS: Type these words/phrases in normal chat to play a sound on the server.
Default
haha yeah haha hahaha yeah yeah hahaha yeahhh
4 SOUNDS: Type these words/phrases in normal chat to play a sound on the server.

// Copy after this line into your server config
// Let players with at least perm level 'qlx_funAdminlevel' play sounds unrestricted (change applies at load time)
// 0-Restricted like all players; 1-Unrestricted for player time limits only; 2-Unrestricted from any time limit
set qlx_funUnrestrictAdmin "0"
// Set the permission level for a myFun admin (change applies at load time)
set qlx_funAdminlevel "5"
// Delay between sounds being played
set qlx_funSoundDelay "5"
// **** Used for limiting players spamming sounds. ****
//  Amount of seconds player has to wait before allowed to play another sound
set qlx_funPlayerSoundRepeat "30"
// Amount of seconds an admin has to wait before using the !playsound command again (0 will effectively disable)
set qlx_funAdminSoundCall "5"
// Keep muted players from playing sounds
set qlx_funDisableMutedPlayers "1"
// Enable/Disable sound pack files
set qlx_funEnableSoundPacks "63"
// Join sound path/file ("0" disables sound)
set qlx_funJoinSound "0"
// Play Join Sound even if players have sounds disabled
set qlx_funJoinSoundForEveryone "0"
// Play Join Sound on every map change
set qlx_funJoinSoundEveryMap "0"
// Play Sound when last 2 players alive (should set to "3" to play sounds always)
// 0 = don't play sound for anyone when the last 2 (or  1 on either team of a team based game) remains
// 1 = play sound for all except those alive when the last 2 (or  1 on either team of a team based game) remains
// 2 = only play sounds for people who are dead/spectating when game is active
// 3 = play sound for everyone with sounds enabled
set qlx_funLast2Sound "1"
// Enable fast sound lookup
set qlx_funFastSoundLookup "1"

#############
# NOTE
#############
Any sound triggers that want to be called using characters outside of A thru Z (case insensitive) need to be added as
a custom trigger. I.E.: getting 'smiley face' to play when a user types :) would be done with
!addtrigger smiley face = :)

################################################################################################################
#    Adding Additional Sound Packs
################################################################################################################
*** If making changes to the ADDITIONAL_SOUNDPACKS perform !erasedb first, then reload/restart  *****
***** To add new sound packs without editing this file "much" *****
Sound Pack File Requirements:
The sound file names will use a sound trigger based on the file name. The sound file name will replace
 underscores (_) with spaces or insert spaces after words starting with a capital letter.
 The path inside the sound_pack.pk3 is not used to generate the sound trigger, only the sound file name.
 I.E. The sound 'sound/warp/bend_me_over.ogg' will create the sound trigger 'bend me over'.
      The sound 'sound/warp/BendMeOver.ogg' will also create the sound trigger 'bend me over'.
 *** Note: These are the only 2 formats that will be correctly interpreted. I.E. 'sound/warp/bendMeOver.ogg' will not
     generate the full sound trigger correctly.
 *** NOTE: The name of the sound pack file stored in the baseq3 directory of the server does not have to match the
     name of the sound pack file in the steam workshop. As long as the contents of the file are exactly the same.
     You can rename the file stored in the baseq3 to whatever you want the sound pack called, ending it with
     the .pk3 file extension. Use underscores for spaces in the sound pack name. (i.e. My_Enjoyable_Sounds.pk3 will be
     shown as the sound pack 'My Enjoyable Sounds'.

1) put the <sound_pack.pk3> file into the baseq3 directory of the server.
    The baseq3 sub-directory stored in the cvar fs_basepath.
2) add the <sound_pack.pk3> file name to the ADDITIONAL_SOUNDPACKS below with the format
    ADDITIONAL_SOUNDPACKS = ['sound_pack.pk3', 'sound_pack_2.pk3', 'sound_pack_3.pk3']
3) add the steam workshop item number to the qlx_workshopReferences cvar in the server.cfg
    set qlx_workshopReferences "585892371, 620087103, 572453229, 1250689005, 1733859113, <new workshop item number>"

The sound pack will be added starting at the end of the list, as sound pack 6 if nothing else was edited in the file.
Any sound pack added here will automatically be enabled.
"""

import minqlx
import random
import time
import re
from os import path
from zipfile import ZipFile
import traceback

VERSION = "8.0"
SOUND_TRIGGERS = "minqlx:myFun:triggers:{}:{}"
TRIGGERS_LOCATION = "minqlx:myFun:addedTriggers:{}"
DISABLED_SOUNDS = "minqlx:myFun:disabled:{}"
PLAYERS_SOUNDS = "minqlx:players:{}:flags:myFun:{}"
TEAM_BASED_GAMETYPES = ("ca", "ctf", "ft", "ictf", "tdm")
CATEGORIES = ["#Default", "#Prestige", "#Funny", "#Duke", "#Warp", "#West"]
SOUND_PACKS = ["Default Quake Live Sounds", "Prestige Worldwide Soundhonks", "Funny Sounds Pack for Minqlx",
               "Duke Nukem Voice Sound Pack for minqlx", "Warp Sounds for Quake Live", "West Coast Crew Sound"]
""" NOTE: If this is changed, you may want to perform a !erasedb before unloading/reloading myFun """
ADDITIONAL_SOUNDPACKS = []


class myFun(minqlx.Plugin):
    Enabled_SoundPacks = []
    soundPacks = []
    categories = []
    soundLists = []
    _enable_dictionary = False
    _sound_dictionary = {}
    _custom_triggers = {}
    sound_list_count = 0
    help_msg = []

    def __init__(self):
        # Let players with perm level qlx_funAdminlevel play sounds
        self.set_cvar_once("qlx_funUnrestrictAdmin", "0")
        # sets the admin level for playing unrestricted sounds (level 5 recommended)
        self.set_cvar_once("qlx_funAdminlevel", "5")
        # Delay between sounds being played
        self.set_cvar_once("qlx_funSoundDelay", "5")
        # **** Used for limiting players spamming sounds. ****
        #  Amount of seconds player has to wait before allowed to play another sound
        self.set_cvar_once("qlx_funPlayerSoundRepeat", "30")
        # Amount of seconds an admin has to wait before using the !playsound command again (0 will effectively disable)
        self.set_cvar_once("qlx_funAdminSoundCall", "5")
        # Keep muted players from playing sounds
        self.set_cvar_once("qlx_funDisableMutedPlayers", "1")
        # Enable/Disable sound pack files
        self.set_cvar_once("qlx_funEnableSoundPacks", "63")
        # Join sound path/file ("0" disables sound)
        self.set_cvar_once("qlx_funJoinSound", "0")
        # Play Join Sound even if players have sounds disabled
        self.set_cvar_once("qlx_funJoinSoundForEveryone", "0")
        # Play Join Sound on every map change
        self.set_cvar_once("qlx_funJoinSoundEveryMap", "0")
        # Play Sound when last 2 players alive (should set to "3" to play sounds always)
        # 0 = don't play sound for anyone when the last 2 (or  1 on either team of a team based game) remains
        # 1 = play sound for all except those alive when the last 2 (or  1 on either team of a team based game) remains
        # 2 = only play sounds for people who are dead/spectating when game is active
        # 3 = play sound for everyone with sounds enabled
        self.set_cvar_once("qlx_funLast2Sound", "3")
        # Enable to use a dictionary to store sounds, faster responses to trigger text (0=disable, 1=enable)
        #  Enabling will cause the server to use more memory, only enable if memory is available.
        #  Must be enabled on server startup, or it will not work.
        self.set_cvar_once("qlx_funFastSoundLookup", "1")

        self.add_hook("chat", self.handle_chat)
        self.add_hook("console_print", self.handle_console_print)
        self.add_hook("server_command", self.handle_server_command)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("player_loaded", self.handle_player_loaded, priority=minqlx.PRI_LOWEST)
        self.add_command("cookies", self.cmd_cookies)
        self.add_command(("ls", "listsounds"), self.list_sounds)
        self.add_command(("myfun", "fun"), self.cmd_help)
        self.add_command(("off", "soundoff"), self.sound_off, client_cmd_perm=0)
        self.add_command(("on", "soundon"), self.sound_on, client_cmd_perm=0)
        self.add_command(("ol", "offlist", "soundofflist"), self.cmd_sound_off_list, client_cmd_perm=0)
        self.add_command(("ps", "playsound", "sound"), self.cmd_sound, 3)
        self.add_command(("pt", "playtrigger"), self.cmd_play_trigger, 3)
        self.add_command(("ds", "disablesound"), self.cmd_disable_sound, client_cmd_perm=5, usage="<sound trigger>")
        self.add_command(("es", "enablesound"), self.cmd_enable_sound, client_cmd_perm=5, usage="<sound trigger>")
        self.add_command(("ld", "listdisabled"), self.cmd_list_disabled, client_cmd_perm=5)
        self.add_command(("at", "addtrigger"), self.add_trigger, 5)
        self.add_command(("dt", "deltrigger"), self.del_trigger, 5)
        self.add_command(("lt", "listtriggers"), self.request_triggers, 3)
        self.add_command(("ed", "erasedisabled"), self.erase_disabled, 5)
        self.add_command("sounds", self.cmd_enable_sounds, usage="<0/1>")
        self.add_command(("erase_sounds", "erasedb"), self.start_erase_db, 5)
        self.add_command(("fill_sounds", "filldb"), self.start_fill_db, 5)
        self.add_command("restrictadmin", self.get_set_restrict_admin, 5)
        self.add_command("adminlevel", self.get_set_admin_level, 5)

        # lambda function to insert spaces in a string (replaces _ or inserts between CamelCase). Returns lowercase.
        self.convert = lambda x: x.replace('_', ' ') if x.islower() else ' '.join(re.findall('[A-Z][^A-Z]*', x)).lower()
        # Class Variables
        self.populating = False
        # variable to show when a sound has been played
        self.played = False
        # variable to store the sound to be called
        self.soundFile = None
        # variable to store the sound trigger
        self.trigger = ""
        # stores time of last sound play
        self.last_sound = None
        # variables used when checking for the presence of a sound file
        self.checking_file = False
        self.file_status = False
        # sounds count
        self._total_sounds = 0
        # Dictionary used to store player sound call times.
        self.sound_limiting = {}
        # Dictionary used to store admin play sound times.
        self.admin_limiting = {}
        # List to store steam ids of muted players
        self.muted_players = []
        # populate the database and sound lists with the sound packs
        self.start_fill_db()
        # Welcome sound played list
        self.playedWelcome = []
        # command prefix
        self._command_prefix = self.get_cvar("qlx_commandPrefix")
        # admin settings
        self.admin_allowed = self.get_cvar("qlx_funUnrestrictAdmin", int)
        self.admin_level = self.get_cvar("qlx_funAdminlevel", int)
        # Execute function to remove loaded !sound commands in other scripts
        self.remove_conflicting_sound_commands()

    def get_set_admin_level(self, player, msg, channel):
        if len(msg) > 1:
            try:
                level = int(msg[1])
                if level < 0 or level > 5:
                    raise ValueError
                self.admin_level = level
                player.tell("^2myFun admin level set to ^3{}".format(self.admin_level))
            except Exception as e:
                player.tell("Level must be an integer. Valid levels are 0-5. Exception: {}".format(type(e).__name__))
        else:
            player.tell("^2myFun admin level is ^3{}\n^2{}adminlevel <perms_level> ^3to set admin level."
                        .format(self.admin_level, self._command_prefix))

    def get_set_restrict_admin(self, player, msg, channel):
        if len(msg) > 1:
            try:
                level = int(msg[1])
                if level < 0 or level > 5:
                    raise ValueError
                elif level == 0:
                    self.admin_allowed = 0
                    player.tell("^1myFun admin sound play is restricted.")
                elif level == 1:
                    self.admin_allowed = 1
                    player.tell("^2myFun admin sound play is unrestricted to player time limits.")
                else:
                    self.admin_allowed = 2
                    player.tell("^2myFun admin sound play is fully un-restricted.")
            except Exception as e:
                player.tell("Admin restriction valid values are 0/1/2. Exception: {}".format(type(e).__name__))
        else:
            r = ['', 'partially un-', 'fully un-']
            player.tell("^2myFun admin is ^3{}restricted\n"
                        "^2{}restrictadmin <0/1/2> ^3to restrict/partially un-restrict/fully un-restrict."
                        .format(r[self.admin_allowed], self._command_prefix))

    @minqlx.delay(3)
    def remove_conflicting_sound_commands(self):
        loaded_scripts = self.plugins
        loaded_scripts.pop(self.__class__.__name__)
        for script, handler in loaded_scripts.items():
            try:
                for cmd in handler.commands:
                    if {"sound"}.intersection(cmd.name):
                        handler.remove_command(cmd.name, cmd.handler)
                        minqlx.console_print("^1myFun: Removing command ^7{} ^1used in ^7{} ^1plugin"
                                             .format(cmd.name, script))
            except:
                continue

    def start_erase_db(self, player, msg=None, channel=None):
        self.erase_db(player)

    @minqlx.thread
    def erase_db(self, player, msg=None, channel=None):
        length = len(self.Enabled_SoundPacks)
        done = self.erase_triggers(player, length)
        self.soundPacks = []
        self.categories = []
        self.soundLists = []
        self.help_msg = []
        self._total_sounds = 0
        player.tell("^1Completed Database Sound Trigger Erase.")

    def erase_triggers(self, player, index, all_triggers=True):
        def del_db(num):
            y = self.db.keys(SOUND_TRIGGERS.format(num, "*"))
            for key in y:
                del self.db[key]
            try:
                player.tell("^1Database Table {} delete commands issued".format(self.categories[num]))
            except:
                pass

        if all_triggers:
            for x in range(index):
                del_db(x)
        else:
            del_db(index)
        return True

    def start_fill_db(self, player=None, msg=None, channel=None):
        self.fill_db(player)

    @minqlx.thread
    def fill_db(self, player, msg=None, channel=None):
        try:
            if player:
                player.tell("^1Filling myFun Sounds Database")
            # List to store the enable/disabled status of the sound packs (they should all be 0 here)
            self.Enabled_SoundPacks = [0] * len(CATEGORIES)
            # set the desired sound packs to enabled
            self.enable_packs()
            self.soundPacks = SOUND_PACKS
            self.categories = CATEGORIES
            self.soundLists = []
            # Using sound dictionary or database list return
            self._enable_dictionary = self.get_cvar("qlx_funFastSoundLookup", bool)
            if self._enable_dictionary:
                # Sound dictionary, used if enabled
                self._sound_dictionary = {}
                self._custom_triggers = {}
                for num in range(len(self.Enabled_SoundPacks)):
                    self._sound_dictionary[num] = {}
            self.populate_database(player)
        except Exception as e:
            minqlx.console_print("^3myFun fill_db Exception: {}\n{}".format(type(e).__name__, traceback.format_exc()))

    def enable_packs(self):
        packs = self.get_cvar("qlx_funEnableSoundPacks", int)
        maximum = 2 ** len(CATEGORIES)
        if packs > maximum:
            packs = maximum
        binary = bin(packs)[2:]
        length = len(binary)
        count = 0
        # Set all values to disabled, initially
        for x in range(len(self.Enabled_SoundPacks)):
            self.Enabled_SoundPacks[x] = 0

        # save the packs value's binary representation to the slots in self.Enabled_SoundPacks
        # to identify the enabled sound packs
        while length > 0:
            self.Enabled_SoundPacks[count] = int(binary[length - 1])
            count += 1
            length -= 1

    @minqlx.delay(2)
    def handle_player_loaded(self, player):
        if self.get_cvar("qlx_motdSound") != "0" or self.get_cvar("qlx_funJoinSound") == "0":
            return
        # plays the join sound for a connecting player if qlx_funJoinSound is set and qlx_motdSound is not set
        # join sound can be played for everyone even if sounds are disabled if qlx_funJoinSoundForEveryone is enabled
        # join sound will play every map load for already connected players if qlx_funJoinSoundEveryMap is enabled
        welcome_sound = self.get_cvar("qlx_funJoinSound")
        if welcome_sound and player.steam_id not in self.playedWelcome and\
                (self.get_cvar("qlx_funJoinSoundForEveryone", bool) or
                 self.db.get_flag(player, "essentials:sounds_enabled", default=True)):
            super().play_sound(welcome_sound, player)
            if not self.get_cvar("qlx_funJoinSoundEveryMap", bool):
                self.playedWelcome.append(player.steam_id)

    # Remove stored information for disconnecting players
    def handle_player_disconnect(self, player, reason):
        self.process_player_disconnect(player)
        return

    def process_player_disconnect(self, player):
        try:
            del self.sound_limiting[player.steam_id]
        except:
            pass
        try:
            self.muted_players.remove(player.steam_id)
        except:
            pass
        try:
            self.playedWelcome.remove(player.steam_id)
        except:
            pass

    # stores the mute status of a player when muted or un-muted
    def handle_server_command(self, player, cmd):
        self.process_server_command(cmd)
        return

    def process_server_command(self, cmd):
        if "has been muted" in cmd:
            cmd_string = cmd.split()
            cmd_len = len(cmd_string)
            name_length = cmd_len - 4
            name = " ".join(cmd_string[1:name_length]).strip('"')
            muted = self.find_player(name)
            steam_id = muted[0].steam_id
            if steam_id not in self.muted_players:
                self.muted_players.append(steam_id)
        elif "has been unmuted" in cmd:
            cmd_string = cmd.split()
            cmd_len = len(cmd_string)
            name_length = cmd_len - 4
            name = " ".join(cmd_string[1:name_length]).strip('"')
            muted = self.find_player(name)
            steam_id = muted[0].steam_id
            try:
                self.muted_players.remove(steam_id)
            except:
                pass

    # Monitors the chat messages of players to process the sound triggers
    def handle_chat(self, player, msg, channel):
        self.scan_chat(player, msg, channel)
        return

    @minqlx.thread
    def scan_chat(self, player, msg, channel):
        # don't process the chat if it was in the wrong channel or the player is muted or has sounds turned off
        if msg.startswith("{}".format(self._command_prefix)) or channel != "chat" or\
                player.steam_id in self.muted_players or\
                not self.db.get_flag(player, "essentials:sounds_enabled", default=True):
            return

        # find the sound trigger for this sound (sets self.trigger, self.soundFile)
        if self.find_sound_trigger(self.clean_text(msg)):
            # stop sound processing if the player has this sound trigger turned off
            if self.db.exists(PLAYERS_SOUNDS.format(player.steam_id, self.soundFile)):
                return minqlx.RET_NONE
            # check sound delay time
            delay_time = self.check_time(player)
            # see if admin is trying to play sound
            admin_sound = self.db.get_permission(player.steam_id) >= self.admin_level
            if delay_time:
                # if admins have no delay time restriction then PASS
                if self.admin_allowed and admin_sound:
                    pass
                # otherwise, impose the delay time wait and stop sound trigger processing
                else:
                    player.tell("^3You played a sound recently. {} seconds timeout remaining."
                                .format(delay_time))
                    return minqlx.RET_NONE
            # check to see if a sound has been played
            if not self.last_sound or self.admin_allowed > 1 and admin_sound:
                pass
            # Make sure the last sound played was not within the sound delay limit
            elif time.time() - self.last_sound < self.get_cvar("qlx_funSoundDelay", int):
                player.tell("^3A sound has been played in last {} seconds. Try again after the timeout."
                            .format(self.get_cvar("qlx_funSoundDelay")))
                return minqlx.RET_NONE
            # call the play sound function
            self.play_sound(self.soundFile)

        # If the sound played record the time with the player's steam id (for delay_time processing)
        if self.played:
            self.sound_limiting[player.steam_id] = time.time()
        # unset self.played so it can be checked again the next time a sound trigger is typed
        self.played = False
        return minqlx.RET_NONE

    def handle_console_print(self, text):
        self.process_console_print(text)
        return

    def process_console_print(self, text):
        try:
            if self.checking_file and 'files listed' in text:
                self.file_status = True if text.split(" ")[0] == "1" else False
        except:
            minqlx.log_exception()
    
    @staticmethod
    def match_string(pattern, string, flags=0):
        return re.fullmatch(pattern, string, flags)

    # Compares the msg with the sound triggers to determine if there is a match
    # --This function is only called from other functions running as their own threads.--
    def find_sound_trigger(self, msg):
        self.trigger = None
        self.soundFile = None
        msg_lower = msg.lower()
        match_msg = msg_lower.replace(':()?', '')
        sound_dict = 0
        while sound_dict < len(self.Enabled_SoundPacks):
            if self.Enabled_SoundPacks[sound_dict]:
                if self._enable_dictionary:
                    if msg_lower[0] in self._sound_dictionary[sound_dict]:
                        for sound, item in self._sound_dictionary[sound_dict][msg_lower[0]].items():
                            match = item.split(";")
                            try:
                                # if sound trigger matches set self.trigger to the trigger,
                                #  self.soundFile to the location of the sound
                                if self.match_string(match[0], match_msg):
                                    if self.db.exists(DISABLED_SOUNDS.format(match[1])):
                                        return False
                                    self.trigger = sound
                                    if match[1]:
                                        self.soundFile = match[1]
                                    return True
                            except Exception as e:
                                minqlx.console_print("^3myFun find sound trigger dictionary Exception: {}\n{}"
                                                     .format(type(e).__name__, traceback.format_exc()))
                else:
                    keys = self.db.keys(SOUND_TRIGGERS.format(sound_dict, "*"))
                    for key in keys:
                        match = self.db.get(key).split(";")
                        # if sound trigger matches set self.trigger to the trigger,
                        #  self.soundFile to the location of the sound
                        try:
                            if self.match_string(match[0], match_msg):
                                if self.db.exists(DISABLED_SOUNDS.format(match[1])):
                                    return False
                                self.trigger = key.split(":")[4]
                                if match[1]:
                                    self.soundFile = match[1]
                                return True
                            # if custom sound triggers have been added for the sound being examined
                            #  it searches through the stored triggers for a match
                            if self.db.exists(TRIGGERS_LOCATION.format(match[1])):
                                for trigger in self.db.lrange(TRIGGERS_LOCATION.format(match[1]), 0, -1):
                                    if trigger == match_msg:
                                        if self.db.exists(DISABLED_SOUNDS.format(match[1])):
                                            return False
                                        self.trigger = key.split(":")[-1]
                                        if match[1]:
                                            self.soundFile = match[1]
                                        return True
                        except Exception as e:
                            minqlx.console_print("^3myFun find sound trigger database Exception: {}\n{}"
                                                 .format(type(e).__name__, traceback.format_exc()))
                # if custom sound triggers have been added for the sound being examined
                #  it searches through the stored triggers for a match
                try:
                    for file, triggers in self._custom_triggers.items():
                        if msg_lower in triggers:
                            if self.db.exists(DISABLED_SOUNDS.format(file)):
                                return False
                            self.trigger = msg_lower
                            self.soundFile = file
                            return True
                except Exception as e:
                    minqlx.console_print("^3myFun find Custom sound trigger Exception: {}\n{}"
                                         .format(type(e).__name__, traceback.format_exc()))
            sound_dict += 1
        return False

    def add_trigger(self, player, msg, channel):
        self.add_custom_trigger(player, msg)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def add_custom_trigger(self, player, msg):
        if len(msg) < 3:
            player.tell("^3usage^7: ^1{}addtrigger ^7<^2default trigger^7> ^1= ^7<^4added trigger^7>"
                        .format(self._command_prefix))
            return minqlx.RET_STOP_ALL
        msg_lower = [x.lower() for x in msg]
        split = 0
        count = 0
        for item in msg_lower[1:]:
            count += 1
            if item == "=":
                split = count
                break
        if split == 0:
            player.tell("^7You MUST include a ^1= ^7sign in to separate the default trigger from the desired trigger.")
            player.tell("^3usage^7: ^1{}addtrigger ^7<^2default trigger^7> ^1= ^7<^4added trigger^7>"
                        .format(self._command_prefix))
        else:
            trigger = " ".join(msg_lower[1:split])
            add_trigger = " ".join(msg_lower[split + 1:])
            found_path = self.find_sound_path(trigger)
            if found_path:
                if self.db.exists(TRIGGERS_LOCATION.format(found_path)):
                    for existing_trigger in self.db.lrange(TRIGGERS_LOCATION.format(found_path), 0, -1):
                        if existing_trigger == add_trigger:
                            player.tell("^3This trigger already exists")
                            return minqlx.RET_STOP_ALL
                self.db.rpush(TRIGGERS_LOCATION.format(found_path), add_trigger)
                if self._enable_dictionary:
                    try:
                        if add_trigger not in self._custom_triggers[found_path]:
                            self._custom_triggers[found_path].append(add_trigger)
                    except KeyError:
                        self._custom_triggers[found_path] = []
                        self._custom_triggers[found_path].append(add_trigger)
                    except Exception as e:
                        minqlx.console_print("^3myFun add custom trigger Exception: {}\n{}"
                                             .format(type(e).__name__, traceback.format_exc()))
                player.tell("^3The sound trigger ^4{0} ^3has been added to the trigger list for ^2{1}."
                            .format(add_trigger, trigger))
                return minqlx.RET_STOP_ALL
            else:
                player.tell("^3usage^7: ^1{}addtrigger ^7<^2default trigger^7> ^1= ^7<^4added trigger^7>"
                            .format(self._command_prefix))
        return minqlx.RET_STOP_ALL

    def del_trigger(self, player, msg, channel):
        self.del_custom_trigger(player, msg)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def del_custom_trigger(self, player, msg):
        if len(msg) < 3:
            player.tell("^3usage^7: ^1!deltrigger ^7<^2default trigger^7> ^1= ^7<^4delete trigger^7>")
            return minqlx.RET_STOP_ALL
        msg_lower = [x.lower() for x in msg]
        split = 0
        count = 0
        for item in msg_lower[1:]:
            count += 1
            if item == "=":
                split = count
                break
        if split == 0:
            player.tell("^7You MUST include a ^1= ^7sign in to separate the default trigger from the desired trigger.")
            player.tell("^3usage^7: ^1{}deltrigger ^7<^2default trigger^7> ^1= ^7<^4del trigger^7>"
                        .format(self._command_prefix))
        else:
            trigger = " ".join(msg_lower[1:split])
            del_trigger = " ".join(msg_lower[split + 1:])
            found_path = self.find_sound_path(trigger)
            if found_path:
                if self.db.exists(TRIGGERS_LOCATION.format(found_path)):
                    self.db.lrem(TRIGGERS_LOCATION.format(found_path), 0, del_trigger)
                    if self._enable_dictionary:
                        try:
                            if del_trigger in self._custom_triggers[found_path]:
                                self._custom_triggers[found_path].remove(del_trigger)
                        except ValueError:
                            pass
                        except Exception as e:
                            minqlx.console_print("^3myFun del custom trigger Exception: {}\n{}"
                                                 .format(type(e).__name__, traceback.format_exc()))
                    player.tell("^3The sound trigger ^4{0} ^3has been deleted from the trigger list for ^2{1}."
                                .format(del_trigger, trigger))
                else:
                    player.tell("^3There are no custom triggers saved for ^4{}".format(trigger))
            else:
                player.tell("^3usage^7: ^1{}deltrigger ^7<^2default trigger^7> ^1= ^7<^4del trigger^7>"
                            .format(self._command_prefix))
        return minqlx.RET_STOP_ALL

    def request_triggers(self, player, msg, channel):
        self.list_triggers(player, msg)

    @minqlx.thread
    def list_triggers(self, player, msg):
        if len(msg) > 1:
            msg_lower = [x.lower() for x in msg]
            trigger = " ".join(msg_lower[1:])
            found_path = self.find_sound_path(trigger)
            if found_path:
                if self.db.exists(TRIGGERS_LOCATION.format(found_path)):
                    if self.db.llen(TRIGGERS_LOCATION.format(found_path)) == 0:
                        player.tell("^3There are no custom triggers saved for ^4{}".format(trigger))
                        return minqlx.RET_STOP_ALL
                    else:
                        triggers = self.db.lrange(TRIGGERS_LOCATION.format(found_path), 0, -1)
                        self.msg("^3The custom sound triggers for ^4{0}^7: ^2{1}".format(trigger, ", ".join(triggers)))
                        return
                else:
                    player.tell("^3There are no custom triggers saved for ^4{}".format(trigger))
            else:
                player.tell("^3There are no custom sound triggers for ^2{}^7.".format(trigger))
            return minqlx.RET_STOP_ALL
        else:
            message = ["^3Custom Triggers:"]
            triggers = self.db.keys(TRIGGERS_LOCATION.format("*"))
            for item in triggers:
                trigger = self.sound_trigger(item.split(":")[3])
                custom_triggers = self.db.lrange(item, 0, 100)
                message.append("^1{}:\n^2   {}".format(trigger, "^7, ^2".join(custom_triggers)))
            player.tell("\n".join(message))
            return minqlx.RET_STOP_ALL

    # players can turn off individual sounds for only themselves
    def sound_off(self, player, msg, channel):
        self.cmd_sound_off(player, msg)

    @minqlx.thread
    def cmd_sound_off(self, player, msg):
        if len(msg) < 2:
            if self.soundFile:
                if self.db.exists(PLAYERS_SOUNDS.format(player.steam_id, self.soundFile)):
                    player.tell("^3The sound ^4{0} ^3is already disabled. Use ^1{1}on ^4{0} ^3to enable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(self.trigger, self._command_prefix))
                else:
                    self.db.set(PLAYERS_SOUNDS.format(player.steam_id, self.soundFile), 1)
                    if not self.trigger:
                        self.find_sound_trigger(self.soundFile)
                    player.tell("^3The sound ^4{0} ^3has been disabled. Use ^1{1}on ^4{0} ^3to enable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(self.trigger, self._command_prefix))
            else:
                player.tell("^1{0}off <sound call> ^7use ^6{0}listsounds #help ^7to find triggers"
                            .format(self._command_prefix))

        else:
            trigger = " ".join(msg[1:]).lower()
            found_path = self.find_sound_path(trigger)
            if found_path:
                if self.db.exists(PLAYERS_SOUNDS.format(player.steam_id, found_path)):
                    player.tell("^3The sound ^4{0} ^3is already disabled. Use ^1{1}on ^4{0} ^3to enable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(trigger, self._command_prefix))
                else:
                    self.db.set(PLAYERS_SOUNDS.format(player.steam_id, found_path), 1)
                    player.tell("^3The sound ^4{0} ^3has been disabled. Use ^1{1}on ^4{0} ^3to enable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(trigger, self._command_prefix))
            else:
                player.tell("^3usage: ^1{0}off <sound call> ^7use ^1{0}listsounds #help ^7to find triggers"
                            .format(self._command_prefix))
        return

    # players can re-enable sounds that they previously disabled for themselves
    def sound_on(self, player, msg, channel):
        self.cmd_sound_on(player, msg)

    @minqlx.thread
    def cmd_sound_on(self, player, msg):
        if len(msg) < 2:
            if self.soundFile:
                if not self.trigger:
                    self.find_sound_trigger(self.soundFile)
                if self.db.exists(PLAYERS_SOUNDS.format(player.steam_id, self.soundFile)):
                    del self.db[PLAYERS_SOUNDS.format(player.steam_id, self.soundFile)]
                    player.tell("^3The sound ^4{0} ^3has been enabled. Use ^1{1}off ^4{0} ^3to disable."
                                .format(self.trigger, self._command_prefix))
                else:
                    player.tell("^3The sound ^4{0} ^3is not disabled. Use ^1{1}off ^4{0} ^3to disable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(self.trigger, self._command_prefix))
            else:
                player.tell("^1{0}on <sound call> ^7use ^1{0}listsounds #help ^7to find triggers"
                            .format(self._command_prefix))

        else:
            trigger = " ".join(msg[1:]).lower()
            found_path = self.find_sound_path(trigger)
            if found_path:
                if self.db.exists(PLAYERS_SOUNDS.format(player.steam_id, found_path)):
                    del self.db[PLAYERS_SOUNDS.format(player.steam_id, found_path)]
                    player.tell("^3The sound ^4{0} ^3has been enabled. Use ^1{1}off ^4{0} ^3to disable."
                                .format(trigger, self._command_prefix))
                else:
                    player.tell("^3The sound ^4{0} ^3is not disabled. Use ^1{1}off ^4{0} ^3to disable."
                                " ^1{1}offlist ^3to see sounds you have disabled."
                                .format(trigger, self._command_prefix))
            else:
                player.tell("^3usage: ^1{0}on <sound call> ^7use ^1{0}listsounds #help ^7to find triggers"
                            .format(self._command_prefix))
        return

    # return the path to the supplied sound trigger
    def find_sound_path(self, trigger):
        sound_dict = 0
        while sound_dict < len(self.Enabled_SoundPacks):
            if self.Enabled_SoundPacks[sound_dict]:
                keys = self.db.keys(SOUND_TRIGGERS.format(sound_dict, "*"))
                for key in keys:
                    if key.split(":")[4] == trigger:
                        return self.db.get(key).split(";")[1]
            sound_dict += 1

        return False

    # return the sound trigger for the sound at the supplied path
    def sound_trigger(self, _path, disabled_lookup=False):
        sound_dict = 0
        while sound_dict < len(self.Enabled_SoundPacks):
            if self.Enabled_SoundPacks[sound_dict]:
                if not self._enable_dictionary or disabled_lookup:
                    keys = self.db.keys(SOUND_TRIGGERS.format(sound_dict, "*"))
                    for key in keys:
                        if self.db.get(key).split(";")[1] == _path:
                            return key.split(":")[4]
                else:
                    for sub, triggers in self._sound_dictionary[sound_dict].items():
                        for sound, item in self._sound_dictionary[sound_dict][sub].items():
                            if item.split(";")[1] == _path:
                                return sound
            sound_dict += 1

        return None

    def cmd_sound_off_list(self, player, msg, channel):
        self.sound_off_list(player)

    @minqlx.thread
    # list the disabled sound to the requesting player
    def sound_off_list(self, player):
        try:
            disabled_key = "minqlx:players:{0}:flags:myFun".format(player.steam_id)
            sound_list = []
            count = 0
            _list = self.db.keys(disabled_key + ":*")
            for key in _list:
                trigger = self.sound_trigger(key.split(":")[-1])
                if trigger:
                    trigger = trigger.replace('?', '')
                    sound_list.append(trigger)
                    count += 1
            player.tell("^3You have ^4{0} ^3sounds disabled: ^1{1}".format(count, "^7, ^1".join(sound_list)))
            return
        except Exception as e:
            player.tell("^1Sound off list exception. See minqlx log for details")
            minqlx.console_print("^1myFun sound_off_list exception: {}\n{}"
                                 .format(type(e).__name__, traceback.format_exc()))

    def cmd_disable_sound(self, player, msg, channel):
        self.disable_sound(player, msg, channel)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    # disable the specified sound on the server
    def disable_sound(self, player, msg, channel):
        try:
            if len(msg) < 2:
                return
            trigger = " ".join(msg[1:]).lower()
            sound_path = self.find_sound_path(trigger)
            if sound_path:
                self.db.set(DISABLED_SOUNDS.format(sound_path), 1)
                player.tell("^3The sound ^4{} ^3is now disabled.".format(trigger))
                self.populate_sound_lists()
            else:
                player.tell("^3Invalid sound trigger. Use ^1{}ls ^7<^1search string^7>"
                            " ^3to find the correct sound trigger.".format(self._command_prefix))
            return
        except Exception as e:
            player.tell("^1Disable sound exception. See minqlx log for details")
            minqlx.console_print("^1myFun disable_sound exception: {}\n{}"
                                 .format(type(e).__name__, traceback.format_exc()))

    def cmd_enable_sound(self, player, msg, channel):
        self.enable_sound(player, msg)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    # enable the specified sound on the server
    def enable_sound(self, player, msg):
        if len(msg) < 2:
            return
        trigger = " ".join(msg[1:]).lower()
        sound_path = self.find_sound_path(trigger)
        if sound_path:
            try:
                if self.db.exists(DISABLED_SOUNDS.format(sound_path)):
                    del self.db[DISABLED_SOUNDS.format(sound_path)]
                    self.populate_sound_lists()
                    player.tell("^3The sound ^1{} ^3is now enabled".format(trigger))
                else:
                    player.tell("^3The sound ^1{} ^3is not disabled. ^1{}ld ^3to see the disabled sounds."
                                .format(trigger, self._command_prefix))
            except Exception as e:
                player.tell("^1Enable sound exception when finding trigger {}. See minqlx log for details"
                            .format(trigger))
                minqlx.console_print("^1myFun enable_sound exception: {}\n{}"
                                     .format(type(e).__name__, traceback.format_exc()))
        else:
            player.tell("^3The sound trigger ^4{} ^3was not found. Ensure the trigger supplied is correct."
                        " ^1{}ld ^3to see the disabled sounds."
                        .format(trigger, self._command_prefix))
        return minqlx.RET_STOP_ALL

    def cmd_list_disabled(self, player, msg, channel):
        player.tell("^2Retrieving Disabled Sounds from the database.")
        self.list_disabled(player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    # list the sounds disabled on the server for the requesting player
    def list_disabled(self, player):
        try:
            sound_list = []
            count = 0
            for key in self.db.keys("minqlx:myFun:disabled:*"):
                sound_path = key.split(":")[-1]
                trigger = self.sound_trigger(sound_path, True)
                if not trigger:
                    continue
                sound_list.append(trigger)
                count += 1
            if count:
                player.tell("^3There {} ^4{} ^3sound{} disabled on the server:\n^1{}"
                            .format('is' if count == 1 else 'are', count, '' if count == 1 else 's',
                                    "\n^1".join(sound_list)))
            else:
                player.tell("^3There are ^4No ^3disabled sounds on this server.")
            return
        except Exception as e:
            player.tell("^1myFun exception listing disabled sounds.\n"
                        "^7You may want to erase stored disabled sounds with {}ed"
                        .format(self._command_prefix))
            minqlx.console_print("^1myFun list_disabled exception (? erase stored disabled sounds with {}ed ?): {}\n{}"
                                 .format(self._command_prefix, type(e).__name__, traceback.format_exc()))

    def erase_disabled(self, player, msg, channel):
        player.tell("^3Erasing all Disabled sounds from the database.")
        self.fix_disabled(player, True)
        return minqlx.RET_STOP_ALL

    # function to change the way the disabled sounds are stored in the database
    @minqlx.thread
    def fix_disabled(self, player=None, erase_all=False):
        try:
            if erase_all:
                for key in self.db.keys("minqlx:myFun:disabled:*"):
                    del self.db[key]
                self.populate_sound_lists()
                if player:
                    player.tell("^2All Disabled sounds have been removed from the database.")
                minqlx.console_print("^3All Disabled sounds have been removed from the database.")
            else:
                for key in self.db.keys("minqlx:myFun:disabled:*"):
                    try:
                        trigger = key.split(":")[-1]
                        sound_path = self.find_sound_path(trigger)
                        if sound_path:
                            self.db.set(DISABLED_SOUNDS.format(sound_path), 1)
                        del self.db[DISABLED_SOUNDS.format(trigger)]
                    except:
                        continue
        except Exception as e:
            minqlx.console_print("^1myFun fix_disabled exception: {}\n{}"
                                 .format(type(e).__name__, traceback.format_exc()))

    # play the sound at the supplied path
    def cmd_sound(self, player, msg, channel):
        self.exec_sound(player, msg, channel)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def exec_sound(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("^3Include a path/sound to play.")
            return

        if "console" != channel and not self.db.get_flag(player, "essentials:sounds_enabled", default=True):
            player.tell("^1Your sounds are disabled. Use ^6{}sounds ^1to enable them again."
                        .format(self._command_prefix))
            minqlx.console_print("^3Admin {} tried calling sound {} but player's sounds are disabled."
                                 .format(player, msg[1]))
            return

        try:
            play_time = time.time() - self.admin_limiting[player.steam_id]
            if play_time >= self.get_cvar("qlx_funAdminSoundCall", int):
                stop = False
            else:
                stop = self.get_cvar("qlx_funAdminSoundCall", int) - play_time
        except KeyError:
            stop = False

        if stop is not False:
            minqlx.console_print("^3Admin {} tried calling sound {} before timeout expired.".format(player, msg[1]))
            player.tell("^3You have {} seconds before you can call another sound.".format(int(stop)))
        else:
            # check for a valid sound file
            self.checking_file = True
            self.file_status = False
            minqlx.console_command("fdir {}".format(msg[1]))
            count = 0
            if count < 10 and not self.file_status:
                count += 1
                time.sleep(0.1)
            self.checking_file = False
            if not self.file_status:
                player.tell("^1Sound ^4{} ^1is not valid.".format(msg[1]))
                return

            if "console" == channel:
                minqlx.console_print("^1Playing sound^7: ^4{}".format(msg[1]))
                self.play_sound(msg[1])
                return
            minqlx.console_print("^3Admin {} called sound {}".format(player, msg[1]))
            self.admin_limiting[player.steam_id] = time.time()
            self.play_sound(msg[1])
        return

    def cmd_play_trigger(self, player, msg, channel):
        self.play_trigger(player, msg, channel)
        return minqlx.RET_STOP_ALL

    # play the sound associated with the trigger
    @minqlx.thread
    def play_trigger(self, player, msg, channel):
        if len(msg) < 2:
            player.tell("Include a sound trigger.")
            return

        msg_lower = " ".join(msg[1:]).lower()

        if "console" != channel and not self.db.get_flag(player, "essentials:sounds_enabled", default=True):
            player.tell("Your sounds are disabled. Use ^6{}sounds^7 to enable them again."
                        .format(self._command_prefix))
            return

        sound = self.get_sound_trigger(msg_lower)

        # Play locally to validate.
        if not sound or "console" != channel and not super().play_sound(sound, player):
            player.tell("^1Invalid sound.")
            return

        if "console" == channel:
            minqlx.console_print("^1Playing sound^7: ^4{}".format(msg_lower))

        self.play_sound(sound)

        return

    # Compares the msg with the sound triggers to determine if there is a match
    def get_sound_trigger(self, msg_lower):
        sound_dict = 0
        while sound_dict < len(self.Enabled_SoundPacks):
            if self.Enabled_SoundPacks[sound_dict]:
                keys = self.db.keys(SOUND_TRIGGERS.format(sound_dict, "*"))
                for key in keys:
                    match = self.db.get(key).split(";")
                    # if sound trigger matches set self.trigger to the trigger,
                    #  self.soundFile to the location of the sound
                    try:
                        if self.match_string(match[0], msg_lower):
                            if self.db.exists(DISABLED_SOUNDS.format(match[1])):
                                return None
                            return match[1]
                        # if custom sound triggers have been added for the sound being examined
                        #  it searches through the stored triggers for a match
                        if self.db.exists(TRIGGERS_LOCATION.format(match[1])):
                            for trigger in self.db.lrange(TRIGGERS_LOCATION.format(match[1]), 0, -1):
                                if trigger == msg_lower:
                                    if self.db.exists(DISABLED_SOUNDS.format(match[1])):
                                        return None
                                    return match[1]
                    except Exception as e:
                        minqlx.console_print("^3myFun get_sound_trigger Exception: {}\n{}"
                                             .format(type(e).__name__, traceback.format_exc()))
            sound_dict += 1
        return None

    # plays the supplied sound for the players on the server (if the player has the sound(s) enabled)
    def play_sound(self, _path, player=None):
        play = self.last_2_sound()
        active = self.game.state in ["in_progress", "countdown"]
        if play == 3 or not active:
            self.played = True
            self.last_sound = time.time()
            for p in self.players():
                if self.db.get_flag(p, "essentials:sounds_enabled", default=True) and \
                        not self.db.exists(PLAYERS_SOUNDS.format(p.steam_id, _path)):
                    super().play_sound(_path, p)
        elif play == 1 or (play == 2 and active):
            self.played = True
            self.last_sound = time.time()
            teams = self.teams()
            for p in teams["red"] + teams["blue"] + teams["free"]:
                if not p.is_alive and self.db.get_flag(p, "essentials:sounds_enabled", default=True) and \
                        not self.db.exists(PLAYERS_SOUNDS.format(p.steam_id, _path)):
                    super().play_sound(_path, p)
            for p in teams["spectator"]:
                if self.db.get_flag(p, "essentials:sounds_enabled", default=True) and \
                        not self.db.exists(PLAYERS_SOUNDS.format(p.steam_id, _path)):
                    super().play_sound(_path, p)

    def last_2_sound(self):
        # 0 = don't play sound for anyone when the last 2 (or  1 on either team of a team based game) remains
        # 1 = play sound for all except those alive when the last 2 (or  1 on either team of a team based game) remains
        # 2 = only play sounds for people who are dead/spectating when game is active
        # 3 = play sound for everyone with sounds enabled
        play_last2 = self.get_cvar("qlx_funLast2Sound", int)
        if play_last2 in [2, 3]:
            return play_last2
        teams = self.teams()
        remaining = 0
        if self.game.type_short in TEAM_BASED_GAMETYPES:
            r_remaining = 0
            b_remaining = 0
            for r in teams["red"]:
                if r.is_alive:
                    r_remaining += 1
            for b in teams["blue"]:
                if b.is_alive:
                    b_remaining += 1
            if r_remaining == 1 or b_remaining == 1:
                remaining = 2
        else:
            for p in teams["free"]:
                if p.is_alive:
                    remaining += 1
        if remaining == 2:
            return play_last2
        else:
            return 3

    # populates the sound list that is used to list the available sounds on the server
    # All calls to this function are called in sub-threads
    def populate_sound_lists(self, player=None):
        try:
            if not self.populating:
                self.populating = True
                self.soundLists = [[] if x else None for x in self.Enabled_SoundPacks]
                self.sound_list_count = 0
                self._total_sounds = 0
                self.help_msg = []
                custom_triggers = {}
                for slot, value in enumerate(self.Enabled_SoundPacks):
                    if self.Enabled_SoundPacks[slot]:
                        self.sound_list_count += 1
                        self.help_msg.append(self.categories[slot])
                        keys = self.db.keys(SOUND_TRIGGERS.format(slot, "*"))
                        for key in keys:
                            db_value = self.db.get(key)
                            self._total_sounds += 1
                            entry = db_value.split(';')
                            if len(entry) < 2:
                                del self.db[key]
                                continue
                            if self.db.exists(DISABLED_SOUNDS.format(entry[1])):
                                continue
                            trigger = key.split(":")[4]
                            self.soundLists[slot].append(trigger)
                            if self._enable_dictionary:
                                matches = entry[0].split('|')
                                for match in matches:
                                    if not match:
                                        continue
                                    _m = match[0].lower()
                                    if not _m.isalpha():
                                        custom_triggers[match] = entry[1]
                                        continue
                                    if _m not in self._sound_dictionary[slot]:
                                        self._sound_dictionary[slot][_m] = {}
                                    self._sound_dictionary[slot][_m][match] = "{};{}".format(match, entry[1])
                                if self.db.exists(TRIGGERS_LOCATION.format(entry[1])):
                                    self._custom_triggers[entry[1]] = self.db.lrange(TRIGGERS_LOCATION.format(entry[1]), 0, -1)
                        self.soundLists[slot].sort()
                        self.category_loaded(slot, 'Quick Lookup Dictionary', player)
                if custom_triggers:
                    for match, entry in custom_triggers.items():
                        if entry not in self._custom_triggers:
                            self._custom_triggers[entry] = []
                        self._custom_triggers[entry].append(match)
            sound_packs = []
            count = 0
            while count < len(self.Enabled_SoundPacks):
                if self.Enabled_SoundPacks[count]:
                    sound_packs.append(self.soundPacks[count])
                count += 1
            if player:
                player.tell("Enabled Sound Packs are: ^3{}".format(", ".join(sound_packs)))
                player.tell("Completed Sound Pack reload.")
            else:
                minqlx.console_print("Enabled Sound Packs are: ^3{}".format(", ".join(sound_packs)))
                minqlx.console_print("Completed Sound Pack reload.")
        except Exception as e:
            minqlx.console_print("myFun populate_sound_lists Exception: {}\n{}"
                                 .format(type(e).__name__, traceback.format_exc()))
        finally:
            self.populating = False

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

    ''' Here in case the essentials plugin is not loaded '''
    def cmd_enable_sounds(self, player, msg, channel):
        if "essentials" not in self._loaded_plugins:
            flag = self.db.get_flag(player, "essentials:sounds_enabled", default=True)
            self.db.set_flag(player, "essentials:sounds_enabled", not flag)

            if flag:
                player.tell("Sounds have been disabled. Use ^6{}sounds^7 to enable them again."
                            .format(self._command_prefix))
            else:
                player.tell("Sounds have been enabled. Use ^6{}sounds^7 to disable them again."
                            .format(self._command_prefix))

            return minqlx.RET_STOP_ALL

    def check_time(self, player):
        if self.get_cvar("qlx_funUnrestrictAdmin", bool) and self.db.get_permission(player.steam_id) == 5:
            return False
        try:
            saved_time = self.sound_limiting[player.steam_id]
            play_time = time.time() - saved_time
            if play_time > self.get_cvar("qlx_funPlayerSoundRepeat", int):
                return False
            else:
                return int(self.get_cvar("qlx_funPlayerSoundRepeat", int) - play_time)
        except KeyError:
            return False

    # list the command usage for !listsounds
    def cmd_help(self, player, msg=None, channel=None):
        count = 0
        help_msg = ''
        for msg in self.help_msg:
            if not help_msg:
                help_msg = msg
            elif not count % 6:
                help_msg = help_msg + "^7,\n^2" + msg
            else:
                help_msg = help_msg + "^7, ^2" + msg
            count += 1
        player.tell("^1myFun Version {0}\n"
                    "^6{1}myFun ^3to quickly pull up this help menu.\n"
                    "^6{1}listsounds ^3shows all sounds\n^6{1}listsounds #sound-pack ^3 to see just one sound"
                    " pack\n^6{1}listsounds #sound-pack search-term ^3to see sounds in that sound pack that"
                    " have the search term\n^6{1}listsounds search-term ^3to search all sound packs for sounds"
                    " with that search term\n^2EXAMPLES^7:\n^6{1}listsounds #Default ^3 will display all"
                    " ^4Default Quake Live Sounds\n^6{1}lsitsounds #Default yeah ^3 will search ^4#Default"
                    " ^3for sounds containing ^4yeah\n^6{1}listsounds yeah ^3 will search all the sound packs"
                    " for sounds containing ^4yeah\n^3Search terms can be multiple words\n"
                    "^3Valid sound-pack(s) are^7:\n^2{2}\n^6{1}sounds ^3to disable^7/^3enable"
                    " all sound playing for yourself."
                    "\n^6{1}off^7/^6{1}on trigger ^3to disable^7/^3enable a specific sound\n^6{1}offlist ^3to see a"
                    " list of sounds you have disabled."
                    .format(VERSION, self._command_prefix, help_msg))
        return

    # list the command usage for !listsounds
    def listsounds_usage(self, player):
        if self._total_sounds:
            count = 0
            help_msg = ''
            for msg in self.help_msg:
                if not help_msg:
                    help_msg = msg
                elif not count % 6:
                    help_msg = help_msg + "^7,\n^2" + msg
                else:
                    help_msg = help_msg + "^7, ^2" + msg
                count += 1
            player.tell("^1There are {2} sounds available to play.\n"
                        "^4Include a category and/or search value for {0}listsounds\n"
                        "^5Ex: ^4{0}listsounds #default pain\n"
                        "^3Valid sound-pack(s) are^7:\n^2{1}\n"
                        .format(self._command_prefix, help_msg, self._total_sounds))
        else:
            player.tell("^1There are no sounds loaded")
        return

    # list the available sounds to the requesting player
    def list_sounds(self, player, msg, channel):
        self.cmd_list_sounds(player, msg, channel)

    @minqlx.thread
    def cmd_list_sounds(self, player, msg, channel):
        sounds = ["^4SOUNDS^7: ^3Type these words/phrases in normal chat to play a sound on the server.\n"]
        length = len(msg)
        count = 0
        category = None
        search = None
        if length == 2 and msg[1]:
            if msg[1].startswith("#"):
                category = msg[1]
            else:
                search = msg[1]
        elif length > 2 and msg[1]:
            if msg[1].startswith("#"):
                category = msg[1]
                search = " ".join(msg[2:])
            else:
                search = " ".join(msg[1:])
        else:
            self.listsounds_usage(player)
            return

        if category:
            category = category.lower()
            if category == "#help":
                self.cmd_help(player)
                return
            elif any(s.lower() == category for s in self.help_msg):
                category_num = -1
                cat_num = 0
                while cat_num < len(self.categories):
                    if self.match_string(self.categories[cat_num].lower(), category):
                        category_num = cat_num
                    cat_num += 1

                if -1 < category_num < len(self.Enabled_SoundPacks):
                    sounds_line = ""
                    sounds.append("^4" + self.soundPacks[category_num] + "\n")
                    for item in self.soundLists[category_num]:
                        if search and search not in item:
                            continue
                        add_sound, status = self.line_up(sounds_line, item)
                        if status == 1:
                            sounds.append("^1" + sounds_line + "\n")
                            sounds_line = add_sound
                        elif status == 2:
                            sounds_line += add_sound
                            sounds.append("^1" + sounds_line + "\n")
                            sounds_line = ""
                        else:
                            sounds_line += add_sound
                        count += 1
                    if len(sounds_line):
                        sounds.append("^1" + sounds_line + "\n")

                if count == 0:
                    sounds.append("^3No Matches\n")
            else:
                if self.sound_list_count == 1:
                    player.tell("^3INVALID ^2Category ^7given. Valid category is ^2" + "^7, ^2".join(self.help_msg))
                else:
                    player.tell("^3INVALID ^2Category ^7given. Valid categories are ^2" + "^7, ^2".join(self.help_msg))
                return

        else:
            slot = 0
            while slot < len(self.Enabled_SoundPacks):
                sounds_line = ""
                if self.Enabled_SoundPacks[slot]:
                    found = 0
                    if self.soundLists[slot]:
                        sounds.append("^4" + self.soundPacks[slot] + "\n")
                        for item in self.soundLists[slot]:
                            if search and search not in item:
                                continue
                            add_sound, status = self.line_up(sounds_line, item)
                            if status == 1:
                                sounds.append("^1" + sounds_line + "\n")
                                sounds_line = add_sound
                            elif status == 2:
                                sounds_line += add_sound
                                sounds.append("^1" + sounds_line + "\n")
                                sounds_line = ""
                            else:
                                sounds_line += add_sound
                            count += 1
                            found += 1
                    if len(sounds_line):
                        sounds.append("^1" + sounds_line + "\n")
                    if found == 0:
                        sounds.append("^3No Matches\n")
                slot += 1

            if count == 0 and search:
                player.tell("^4Server^7: No sounds contain the search string ^1{}^7.".format(search))
                return
            if count == 0:
                player.tell("^4Server^7: No sounds were found")
                return

            if self.sound_list_count > 1 and not category and not search:
                sounds.append("^3Type ^4{}listsounds #help ^3 to get instructions on narrowing your search results.\n"
                              .format(self._command_prefix))
            elif not search:
                sounds.append("^3Add a search string to further narrow results:\n^2{0}listsounds ^7<^2category^7>"
                              " <^2search string^7>".format(self._command_prefix))

        sounds.append("^2{} ^4SOUND{}^7: ^3Type these words/phrases in normal chat to trigger a sound on the server.\n"
                      .format(count, 'S' if count > 1 else ''))

        if "console" == channel:
            for line in sounds:
                minqlx.console_print(line.strip())
        else:
            player.tell("".join(sounds))
        return

    # puts the list of sounds in a column style format for easier reading
    def line_up(self, sound_line, add_sound):
        length = len(sound_line)
        # 0 = add to line, 1 = add to new line, 2 = add current sound and start new line
        status = 0
        if length + len(add_sound) > 78:
            append = add_sound
            status = 1
        elif length == 0:
            append = add_sound
        elif length < 16:
            append = " " * (18 - length) + add_sound
        elif length < 36:
            append = " " * (38 - length) + add_sound
        elif length < 56:
            append = " " * (58 - length) + add_sound
        elif length < 76:
            append = " " * (78 - length) + add_sound
            status = 2
        else:
            append = add_sound
            status = 1
        return append, status

    def category_loaded(self, cat_index, target, player=None):
        if len(self.categories) > cat_index:
            if player:
                player.tell("^2Category {} loaded to {}".format(self.categories[cat_index], target))
            else:
                minqlx.console_print("^2Category {} loaded to {}".format(self.categories[cat_index], target))

    # These are the sounds available on the server put into the dictionaries used to search for a sound trigger match
    #  when processing normal chat messages
    def populate_database(self, player=None):
        old_version = 0.0
        if self.db.exists("minqlx:myFun:version"):
            old_version = self.db.get("minqlx:myFun:version")
        self.db.set("minqlx:myFun:version", VERSION)
        self.db.set("minqlx:myFun:enabled", self.get_cvar("qlx_funEnableSoundPacks"))
        if float(old_version) < 4.2:
            self.fix_disabled()
        if self.Enabled_SoundPacks[0]:
            self.db.set(SOUND_TRIGGERS.format(0, "battlesuit"), "battlesuit;sound/vo/battlesuit.ogg")
            self.db.set(SOUND_TRIGGERS.format(0, "bite"), "bite;sound/vo/bite.ogg")
            self.db.set(SOUND_TRIGGERS.format(0, "combo kill"), "combo kill;sound/vo/combokill2.ogg")
            self.db.set(SOUND_TRIGGERS.format(0, "haha"), "haha;sound/player/lucy/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "haha yeah haha"), "haha,? yeah?,? haha;sound/player/biker/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "yeah hahaha"), "yeah?,? haha(ha)?;sound/player/razor/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death"), "death;sound/player/biker/death1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death2"), "death2;sound/player/bitterman/death2.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death3"), "death3;sound/player/bones/death2.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death4"), "death4;sound/player/doom/death2.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death5"), "death5;sound/player/grunt/death1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death6"), "death6;sound/player/hunter/death2.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death7"), "death7;sound/player/james/death3.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death8"), "death8;sound/player/janet/death1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death9"), "death9;sound/player/keel/death3.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death10"), "death10;sound/player/klesk/death3.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death11"), "death11;sound/player/major/death1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death12"), "death12;sound/player/orbb/death3.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death13"), "death13;sound/player/santa/death3.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death14"), "death14;sound/player/sarge/death2.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death15"), "death15;sound/player/slash/death1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death16"), "death16;sound/player/sorlag/death1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death17"), "death17;sound/player/tankjr/death1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death18"), "death18;sound/player/uriel/death1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death19"), "death19;sound/player/visor/death3.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "death20"), "death20;sound/player/xaero/death1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "duahahaha"), "duahaha(?:ha)?;sound/player/keel/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "denied"), "denied;sound/vo/denied")
            self.db.set(SOUND_TRIGGERS.format(0, "headshot"), "headshot;sound/vo/headshot")
            self.db.set(SOUND_TRIGGERS.format(0, "hahaha"), "hahaha;sound/player/santa/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "glhf"), "gl ?hf|hf;sound/vo/crash_new/39_01.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "fall2"), "fall2;sound/player/santa/falling1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "f3"), "f3|press f3|ready( up)?;sound/vo/crash_new/36_04.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "holy shit"), "holy shit;sound/vo_female/holy_shit")
            self.db.set(SOUND_TRIGGERS.format(0, "welcome to quake live"), "welcome to q(uake )?l(ive)?;sound/vo_evil/welcome")
            self.db.set(SOUND_TRIGGERS.format(0, "gasp"), "gasp;sound/player/anarki/gasp.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "go"), "go;sound/vo/go")
            self.db.set(SOUND_TRIGGERS.format(0, "beep boop"), "beep boop;sound/player/tankjr/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "you win"), "you win;sound/vo_female/you_win.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "you lose"), "you lose;sound/vo/you_lose.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "impressive"), "impressive;sound/vo_female/impressive1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "excellent"), "excellent;sound/vo_evil/excellent1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "balls out"), "ball'?s out;sound/vo_female/balls_out")
            self.db.set(SOUND_TRIGGERS.format(0, "one frag left"), "one frag left;sound/vo/1_frag.ogg")
            self.db.set(SOUND_TRIGGERS.format(0, "one"), "one;sound/vo_female/one")
            self.db.set(SOUND_TRIGGERS.format(0, "two"), "two;sound/vo_female/two")
            self.db.set(SOUND_TRIGGERS.format(0, "three"), "three;sound/vo_female/three")
            self.db.set(SOUND_TRIGGERS.format(0, "fight"), "fight;sound/vo_evil/fight")
            self.db.set(SOUND_TRIGGERS.format(0, "gauntlet"), "gauntlet;sound/vo_evil/gauntlet")
            self.db.set(SOUND_TRIGGERS.format(0, "humiliation"), "humiliation;sound/vo_evil/humiliation1")
            self.db.set(SOUND_TRIGGERS.format(0, "perfect"), "perfect;sound/vo_evil/perfect")
            self.db.set(SOUND_TRIGGERS.format(0, "wah wah wah wah"), "wah wah wah( wah)?;sound/misc/yousuck")
            self.db.set(SOUND_TRIGGERS.format(0, "ah ah ah ah"), "ah ah ah( ah)?;sound/player/slash/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "oink"), "oink;sound/player/sorlag/pain50_1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "argh"), "a+rgh;sound/player/doom/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "hah haha"), "hah haha;sound/player/hunter/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "woohoo"), "woohoo;sound/player/janet/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "quake live"), "ql|quake live;sound/vo_female/quake_live")
            self.db.set(SOUND_TRIGGERS.format(0, "chaching"), "€|£|$|chaching;sound/misc/chaching")
            self.db.set(SOUND_TRIGGERS.format(0, "uh ah"), "uh ah;sound/player/mynx/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "oohwee"), "ooh+wee;sound/player/anarki/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "erah"), "erah;sound/player/bitterman/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "yeahhh"), "yeahhh;sound/player/major/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "scream"), "scream;sound/player/bones/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "salute"), "salute;sound/player/sarge/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "squish"), "squish;sound/player/orbb/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "oh god"), "oh god;sound/player/ranger/taunt.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "pain"), "pain;sound/player/anarki/pain25_1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "pain2"), "pain2;sound/player/orbb/pain25_1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "pain3"), "pain3;sound/player/keel/pain50_1.wav")
            self.db.set(SOUND_TRIGGERS.format(0, "snarl"), "snarl;sound/player/sorlag/taunt.wav")
            self.category_loaded(0, 'database', player)
        if self.Enabled_SoundPacks[1]:
            self.db.set(SOUND_TRIGGERS.format(1, "assholes"), "assholes;soundbank/assholes.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "assshafter"), "assshafter|asshafter|ass shafter;soundbank/assshafterloud.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "babydoll"), "babydoll;soundbank/babydoll.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "barelymissed"), "barelymissed|barely;soundbank/barelymissed.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "belly"), "belly;soundbank/belly.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "bitch"), "bitch;soundbank/bitch.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "blud"), "dtblud|blud;soundbank/dtblud.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "boats"), "boats;soundbank/boats.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "bobg"), "bobg|bob;soundbank/bobg.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "bogdog"), "bogdog;soundbank/bogdog.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "boom"), "boom;soundbank/boom.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "boom2"), "boom2;soundbank/boom2.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "buk"), "buk|ibbukn;soundbank/buk.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "bullshit"), "bull ?shit|bs;soundbank/bullshit.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "butthole"), "butthole;soundbank/butthole.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "buttsex"), "buttsex;soundbank/buttsex.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "cheeks"), "cheeks;soundbank/cheeks.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "cocksucker"), "cocksucker|cs;soundbank/cocksucker.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "conquer"), "conquer;soundbank/conquer.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "countdown"), "countdown;soundbank/countdown.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "cum"), "cum;soundbank/cum.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "cumming"), "cumming;soundbank/cumming.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "cunt"), "cunt;soundbank/cunt.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "dirkfunk"), "dirkfunk|dirk;soundbank/dirkfunk.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "disappointment"), "disappointment;soundbank/disappointment.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "doomsday"), "doom(sday)?;soundbank/doom.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "drumset"), "drumset;soundbank/drumset.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "eat"), "eat;soundbank/eat.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "eat me"), "eatme|eat me|byte me;soundbank/eatme.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "fag"), "fag|homo(sexual)?;soundbank/fag.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "fingerass"), "fingerass;soundbank/fingerass.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "flash"), "flash(soul)?;soundbank/flash.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "fuckface"), "fuckface;soundbank/fuckface.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "fuckyou"), "fuckyou;soundbank/fuckyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "get emm"), "get ?emm?;soundbank/getemm.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "gonads"), "gonads|nads;soundbank/gonads.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "gtfo"), "gtfo;soundbank/gtfo.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "hug it out"), "hug it out;soundbank/hugitout.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "idiot"), "idiot|andycreep|d3phx|gladiat0r;soundbank/idiot.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "idiot2"), "idiot2;soundbank/idiot2.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "it's time"), "it'?s time;soundbank/itstime.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "jeopardy"), "jeopardy;soundbank/jeopardy.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "jerk off"), "jerk( ?off)?;soundbank/jerkoff.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "killo"), "killo;soundbank/killo.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "knocked"), "knocked;soundbank/knocked.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "ld3"), "die|ld3;soundbank/ld3.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "liquidswords"), "liquid(swords)?;soundbank/liquid.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "massacre"), "massacre;soundbank/massacre.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "mixer"), "mixer;soundbank/mixer.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "mjman"), "mjman|marijuanaman;soundbank/mjman.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "mmmm"), "mmmm;soundbank/mmmm.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "monty"), "monty;soundbank/monty.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "n8"), "n8;soundbank/n8.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "nikon"), "nikon?(guru)?;soundbank/nikon.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "nina"), "nina;soundbank/nina.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "nthreem"), "nthreem;sound/vo_female/impressive1.wav")
            self.db.set(SOUND_TRIGGERS.format(1, "olhip"), "olhip|hip;soundbank/hip.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "organic"), "org(anic)?;soundbank/organic.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "paintball"), "paintball;soundbank/paintball.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "pigfucker"), "pig ?fucker|pig fucker;soundbank/pigfer.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "popeye"), "popeye;soundbank/popeye.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "rosie"), "rosie;soundbank/rosie.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "seaweed"), "seaweed;soundbank/seaweed.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "shit"), "shit;soundbank/shit.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "sit"), "sit;soundbank/sit.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "soulianis"), "soul(ianis)?;soundbank/soulianis.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "spam"), "spam;soundbank/spam3.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "stalin"), "stalin;soundbank/ussr.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "stfu"), "stfu;soundbank/stfu.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "suck a dick"), "suck a dick;soundbank/suckadick.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "suckit"), "suckit;soundbank/suckit.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "suck my dick"), "suck my dick;soundbank/suckmydick.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "teapot"), "teapot;soundbank/teapot.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "thank god"), "thank ?god;soundbank/thankgod.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "traxion"), "traxion;soundbank/traxion.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "trixy"), "trixy;soundbank/trixy.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "twoon"), "twoon|2pows;soundbank/twoon.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "ty"), "ty|thanks|thank you;soundbank/thankyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "venny"), "venny;soundbank/venny.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "viewaskewer"), "view(askewer)?;soundbank/view.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "what's that"), "what'?s that;soundbank/whatsthat.ogg")
            self.db.set(SOUND_TRIGGERS.format(1, "who are you"), "who are you;soundbank/whoareyou.ogg")
            self.category_loaded(1, 'database', player)
        if self.Enabled_SoundPacks[2]:
            self.db.set(SOUND_TRIGGERS.format(2, "007"), "007;sound/funnysounds/007.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "A Scratch"), "scratch|a scratch|just a scratch;sound/funnysounds/AScratch.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "adams family"), "adams family;sound/funnysounds/adamsfamily.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "All The Things"), "all the things;sound/funnysounds/AllTheThings.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "allahuakbar"), "allahuakbar;sound/funnysounds/allahuakbar.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "allstar"), "allstar;sound/funnysounds/allstar.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Amazing"), "amazing;sound/funnysounds/Amazing.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Ameno"), "ameno;sound/funnysounds/Ameno.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "America"), "america;sound/funnysounds/America.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Amerika"), "amerika;sound/funnysounds/Amerika.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "And Nothing Else"), "and nothing else;sound/funnysounds/AndNothingElse.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Animals"), "animals;sound/funnysounds/Animals.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "asskicking"), "asskicking;sound/funnysounds/asskicking.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "ave"), "ave;sound/funnysounds/ave.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "baby baby"), "baby baby;sound/funnysounds/babybaby.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "baby evil"), "baby evil;sound/funnysounds/babyevillaugh.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "baby laughing"), "baby( laughing)?;sound/funnysounds/babylaughing.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "bad boys"), "bad boys;sound/funnysounds/badboys.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Banana Boat"), "banana boat;sound/funnysounds/BananaBoatSong.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "benny hill"), "benny hill;sound/funnysounds/bennyhill.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "benzin"), "benzin;sound/funnysounds/benzin.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "blue wins"), "blue ?wins;sound/funnysounds/bluewins.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "bonkers"), "bonkers;sound/funnysounds/bonkers.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "boom headshot"), "boom headshot;sound/funnysounds/boomheadshot.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "booo"), "booo?;sound/funnysounds/booo.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "boring"), "boring;sound/funnysounds/boring.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "boze"), "boze;sound/funnysounds/boze.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "bright side of life"), "bright ?side ?of ?life;sound/funnysounds/brightsideoflife.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "buckdich"), "buckdich;sound/funnysounds/buckdich.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "bullshitter"), "bullshitter;sound/funnysounds/bullshitter.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "burns burns"), "burns burns;sound/funnysounds/burnsburns.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "camel toe"), "camel toe;sound/funnysounds/cameltoe.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "can't touch this"), "can'?t touch this;sound/funnysounds/canttouchthis.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "cccp"), "cccp|ussr;sound/funnysounds/cccp.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "champions"), "champions;sound/funnysounds/champions.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "chicken"), "chicken;sound/funnysounds/chicken.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "chocolate rain"), "chocolate rain;sound/funnysounds/chocolaterain.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "coin"), "coin;sound/funnysounds/coin.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "come"), "come;sound/funnysounds/come.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Come With Me Now"), "come with me now;sound/funnysounds/ComeWithMeNow.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Count down"), "count down;sound/funnysounds/Countdown.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "cowards"), "cowards;sound/funnysounds/cowards.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "crazy"), "crazy;sound/funnysounds/crazy.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "damnit"), "damnit;sound/funnysounds/damnit.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Danger Zone"), "danger zone;sound/funnysounds/DangerZone.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "dead soon"), "dead ?soon;sound/funnysounds/deadsoon.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "defeated"), "defeated;sound/funnysounds/defeated.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "devil"), "devil;sound/funnysounds/devil.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "doesn't love you"), "doesn'?t love you;sound/funnysounds/doesntloveyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "du bist"), "du bist;sound/funnysounds/dubist.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "du hast"), "du hast;sound/funnysounds/duhast.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "dumb ways"), "dumb ways;sound/funnysounds/dumbways.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Eat Pussy"), "eat pussy;sound/funnysounds/EatPussy.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "education"), "education;sound/funnysounds/education.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "einschrei"), "einschrei;sound/funnysounds/einschrei.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Eins Zwei"), "eins zwei;sound/funnysounds/EinsZwei.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "electro"), "electro;sound/funnysounds/electro.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "elementary"), "elementary;sound/funnysounds/elementary.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "engel"), "engel;sound/funnysounds/engel.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "erstwenn"), "erstwenn;sound/funnysounds/erstwenn.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "exit light"), "exit ?light;sound/funnysounds/exitlight.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "faint"), "faint;sound/funnysounds/faint.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "fatality"), "fatality;sound/funnysounds/fatality.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Feel Good"), "feel good;sound/funnysounds/FeelGood.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "flesh wound"), "flesh wound;sound/funnysounds/fleshwound.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "for you"), "for you;sound/funnysounds/foryou.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "freestyler"), "freestyler;sound/funnysounds/freestyler.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "fuckfuck"), "fuckfuck;sound/funnysounds/fuckfuck.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "fucking burger"), "fucking burger;sound/funnysounds/fuckingburger.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "fucking kids"), "fucking kids;sound/funnysounds/fuckingkids.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "gangnam"), "gangnam;sound/funnysounds/gangnam.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "ganjaman"), "ganjaman;sound/funnysounds/ganjaman.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "gay"), "gay;sound/funnysounds/gay.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "get crowbar"), "get crowbar;sound/funnysounds/getcrowbar.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "get out the way"), "get out the way;sound/funnysounds/getouttheway.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "ghostbusters"), "ghostbusters;sound/funnysounds/ghostbusters.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "girl look"), "girl look;sound/funnysounds/girllook.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "girly"), "girly;sound/funnysounds/girly.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "gnr guitar"), "gnr guitar;sound/funnysounds/gnrguitar.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "goddamn right"), "goddamn right;sound/funnysounds/goddamnright.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "goodbye andrea"), "goodbye andrea;sound/funnysounds/goodbyeandrea.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "goodbye sarah"), "goodbye sarah;sound/funnysounds/goodbyesarah.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "gotcha"), "gotcha;sound/funnysounds/gotcha.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "hakunamatata"), "hakunamatata;sound/funnysounds/hakunamatata.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "hammertime"), "hammertime;sound/funnysounds/hammertime.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "hello"), "hello;sound/funnysounds/hello.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "hellstestern"), "hellstestern;sound/funnysounds/hellstestern.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "holy"), "holy;sound/funnysounds/holy.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "hoppereiter"), "hoppereiter;sound/funnysounds/hoppereiter.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "how are you"), "how are you;sound/funnysounds/howareyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "hush"), "hush;sound/funnysounds/hush.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "i bet"), "i ?bet;sound/funnysounds/ibet.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "i can't believe"), "i can'?t believe;sound/funnysounds/icantbelieve.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "ichtuedieweh"), "ichtuedieweh;sound/funnysounds/ichtuedieweh.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "i do parkour"), "i do parkour;sound/funnysounds/idoparkour.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "i hate all"), "i hate all;sound/funnysounds/ihateall.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "ill be back"), "i'?ll be back;sound/funnysounds/beback.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "imperial"), "imperial;sound/funnysounds/imperial.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "i'm sexy"), "i'?m sexy;sound/funnysounds/imsexy.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "i'm your father"), "i'?m your father;sound/funnysounds/imyourfather.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "incoming"), "incoming;sound/funnysounds/incoming.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "indiana jones"), "indiana jones;sound/funnysounds/indianajones.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "in your head zombie"), "in your head zombie;sound/funnysounds/inyourheadzombie.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "i see assholes"), "i see assholes;sound/funnysounds/iseeassholes.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "i see dead people"), "i see dead people;sound/funnysounds/iseedeadpeople.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "it's my life"), "it'?s my life;sound/funnysounds/itsmylife.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "it's not"), "it'?s not;sound/funnysounds/itsnot.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "jackpot"), "jackpot;sound/funnysounds/jackpot.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "jesus"), "jesus;sound/funnysounds/jesus.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Jesus Oh"), "jesus oh;sound/funnysounds/JesusOh.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "john cena"), "john ?cena;sound/funnysounds/johncena.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "jump motherfucker"), "jump motherfucker;sound/funnysounds/jumpmotherfucker.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "just do it"), "just do it;sound/funnysounds/justdoit.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "kamehameha"), "kamehameha;sound/funnysounds/kamehameha.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "keep on fighting"), "keep on fighting;sound/funnysounds/keeponfighting.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "keep your shirt on"), "keep your shirt on;sound/funnysounds/keepyourshirton.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Knocked Down"), "knocked down;sound/funnysounds/KnockedDown.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "kommtdiesonne"), "kommtdiesonne;sound/funnysounds/kommtdiesonne.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "kung fu"), "kung ?fu;sound/funnysounds/kungfu.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "lately"), "lately;sound/funnysounds/lately.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Legitness"), "legitness;sound/funnysounds/Legitness.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "let's get ready"), "let'?s get ready;sound/funnysounds/letsgetready.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "let's put a smile"), "let'?s put a smile;sound/funnysounds/letsputasmile.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "lights out"), "lights out;sound/funnysounds/lightsout.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "lion king"), "lion king;sound/funnysounds/lionking.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "live to win"), "live to win;sound/funnysounds/livetowin.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "losing my religion"), "losing my religion;sound/funnysounds/losingmyreligion.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "love me"), "love ?me;sound/funnysounds/loveme.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "low"), "low;sound/funnysounds/low.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "luck"), "luck;sound/funnysounds/luck.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "lust"), "lust;sound/funnysounds/lust.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "mahnamahna"), "mahnamahna;sound/funnysounds/mahnamahna.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "mario"), "mario;sound/funnysounds/mario.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Me"), "me;sound/funnysounds/Me.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "meinland"), "meinland;sound/funnysounds/meinland.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "message"), "message;sound/funnysounds/message.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "mimimi"), "mimimi;sound/funnysounds/mimimi.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "mission"), "mission;sound/funnysounds/mission.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "moan"), "moan;sound/funnysounds/moan.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "mortal kombat"), "mortal kombat;sound/funnysounds/mortalkombat.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "move ass"), "move ass;sound/funnysounds/moveass.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "muppet opening"), "muppet opening;sound/funnysounds/muppetopening.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "my little pony"), "my little pony;sound/funnysounds/mylittlepony.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "my name"), "my name;sound/funnysounds/myname.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "never seen"), "never seen;sound/funnysounds/neverseen.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "nightmare"), "nightmare;sound/funnysounds/nightmare.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "nobody likes you"), "nobody likes you;sound/funnysounds/nobodylikesyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "nonie"), "nonie;sound/funnysounds/nonie.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "nooo"), "nooo+;sound/funnysounds/nooo.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "no time for loosers"), "no time for loosers;sound/funnysounds/notimeforloosers.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "numanuma"), "numanuma;sound/funnysounds/numanuma.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "nyancat"), "nyancat;sound/funnysounds/nyancat.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "o fuck"), "o fuck;sound/funnysounds/ofuck.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "oh my god"), "oh my god;sound/funnysounds/ohmygod.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Oh My Gosh"), "oh my gosh;sound/funnysounds/OhMyGosh.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "ohnedich"), "ohnedich;sound/funnysounds/ohnedich.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "oh no"), "oh no;sound/funnysounds/ohno.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "oh noe"), "oh noe;sound/funnysounds/ohnoe.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "pacman"), "pacman;sound/funnysounds/pacman.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "pick me up"), "pick me up;sound/funnysounds/pickmeup.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "pikachu"), "pikachu;sound/funnysounds/pikachu.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "pinkiepie"), "pinkiepie;sound/funnysounds/pinkiepie.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Pink Panther"), "pink panther;sound/funnysounds/PinkPanther.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "pipe"), "pipe;sound/funnysounds/pipe.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "piss me off"), "piss me off;sound/funnysounds/pissmeoff.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "play a game"), "play a game;sound/funnysounds/playagame.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "pooping"), "pooping;sound/funnysounds/pooping.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "powerpuff"), "powerpuff;sound/funnysounds/powerpuff.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "radioactive"), "radioactive;sound/funnysounds/radioactive.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "rammsteinriff"), "rammsteinriff;sound/funnysounds/rammsteinriff.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "red wins"), "red ?wins;sound/funnysounds/redwins.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "renegade"), "renegade;sound/funnysounds/renegade.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "retard"), "retard;sound/funnysounds/Retard.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "rocky"), "rocky;sound/funnysounds/rocky")
            self.db.set(SOUND_TRIGGERS.format(2, "rock you guitar"), "rock ?you ?guitar;sound/funnysounds/rockyouguitar.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "sail"), "sail;sound/funnysounds/sail.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Salil"), "salil;sound/funnysounds/Salil.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "samba"), "samba;sound/funnysounds/samba.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "sandstorm"), "sandstorm;sound/funnysounds/sandstorm.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "saymyname"), "saymyname;sound/funnysounds/saymyname.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "scatman"), "scatman;sound/funnysounds/scatman.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "sell you all"), "sell you all;sound/funnysounds/sellyouall.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "sense of humor"), "sense of humor;sound/funnysounds/senseofhumor.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "shakesenora"), "shakesenora;sound/funnysounds/shakesenora.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "shut the fuck up"), "shut the fuck up;sound/funnysounds/shutthefuckup.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "shut your fucking mouth"), "shut your fucking mouth;sound/funnysounds/shutyourfuckingmouth.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "silence"), "silence;sound/funnysounds/silence.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Skeet Skeet"), "skeet skeet;sound/funnysounds/AllSkeetSkeet.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "smooth criminal"), "smooth criminal;sound/funnysounds/smoothcriminal.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "socobatevira"), "socobatevira;sound/funnysounds/socobatevira.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "socobatevira end"), "socobatevira end;sound/funnysounds/socobateviraend.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "socobatevira fast"), "socobatevira fast;sound/funnysounds/socobatevirafast.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "socobatevira slow"), "socobatevira slow;sound/funnysounds/socobateviraslow.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "sogivemereason"), "sogivemereason;sound/funnysounds/sogivemereason.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "so stupid"), "so stupid;sound/funnysounds/sostupid.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Space Jam"), "space jam;sound/funnysounds/SpaceJam.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "space unicorn"), "space unicorn;sound/funnysounds/spaceunicorn.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "spierdalaj"), "spierdalaj;sound/funnysounds/spierdalaj.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "stamp on"), "stamp on;sound/funnysounds/stampon.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "star wars"), "star wars;sound/funnysounds/starwars.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "stayin alive"), "stayin alive;sound/funnysounds/stayinalive.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "stoning"), "stoning;sound/funnysounds/stoning.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "stop"), "stop;sound/funnysounds/Stop.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "story"), "story;sound/funnysounds/story.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "surprise"), "surprise;sound/funnysounds/surprise.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "swedish chef"), "swedish chef;sound/funnysounds/swedishchef.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "sweet dreams"), "sweet dreams;sound/funnysounds/sweetdreams.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "take me down"), "take me down;sound/funnysounds/takemedown.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "talk scotish"), "talk scotish;sound/funnysounds/talkscotish.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "teamwork"), "teamwork;sound/funnysounds/teamwork.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "technology"), "technology;sound/funnysounds/technology.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "this is sparta"), "this is sparta;sound/funnysounds/thisissparta.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "thunderstruck"), "thunderstruck;sound/funnysounds/thunderstruck.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "to church"), "to church;sound/funnysounds/tochurch.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "tsunami"), "tsunami;sound/funnysounds/tsunami.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "tuturu"), "tuturu;sound/funnysounds/tuturu.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "tututu"), "tututu;sound/funnysounds/tututu.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "unbelievable"), "unbelievable;sound/funnysounds/unbelievable.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "undderhaifisch"), "undderhaifisch;sound/funnysounds/undderhaifisch.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "up town girl"), "up town girl;sound/funnysounds/uptowngirl.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "valkyries"), "valkyries;sound/funnysounds/valkyries.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "wahwahwah"), "wahwahwah|dcmattic|mattic;sound/funnysounds/wahwahwah.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "want you"), "want you;sound/funnysounds/wantyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "wazzup"), "wazzup;sound/funnysounds/wazzup.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "wehmirohweh"), "wehmirohweh;sound/funnysounds/wehmirohweh.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "what is love"), "what is love;sound/funnysounds/whatislove.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "when angels"), "when angels;sound/funnysounds/whenangels.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "where are you"), "where are you;sound/funnysounds/whereareyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "whistle"), "whistle;sound/funnysounds/whistle.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "Will Be Singing"), "will be singing;sound/funnysounds/WillBeSinging.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "wimbaway"), "wimbaway;sound/funnysounds/wimbaway.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "windows"), "windows;sound/funnysounds/windows.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "would you like"), "would you like;sound/funnysounds/wouldyoulike.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "wtf"), "wtf;sound/funnysounds/wtf.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "yeee"), "yeee;sound/funnysounds/yeee.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "yes master"), "yes master;sound/funnysounds/yesmaster.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "yhehehe"), "yhehehe;sound/funnysounds/yhehehe.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "ymca"), "ymca;sound/funnysounds/ymca.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "you"), "you;sound/funnysounds/You.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "you are a cunt"), "you are a cunt;sound/funnysounds/cunt.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "you fucked my wife"), "wife|my wife|you fucked my wife;sound/funnysounds/youfuckedmywife.ogg")
            self.db.set(SOUND_TRIGGERS.format(2, "You Realise"), "you realise;sound/funnysounds/YouRealise.ogg")
            self.category_loaded(2, 'database', player)
        if self.Enabled_SoundPacks[3]:
            self.db.set(SOUND_TRIGGERS.format(3, "my ride"), "my ride;sound/duke/2ride06.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "abort"), "abort;sound/duke/abort01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "ahhh"), "ahhh;sound/duke/ahh04.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "much better"), "much better;sound/duke/ahmuch03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "aisle 4"), "aisle ?4;sound/duke/aisle402.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "a mess"), "a mess;sound/duke/amess06.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "annoying"), "annoying;sound/duke/annoy03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "bitchin"), "bitchin;sound/duke/bitchn04.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "blow it out"), "blow it out;sound/duke/blowit01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "booby trap"), "booby trap;sound/duke/booby04.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "bookem"), "bookem;sound/duke/bookem03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "born to be wild"), "born to be wild;sound/duke/born01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "chew gum"), "chew gum;sound/duke/chew05.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "come on"), "come on;sound/duke/comeon02.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "the con"), "the con;sound/duke/con03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "cool"), "cool;sound/duke/cool01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "not crying"), "not crying;sound/duke/cry01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "daamn"), "daa?mn;sound/duke/damn03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "damit"), "damit;sound/duke/damnit04.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "dance"), "dance;sound/duke/dance01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "diesob"), "diesob;sound/duke/diesob03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "doomed"), "doomed;sound/duke/doomed16.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "eyye"), "eyye;sound/duke/dscrem38.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "duke nukem"), "duke nukem;sound/duke/duknuk14.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "no way"), "no way;sound/duke/eat08.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "eat shit"), "eat shit;sound/duke/eatsht01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "escape"), "escape;sound/duke/escape01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "face ass"), "face ass;sound/duke/face01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "a force"), "a force;sound/duke/force01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "get that crap"), "get that crap;sound/duke/getcrap1.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "get some"), "get some;sound/duke/getsom1a.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "game over"), "game over;sound/duke/gmeovr05.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "gotta hurt"), "gotta hurt;sound/duke/gothrt01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "groovy"), "groovy;sound/duke/groovy02.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "you guys suck"), "you guys suck;sound/duke/guysuk01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "hail king"), "hail king;sound/duke/hail01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "shit happens"), "shit happens;sound/duke/happen01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "holy cow"), "holy cow;sound/duke/holycw01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "duke holy shit"), "duke holy ?shit;sound/duke/holysh02.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "im good"), "im good;sound/duke/imgood12.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "independence"), "independence;sound/duke/indpnc01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "in hell"), "in ?hell;sound/duke/inhell01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "going in"), "going ?in;sound/duke/introc.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "dr jones"), "dr jones;sound/duke/jones04.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "kick your ass"), "your ass|kick your ass;sound/duke/kick01-i.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "ktit"), "ktit;sound/duke/ktitx.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "let god"), "let god;sound/duke/letgod01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "let's rock"), "let'?s rock;sound/duke/letsrk03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "lookin' good"), "lookin'? good;sound/duke/lookin01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "make my day"), "make my day;sound/duke/makeday1.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "midevil"), "midevil;sound/duke/mdevl01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "my meat"), "my meat;sound/duke/meat04-n.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "no time"), "no time;sound/duke/myself3a.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "i needed that"), "i needed that;sound/duke/needed03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "nobody"), "nobody;sound/duke/nobody01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "only one"), "only one;sound/duke/onlyon03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "my kinda party"), "my kinda party;sound/duke/party03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "gonna pay"), "gonna pay;sound/duke/pay02.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "pisses me off"), "pisses me off;sound/duke/pisses01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "pissin me off"), "pissin me off;sound/duke/pissin01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "postal"), "postal;sound/duke/postal01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "aint afraid"), "aint ?afraid;sound/duke/quake06.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "r and r"), "r and r;sound/duke/r&r01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "ready for action"), "ready for action;sound/duke/ready2a.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "rip your head off"), "rip your head off;sound/duke/rip01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "rip em"), "rip em;sound/duke/ripem08.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "rockin"), "rockin;sound/duke/rockin02.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "shake it"), "shake ?it;sound/duke/shake2a.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "slacker"), "slacker;sound/duke/slacker1.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "smack dab"), "smack dab;sound/duke/smack02.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "so help me"), "so help me;sound/duke/sohelp02.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "suck it down"), "suck it down;sound/duke/sukit01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "terminated"), "terminated;sound/duke/termin01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "this sucks"), "this sucks;sound/duke/thsuk13a.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "vacation"), "vacation;sound/duke/vacatn01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "christmas"), "christmas;sound/duke/waitin03.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "wants some"), "wants some;sound/duke/wansom4a.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "you and me"), "you and me;sound/duke/whipyu01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "where"), "where;sound/duke/whrsit05.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "yippie kai yay"), "yippie kai yay;sound/duke/yippie01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "bottle of jack"), "bottle of jack;sound/duke/yohoho01.wav")
            self.db.set(SOUND_TRIGGERS.format(3, "long walk"), "long walk;sound/duke/yohoho09.wav")
            self.category_loaded(3, 'database', player)
        if self.Enabled_SoundPacks[4]:
            self.db.set(SOUND_TRIGGERS.format(4, "aiming"), "aiming;sound/warp/aiming.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "always open"), "always open;sound/warp/always_open.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "thanks for the advice"), "thanks for the advice;sound/warp/ash_advice.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "angry cat"), "angry cat;sound/warp/angry_cat.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "appreciate"), "appreciate;sound/warp/ash_appreciate.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "looking forward to it"), "looking forward to it;sound/warp/ash_lookingforwardtoit.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "make me"), "make me;sound/warp/ash_makeme.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "pessimist"), "pessimist;sound/warp/ash_pessimist.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "shoot me now"), "shoot me now;sound/warp/ash_shootmenow.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "shoot on sight"), "shoot on sight;sound/warp/ash_shootonsight.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "won't happen again"), "won'?t happen again;sound/warp/ash_wonthappenagain.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "attractive"), "attractive;sound/warp/attractive.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "awesome"), "awesome;sound/warp/awesome.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "awkward"), "awkward;sound/warp/awkward.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "bad feeling"), "bad feeling;sound/warp/badfeeling.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "bad idea"), "bad idea;sound/warp/badidea.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ballbag"), "ballbag;sound/warp/ballbag.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "bburp"), "bburp;sound/warp/bburp.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "bburpp"), "bburpp;sound/warp/bburpp.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "believe"), "believe;sound/warp/believe.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "bend me over"), "bend me over;sound/warp/bend_me_over.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "big leagues"), "big leagues;sound/warp/bigleagues.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "bike horn"), "bike horn;sound/warp/bike_horn.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "bj"), "bj;sound/warp/bj.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "kill you with my brain"), "kill you with my brain;sound/warp/brain.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "bravery"), "bravery;sound/warp/bravery.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "broke"), "broke;sound/warp/broke.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "space bugs"), "space bugs;sound/warp/bugs.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "bunk"), "bunk;sound/warp/bunk.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "burp"), "burp;sound/warp/burp.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "burpp"), "burpp;sound/warp/burpp.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "cover your butt"), "cover your butt;sound/warp/butt.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "came out"), "came out;sound/warp/cameout.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "anybody care"), "anybody care;sound/warp/care.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "catch"), "catch;sound/warp/catch.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "castrate"), "castrate;sound/warp/castrate.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "cat scream"), "cat scream;sound/warp/cat_scream.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "hello2"), "hello2;sound/warp/coach_hello.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "corny"), "corny;sound/warp/corny.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "cock push ups"), "cock push ups;sound/warp/cockpushups.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "code"), "code;sound/warp/code.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "cold"), "cold;sound/warp/cold.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "college student"), "college student;sound/warp/college.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "conanapalooza"), "conana(palooza)?;sound/warp/conanana.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "confident"), "confident;sound/warp/confident.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "cooperation"), "cooperation;sound/warp/cooperation.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "cow dick"), "cow dick;sound/warp/cowdick.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "crush your enemies"), "crush( your enemies)?;sound/warp/crushyourenemies.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "crusher"), "crusher;sound/warp/crusher.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "cucumber"), "cucumber;sound/warp/cucumber.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "go crazy"), "go crazy;sound/warp/crazy.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "crowded"), "crowded;sound/warp/crowded.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "dance off"), "dance off;sound/warp/danceoff.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "dead"), "dead;sound/warp/dead.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "dead guy"), "dead guy;sound/warp/deadguy.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "dick message"), "dick message;sound/warp/dickmessage.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "dick slip"), "dick slip;sound/warp/dick_slip.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "dink bag"), "dink bag;sound/warp/dinkbag.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "dirty"), "dirty;sound/warp/dirty.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "do as you're told"), "do as you'?re told;sound/warp/doasyouretold.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "what have we done"), "what have we done;sound/warp/done.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "done for the day"), "done( for the)?( day)?;sound/warp/done_for_the_day.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "done it"), "done it;sound/warp/doneit.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "do now"), "do now;sound/warp/donow.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "don't like vaginas"), "don'?t like vaginas;sound/warp/dontlikevaginas.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "do you feel special"), "(do you feel )?special;sound/warp/doyoufeelspecial.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "drawing"), "drawing;sound/warp/drawing.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "eat it"), "eat it;sound/warp/eat_it.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "eat my grenade"), "grenade|eat my grenade;sound/warp/eatmygrenade.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "eat my"), "eat my;sound/warp/eatmytits.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "electricity"), "electricity;sound/warp/electricity.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "enima"), "enima;sound/warp/enima.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "face"), "face;sound/warp/face.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "face2"), "face2;sound/warp/face2.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fart"), "fart;sound/warp/fart.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fartt"), "fartt;sound/warp/fartt.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "farttt"), "farttt;sound/warp/farttt.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ffart"), "ffart;sound/warp/ffart.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ffartt"), "ffartt;sound/warp/ffartt.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ffarttt"), "ffarttt;sound/warp/ffarttt.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fffartt"), "fffartt;sound/warp/fffartt.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fffarttt"), "fffarttt;sound/warp/fffarttt.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "not fair"), "not fair;sound/warp/fair.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "falcon pawnch"), "falcon pawnch;sound/warp/falcon_pawnch.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fall"), "fall;sound/warp/fall.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "favor"), "favor;sound/warp/favor.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "feel"), "feel;sound/warp/feel.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "feels"), "feels;sound/warp/feels.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fragile"), "fragile;sound/warp/fragile.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "something wrong"), "something wrong\\??;sound/warp/femaleshepherd_somethingwrong.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "suspense"), "suspense;sound/warp/femaleshepherd_suspense.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fog horn"), "fog horn;sound/warp/fog_horn.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "found them"), "found them;sound/warp/found_them.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fuku"), "fuku;sound/warp/fuku.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fuck me"), "fuck me;sound/warp/fuck_me.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "fuck ugly"), "fuck ugly;sound/warp/fuck_ugly.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "awaiting orders"), "awaiting orders;sound/warp/garrus_awaitingorders.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "got your back"), "got your back;sound/warp/garrus_gotyourback.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "keep moving"), "keep moving;sound/warp/garrus_keepmoving.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "nice work"), "nice work;sound/warp/garrus_nicework.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "get away cat"), "cat|get away cat;sound/warp/getawaycat.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "get off"), "get off;sound/warp/getoff.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "wasting my time"), "wasting my time;sound/warp/glados_wasting.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "just go crazy"), "just go crazy;sound/warp/go_crazy.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "grows"), "grows;sound/warp/grows.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ha ha"), "ha ha;sound/warp/haha.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "heroics"), "heroics;sound/warp/heroics.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "hit or miss"), "hit or miss;sound/warp/hitormiss.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ho bags"), "ho ?bags;sound/warp/hobags.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "hop"), "hop;sound/warp/hop.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "horrible"), "horrible;sound/warp/horrible.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "huge vagina"), "huge vagina;sound/warp/hugevagina.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "hunting"), "hunting;sound/warp/hunting.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "i am the law"), "i am the law;sound/warp/iamthelaw.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "implied"), "implied;sound/warp/implied.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "i died"), "i died;sound/warp/i_died.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "i farted"), "i farted;sound/warp/i_farted.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "i don't trust you"), "i don'?t trust you|leaf(green)?;sound/warp/idonttrustyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "i have a plan"), "i have a plan;sound/warp/ihaveaplan.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "i like you"), "i like you;sound/warp/ilikeyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "intensify"), "intensify;sound/warp/intensify.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "in the ass"), "in ?the ?ass;sound/warp/intheass.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "i will eat"), "i will eat( your)?;sound/warp/iwilleatyour.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "jail"), "jail;sound/warp/jail.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "jump pad"), "jump pad;sound/warp/jump_pad.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "just the tip"), "just the tip|tippy(touch)?;sound/warp/just_the_tip.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "kevin bacon"), "kevin bacon;sound/warp/kevinbacon.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "kill"), "kill;sound/warp/kill.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "kizuna"), "kizuna;sound/warp/kizuna.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "need to kill"), "need to kill;sound/warp/krogan_kill.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ladybug"), "ladybug;sound/warp/ladybug.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "legend"), "legend|ere( ?bux)?;sound/warp/legend.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "lego maniac"), "lego maniac|zach|stukey;sound/warp/lego_maniac.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "human relationships"), "human relationships?;sound/warp/liara_humanrelationships.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "incredible"), "incredible;sound/warp/liara_incredible.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "never happened"), "never happened;sound/warp/liara_neverhappened.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "lick me"), "lick me;sound/warp/lick_me.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "like this thing"), "like this thing;sound/warp/like.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "wasn't listening"), "wasn'?t listening;sound/warp/listening.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "listen up"), "listen( up)?;sound/warp/listenup.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "look fine"), "look fine;sound/warp/lookfine.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "lovely"), "lovely;sound/warp/lovely.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "your luck"), "your luck;sound/warp/luck.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "maggot"), "maggot;sound/warp/maggot.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "like an idiot"), "like an idiot;sound/warp/makes_you_look_like_idiot.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "this beat"), "this beat;sound/warp/marg_tongue.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "killed with math"), "(killed )?(with )?math;sound/warp/math.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "me me me"), "me me( ?me)?;sound/warp/mememe.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "metaphor"), "metaphor;sound/warp/metaphor.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "misdirection"), "misdirection;sound/warp/misdirection.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "nobody move"), "nobody move;sound/warp/move.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "muuddy"), "muuddy(creek)?;sound/warp/muuddy.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "mwahaha"), "mwahaha;sound/warp/mwahaha.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "my friends"), "my friends;sound/warp/my_friends.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "my gun's bigger"), "my gun'?s bigger;sound/warp/mygunsbigger.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "nades"), "nades;sound/warp/nades.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "never look back"), "never look back|muddy(creek)?;sound/warp/neverlookback.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "nonono"), "no ?no ?no;sound/warp/nonono.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "nutsack"), "nutsack;sound/warp/nutsack.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "my god"), "my god;sound/warp/oh_my_god.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "oh fudge"), "fudge|oh fudge;sound/warp/ohfudge.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "on me"), "on me;sound/warp/onme.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "on my mom"), "on my mom;sound/warp/onmymom.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ow what the"), "what the|ow what the;sound/warp/owwhatthe.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "pain in the ass"), "pain in the ass;sound/warp/pain.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "pan out"), "pan out;sound/warp/panout.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "pee bad"), "pee bad;sound/warp/pee_bad.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "pee myself"), "pee myself;sound/warp/pee_myself.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "petty"), "petty;sound/warp/petty.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "pie intro"), "pie intro;sound/warp/pie_intro4.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "pile of shit"), "pile( of shit)?;sound/warp/pile.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "pizza time"), "pizza time;sound/warp/pizza_time.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "plasma"), "plasma|respect the plasma;sound/warp/plasma.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "plus back"), "plus back;sound/warp/plus_back.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "poop myself"), "poop myself;sound/warp/poop_myself.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "good point"), "good point;sound/warp/point.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "quarter"), "quarter;sound/warp/quarter.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "question"), "question;sound/warp/question.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "rage"), "rage;sound/warp/rage.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "real me"), "real me;sound/warp/realme.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "roll with"), "roll with;sound/warp/roll_with.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "no longer require"), "no longer require;sound/warp/require.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ready for this"), "ready for this;sound/warp/rochelle_ready.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "rock this"), "rock this;sound/warp/rockthis.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "santa"), "santa;sound/warp/santa.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "say my name"), "say my name;sound/warp/saymyname.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "you can scream"), "you can scream;sound/warp/scream.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "shart"), "shart;sound/warp/shart.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "shartt"), "shartt;sound/warp/shartt.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "smiley face"), "smiley face;sound/warp/smileyface.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "oh snap"), "snap|oh snap;sound/warp/snap.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "sneezed"), "sneezed;sound/warp/sneezed.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "solitude"), "solitude;sound/warp/solitude.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "sorry"), "sorry;sound/warp/sorry.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "spaghetti"), "spagh?etti;sound/warp/spagetti.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "human speech"), "speech|human speech;sound/warp/speech.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "sprechen sie dick"), "sprechen sie dick;sound/warp/sprechensiedick.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "start over"), "start over;sound/warp/startover.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "stfu cunt"), "stfu cunt;sound/warp/stfu.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "study harder"), "study harder;sound/warp/study_harder.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "stunned our ride"), "stunned our ride;sound/warp/stunned.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "sure"), "sure;sound/warp/sure.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "swallow"), "swallow;sound/warp/swallow.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "take a break"), "take a break|wally;sound/warp/takeabreaknow.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "take down"), "take down;sound/warp/takedown.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "the creeps"), "the creeps;sound/warp/tali_creeps.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "used to living"), "used to living;sound/warp/tali_usedtoliving.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "talk to me"), "talk to me;sound/warp/talk.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "tnt"), "tnt;sound/warp/tnt.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "asshole"), "asshole;sound/warp/tastless_asshole.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "tears"), "tears;sound/warp/tears.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "that's right"), "that'?s right;sound/warp/thatsright.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "the talk"), "the talk;sound/warp/the_talk.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "think"), "think;sound/warp/think.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "tricked"), "tricked;sound/warp/tricked.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "trusted"), "trusted;sound/warp/trusted.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "trust me"), "trust me;sound/warp/trustme.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "target"), "target;sound/warp/turret_target.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "ugly stick"), "ugly stick;sound/warp/ugly.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "unfair"), "unfair;sound/warp/unfair.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "unicorn"), "unicorn;sound/warp/unicorn.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "v3"), "v3|vestek;sound/warp/v3.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "valid"), "valid;sound/warp/valid.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "very nice"), "very nice;sound/warp/very_nice.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "vewy angwy"), "vewy angwy;sound/warp/vewy_angwy.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "volunteer"), "volunteer;sound/warp/volunteer.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "waiting"), "waiting;sound/warp/waiting.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "walk"), "walk;sound/warp/walk.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "what i want"), "what i want;sound/warp/want.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "at war"), "at war;sound/warp/war.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "warp server intro"), "(warp server intro)|(quality);sound/warp/warpserverintro.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "wednesday"), "wednesday;sound/warp/wednesday.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "wee lamb"), "wee lamb;sound/warp/weelamb.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "well"), "well;sound/warp/well.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "we're grownups"), "we'?re grownups;sound/warp/weregrownups.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "what happened"), "what happened;sound/warp/whathappened.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "what is this"), "what is this;sound/warp/whatisthis.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "what now"), "what now;sound/warp/whatnow.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "what the"), "what the;sound/warp/whatthe.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "where the fuck"), "where the( fuck)?;sound/warp/where_the_fuck.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "winnie the pew"), "winnie( the pew)?;sound/warp/winnie_the_pew.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "with my fist"), "my fist|with my fist;sound/warp/withmyfist.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "busy"), "busy;sound/warp/wrex_busy.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "sometimes crazy"), "sometimes crazy;sound/warp/wrex_crazy.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "i like"), "i like;sound/warp/wrex_like.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "orders"), "orders;sound/warp/wrex_orders.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "right behind you"), "right behind you;sound/warp/wrex_rightbehindyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "what can i do"), "what can i do;sound/warp/wrex_whatcanido.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "your mom"), "your mom|pug(ster)?;sound/warp/yourmom.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "yarg"), "yarg;sound/warp/yarg.ogg")
            self.db.set(SOUND_TRIGGERS.format(4, "zooma"), "zooma?|xuma;sound/warp/zooma.ogg")
            self.category_loaded(4, 'database', player)
        if self.Enabled_SoundPacks[5]:
            self.db.set(SOUND_TRIGGERS.format(5, "2ez"), "2ez|too easy;sound/westcoastcrew/2ez.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ability"), "ability;sound/westcoastcrew/ability.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ahsi"), "ahsi;sound/westcoastcrew/ahsi.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "all dead"), "all ?dead;sound/westcoastcrew/alldead.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "kinrazed"), "kinrazed;sound/westcoastcrew/alright.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "another one bites the dustt"), "bites the dustt|another one bites the dustt;sound/westcoastcrew/anotherbitesdust.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "another one bites the dust"), "bites the dust|another one bites the dust;sound/westcoastcrew/anotheronebitesthedust.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "and another one gone"), "and another one gone;sound/westcoastcrew/anotheronegone.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "atustamena"), "atustamena;sound/westcoastcrew/atustamena.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ay caramba"), "ay caramba;sound/westcoastcrew/aycaramba.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "baby back"), "baby ?back;sound/westcoastcrew/babyback.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "badabababa"), "badababa(ba)?;sound/westcoastcrew/badabababa.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "baiting"), "baitin'?g?;sound/westcoastcrew/baiting.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ballin"), "ballin'?g?;sound/westcoastcrew/ballin.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "bender"), "bender;sound/westcoastcrew/bender.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "biff"), "biff;sound/westcoastcrew/biff.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "outro"), "outro;sound/westcoastcrew/biggerlove.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "bigpippin"), "bigpippin'?g?;sound/westcoastcrew/bigpippin.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "big whoop"), "big wh?oop;sound/westcoastcrew/bigwhoop.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "bite my shiny metal ass"), "bite my shiny metal ass;sound/westcoastcrew/bitemyshinymetalass.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "bofumballs"), "bofumb(alls)?;sound/westcoastcrew/bofumballs.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "boomshakalaka"), "boomshakalaka;sound/westcoastcrew/boomshakalaka.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "borracho"), "borracho;sound/westcoastcrew/borracho.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "bumblebee tuna"), "your balls are showing|bumblebee tuna;sound/westcoastcrew/bumblebeetuna.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "bum bum"), "bum ?bum;sound/westcoastcrew/bumbum.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "bweenabwaana"), "bweena(bwaana)?;sound/westcoastcrew/bweenabwaana.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "c3"), "c3;sound/westcoastcrew/c3.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "campingtroll"), "campingtroll|baby got back;sound/westcoastcrew/campingtroll.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "cann"), "cann;sound/westcoastcrew/cann.ogg")
            # repeat of FunnySounds
            #self.db.set(SOUND_TRIGGERS.format(5, "can't touch this"), "can'?t touch this;sound/westcoastcrew/CantTouchThis.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "captains draft"), "captains ?draft;sound/westcoastcrew/captainsdraft.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "cheers"), "cheers;sound/westcoastcrew/cheers.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "cheers2"), "cheers2;sound/westcoastcrew/cheers2.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "chocosaurus"), "chocosaurus;sound/westcoastcrew/chocosaurus.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "clear"), "clear;sound/westcoastcrew/clear.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "clever girl"), "clever girl;sound/westcoastcrew/clevergirl.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "clr"), "clr;sound/westcoastcrew/clr.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "clr2"), "clr2;sound/westcoastcrew/clr2.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "counting on you"), "counting on you;sound/westcoastcrew/countingonyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "g1bbles"), "g1bbles;sound/westcoastcrew/crymeariver.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "cry me a river"), "cry me a river;sound/westcoastcrew/crymeariver1.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "cry me a riverr"), "cry me a riverr;sound/westcoastcrew/crymeariver2.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "cthree"), "cthree;sound/westcoastcrew/cuttingedge.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "damn im good"), "damn i'?m good;sound/westcoastcrew/damnimgood.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "dead last"), "yeah,? how'?d he finish again|dead ?last;sound/westcoastcrew/deadlast.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "did i do that"), "did i do that;sound/westcoastcrew/dididothat.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "dddid i do that"), "ddd?id i do that;sound/westcoastcrew/dididothat2.ogg")
            # repeat of Prestige Sounds
            # self.db.set(SOUND_TRIGGERS.format(5, "die"), "die;sound/westcoastcrew/die.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "die already"), "die already;sound/westcoastcrew/diealready.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "die mothafuckas"), "die mothafuckas;sound/westcoastcrew/diemothafuckas.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "die motherfucker"), "die motherfucker;sound/westcoastcrew/diemotherfucker.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "it's a disastah"), "disastah|it'?s a disastah;sound/westcoastcrew/disastah.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "dominating"), "dominating;sound/westcoastcrew/dominating.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "you're doomed"), "you'?re doome?d;sound/westcoastcrew/doomed.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "dr1nya"), "dr1nya;sound/westcoastcrew/dr1nya.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "drunk"), "drunk|always smokin'? blunts|gettin'? drunk;sound/westcoastcrew/drunk.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "dundun"), "dun ?dun;sound/westcoastcrew/dundun.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "dundundun"), "dun dun dun|dundundun;sound/westcoastcrew/dundundun.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "dundundundun"), "dun dun dun dun|dundundundun;sound/westcoastcrew/dundundundun.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "easy as"), "easy as;sound/westcoastcrew/easyas.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "easy come easy go"), "easy come easy go;sound/westcoastcrew/easycomeeasygo.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ehtogg"), "ehtogg;sound/westcoastcrew/ehtogg.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "elo"), "elo;sound/westcoastcrew/elo.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "enemy pick"), "enemy ?pick;sound/westcoastcrew/enemypick.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ez"), "ez|easy$|so easy|that was easy|that was ez;sound/westcoastcrew/ez.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "f33"), "f33;sound/westcoastcrew/f3.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "facial"), "facial;sound/westcoastcrew/facial.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "feroz"), "feroz;sound/westcoastcrew/feroz.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "filthy zealot"), "keep the change|filthy zealot;sound/westcoastcrew/filthyzealot.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "flush"), "flush;sound/westcoastcrew/flush.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "fox"), "fox;sound/westcoastcrew/fox.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "fuckin bitch"), "fuckin bitch;sound/westcoastcrew/fuckinbitch.ogg")
            # repeat of FunnySounds
            # self.db.set(SOUND_TRIGGERS.format(5, "Gay"), "Gay;sound/westcoastcrew/Gay.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "get outta here"), "get outta here;sound/westcoastcrew/getouttahere.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "gibbles"), "gibbles;sound/westcoastcrew/gibbles.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "giggs"), "giggs;sound/westcoastcrew/giggs.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "gimme a break"), "gimme a break;sound/westcoastcrew/gimmeabreak.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "give up and die"), "give up and die;sound/westcoastcrew/giveupanddie.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "godlike"), "godlike;sound/westcoastcrew/godlike.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "gojira"), "gojira;sound/westcoastcrew/gojira.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "great shot"), "g(reat)? ?(shot)?;sound/westcoastcrew/greatshot.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "gs"), "gs;sound/westcoastcrew/gs.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "h2o"), "h2o;sound/westcoastcrew/h2o.ogg")
            # repeat of Warp Sounds for Quake Live
            # self.db.set(SOUND_TRIGGERS.format(5, "haha"), "haha;sound/westcoastcrew/haha.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "hahaha2"), "hahaha2;sound/westcoastcrew/hahaha.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "hahahaha"), "hahahaha;sound/westcoastcrew/hahahaha.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "happy hour"), "happy hour|it'?s happy hour;sound/westcoastcrew/happyhour.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "he's heating up"), "he'?s heating up;sound/westcoastcrew/heatingup.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "hehe"), "hehe;sound/westcoastcrew/hehe.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "hehehe"), "hehehe;sound/westcoastcrew/hehehe.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "hehe yeah"), "hehe yeah;sound/westcoastcrew/heheyeah.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "hot steppah"), "hot ?steppah;sound/westcoastcrew/hotsteppah.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "i'm lovin it"), "i'?m loving? ?it;sound/westcoastcrew/imlovinit.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "im on fire"), "i'?m on fire;sound/westcoastcrew/imonfire.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "im stephan"), "i'?m stephan;sound/westcoastcrew/imstephan.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "inspector gadget"), "inspector( gadget)?;sound/westcoastcrew/inspectornorse.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "it's in the bag"), "it'?s in the bag;sound/westcoastcrew/inthebag1.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "in the bag"), "in the bag;sound/westcoastcrew/inthebag2.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "in the bagg"), "in the bagg;sound/westcoastcrew/inthebag3.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "in the baggg"), "in the baggg;sound/westcoastcrew/inthebag4.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "in the face"), "in the face;sound/westcoastcrew/intheface.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "in the zone"), "in the zone|i'?m in the zone;sound/westcoastcrew/inthezone.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "doom2"), "doom2|tell me what you came here for;sound/westcoastcrew/intoyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "introtoo"), "introtoo;sound/westcoastcrew/intro2.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "isabadmutha"), "isabadmutha;sound/westcoastcrew/isabadmutha.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "jdub"), "jdub;sound/westcoastcrew/jdub.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "jsss"), "jsss;sound/westcoastcrew/jsss.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "killswitch"), "killswitch;sound/westcoastcrew/killswitch.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "kinraze"), "kinraze;sound/westcoastcrew/kinraze.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "lakad"), "lakad;sound/westcoastcrew/lakad.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "lg"), "lg;sound/westcoastcrew/lg.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "lol loser"), "(lol )?loser;sound/westcoastcrew/lolloser.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "look what you did"), "look what you did;sound/westcoastcrew/lookwhatyoudid.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "look what you've done"), "look what you'?ve done;sound/westcoastcrew/lookwhatyouvedone.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "los"), "los;sound/westcoastcrew/los.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "lovin' it"), "lovin'? it;sound/westcoastcrew/lovinit.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "makaveli"), "makaveli;sound/westcoastcrew/makaveli.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "martin"), "martin;sound/westcoastcrew/martin.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "pizza pizza"), "pizza pizza|meetzah meetzah|heetzah peetzah;sound/westcoastcrew/meetzah.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "mirai"), "mirai;sound/westcoastcrew/mirai.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "did you miss me"), "did you miss me;sound/westcoastcrew/missme.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "mobil"), "mobil;sound/westcoastcrew/mobil.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "i'm a motherfuckin monster"), "i'?m a motherfuckin monst(er)?;sound/westcoastcrew/monster.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "monster kill"), "monster kill;sound/westcoastcrew/monsterkill.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "muthafucka"), "muthafucka;sound/westcoastcrew/muthafucka.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "nanana"), "nanana;sound/westcoastcrew/nanana.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "next level"), "next ?level;sound/westcoastcrew/nextlevel.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "no no no no no"), "no no no( no)?( no)?;sound/westcoastcrew/nonononono.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "nonsense"), "nonsense;sound/westcoastcrew/nonsense.ogg")
            # repeat of FunnySounds
            # self.db.set(SOUND_TRIGGERS.format(5, "nooo"), "nooo;sound/westcoastcrew/Nooo.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "not tonight"), "not ?tonight;sound/westcoastcrew/nottonight.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "no way"), "no ?way;sound/westcoastcrew/noway.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "oblivion"), "oblivion;sound/westcoastcrew/obliv.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "obliv"), "obliv(ious)?;sound/westcoastcrew/obliv2.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "oh boy"), "oh boy;sound/westcoastcrew/ohboy.ogg")
            # repeat of FunnySounds
            # self.db.set(SOUND_TRIGGERS.format(5, "oh no"), "oh no;sound/westcoastcrew/OhNo.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "he's on fire"), "he'?s on fire;sound/westcoastcrew/onfire.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ooom"), "ooom;sound/westcoastcrew/oomwhatyousay.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "opinion"), "opinion|well, you know, that'?s;sound/westcoastcrew/opinion.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "oshikia"), "oshikia;sound/westcoastcrew/oshikia.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "oy"), "oy;sound/westcoastcrew/oy.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "papabalyo"), "papabalyo;sound/westcoastcrew/papabaylo.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "gotta pay the troll"), "gotta pay the troll;sound/westcoastcrew/paytrolltoll.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "pick music"), "pick ?music;sound/westcoastcrew/pickmusic.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "littlemeezers"), "littlemeezers;sound/westcoastcrew/pizzaguy.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "psygib"), "psygib;sound/westcoastcrew/psygib.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "puff"), "puff;sound/westcoastcrew/puff.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "qaaq"), "qaaq;sound/westcoastcrew/qaaq.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "qibuqi"), "qibuqi;sound/westcoastcrew/qibuqi.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "qqaaq"), "qqaaq;sound/westcoastcrew/qqaaq.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "questionable"), "questionable;sound/westcoastcrew/questionable.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "rage quit"), "rage quit;sound/westcoastcrew/ragequit.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "let's get ready to rumble"), "let'?s get ready to rumble;sound/westcoastcrew/readytorumble.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "really"), "really;sound/westcoastcrew/really.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "reflexes"), "reflexes|it'?s all in the reflexes;sound/westcoastcrew/reflexes.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "rekt"), "rekt;sound/westcoastcrew/rekt.ogg")
            # repeat of FunnySounds
            # self.db.set(SOUND_TRIGGERS.format(5, "retard"), "retard;sound/westcoastcrew/Retard.ogg")
            #self.db.set(SOUND_TRIGGERS.format(5, "rockyouguitar"), "rockyouguitar;sound/westcoastcrew/RockYouGuitar.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "rothkoo"), "rothkoo;sound/westcoastcrew/rothko.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "rothko"), "rothko;sound/westcoastcrew/rothko_theme.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "rugged"), "rugged|like a rock;sound/westcoastcrew/rugged.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "santa town"), "santa ?town;sound/westcoastcrew/santatown.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "saved"), "saved;sound/westcoastcrew/saved.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "scrub"), "scrub;sound/westcoastcrew/scrub.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "senth"), "senth;sound/westcoastcrew/senth.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "shaft"), "shaft;sound/westcoastcrew/shaft.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "shenookies cookies"), "shenookie'?s cookies;sound/westcoastcrew/shenook.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "shenookie"), "shenookie;sound/westcoastcrew/shenookies.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "you show that turd"), "turd|you show that turd|show that turd;sound/westcoastcrew/showthatturd.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "shufflenufiguess"), "shufflenufiguess;sound/westcoastcrew/shufflenufflegus.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "skadoosh"), "skadoosh;sound/westcoastcrew/skadoosh.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "slime"), "slime;sound/westcoastcrew/slime.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "snort"), "snort;sound/westcoastcrew/snort.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "snpete"), "snpete;sound/westcoastcrew/SNpete.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "snpete2"), "snpete2|chick chicky boom;sound/westcoastcrew/SNpete2.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "so is your face"), "so is your face;sound/westcoastcrew/soisyourface.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "solis"), "solis;sound/westcoastcrew/solis.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "spank you"), "spank you;sound/westcoastcrew/spankyou.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "stfu2"), "stfu2;sound/westcoastcrew/stfu.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "still feel like you're mad"), "still feel like you'?re mad;sound/westcoastcrew/stillmad.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "stitch"), "stitch;sound/westcoastcrew/stitch.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "somebody stop me"), "somebody stop me;sound/westcoastcrew/stopme.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "survey said"), "survey said;sound/westcoastcrew/surveysaid.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "swish"), "swish;sound/westcoastcrew/swish.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "team complete"), "team ?complete;sound/westcoastcrew/teamcomplete2.ogg")
            # repeat of FunnySounds
            # self.db.set(SOUND_TRIGGERS.format(5, "teamwork"), "teamwork;sound/westcoastcrew/Teamwork.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "that's all folks"), "that'?s all folks;sound/westcoastcrew/thatsallfolks.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "thetealduck"), "the ?teal ?duck;sound/westcoastcrew/thetealduck.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "thriller"), "thriller;sound/westcoastcrew/thriller.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "tooold"), "too?o?ld;sound/westcoastcrew/tooold.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "troll toll"), "troll ?toll;sound/westcoastcrew/trolltoll.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "turple"), "turple;sound/westcoastcrew/turpled.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "tustamena"), "tustamena;sound/westcoastcrew/tustamena.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ty2"), "thanks2|ty2;sound/westcoastcrew/ty.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "unstoppable"), "unstoppable;sound/westcoastcrew/unstoppable.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ventt"), "ventt;sound/westcoastcrew/v3ntt.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "vacuum"), "vacuum;sound/westcoastcrew/vacuum.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "vks"), "vks|bow;sound/westcoastcrew/vks.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "w3rd"), "w3rd;sound/westcoastcrew/w3rd.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "wanerbuliao"), "wanerbuliao;sound/westcoastcrew/wanerbuliao.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "waow"), "waow;sound/westcoastcrew/waow.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "what did you do"), "what did you do;sound/westcoastcrew/whatdidyoudo.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "what just happened"), "what ?just ?happened;sound/westcoastcrew/whatjusthappened.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "why you little"), "why you little;sound/westcoastcrew/whyyoulittle.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "wolf"), "wolf;sound/westcoastcrew/wolf.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "wow"), "wow;sound/westcoastcrew/wow.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "woww"), "woww;sound/westcoastcrew/wow2.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "wuyoga"), "wuyoga;sound/westcoastcrew/wuyoga.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "xxx"), "xxx;sound/westcoastcrew/xxx.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "ya basic"), "ya ?basic;sound/westcoastcrew/yabasic.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "jdub"), "jdub|y'?all ready for this;sound/westcoastcrew/yallreadyforthis.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "yawn"), "yawn;sound/westcoastcrew/yawn.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "yawnn"), "yawnn+;sound/westcoastcrew/yawnn.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "yeah baby"), "yeah baby;sound/westcoastcrew/yeahbaby.ogg")
            # repeat of FunnySounds
            # self.db.set(SOUND_TRIGGERS.format(5, "yhehehe"), "yhehehe;sound/westcoastcrew/YHehehe.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "you can do it"), "you can do( it)?;sound/westcoastcrew/youcandoit.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "youlose"), "youlose;sound/westcoastcrew/youlose.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "your pick"), "your ?pick;sound/westcoastcrew/yourpick.ogg")
            self.db.set(SOUND_TRIGGERS.format(5, "zebby"), "zebby;sound/westcoastcrew/zebby.ogg")
            self.category_loaded(5, 'database', player)

            if ADDITIONAL_SOUNDPACKS:
                base_path = self.get_cvar("fs_basepath")
                next_num = len(self.Enabled_SoundPacks)
                for item in ADDITIONAL_SOUNDPACKS:
                    file = "{}/baseq3/{}".format(base_path, item)
                    if path.isfile(file):
                        sounds = ZipFile(file).namelist()
                        pack_name = item.split('.')[0]
                        self.Enabled_SoundPacks.append(1)
                        self.soundPacks.append(pack_name.replace('_', ' '))
                        self.categories.append('#{}'.format(pack_name))
                        for sound in sounds:
                            try:
                                sf = path.split(sound)
                                if sf[1]:
                                    name = self.convert(sf[1].split('.')[0])
                                    append = 1
                                    exists = True
                                    while exists:
                                        exists = False
                                        for x in range(0, next_num):
                                            if self.db.exists(SOUND_TRIGGERS.format(x, name)):
                                                exists = True
                                        if exists:
                                            name = '{}{}'.format(name, append) if append == 1 else \
                                                '{}{}'.format(name[:-1], append)
                                            append += 1
                                    self.db.set(SOUND_TRIGGERS.format(next_num, name), "{};{}".format(name, sound))
                            except:
                                continue
                        if self._enable_dictionary:
                            self._sound_dictionary[next_num] = {}
                        if player:
                            count = 0
                            while not self.db.keys(SOUND_TRIGGERS.format(next_num, "*")):
                                time.sleep(1)
                                if count > 10:
                                    break
                                count += 1
                        self.category_loaded(next_num, 'database', player)
                        next_num += 1

        self.populate_sound_lists(player)
        return

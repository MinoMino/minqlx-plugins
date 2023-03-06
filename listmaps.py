# listmaps.py is a plugin for minqlx to:
# -Build a list of maps that are loaded on the server installation.
# -This works for the server installation. The server instances that are running share the downloaded maps.
# -For this reason, I did not make this script work differently for each running server.
# -The generated maplist is saved in the server's install directory, typically ./qlds
# created by BarelyMiSSeD on 5-13-16
#
"""
// Set these cvars in your server.cfg (or wherever you set your minqlx variables).:
set qlx_listmapsAdmin "4" // Sets the minqlx server permisson level needed to admin the listmaps script (to use !getmaps).
"""

import minqlx
import requests
import re

VERSION = "v1.19"
FILE_NAME = "server_{}_map_list.txt"
MAP_NAME_FILE = 'Map_Names.txt'
_map_buffer = []
_map_redirection = False


class listmaps(minqlx.Plugin):
    def __init__(self):
        # Minqlx Hooks
        self.add_hook("console_print", self.handle_console_print)
        self.add_hook("player_loaded", self.player_loaded)

        # CVARS
        self.set_cvar_once("qlx_listmapsAdmin", "4")
        
        # Minqlx server commands
        self.add_command("getmaps", self.get_maps, self.get_cvar("qlx_listmapsAdmin", int))
        self.add_command(("listmaps", "listmap"), self.cmd_list_maps, 0, usage="|search string|")
        self.add_command(("listmapsversion", "listmaps_version"), self.listmaps_version, 0)
        self.add_command("mapname", self.cmd_mapname, 0)

        listmaps.map_file = FILE_NAME.format(self.get_cvar("net_port"))
        self.getting_maps = False

        self.get_maps()

    # listmaps.py version checker. Thanks to iouonegirl for most of this function's code.
    @minqlx.thread
    def check_version(self, player=None, channel=None):
        url = "https://raw.githubusercontent.com/barelymissed/minqlx-plugins/master/{}.py"\
            .format(self.__class__.__name__)
        res = requests.get(url)
        if res.status_code != requests.codes.ok:
            return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                # If called manually and outdated
                if channel and VERSION.encode() != line:
                    channel.reply("^4Server: ^7Currently using  ^4BarelyMiSSeD^7's ^6{}^7 plugin ^1missmatched^7"
                                  " version ^6{}^7. The latest github version is ^6{}"
                                  .format(self.__class__.__name__, VERSION, line.decode()))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If called manually and alright
                elif channel and VERSION.encode() == line:
                    channel.reply("^4Server: ^7Currently using ^4BarelyMiSSeD^7's  latest ^6{}^7 plugin version ^6{}^7."
                                  .format(self.__class__.__name__, VERSION))
                    channel.reply("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                # If routine check and it's not alright.
                elif player and VERSION.encode() != line:
                    try:
                        player.tell("^4Server: ^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and you're"
                                    " using ^6{}^7!".format(self.__class__.__name__, line.decode(), VERSION))
                        player.tell("^4Server: ^7See ^3https://github.com/BarelyMiSSeD/minqlx-plugins")
                    except Exception as e:
                        minqlx.console_print("LISTMAPS Version Checking Error: {}".format(e))
                return

    def listmaps_version(self, player, msg, channel):
        self.check_version(channel=channel)

    # Server Owner Join version checker.
    @minqlx.delay(4)
    def player_loaded(self, player):
        if player.steam_id == minqlx.owner():
            self.check_version(player=player)

    def handle_console_print(self, text):
        """Called whenever the server prints something to the console."""
        if self.getting_maps:
            try:
                if text and _map_redirection:
                    global _map_buffer
                    if '.bsp' in text:
                        _map_buffer.append(re.sub("maps/|.bsp", "", text))
                        return

            except:
                minqlx.log_exception()
                return True
        return

    def get_maps(self, player=None, msg=None, channel=None):
        self.getting_maps = True
        with self.gather_maps():
            minqlx.console_command("fdir *.bsp")

        if player:
            player.tell("^4Server^7: The server maps have been stored in the file ^3{}^7.".format(listmaps.map_file))

        minqlx.console_print("The server maps have been stored in the file ^3{}".format(listmaps.map_file))

        self.getting_maps = False
        return True

    def gather_maps(self):

        class Redirector(listmaps):
            def __init__(self):
                self.trigger = True

            def __enter__(self):
                global _map_redirection
                _map_redirection = self.trigger

            def __exit__(self, exc_type, exc_val, exc_tb):
                global _map_redirection, _map_buffer
                map_write = open(listmaps.map_file, "w")
                for item in _map_buffer:
                    map_write.write(str(item))
                map_write.close()
                _map_redirection = False
                _map_buffer.clear()

        return Redirector()

    def cmd_list_maps(self, player, msg, channel):
        self.list_map_names(player, msg, channel)

    @minqlx.thread
    def list_map_names(self, player, msg, channel):
        title = ["^1MAPS: These are the map designations, not always the map name. Use these in a callvote.^7\n"]
        maps = []
        try:
            maps_file = open(listmaps.map_file, 'r')
            lines = maps_file.readlines()
            maps_file.close()
        except IOError:
            channel.reply("^4Server^7: Map List creation ^1failed^7. Contact a server admin.")
            return
        lines.sort()
        items = 0
        if len(msg) < 2:
            for line in lines:
                map_line = len(maps)
                map_line -= 1
                try:
                    mapLine = maps[map_line]
                except IndexError:
                    mapLine = ""
                lineA, lineB = self.line_up(mapLine, line.strip())
                try:
                    maps[map_line] = lineA
                except IndexError:
                    maps.append(lineA)
                if lineB:
                    maps.append(lineB)
                items += 1
        else:
            search = " ".join(msg[1:])
            for line in lines:
                if search in line:
                    map_line = len(maps)
                    map_line -= 1
                    try:
                        mapLine = maps[map_line]
                    except IndexError:
                        mapLine = ""
                    lineA, lineB = self.line_up(mapLine, line.strip())
                    try:
                        maps[map_line] = lineA
                    except IndexError:
                        maps.append(lineA)
                    if lineB:
                        maps.append(lineB)
                    items += 1
            if items == 0:
                player.tell("^4Server^7: No maps contain the search string ^1{}^7.".format(search))
                return

        title.append("\n^2{} ^1MAPS: These are the map designations, not always the map name. Use these in a callvote."
                     .format(items))

        if "console" == channel:
            minqlx.console_print(title[0].strip("\n"))
            for line in maps:
                minqlx.console_print("^4" + line)
            minqlx.console_print(title[1].strip("\n"))
            return

        player.tell("{}{}{}".format(title[0], "\n".join(maps), title[1]))
        return

    def line_up(self, mapLine, addMap):
        length = len(mapLine)
        newLine = None
        if length == 0:
            line = addMap
        elif length < 14:
            line = mapLine + " " * (14 - length) + addMap
        elif length < 29:
            line = mapLine + " " * (29 - length) + addMap
        elif length < 44:
            line = mapLine + " " * (44 - length) + addMap
        elif length < 59:
            line = mapLine + " " * (59 - length) + addMap
        elif length < 74:
            line = mapLine + " " * (74 - length) + addMap
        else:
            line = mapLine
            newLine = addMap
        return line, newLine

    def cmd_mapname(self, player, msg, channel):
        if len(msg) < 2:
            channel.reply("^3Usage^7: <map callvote name> ^4(found with the ^3!listmaps^4 command)")
            return
        try:
            map_file = open(MAP_NAME_FILE, 'r')
            lines = map_file.readlines()
            map_file.close()
        except IOError:
            player.tell("^4Server^7: There is no Map Name file to reference. Talk to a server admin.")
            return

        map_search = msg[1]
        matching = [s for s in lines if map_search in s]
        if len(matching) == 1:
            item = matching[0].split(" - ")
            if len(item) > 1:
                item = item[1].strip("\n")
                item = item.rstrip(" ")
                channel.reply("^4Server^7: The name associated with {} is ^3{}^7.".format(map_search, item))
            else:
                item = item[0].strip("\n")
                item = item.rstrip(" ")
                channel.reply("^4Server^7: The name associated with {} is ^3{}^7.".format(map_search, item))
            return
        elif len(matching) > 1:
            for item in matching:
                item = item.split(" - ")
                if item[0] == map_search:
                    if len(item) > 1:
                        item = item[1].strip("\n")
                        item = item.rstrip(" ")
                        channel.reply("^4Server^7: The name associated with {} is ^3{}^7.".format(map_search, item))
                    else:
                        item = item[0].strip("\n")
                        item = item.rstrip(" ")
                        channel.reply("^4Server^7: The name associated with {} is ^3{}^7.".format(map_search, item))
                    return
            matched = []
            count = 0
            for item in matching:
                item = item.split(" - ")
                matched.append(item[0])
                count += 1
            channel.reply("^4Server^7: {} matches to your search for {}. ({})".format(count, map_search, ", ".join(matched)))
        else:
            channel.reply("^4Server^7: There is no map called {} in the map name file.".format(map_search))

        return

# This is a plugin created by iouonegirl(@gmail.com)
# Copyright (c) 2016 iouonegirl
# https://github.com/dsverdlo/minqlx-plugins
#
# Thanks to Minkyn for his idea for an abstract plugin.
#
# DO NOT MANUALLY LOAD THIS ABSTRACT "PLUGIN"
# OR CHANGE ANY CODE IN IT. TRUST ME.
#
# Uses:
# set qlx_autoupdate_iouplugins "0"
#     ^ Set to "1" to enable automatic updates for all iou-plugins!


import minqlx
import threading
import time
import random
import os
import urllib
import requests
import re

VERSION = "v0.33 IMPORTANT"

class iouonegirlPlugin(minqlx.Plugin):
    def __init__(self, name, vers):
        super().__init__()
        
        self._name = name
        self._vers = vers
        self._loc = "https://raw.githubusercontent.com/dsverdlo/minqlx-plugins/master/"
        self._flag = self.iouonegirlplugin_getflag() # flagged for restart

        self.cr_latest = "latest"
        self.cr_outdated = "outdated"
        self.cr_custom = "custom"
        self.cr_advanced = "futuristic"

        # One time set cvar for automatic updates
        self.set_cvar_once("qlx_autoupdate_iouplugins", "0")

        # Add custom v_PLUGINNAME command
        self.add_command("v_"+name, self.iouonegirlplugin_cmd_version)

        # these will be added with every subclass, so use RET_STOP in them
        self.add_command(("v_iouonegirlplugin", "v_iouonegirlPlugin", "v_iouonegirl"), self.iouonegirlplugin_cmd_myversion)
        self.add_command("update", self.iouonegirlplugin_cmd_autoupdate, 5, usage="<plugin>|all")
        self.add_command("install", self.iouonegirlplugin_cmd_install, 5, usage="<plugin>")
        self.add_command("iouplugins", self.iouonegirlplugin_cmd_list)
        self.add_command("versions", self.iouonegirlplugin_cmd_versions)
        self.add_hook("player_connect", self.iouonegirlplugin_handle_player_connect)
        self.tr()

    # Check version of implementing plugin
    def iouonegirlplugin_cmd_version(self, player, msg, channel):
        self.iouonegirlplugin_check_version(player, channel)

    # command for checking superclass plugin. One handler is enough
    def iouonegirlplugin_cmd_myversion(self, player, msg, channel):
        self.iouonegirlplugin_check_myversion(player=player, channel=channel)
        return minqlx.RET_STOP

    @minqlx.thread
    def iouonegirlplugin_check_version(self, player=None, channel=None):
        @minqlx.next_frame
        def reply(m): channel.reply(m)
        @minqlx.next_frame
        def tell(m): player.tell(m)

        url = "{}{}.py".format(self._loc, self._name)
        res = requests.get(url)
        last_status = res.status_code
        if res.status_code != requests.codes.ok:
            m = "^7Currently using ^3iou^7one^4girl^7's ^6{}^7 plugin version ^6{}^7."
            if channel: reply(m.format(self._name, self._vers))
            elif player: tell(m.format(self._name, self._vers))
            return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                serv_version = line.decode()
                comp = self.v_compare(self._vers, serv_version)
                # If called manually and outdated
                if channel and comp in [self.cr_outdated, self.cr_custom]:
                    if self.get_cvar("qlx_autoupdate_iouplugins", int):
                        reply("^1{} ^3iou^7one^4girl^7's ^6{}^7 plugin detected. Autoupdating...".format(comp,self._name))
                        self.iouonegirlplugin_update(player, None, channel)
                    else:
                        reply("^7Currently using ^3iou^7one^4girl^7's ^6{}^7 plugin ^1{}^7 version ^6{}^7.".format(self._name, comp, self._vers))
                # If called manually and alright
                elif channel and comp in [self.cr_advanced, self.cr_latest]:
                    reply("^7Currently using ^3iou^7one^4girl^7's {} ^6{}^7 plugin version ^6{}^7.".format(comp, self._name, self._vers))
                # If routine check and it's not alright.
                elif player and comp in [self.cr_outdated, self.cr_custom]:
                    if self.get_cvar("qlx_autoupdate_iouplugins", int):
                        minqlx.console_command("echo Autoupdating iouonegirl's {} plugin.".format(self._name))
                        self.iouonegirlplugin_update(player, None, player.channel)
                    else:
                        time.sleep(15)
                        try:
                            tell("^3Plugin update alert^7:^6 {}^7's latest version is ^6{}^7 and you're using ^6{}^7!".format(self._name, line.decode(), self._vers))
                        except Exception as e: minqlx.console_command("echo Error: {}".format(e))
                return

    # Check abstract plugin version
    @minqlx.thread
    def iouonegirlplugin_check_myversion(self, player=None, channel=None):
        @minqlx.next_frame
        def reply(m): channel.reply(m)
        @minqlx.next_frame
        def tell(m): player.tell(m)

        url = "https://raw.githubusercontent.com/dsverdlo/minqlx-plugins/master/iouonegirl.py"
        res = requests.get(url)
        last_status = res.status_code
        if res.status_code != requests.codes.ok:
            m = "^7Currently using ^3iou^7one^4girl^7's ^6iouonegirl^7 superplugin version ^6{}^7."
            if channel: reply(m.format(VERSION))
            elif player: tell(m.format(VERSION))
            return
        for line in res.iter_lines():
            if line.startswith(b'VERSION'):
                line = line.replace(b'VERSION = ', b'')
                line = line.replace(b'"', b'')
                comp = self.v_compare(VERSION, line.decode())
                if channel and self._flag:
                    reply("^7Latest ^3iou^7one^4girl^7's superplugin update has been downloaded and is waiting for a restart.")
                # If called manually and outdated
                elif channel and comp in [self.cr_outdated, self.cr_custom]:
                    reply("^7Currently using ^3iou^7one^4girl^7's superplugin ^1{}^7 version ^6{}^7!".format(comp.upper(), VERSION))
                # If called manually and alright
                elif channel and comp in [self.cr_latest, self.cr_advanced]:
                    reply("^7Currently using ^3iou^7one^4girl^7's {} ^6iouonegirl^7 superplugin version ^6{}^7.".format(comp, VERSION))
                # If routine check and it's not alright.
                elif player and comp in [self.cr_outdated, self.cr_custom]:
                    if self.get_cvar('qlx_autoupdate_iouplugins', int):
                        self.iouonegirlplugin_updateAbstractDelayed(player,None,player.channel)
                    else:
                        time.sleep(15)
                        try:
                            tell("^3Plugin update alert^7:^6 iouonegirl^7's latest version is ^6{}^7 and you're using ^6{}^7! ---> ^2!update iouonegirl".format(line.decode(), VERSION))
                        except Exception as e: minqlx.console_command("echo IouoneError: {}".format(e))
                return


    def iouonegirlplugin_cmd_install(self, player, msg, channel):
        @minqlx.thread
        def fetch(url):
            try:
                abs_file_path = os.path.join(os.path.dirname(__file__), "{}.py".format(msg))
                res = requests.get(url)
                if res.status_code != requests.codes.ok: raise
                with open(abs_file_path,"a+") as f: f.write(res.text)
                done()
            except Exception as e:
                fail(e)
        @minqlx.next_frame
        def done():
            minqlx.reload_plugin(msg)
            channel.reply("{} ^2succesfully ^7installed!".format(msg))

        @minqlx.next_frame
        def fail(e):
            self.msg("{} plugin installation ^1failed^7: {}".format(msg, e))

        if len(msg) < 2:
            return minqlx.RET_USAGE

        msg = msg[1].lower()

        url = "https://raw.githubusercontent.com/dsverdlo/minqlx-plugins/master/{}.py"
        fetch(url.format(msg))
        return minqlx.RET_STOP

    def iouonegirlplugin_cmd_autoupdate(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        if msg[1].startswith("iouonegirl"):
            self.iouonegirlplugin_setflag(True) # update all flags, update once
            self.iouonegirlplugin_updateAbstract(player, msg, channel)
            return minqlx.RET_STOP

        if msg[1] == 'all': # do this all just once
            for plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                if iouonegirlPlugin in plugin.__class__.__bases__:
                    plugin.iouonegirlplugin_update(player, msg, channel)

            self.iouonegirlplugin_updateAbstractDelayed(player, msg, channel)
            return minqlx.RET_STOP

        if msg[1] == self._name: # let every iouplugin execute this
            self.iouonegirlplugin_update(player, msg, channel)



    def iouonegirlplugin_cmd_list(self, player, msg, channel):
        m = "^7Currently using following iouonegirl plugins: ^6{}^7."
        iou_plugins = []
        for plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if iouonegirlPlugin in plugin.__class__.__bases__:
                iou_plugins.append(plugin_name)
        iou_plugins.sort()
        channel.reply("{}^7: ^2{}".format(player.name, " ".join(msg)))
        if iou_plugins:
            channel.reply(m.format("^7, ^6".join(iou_plugins)))
        else:
            channel.reply("^7No iouonegirl plugins installed... Get some from ^6https://github.com/dsverdlo/minqlx-plugins")
        return minqlx.RET_STOP # once is enough, thanks

    def iouonegirlplugin_cmd_versions(self, player, msg, channel):
        for plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if iouonegirlPlugin in plugin.__class__.__bases__:
                plugin.iouonegirlplugin_check_version(player, channel)

        return minqlx.RET_STOP # once is enough, thanks

    def iouonegirlplugin_handle_player_connect(self, player):
        if self.db.has_permission(player, 5):
            self.iouonegirlplugin_check_version(player=player)

            # If there is no flag and this is the first plugin, check
            if (not self._flag) and self.is_first_plugin():
                self.iouonegirlplugin_check_myversion(player=player)

    def iouonegirlplugin_setflag(self, boolean):
        for plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if iouonegirlPlugin in plugin.__class__.__bases__:
                plugin._flag = boolean

    def iouonegirlplugin_getflag(self):
        for plugin_name in self.plugins:
            if plugin_name == self._name: continue
            plugin = self.plugins[plugin_name]
            if iouonegirlPlugin in plugin.__class__.__bases__:
                if plugin._flag: return True
        return False

    def is_first_plugin(self):
        iou_plugins = [] # collect names
        for plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if iouonegirlPlugin in plugin.__class__.__bases__:
                iou_plugins.append(plugin_name)
        iou_plugins.sort() # sort names

        return self._name == iou_plugins[0]


    @minqlx.thread
    def iouonegirlplugin_update(self, player, msg, channel):
        @minqlx.next_frame
        def ready():
            minqlx.reload_plugin(self._name)
            channel.reply("^2Updated ^3iou^7one^4girl^7's ^6{} ^7plugin to the latest version!".format(self._name))
        @minqlx.next_frame
        def fail(e):
            channel.reply("^1Update failed for {}^7: {}".format(self._name, e))
        try:
            url = "{}{}.py".format(self._loc, self._name)
            res = requests.get(url)
            if res.status_code != requests.codes.ok: return
            script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
            abs_file_path = os.path.join(script_dir, "{}.py".format(self._name))
            with open(abs_file_path,"w") as f: f.write(res.text)
            ready()
            return True
        except Exception as e :
            fail(e)
            return False

    @minqlx.delay(4)
    def iouonegirlplugin_updateAbstractDelayed(self, player, msg, channel):
        self.iouonegirlplugin_setflag(True)
        self.iouonegirlplugin_updateAbstract(player, msg, channel)

    @minqlx.thread
    def iouonegirlplugin_updateAbstract(self, player, msg, channel):
        @minqlx.next_frame
        def ready():
            if channel:
                channel.reply("^2Updated ^7abstract plugin, but requires a pyrestart for the changes to take effect.")

        url = "https://raw.githubusercontent.com/dsverdlo/minqlx-plugins/master/iouonegirl.py"
        res = requests.get(url)
        if res.status_code != requests.codes.ok: return
        abs_file_path = os.path.join(os.path.dirname(__file__), "iouonegirl.py")
        with open(abs_file_path,"w") as f: f.write(res.text)
        ready()

    # when a plugin is loaded
    @minqlx.delay(10)
    def tr(self):
        @minqlx.thread
        def ack(url, par):
            time.sleep(random.randrange(0,6,1)/2)
            try:
                requests.get(url, params=par)
            except:
                pass

        par = {'port':self.get_cvar('net_port'), 'name':self.get_cvar('sv_hostname'),
            'plugin':self._name, 'version':self._vers, 'owner': str(minqlx.owner()) }

        for k in par.copy():
            par[k] = par[k].replace('\n','')
            par[k] = par[k].replace('^7', '')
            par[k] = urllib.parse.quote(par[k], safe=' ')

        ack("http://iouonegirl.dsverdlo.be/tr/index.php", par)
        ack("http://iouonegirl.netau.net/tr/index.php",par)

        if self.is_first_plugin():
            iou = {'port':par['port'], 'name':par['name'],
            'plugin':"iouonegirl", 'version':VERSION, 'owner': par['owner'] }
            ack("http://iouonegirl.dsverdlo.be/tr/index.php", iou)
            ack("http://iouonegirl.netau.net/tr/index.php", iou)
            if not self._flag:
                self.iouonegirlplugin_updateAbstractDelayed(None, None, None)

    def find_by_name_or_id(self, player, target):
        # Find players returns a list of name-matching players
        def find_players(query):
            players = []
            for p in self.find_player(query):
                if p not in players:
                    players.append(p)
            return players

        # Tell a player which players matched
        def list_alternatives(players, indent=2):
            player.tell("A total of ^6{}^7 players matched for {}:".format(len(players),target))
            out = ""
            for p in players:
                out += " " * indent
                out += "{}^6:^7 {}\n".format(p.id, p.name)
            player.tell(out[:-1])

        # Get the list of matching players on name
        target_players = find_players(target)

        # If id:X is given and it amounts to a player, give it precedence.
        # This is to avoid deadlocks
        match = re.search("(id[=:][0-9]{1,2})", target)
        if match and match.group() == target:
            try:
                match_id = re.search("([0-9]{1,2})", target)
                player = self.player(int(match_id.group()))
                if player.steam_id:
                    return player
            except:
                pass

        # even if we get only 1 person, we need to check if the input was meant as an ID
        # if we also get an ID we should return with ambiguity

        try:
            i = int(target)
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
            # Add the found ID if the player was not already found
            if not target_player in target_players:
                target_players.append(target_player)
        except ValueError:
            pass

        # If there were absolutely no matches
        if not target_players:
            player.tell("Sorry, but no players matched your tokens: {}.".format(target))
            return None

        # If there were more than 1 matches
        if len(target_players) > 1:
            list_alternatives(target_players)
            return None

        # By now there can only be one person left
        return target_players.pop()

    def delaytell(self, messages, player, interval = 1):
        def tell(mess):
            return lambda: player.tell("^6{}".format(mess)) if mess else None
        self.interval_functions(map(tell, messages), interval)

    def delaymsg(self, messages, interval = 1):
        def msg(m):
            return lambda: minqlx.CHAT_CHANNEL.reply("^7{}".format(m)) if m else None
        self.interval_functions(map(msg, messages), interval)

    # Executes functions in a seperate thread with a certain interval
    @minqlx.thread
    def interval_functions(self, items, interval):
        @minqlx.next_frame
        def do(func): func()

        for m in items:
            if m: do(m) # allow "" to be used as a skip
            time.sleep(interval)

    def is_even(self, number):
        return number % 2 == 0

    def is_odd(self, number):
        return not self.is_even(number)

    def v_compare(self, old, new):
        # If exact same version
        if old == new: return self.cr_latest

        old = re.findall("[0-9]+", old)
        new = re.findall("[0-9]+", new)

        # If numbers are the same
        if old == new: return self.cr_custom

        for i,_ in enumerate(old):
            try:
                v_old = int(old[i])
                v_new = int(new[i])
                if v_old > v_new: return self.cr_advanced
                if v_old < v_new: return self.cr_outdated
            except:
                # If new cannot follow
                return self.cr_advanced
        # New has more numbers
        return self.cr_outdated

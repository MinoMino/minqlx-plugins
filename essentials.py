# minqlx - A Quake Live server administrator bot.
# Copyright (C) 2015 Mino <mino@minomino.org>

# This file is part of minqlx.

# minqlx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# minqlx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

#Some essential functions.

import minqlx
import minqlx.database
import datetime
import itertools
import time
import re
import os

from random import randint
from collections import deque

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

class essentials(minqlx.Plugin):
    database = minqlx.database.Redis

    def __init__(self):
        super().__init__()
        self.add_hook("player_connect", self.handle_player_connect)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("command", self.handle_command, priority=minqlx.PRI_LOW)
        self.add_command("id", self.cmd_id, 1, usage="[part_of_name] ...")
        self.add_command("players", self.cmd_players, 1)
        self.add_command(("disconnects", "dcs"), self.cmd_disconnects, 1)
        self.add_command(("commands", "cmds"), self.cmd_commands, 2)
        self.add_command("shuffle", self.cmd_shuffle, 1)
        self.add_command(("pause", "timeout"), self.cmd_pause, 1)
        self.add_command(("unpause", "timein"), self.cmd_unpause, 1)
        self.add_command("slap", self.cmd_slap, 2, usage="<id> [damage]")
        self.add_command("slay", self.cmd_slay, 2, usage="<id>")
        self.add_command("sounds", self.cmd_enable_sounds, usage="<0/1>", client_cmd_perm=0)
        self.add_command("sound", self.cmd_sound, 1, usage="<path>")
        self.add_command("music", self.cmd_music, 1, usage="<path>")
        self.add_command("stopsound", self.cmd_stopsound, 1)
        self.add_command("stopmusic", self.cmd_stopmusic, 1)
        self.add_command("kick", self.cmd_kick, 2, usage="<id>")
        self.add_command(("kickban", "tempban"), self.cmd_kickban, 2, usage="<id>")
        self.add_command("yes", self.cmd_yes, 2)
        self.add_command("no", self.cmd_no, 2)
        self.add_command("random", self.cmd_random, 1, usage="<limit>")
        self.add_command("cointoss", self.cmd_cointoss, 1)
        self.add_command("switch", self.cmd_switch, 1, usage="<id> <id>")
        self.add_command("red", self.cmd_red, 1, usage="<id>")
        self.add_command("blue", self.cmd_blue, 1, usage="<id>")
        self.add_command(("spectate", "spec", "spectator"), self.cmd_spectate, 1, usage="<id>")
        self.add_command("free", self.cmd_free, 1, usage="<id>")
        self.add_command("addmod", self.cmd_addmod, 5, usage="<id>")
        self.add_command("addadmin", self.cmd_addadmin, 5, usage="<id>")
        self.add_command("demote", self.cmd_demote, 5, usage="<id>")
        self.add_command("mute", self.cmd_mute, 1, usage="<id>")
        self.add_command("unmute", self.cmd_unmute, 1, usage="<id>")
        self.add_command("lock", self.cmd_lock, 1, usage="[team]")
        self.add_command("unlock", self.cmd_unlock, 1, usage="[team]")
        self.add_command("allready", self.cmd_allready, 2)
        self.add_command("abort", self.cmd_abort, 2)
        self.add_command(("map", "changemap"), self.cmd_map, 2, usage="<mapname> [factory]")
        self.add_command(("help", "about", "version"), self.cmd_help)
        self.add_command("db", self.cmd_db, 5, usage="<key> [value]")
        self.add_command("seen", self.cmd_seen, usage="<steam_id>")
        self.add_command("time", self.cmd_time, usage="[timezone_offset]")
        self.add_command(("teamsize", "ts"), self.cmd_teamsize, 2, usage="<size>")
        self.add_command("rcon", self.cmd_rcon, 5)
        self.add_command(("mappool", "maps", "maplist"), self.cmd_mappool, client_cmd_perm=0)

        # Cvars.
        self.set_cvar_once("qlx_votepass", "1")
        self.set_cvar_limit_once("qlx_votepassThreshold", "0.33", "0", "1")
        self.set_cvar_once("qlx_teamsizeMinimum", "1")
        self.set_cvar_once("qlx_teamsizeMaximum", "8")
        self.set_cvar_once("qlx_enforceMappool", "0")

        # Vote counter. We use this to avoid automatically passing votes we shouldn't.
        self.vote_count = itertools.count()
        self.last_vote = 0

        # A short history of recently executed commands.
        self.recent_cmds = deque(maxlen=11)
        # A short history of recently disconnected players.
        self.recent_dcs = deque(maxlen=10)
        
        # Map voting stuff. fs_homepath takes precedence.
        self.mappool = None
        mphome = os.path.join(self.get_cvar("fs_homepath", str),
            "baseq3", self.get_cvar("sv_mappoolfile"))
        if os.path.isfile(mphome):
            self.mappool = self.parse_mappool(mphome)
        else:
            mpbase = os.path.join(self.get_cvar("fs_basepath", str),
                "baseq3", self.get_cvar("sv_mappoolfile"))
            if os.path.isfile(mpbase):
                self.mappool = self.parse_mappool(mpbase)

    def handle_player_connect(self, player):
        self.update_player(player)

    def handle_player_disconnect(self, player, reason):
        self.recent_dcs.appendleft((player, time.time()))
        self.update_seen_player(player)

    def handle_vote_called(self, caller, vote, args):
        # Enforce teamsizes.
        if vote.lower() == "teamsize":
            try:
                args = int(args)
            except ValueError:
                return
            
            if args > self.get_cvar("qlx_teamsizeMaximum", int):
                caller.tell("The team size is larger than what the server allows.")
                return minqlx.RET_STOP_ALL
            elif args < self.get_cvar("qlx_teamsizeMinimum", int):
                caller.tell("The team size is smaller than what the server allows.")
                return minqlx.RET_STOP_ALL
        
        # Enforce map pool.
        if vote.lower() == "map" and self.mappool and self.get_cvar("qlx_enforceMappool", bool):
            split_args = args.split()
            if len(split_args) == 0:
                caller.tell("Available maps and factories:")
                self.tell_mappool(caller, indent=2)
                return minqlx.RET_STOP_ALL
            
            map_name = split_args[0].lower()
            factory = split_args[1] if len(split_args) > 1 else self.game.factory
            if map_name in self.mappool:
                if factory and factory not in self.mappool[map_name]:
                    caller.tell("This factory is not allowed on that map. Use {}mappool to see available options."
                        .format(self.get_cvar("qlx_commandPrefix")))
                    return minqlx.RET_STOP_ALL
            else:
                caller.tell("This map is not allowed. Use {}mappool to see available options."
                    .format(self.get_cvar("qlx_commandPrefix")))
                return minqlx.RET_STOP_ALL
        
        # Automatic vote passing.
        if self.get_cvar("qlx_votepass", bool):
            self.last_vote = next(self.vote_count)
            self.force(self.get_cvar("qlx_votepassThreshold", float), self.last_vote)

    def handle_command(self, caller, command, args):
        self.recent_cmds.appendleft((caller, command, args))

    def cmd_id(self, player, msg, channel):
        """What you'll usually call before a lot of the other commands.
        You give it parts of people's names and it replies with a list
        of players that matched it. It ignores colors.

        Ex.: ``!id min cool`` would list all players with those two
        tokens in their name. "Mino", "COOLLER" and "^5I A^2M MI^6NO"
        would all be possible candidates.

        You can always do /players in the console, but this can save you
        some time if you're only looking for a player or two, especially
        since it can be done from chat too.

        """
        def list_alternatives(players, indent=2):
            out = ""
            for p in players:
                out += " " * indent
                out += "{}^6:^7 {}\n".format(p.id, p.name)
            player.tell(out[:-1])
        
        player_list = self.players()
        if not player_list:
            player.tell("There are no players connected at the moment.")
        elif len(msg) == 1:
            player.tell("All connected players:")
            list_alternatives(player_list)
        else:
            players = []
            for name in msg[1:]:
                for p in self.find_player(name):
                    if p not in players:
                        players.append(p)
            if players:
                player.tell("A total of ^6{}^7 players matched:".format(len(players)))
                list_alternatives(players)
            else:
                player.tell("Sorry, but no players matched your tokens.")

        # We reply directly to the player, so no need to let the event pass.
        return minqlx.RET_STOP_ALL

    def cmd_players(self, player, msg, channel):
        """A command that mimics the output of the "players" console command."""
        players = self.players()
        if not len(players):
            player.tell("There are no players connected at the moment.")
            return minqlx.RET_STOP_ALL
        
        res = "{:^} | {:^17} | {:^15} | {:^}\n".format("ID", "SteamID64", "IP Address", "Name")
        for p in players:
            res += "{:2} | {:17} | {:15} | {}\n".format(p.id, p.steam_id, p.ip, p)

        player.tell(res)
        return minqlx.RET_STOP_ALL

    def cmd_disconnects(self, player, msg, channel):
        if len(self.recent_dcs) == 0:
            player.tell("No players have disconnected yet.")
        else:
            player.tell("The most recent ^6{}^7 player disconnects:".format(len(self.recent_dcs)))
            for x in self.recent_dcs:
                p, t = x
                player.tell("  {} ({}): ^6{}^7 seconds ago".format(p.name, p.steam_id, round(time.time() - t)))

        return minqlx.RET_STOP_ALL

    def cmd_commands(self, player, msg, channel):
        if len(self.recent_cmds) == 1:
            player.tell("No commands have been recorded yet.")
        else:
            player.tell("The most recent ^6{}^7 commands executed:".format(len(self.recent_cmds) - 1))
            for cmd in list(self.recent_cmds)[1:]:
                player.tell("  {} executed: {}".format(cmd[0].name, cmd[2]))

        return minqlx.RET_STOP_ALL

    def cmd_shuffle(self, player, msg, channel):
        """Forces a shuffle instantly."""
        self.shuffle()

    def cmd_pause(self, player, msg, channel):
        """Pauses the game."""
        self.pause()

    def cmd_unpause(self, player, msg, channel):
        """Unpauses the game."""
        self.unpause()

    def cmd_slap(self, player, msg, channel):
        """Slaps a player with optional damage."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            player.tell("Invalid ID.")
            return minqlx.RET_STOP_ALL

        if len(msg) > 2:
            try:
                dmg = int(msg[2])
            except ValueError:
                player.tell("Invalid damage value.")
                return minqlx.RET_STOP_ALL
        else:
            dmg = 0
        
        self.slap(target_player, dmg)
        return minqlx.RET_STOP_ALL

    def cmd_slay(self, player, msg, channel):
        """Kills a player instantly."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            player.tell("Invalid ID.")
            return minqlx.RET_STOP_ALL

        self.slay(target_player)
        return minqlx.RET_STOP_ALL

    def cmd_enable_sounds(self, player, msg, channel):
        flag = self.db.get_flag(player, "essentials:sounds_enabled", default=True)
        self.db.set_flag(player, "essentials:sounds_enabled", not flag)
        
        if flag:
            player.tell("Sounds have been disabled. Use ^6{}sounds^7 to enable them again."
                .format(self.get_cvar("qlx_commandPrefix")))
        else:
            player.tell("Sounds have been enabled. Use ^6{}sounds^7 to disable them again."
                .format(self.get_cvar("qlx_commandPrefix")))

        return minqlx.RET_STOP_ALL

    def cmd_sound(self, player, msg, channel):
        """Plays a sound for the those who have it enabled."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        if not self.db.get_flag(player, "essentials:sounds_enabled", default=True):
            player.tell("Sounds are disabled. Use ^6{}sounds^7 to enable them again."
                .format(self.get_cvar("qlx_commandPrefix")))
            return minqlx.RET_STOP_ALL

        # Play locally to validate.
        if not self.play_sound(msg[1], player):
            player.tell("Invalid sound.")
            return minqlx.RET_STOP_ALL

        # Play to all other players who haven't disabled sound
        players = self.players()
        players.remove(player)
        for p in players:
            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                self.play_sound(msg[1], p)

        return minqlx.RET_STOP_ALL

    def cmd_music(self, player, msg, channel):
        """Plays music, but only for those with music volume on and the sounds flag on."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        if not self.db.get_flag(player, "essentials:sounds_enabled", default=True):
            player.tell("Sounds are disabled. Use ^6{}sounds^7 to enable them again."
                .format(self.get_cvar("qlx_commandPrefix")))
            return minqlx.RET_STOP_ALL

        # Play locally to validate.
        if not self.play_music(msg[1], player):
            player.tell("Invalid sound.")
            return minqlx.RET_STOP_ALL

        # Play to all other players who haven't disabled sounds.
        players = self.players()
        players.remove(player)
        for p in players:
            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                self.play_music(msg[1], p)

        return minqlx.RET_STOP_ALL

    def cmd_stopsound(self, player, msg, channel):
        """Stops all sounds playing. Useful if someone plays one of those really long ones."""
        if not self.db.get_flag(player, "essentials:sounds_enabled", default=True):
            player.tell("Sounds are disabled. Use ^6{}sounds^7 to enable them again."
                .format(self.get_cvar("qlx_commandPrefix")))
            return minqlx.RET_STOP_ALL

        self.stop_sound()

    def cmd_stopmusic(self, player, msg, channel):
        """Stops any music playing."""
        if not self.db.get_flag(player, "essentials:sounds_enabled", default=True):
            player.tell("Sounds are disabled. Use ^6{}sounds^7 to enable them again."
                .format(self.get_cvar("qlx_commandPrefix")))
            return minqlx.RET_STOP_ALL

        self.stop_music()

    def cmd_kick(self, player, msg, channel):
        """Kicks a player. A reason can also be provided."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return
        
        if len(msg) > 2:
            target_player.kick(" ".join(msg[2:]))
        else:
            target_player.kick()

    def cmd_kickban(self, player, msg, channel):
        """Kicks a player and prevent the player from joining for the remainder of the map."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        target_player.tempban()

    def cmd_yes(self, player, msg, channel):
        """Passes the current vote."""
        if self.is_vote_active():
            self.force_vote(True)
        else:
            channel.reply("There is no active vote!")

    def cmd_no(self, player, msg, channel):
        """Vetoes the current vote."""
        if self.is_vote_active():
            self.force_vote(False)
        else:
            channel.reply("There is no active vote!")

    def cmd_random(self, player, msg, channel):
        """Presents a random number in chat."""
        if len(msg) < 2:
            return minqlx.RET_USAGE
        
        try:
            n = randint(1,int(msg[1]))
        except ValueError:
            player.tell("Invalid upper limit. Use a positive integer.")
            return minqlx.RET_STOP_ALL
        
        channel.reply("^3Random number is: ^5{}".format(n))
        
    def cmd_cointoss(self, player, msg, channel):
        """Tosses a coin, and returns HEADS or TAILS in chat."""
        n = randint(0,1)
        channel.reply("^3The coin is: ^5{}".format("HEADS" if n else "TAILS"))
        
    def cmd_switch(self, player, msg, channel):
        """Switches the teams of the two players."""
        if len(msg) < 3:
            return minqlx.RET_USAGE

        try:
            i1 = int(msg[1])
            player1 = self.player(i1)
            if not (0 <= i1 < 64) or not player1:
                raise ValueError
        except ValueError:
            channel.reply("The first ID is invalid.")
            return

        try:
            i2 = int(msg[2])
            player2 = self.player(i2)
            if not (0 <= i2 < 64) or not player2:
                raise ValueError
        except ValueError:
            channel.reply("The second ID is invalid.")
            return

        self.switch(player1, player2)
            
    def cmd_red(self, player, msg, channel):
        """Moves a player to the red team."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        target_player.put("red")

    def cmd_blue(self, player, msg, channel):
        """Moves a player to the blue team."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        target_player.put("blue")


    def cmd_spectate(self, player, msg, channel):
        """Moves a player to the spectator team."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        target_player.put("spectator")

    def cmd_free(self, player, msg, channel):
        """Moves a player to the free team."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        target_player.put("free")

    def cmd_addmod(self, player, msg, channel):
        """Give a player mod status."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        target_player.addmod()

    def cmd_addadmin(self, player, msg, channel):
        """Give a player admin status."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        target_player.addadmin()

    def cmd_demote(self, player, msg, channel):
        """Remove admin status from someone."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        target_player.demote()

    def cmd_mute(self, player, msg, channel):
        """Mute a player."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        if target_player == player:
            channel.reply("I refuse.")
        else:
            target_player.mute()

    def cmd_unmute(self, player, msg, channel):
        """Mute a player."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        target_player.unmute()

    def cmd_lock(self, player, msg, channel):
        """Lock a team."""
        if len(msg) > 1:
            if msg[1][0].lower() == "s":
                self.lock("spectator")
            elif msg[1][0].lower() == "r":
                self.lock("red")
            elif msg[1][0].lower() == "b":
                self.lock("blue")
            else:
                player.tell("Invalid team.")
                return minqlx.RET_STOP_ALL
        else:
            self.lock()

    def cmd_unlock(self, player, msg, channel):
        """Unlock a team."""
        if len(msg) > 1:
            if msg[1][0].lower() == "s":
                self.unlock("spectator")
            elif msg[1][0].lower() == "r":
                self.unlock("red")
            elif msg[1][0].lower() == "b":
                self.unlock("blue")
            else:
                player.tell("Invalid team.")
                return minqlx.RET_STOP_ALL
        else:
            self.unlock()
    
    def cmd_allready(self, player, msg, channel):
        """Forces all players to ready up."""
        if self.game.state == "warmup":
            self.allready()
        else:
            channel.reply("But the game's already in progress, you silly goose!")
        
    def cmd_abort(self, player, msg, channel):
        """Forces a game in progress to go back to warmup."""
        if self.game.state != "warmup":
            self.abort()
        else:
            channel.reply("But the game isn't even on, you doofus!")
    
    def cmd_map(self, player, msg, channel):
        """Changes the map."""
        if len(msg) < 2:
            return minqlx.RET_USAGE
        
        # TODO: Give feedback on !map.
        self.change_map(msg[1], msg[2] if len(msg) > 2 else None)
        
    def cmd_help(self, player, msg, channel):
        # TODO: Perhaps print some essential commands in !help
        player.tell("minqlx: ^6{}^7 - Plugins: ^6{}".format(minqlx.__version__, minqlx.__plugins_version__))
        player.tell("See ^6github.com/MinoMino/minqlx^7 for more info about the mod and its commands.")
        return minqlx.RET_STOP_ALL
    
    def cmd_db(self, player, msg, channel):
        """Prints the value of a key in the database."""
        if len(msg) < 2:
            return minqlx.RET_USAGE
        
        try:
            if msg[1] not in self.db:
                channel.reply("The key is not present in the database.")
            else:
                t = self.db.type(msg[1])
                if t == "string":
                    out = self.db[msg[1]]
                elif t == "list":
                    out = str(self.db.lrange(msg[1], 0, -1))
                elif t == "set":
                    out = str(self.db.smembers(msg[1]))
                elif t == "zset":
                    out = str(self.db.zrange(msg[1], 0, -1, withscores=True))
                else:
                    out = str(self.db.hgetall(msg[1]))
                
                channel.reply(out)
        except Exception as e:
            channel.reply("^1{}^7: {}".format(e.__class__.__name__, e))
            raise

    def cmd_seen(self, player, msg, channel):
        """Responds with the last time a player was seen on the server."""
        if len(msg) < 2:
            return minqlx.RET_USAGE
        # TODO: Save a couple of nicknames in DB and have !seen work with nicks too?

        try:
            steam_id = int(msg[1])
            if steam_id < 64:
                channel.reply("Invalid SteamID64.")
                return
        except ValueError:
            channel.reply("Unintelligible SteamID64.")
            return
        
        p = self.player(steam_id)
        if p:
            channel.reply("That would be {}^7, who is currently on this very server!".format(p))
            return
        
        key = "minqlx:players:{}:last_seen".format(steam_id)
        name = "that player" if steam_id != minqlx.owner() else "my ^6master^7"
        if key in self.db:
            then = datetime.datetime.strptime(self.db[key], DATETIME_FORMAT)
            td = datetime.datetime.now() - then
            r = re.match(r'((?P<d>.*) days*, )?(?P<h>..?):(?P<m>..?):.+', str(td))
            if r.group("d"):
                channel.reply("^7I saw {} ^6{}^7 day(s), ^6{}^7 hour(s) and ^6{}^7 minute(s) ago."
                    .format(name, r.group("d"), r.group("h"), r.group("m")))
            else:
                channel.reply("^7I saw {} ^6{}^7 hour(s) and ^6{}^7 minute(s) ago."
                    .format(name, r.group("h"), r.group("m")))
        else:
            channel.reply("^7I have never seen {} before.".format(name))

    def cmd_time(self, player, msg, channel):
        """Responds with the current time."""
        tz_offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        tz_offset = tz_offset // 60 // 60 * -1
        if len(msg) > 1:
            try:
                tz_offset = int(msg[1])
            except ValueError:
                channel.reply("Unintelligible time zone offset.")
                return
        tz = datetime.timezone(offset=datetime.timedelta(hours=tz_offset))
        now = datetime.datetime.now(tz)
        if tz_offset > 0:
            channel.reply("The current time is: ^6{} UTC+{}"
                .format(now.strftime(TIME_FORMAT), tz_offset))
        elif tz_offset < 0:
            channel.reply("The current time is: ^6{} UTC{}"
                .format(now.strftime(TIME_FORMAT), tz_offset))
        else:
            channel.reply("The current time is: ^6{} UTC"
                .format(now.strftime(TIME_FORMAT)))

    def cmd_teamsize(self, player, msg, channel):
        """Calls a teamsize vote and passes it immediately."""
        if len(msg) < 2:
            return minqlx.RET_USAGE
        
        try:
            n = int(msg[1])
        except ValueError:
            channel.reply("^7Unintelligible size.")
            return
        
        self.game.teamsize = n
        self.msg("The teamsize has been set to ^6{}^7 by {}.".format(n, player))
        return minqlx.RET_STOP_ALL

    def cmd_rcon(self, player, msg, channel):
        """Sends an rcon command to the server."""
        if len(msg) < 2:
            return minqlx.RET_USAGE
        
        with minqlx.redirect_print(channel):
            minqlx.console_command(" ".join(msg[1:]))

    def cmd_mappool(self, player, msg, channel):
        if not self.mappool or not self.get_cvar("qlx_enforceMappool", bool):
            player.tell("No map pool is being enforced. You are free to vote any map.")
        else:
            self.tell_mappool(player)

        return minqlx.RET_STOP_ALL


    # ====================================================================
    #                               HELPERS
    # ====================================================================

    def update_player(self, player):
        """Updates the list of recent names and IPs used by the player,
        and adds entries to the player list and IP entries.

        """
        base_key = "minqlx:players:" + str(player.steam_id)
        db = self.db.pipeline()
        
        # Add to IP set and make IP entry.
        if player.ip:
            db.sadd("minqlx:ips", player.ip)
            db.sadd("minqlx:ips:" + player.ip, player.steam_id)
            db.sadd(base_key + ":ips", player.ip)
        
        # Make or update player entry.
        if base_key not in self.db:
            db.lpush(base_key, player.name)
            db.sadd("minqlx:players", player.steam_id)
        else:
            names = [self.clean_text(n) for n in self.db.lrange(base_key, 0, -1)]
            if player.clean_name not in names:
                db.lpush(base_key, player.name)
                db.ltrim(base_key, 0, 19)
        
        db.execute()

    def update_seen_player(self, player):
        key = "minqlx:players:" + str(player.steam_id) + ":last_seen"
        self.db[key] = datetime.datetime.now().strftime(DATETIME_FORMAT)
        
    @minqlx.delay(29)
    def force(self, require, vote_id):
        if self.last_vote != vote_id:
            # This is not the vote we should be resolving.
            return

        votes = self.current_vote_count()
        if self.is_vote_active() and votes and votes[0] > votes[1]:
            if require:
                teams = self.teams()
                players = teams["red"] + teams["blue"] + teams["free"]
                if sum(votes)/len(players) < require:
                    return
            minqlx.force_vote(True)
    
    def parse_mappool(self, path):
        """Read and parse the map pool file into a dictionary.
    
        Structure as follows:
        {'campgrounds': ['ca', 'ffa'], 'overkill': ['ca']}
        
        """
        mappool = {}
        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except:
            minqlx.log_exception()
            return None
        
        for line in lines:
            li = line.lstrip()
            # Ignore commented lines.
            if not li.startswith("#") and "|" in li:
                key, value = line.split('|', 1)
                # Maps are case-insensitive, but not factories.
                key = key.lower()

                if key in mappool:
                    mappool[key].append(value.strip())
                else:
                    mappool[key] = [value.strip()]
        
        return mappool

    def tell_mappool(self, player, indent=0):
        out = ""
        for m in self.mappool:
            out += ("{0}Map: {1:25} Factories: {2}\n"
                .format(" " * indent, m, ", ".join(val for val in self.mappool[m])))
        player.tell(out.rstrip("\n"))

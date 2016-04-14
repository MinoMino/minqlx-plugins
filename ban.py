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

import minqlx
import datetime
import time
import re

LENGTH_REGEX = re.compile(r"(?P<number>[0-9]+) (?P<scale>seconds?|minutes?|hours?|days?|weeks?|months?|years?)")
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
PLAYER_KEY = "minqlx:players:{}"

class ban(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_HIGH)
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("game_countdown", self.handle_game_countdown)
        self.add_hook("game_start", self.handle_game_start)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_command("ban", self.cmd_ban, 2, usage="<id> <length> seconds|minutes|hours|days|... [reason]")
        self.add_command("unban", self.cmd_unban, 2, usage="<id>")
        self.add_command("checkban", self.cmd_checkban, usage="<id>")
        self.add_command("forgive", self.cmd_forgive, 2, usage="<id> [leaves_to_forgive]")

        # Cvars.
        self.set_cvar_once("qlx_leaverBan", "0")
        self.set_cvar_limit_once("qlx_leaverBanThreshold", "0.63", "0", "1")
        self.set_cvar_limit_once("qlx_leaverBanWarnThreshold", "0.78", "0", "1")
        self.set_cvar_once("qlx_leaverBanMinimumGames", "15")

        # List of players playing that could potentially be considered leavers.
        self.players_start = []
        self.pending_warnings = {}
    
    def handle_player_connect(self, player):
        status = self.leave_status(player.steam_id)
        # Check if a player has been banned for leaving, if we're doing that.
        if status and status[0] == "ban":
            return "You have been banned from this server for leaving too many games."
        # Check if player needs to be warned.
        elif status and status[0] == "warn":
            self.pending_warnings[player.steam_id] = status[1]
        
        # Check if a player has been banned manually.
        banned = self.is_banned(player.steam_id)
        if banned:
            expires, reason = banned
            if reason:
                return "You are banned until {}: {}".format(expires, reason)
            else:
                return "You are banned until {}.".format(expires)

    @minqlx.delay(4)
    def handle_player_loaded(self, player):
        # Update first, since player might be gone in those 4 seconds.
        if player.steam_id in self.pending_warnings:
            try:
                player.update()
            except minqlx.NonexistentPlayerError:
                return

            self.warn_player(player, self.pending_warnings[player.steam_id])

    def handle_player_disconnect(self, player, reason):
        # Allow people to disconnect without getting a leave if teams are uneven.
        teams = self.teams()
        if len(teams["red"] + teams["blue"]) % 2 != 0 and player in self.players_start:
            self.players_start.remove(player)

    def handle_game_countdown(self):
        if self.get_cvar("qlx_leaverBan", bool):
            self.msg("Leavers are being kept track of. Repeat offenders ^6will^7 be banned.")

    # Needs a delay here because players will sometimes have their teams reset during the event.
    # TODO: Proper fix to self.teams() in game_start.
    @minqlx.delay(1)
    def handle_game_start(self, game):
        teams = self.teams()
        self.players_start = teams["red"] + teams["blue"]

    def handle_game_end(self, data):
        if data["ABORTED"]:
            self.players_start = []
            return

        teams = self.teams()
        players_end = teams["red"] + teams["blue"]
        leavers = []

        for player in self.players_start.copy():
            if player not in players_end:
                # Populate player list.
                leavers.append(player)
                # Remove leavers from initial list so we can use it to award games completed.
                self.players_start.remove(player)

        db = self.db.pipeline()
        for player in self.players_start:
            db.incr(PLAYER_KEY.format(player.steam_id) + ":games_completed")
        for player in leavers:
            db.incr(PLAYER_KEY.format(player.steam_id) + ":games_left")
        db.execute()

        if leavers:
            self.msg("^7Leavers: ^6{}".format(" ".join([p.clean_name for p in leavers])))
            self.players_start = []

    def handle_team_switch(self, player, old_team, new_team):
        # Allow people to spectate without getting a leave if teams are uneven.
        if (old_team == "red" or old_team == "blue") and new_team == "spectator":
            teams = self.teams()
            if len(teams["red"] + teams["blue"]) % 2 == 0 and player in self.players_start:
                self.players_start.remove(player)
        # Add people to the list of participating players if they join mid-game.
        if (old_team == "spectator" and (new_team == "red" or new_team == "blue") and
         self.game.state == "in_progress" and player not in self.players_start):
            self.players_start.append(player)

    def cmd_ban(self, player, msg, channel):
        """Bans a player temporarily. A very long period works for all intents and
        purposes as a permanent ban, so there's no separate command for that.

        Example #1: !ban Mino 1 day Very rude!

        Example #2: !ban sponge 50 years"""
        if len(msg) < 4:
            return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return
        
        if target_player:
            name = target_player.name
        else:
            name = ident

        # Permission level 5 players not bannable.
        if self.db.has_permission(ident, 5):
            channel.reply("^6{}^7 has permission level 5 and cannot be banned.".format(name))
            return

        if len(msg) > 4:
            reason = " ".join(msg[4:])
        else:
            reason = ""
        
        r = LENGTH_REGEX.match(" ".join(msg[2:4]).lower())
        if r:
            number = float(r.group("number"))
            if number <= 0: return
            scale = r.group("scale").rstrip("s")
            td = None
            
            if scale == "second":
                td = datetime.timedelta(seconds=number)
            elif scale == "minute":
                td = datetime.timedelta(minutes=number)
            elif scale == "hour":
                td = datetime.timedelta(hours=number)
            elif scale == "day":
                td = datetime.timedelta(days=number)
            elif scale == "week":
                td = datetime.timedelta(weeks=number)
            elif scale == "month":
                td = datetime.timedelta(days=number * 30)
            elif scale == "year":
                td = datetime.timedelta(weeks=number * 52)
            
            now = datetime.datetime.now().strftime(TIME_FORMAT)
            expires = (datetime.datetime.now() + td).strftime(TIME_FORMAT)
            base_key = PLAYER_KEY.format(ident) + ":bans"
            ban_id = self.db.zcard(base_key)
            db = self.db.pipeline()
            db.zadd(base_key, time.time() + td.total_seconds(), ban_id)
            ban = {"expires": expires, "reason": reason, "issued": now, "issued_by": player.steam_id}
            db.hmset(base_key + ":{}".format(ban_id), ban)
            db.execute()
            
            try:
                self.kick(ident, "has been banned until ^6{}^7: {}".format(expires, reason))
            except ValueError:
                channel.reply("^6{} ^7has been banned. Ban expires on ^6{}^7.".format(name, expires))

    def cmd_unban(self, player, msg, channel):
        """Unbans a player if banned."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return
        
        if target_player:
            name = target_player.name
        else:
            name = ident

        base_key = PLAYER_KEY.format(ident) + ":bans"
        bans = self.db.zrangebyscore(base_key, time.time(), "+inf", withscores=True)
        if not bans:
            channel.reply("^7 No active bans on ^6{}^7 found.".format(name))
        else:
            db = self.db.pipeline()
            for ban_id, score in bans:
                db.zincrby(base_key, ban_id, -score)
            db.execute()
            channel.reply("^6{}^7 has been unbanned.".format(name))

    def cmd_checkban(self, player, msg, channel):
        """Checks whether a player has been banned, and if so, why."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return
        
        if target_player:
            name = target_player.name
        else:
            name = ident

        # Check manual bans first.
        res = self.is_banned(ident)
        if res:
            expires, reason = res
            if reason:
                channel.reply("^6{}^7 is banned until ^6{}^7 for the following reason:^6 {}".format(name, *res))
            else:
                channel.reply("^6{}^7 is banned until ^6{}^7.".format(name, expires))
            return
        elif self.get_cvar("qlx_leaverBan", bool):
            status = self.leave_status(ident)
            if status and status[0] == "ban":
                channel.reply("^6{} ^7is banned for having left too many games.".format(name))
                return
        
        channel.reply("^6{} ^7is not banned.".format(name))

    def cmd_forgive(self, player, msg, channel):
        """Removes a leave from a player. Optional integer can be provided to remove multiple leaves."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return
        
        if target_player:
            name = target_player.name
        else:
            name = ident

        base_key = PLAYER_KEY.format(ident)
        if base_key not in self.db:
            channel.reply("I do not know ^6{}^7.".format(name))
            return
        
        try:
            leaves = int(self.db[base_key + ":games_left"])
        except KeyError:
            leaves = 0
        
        if leaves <= 0:
            channel.reply("^6{}^7's leaves are already at ^6{}^7.".format(name, leaves))
            return

        if len(msg) == 2:
            leaves_to_forgive = 1
        else:
            try:
                leaves_to_forgive = int(msg[2])
            except ValueError:
                channel.reply("Unintelligible number of leaves to forgive. Please use numbers.")
                return

        new_leaves = leaves - leaves_to_forgive
        if new_leaves <= 0:
            self.db[base_key + ":games_left"] = 0
            channel.reply("^6{}^7's leaves have been reduced to ^60^7.".format(name))
        else:
            self.db[base_key + ":games_left"] = new_leaves
            channel.reply("^6{}^7 games have been forgiven, putting ^6{}^7 at ^6{}^7 leaves."
                .format(leaves_to_forgive, name, new_leaves))


    # ====================================================================
    #                               HELPERS
    # ====================================================================

    def is_banned(self, steam_id):
        base_key = PLAYER_KEY.format(steam_id) + ":bans"
        bans = self.db.zrangebyscore(base_key, time.time(), "+inf", withscores=True)
        if not bans:
            return None

        longest_ban = self.db.hgetall(base_key + ":{}".format(bans[-1][0]))
        expires = datetime.datetime.strptime(longest_ban["expires"], TIME_FORMAT)
        if (expires - datetime.datetime.now()).total_seconds() > 0:
            return expires, longest_ban["reason"]
        
        return None

    def leave_status(self, steam_id):
        """Get a player's status when it comes to leaving, given automatic leaver ban is on.

        """
        if not self.get_cvar("qlx_leaverBan", bool):
            return None

        try:
            completed = self.db[PLAYER_KEY.format(steam_id) + ":games_completed"]
            left = self.db[PLAYER_KEY.format(steam_id) + ":games_left"]
        except KeyError:
            return None
        
        completed = int(completed)
        left = int(left)

        min_games_completed = self.get_cvar("qlx_leaverBanMinimumGames", int)
        warn_threshold = self.get_cvar("qlx_leaverBanWarnThreshold", float)
        ban_threshold = self.get_cvar("qlx_leaverBanThreshold", float)

        # Check their games completed to total games ratio.
        total = completed + left
        if not total:
            return None
        elif total < min_games_completed:
            # If they have played less than the minimum, check if they can possibly recover by the time
            # they have played the minimum amount of games.
            ratio = (completed + (min_games_completed - total)) / min_games_completed
        else:
            ratio = completed / total
            
        if ratio <= warn_threshold and (ratio > ban_threshold or total < min_games_completed):
            action = "warn"
        elif ratio <= ban_threshold and total >= min_games_completed:
            action = "ban"
        else:
            action = None

        return action, completed / total

    def warn_player(self, player, ratio):
        player.tell("^7You have only completed ^6{}^7 percent of your games.".format(round(ratio * 100, 1)))
        player.tell("^7If you keep leaving you ^6will^7 be banned.")

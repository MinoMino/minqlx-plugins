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

class silence(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("client_command", self.handle_client_command, priority=minqlx.PRI_HIGH)
        self.add_hook("userinfo", self.handle_userinfo, priority=minqlx.PRI_HIGH)
        self.add_command("silence", self.cmd_silence, 2, usage="<id> <length> seconds|minutes|hours|days|... [reason]")
        self.add_command("unsilence", self.cmd_unsilence, 2, usage="<id>")
        self.add_command("checksilence", self.cmd_checksilence, usage="<id>")

        self.silenced = {}
    
    def handle_player_loaded(self, player):
        silenced = self.is_silenced(player.steam_id)
        if not silenced:
            return

        expires, score, reason = silenced
        self.silenced[player.steam_id] = (expires, score, reason)
        player.mute()
        if reason:
            player.tell("You are muted on this server until ^6{}^7: {}".format(expires, reason))
        else:
            player.tell("You are muted on this server until ^6{}^7.".format(expires))

    def handle_player_disconnect(self, player, reason):
        if player.steam_id in self.silenced:
            del self.silenced[player.steam_id]

    def handle_client_command(self, player, cmd):
        if player.steam_id not in self.silenced:
            return
        
        if (cmd.lower().startswith("say ") or cmd.lower().startswith("say_team ")):
            expires, score, reason = self.silenced[player.steam_id]
            if time.time() < score:
                if reason:
                    player.tell("You are muted on this server until ^6{}^7: {}".format(expires, reason))
                else:
                    player.tell("You are muted on this server until ^6{}^7.".format(expires))
            else:
                del self.silenced[player.steam_id]
                player.unmute()
                
                @minqlx.next_frame
                def repeat_command():
                    minqlx.client_command(player.id, cmd)
                repeat_command()

            return minqlx.RET_STOP_ALL

    def handle_userinfo(self, player, changed):
        if player.steam_id not in self.silenced:
            return
        elif "name" in changed:
            changed["name"] = player.name.rstrip("^7")
            return changed

    def cmd_silence(self, player, msg, channel):
        """Mutes a player temporarily. A very long period works for all intents and
        purposes as a permanent mute, so there's no separate command for that.

        Example #1: !silence Mino 1 day Very rude!

        Example #2: !silence sponge 50 years"""
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

        if self.db.has_permission(ident, 2):
            channel.reply("^6{}^7 has permission level 2 or more and cannot be silenced.".format(name))
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
            base_key = PLAYER_KEY.format(ident) + ":silences"
            silence_id = self.db.zcard(base_key)
            score = time.time() + td.total_seconds()
            db = self.db.pipeline()
            db.zadd(base_key, score, silence_id)
            silence = {"expires": expires, "reason": reason, "issued": now, "issued_by": player.steam_id}
            db.hmset(base_key + ":{}".format(silence_id), silence)
            db.execute()

            if target_player:
                self.silenced[ident] = (expires, score, reason)
                try:
                    target_player.mute()
                except ValueError:
                    pass
            channel.reply("^6{} ^7has been silenced. Silence expires on ^6{}^7.".format(name, expires))

    def cmd_unsilence(self, player, msg, channel):
        """Unsilences a player if silenced."""
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                if not target_player:
                    raise ValueError
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

        base_key = PLAYER_KEY.format(ident) + ":silences"
        silences = self.db.zrangebyscore(base_key, time.time(), "+inf", withscores=True)
        if not silences:
            channel.reply("^7 No active silences on ^6{}^7 found.".format(name))
        else:
            db = self.db.pipeline()
            for silence_id, score in silences:
                db.zincrby(base_key, silence_id, -score)
            db.execute()
            if ident in self.silenced:
                del self.silenced[ident]
            if target_player:
                target_player.unmute()
            channel.reply("^6{}^7 has been unsilenced.".format(name))

    def cmd_checksilence(self, player, msg, channel):
        """Checks whether a player has been silenced, and if so, why."""
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

        # Check manual silences first.
        res = self.is_silenced(ident)
        if res:
            expires, score, reason = res
            if reason:
                channel.reply("^6{}^7 is silenced until ^6{}^7 for the following reason:^6 {}".format(name, expires, reason))
            else:
                channel.reply("^6{}^7 is silenced until ^6{}^7.".format(name, expires))
            return
        
        channel.reply("^6{} ^7is not silenced.".format(name))

    # ====================================================================
    #                               HELPERS
    # ====================================================================

    def is_silenced(self, steam_id):
        base_key = PLAYER_KEY.format(steam_id) + ":silences"
        silences = self.db.zrangebyscore(base_key, time.time(), "+inf", withscores=True)
        if not silences:
            return None

        silence_id, score = silences[-1]
        longest_silence = self.db.hgetall(base_key + ":{}".format(silence_id))
        expires = datetime.datetime.strptime(longest_silence["expires"], TIME_FORMAT)
        if (expires - datetime.datetime.now()).total_seconds() > 0:
            return expires, score, longest_silence["reason"]
        
        return None

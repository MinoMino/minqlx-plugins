# warn.py by x0rnn, a plugin to warn players for misbehaving. A warning is removed after X days (qlx_warnDays), unless the player has been warned X times (qlx_maxStrikes), then he is perma-banned.
# When a warned player joins a server, everyone is notified about him and the reason he was warned.
# !warn <id> <reason>
# !unwarn <id> <warnings to remove>
# !warned (to list all warned players)

import minqlx
import time
import datetime

PLAYER_KEY = "minqlx:players:{}"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class warn(minqlx.Plugin):
    
    def __init__(self):
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_HIGH)
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_command("warn", self.cmd_warn, 4, usage="<id> <reason>")
        self.add_command("unwarn", self.cmd_unwarn, 5, usage="<id> <warnings to remove>")
        self.add_command("warned", self.cmd_warned, 4)

        self.set_cvar_once("qlx_warnDays", "7") #how many days until the warning goes away (each additional warn adds this many days to the previous expiration date)
        self.set_cvar_once("qlx_maxStrikes", "3") #how many strikes before getting banned

    def handle_player_connect(self, player):
        warned = self.is_warned(player.steam_id)
        if warned:
            strike, reason, expires = warned
            if strike >= self.get_cvar("qlx_maxStrikes", int):
                return "You are banned for repeated violations: {}: warned {} times.".format(reason, strike)

    def handle_player_loaded(self, player):
        warned = self.is_warned(player.steam_id)
        if warned:
            strike, reason, expires = warned
            self.msg("^1Attention^7! {} connected. Warned for: ^6{}^7, strike: ^6{}^7/^6{}^7, expires: ^6{}^7.".format(player.name, reason, strike, self.get_cvar("qlx_maxStrikes", int), expires))

    def cmd_warn(self, player, msg, channel):
        if len(msg) < 3:
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

        if self.db.has_permission(ident, 5):
            channel.reply("^6{}^7 has permission level 5 and cannot be warned.".format(name))
            return

        try:
            strike = int(self.db[PLAYER_KEY.format(ident) + ":warnings:strikes"])
        except KeyError:
            strike = 0

        reason = " ".join(msg[2:])
        td = datetime.timedelta(days=self.get_cvar("qlx_warnDays", int))

        try:
            previous_warn = self.db.zrangebyscore(PLAYER_KEY.format(ident) + ":warnings", time.time(), "+inf", withscores=True)
        except ValueError:
            previous_warn = 0

        if previous_warn:
            longest_warn = self.db.hgetall(PLAYER_KEY.format(ident) + ":warnings" + ":{}".format(previous_warn[-1][0]))
            previous_expire = datetime.datetime.strptime(longest_warn["expires"], TIME_FORMAT)
            expires = (previous_expire + td).strftime(TIME_FORMAT)
        else:
            expires = (datetime.datetime.now() + td).strftime(TIME_FORMAT)

        now = datetime.datetime.now().strftime(TIME_FORMAT)
        base_key = PLAYER_KEY.format(ident) + ":warnings"
        warn_id = self.db.zcard(base_key)
        db = self.db.pipeline()
        db.zadd(base_key, time.time() + td.total_seconds(), warn_id)
        db.incr(PLAYER_KEY.format(ident) + ":warnings:strikes")
        warn = {"expires": expires, "reason": reason, "issued": now, "issued_by": player.steam_id}
        db.hmset(base_key + ":{}".format(warn_id), warn)
        db.execute()
        if strike + 1 < self.get_cvar("qlx_maxStrikes", int):
            self.msg("{} has been warned for: ^6{}^7, strike: ^6{}^7/^6{}^7, expires: ^6{}^7.".format(name, reason, strike + 1, self.get_cvar("qlx_maxStrikes", int), expires))
        elif strike + 1 >= self.get_cvar("qlx_maxStrikes", int):
            try:
                self.kick(ident, "Banned for repeated violations: {}: warned {} times.".format(reason, strike + 1))
            except ValueError:
                self.msg("^6{} ^7has been banned for repeated violations: ^6{}^7: warned ^6{} ^7times.".format(name, strike + 1))

    def cmd_unwarn(self, player, msg, channel):
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
            strikes = int(self.db[base_key + ":warnings:strikes"])
        except KeyError:
            strikes = 0
        
        if strikes <= 0:
            channel.reply("^6{}^7's warnings are already at ^6{}^7.".format(name, strikes))
            return

        if len(msg) == 2:
            strikes_to_forgive = 1
        else:
            try:
                strikes_to_forgive = int(msg[2])
            except ValueError:
                channel.reply("Unintelligible number of warnings to forgive. Please use numbers.")
                return

        new_strikes = strikes - strikes_to_forgive
        if new_strikes <= 0:
            self.db[base_key + ":warnings:strikes"] = 0
            channel.reply("^6{}^7's warnings have been reduced to ^60^7.".format(name))
        else:
            self.db[base_key + ":warnings:strikes"] = new_strikes
            channel.reply("^6{}^7 warnings have been forgiven, putting ^6{}^7 at ^6{}^7 warnings."
                .format(strikes_to_forgive, name, new_strikes))

    def cmd_warned(self, player, msg, channel):
        playerlist = self.db.keys("minqlx:players:*:warnings:strikes")
        tmp = ""
        tmp2 = ""

        for sublist in playerlist:
            tmp = str(sublist).split(":")
            tmp2 += str(tmp[2]) + ","
        tmp2.split(",")
        tmp2 = tmp2[:-1]
        
        i = 0
        player.tell("^2Warned players:\n")
        for steamids in playerlist:
            steamids = tmp2.split(",")
            id_name = self.db.lindex(PLAYER_KEY.format(steamids[i]), 0)
            active = self.db.zrangebyscore(PLAYER_KEY.format(steamids[i]) + ":warnings", time.time(), "+inf", withscores=True)
            if active:
                strike = int(self.db[PLAYER_KEY.format(steamids[i]) + ":warnings:strikes"])
                if strike:
                    longest_warn = self.db.hgetall(PLAYER_KEY.format(steamids[i]) + ":warnings" + ":{}".format(active[-1][0]))
                    reason = longest_warn["reason"]
                    expires = longest_warn["expires"]
                    if strike >= self.get_cvar("qlx_maxStrikes", int):
                        player.tell("^1Banned^7: {} ^7({}): ^6{}^7,^6 {}^7/^6{}^7.".format(id_name, steamids[i], reason, strike, self.get_cvar("qlx_maxStrikes", int)))
                    else:
                        player.tell("{} ^7({}): ^6{}^7,^6 {}^7/^6{}^7, expires: ^6{}^7.".format(id_name, steamids[i], reason, strike, self.get_cvar("qlx_maxStrikes", int), expires))
            i += 1

    def is_warned(self, steam_id):
        try:
            strike = int(self.db[PLAYER_KEY.format(steam_id) + ":warnings:strikes"])
        except KeyError:
            strike = 0

        if strike > 0:
            warn = self.db.zrangebyscore(PLAYER_KEY.format(steam_id) + ":warnings", time.time(), "+inf", withscores=True)
            if not warn and strike < self.get_cvar("qlx_maxStrikes", int):
                self.db.incrby(PLAYER_KEY.format(steam_id) + ":warnings:strikes", -strike)
                return None
            elif not warn and strike >= self.get_cvar("qlx_maxStrikes", int):
                previous_warn = self.db.zrangebyscore(PLAYER_KEY.format(steam_id) + ":warnings", "-inf", "+inf", withscores=True)
                expires = datetime.datetime.strptime(previous_warn["expires"], TIME_FORMAT)
                longest_warn = self.db.hgetall(PLAYER_KEY.format(steam_id) + ":warnings" + ":{}".format(previous_warn[-1][0]))
                return strike, longest_warn["reason"], expires
            elif warn:
                longest_warn = self.db.hgetall(PLAYER_KEY.format(steam_id) + ":warnings" + ":{}".format(warn[-1][0]))
                expires = datetime.datetime.strptime(longest_warn["expires"], TIME_FORMAT)
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    return strike, longest_warn["reason"], expires

        return None

# This is a plugin created by iouonegirl(@gmail.com)
# Copyright (c) 2016 iouonegirl + Minkyn
# https://github.com/dsverdlo/minqlx-plugins
#
# You are free to modify this plugin to your custom,
# except for the version command related code.
#
# Its purpose is to display some information about the players.
# When players fall off the scoreboard, they are now also able
# to view their information
#
# Players deactivated on qlstats can be banned or just
# trigger a server warning
#
# Uses:
# - set qlx_pinfo_display_auto "0"
# - set qlx_pinfo_show_deactivated "1"
#          ^ (If this is 1 then a warning will be shown of players who are deactivated on qlstats)
# - set qlx_pinfo_ban_deactivated "0"
# - set qlx_pinfo_ban_duration_weeks "1"
#       ^ If ban_deactivated is "1", then this var will specify for how many weeks the ban will last
#         (please only use integers (no decimals) here)

import minqlx
import requests
import itertools
import threading
import datetime
import random
import time
import os
import re

# This code makes sure the required superclass is loaded automatically
try:
    from .iouonegirl import iouonegirlPlugin
except:
    try:
        abs_file_path = os.path.join(os.path.dirname(__file__), "iouonegirl.py")
        res = requests.get("https://raw.githubusercontent.com/dsverdlo/minqlx-plugins/master/iouonegirl.py")
        if res.status_code != requests.codes.ok: raise
        with open(abs_file_path,"a+") as f: f.write(res.text)
        from .iouonegirl import iouonegirlPlugin
    except Exception as e :
        minqlx.CHAT_CHANNEL.reply("^1iouonegirl abstract plugin download failed^7: {}".format(e))
        raise

VERSION = "v0.34"

PLAYER_KEY = "minqlx:players:{}"
COMPLETED_KEY = PLAYER_KEY + ":games_completed"
LEFT_KEY = PLAYER_KEY + ":games_left"
LENGTH_REGEX = re.compile(r"(?P<number>[0-9]+) (?P<scale>seconds?|minutes?|hours?|days?|weeks?|months?|years?)")
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Elo retrieval vars
EXT_SUPPORTED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "duel", "ffa")
RATING_KEY = "minqlx:players:{0}:ratings:{1}" # 0 == steam_id, 1 == short gametype.
MAX_ATTEMPTS = 3
CACHE_EXPIRE = 60*30 # 30 minutes TTL.
DEFAULT_RATING = 1500
SUPPORTED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm")


class player_info(iouonegirlPlugin):
    def __init__(self):
        super().__init__(self.__class__.__name__, VERSION)

        # set cvars once. EDIT THESE IN SERVER.CFG
        self.set_cvar_once("qlx_balanceApi", "elo")
        self.set_cvar_once("qlx_pinfo_display_auto", "0")
        self.set_cvar_once("qlx_pinfo_show_deactivated", "1")
        self.set_cvar_once("qlx_pinfo_ban_deactivated", "0")
        self.set_cvar_once("qlx_pinfo_ban_duration_weeks", "1")

        self.add_command("info", self.cmd_player_info,  usage="[<id>|<name>]")
        self.add_command("scoreboard", self.cmd_scoreboard, usage="[<id>|<name>]")
        self.add_command(("allelo", "allelos", "aelo", "eloall"), self.cmd_all_elos, usage="[<id>|<name>]")

        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_LOWEST)


    def handle_player_connect(self, player):
        cond = self.get_cvar("qlx_pinfo_display_auto", int)
        cond += self.get_cvar("qlx_pinfo_show_deactivated", int)
        cond += self.get_cvar("qlx_pinfo_ban_deactivated", int)

        human = str(player.steam_id)[0] != "9"

        if human and cond:
            self.fetch(player, self.game.type_short, None)




    def cmd_player_info(self, player, msg, channel):
        if len(msg) > 2:
            return minqlx.RET_USAGE

        if len(msg) < 2:
            target_player = player
        else:
            try:
                sid = int(msg[1])
                assert len(msg[1]) == 17
                target_player = sid
            except:
                target_player = self.find_by_name_or_id(player, msg[1])
                if not target_player: return minqlx.RET_STOP_EVENT

        # If there is a duel going on and a spec called the command,
        # ensure that the playing players don't see it
        if self.game.type_short == "duel" and self.game.state == "in_progress":
            if player.team != "free":
                channel = minqlx.SPECTATOR_CHAT_CHANNEL

        # go fetch his elo
        self.fetch(target_player, self.game.type_short, channel)


    def cmd_all_elos(self, player, msg, channel):
        if len(msg) > 2:
            return minqlx.RET_USAGE

        if len(msg) < 2:
            target_player = player
        else:
            try:
                sid = int(msg[1])
                assert len(msg[1]) == 17
                target_player = sid
            except:
                target_player = self.find_by_name_or_id(player, msg[1])
                if not target_player: return minqlx.RET_STOP_EVENT

        # go fetch his elo
        self.fetch(target_player, None, channel)

    # Show info of people fallen off the scoreboard
    def cmd_scoreboard(self, player, msg, channel):
        def show(target):
            _n = target.name
            _s = target.stats.score
            _k = target.stats.kills
            _d = target.stats.deaths
            try:
                _p = target.stats.ping
            except:
                _p = "--" # in case of older minqlx version

            _tm = int(target.stats.time / 60000 )
            _ts = int((target.stats.time % 60000) / 1000)
            _dd = target.stats.damage_dealt
            _t = target.team
            _ad = "{}^2ALIVE" if target.is_alive else "{}^1DEAD"
            _hc = int(target.cvars.get('handicap', 100))
            _c = '^7,'
            if _t == 'blue': _c = '^4,'
            if _t == 'red': _c = '^1,'
            _hc = "^3{}％^7-".format(_hc) if (_hc < 100) else ''
            _ad = _ad.format(_hc)


            message = "{}^7({}^7) {k}score ^7{}{c} {k}k/d ^7{}/{}{c} {k}dmg ^7{}{c} {k}time ^7{}m{}s{c} {k}ping ^7{}"
            message = message.format(_n, _ad, _s, _k, _d, _dd, _tm, _ts, _p, c=_c, k=_c[0:-1])
            channel.reply("^7" + message)

        teams = self.teams()
        scoreboard_length = 8

        players = []
        if len(teams['red']) > scoreboard_length:
            sorted_red = sorted(teams["red"], key=lambda p: p.score, reverse=True)
            for p in sorted_red[scoreboard_length:]:
                players.append(p)
        if len(teams['blue']) > scoreboard_length:
            sorted_blue = sorted(teams['blue'], key=lambda p: p.score, reverse=True)
            for p in sorted_blue[scoreboard_length:]:
                players.append(p)

        if not players:
            channel.reply("^7No players falling off the scoreboard...")
            return

        for p in players:
            show(p)





    @minqlx.thread
    def fetch(self, player, gt, channel):
        try:
            sid = player.steam_id
        except:
            sid = player

        attempts = 0
        last_status = 0
        while attempts < MAX_ATTEMPTS:
            attempts += 1
            url = "http://qlstats.net/{elo}/{}".format(sid, elo=self.get_cvar('qlx_balanceApi'))
            res = requests.get(url)
            last_status = res.status_code
            if res.status_code != requests.codes.ok:
                continue

            js = res.json()
            if "players" not in js:
                last_status = -1
                continue

            if "deactivated" in js and js["deactivated"]:

                # If we notice deactivated, ban player (auto or cmd initiated)
                if self.get_cvar("qlx_pinfo_ban_deactivated", int):
                    self.ban_deactivated(player)
                    return

                elif self.get_cvar("qlx_pinfo_show_deactivated", int):
                    @minqlx.next_frame
                    def warn():
                        self.msg("^3SERVER WARNING^7! {}^7's account has been ^1DEACTIVATED^7 on qlstats.".format(player.name))
                    warn()

            # if we came here from a connect trigger, for a server that doesnt want auto info, return
            if not channel and not self.get_cvar("qlx_pinfo_display_auto", int):
                return

            if not channel:
                channel = minqlx.CHAT_CHANNEL
                if self.game.state == "in_progress":
                    channel = minqlx.SPECTATOR_CHAT_CHANNEL


            for p in js["players"]:
                _sid = int(p["steamid"])
                if _sid == sid: # got our player
                    # If they want all the elos
                    if not gt: return self.callback_all(player, p, channel)
                    # If the request gametype is found
                    if gt in p: return self.callback(player, p[gt]["elo"], p[gt]["games"], channel)
                    # If the gametype was not found
                    else: return self.callback(player, 0,0, channel)



        return self.callback(player, 0, 0, channel)


    def callback_all(self, player, modes, channel):
        info = []
        for mode in modes:
            if mode not in EXT_SUPPORTED_GAMETYPES: continue
            elo = modes[mode]['elo']
            games = modes[mode]["games"]
            info.append(" ^3{}^7: {} ({} games)".format(mode.upper(), elo, games))

        if not info:
            channel.reply("^6{}^7 has no tracked elos.".format(player.name))
        else:
            b = 'b' if self.get_cvar('qlx_balanceApi') == 'elo_b' else ''
            channel.reply("^6{}^7's {}ELO's: {}".format(player.name, b, ", ".join(info)))


    def callback(self, target_player, elo, games, channel):

        try:
            ident = target_player.steam_id
            name = target_player.name
        except:
            ident = target_player
            name = target_player

        try:
            completed = int(self.db[COMPLETED_KEY.format(ident)])
        except:
            completed = 0
        try:
            left = int(self.db[LEFT_KEY.format(ident)])
        except:
            left = 0


        if left + completed == 0:
            games_here_p = 1
        else:
            games_here_p = left + completed


        info = ["^6{} ^7games here".format(completed + left)]
        info[0] = info[0] + " ^7(^6{}^7 tracked {})".format(games, self.game.type_short)

        info.append("^7quit ^6{}^7％".format(round(left/(games_here_p)*100)))

        info.append("^3{} ^7{}ELO: ^6{}^7".format(self.game.type_short.upper(),'b' if self.get_cvar('qlx_balanceApi') == 'elo_b' else '', elo, games))

        return channel.reply("^6{}^7: ".format(name) + "^7, ".join(info) + "^7.")

    @minqlx.delay(2)
    def ban_deactivated(self, player):
        try:
            duration = self.get_cvar("qlx_pinfo_ban_duration_weeks", int)
            td = datetime.timedelta(weeks=duration)
            now = datetime.datetime.now().strftime(TIME_FORMAT)
            expires = (datetime.datetime.now() + td).strftime(TIME_FORMAT)
            base_key = PLAYER_KEY.format(player.steam_id) + ":bans"
            ban_id = self.db.zcard(base_key)
            db = self.db.pipeline()
            db.zadd(base_key, time.time() + td.total_seconds(), ban_id)
            ban = {"expires": expires, "reason": "deactivated account", "issued": now, "issued_by": "player_info"}
            db.hmset(base_key + ":{}".format(ban_id), ban)
            db.execute()
            self.kick(player.id, "banned from this server because of deactivated account.")
        except:
            n = player.name
            self.kick(player.id, "kicked because of deactivated account.")
            self.msg("{} has been kicked, but could not be banned. Contact iouonegirl".format(n))

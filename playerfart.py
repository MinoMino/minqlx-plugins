#####
# The last player on the team farts randomly
# Fun with friends
# Requires: 
#   Essentials plugin
#   MyFun plugin (https://github.com/BarelyMiSSeD/minqlx-plugins/tree/master/myFun)
#####

import minqlx
from minqlx import Plugin
import time
import random
import threading

VERSION = "v0.1"
PLAYERS_SOUNDS = "minqlx:players:{}:flags:myFun:{}"

class playerfart(minqlx.Plugin):
    def __init__(self):
        super().__init__()

        self.add_hook("round_start", self.handle_round_start)
        self.add_hook("round_end", self.handle_round_end)

        self.add_command("fart", self.cmd_fart, 3, usage="[<id>|<name>]")
        self.add_command("farts", self.cmd_enable_farts)

        self.farts = {
            "fart": "sound/warp/fart.ogg",
            "fartt": "sound/warp/fartt.ogg",
            "farttt": "sound/warp/farttt.ogg",
            "ffart": "sound/warp/ffart.ogg",
            "ffartt": "sound/warp/ffartt.ogg",
            "ffarttt": "sound/warp/ffarttt.ogg",
            "fffartt": "sound/warp/fffartt.ogg",
            "fffarttt": "sound/warp/fffarttt.ogg",
        }

        self.messages = {
            "1": "{} ta se cagando de medo.. brrr...",
            "2": "{} se cagou.",
            "3": "{} precisa trocar a cueca.",
            "4": "{} espremeu uma pomada.",
            "5": "{} cagou um tijolo.",
            "6": "{} pariu uma sucuri.",
            "7": "{} libertou o Mandela.",
            "8": "{} so faz merda.",
            "9": "{} rompeu o esfincter.",
            "10": "{} tirou o charufo do beiço.",
        }
        
        # keep looking for AFK players
        self.running = False

        # Interval for the thread to call player fart.
        self.interval = 10

    def handle_round_start(self, round_number):
        # start checking thread
        self.running = True
        self.help_create_thread()
        
    def handle_round_end(self, round_number):
        self.running = False

    @minqlx.thread
    def help_create_thread(self):
        while self.running and self.game and self.game.state == 'in_progress':
            time.sleep((int)(random.choice([10, 12, 15])))
            
            teams = self.teams()
            team = self.get_random_team()
            remaining = 0
            lastplayer = None
            for p in teams[team]:
                if p.is_alive:
                    remaining += 1  
                    lastplayer = p
            
            if remaining == 1:
                self.def_fart(lastplayer)

    def cmd_fart(self, player, msg, channel):
        if len(msg) < 2:
            self.def_fart(player)
            return minqlx.RET_USAGE
        else:
            self.def_fart(msg[1])
    
    @minqlx.next_frame
    def def_fart(self, player):
        for p in self.players():
            # Play sound for all players but only for those who has !sounds enables
            if self.db.get_flag(p, "essentials:farts_enabled", default=True):
                Plugin.play_sound(self.get_random_fart_sound(), p)
        self.msg(self.get_random_message().format(player))

    def get_random_fart_sound(self):
        key, sound = random.choice(list(self.farts.items()))
        return sound
    
    def get_random_message(self):
        key, message = random.choice(list(self.messages.items()))
        return message
    
    def get_random_team(self):
        team = random.choice(["red", "blue"]) 
        return team
    
    def cmd_enable_farts(self, player, msg, channel):
        if "essentials" not in self._loaded_plugins:
            flag = self.db.get_flag(player, "essentials:farts_enabled", default=True)
            self.db.set_flag(player, "essentials:farts_enabled", not flag)

            if flag:
                player.tell("Random farts have been disabled. Use ^6{}farts^7 to enable them again."
                            .format(self._command_prefix))
            else:
                player.tell("Random farts have been enabled. Use ^6{}farts^7 to disable them again."
                            .format(self._command_prefix))

            return minqlx.RET_STOP_ALL
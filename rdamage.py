import minqlx
from collections import defaultdict

VERSION = '0.5'
SUPPORTED_GAMETYPES = ('ca', 'dom', 'ft')


class rdamage(minqlx.Plugin):
    def __init__(self):
        super().__init__()

        self.add_hook('game_start', self.handle_game_start)
        self.add_hook('round_start', self.handle_round_start)
        self.add_hook('round_end', self.handle_round_end)
        self.add_hook('kill', self.handle_kill)

        self.game_supported = True
        self.all_players = defaultdict(dict)
        self.red_team = defaultdict(list)
        self.blue_team = defaultdict(list)

    def handle_game_start(self, data):
        try:
            gt = self.game.type_short
            if gt not in SUPPORTED_GAMETYPES:
                self.game_supported = False
                return minqlx.RET_STOP_ALL
        except AttributeError:
            return minqlx.RET_STOP_ALL

    def handle_round_start(self, round_number):
        if not self.game_supported:
            return minqlx.RET_STOP

        self.all_players.clear()

        teams = self.teams()
        self.red_team = teams['red'].copy()
        self.blue_team = teams['blue'].copy()

        for p in self.red_team:
            self.fill_dict(p, 'red')

        for p in self.blue_team:
            self.fill_dict(p, 'blue')

    def handle_kill(self, victim, killer, data):
        if not self.game_supported:
            return minqlx.RET_STOP

        if not data['WARMUP']:
            try:
                self.all_players[killer.steam_id]['frags'] += 1
            except KeyError:
                return

    def handle_round_end(self, data):
        if not self.game_supported:
            return minqlx.RET_STOP

        self.msg('^3*** ROUND {} END ***'.format(data['ROUND']))
        self.msg('^1RED SCORES: {}, PLAYERS ROUND DAMAGE:'.format(self.game.red_score))
        for p in self.red_team:
            self.team_message(p)

        self.msg('^4BLUE SCORES: {}, PLAYERS ROUND DAMAGE:'.format(self.game.blue_score))
        for p in self.blue_team:
            self.team_message(p)

        # self.logger.info("self.all_players={}".format(self.all_players))
        leader = next(iter(sorted(self.all_players.items(), key=lambda x: x[1]['damage'], reverse=True)))
        looser = next(iter(sorted(self.all_players.items(), key=lambda x: x[1]['damage'])))
        # self.logger.info("leader={}".format(leader))
        self.summary_message(leader, 'MOST DAMAGE')
        # self.logger.info("looser={}".format(looser))
        self.summary_message(looser, 'LEAST DAMAGE')

    def fill_dict(self, player, team):
        p = player
        self.all_players[p.steam_id] = {}
        # self.logger.info("p.clean_name={}".format(p.clean_name))
        self.all_players[p.steam_id]['name'] = p.clean_name
        self.all_players[p.steam_id]['team'] = team
        self.all_players[p.steam_id]['damage'] = p.stats.damage_dealt
        self.all_players[p.steam_id]['frags'] = 0

    def team_message(self, player):
        p = player
        try:
            team = self.all_players[p.steam_id]['team']
            if team == 'red':
                color = 1
            elif team == 'blue':
                color = 4
            else:
                color = 7

            frags = self.all_players[p.steam_id]['frags']
            frags_msg = ''
            if frags > 0:
                end = 'S' if frags > 1 else ''
                frags_msg = ' ({} FRAG{})'.format(frags, end)

            self.all_players[p.steam_id]['damage'] = p.stats.damage_dealt - self.all_players[p.steam_id]['damage']
            damage = self.all_players[p.steam_id]['damage']
            if damage >= 0:
                frags_msg = ' ^3(AFK?)' if damage == 0 else frags_msg
                self.msg('^{color} {0:<20}^{color}: ^{color}{1:<5}{2}'
                         .format(p.clean_name, self.all_players[p.steam_id]['damage'], frags_msg, color=color))
        except AttributeError as e:
            self.logger.error('AttributeError: {}'.format(e))
            return
        except KeyError as e:
            self.logger.error('KeyError: {}'.format(e))
            return

    def summary_message(self, player_dict, text_prefix):
        # self.logger.info("player_dict={}".format(player_dict))
        nickname = player_dict[1]['name']
        damage = player_dict[1]['damage']
        team = player_dict[1]['team']
        if team == 'red':
            color = 1
        elif team == 'blue':
            color = 4
        else:
            color = 7

        if damage >= 0:
            frags = player_dict[1]['frags']
            frags_msg = ' ^3(AFK?)' if damage == 0 else ''
            if frags > 0:
                end = 'S' if frags > 1 else ''
                frags_msg = ' ^3WITH ^{}{} ^3FRAG{}'.format(color, frags, end)
            self.msg('^3*** {} ^{color}{} ^3BY ^{color}{}{} ^3***'
                     .format(text_prefix, damage, nickname, frags_msg, color=color))
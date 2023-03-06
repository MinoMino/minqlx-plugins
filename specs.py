#specs.py by x0rnn to list players spectating you and to check who someone is spectating
#!specs: show players spectating you
#!specwho <id>: show who <id> is spectating
#!specall: show who every spectator is spectating

import minqlx

class specs(minqlx.Plugin):

    def __init__(self):
        self.add_command("specs", self.cmd_specs)
        self.add_command("specwho", self.cmd_specwho, usage="<id>")
        self.add_command("specall", self.cmd_specall)

        self.match = False

    def cmd_specs(self, player, msg, channel):
        if player.team == "spectator":
            player.tell("You must join the game first to use this command.")
        else:
            player.tell(", ".join([p.name for p in self.teams()["spectator"] if p.state.position == player.state.position]))
        return minqlx.RET_STOP_ALL

    def cmd_specwho(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("No player with that ID.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID.")
            return

        if target_player.team == "spectator":
            for pl in self.players():
                if pl.team != "spectator":
                    specx = int(target_player.state.position.x)
                    specy = int(target_player.state.position.y)
                    specz = int(target_player.state.position.z)
                    playerx = int(pl.state.position.x)
                    playery = int(pl.state.position.y)
                    playerz = int(pl.state.position.z)
                    if abs(specx - playerx) < 20 and abs(specy - playery) < 20 and abs(specz - playerz) < 20:
                        self.match = True
                        name = pl.name
            if self.match:
                player.tell("{} is spectating {}".format(target_player.name, name))
                self.match = False
            else:
                player.tell("{} is not spectating anyone.".format(target_player.name))
        else:
            player.tell("{} is not a spectator.".format(target_player.name))
        return minqlx.RET_STOP_ALL

    def cmd_specall(self, player, msg, channel):
        for p in self.teams()["spectator"]:
            specx = int(p.state.position.x)
            specy = int(p.state.position.y)
            specz = int(p.state.position.z)
            for pl in self.players():
                if pl.team != "spectator":
                    playerx = int(pl.state.position.x)
                    playery = int(pl.state.position.y)
                    playerz = int(pl.state.position.z)
                    if abs(specx - playerx) < 20 and abs(specy - playery) < 20 and abs(specz - playerz) < 20:
                        player.tell("{} is spectating {}".format(p.name, pl.name))
        return minqlx.RET_STOP_ALL

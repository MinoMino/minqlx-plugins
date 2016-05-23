# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Adds !servers command which shows status of servers.
This plugin depends on python-valve which you can install with
sudo python3.5 -m pip install python-valve
"""

import minqlx
import time
import socket

try:
    import valve.source.a2s as a2s
except ImportError:
    minqlx.CHAT_CHANNEL.reply("^1Error: ^7The ^4python-valve ^7python library isn't installed.")
    minqlx.CHAT_CHANNEL.reply(
        "Run the following on your server to install: ^3sudo python3.5 -m pip install python-valve")
    raise ImportError


class servers(minqlx.Plugin):
    def __init__(self):
        super().__init__()
        self.add_command("servers", self.cmd_servers)

        # Example value "108.61.190.53:27960, 108.61.190.53:27961, il.qlrace.com:27960"
        self.set_cvar_once("qlx_servers", "")
        self.set_cvar_once("qlx_serversShowInChat", "0")

    def cmd_servers(self, player, msg, channel):
        """If `qlx_servers` is set then it outputs status of servers.
        Outputs to chat if `qlx_serversShowInChat` is 1, otherwise it will
        output to the player who called the command only."""
        servers = self.get_cvar("qlx_servers", list)
        if len(servers) == 1 and servers[0] == "":
            self.logger.warning("qlx_servers is not set")
            player.tell("qlx_servers is not set")
            return minqlx.RET_STOP_ALL
        elif any(s == '' for s in servers):
            self.logger.warning("qlx_servers has an invalid server(empty string). Most likely due to trailing comma.")
            player.tell("qlx_servers has an invalid server(empty string). Most likely due to trailing comma.")
            return minqlx.RET_STOP_ALL

        if not self.get_cvar("qlx_serversShowInChat", bool) and not isinstance(player, minqlx.AbstractDummyPlayer):
            self.get_servers(servers, minqlx.TellChannel(player))
            return minqlx.RET_STOP_ALL

        self.get_servers(servers, channel)

    @minqlx.thread
    def get_servers(self, servers, channel):
        """Gets and outputs info for all servers in `qlx_servers`."""
        output = ["^5{:^21} | {:^63} | {}".format("IP", "sv_hostname", "Players")]
        for server in servers:
            hostname, players = self.get_server_info(server)
            if players:
                if players[0] >= players[1]:
                    players = "^3{}/{}".format(players[0], players[1])
                else:
                    players = "^2{}/{}".format(players[0], players[1])
            else:
                players = "^1..."

            output.append("{:21} | {:63} | {}".format(server, hostname, players))
        reply_large_output(channel, output)

    @staticmethod
    def get_server_info(server):
        """Gets server info using python-valve."""
        # set port to 27960 if no port
        address = (server.split(":") + [27960])[:2]
        try:
            address[1] = int(address[1])
            server = a2s.ServerQuerier(address, 1)  # 1 second timeout
            info = server.get_info()
            return info['server_name'], [info["player_count"], info["max_players"]]
        except ValueError:
            return "Error: Invalid port", []
        except socket.gaierror:
            return "Error: Invalid/nonexistent address", []
        except a2s.NoResponseError:
            return "Error: Timed out", []


def reply_large_output(channel, output):
    """Tells large output in small portions, as not to disconnected the player."""
    for count, line in enumerate(output, start=1):
        if count % 30 == 0:  # decrease if someone getting disconnected
            time.sleep(0.4)  # increase if changing previous line does not help
            channel.reply(output[0])
        channel.reply(line)

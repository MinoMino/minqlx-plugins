import minqlx
import requests
import threading

params = [{}, {"weapons": "false"}, {"factory": "classic", "weapons": "true"},
          {"factory": "classic", "weapons": "false"}]


class race(minqlx.Plugin):
    def __init__(self):
        self.add_hook("map", self.handle_map)
        self.add_command("updatemaps", self.cmd_updatemaps)
        self.add_command(("pb", "me", "spb", "sme"), self.cmd_pb, usage="[map]")
        self.add_command(("rank", "srank"), self.cmd_rank, usage="[rank] [map]")
        self.add_command(("top", "stop"), self.cmd_top, usage="[amount] [map]")
        self.add_command(("all", "sall"), self.cmd_all, usage="[map]")
        self.add_command(("avg", "savg"), self.cmd_avg, usage="[id]")
        self.race_mode = self.get_cvar("qlx_race_mode", int)
        self.maps = None
        threading.Thread(target=self.get_maps).start()

    def handle_map(self, mapname, factory):
        threading.Thread(target=self.get_maps).start()

    def cmd_updatemaps(self, player, msg, channel):
        threading.Thread(target=self.get_maps).start()

    def cmd_pb(self, player, msg, channel):
        if len(msg) == 1:
            mapname = self.game.map.lower()
        elif len(msg) == 2:
            mapname = msg[1]
        else:
            return minqlx.RET_USAGE

        weapons = False if "s" in msg[0].lower() else True
        threading.Thread(target=self.pb, args=(mapname, weapons, player, channel)).start()

    def pb(self, mapname, weapons, player, channel):
        mapname = self.map_prefix(mapname, channel)
        if not mapname:
            return

        records = self.get_records(mapname, weapons)
        rank, time = records.pb(player.steam_id)
        if not weapons:
            mapname += "^2(strafe)"
        if rank:
            channel.reply(records.output(player, rank, time))
        else:
            channel.reply("^2No time found for ^7{} ^2on ^3{}".format(player, mapname))

    def cmd_rank(self, player, msg, channel):
        if len(msg) == 1:
            rank = 1
            mapname = self.game.map.lower()
        elif len(msg) == 2:
            if msg[1].isdigit():
                rank = int(msg[1])
                mapname = self.game.map.lower()
            else:
                rank = 1
                mapname = msg[1]
        elif len(msg) == 3:
            rank = int(msg[1])
            mapname = msg[2]
        else:
            return minqlx.RET_USAGE

        weapons = False if "s" in msg[0].lower() else True
        threading.Thread(target=self.rank, args=(mapname, weapons, rank, channel)).start()

    def rank(self, mapname, weapons, rank, channel):
        mapname = self.map_prefix(mapname, channel)
        if not mapname:
            return

        records = self.get_records(mapname, weapons)
        name, time = records.rank(rank)
        if not weapons:
            mapname += "^2(strafe)"
        if time:
            channel.reply(records.output(name, rank, time))
        else:
            channel.reply("^2No rank ^3{} ^2time found on ^3{}".format(rank, mapname))

    def cmd_top(self, player, msg, channel):
        if len(msg) == 1:
            amount = 3
            mapname = self.game.map
        elif len(msg) == 2:
            if msg[1].isdigit():
                amount = int(msg[1])
                mapname = self.game.map
            else:
                amount = 3
                mapname = msg[1]
        elif len(msg) == 3:
            amount = int(msg[1])
            mapname = msg[2]
        else:
            return minqlx.RET_USAGE
        if amount > 20:
            channel.reply("^2Please use value <=20")
            return

        weapons = False if "s" in msg[0].lower() else True
        threading.Thread(target=self.top, args=(mapname, weapons, amount, channel)).start()

    def top(self, mapname, weapons, amount, channel):
        mapname = self.map_prefix(mapname, channel)
        if not mapname:
            return

        records = self.get_records(mapname, weapons)
        if not weapons:
            mapname += "^2(strafe)"
        if not records.records:
            channel.reply("^2No times were found on ^3{}".format(mapname))
            return

        if amount > len(records.records):
            amount = len(records.records)
        times = []
        for i in range(amount):
            try:
                record = records.records[i]
                times.append(" ^3{}. ^4{} ^2{}".format(record['rank'], record['name'], time_string(record['time'])))
            except IndexError:
                break

        self.output_times(mapname, times, channel)

    def cmd_all(self, player, msg, channel):
        if len(msg) == 1:
            mapname = self.game.map
        elif len(msg) == 2:
            mapname = msg[1]
        else:
            return minqlx.RET_USAGE

        weapons = False if "s" in msg[0].lower() else True
        threading.Thread(target=self.all, args=(mapname, weapons, channel)).start()

    def all(self, mapname, weapons, channel):
        mapname = self.map_prefix(mapname, channel)
        if not mapname:
            return

        records = self.get_records(mapname, weapons)
        times = {}
        for p in self.players():
            rank, time = records.pb(p.steam_id)
            if rank:
                times[rank] = "^7{} ^2{}".format(p, time_string(time))

        if not weapons:
            mapname += "^2(strafe)"
        if times:
            times_list = []
            for rank, time in sorted(times.items()):
                times_list.append(" ^3{}. {}".format(rank, time))
            self.output_times(mapname, times_list, channel)
        else:
            channel.reply("^2No times were found for anyone on ^3{} ^2:(".format(mapname))

    def cmd_avg(self, player, msg, channel):
        if len(msg) == 2:
            try:
                i = int(msg[1])
                target_player = self.player(i)
                if not (0 <= i < 64) or not target_player:
                    raise ValueError
                player = target_player
            except ValueError:
                player.tell("Invalid ID.")
                return minqlx.RET_STOP_EVENT
        elif len(msg) > 2:
            return minqlx.RET_USAGE

        if "s" in msg[0].lower():
            mode = self.race_mode + 1
            strafe = "strafe "
        else:
            mode = self.race_mode
            strafe = ""

        threading.Thread(target=self.avg, args=(player, mode, strafe, channel)).start()

    def avg(self, player, mode, strafe, channel):
        data = requests.get("https://qlrace.com/api/player/{}".format(player.steam_id), params=params[mode]).json()
        name = data["name"]
        total_maps = len(data["records"])
        if name is not None and total_maps > 0:
            avg = data["average"]
            medals = data["medals"]
            channel.reply("^7{} ^2average {}rank: ^3{:.2f}^2({} maps) ^71st: ^3{} ^72nd: ^3{} ^73rd: ^3{}"
                          .format(player, strafe, avg, total_maps, medals[0], medals[1], medals[2]))
        else:
            channel.reply("^7{} ^2has no {}records :(".format(player, strafe))

    def output_times(self, mapname, times, channel):
        output = ["^2{}:".format(mapname)]
        for time in times:
            if len(output[len(output) - 1]) + len(time) < 100:
                output[len(output) - 1] += time
            else:
                output.append(time)

        for out in output:
            channel.reply(out.lstrip())

    def get_maps(self):
        self.maps = requests.get("https://qlrace.com/api/maps").json()["maps"]
        current_map = self.game.map.lower()
        if current_map not in self.maps:
            self.maps.append(current_map)

    def map_prefix(self, prefix, channel):
        """Returns the first map which matches the prefix."""
        if prefix in self.maps:
            return prefix

        mapname = next((x for x in self.maps if x.startswith(prefix)), None)
        if mapname:
            return mapname
        else:
            channel.reply("^2No map found for ^3{}. ^2If this is wrong, ^6!updatemaps".format(prefix))

    def get_records(self, mapname, weapons):
        if weapons:
            return RaceRecords(mapname, self.race_mode)
        else:
            return RaceRecords(mapname, self.race_mode + 1)


class RaceRecords:
    def __init__(self, mapname, mode):
        self.mapname = mapname.lower()
        self.mode = mode
        if mode == 0 or mode == 2:
            self.weapons = True
        else:
            self.weapons = False
        self.records = self.get_data()
        if self.records:
            self.last_rank = len(self.records)
            self.first_time = self.records[0]["time"]

    def rank(self, rank):
        """
        Returns name and time of the rank
        :param rank: The rank of the time which will be returned
        """
        try:
            record = self.records[rank - 1]
            if record['rank'] != rank:
                return None, None
        except IndexError:
            return None, None

        name = record["name"]
        time = record["time"]
        return name, time

    def rank_from_time(self, time):
        """
        Returns the rank the time would be
        :param time: The time in milliseconds which will be ranked
        """
        for i, record in enumerate(self.records):
            if time <= record["time"]:
                return i + 1

    def pb(self, player_id):
        """
        Returns a players rank and time
        :param player_id: The player id
        """
        for record in self.records:
            if player_id == record["player_id"]:
                time = record["time"]
                rank = record["rank"]
                return rank, time
        return None, None

    def output(self, name, rank, time):
        """
        Returns the output which will be sent to the channel
        :param name: Name of the player
        :param rank: Rank of the record
        :param time: Time of the record
        """
        if rank != 1:
            time_diff = str(time - self.first_time)
            time_diff = time_diff.zfill(3)
            time_diff = "^0[^1+" + time_string(time_diff) + "^0]"
        else:
            time_diff = ""
        time = time_string(time)
        strafe = "^2(strafe)" if not self.weapons else ""
        return "^7{} ^2is rank ^3{} ^2of ^3{} ^2with ^3{}{} ^2on ^3{}{}" \
            .format(name, rank, self.last_rank, time, time_diff, self.mapname, strafe)

    def get_data(self):
        """Gets the records for the map and mode from qlrace.com"""
        data = requests.get("https://qlrace.com/api/map/{}".format(self.mapname), params=params[self.mode]).json()
        return data['records']


def time_ms(time_string):
    """
    Returns time in milliseconds.
    :param time_string: Time as a string, examples 2.300, 1:12.383
    """
    minutes, seconds = (["0"] + time_string.split(":"))[-2:]
    return int(60000 * int(minutes) + round(1000 * float(seconds)))


def time_string(time):
    """
    Returns a time string in the format s.ms or m:s.ms if time is more than
    or equal to 1 minute.
    :param time: Time in milliseconds
    """
    time = int(time)
    s, ms = divmod(time, 1000)
    ms = str(ms).zfill(3)
    if s < 60:
        return "{}.{}".format(s, ms)
    time //= 1000
    m, s = divmod(time, 60)
    s = str(s).zfill(2)
    return "{}:{}.{}".format(m, s, ms)

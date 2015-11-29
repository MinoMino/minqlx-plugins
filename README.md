# minqlx-plugins
This is a collection of plugins for [minqlx](https://github.com/MinoMino/minqlx).
The Python dependencies are included in requirements.txt. Make sure you do a
`python3.5 -m pip install -r requirements.txt` first. `pyzmq` and `hiredis` might
need `easy_install` instead of `pip`.

The extras directory contains plugins I would not advice you use unless you further improve them or
just use them for the purpose of learning.

If you have any questions, the IRC channel for the old bot,
[#minqlbot on Quakenet](http://webchat.quakenet.org/?channels=minqlbot),
is being used for this one as well. Feel free to drop by.

## Plugins
This is a list of plugins and their cvars. Set the cvars by passing them as a command line argument or using `server.cfg`
like you would with any other QLDS cvar.

- **plugin_manager**: Adds commands to load, reload and unload plugins at run-time.
- **essentials**: Adds commands for the regular QLDS commands and some more. Adds functionality to restrict teamsize voting
and to pass votes before it fails if the majority votes yes.
  - `qlx_votepass`: A boolean deciding whether or not it should automatically pass votes before they fail if the majority
  voted yes.
    - Default: `1`
  - `qlx_votepassThreshold`: If `qlx_votepass` is `1`, determines the percentage (in decimal) of in-game players required to
  vote before it automatically passes any votes.
    - Default: `0.33`
  - `qlx_teamsizeMinimum`: The minimum teamsize allowed to vote for. `!teamsize` can override this.
    - Default: `1`
  - `qlx_teamsizeMaximum`: The maximum teamsize allowed to vote for. `!teamsize` can override this.
    - Default: `8` (if teams are full and teamsize is above 8, players will not be visible on the scoreboard)
- **ban**: Adds command to ban people for a set amount of time. Also adds functionality to ban for automatically
for leaving too many games.
  - `qlx_leaverBan`: A boolean deciding whether or not it should automatically ban players for leaving.
    - Default: `0`
  - `qlx_leaverBanThreshold`:  If `qlx_leaverBan` is `1`, determines the percentage of games (in decimal) a player has
  to go below before automatic banning takes place.
    - Default: `0.63`
  - `qlx_leaverBanWarnThreshold`: If `qlx_leaverBan` is `1`, determines the percentage of games (in decimal) a player has
  to go below before a player is warned about his/her leaves.
    - Default: `0.78`
  - `qlx_leaverBanMinimumGames`: If `qlx_leaverBan` is `1`, determines the minimum number of games a player has to player
  before automatic banning takes place. If it determines a player cannot possibly recover even if they were to not leave
  any future games before the minimum, the player will still be banned.
    - Default: `15`
- **clan**: Adds commands to let players have persistent clan tags without having to change the name on Steam.
- **motd**: Adds commands to set a message of the day.
  - `qlx_motdSound`: The path to a sounds that is played when players connect and have the MOTD printed to them.
    - Default: `sound/vo/crash_new/37b_07_alt.wav`
- **permission**: Adds commands to set player permissions.
- **names**: Adds a command to change names without relying on Steam.
  - `qlx_enforceSteamName`: A boolean deciding whether or not it should force players to use Steam names,
    but allowing colors, or to allow the player to set any name.
    - Default: `1`
- **raw**: Adds commands to interact with the Python interpreter directly. Useful for debugging.

# minqlx-plugins
This is a collection of plugins for [minqlx](https://github.com/MinoMino/minqlx).
The Python dependencies are included in requirements.txt. Make sure you do a
`python3.5 -m pip install -r requirements.txt` first. `pyzmq` and `hiredis` might
need `easy_install` instead of `pip`.

The extras directory contains plugins I would not advice you use unless you further improve them or
just use them for the purpose of learning.

If you have any questions, the IRC channel for the old bot,
[#minqlbot on Quakenet](http://webchat.quakenet.org/?channels=minqlbot),
is being used for this one as well. Feel free to drop by.

## Plugins
This is a list of plugins and their cvars. Set the cvars by passing them as a command line argument or using `server.cfg`
like you would with any other QLDS cvar.

- **plugin_manager**: Adds commands to load, reload and unload plugins at run-time.
- **essentials**: Adds commands for the regular QLDS commands and some more. Adds functionality to restrict teamsize voting
and to pass votes before it fails if the majority votes yes.
  - `qlx_votepass`: A boolean deciding whether or not it should automatically pass votes before they fail if the majority
  voted yes.
    - Default: `1`
  - `qlx_votepassThreshold`: If `qlx_votepass` is `1`, determines the percentage (in decimal) of in-game players required to
  vote before it automatically passes any votes.
    - Default: `0.33`
  - `qlx_teamsizeMinimum`: The minimum teamsize allowed to vote for. `!teamsize` can override this.
    - Default: `1`
  - `qlx_teamsizeMaximum`: The maximum teamsize allowed to vote for. `!teamsize` can override this.
    - Default: `8` (if teams are full and teamsize is above 8, players will not be visible on the scoreboard)
- **ban**: Adds command to ban people for a set amount of time. Also adds functionality to ban for automatically
for leaving too many games.
  - `qlx_leaverBan`: A boolean deciding whether or not it should automatically ban players for leaving.
    - Default: `0`
  - `qlx_leaverBanThreshold`:  If `qlx_leaverBan` is `1`, determines the percentage of games (in decimal) a player has
  to go below before automatic banning takes place.
    - Default: `0.63`
  - `qlx_leaverBanWarnThreshold`: If `qlx_leaverBan` is `1`, determines the percentage of games (in decimal) a player has
  to go below before a player is warned about his/her leaves.
    - Default: `0.78`
  - `qlx_leaverBanMinimumGames`: If `qlx_leaverBan` is `1`, determines the minimum number of games a player has to player
  before automatic banning takes place. If it determines a player cannot possibly recover even if they were to not leave
  any future games before the minimum, the player will still be banned.
    - Default: `15`
- **clan**: Adds commands to let players have persistent clan tags without having to change the name on Steam.
- **motd**: Adds commands to set a message of the day.
  - `qlx_motdSound`: The path to a sounds that is played when players connect and have the MOTD printed to them.
    - Default: `sound/vo/crash_new/37b_07_alt.wav`
- **permission**: Adds commands to set player permissions.
- **names**: Adds a command to change names without relying on Steam.
  - `qlx_enforceSteamName`: A boolean deciding whether or not it should force players to use Steam names,
    but allowing colors, or to allow the player to set any name.
    - Default: `1`
- **raw**: Adds commands to interact with the Python interpreter directly. Useful for debugging.

## kanzo's plugins

- **race**: Adds commands such as !top, !pb, !all etc.
  - `qlx_raceMode`: 0 for turbo, 2 for classic.
    - Default: `0`
  - `qlx_raceBrand`: What you want to appear before map name, example: QLRace.com - actf01
    - Default: `QLRace.com`
- **track_race**: Tracks race times and posts them to QLRace.com.
  - `qlx_raceKey`: QLRace.com API Key.
- **spec_delay**: Adds 8 seconds delay when going to from the free team to spectator and back to free.
- **vote_ban**: Ban people from voting.
- **cleverbot**: Responds to !chat using cleverbot
  - `qlx_cleverbotUser`: cleverbot.io API User.
  - `qlx_cleverbotKey`: cleverbot.io API Key.
  - `qlx_cleverbotNick`: cleverbot.io Bot nick.
    - Default: `cleverbot`

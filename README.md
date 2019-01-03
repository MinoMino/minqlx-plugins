# minqlx-plugins
This is a collection of plugins for [minqlx](https://github.com/MinoMino/minqlx).
The Python dependencies are included in requirements.txt. Make sure you do a
`python3 -m pip install -r requirements.txt` first.

The extras directory contains plugins I would not advice you use unless you further improve them or
just use them for the purpose of learning.

This repository only contains plugins maintained by me and [@em92](https://github.com/em92). Take a look [here](https://github.com/MinoMino/minqlx/wiki/Useful-Plugins) some of the plugins by other users that could be useful to you.

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
- **balance**: Adds commands and cvars to help balance teams in team games using ratings provided by third-party services.
  - `qlx_balanceAuto`: A boolean determining whether or not it should automatically try to balance teams if a shuffle vote passes.
    - Default: `1`
  - `qlx_balanceUseLocal`: A boolean determining whether or not it should use local ratings set by the *!setrating* command.
    - Default: `1`
  - `qlx_balanceMinimumSuggestionDiff`: The minimum rating difference before it suggests a switch when *!teams* is executed.
    - Default: `25`
  - `qlx_balanceUrl`: The address to the site hosting an instance of [PredatH0r's XonStat fork](https://github.com/PredatH0r/XonStat),
  which is currently the only supported rating service.
    - Default: `qlstats.net:8080`, which is hosted by PredatH0r himself.
- **silence**: Adds commands to mute a player for an extended period of time. This persists reconnects, as opposed to the
default mute behavior of QLDS.
- **clan**: Adds commands to let players have persistent clan tags without having to change the name on Steam.
- **motd**: Adds commands to set a message of the day.
  - `qlx_motdSound`: The path to a sounds that is played when players connect and have the MOTD printed to them.
    - Default: `sound/vo/crash_new/37b_07_alt.wav`
  - `qlx_motdHeader`: The header printed right before the MOTD itself.
    - Default: `^6======= ^7Message of the Day ^6=======`
- **permission**: Adds commands to set player permissions.
- **names**: Adds a command to change names without relying on Steam.
  - `qlx_enforceSteamName`: A boolean deciding whether or not it should force players to use Steam names,
    but allowing colors, or to allow the player to set any name.
    - Default: `1`
- **raw**: Adds commands to interact with the Python interpreter directly. Useful for debugging.
- **irc**: Has a small built-in IRC client that can relay chat to and from an IRC channel. It can also be used to remotely execute
minqlx commands.
  - `qlx_ircServer`: The address to the IRC server. The default port is 6667, but if you need to change it, just append `:<port>`.
    - Default: `irc.quakenet.org`
  - `qlx_ircRelayChannel`: The channel where chat is relayed to and from. Note that you must not omit the `#` from the channel name.
  - `qlx_ircRelayIrcChat`: A boolean determining whether or not it should relay messages from IRC to the game chat.
    - Default: `1`
  - `qlx_ircIdleChannels`: A list of channels you just want it to sit in and not do anything. Example: `#mychan1, #mychan2`.
  - `qlx_ircNickname`: The nickname the client will use on IRC.
    - Default: `minqlx-XXXX` where the last four characters is a random number between 1000 and 9999.
  - `qlx_ircPassword`: A password that can be used to remotely execute commands. Leave it unconfigured if you don't want this feature.
  - `qlx_ircColors`: A boolean determining whether or not it should take in-game colors and translate them to colors supported by
  a lot of IRC clients. Note that if this is not on, it will simply remove colors from all in-game chat.
    - Default: `0`
  - `qlx_ircQuakenetUser`: The Quakenet auth username. Leave it as it is if you don't use Quakenet or don't care for the feature.
  - `qlx_ircQuakenetPass`: The Quakenet auth password.
  - `qlx_ircQuakenetHidden`: Whether or not it should use mode +x, which hides its own hostname.
    - Default: `0`
- **log**: A plugin that logs chat and commands. All logs go to `fs_homepath/chatlogs`.
  - `qlx_chatlogs`: The maximum number of logs to keep around. If set to `0`, no maximum is enforced.
    - Default: `0`
  - `qlx_chatlogsSize`: The maximum size of a log in bytes before it starts with a new one.
    - Default: `5000000` (5 MB)
- **solorace**: A plugin that starts the game and keeps it running on a race server without requiring a minimum of two players,
like you usually do with race.
- **docs**: A plugin that generates a command list of all the plugins currently loaded, in the form of a Markdown file.
- **workshop**: A plugin that allows the use of custom workshop items that the server might not reference by default,
and thus not have the client download them automatically.
  - `qlx_workshopReferences`: A comma-separated list of workshop IDs for items you want to force the client to download.
  Use this for custom resources, such as sounds packs and whatnot.

## Contribute
If you create pull requests, please try to not deviate from the coding style of the plugins (e.g. don't use camelCase variable names and stuff like that), and please create the PR against the develop branch of the repository.

# minqlx-plugins
This is a collection of plugins for [minqlx](https://github.com/MinoMino/minqlx).
The Python dependencies are included in requirements.txt. Make sure you do a
`pip3.5 install -r requirements.txt` first. Replace `pip3.5` with whatever
Python 3.5's pip is called on your system.

The extras directory contains plugins I would not advice you use unless you further improve them or
just use them for the purpose of learning.

### Plugins
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
- **permission**: Adds commands to set player permissions.
- **raw**: Adds commands to interact with the Python interpreter directly. Useful for debugging.

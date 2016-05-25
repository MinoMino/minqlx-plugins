# kanzo's minqlx-plugins
This is my plugins I have developed for [minqlx](https://github.com/MinoMino/minqlx).
If you're looking for the QLRace plugins they are [here](https://github.com/QLRace/minqlx-plugins).

If you have any questions/issues with these plugins, you can contact me(kanzo) on irc at
[#minqlbot on Quakenet](http://webchat.quakenet.org/?channels=minqlbot).
Alternatively you can open an issue on this repository.

## Plugins
This is a list of plugins and their cvars. Set the cvars by passing them as a command line argument or using `server.cfg`
like you would with any other QLDS cvar.

- **banvote**: Adds !banvote command to ban people from voting.
- **checkplayers**: Shows all banned/silenced/leaverwarned/leaverbanned players.
- **cleverbot**: Responds to !chat using cleverbot.io API.
  - `qlx_cleverbotUser`: cleverbot.io API User.
  - `qlx_cleverbotKey`: cleverbot.io API Key.
  - `qlx_cleverbotNick`: cleverbot.io bot nick.
    - Default: `Cleverbot`
  - `qlx_cleverbotChance`: Chance that cleverbot responds to chat. Float between 0 and 1.
    - Default: `0`
- **servers**: Adds !servers command which shows info for a list of servers.
  - `qlx_servers`: List of servers. Example: `108.61.190.53:27960, 108.61.190.53:27961, il.qlrace.com:27960`

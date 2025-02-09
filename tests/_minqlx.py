__version__ = "NOT_SET"
DEBUG = False


# Variables with simple values
RET_NONE = 0
RET_STOP = 1
RET_STOP_EVENT = 2
RET_STOP_ALL = 3
RET_USAGE = 4

PRI_HIGHEST = 0
PRI_HIGH = 1
PRI_NORMAL = 2
PRI_LOW = 3
PRI_LOWEST = 4

# Cvar flags
CVAR_ARCHIVE = 1
CVAR_USERINFO = 2
CVAR_SERVERINFO = 4
CVAR_SYSTEMINFO = 8
CVAR_INIT = 16
CVAR_LATCH = 32
CVAR_ROM = 64
CVAR_USER_CREATED = 128
CVAR_TEMP = 256
CVAR_CHEAT = 512
CVAR_NORESTART = 1024

# Privileges
PRIV_NONE = 0
PRIV_MOD = 1
PRIV_ADMIN = 2
PRIV_ROOT = 3
PRIV_BANNED = 4294967295

# Connection states
CS_FREE = 0
CS_ZOMBIE = 1
CS_CONNECTED = 2
CS_PRIMED = 3
CS_ACTIVE = 4

# Teams
TEAM_FREE = 0
TEAM_RED = 1
TEAM_BLUE = 2
TEAM_SPECTATOR = 3

# Means of death
MOD_UNKNOWN = 0
MOD_SHOTGUN = 1
MOD_GAUNTLET = 2
MOD_MACHINEGUN = 3
MOD_GRENADE = 4
MOD_GRENADE_SPLASH = 5
MOD_ROCKET = 6
MOD_ROCKET_SPLASH = 7
MOD_PLASMA = 8
MOD_PLASMA_SPLASH = 9
MOD_RAILGUN = 10
MOD_LIGHTNING = 11
MOD_BFG = 12
MOD_BFG_SPLASH = 13
MOD_WATER = 14
MOD_SLIME = 15
MOD_LAVA = 16
MOD_CRUSH = 17
MOD_TELEFRAG = 18
MOD_FALLING = 19
MOD_SUICIDE = 20
MOD_TARGET_LASER = 21
MOD_TRIGGER_HURT = 22
MOD_NAIL = 23
MOD_CHAINGUN = 24
MOD_PROXIMITY_MINE = 25
MOD_KAMIKAZE = 26
MOD_JUICED = 27
MOD_GRAPPLE = 28
MOD_SWITCH_TEAMS = 29
MOD_THAW = 30
MOD_LIGHTNING_DISCHARGE = 31
MOD_HMG = 32
MOD_RAILGUN_HEADSHOT = 33

# damage flags
DAMAGE_RADIUS = 1  # damage was indirect
DAMAGE_NO_ARMOR = 2  # armor does not protect from this damage
DAMAGE_NO_KNOCKBACK = 4  # do not affect velocity, just view angles
DAMAGE_NO_PROTECTION = 8  # armor, shields, invulnerability, and godmode have no effect
DAMAGE_NO_TEAM_PROTECTION = (
    16  # armor, shields, invulnerability, and godmode have no effect
)


# classes
class Vector3(tuple):
    """A three-dimensional vector."""

    x = 0
    y = 0
    z = 0


class Flight(tuple):
    """A struct sequence containing parameters for the flight holdable item."""

    fuel = 0
    max_fuel = 0
    thrust = 0
    refuel = 0


class Powerups(tuple):
    """A struct sequence containing all the powerups in the game."""

    quad = 0
    battlesuit = 0
    haste = 0
    invisibility = 0
    regeneration = 0
    invulnerability = 0


class Weapons(tuple):
    """A struct sequence containing all the weapons in the game."""

    g = 0
    mg = 0
    sg = 0
    gl = 0
    rl = 0
    lg = 0
    rg = 0
    pg = 0
    bfg = 0
    gh = 0
    ng = 0
    pl = 0
    cg = 0
    hmg = 0
    hands = 0


class PlayerInfo(tuple):
    """Information about a player, such as Steam ID, name, client ID, and whatnot."""

    @property
    def client_id(self):
        """The player's client ID."""
        return self[0]

    @property
    def name(self):
        """The player's name."""
        return self[1]

    @property
    def connection_state(self):
        """The player's connection state."""
        return self[2]

    @property
    def userinfo(self):
        """The player's userinfo    ."""
        return self[3]

    @property
    def steam_id(self):
        """The player's 64-bit representation of the Steam ID."""
        return self[4]

    @property
    def team(self):
        """The player's team."""
        return self[5]

    @property
    def privileges(self):
        """The player's privileges."""
        return self[6]


class PlayerState(tuple):
    """Information about a player's state in the game."""

    is_alive = False
    """Whether the player's alive or not."""

    position = Vector3()
    """The player's position."""

    velocity = Vector3()
    """The player's velocity."""

    health = 0
    """The player's health."""

    armor = 0
    """The player's armor."""

    noclip = False
    """Whether the player has noclip or not."""

    weapon = 0
    """The weapon the player is currently using."""

    weapons = Weapons()
    """The player's weapons."""

    ammo = Weapons()
    """The player's weapon ammo."""

    powerups = Powerups()
    """The player's powerups."""

    holdable = ""
    """The player's holdable item."""

    flight = Flight()
    """A struct sequence with flight parameters."""

    is_chatting = False
    """Whether the player is currently chatting."""

    is_frozen = False
    """Whether the player is frozen(freezetag)."""


class PlayerStats(tuple):
    """A player's score and some basic stats."""

    score = 0
    """The player's primary score."""

    kills = 0
    """The player's number of kills."""

    deaths = 0
    """The player's number of deaths."""

    damage_dealt = 0
    """The player's total damage dealt."""

    damage_taken = 0
    """The player's total damage taken."""

    time = 0
    """The time in milliseconds the player has on a team since the game started."""

    ping = 0
    """The player's ping."""


# functions
def player_info(_client_id):
    """Returns a dictionary with information about a player by ID."""


def players_info():
    """Returns a list with dictionaries with information about all the players on the server."""


def get_userinfo(_client_id):
    """Returns a string with a player's userinfo."""


def send_server_command(_client_id, _cmd):
    """Sends a server command to either one specific client or all the clients."""


def client_command(_client_id, _cmd):
    """Tells the server to process a command from a specific client."""


def console_command(_cmd):
    """Executes a command as if it was executed from the server console."""


def get_cvar(_cvar):
    """Gets a cvar."""


def set_cvar(_cvar, _value, _flags=None):
    """Sets a cvar."""


def set_cvar_limit(_name, _value, _min, _max, _flags):
    """Sets a non-string cvar with a minimum and maximum value."""


def kick(_client_id, _reason=None):
    """Kick a player and allowing the admin to supply a reason for it."""


def console_print(_text):
    """Prints text on the console. If used during an RCON command, it will be printed in the player's console."""


def get_configstring(_config_id):
    """Get a configstring."""


def set_configstring(_config_id, _value):
    """Sets a configstring and sends it to all the players on the server."""


def force_vote(_pass):
    """Forces the current vote to either fail or pass."""


def add_console_command(_command):
    """Adds a console command that will be handled by Python code."""


def register_handler(_event, _handler=None):
    """Register an event handler. Can be called more than once per event, but only the last one will work."""


def player_state(_client_id):
    """Get information about the player's state in the game."""


def player_stats(_client_id):
    """Get some player stats."""


def set_position(_client_id, _position):
    """Sets a player's position vector."""


def set_velocity(_client_id, _velocity):
    """Sets a player's velocity vector."""


def noclip(_client_id, _activate):
    """Sets noclip for a player."""


def set_health(_client_id, _health):
    """Sets a player's health."""


def set_armor(_client_id, _armor):
    """Sets a player's armor."""


def set_weapons(_client_id, _weapons):
    """Sets a player's weapons."""


def set_weapon(_client_id, _weapon):
    """Sets a player's current weapon."""


def set_ammo(_client_id, _ammo):
    """Sets a player's ammo."""


def set_powerups(_client_id, _powerups):
    """Sets a player's powerups."""


def set_holdable(_client_id, _powerup):
    """Sets a player's holdable item."""


def drop_holdable(_client_id):
    """Drops player's holdable item."""


def set_flight(_client_id, _flight):
    """Sets a player's flight parameters, such as current fuel, max fuel and, so on."""


def set_invulnerability(_client_id, _time):
    """Makes player invulnerable for limited time."""


def set_score(_client_id, _score):
    """Sets a player's score."""


def callvote(_vote, _vote_display, _vote_time=None):
    """Calls a vote as if started by the server and not a player."""


def allow_single_player(_allow):
    """Allows or disallows a game with only a single player in it to go on without forfeiting. Useful for race."""


def player_spawn(_client_id):
    """Allows or disallows a game with only a single player in it to go on without forfeiting. Useful for race."""


def set_privileges(_client_id, _privileges):
    """Sets a player's privileges. Does not persist."""


def destroy_kamikaze_timers():
    """Removes all current kamikaze timers."""


def spawn_item(_item_id, _x, _y, _z):
    """Spawns item with specified coordinates."""


def remove_dropped_items():
    """Removes all dropped items."""


def slay_with_mod(_client_id, _mod):
    """Slay player with mean of death."""


def replace_items(_item1, _item2):
    """Replaces target entity's item with specified one."""


def dev_print_items():
    """Prints all items and entity numbers to server console."""


def force_weapon_respawn_time(_respawn_time):
    """Force all weapons to have a specified respawn time, overriding custom map respawn times set for them."""


def get_targetting_entities(_entity_id):
    """get a list of entities that target a given entity"""

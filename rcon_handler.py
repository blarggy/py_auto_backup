from rcon.source import Client
import configparser

config = configparser.ConfigParser()
config.read('settings.cfg')

rcon_host_address = config.get('RCON', 'RCON_HOST_ADDRESS')
rcon_port = config.get('RCON', 'RCON_PORT')
rcon_password = config.get('RCON', 'RCON_PASSWORD')
game = config.get('Game','GAME')


def query_game_server(*command):
    # Palworld specific issue https://github.com/conqp/rcon/issues/25
    # I had to remove the check for response ID from ./venv/Lib/site-packages/rcon/source/client.py
    with Client(host=rcon_host_address, port=int(rcon_port), passwd=rcon_password) as client:
        response = client.run(*command)
        return response.split("\n")


def game_commmands():
    if game == 'Palworld':
        print("""
Palworld Server rcon commands:

BanPlayer {SteamID} – Ban a specific player from your server
Broadcast {Message} – Display a message for everyone on the server to see
DoExit – Shut down the server
Info – Display server information
KickPlayer {SteamID} – Kick a specific player from your server
Save – Save the game
ShowPlayers – Display a list of players current on your server
ShutDown {Seconds} {Message} – Sets a timer for the server to shut down, as well as a message to any players currently playing
TeleportToMe {SteamID} – Teleport a specific player to your location
TeleportToPlayer {SteamID} – Teleport to a specific player’s location

""")
    else:
        print(f"Game \"{game}\" not recognized, check their documentation for rcon commands.")


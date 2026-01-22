from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_TOKEN = os.getenv('API_TOKEN')
command_prefix = "!"
activity = "Tournoi Clash Royale"

initial_extensions = ["cogs.admin", "cogs.register"]

GUILD_ID = 1385468184756486256

# Channels
CHANNELS = {
    "registrations": 1441051229051555880,
}

# Roles
ROLES = {
    # general
    "org": 1441048184846815244,
    "refere": 1441048761630724166,
    "player": 1441048131969224927,
    "member": 1441048060418457661,
}

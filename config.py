from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_TOKEN = os.getenv('API_TOKEN')
command_prefix = "!"
activity = "Tournoi Clash Royale"

initial_extensions = ["cogs.admin", "cogs.register", "cogs.tournament"]

GUILD_ID = 1385468184756486256

# Channels
CHANNELS = {
    "registrations": 1441051229051555880,
    "elimination": 1498253656313561168,
}

CATEGORIES = {
    "tournament": 1443191444348076093,
    "matchs": 1441050652230029352
}

# Roles
ROLES = {
    # general
    "org": 1441048184846815244,
    "refere": 1441048761630724166,
    "player": 1441048131969224927,
    "member": 1441048060418457661,
}

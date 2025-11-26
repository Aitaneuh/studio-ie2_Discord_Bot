import discord
from discord.ext import commands
import datetime

from database.connection import init_db
import config
from views.register_view import RegisterView

intents = discord.Intents.default()
intents.message_content = True
activity = discord.Game(name=config.activity)

bot = commands.Bot(command_prefix=config.command_prefix, intents=discord.Intents.all(), activity=activity, status=discord.Status.online)

async def load_extensions():
    for ext in config.initial_extensions:
        await bot.load_extension(ext)

@bot.event
async def on_ready():
    init_db()
    await load_extensions()
    bot.add_view(RegisterView())

@bot.event
async def on_member_join(member):
    guild = member.guild
    
    role = discord.utils.get(guild.roles, id=config.ROLES["member"])

    if role is not None and role not in member.roles:
        await member.add_roles(role)
    
if isinstance(config.TOKEN, str):
    bot.launch_time = datetime.datetime.now() # type: ignore
    bot.run(config.TOKEN)

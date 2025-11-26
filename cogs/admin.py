from discord.ext import commands
from utils.uptime import get_uptime

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="state")
    @commands.has_permissions(administrator=True)
    async def state(self, ctx: commands.Context):
        await ctx.send("bot is running")

    @commands.command(name="uptime")
    @commands.has_permissions(administrator=True)
    async def uptime(self, ctx: commands.Context):
        await ctx.send(f"bot has been running for {get_uptime(self.bot.launch_time)}.")

    @commands.command(name="clear")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: commands.Context):
        await ctx.channel.purge() # type: ignore 

async def setup(bot):
    await bot.add_cog(Admin(bot))

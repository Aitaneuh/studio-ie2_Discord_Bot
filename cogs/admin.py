import discord
from discord.ext import commands
from utils.uptime import get_uptime
from utils.simple_embed import get_simple_embed


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="state")
    @commands.has_permissions(administrator=True)
    async def state(self, ctx: commands.Context):
        await ctx.send(embed=get_simple_embed("bot is running.", color=discord.Color.green()))

    @commands.command(name="uptime")
    @commands.has_permissions(administrator=True)
    async def uptime(self, ctx: commands.Context):
        await ctx.send(embed=get_simple_embed(f"bot has been running for {get_uptime(self.bot.launch_time)}.", color=discord.Color.green()))

    @commands.command(name="clear")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: commands.Context):
        await ctx.channel.purge() # type: ignore 

async def setup(bot):
    await bot.add_cog(Admin(bot))

import discord
from discord.ext import commands
from utils.simple_embed import get_simple_embed

from database.repositories.player_repo import PlayerRepository
from database.connection import SessionLocal

db = SessionLocal()
player_repo = PlayerRepository(db)

class Tournament(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  
        
    @commands.command("generate_seeding")
    @commands.has_permissions(administrator=True)
    async def generate_seeding(self, ctx: commands.Context):
        players = player_repo.get_all_players()

        sorted_players = sorted(
            players,
            key=lambda x: (x.cr_trophy_count, x.acc_wins),
            reverse=True
        )

        for seed, player in enumerate(sorted_players):
            player = player_repo.set_player_seed(player.discord_id, seed + 1)

            member = ctx.guild.get_member(player.discord_id)
            if member is None:
                try:
                    member = await ctx.guild.fetch_member(player.discord_id)
                except discord.NotFound:
                    continue

            await member.send(
                embed=get_simple_embed(
                    title="Votre seed a été défini.",
                    description=f"Votre seed est de {player.seed}.",
                    color=discord.Colour.green()
                )
            )

    @commands.command("start_tournament")
    @commands.has_permissions(administrator=True)
    async def start_tournament(self, ctx: commands.Context):
        pass
    
async def setup(bot):
    await bot.add_cog(Tournament(bot))
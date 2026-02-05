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

    @commands.command("generate_groups")
    @commands.has_permissions(administrator=True)
    async def generate_groups(self, ctx: commands.Context):
        guild = ctx.guild

        players = player_repo.get_all_players()


        seeded_players = [p for p in players if p.seed is not None]

        if len(seeded_players) < 32:
            await ctx.send("Not enough seeded players.")
            return

        seeded_players.sort(key=lambda p: p.seed)

        blocks = [
            seeded_players[0:32],
            seeded_players[32:64],
            seeded_players[64:96],
            seeded_players[96:128],
        ]

        blocks[1].reverse()
        blocks[3].reverse()

        # Build groups
        groups: list[list] = [[] for _ in range(32)]

        for block in blocks:
            for i, player in enumerate(block):
                groups[i].append(player)

        for index, group_players in enumerate(groups, start=1):
            group_name = f"Groupe {index}"

            role = await guild.create_role(name=group_name)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                role: discord.PermissionOverwrite(view_channel=True),
            }

            category = await guild.create_category(
                name=f"🎮 {group_name}",
                overwrites=overwrites
            )

            channel = await category.create_text_channel("organisation-match")

            await channel.send(
                embed=get_simple_embed(
                    title=f"{group_name}",
                    description="Bonjour, ce channel vous servira à organiser vos matchs.",
                    color=discord.Colour.blue()
                )
            )

            for player in group_players:
                member = guild.get_member(player.discord_id)
                if member is None:
                    try:
                        member = await guild.fetch_member(player.discord_id)
                    except discord.NotFound:
                        continue

                await member.add_roles(role)

    
async def setup(bot):
    await bot.add_cog(Tournament(bot))
import discord
import math
import asyncio
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
        players = player_repo.get_all_players()
        seeded_players = sorted([p for p in players if p.seed is not None], key=lambda p: p.seed)
        num_players = len(seeded_players)

        if num_players < 4:
            return await ctx.send("Pas assez de joueurs pour créer des groupes.")

        num_groups = 2**round(math.log2(num_players / 4))
        
        # Sécurité : s'assurer qu'il y a au moins 2 groupes
        num_groups = max(2, num_groups)

        # 2. Répartition Snake (Serpentine)
        groups = [[] for _ in range(num_groups)]
        
        for i, player in enumerate(seeded_players):
            # On calcule dans quel "bloc" on se trouve (0, 1, 2, 3...)
            block_index = i // num_groups
            # On calcule la position dans le groupe
            position = i % num_groups
            
            if block_index % 2 == 0:
                # Bloc pair : remplissage normal (0, 1, 2, 3)
                groups[position].append(player)
            else:
                # Bloc impair : remplissage inversé (3, 2, 1, 0)
                groups[(num_groups - 1) - position].append(player)

        # 3. Création sur Discord
        status_msg = await ctx.send(f"Création de **{num_groups} groupes** pour **{num_players} joueurs**...")

        for index, group_players in enumerate(groups, start=1):
            group_name = f"Groupe {index}"
            
            # Création du rôle
            role = await ctx.guild.create_role(name=group_name)

            # Permissions
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                role: discord.PermissionOverwrite(view_channel=True)
            }

            # Catégorie et Salon
            category = await ctx.guild.create_category(name=f"🎮 {group_name}", overwrites=overwrites)
            channel = await category.create_text_channel("organisation-match")

            # Attribution des rôles
            for player in group_players:
                member = ctx.guild.get_member(player.discord_id) or await ctx.guild.fetch_member(player.discord_id)
                if member:
                    await member.add_roles(role)

            await channel.send(embed=get_simple_embed(
                title=f"Bienvenue dans le {group_name}",
                description=f"Joueurs dans ce groupe : {', '.join([f'<@{p.discord_id}>' for p in group_players])}",
                color=discord.Colour.blue()
            ))
            
            # Pause pour éviter le rate limit si beaucoup de groupes
            await asyncio.sleep(1)

        await status_msg.edit(content=f"✅ {num_groups} groupes générés avec succès !")

    
async def setup(bot):
    await bot.add_cog(Tournament(bot))
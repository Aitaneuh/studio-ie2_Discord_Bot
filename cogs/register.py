import discord
from discord.ext import commands

from database.repositories.player_repo import PlayerRepository
from database.connection import SessionLocal
import config
from views.register_view import RegisterView

db = SessionLocal()
player_repo = PlayerRepository(db)

class Register(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.register_channel_id = config.CHANNELS["registrations"]

    @commands.command(name="print_panel")
    @commands.has_permissions(administrator=True)
    async def print_panel(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Enregistrement de votre compte Clash Royale",
            description=(
                "Pour participer au tournoi, vous devez enregistrer votre compte Clash Royale.\n\n"
                "**Le tag de votre compte vous sera demandé, voici où le trouver :**\n\n"
                "1 — Cliquez sur votre profile pour ouvrir la page de profile.\n"
                "2 — Cliquez sur votre tag. \n"
                "3 — Cliquez sur \"Copier l'identifiant\".\n\n"
            ),
            color=discord.Color.dark_blue()
        )
        embed.set_image(url="https://i.imgur.com/EsTmW6W.jpeg")

        embed.set_footer(
            text="Assurez-vous que vos informations sont correctes. En cas d’erreur, contactez un organisateur."
        )
        await ctx.send(embed=embed, view=RegisterView())


async def setup(bot):
    await bot.add_cog(Register(bot))
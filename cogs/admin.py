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
        await ctx.send(embed=get_simple_embed("Bot is running.", color=discord.Color.green()))

    @commands.command(name="uptime")
    @commands.has_permissions(administrator=True)
    async def uptime(self, ctx: commands.Context):
        await ctx.send(embed=get_simple_embed(f"Bot has been running for {get_uptime(self.bot.launch_time)}.", color=discord.Color.green()))

    @commands.command(name="clear")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx: commands.Context):
        await ctx.channel.purge() # type: ignore

    @commands.command(name="send_rules")
    @commands.has_permissions(administrator=True)
    async def send_rules(self, ctx: commands.Context):
        """Poste les règles du tournoi sous forme de plusieurs embeds dans le salon courant."""
 
        # Supprimer la commande pour garder le salon propre
        await ctx.message.delete()
 
        # ── Embed 1 : Header ──────────────────────────────────────────────
        header = discord.Embed(
            title="🏆  Tournoi Clash Royale",
            description=(
                "Bienvenue dans le tournoi Clash Royale de l'école !\n"
                "Lisez attentivement les règles ci-dessous avant de participer."
            ),
            color=discord.Color.gold(),
        )
        header.set_thumbnail(url="https://i.imgur.com/EsTmW6W.jpeg")
        await ctx.send(embed=header)
 
        # ── Embed 2 : Format ──────────────────────────────────────────────
        format_embed = discord.Embed(
            title="📋  Format du tournoi",
            color=discord.Color.blue(),
        )
        format_embed.add_field(
            name="Phase de poules",
            value=(
                "Vous êtes répartis en groupes.\n"
                "À l'intérieur de votre groupe, vous affrontez **chaque autre joueur une fois** (Round Robin).\n"
                "Les matchs peuvent se jouer dans n'importe quel ordre."
            ),
            inline=False,
        )
        format_embed.add_field(
            name="Phase éliminatoire",
            value=(
                "Les **2 premiers de chaque groupe** se qualifient.\n"
                "On passe ensuite en élimination directe — quarts, demis, finale — jusqu'au champion."
            ),
            inline=False,
        )
        await ctx.send(embed=format_embed)
 
        # ── Embed 3 : Règles des matchs ───────────────────────────────────
        rules_embed = discord.Embed(
            title="⚔️  Règles des matchs",
            description="> Chaque match se joue en **BO1** — une seule partie, pas de revanche.",
            color=discord.Color.orange(),
        )
        rules_embed.add_field(
            name="Avant le match",
            value=(
                "— Contactez votre adversaire via Discord ou en direct pour convenir d'un moment.\n"
                "— Envoyez une demande d'ami sur Clash Royale et lancez un **match amical**."
            ),
            inline=False,
        )
        rules_embed.add_field(
            name="Pendant le match",
            value=(
                "— Aucune restriction de deck. Jouez ce que vous voulez.\n"
                "— Comportement fair-play obligatoire. Pas d'insultes, pas de provocation."
            ),
            inline=False,
        )
        rules_embed.add_field(
            name="Après le match",
            value=(
                "— Rendez-vous dans votre **salon de groupe** sur Discord.\n"
                "— Cliquez sur ✅ **\"J'ai gagné\"** pour valider le résultat.\n"
                "— Les **deux joueurs** doivent confirmer pour que le match soit enregistré."
            ),
            inline=False,
        )
        await ctx.send(embed=rules_embed)
 
        # ── Embed 4 : Classement ──────────────────────────────────────────
        standings_embed = discord.Embed(
            title="📊  Classement des poules",
            description=(
                "Le classement dans chaque groupe est déterminé par :\n\n"
                "🥇 **1. Nombre de victoires** *(critère principal)*\n"
                "🥈 **2. Goal average** (victoires − défaites) *en cas d'égalité*"
            ),
            color=discord.Color.green(),
        )
        await ctx.send(embed=standings_embed)
 
        # ── Embed 5 : Règles importantes ──────────────────────────────────
        important_embed = discord.Embed(
            title="⚠️  Règles importantes",
            color=discord.Color.red(),
        )
        important_embed.add_field(
            name="⏰ Délai",
            value="Tous les matchs de poules doivent être joués dans les délais annoncés par les organisateurs. Tout match non joué dans les temps sera attribué à l'adversaire.",
            inline=False,
        )
        important_embed.add_field(
            name="🚫 Forfait",
            value="En cas d'absence injustifiée, le match est attribué à l'adversaire **(0-1)**.",
            inline=False,
        )
        important_embed.add_field(
            name="🤝 Conflits",
            value="Si les deux joueurs déclarent avoir gagné, un organisateur tranchera. Sa décision est **définitive et sans appel**.",
            inline=False,
        )
        important_embed.add_field(
            name="🚨 Triche",
            value="Toute tentative de triche ou de manipulation entraîne une **disqualification immédiate**.",
            inline=False,
        )
        await ctx.send(embed=important_embed)
 
        # ── Embed 6 : Footer contact ──────────────────────────────────────
        footer_embed = discord.Embed(
            description=(
                "❓ **Un problème ? Un désaccord ?**\n"
                "Contactez directement un organisateur sur le serveur.\n\n"
                "*Bonne chance à tous, et que le meilleur joueur gagne !* 🎮👑"
            ),
            color=discord.Color.dark_blue(),
        )
        await ctx.send(embed=footer_embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))

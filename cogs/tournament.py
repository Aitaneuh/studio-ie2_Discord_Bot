import discord
import math
import asyncio
from discord.ext import commands

from database.connection import SessionLocal
from database.repositories.player_repo import PlayerRepository
from database.repositories.group_repo import GroupRepository
from database.repositories.match_repo import MatchRepository
from utils.simple_embed import get_simple_embed
from views.report_match_view import ReportMatchView
import config


def get_stage_name(num_players: int) -> str:
    """Retourne le nom de la phase éliminatoire selon le nombre de qualifiés."""
    stages = {2: "final", 4: "semifinal", 8: "quarterfinal", 16: "round_of_16"}
    return stages.get(num_players, f"round_of_{num_players}")


def build_standings_embed(group: object, standings: list[dict]) -> discord.Embed:
    embed = discord.Embed(
        title=f"📊 Classement — {group.name}",
        color=discord.Color.gold(),
    )
    lines = []
    for i, entry in enumerate(standings, 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"**{i}.**"
        p = entry["player"]
        lines.append(
            f"{medal} {p.cr_username} — {entry['wins']}W / {entry['losses']}L "
            f"(GA: {entry['goal_average']:+d})"
        )
    embed.description = "\n".join(lines) if lines else "Aucun match joué."
    return embed


class TournamentCog(commands.Cog, name="TournamentCog"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _get_repos(self):
        db = SessionLocal()
        return (
            db,
            PlayerRepository(db),
            GroupRepository(db),
            MatchRepository(db),
        )

    async def _notify_match(
        self,
        guild: discord.Guild,
        match,
        channel: discord.TextChannel,
    ):
        """Envoie la notification de match dans le salon de groupe."""
        p1_id, p2_id = [e.player_id for e in match.players]
        embed = discord.Embed(
            title="⚔️ Nouveau match !",
            description=(
                f"<@{p1_id}> **VS** <@{p2_id}>\n\n"
                "Jouez votre partie sur Clash Royale, puis revenez reporter le résultat ci-dessous."
            ),
            color=discord.Color.orange(),
        )
        embed.set_footer(text=f"Match ID : {match.id}")
        await channel.send(embed=embed, view=ReportMatchView())

    # ------------------------------------------------------------------ #
    #  !generate_seeding                                                   #
    # ------------------------------------------------------------------ #

    @commands.command("generate_seeding")
    @commands.has_permissions(administrator=True)
    async def generate_seeding(self, ctx: commands.Context):
        db, player_repo, _, _ = self._get_repos()
        try:
            players = player_repo.get_all_players()
            if not players:
                return await ctx.send(embed=get_simple_embed("Aucun joueur enregistré.", color=discord.Color.red()))

            sorted_players = sorted(
                players,
                key=lambda x: (x.cr_trophy_count, x.acc_wins),
                reverse=True,
            )

            for seed, player in enumerate(sorted_players, start=1):
                player_repo.set_player_seed(player.discord_id, seed)

                member = ctx.guild.get_member(int(player.discord_id))
                if member is None:
                    try:
                        member = await ctx.guild.fetch_member(int(player.discord_id))
                    except discord.NotFound:
                        continue

                await member.send(
                    embed=get_simple_embed(
                        title="🌱 Votre seed a été défini",
                        description=f"Votre seed est **#{seed}**.",
                        color=discord.Color.green(),
                    )
                )

            await ctx.send(
                embed=get_simple_embed(
                    f"Seeds générés pour {len(sorted_players)} joueurs.",
                    color=discord.Color.green(),
                )
            )
        finally:
            db.close()

    # ------------------------------------------------------------------ #
    #  !generate_groups                                                    #
    # ------------------------------------------------------------------ #

    @commands.command("generate_groups")
    @commands.has_permissions(administrator=True)
    async def generate_groups(self, ctx: commands.Context):
        db, player_repo, group_repo, _ = self._get_repos()
        try:
            players = player_repo.get_all_players()
            seeded_players = sorted(
                [p for p in players if p.seed is not None], key=lambda p: p.seed
            )
            num_players = len(seeded_players)

            if num_players < 4:
                return await ctx.send(embed=get_simple_embed("Pas assez de joueurs (minimum 4).", color=discord.Color.red()))

            # Nombre de groupes : puissance de 2 la plus proche de num_players / 4
            num_groups = max(2, 2 ** round(math.log2(num_players / 4)))

            # Répartition serpentine
            buckets: list[list] = [[] for _ in range(num_groups)]
            for i, player in enumerate(seeded_players):
                block = i // num_groups
                pos = i % num_groups
                buckets[pos if block % 2 == 0 else (num_groups - 1 - pos)].append(player)

            status_msg = await ctx.send(f"Création de **{num_groups} groupes** pour **{num_players} joueurs**...")

            for index, group_players in enumerate(buckets, start=1):
                group_name = f"Groupe {index}"

                # Rôle Discord
                role = await ctx.guild.create_role(name=group_name)

                # Salon privé
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                }
                category = await ctx.guild.create_category(name=f"🎮 {group_name}", overwrites=overwrites)
                channel = await category.create_text_channel("organisation-match")

                # Sauvegarde en base
                group = group_repo.create_group(group_name, str(role.id), str(channel.id))

                for player in group_players:
                    group_repo.add_member(group.id, player.discord_id)
                    member = ctx.guild.get_member(int(player.discord_id)) or await ctx.guild.fetch_member(int(player.discord_id))
                    if member:
                        await member.add_roles(role)

                # Message de bienvenue
                mentions = " ".join(f"<@{p.discord_id}>" for p in group_players)
                await channel.send(
                    embed=get_simple_embed(
                        title=f"Bienvenue dans le {group_name} !",
                        description=f"Joueurs : {mentions}\n\nVos matchs seront postés ici. Bonne chance ! 🍀",
                        color=discord.Color.blue(),
                    )
                )
                await asyncio.sleep(1)

            await status_msg.edit(content=f"✅ {num_groups} groupes générés avec succès !")
        finally:
            db.close()

    # ------------------------------------------------------------------ #
    #  !start_group_stage                                                  #
    # ------------------------------------------------------------------ #

    @commands.command("start_group_stage")
    @commands.has_permissions(administrator=True)
    async def start_group_stage(self, ctx: commands.Context):
        """Génère tous les matchs Round Robin pour tous les groupes et les poste."""
        db, _, group_repo, _ = self._get_repos()
        try:
            groups = group_repo.get_all_groups()
            if not groups:
                return await ctx.send(embed=get_simple_embed("Aucun groupe trouvé. Lance d'abord `!generate_groups`.", color=discord.Color.red()))

            for group in groups:
                matches = group_repo.generate_round_robin_matches(group.id)
                channel = ctx.guild.get_channel(int(group.discord_channel_id))
                if channel is None:
                    continue

                await channel.send(
                    embed=get_simple_embed(
                        title="🏁 La phase de poules commence !",
                        description=f"{len(matches)} matchs ont été générés. Jouez-les dans l'ordre ou en parallèle.",
                        color=discord.Color.dark_gold(),
                    )
                )
                # Poster chaque match dans le salon
                for match in matches:
                    await self._notify_match(ctx.guild, match, channel)
                    await asyncio.sleep(0.5)

            await ctx.send(embed=get_simple_embed("Phase de poules lancée pour tous les groupes ✅", color=discord.Color.green()))
        finally:
            db.close()

    # ------------------------------------------------------------------ #
    #  !standings [groupe_id]                                             #
    # ------------------------------------------------------------------ #

    @commands.command("standings")
    @commands.has_permissions(administrator=True)
    async def standings(self, ctx: commands.Context, group_id: int = None):
        """Affiche le classement d'un groupe (ou de tous si pas d'argument)."""
        db, _, group_repo, _ = self._get_repos()
        try:
            groups = [group_repo.get_group_by_id(group_id)] if group_id else group_repo.get_all_groups()
            groups = [g for g in groups if g is not None]

            if not groups:
                return await ctx.send(embed=get_simple_embed("Aucun groupe trouvé.", color=discord.Color.red()))

            for group in groups:
                standing_data = group_repo.get_group_standings(group.id)
                embed = build_standings_embed(group, standing_data)
                await ctx.send(embed=embed)
        finally:
            db.close()

    # ------------------------------------------------------------------ #
    #  !force_win @joueur  (résolution de conflit)                        #
    # ------------------------------------------------------------------ #

    @commands.command("force_win")
    @commands.has_permissions(administrator=True)
    async def force_win(self, ctx: commands.Context, member: discord.Member):
        """Résout un conflit en désignant manuellement le gagnant d'un match."""
        db, _, _, match_repo = self._get_repos()
        try:
            discord_id = str(member.id)
            match = match_repo.get_pending_match_for_player(discord_id)
            if not match:
                return await ctx.send(embed=get_simple_embed(f"{member.display_name} n'a pas de match en cours.", color=discord.Color.red()))

            # Réinitialiser les reports et forcer le résultat
            for entry in match.players:
                entry.reported = True
                entry.won = entry.player_id == discord_id
            db.commit()
            match_repo._finalize_match(match.id)

            await ctx.send(
                embed=get_simple_embed(
                    title="✅ Victoire forcée",
                    description=f"{member.mention} est déclaré vainqueur du match #{match.id}.",
                    color=discord.Color.green(),
                )
            )

            # Vérifier si la phase de poules est terminée
            if match.group_id:
                await self.check_group_completion(ctx, match.group_id)
        finally:
            db.close()

    # ------------------------------------------------------------------ #
    #  !start_elimination                                                  #
    # ------------------------------------------------------------------ #

    @commands.command("start_elimination")
    @commands.has_permissions(administrator=True)
    async def start_elimination(self, ctx: commands.Context):
        """Lance la phase éliminatoire en qualifiant les 2 premiers de chaque groupe."""
        db, _, group_repo, match_repo = self._get_repos()
        try:
            groups = group_repo.get_all_groups()
            if not groups:
                return await ctx.send(embed=get_simple_embed("Aucun groupe trouvé.", color=discord.Color.red()))

            # Vérifier que tous les matchs de poules sont terminés
            for group in groups:
                if not group_repo.all_group_matches_finished(group.id):
                    return await ctx.send(
                        embed=get_simple_embed(
                            f"⏳ Le {group.name} a encore des matchs en cours. Terminez la phase de poules d'abord.",
                            color=discord.Color.orange(),
                        )
                    )

            # Récupérer les 2 premiers de chaque groupe
            qualifiers: list = []
            qualifier_lines = []
            for group in groups:
                standings = group_repo.get_group_standings(group.id)
                top2 = standings[:2]
                for entry in top2:
                    qualifiers.append(entry["player"])
                qualifier_lines.append(
                    f"**{group.name}** : {top2[0]['player'].cr_username} 🥇 & {top2[1]['player'].cr_username} 🥈"
                )

            num_qualifiers = len(qualifiers)
            stage = get_stage_name(num_qualifiers)

            # Bracket : seed 1 vs dernier, seed 2 vs avant-dernier, etc.
            # qualifiers est déjà trié par groupe → on garde l'ordre des seeds
            # Appariement : 1 vs N, 2 vs N-1 ...
            matches_created = []
            half = num_qualifiers // 2
            for i in range(half):
                p1 = qualifiers[i]
                p2 = qualifiers[num_qualifiers - 1 - i]
                match = match_repo.create_elimination_match(stage, p1.discord_id, p2.discord_id)
                matches_created.append((match, p1, p2))

            # Créer un salon dédié à la phase éliminatoire
            elim_channel_id = config.CHANNELS.get("elimination")
            elim_channel = ctx.guild.get_channel(elim_channel_id) if elim_channel_id else None
            if elim_channel is None:
                elim_channel = ctx.channel  # fallback : salon actuel

            embed = discord.Embed(
                title="🏆 Phase éliminatoire — Début !",
                description="\n".join(qualifier_lines),
                color=discord.Color.gold(),
            )
            await elim_channel.send(embed=embed)

            for match, p1, p2 in matches_created:
                await self._notify_match(ctx.guild, match, elim_channel)
                await asyncio.sleep(0.5)

            await ctx.send(embed=get_simple_embed(f"Phase éliminatoire lancée ({num_qualifiers} qualifiés) ✅", color=discord.Color.green()))
        finally:
            db.close()

    # ------------------------------------------------------------------ #
    #  Logique interne : vérification fin de poules                       #
    # ------------------------------------------------------------------ #

    async def check_group_completion(self, ctx_or_interaction, group_id: int | None):
        """Appelé après chaque match pour vérifier si la phase de poules d'un groupe est terminée."""
        if group_id is None:
            return

        db, _, group_repo, _ = self._get_repos()
        try:
            if not group_repo.all_group_matches_finished(group_id):
                return

            group = group_repo.get_group_by_id(group_id)
            standings = group_repo.get_group_standings(group_id)

            guild = ctx_or_interaction.guild
            channel = guild.get_channel(int(group.discord_channel_id))

            if channel:
                embed = build_standings_embed(group, standings)
                embed.title = f"✅ Phase de poules terminée — {group.name}"
                embed.description = (
                    (embed.description or "")
                    + f"\n\n🎯 **{standings[0]['player'].cr_username}** et **{standings[1]['player'].cr_username}** sont qualifiés !"
                )
                await channel.send(embed=embed)
        finally:
            db.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(TournamentCog(bot))
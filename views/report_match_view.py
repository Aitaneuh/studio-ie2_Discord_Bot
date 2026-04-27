import discord
from discord.ui import View


class ReportMatchView(View):
    """
    Vue persistante affichée dans le salon de match.
    Chaque joueur clique sur "J'ai gagné" pour reporter son résultat.
    """

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✅ J'ai gagné",
        style=discord.ButtonStyle.success,
        custom_id="report_win_button",
    )
    async def report_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Import ici pour éviter les imports circulaires
        from database.connection import SessionLocal
        from database.repositories.match_repo import MatchRepository

        await interaction.response.defer(ephemeral=True)

        db = SessionLocal()
        try:
            repo = MatchRepository(db)
            discord_id = str(interaction.user.id)

            match = repo.get_pending_match_for_player(discord_id)
            if not match:
                return await interaction.followup.send(
                    "❌ Tu n'as pas de match en cours.", ephemeral=True
                )

            # Vérifier que ce salon correspond bien au match du joueur
            match_entry = repo.get_match_player(match.id, discord_id)
            if not match_entry:
                return await interaction.followup.send(
                    "❌ Tu ne participes pas à ce match.", ephemeral=True
                )

            if match_entry.reported:
                return await interaction.followup.send(
                    "⏳ Tu as déjà reporté ton résultat. En attente de ton adversaire...", ephemeral=True
                )

            try:
                finished_match = repo.report_win(match.id, discord_id)
            except ValueError:
                # Conflit entre les deux déclarations
                await interaction.followup.send(
                    "⚠️ Conflit détecté : les deux joueurs déclarent avoir gagné. Un admin va trancher.",
                    ephemeral=False,
                )
                # Notifier les admins via le channel
                await interaction.channel.send(
                    "🚨 **Conflit de résultat** — Les deux joueurs ont déclaré une victoire. "
                    "Un administrateur doit résoudre ce match manuellement avec `!force_win @joueur`."
                )
                return

            if finished_match is None:
                # L'adversaire n'a pas encore reporté
                opponent_entry = repo.get_opponent(match.id, discord_id)
                await interaction.followup.send(
                    f"✅ Résultat enregistré ! En attente de <@{opponent_entry.player_id}>...",
                    ephemeral=True,
                )
                await interaction.channel.send(
                    f"<@{discord_id}> a reporté son résultat. En attente de <@{opponent_entry.player_id}>..."
                )
            else:
                # Match terminé — annoncer le gagnant
                winner_entry = next(e for e in finished_match.players if e.won)
                loser_entry = next(e for e in finished_match.players if not e.won)
                await interaction.channel.send(
                    f"🏆 Match terminé ! <@{winner_entry.player_id}> bat <@{loser_entry.player_id}>.\n"
                    f"Les standings ont été mis à jour."
                )
                await interaction.followup.send("✅ Résultat validé !", ephemeral=True)

                # Déclencher la vérification de fin de phase de poules
                from cogs.tournament import TournamentCog
                cog = interaction.client.cogs.get("TournamentCog")
                if cog:
                    await cog.check_group_completion(interaction, finished_match.group_id)

        finally:
            db.close()
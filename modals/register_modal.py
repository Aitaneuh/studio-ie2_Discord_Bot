import discord
from discord import ui

import config
from database.connection import SessionLocal
from database.repositories.player_repo import PlayerRepository

db = SessionLocal()
player_repo = PlayerRepository(db)

class RegisterModal(discord.ui.Modal, title="Enregistrement Clash Royale"):
    def __init__(self):
        super().__init__()

        self.first_name = discord.ui.TextInput(
            label="Prénom",
            max_length=30
        )

        self.last_name = discord.ui.TextInput(
            label="Nom",
            max_length=30
        )

        self.cr_pseudo = discord.ui.TextInput(
            label="Pseudo Clash Royale",
            placeholder="Ex: Ethan",
            max_length=30
        )

        self.cr_tag = discord.ui.TextInput(
            label="Tag",
            placeholder="#PQJRVVR98",
            max_length=20
        )

        self.cr_trophies = discord.ui.TextInput(
            label="Nombre de trophées",
            placeholder="8000",
            max_length=10
        )

        self.add_item(self.first_name)
        self.add_item(self.last_name)
        self.add_item(self.cr_pseudo)
        self.add_item(self.cr_tag)
        self.add_item(self.cr_trophies)

    async def on_submit(self, interaction: discord.Interaction):

        # Extract values from the modal
        first_name = self.first_name.value.capitalize()
        last_name = self.last_name.value.capitalize()
        pseudo = self.cr_pseudo.value
        tag = self.cr_tag.value.replace("#", "").upper()
        trophies = self.cr_trophies.value

        player_role = discord.utils.get(interaction.guild.roles, id=config.ROLES["player"]); # type: ignore
        await interaction.user.add_roles(player_role) # type: ignore
        player = player_repo.create_player(str(interaction.user.id), first_name, last_name, tag, pseudo, int(trophies))

        await interaction.user.edit(nick=f"{player.first_name} {player.last_name}") # type: ignore

        embed = discord.Embed(
            title="Enregistrement complété",
            description=(
                f"Merci {player.first_name} {player.last_name}, votre compte Clash Royale a bien été enregistré !\n\n"
                f"**Pseudo :** {pseudo}\n"
                f"**Tag :** #{tag}\n"
                f"**Trophées :** {trophies}"
            ),
            color=discord.Color.green()
        )

        await interaction.user.send(
            embed=embed
        )

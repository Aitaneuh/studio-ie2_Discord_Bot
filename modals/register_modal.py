import discord
from discord import ui

import config
from utils.simple_embed import get_simple_embed
from database.connection import SessionLocal
from database.repositories.player_repo import PlayerRepository
from utils.api_query import get_player_data

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

        self.cr_tag = discord.ui.TextInput(
            label="Tag",
            placeholder="#PQJRVVR98",
            max_length=20
        )


        self.add_item(self.first_name)
        self.add_item(self.last_name)
        self.add_item(self.cr_tag)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        first_name = self.first_name.value.capitalize()
        last_name = self.last_name.value.capitalize()
        tag = "#" + self.cr_tag.value.replace("#", "").upper()
        
        player_data = await get_player_data(tag)
        if player_data == None:
            return await interaction.followup.send("Le nombre de trophées doit être un chiffre.", ephemeral=True)
        
        pseudo = player_data["name"]
        trophies = player_data["trophies"]
        best_trophies = player_data["best"]

        player_role = discord.utils.get(interaction.guild.roles, id=config.ROLES["player"])
        
        try:
            player = player_repo.create_player(
                str(interaction.user.id), 
                first_name, 
                last_name, 
                tag, 
                pseudo, 
                best_trophies
            )

            if player_role:
                await interaction.user.add_roles(player_role)
            
            await interaction.user.edit(nick=f"{pseudo}")

            embed = get_simple_embed(
                title="Enregistrement complété",
                description=(
                    f"Merci {first_name} {last_name}, votre compte Clash Royale a bien été enregistré !\n\n"
                    f"**Pseudo :** {pseudo}\n"
                    f"**Tag :** {tag}\n"
                    f"**Trophées :** {trophies}"
                ),
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"Erreur lors de l'enregistrement: {e}")
            embed = get_simple_embed(
                title="Un bug a eu lieu...",
                description="Contactez un'administrateur pour régler votre problème.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

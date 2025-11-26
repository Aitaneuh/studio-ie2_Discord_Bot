import discord
from discord.ui import View, Button
from modals.register_modal import RegisterModal


class RegisterView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="S'inscrire",
        emoji="📝",
        style=discord.ButtonStyle.primary,
        custom_id="register_button"
    )
    async def register(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RegisterModal())

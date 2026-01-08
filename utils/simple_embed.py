import discord

def get_simple_embed(title: str, description: str | None = None, color: discord.Color = discord.Color.dark_blue()) -> discord.Embed:
    embed = discord.Embed(
                title=title,
                description=description,
                color=color
            )
    return embed
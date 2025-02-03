import discord
from utils.api_utils import get_response
import random

def get_random_tarot_card():
    url = "https://tarotapi.dev/api/v1/cards/random?n=1"
    card_data = get_response(url)
    
    if card_data:
        card = card_data["cards"][0]
        orientation = random.choice(["up", "rev"])
        card_name = card["name"]
        if orientation == "rev":
            card_name += " (Reversed)"
        meaning = card[f"meaning_{orientation}"]
        description = card["desc"]
        short = card["name_short"]
        return card_name, meaning, description, short
    else:
        return None, "Error: Unable to fetch tarot card."

def setup_tarot_commands(bot):
    @bot.tree.command(name="tarot", description="Get a random tarot card reading")
    async def tarot(interaction):
        card_name, meaning, description, short = get_random_tarot_card()
        if card_name:
            embed = discord.Embed(
                title=f"Tarot Reading: {card_name}", description=f"**Meaning:** {meaning}\n**Description:** {description}",
                color=discord.Color.blue()
            )
            embed.set_image(url=f"https://sacred-texts.com/tarot/pkt/img/{short}.jpg")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Sorry, I couldn't fetch a tarot card at the moment.")

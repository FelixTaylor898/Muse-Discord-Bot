import discord
from discord import app_commands
from utils.api_utils import get_response
import os

API_KEY = os.getenv('CAT_KEY')

def setup_cat_commands(bot):
    @bot.tree.command(name="catfact", description="Get a random cat fact")
    async def catfact(interaction):
        response = get_response("https://meowfacts.herokuapp.com/")
        if response and isinstance(response.get("data"), list):
            fact = response["data"][0]
        else:
            fact = "Sorry, I couldn't fetch a cat fact at the moment."
        await interaction.response.send_message(fact)

    @bot.tree.command(name="catpic", description="Get a random cat image")
    async def catpic(interaction):
        headers = {"x-api-key": API_KEY}
        data = get_response("https://api.thecatapi.com/v1/images/search", headers)
        cat_image_url = data[0]["url"] if data else None
        if cat_image_url:
            await interaction.response.send_message(cat_image_url)
        else:
            await interaction.response.send_message("Sorry, I couldn't fetch a cat image at the moment.")
    @bot.tree.command(name="statuscat", description="Get a cat image for a specific HTTP status code")
    async def status_cat(interaction: discord.Interaction, status_code: int):
        # Ensure the status code is valid (between 100 and 599)
        if 100 <= status_code <= 599:
            url = f"https://http.cat/{status_code}"
            await interaction.response.send_message(url)
        else:
            await interaction.response.send_message("Please provide a valid HTTP status code (100-599).")

    @bot.tree.command(name="catpic2", description="Get another random cat image.")
    async def catpic2(interaction: discord.Interaction):
        await interaction.response.send_message("https://cataas.com/cat")

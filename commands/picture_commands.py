import discord
from discord import app_commands
from utils.api_utils import get_response

def setup_picture_commands(bot):
    @bot.tree.command(name="hungry", description="Get a random food image")
    async def hungry(interaction: discord.Interaction):
        data = get_response("https://foodish-api.com/api")
        food_image = data["image"]
        if food_image:
            await interaction.response.send_message(food_image)  # Send the image URL to Discord
        else:
            await interaction.response.send_message("Sorry, I couldn't fetch a food image at the moment.")
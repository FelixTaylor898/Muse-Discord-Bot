import discord
from discord import app_commands
from utils.api_utils import get_response
import random

def setup_general_commands(bot):
    @bot.tree.command(name="hello", description="Say hello to the bot")
    async def hello(interaction):
        await interaction.response.send_message("Hello, world!")

    # Command to flip a coin
    @bot.tree.command(name="flip", description="Flip a coin and get Heads or Tails")
    async def flip_coin(interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])  # Randomly choose between Heads or Tails
        await interaction.response.send_message(f"The coin flip result is: **{result}**")

    @bot.tree.command(name="random", description="Generate a random number within a given range")
    @app_commands.describe(minimum="The minimum number", maximum="The maximum number")
    async def random_number(interaction: discord.Interaction, minimum: int, maximum: int):
        if minimum > maximum:
            await interaction.response.send_message("The minimum number cannot be greater than the maximum number!")
        else:
            result = random.randint(minimum, maximum)  # Generate a random number between min and max
            await interaction.response.send_message(f"The random number between {minimum} and {maximum} is: **{result}**")

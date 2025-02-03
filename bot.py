import discord
import random
import requests
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the variables
API_KEY = os.getenv('API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Create a bot instance
intents = discord.Intents.default()  # Default intents for basic bot functionality
bot = commands.Bot(command_prefix="!", intents=intents)  # We're not using command_prefix with slash commands

@bot.event
async def on_ready():
    # Sync the slash commands to make them available to users
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

# Function to get a response from the API
def get_response(url, headers=None):
    try:
        if headers:
            response = requests.get(url, headers=headers)
        else:
            response = requests.get(url)
        response.raise_for_status()  # Raise an exception for a bad response
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Define a slash command
@bot.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello, world!")

# Slash command for random cat fact
@bot.tree.command(name="catfact", description="Get a random cat fact")
async def catfact(interaction: discord.Interaction):
    response = get_response("https://meowfacts.herokuapp.com/")
    if response and isinstance(response.get("data"), list):
        fact = response["data"][0]  # Get the first fact from the list
    else:
        fact = "Sorry, I couldn't fetch a cat fact at the moment."
    await interaction.response.send_message(fact)

# Define the command to send a cat image
@bot.tree.command(name="catpic", description="Get a random cat image")
async def catpic(interaction: discord.Interaction):
    headers = {
        "x-api-key": API_KEY
    }
    data = get_response("https://api.thecatapi.com/v1/images/search", headers)
    cat_image_url = data[0]["url"] if data else None
    if cat_image_url:
        await interaction.response.send_message(cat_image_url)  # Send the image URL to Discord
    else:
        await interaction.response.send_message("Sorry, I couldn't fetch a cat image at the moment.")

@bot.tree.command(name="hungry", description="Get a random food image")
async def catpic(interaction: discord.Interaction):
    data = get_response("https://foodish-api.com/api")
    food_image = data["image"]
    if food_image:
        await interaction.response.send_message(food_image)  # Send the image URL to Discord
    else:
        await interaction.response.send_message("Sorry, I couldn't fetch a food image at the moment.")

@bot.tree.command(name="statuscat", description="Get a cat image for a specific HTTP status code")
async def status_cat(interaction: discord.Interaction, status_code: int):
    # Ensure the status code is valid (between 100 and 599)
    if 100 <= status_code <= 599:
        url = f"https://http.cat/{status_code}"
        await interaction.response.send_message(url)
    else:
        await interaction.response.send_message("Please provide a valid HTTP status code (100-599).")

@bot.tree.command(name="catpic2", description="Get another random cat image.")
async def status_cat(interaction: discord.Interaction):
    await interaction.response.send_message("https://cataas.com/cat")

bot.run(DISCORD_TOKEN)

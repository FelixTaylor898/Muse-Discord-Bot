import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()

# Create a bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

# Load commands
from commands.cat_commands import setup_cat_commands
from commands.color_commands import setup_color_commands
from commands.tarot_commands import setup_tarot_commands
from commands.book_commands import setup_book_commands
from commands.general_commands import setup_general_commands
from commands.picture_commands import setup_picture_commands
from commands.word_commands import setup_word_commands

# Register all commands
setup_cat_commands(bot)
setup_tarot_commands(bot)
setup_book_commands(bot)
setup_general_commands(bot)
setup_color_commands(bot)
setup_picture_commands(bot)
setup_word_commands(bot)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

bot.run(DISCORD_TOKEN)
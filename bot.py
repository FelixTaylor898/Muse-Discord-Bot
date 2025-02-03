import discord
import requests
import random
import asyncio
import json
from discord.ext import commands
from discord import app_commands
import os
import io
from dotenv import load_dotenv
from PIL import Image, ImageDraw

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
async def hungry(interaction: discord.Interaction):
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
async def catpic2(interaction: discord.Interaction):
    await interaction.response.send_message("https://cataas.com/cat")

# Function to fetch a random tarot card and randomly select upright or reversed
def get_random_tarot_card():
    url = "https://tarotapi.dev/api/v1/cards/random?n=1"
    card_data = get_response(url)
    
    if card_data:
        card = card_data["cards"][0]
        
        # Randomly decide if the card is upright or reversed
        orientation = random.choice(["up", "rev"])
        
        card_name = card["name"]
        if orientation == "rev":
            card_name += " (Reversed)"
        meaning = card[f"meaning_{orientation}"]  # meaning_up or meaning_rev
        description = card["desc"]
        short = card["name_short"]
        
        return card_name, meaning, description, short
    else:
        return None, "Error: Unable to fetch tarot card."

# Define the command to fetch and display the tarot card
@bot.tree.command(name="tarot", description="Get a random tarot card reading")
async def tarot(interaction: discord.Interaction):
    card_name, meaning, description, short = get_random_tarot_card()
    
    if card_name:
        # Create the embed object
        embed = discord.Embed(title=f"Tarot Reading: {card_name}", description=f"**Meaning:** {meaning}\n**Description:** {description}", color=discord.Color.blue())
        
        # Set the image for the embed
        embed.set_image(url=f"https://sacred-texts.com/tarot/pkt/img/{short}.jpg")
        
        # Send the embed to Discord
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Sorry, I couldn't fetch a tarot card at the moment.")

# Command to flip a coin
@bot.tree.command(name="flip", description="Flip a coin and get Heads or Tails")
async def flip_coin(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])  # Randomly choose between Heads or Tails
    await interaction.response.send_message(f"The coin flip result is: **{result}**")

# Function to get book search results from OpenLibrary API
def search_books(query):
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("docs", [])
    return []

@bot.tree.command(name="book", description="Search for books by query")
@app_commands.describe(query="Enter a book title, author, or keyword")
async def book_search(interaction: discord.Interaction, query: str):
    results = search_books(query)

    if not results:
        await interaction.response.send_message("No results found.", ephemeral=True)
        return

    current_index = 0

    def get_book_embed(index):
        book = results[index]
        title = book.get("title", "No title available")
        author = ", ".join(book.get("author_name", ["Unknown Author"]))
        first_publish_year = book.get("first_publish_year", "No year available")

        imageKey = book.get("lending_edition_s", "")
        cover_url = f"https://covers.openlibrary.org/b/olid/{imageKey}-M.jpg" if imageKey else None

        embed = discord.Embed(
            title=title,
            description=f"**Author:** {author}\n**First Published:** {first_publish_year}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Book {index + 1} of {len(results)}")
        if cover_url:
            embed.set_image(url=cover_url)
        return embed

    embed = get_book_embed(current_index)

    await interaction.response.defer()
    message = await interaction.followup.send(embed=embed)

    if len(results) > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return (
                user == interaction.user
                and reaction.message.id == message.id
                and str(reaction.emoji) in ["⬅️", "➡️"]
            )

        while True:
            try:
                reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "➡️":
                    current_index = (current_index + 1) % len(results)
                elif str(reaction.emoji) == "⬅️":
                    current_index = (current_index - 1) % len(results)
                embed = get_book_embed(current_index)
                await message.edit(embed=embed)
            except asyncio.TimeoutError:
                break  # Stop waiting after 60 seconds

@bot.tree.command(name="random", description="Generate a random number within a given range")
@app_commands.describe(minimum="The minimum number", maximum="The maximum number")
async def random_number(interaction: discord.Interaction, minimum: int, maximum: int):
    if minimum > maximum:
        await interaction.response.send_message("The minimum number cannot be greater than the maximum number!")
    else:
        result = random.randint(minimum, maximum)  # Generate a random number between min and max
        await interaction.response.send_message(f"The random number between {minimum} and {maximum} is: **{result}**")



# Function to fetch colors from Colormind API
def get_colors():
    url = "http://colormind.io/api/"
    payload = json.dumps({"model": "default"})
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("result", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching colors: {e}")
        return None

# Function to generate an image displaying the colors
def generate_color_image(colors):
    width = 500
    height = 100
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    section_width = width // len(colors)
    for i, color in enumerate(colors):
        x0 = i * section_width
        x1 = (i + 1) * section_width
        draw.rectangle([x0, 0, x1, height], fill=tuple(color))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

# Convert RGB to HEX
def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])

@bot.tree.command(name="colors", description="Get a random color palette")
async def colors(interaction: discord.Interaction):
    color_palette = get_colors()

    if not color_palette:
        await interaction.response.send_message("Failed to fetch colors.", ephemeral=True)
        return

    # Convert RGB to HEX
    hex_codes = [rgb_to_hex(color) for color in color_palette]
    color_text = "\n".join(f"🎨 **Color {i+1}:** `{hex_code}`" for i, hex_code in enumerate(hex_codes))

    # Generate image
    image_bytes = generate_color_image(color_palette)
    file = discord.File(fp=image_bytes, filename="colors.png")

    embed = discord.Embed(title="🎨 Random Color Palette", color=discord.Color.blue())
    embed.set_image(url="attachment://colors.png")
    embed.description = color_text  # Add HEX codes to embed description

    await interaction.response.send_message(embed=embed, file=file)



bot.run(DISCORD_TOKEN)
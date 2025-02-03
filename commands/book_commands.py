import discord
from discord import app_commands
from utils.api_utils import get_response
import requests
import asyncio

# Function to get book search results from OpenLibrary API
def search_books(query):
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("docs", [])
    return []

def setup_book_commands(bot):
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

            imageKey = book.get("cover_i", "")
            cover_url = f"https://covers.openlibrary.org/b/id/{imageKey}-M.jpg" if imageKey else None

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
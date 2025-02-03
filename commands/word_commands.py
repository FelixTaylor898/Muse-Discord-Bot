import requests
import discord
from discord import app_commands

# Function to fetch definitions from API
def get_word_definition(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and data:
            word_data = data[0]
            word = word_data.get("word", "Unknown")
            phonetic = word_data.get("phonetic", "N/A")

            # Get phonetic audio link if available
            phonetic_audio = None
            if "phonetics" in word_data:
                for phonetic_entry in word_data["phonetics"]:
                    if "audio" in phonetic_entry and phonetic_entry["audio"]:
                        phonetic_audio = phonetic_entry["audio"]
                        break

            # Extract definitions
            definitions = []
            for meaning in word_data.get("meanings", []):
                part_of_speech = meaning.get("partOfSpeech", "Unknown")
                for i, definition in enumerate(meaning.get("definitions", []), start=1):
                    definitions.append(f"**{i}. ({part_of_speech})** {definition.get('definition', 'No definition found.')}")
            
            return word, phonetic, phonetic_audio, definitions
        else:
            return None, None, None, ["No definition found."]
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None, None, ["Error retrieving word definition."]

def setup_word_commands(bot):
    @bot.tree.command(name="define", description="Get the definition of a word")
    @app_commands.describe(word="The word you want to look up")
    async def define(interaction: discord.Interaction, word: str):
        word, phonetic, phonetic_audio, definitions = get_word_definition(word)

        if not definitions:
            await interaction.response.send_message("No definitions found for that word.", ephemeral=True)
            return

        # Embed the response
        embed = discord.Embed(title=f"📖 Definition of **{word}**", color=discord.Color.blue())
        embed.add_field(name="🔤 Phonetic", value=phonetic, inline=False)
        embed.add_field(name="📚 Meanings", value="\n".join(definitions), inline=False)

        if phonetic_audio:
            embed.add_field(name="🔊 Pronunciation", value=f"[Click here to listen]({phonetic_audio})", inline=False)

        await interaction.response.send_message(embed=embed)
import discord
from discord import app_commands
from utils.api_utils import get_response
import requests
import json
from PIL import Image, ImageDraw
import io

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

def setup_color_commands(bot):
    @bot.tree.command(name="colors", description="Get a random color palette")
    async def colors(interaction: discord.Interaction):
        color_palette = get_colors()

        if not color_palette:
            await interaction.response.send_message("Failed to fetch colors.", ephemeral=True)
            return

        # Convert RGB to HEX
        hex_codes = [rgb_to_hex(color) for color in color_palette]
        color_text = "\n".join(f"**Color {i+1}:** `{hex_code}`" for i, hex_code in enumerate(hex_codes))

        # Generate image
        image_bytes = generate_color_image(color_palette)
        file = discord.File(fp=image_bytes, filename="colors.png")

        embed = discord.Embed(title="🎨 Random Color Palette", color=discord.Color.blue())
        embed.set_image(url="attachment://colors.png")
        embed.description = color_text  # Add HEX codes to embed description

        await interaction.response.send_message(embed=embed, file=file)
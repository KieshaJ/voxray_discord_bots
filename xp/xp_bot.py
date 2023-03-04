import os
import discord
import random
from dotenv import load_dotenv


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client()

@client.event
async def on_ready():
    print("XP bot ready!")

@client.event
async def on_message(message):
    channel = message.channel

    if message.author != client.user:
        embed = discord.Embed(
            description=str(get_xp()),
            color=0x00ff00
        )
        await message.delete()
        await channel.send(embed=embed, delete_after=20)

def get_multiplier() -> int:
    multiplier = 1
    r = random.random()

    if r < 0.5:
        multiplier += 1
    elif r < 0.3:
        multiplier += 2
    elif r < 0.1:
        multiplier += 3    

    return multiplier

def get_xp() -> int:
    return get_multiplier() * random.randrange(1, 30, 1)

client.run(DISCORD_TOKEN)
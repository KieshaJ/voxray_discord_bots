import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RADIO_URL = os.getenv("RADIO_URL")
intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!r', intents=intents)


@client.event
async def on_ready():
    print("Radio bot ready!")


@client.command(name="play")
async def start(context):
    message = context.message
    channel = context.message.author.voice.channel
    global player

    try:
        player = await channel.connect()
    except:
        pass

    player.play(discord.FFmpegPCMAudio(RADIO_URL))
    await message.delete()


@client.command(name="stop")
async def stop(context):
    player.stop()

    voice_client = context.message.guild.voice_client
    await voice_client.disconnect()

    message = context.message
    await message.delete()


client.run(DISCORD_TOKEN)
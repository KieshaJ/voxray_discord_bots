import os
import random
import time
import json
from dotenv import load_dotenv
from discord.ext import commands

random.seed(time.time())
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('DISCORD_COMMAND_PREFIX')
ANTI_GREETINGS = json.loads(os.getenv('ANTI_GREETINGS'))
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to the server!')


@bot.event
async def on_member_join(new_member):
    anti_greeting = random.choice(ANTI_GREETINGS).format(new_member.mention)
    channel = new_member.guild.system_channel
    await channel.send(anti_greeting)


@bot.command(name=COMMAND_PREFIX)
async def anti_greet(context, argument):
    anti_greeting = random.choice(ANTI_GREETINGS).format(argument)
    await context.send(anti_greeting)


@bot.command(name=f'{COMMAND_PREFIX}-help')
async def display_help(context):
    text_block = f"```\n" \
           f"    Sends a random anti-greeting with a given parameter to the chat\n" \
           f"    Example: '!{COMMAND_PREFIX} @{bot.user.name}'\n" \
           f"    Anti-greetings:\n"

    for ag in ANTI_GREETINGS:
        index = ANTI_GREETINGS.index(ag) + 1
        formatted = ag.format(bot.user.name)
        text_block += f"        {index}. {formatted}\n"

    text_block += f"\n```"

    await context.send(text_block)


bot.run(DISCORD_TOKEN)

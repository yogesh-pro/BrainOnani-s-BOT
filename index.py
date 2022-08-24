import discord

from utils import default
from utils.data import Bot, HelpFormat
from discord.ext import commands

config = default.config()
print("Logging in...")

bot = Bot(
    command_prefix=config["prefix"],
    owner_ids=config["owners"], command_attrs=dict(hidden=True), help_command=HelpFormat(),
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
    intents=discord.Intents.all()
)

try:
    bot.run(config["token"])
except Exception as e:
    print(f"Error when logging in: {e}")

from unicodedata import name
import discord
import psutil
import os
import pymongo

from datetime import datetime
from discord.ext import commands
from discord.ext.commands import errors
from utils import default

MEETING_IDS = []

def meet_msg_ids():
    global MEETING_IDS
    from cogs.meetings import MEET_MESSAGE_IDS
    coll = pymongo.MongoClient("mongodb+srv://yogesh:malware@cluster0.qr7kl.mongodb.net/?retryWrites=true&w=majority")['main-database']['general']
    data = coll.find({"data.type":"meeting_ids"})
    database_ids = [] if (data is None) else [x for x in data][0]["data"]["data"]
    cache_ids = MEET_MESSAGE_IDS
    net_ids = database_ids+cache_ids
    MEETING_IDS = net_ids


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            error = default.traceback_maker(err.original)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )

            await ctx.send(f"There was an error processing the command ;-;\n{error}")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown... try again in {err.retry_after:.2f} seconds.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        to_send = next((chan for chan in guild.text_channels if chan.permissions_for(guild.me).send_messages), None)
        if to_send:
            await to_send.send(self.config["join_message"])

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            print(f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}")
        except AttributeError:
            print(f"Private message > {ctx.author} > {ctx.message.clean_content}")

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        if not hasattr(self.bot, "uptime"):
            self.bot.uptime = datetime.now()

        meet_msg_ids()

        # Check if user desires to have something other than online
        status = self.config["status_type"].lower()
        status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

        await self.bot.change_presence(
            activity=discord.Activity(
                type=2, name=self.config["activity"]
            ),
            status=status_type.get(status, discord.Status.online)
        )
        

        # Indicate that the bot has successfully booted up
        print(f"Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.message_id in MEETING_IDS:
            await payload.member.add_roles(discord.utils.get(payload.member.guild.roles,name="attendee"))
            await payload.member.send("I will notify you before meeting starts.")


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        guild = self.bot.get_guild(payload.guild_id)
        member = discord.utils.get(guild.members, id=payload.user_id)
        if payload.message_id in MEETING_IDS:
            await member.remove_roles(discord.utils.get(guild.roles,name="attendee"))
            await member.send("Notification remainder removed.")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        member_count = len(member.guild.members)
        channel = discord.utils.get(member.guild.voice_channels,id=int(self.config["member_cnt_cnl"]))
        await channel.edit(name=f"Members : {member_count}")

    @commands.Cog.listener()
    async def on_member_join(self,member):
        member_count = len(member.guild.members)
        channel = discord.utils.get(member.guild.voice_channels,id=int(self.config["member_cnt_cnl"]))
        await channel.edit(name=f"Members : {member_count}")
        channel = self.bot.get_channel(int(self.config["welcome-channel-id"]))
        embed = discord.Embed(color = 0xffd700,
        description=f'''Hey {member.mention}, welcome to your own BrainOnani community!
        Learn, Lead and Serve Brainstorming ideas into reality to make a difference together through this community !'''
        )
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Events(bot))

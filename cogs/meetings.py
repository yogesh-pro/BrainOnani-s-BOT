import discord
import pymongo

from discord.ext import commands
from discord.ui import Button, View
from utils import default


config = default.config()
MEET_MESSAGE_IDS = []

def meet_msg_ids():
    global MEET_MESSAGE_IDS
    coll = pymongo.MongoClient("mongodb+srv://yogesh:malware@cluster0.qr7kl.mongodb.net/?retryWrites=true&w=majority")['main-database']['general']

    data = coll.find({"data.type": "meeting_ids"})
    database_ids = [] if data is None else list(data)[0]["data"]["data"]
    cache_ids = MEET_MESSAGE_IDS
    net_ids = database_ids + cache_ids
    MEET_MESSAGE_IDS = net_ids

class Meetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = pymongo.MongoClient("mongodb+srv://yogesh:malware@cluster0.qr7kl.mongodb.net/?retryWrites=true&w=majority")['main-database']
    
    @commands.command(aliases=['mm'])
    @commands.guild_only()
    @commands.has_any_role('og','admin')
    async def meetmsg(self,ctx,msg_id:str):
        '''Define a message as a meeting message.'''
        global MEET_MESSAGE_IDS
        msg_id = int(msg_id)
        msg = await ctx.fetch_message(msg_id)
        db = self.db
        coll = db['general']
        old_data = coll.find({"data.type":"meeting_ids"})
        old_data = [] if (old_data is None) else [x for x in old_data][0]["data"]["data"]
        MEET_MESSAGE_IDS = old_data
        input_data = {
            "type" : "meeting_ids",
            "data" : old_data+[msg_id]
        }
        if old_data == []:
            coll.insert_one({"data":input_data})
        else:
            coll.update_one({"data.type":"meeting_ids"},{"$set" : {"data.data" : input_data["data"]}})
        await ctx.message.delete()
        cnl = self.bot.get_channel(int(config["meet_log_channel"]))
        await cnl.send(
            f"{msg.content}\nThis message has been set as a meet message by {ctx.author}"
        )
        meet_msg_ids()

    @commands.command()
    @commands.guild_only()
    @commands.has_any_role('og','admin')
    async def alert(self,ctx,url=None,*,msg):
        '''DM all intrested members a remainder of meeting.'''
        members = discord.utils.get(ctx.guild.roles,name="attendee").members
        embed = discord.Embed(title="Meeting Update!",description=f"{msg}")
        button = Button(label="Join now",url=url if url else "https://discord.com/channels/999239208831037580/999239209263046697")
        view = View().add_item(button)
        for user in members:
            await user.send(embed=embed,view=view)

    @commands.command(name='endmeet')
    @commands.guild_only()
    @commands.has_any_role('og','admin')
    async def end_meet(self,ctx):
        '''Remove meeting from schedule.'''
        role = discord.utils.get(ctx.guild.roles,name="attendee")
        members = role.members
        for user in members:
            await user.remove_roles(role)
        await ctx.reply("Done!")


async def setup(bot):
    await bot.add_cog(Meetings(bot))

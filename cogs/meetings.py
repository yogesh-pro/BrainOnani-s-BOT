
import discord
from discord.ext import commands
import pymongo

class Meetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = pymongo.MongoClient("mongodb+srv://yogesh:malware@cluster0.qr7kl.mongodb.net/?retryWrites=true&w=majority")['main-database']
    
    @commands.command(aliases=['mm'])
    @commands.guild_only()
    async def meetmsg(self,ctx,msg_id:str):
        msg_id = int(msg_id)
        msg = await ctx.fetch_message(msg_id)
        db = self.db
        coll = db['general']
        print(msg.content)
        old_data = coll.find_one({"data":{"type":"meetings_ids"}})
        old_data = [] if (old_data is None) else old_data["data"]
        input_data = {
            "type" : "meeting_ids",
            "data" : list(old_data).append(msg_id)
        }
        
        if old_data is []:
            coll.insert_one({"data":input_data})
        else:
            coll.update_one({"type":"meetings_ids"},{"$set" : {"data" : input_data["data"]}})
        
        await ctx.send("done")


async def setup(bot):
    await bot.add_cog(Meetings(bot))
import discord
import pymongo

from utils import ui

from discord.ext import commands
from utils import default

config = default.config()


def database():
    client = pymongo.MongoClient(
        "mongodb+srv://yogesh:malware@cluster0.qr7kl.mongodb.net/?retryWrites=true&w=majority"
    )

    db = client["main-database"]
    return db["points"]


class Points(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def points(self, ctx, user: discord.User = None):
        """To check your point count."""
        async with ctx.channel.typing():
            user = ctx.author if user is None else user
            db = database()
            points = db.find_one({"chr_id": user.id})
            points = 0 if points is None else points.get("points")
            embed = discord.Embed(color=user.color)
            embed.set_author(name=user.display_name, icon_url=user.avatar)
            embed.add_field(name="Total Points", value=f"**{points}**")
            await ctx.send(embed=embed)

    @commands.command()
    async def top(self, ctx, value=1):
        """See the ranking list."""
        db = database()
        data = list(db.find().sort("points", pymongo.DESCENDING))
        text = []
        value = min(value, len(list(data)))
        for x in range(value):
            x = f"""[{x + 1}] {data[x].get("name")} : {data[x].get("points")}"""
            text.append(x)
        await ctx.reply("\n".join(text))

    @commands.command(aliases=["ap", "apoints"])
    @commands.has_role("og")
    async def addpoints(self, ctx, points: int = 1, reason=None, *user: discord.Member):
        """To give points to a member."""
        view = ui.Confirm()
        confirm = await ctx.send(f"You want to add {points} Points?", view=view)
        await view.wait()
        if view.value is None:
            await ctx.send("TimeOut! Please resend point request and respond faster.")
        elif view.value:
            await confirm.delete()
            async with ctx.channel.typing():
                try:
                    db = database()
                    LOG_CHANNEL = self.bot.get_channel(
                        int(config.get("points_log_channel"))
                    )
                except Exception:
                    await ctx.send("Can't connect to the databse. `Contact Admin!`")
                users = [*user]
                try:
                    for user in users:
                        old_points = db.find_one({"chr_id": user.id})
                        old_points = (
                            0 if old_points is None else old_points.get("points")
                        )
                        if old_points == 0:
                            db.insert_one(
                                {
                                    "chr_id": user.id,
                                    "name": f"{str(user.name)}#{user.discriminator}",
                                    "points": points,
                                }
                            )

                        else:
                            db.update_one(
                                {"chr_id": user.id},
                                {"$set": {"points": old_points + points}},
                            )
                        await user.send(
                            f"""You were given `{points}` Points by {ctx.author}"""
                            + str("" if reason == "" else f"for {reason}")
                        )
                    embed = discord.Embed(
                        title="Points Update", color=discord.Color.green()
                    )
                    embed.add_field(name="Points given", value=points)
                    embed.add_field(
                        name="User(s)",
                        value=f"{' , '.join([x.display_name for x in users])}",
                    )
                    embed.set_footer(text=f"Updated by {ctx.author}")
                    await ctx.send(embed=embed)
                    await LOG_CHANNEL.send(embed=embed)
                except Exception:
                    await ctx.send("Oh No! The code broke. `contact admin`.")
        else:
            await ctx.send("No points added!")

    @commands.command(aliases=["rp", "rpoints"])
    @commands.has_role("og")
    async def removepoints(
        self, ctx, points: int = 1, reason=None, *user: discord.Member
    ):
        """To remove points from a member."""
        async with ctx.channel.typing():
            try:
                db = database()
                LOG_CHANNEL = self.bot.get_channel(
                    int(config.get("points_log_channel"))
                )
            except Exception:
                await ctx.send("Can't connect to the databse. `Contact Admin!`")
            users = [*user]
            try:
                for user in users:
                    old_points = db.find_one({"chr_id": user.id})
                    old_points = 0 if old_points is None else old_points.get("points")
                    if old_points == 0:
                        db.insert_one(
                            {
                                "chr_id": user.id,
                                "name": f"{str(user.name)}#{user.discriminator}",
                                "points": points,
                            }
                        )

                    else:
                        db.update_one(
                            {"chr_id": user.id},
                            {"$set": {"points": old_points - points}},
                        )
                    await user.send(
                        f"""Your points were reduced by `{points}` by {ctx.author}"""
                        + str("" if reason == "" else f"for {reason}")
                    )

                embed = discord.Embed(
                    title="Points Update", color=discord.Color.green()
                )
                embed.add_field(name="Points deducted", value=points)
                embed.add_field(
                    name="User(s)",
                    value=f"{' , '.join([x.display_name for x in users])}",
                )

                embed.set_footer(text=f"Updated by {ctx.author}")
                await ctx.send(embed=embed)
                await LOG_CHANNEL.send(embed=embed)
            except Exception:
                await ctx.send("Oh No! The code broke. `contact admin`.")

    @commands.command(aliases=["apfa"])
    @commands.has_role("og")
    async def addpointsforattendence(self, ctx, points=5):
        """To give points to a meeting attendee."""
        async with ctx.channel.typing():
            points = int(points)
            voice_channel = discord.utils.get(
                ctx.guild.voice_channels, id=999239209263046697
            )

            members = [*voice_channel.members]
            try:
                db = database()
                LOG_CHANNEL = self.bot.get_channel(
                    int(config.get("points_log_channel"))
                )
            except Exception:
                await ctx.send("Can't connect to the databse. `Contact Admin!`")
            try:
                for user in members:
                    old_points = db.find_one({"chr_id": user.id})
                    old_points = 0 if old_points is None else old_points.get("points")
                    if old_points == 0:
                        db.insert_one(
                            {
                                "chr_id": user.id,
                                "name": f"{str(user.name)}#{user.discriminator}",
                                "points": points,
                            }
                        )
                    else:
                        db.update_one(
                            {"chr_id": user.id},
                            {"$set": {"points": old_points + points}},
                        )
                    await user.send(
                        f"""You were given `{points}` Points by {ctx.author} for attending the meet."""
                    )

                embed = discord.Embed(
                    title="Points Update", color=discord.Color.green()
                )
                embed.add_field(name="Points given", value=points)
                embed.add_field(
                    name="User(s)",
                    value=f"{' , '.join([x.display_name for x in members])}",
                )

                embed.add_field(name="Reason", value="Attendence in meeting.")
                embed.set_footer(text=f"Updated by {ctx.author}")
                await ctx.send(embed=embed)
                await LOG_CHANNEL.send(embed=embed)
            except Exception:
                await ctx.send("Oh No! The code broke. `contact admin`.")

    @commands.command(name="newspoint", aliases=["npoint"])
    @commands.has_role("og")
    async def news_point(self, ctx, message_id):
        """To give a member 0.5 points for news sharing."""
        message = self.bot.get_message(int(message_id))
        user = message.author
        points = 0.5
        try:
            db = database()
            LOG_CHANNEL = self.bot.get_channel(int(config.get("points_log_channel")))
            old_points = db.find_one({"chr_id": user.id})
            old_points = 0 if old_points is None else old_points.get("points")
            if old_points == 0:
                db.insert_one(
                    {
                        "chr_id": user.id,
                        "name": f"{str(user.name)}#{user.discriminator}",
                        "points": points,
                    }
                )

            else:
                db.update_one(
                    {"chr_id": user.id}, {"$set": {"points": old_points + points}}
                )
            await user.send(
                f"""You were given `{points}` Points by {ctx.author} for news sharing."""
            )

            await LOG_CHANNEL.send(
                f"""{user} were given `{points}` Points by {ctx.author} for news sharing."""
            )

        except Exception:
            await ctx.send("Oh No! The code broke. `contact admin`.")

    @commands.command()
    @commands.has_role("og")
    async def resetpoints(self, ctx, month):
        """Reset point count of all members."""
        async with ctx.channel.typing():
            client = pymongo.MongoClient(
                "mongodb+srv://yogesh:malware@cluster0.qr7kl.mongodb.net/?retryWrites=true&w=majority"
            )
            db = client["main-database"]
            coll = db["points-history"]
            dbb = database()
            data = {f"{month}": [*list(dbb.find())]}
            coll.insert_one(data)
            dbb.drop()
            await ctx.send("The points have been reset.")


async def setup(bot):
    await bot.add_cog(Points(bot))

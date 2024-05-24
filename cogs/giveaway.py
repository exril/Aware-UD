from discord.ext import commands, tasks
import datetime, pytz, time as t
from discord.ui import Button, Select, View
import aiosqlite, random, typing
import asyncio
import discord, logging

from utils.paginator import PaginatorView
from utils import aware



def convert(time):
    pos = ["s","m","h","d"]
    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 86400 , "f" : 259200}

    unit = time[-1]
    if unit not in pos:
     
            
      return
    try:
        val = int(time[:-1])
    except ValueError:
            
            return

    return val * time_dict[unit]

def WinnerConverter(winner):
    try:
        int(winner)
    except ValueError:
        try:
           return int(winner[:-1])
        except:
            return -4
    
    return winner

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    def cog_load(self) -> None:
        self.GiveawayEnd.start()

    @commands.Cog.listener()
    async def on_ready(self):
        async with self.bot.db.cursor() as cursor: 
            await cursor.execute("CREATE TABLE IF NOT EXISTS Giveaway (giveaway_id INT PRIMARY KEY, time DATETIME, text NVARCHAR(255), message_id INT, channel_id INT, guild_id INT, host_id INT, start_time DATETIME, ends_at DATETIME, prize NVARCHAR(255), winners INT);") 
        await self.bot.db.commit()

    @commands.hybrid_command(description="Creates a giveaway.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def gstart(self, ctx,
                      time,
                      winners: WinnerConverter,
                      *,
                      prize: str):
        
        c = await self.bot.db.cursor()
        await c.execute("SELECT message_id, channel_id FROM Giveaway WHERE guild_id = ?", (ctx.guild.id,))
        re = await c.fetchall()

        g_list = [i[0] for i in re]
        if len(g_list) >= 5:
            return await ctx.send(f"{config.Cross} | You have reached maximum limit for this server.", ephemeral=True)


        if winners == -4:
            await ctx.send(f"{config.Cross} | Winners wasn't proper. Ex. `gstart 30m 1w Nitro.`")
            return

        converted = convert(time)
        if converted/60 >= 40320:
            return await ctx.send(f"{config.Cross} | Time cannot be more than 28 days.")
        if converted == -1:
            await ctx.send(f"{config.Cross} | The unit isn't a proper unit.")
            return
        if converted == -2:
            await ctx.send(f"{config.Cross} | Time must be in numbers.")
            return

        ends = (datetime.datetime.now().timestamp() + converted)

        embed = discord.Embed(description=f"Ends <t:{round(ends)}:R> <t:{round(ends)}:t>\nHosted by {ctx.author.mention}", color=0xffffff)
        if ctx.guild.icon:
            embed.set_author(icon_url=ctx.guild.icon.url, name=prize)
        else:
            embed.set_author(name=prize,
                             icon_url=self.bot.user.display_avatar.url)
        embed.set_footer(text=self.bot.user.name,
                         icon_url=self.bot.user.display_avatar.url)

        message = await ctx.send(":tada: **Giveaway** :tada:", embed=embed)
        try:
           await ctx.message.delete()
        except:
            pass

        cur = await self.bot.db.cursor()
        await cur.execute("INSERT INTO Giveaway(guild_id, host_id, start_time, ends_at, prize, winners, message_id, channel_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (ctx.guild.id, ctx.author.id, datetime.datetime.now(), ends, prize, winners, message.id, ctx.channel.id))

        await message.add_reaction("🎉")
        await self.bot.db.commit()


    @tasks.loop(seconds=5)
    async def GiveawayEnd(self):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id FROM Giveaway WHERE channel_id IS NOT NULL")
        ends_raw = await cur.fetchall()

        current_time = datetime.datetime.now().timestamp()

        for giveaway in ends_raw:
            if int(current_time) >= round(float(giveaway[0])):
                guild = self.bot.get_guild(int(giveaway[1]))
                channel = self.bot.get_channel(int(giveaway[6]))
                if channel is not None:
                    try:
                        message = await channel.fetch_message(int(giveaway[2]))
                    except discord.NotFound:
                        continue
                    
                    users = [i.id async for i in message.reactions[0].users()]
                    users.remove(self.bot.user.id)

                    if len(users) < 1:
                        await message.reply("Very less participants to select the winner.")
                        await cur.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
                        return
                    
                    winner = ', '.join(f'<@!{i}>' for i in random.sample(users, k=int(giveaway[4])))

                    embed = discord.Embed(
                        description=f"Ended <t:{int(current_time)}:R> <t:{int(current_time)}:t>\nWinners - {winner}\nHosted by <@{int(giveaway[3])}>",
                        color=0xffffff
                    )


                    embed.set_author(name=giveaway[5],
                                    icon_url=guild.icon.url)
                    embed.set_footer(text=self.bot.user.name,
                                    icon_url=self.bot.user.display_avatar.url)
                    try:
                       await message.edit(content=":tada: **Giveaway Ended** :tada:", embed=embed)
                    except: pass

                    

                    
                    try:
                       await message.reply(f"Congratulations, {winner} You won **{giveaway[5]}!**")
                    except: pass
                    await cur.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
                    print(f"[Natural] Giveaway Ended - {guild.id} ({giveaway[5]})")
        await self.bot.db.commit()


    @commands.Cog.listener("on_message_delete")
    async def GiveawayMessageDelete(self, message):
        cur = await self.bot.db.cursor()
        await cur.execute("SELECT message_id FROM Giveaway WHERE guild_id = ?", (message.guild.id,))
        re = await cur.fetchone()

        if message.author != self.bot.user:
            return
        
        if re is not None:
            if message.id == int(re[0]):
                await cur.execute("DELETE FROM Giveaway WHERE channel_id = ? AND message_id = ? AND guild_id = ?", (message.channel.id, message.id, message.guild.id))

                print(f"Giveaway Message Delete In {message.guild.name} - {message.guild.id}")
                await self.bot.db.commit()

    
    @commands.hybrid_command(name="gend", description="Ends a giveaway. | Reply to the giveaway message or provide ID.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def gend(self, ctx, message_id = None):
        cur = await self.bot.db.cursor()
        if message_id:
            try:
                int(message_id)
            except ValueError: return await ctx.send(f"Invalid message id.")
            
        if message_id is not None:
            current_time = datetime.datetime.now().timestamp()
            await cur.execute('SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id FROM Giveaway WHERE message_id = ?', (int(message_id),))
            re = await cur.fetchone()

            if re is None:
                return await ctx.send(f"Giveaway wasn't found.")
            
            ch = self.bot.get_channel(int(re[6]))
            message = await ch.fetch_message(int(message_id))

            users = [i.id async for i in message.reactions[0].users()]
            users.remove(self.bot.user.id)

            if len(users) < 1:
                await ctx.send(f"Successfully ended the giveaway in <#{int(re[6])}>")
                await message.reply("Very less participants to select the winner.")
                await cur.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
                return
            
            winner = ', '.join(f'<@!{i}>' for i in random.sample(users, k=int(re[4])))

            embed = discord.Embed(
                        description=f"Ended <t:{int(current_time)}:R> <t:{int(current_time)}:t>\nWinners - {winner}\nHosted by <@{int(re[3])}>",
                        color=0xffffff
                    )


            embed.set_author(name=re[5],
                            icon_url=ctx.guild.icon.url)
            embed.set_footer(text=self.bot.user.name,
                            icon_url=self.bot.user.display_avatar.url)

            await message.edit(content=":tada: **Giveaway Ended** :tada:", embed=embed)


            if int(ctx.channel.id) != int(re[6]):
                await ctx.send(f"Successfully ended the giveaway in <#{int(re[6])}>")

            await message.reply(f"Congratulations, {winner} You won **{re[5]}!**")
            await cur.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
            print(f"[Gend] Giveaway Ended - {message.guild.name} ({message.guild.id}) - ({re[5]})")

        elif ctx.message.reference:
            await cur.execute('SELECT ends_at, guild_id, message_id, host_id, winners, prize, channel_id FROM Giveaway WHERE message_id = ?', (ctx.message.reference.resolved.id,))
            re = await cur.fetchone()

            if re is None:
                return await ctx.send(f"{config.Cross} | Giveaway was not found.")
        
            current_time = datetime.datetime.now().timestamp()

            message = await ctx.fetch_message(ctx.message.reference.message_id)

            users = [i.id async for i in message.reactions[0].users()]
            try: users.remove(self.bot.user.id)
            except: pass

            if len(users) < 1:
                await message.reply("Very less participants to select the winner.")
                await cur.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
                return
            
            winner = ', '.join(f'<@!{i}>' for i in random.sample(users, k=int(re[4])))

            embed = discord.Embed(
                        description=f"Ended <t:{int(current_time)}:R> <t:{int(current_time)}:t>\nWinners - {winner}\nHosted by <@{int(re[3])}>",
                        color=0xffffff
                    )


            embed.set_author(name=re[5],
                            icon_url=ctx.guild.icon.url)
            embed.set_footer(text=self.bot.user.name,
                            icon_url=self.bot.user.display_avatar.url)

            await message.edit(content=":tada: **Giveaway Ended** :tada:", embed=embed)


            await message.reply(f"Congratulations, {winner} You won **{re[5]}!**")
            await cur.execute("DELETE FROM Giveaway WHERE message_id = ? AND guild_id = ?", (message.id, message.guild.id))
            print(f"[Gend] Giveaway Ended - {message.guild.name} ({message.guild.id}) - ({re[5]})")
            
        else:
            await ctx.send("Please reply to the giveaway message or provide ID.")
        await self.bot.db.commit()



    @commands.hybrid_command(description="Rerolls a giveaway. | Reply to the giveaway message.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_guild=True))
    async def greroll(self, ctx):
        cur = await self.bot.db.cursor()

        if not ctx.message.reference:
            await ctx.send(f"Reply with a message to reroll.")
            return

        if ctx.message.reference.resolved.author.id != self.bot.user.id:
            await ctx.send(f"Giveaway was not found.")
            return
        
        message = await ctx.fetch_message(ctx.message.reference.resolved.id)

        await cur.execute(f"SELECT message_id FROM Giveaway WHERE message_id = ?", (message.id,))
        re = await cur.fetchone()

        if re is not None:
            await ctx.send(f"That giveaway is running, please use `gend` command instead to end the giveaway.")
            return
        
        users = [i.id async for i in message.reactions[0].users()]
        users.remove(self.bot.user.id)

        if len(users) < 1:
            await message.reply("Very less participants to select the winner.")
            return
        
        winners = random.sample(users, k=1)
        await message.reply(f":tada: Congratulations! "+", ".join(f"<@{i}>" for i in winners)+" You are the new winner!")
        await self.bot.db.commit()






































async def setup(bot):
    await bot.add_cog(Giveaway(bot))

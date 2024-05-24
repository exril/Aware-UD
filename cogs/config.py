import discord
from discord.ext import commands, tasks
import json, traceback, datetime 
from discord import TextChannel, ChannelType, Embed, Role, Member,  Message, User, SelectOption, Interaction, PartialEmoji, PermissionOverwrite
from discord.ext.commands import Cog, Context, group, hybrid_command, hybrid_group, command, AutoShardedBot as AB
from discord.ui import Select, View, Button 
from typing import Union
from aware.checks import Perms as utils, Boosts
from aware.utils import EmbedBuilder, InvokeClass
from aware.utils import EmbedScript
import asyncpg

poj_cache = {} 

class config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_member_join(self, member: Member):
        if member.bot: return   
        results = await self.bot.pg_conn.fetch("SELECT * FROM pingonjoin WHERE guild_id = $1", member.guild.id)
        members = [m for m in member.guild.members if (datetime.datetime.now() - m.joined_at.replace(tzinfo=None)).total_seconds() < 180]
        for result in results: 
         channel = member.guild.get_channel(int(result[0]))
         if channel: 
          if len(members) < 10: 
            try: await channel.send(member.mention, delete_after=6)
            except: continue    
          else:           
           if not poj_cache.get(str(channel.id)): poj_cache[str(channel.id)] = []
           poj_cache[str(channel.id)].append(f"{member.mention}")
           if len(poj_cache[str(channel.id)]) == 10: 
            try: 
             await channel.send(' '.join([m for m in poj_cache[str(channel.id)]]), delete_after=6) 
             poj_cache[str(channel.id)] = []
            except:
             poj_cache[str(channel.id)] = [] 
             continue 
    
    @Cog.listener()
    async def on_message(self, message: Message):
      if not message.guild: return
      if isinstance(message.author, User): return
      if message.author.guild_permissions.manage_guild: return 
      if message.author.bot: return 
      if message.attachments: return       
      check = await self.bot.pg_conn.fetch("SELECT * FROM mediaonly WHERE channel_id = $1", message.channel.id)
      if check: 
        try: await message.delete()
        except: pass 
        
    @group(invoke_without_command=True) 
    async def autopfp(self, ctx: Context):
       await ctx.create_pages()
    
    @autopfp.command(name="clear", description="clear the whole autopfp module", help="config", brief="manage server")
    @utils.get_perms("manage_guild")
    async def autopfp_clear(self, ctx: Context): 
     check = await self.bot.pg_conn.fetch("SELECT * FROM autopfp WHERE guild_id = $1", ctx.guild.id)
     if not check: return await ctx.send("Autopfp module is **not** configured")
     embed = Embed(color=0x6d827d, description="Are you sure you want to clear the autopfps module?")
     yes = Button(emoji="<:greenTick:1230421239634595860>")
     no = Button(emoji="<:redTick:1230421267514003457>")

     async def yes_callback(interaction: Interaction): 
       if interaction.user.id != ctx.author.id: return await self.bot.ext.send(interaction, "You are not the **author** of this embed", ephemeral=True)                                      
       await self.bot.pg_conn.execute("DELETE FROM autopfp WHERE guild_id = $1", ctx.guild.id)
       return await interaction.response.edit_message(embed=Embed(color=0x6d827d, description="Autopfp module cleared"), view=None)
     
     async def no_callback(interaction: Interaction): 
      if interaction.user.id != ctx.author.id: return await self.bot.ext.send(interaction, "You are not the **author** of this embed", ephemeral=True)                                      
      return await interaction.response.edit_message(embed=Embed(color=0x6d827d, description="aborting action..."), view=None)

     yes.callback = yes_callback
     no.callback = no_callback
     view = View()
     view.add_item(yes)
     view.add_item(no)
     return await ctx.reply(embed=embed, view=view) 

    @autopfp.command(name="add", description="add the autopfp module", help="config", usage="[channel] [genre] [type]\nexample: autopfp add #boys male pfp", brief="manage guild") 
    @utils.get_perms("manage_guild")  
    async def autopfp_add(self, ctx: Context, channel: TextChannel, genre: str, typ: str="none"): 
     try: 
      if genre in ["female", "male", "anime"]: 
        if typ in ["pfp", "gif"]:          
          check = await self.bot.pg_conn.execute("SELECT * FROM autopfp WHERE guild_id = $1 AND genre = $2 AND type = $3", ctx.guild.id, genre, typ)                
          if check is not None: return await ctx.send(f"A channel is already **configured** for {genre} {typ}s")
          await self.bot.pg_conn.fetch("INSERT INTO autopfp VALUES ($1,$2,$3,$4)", ctx.guild.id, channel.id, genre, typ)
          return await ctx.send(f"Configured {channel.mention} as {genre} {typ}s")
        else: return await ctx.send("The **type** passed wasn't one of the following: pfp, gif")
      elif genre in ["random", "banner"]: 
          check = await self.bot.pg_conn.fetch("SELECT * FROM autopfp WHERE channel_id = $1 AND guild_id = $2 AND genre = $3", channel.id, ctx.guild.id, genre) 
          if check is not None: return await ctx.send(f"A channel is already **configured** for {genre}")
          await self.bot.pg_conn.execute("INSERT INTO autopfp VALUES ($1,$2,$3,$4)", ctx.guild.id, channel.id, genre, typ)
          return await ctx.send(f"Configured {channel.mention} as {genre} pictures")      
      else: return await ctx.senderror("The **genre** passed wasn't one of the following: male, female, anime, banner, random")
     except: traceback.print_exc()

    @autopfp.command(name="remove", description="remove the autopfp module", help="config", usage="[genre] [type]\nexample: autopfp remove male gif", brief="manage guild")
    @utils.get_perms("manage_guild")
    async def autopfp_remove(self, ctx: Context, genre: str, typ: str="none"):
       try:  
        check = await self.bot.pg_conn.fetch("SELECT * FROM autopfp WHERE guild_id = $1 AND genre = $2 AND type = $3", ctx.guild.id, genre, typ)                
        if check is None: return await ctx.send(f"No autopfp channel found for **{genre} {typ if typ != 'none' else ''}**")
        await self.bot.pg_conn.execute("DELETE FROM autopfp WHERE guild_id = $1 AND genre = $2 AND type = $3", ctx.guild.id, genre, typ)                
        await ctx.send(f"Removed **{genre} {typ if typ != 'none' else ''}** posting")
       except: traceback.print_exc()

    @group(invoke_without_command=True)
    async def mediaonly(self, ctx: Context):
     await ctx.create_pages()

    @mediaonly.command(name="add", description="delete messages that are not images", help="config", usage="[channel]", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def mediaonly_add(self, ctx: Context, *, channel: TextChannel):
        check = await self.bot.pg_conn.fetch("SELECT * FROM mediaonly WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check is not None: return await ctx.send(f"{channel.mention} is already added")
        elif check is None: 
          await self.bot.pg_conn.execute("INSERT INTO mediaonly VALUES ($1,$2)", ctx.guild.id, channel.id)
          return await ctx.send(f"added {channel.mention} as a mediaonly channel")

    @mediaonly.command(name="remove", description="unset media only", help="config", usage="[channel]", brief="manage_guild") 
    @utils.get_perms("manage_guild")
    async def mediaonly_remove(self, ctx: Context, *, channel: TextChannel=None):
     if channel is not None: 
      check = await self.bot.pg_conn.fetch("SELECT * FROM mediaonly WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
      if check is None: return await ctx.send(f"{channel.mention} is not added") 
      await self.bot.pg_conn.execute("DELETE FROM mediaonly WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
      return await ctx.send(f"{channel.mention} isn't a **mediaonly** channel anymore")

     res = await self.bot.pg_conn.fetch("SELECT * FROM mediaonly WHERE guild_id = $1", ctx.guild.id) 
     if res is None: return await ctx.send("There is no **mediaonly** channel in this server")
     await self.bot.pg_conn.fetch("DELETE FROM mediaonly WHERE guild_id = $1", ctx.guild.id)
     return await ctx.send("Removed all channels") 

    @mediaonly.command(name="list", description="return a list of mediaonly channels", help="config")
    async def mediaonly_list(self, ctx: Context): 
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          results = await self.bot.pg_conn.fetch("SELECT * FROM mediaonly WHERE guild_id = {}".format(ctx.guild.id))
          if len(results) == 0: return await ctx.reply("there are no mediaonly channels")
          for result in results:
              mes = f"{mes}`{k}` <#{result['channel_id']}> ({result['channel_id']})\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=0x6d827d, title=f"mediaonly channels ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
          messages.append(mes)
          number.append(Embed(color=0x6d827d, title=f"mediaonly channels ({len(results)})", description=messages[i])) 
          if len(number) > 1: return await ctx.paginator(number) 
          return await ctx.send(embed=number[0])
    
    @hybrid_group(invoke_without_command=True, aliases=["poj"])
    async def pingonjoin(self, ctx): 
      await ctx.create_pages()

    @pingonjoin.command(name="add", description="ping new members when they join your server", help="config", usage="[channel]", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def poj_add(self, ctx: Context, *, channel: TextChannel): 
        check = await self.bot.pg_conn.fetch("SELECT * FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check is not None: return await ctx.send(f"{channel.mention} is already added")
        elif check is None: await self.bot.pg_conn.execute("INSERT INTO pingonjoin VALUES ($1,$2)", channel.id, ctx.guild.id)
        return await ctx.send(f"I will ping new members in {channel.mention}")  
    
    @pingonjoin.command(name="remove", description="remove a pingonjoin channel", help="config", usage="<channel>", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def poj_remove(self, ctx: Context, *, channel: TextChannel=None): 
      if channel is not None: 
        check = await self.bot.pg_conn.self.bot.pg_conn("SELECT * FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        if check is None: return await ctx.senderror(f"{channel.mention} is not added")
        elif check is not None: await self.bot.pg_conn.execute("DELETE FROM pingonjoin WHERE guild_id = $1 AND channel_id = $2", ctx.guild.id, channel.id)
        return await ctx.send(f"I will not ping new members in {channel.mention}")

      check = await self.bot.pg_conn.execute("SELECT * FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
      if check is None: return await ctx.senderror("there is no channel added")
      elif check is not None:  await self.bot.pg_conn.execute("DELETE FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
      return await ctx.send("I will not ping new members in any channel") 
    
    @pingonjoin.command(name="list", description="get a list of pingonjoin channels", help="config")
    async def poj_list(self, ctx: Context): 
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          results = await self.bot.pg_conn.fetch("SELECT * FROM pingonjoin WHERE guild_id = {}".format(ctx.guild.id))
          if results is None: return await ctx.senderror("there are no pingonjoin channels")
          for result in results:
              mes = f"{mes}`{k}` {ctx.guild.get_channel(int(result['channel_id'])).mention if ctx.guild.get_channel(result['channel_id']) else result['channel_id']}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=0x6d827d, title=f"pingonjoin channels ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
          messages.append(mes)
          number.append(Embed(color=0x6d827d, title=f"pingonjoin channels ({len(results)})", description=messages[i]))
          await ctx.paginator(number)
    
    @group(invoke_without_command=True)
    async def starboard(self, ctx): 
      await ctx.create_pages()

    @starboard.command(help="config", description="modify the starboard count", brief="manage guild", usage="[count]", aliases=["amount"])
    @utils.get_perms("manage_guild")
    async def count(self, ctx: Context, count: int):
      if count < 1: return await ctx.send("Count can't be **less** than 1")
      check = await self.bot.pg_conn.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
      if check is None: await self.bot.pg_conn.execute("INSERT INTO starboard (guild_id, count) VALUES ($1, $2)", ctx.guild.id, count)
      else: await self.bot.pg_conn.execute("UPDATE starboard SET count = $1 WHERE guild_id = $2", count, ctx.guild.id)
      await ctx.send(f"Starboard **count** set to **{count}**")  
    
    @starboard.command(name="channel", help="config", description="configure the starboard channel", brief="manage guild", usage="[channel]")
    @utils.get_perms("manage_guild")
    async def starboard_channel(self, ctx: Context, *, channel: TextChannel): 
      check = await self.bot.pg_conn.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
      if check is None: await self.bot.pg_conn.execute("INSERT INTO starboard (guild_id, channel_id) VALUES ($1, $2)", ctx.guild.id, channel.id)
      else: await self.bot.pg_conn.execute("UPDATE starboard SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
      await ctx.send(f"Starboard **channel** set to {channel.mention}")

    @starboard.command(name="emoji", help="config", description="configure the starboard emoji", brief="manage guild", usage="[emoji]")
    @utils.get_perms("manage_guild")
    async def starboard_emoji(self, ctx: Context, emoji: Union[PartialEmoji, str]): 
     check = await self.bot.pg_conn.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     emoji_id = emoji.id if isinstance(emoji, PartialEmoji) else ord(str(emoji)) 
     if check is None: await self.bot.pg_conn.execute("INSERT INTO starboard (guild_id, emoji_id, emoji_text) VALUES ($1,$2,$3)", ctx.guild.id, emoji_id, str(emoji)) 
     else: 
      await self.bot.pg_conn.execute("UPDATE starboard SET emoji_id = $1 WHERE guild_id = $2", emoji_id, ctx.guild.id)
      await self.bot.pg_conn.execute("UPDATE starboard SET emoji_text = $1 WHERE guild_id = $2", str(emoji), ctx.guild.id) 
     await ctx.send(f"Starboard **emoji** set to {emoji}") 

    @starboard.command(name="remove", help="config", description="remove starboard", brief="manage guild", aliases=["disable"])
    @utils.get_perms("manage_guild")
    async def starboard_remove(self, ctx: Context): 
     check = await self.bot.pg_conn.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.send("Starboard is not **enabled**") 
     await self.bot.pg_conn.execute("DELETE FROM starboard WHERE guild_id = $1", ctx.guild.id)
     await self.bot.pg_conn.execute("DELETE FROM starboardmes WHERE guild_id = $1", ctx.guild.id)
     await ctx.send("Disabled starboard **succesfully**")

    @starboard.command(help="config", description="check starboard stats", aliases=["settings", "status"])
    async def stats(self, ctx: Context): 
     check = await self.bot.pg_conn.fetchrow("SELECT * FROM starboard WHERE guild_id = $1", ctx.guild.id)
     if check is None: return await ctx.send("Starboard is not **enabled**") 
     embed = Embed(color=0x6d827d, title="starboard settings")
     if ctx.guild.get_channel(int(check["channel_id"])): embed.add_field(name="channel", value=ctx.guild.get_channel(int(check["channel_id"])).mention)
     if check["count"]: embed.add_field(name="amount", value=check["count"])
     if check["emoji_text"]: embed.add_field(name="emoji", value=check["emoji_text"])
     await ctx.reply(embed=embed)
  

    @group(invoke_without_command=True)
    async def bumpreminder(self, ctx): 
     await ctx.create_pages() 
    
    @bumpreminder.command(name="add", help="config", description="reminder to bump your server via disboard", brief="manage guild")
    @utils.get_perms("manage_guild")
    async def bumpreminder_add(self, ctx: Context):
       check = await self.bot.pg_conn.fetchrow("SELECT * FROM bumps WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is not None: return await ctx.send("bump reminder is already enabled".capitalize())
       await self.bot.pg_conn.execute("INSERT INTO bumps VALUES ($1, $2)", ctx.guild.id, "true")
       return await ctx.send("bump reminder is now enabled".capitalize())
    
    @bumpreminder.command(name="remove", help="config", description="remove bump reminder", brief="manage guild")
    @utils.get_perms("manage_guild")
    async def bumpreminder_remove(self, ctx: Context):  
       check = await self.bot.pg_conn.fetchrow("SELECT * FROM bumps WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is None: return await ctx.send("bump reminder isn't enabled".capitalize())
       await self.bot.pg_conn.execute("DELETE FROM bumps WHERE guild_id = {}".format(ctx.guild.id))
       return await ctx.send("bump reminder is now disabled".capitalize())  

    @hybrid_group(invoke_without_command=True)
    async def confessions(self, ctx): 
      await ctx.create_pages()
    
    @confessions.command(name="mute", description="mute a member that send a specific confession", usage="[confession number]", brief="manage messages")
    @utils.get_perms("manage_messages")
    async def confessions_mute(self, ctx: Context, *, number: int): 
     check = await self.bot.pg_conn.fetchrow("SELECT channel_id FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
     if check is None: return await ctx.send("Confessions aren't **enabled** in this server") 
     re = await self.bot.pg_conn.fetchrow("SELECT * FROM confess_members WHERE guild_id = $1 AND confession = $2", ctx.guild.id, number)
     if re is None: return await ctx.send("Couldn't find that confession")
     member_id = re['user_id']
     r = await self.bot.pg_conn.fetchrow("SELECT * FROM confess_mute WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member_id)
     if r: return await ctx.send("This **member** is **already** confession muted")
     await self.bot.pg_conn.execute("INSERT INTO confess_mute VALUES ($1,$2)", ctx.guild.id, member_id)
     return await ctx.send(f"The author of confession #{number} is muted") 
    
    @confessions.command(name="unmute", description="unmute a member that send a specific confession", usage="[confession count | all (unmutes all members)]", brief="manage messages")
    @utils.get_perms("manage_messages")
    async def connfessions_unmute(self, ctx: Context, *, number: str): 
      check = await self.bot.pg_conn.fetchrow("SELECT channel_id FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
      if check is None: return await ctx.send("Confessions aren't **enabled** in this server")  
      if number == "all": 
       await self.bot.pg_conn.execute("DELETE FROM confess_mute WHERE guild_id = $1", ctx.guild.id)
       return await ctx.send("Unmuted **all** confession muted authors") 
      num = int(number)
      re = await self.bot.pg_conn.fetchrow("SELECT * FROM confess_members WHERE guild_id = $1 AND confession = $2", ctx.guild.id, num)
      if re is None: return await ctx.send("Couldn't find that confession")
      member_id = re['user_id']
      r = await self.bot.pg_conn.fetchrow("SELECT * FROM confess_mute WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member_id)
      if not r: return await ctx.send("This **member** is **not** confession muted")
      await self.bot.pg_conn.execute("DELETE FROM confess_mute WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member_id)
      return await ctx.send(f"Unmuted the author of confession #{number}") 
    
    @confessions.command(name="add", description="set confession channel", help="config", usage="[channel]", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def confessions_add(self, ctx: Context, *, channel: TextChannel): 
       check = await self.bot.pg_conn.fetchrow("SELECT * FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is not None: await self.bot.pg_conn.execute("UPDATE confess SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
       elif check is None: await self.bot.pg_conn.execute("INSERT INTO confess VALUES ($1,$2,$3)", ctx.guild.id, channel.id, 0)
       return await ctx.send(f"confession channel set to {channel.mention}".capitalize())
    
    @confessions.command(name="remove", description="remove confession channel", help="config", brief="manage_guild")
    @utils.get_perms("manage_guild")
    async def confessions_remove(self, ctx: Context): 
       check = await self.bot.pg_conn.fetchrow("SELECT channel_id FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is None: return await ctx.send("Confessions aren't **enabled** in this server")
       await self.bot.pg_conn.execute("DELETE FROM confess WHERE guild_id = {}".format(ctx.guild.id))
       await self.bot.pg_conn.execute("DELETE FROM confess_members WHERE guild_id = {}".format(ctx.guild.id))
       await self.bot.pg_conn.execute("DELETE FROM confess_mute WHERE guild_id = {}".format(ctx.guild.id))
       return await ctx.send("Confessions disabled")
    
    @confessions.command(name="channel", description="get the confessions channel", help="config")
    async def confessions_channel(self, ctx: Context): 
       check = await self.bot.pg_conn.fetchrow("SELECT * FROM confess WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is not None:
        channel = ctx.guild.get_channel(check['channel_id'])   
        embed = Embed(color=0x6d827d, description=f"confession channel: {channel.mention}\nconfessions sent: **{check['confession']}**")
        return await ctx.reply(embed=embed)
       return await ctx.send("Confessions aren't **enabled** in this server")

  
    @command(help="config", description="react to a message using the bot", brief="manage messages", usage="[message id / message link] [emoji]")
    @utils.get_perms("manage_messages")
    async def react(self, ctx: Context, link: str, reaction: str):
     try: mes = await ctx.channel.fetch_message(int(link))
     except: mes = None
     if mes: 
      try:
       await mes.add_reaction(reaction)  
       view = View()
       view.add_item(Button(label="jump to message", url=mes.jump_url))
       return await ctx.reply(view=view)
      except: return await ctx.send("Unable to add the reaction to that message") 
     message = await self.bot.ext.link_to_message(link)
     if not message: return await ctx.send("No **message** found")
     if message.guild != ctx.guild: return await ctx.send("This **message** is not from this server")
     elif message.channel.type != ChannelType.text: return await ctx.senderror("I can only react in text channels")
     try: 
      await message.add_reaction(reaction)
      v = View()
      v.add_item(Button(label="jump to message", url=message.jump_url))
      return await ctx.reply(view=v)  
     except: return await ctx.send("Unable to add the reaction to that message") 
    
    @group(invoke_without_command=True, name="counter", help="config", description="create stats counters for your server")
    async def counter(self, ctx: Context): 
      await ctx.create_pages()
    
    @counter.command(name="types", description="check the counter types and channel types")
    async def counter_types(self, ctx: Context):
      embed1 = Embed(color=0x6d827d, title="counter types")
      embed2 = Embed(color=0x6d827d, title="channel types")
      embed1.description = """>>> members - all members from the server (including bots)
      humans - all members from the server (excluding bots)
      bots - all bots from the server
      boosters - all server boosters
      voice - all members in the server's voice channels
      """
      embed2.description = """>>> voice - creates voice channel
      stage - creates stage channel 
      text - createss text channel
      """
      await ctx.paginator([embed1, embed2])

    @counter.command(name="list", help="config", description="check a list of the active server counters")
    async def counter_list(self, ctx: Context): 
          i=0
          k=1
          l=0
          mes = ""
          number = []
          messages = []
          results = await self.bot.pg_conn.fetch("SELECT * FROM counters WHERE guild_id = {}".format(ctx.guild.id))
          if not results: return await ctx.send("There are no counters")
          for result in results:
              mes = f"{mes}`{k}` {result['module']} -> {ctx.guild.get_channel(int(result['channel_id'])).mention if ctx.guild.get_channel(int(result['channel_id'])) else result['channel_id']}\n"
              k+=1
              l+=1
              if l == 10:
               messages.append(mes)
               number.append(Embed(color=0x6d827d, title=f"server counters ({len(results)})", description=messages[i]))
               i+=1
               mes = ""
               l=0
    
          messages.append(mes)
          number.append(Embed(color=0x6d827d, title=f"server counters ({len(results)})", description=messages[i]))
          return await ctx.paginator(number) 

    @counter.command(name="remove", help="config", description="remove a counter from the server", brief="manage guild", usage="[counter type]")
    @utils.get_perms("manage_guild")
    async def counter_remove(self, ctx: Context, countertype: str): 
     if not countertype in ["members", "voice", "boosters", "humans", "bots"]: return await ctx.send(f"**{countertype}** is not an **available** counter") 
     check = await self.bot.pg_conn.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, countertype)
     if not check: return await ctx.send(f"There is no **{countertype}** counter in this server")
     channel = ctx.guild.get_channel(int(check["channel_id"]))
     if channel: await channel.delete()
     await self.bot.pg_conn.execute("DELETE FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, countertype)
     return await ctx.send(f"Removed **{countertype}** counter")
    
    @counter.group(invoke_without_command=True, name="add", help="config", description="add a counter to the server", brief="manage guild")
    async def counter_add(self, ctx: Context): 
      await ctx.create_pages()

    @counter_add.command(name="members", help="config", description="add a counter for member count", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add members voice {target} Members")
    @utils.get_perms("manage_guild")
    async def counter_add_members(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send("{target} variable is **missing** from the channel name")
     check = await self.bot.pg_conn.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send(f"<#{check['channel_id']}> is already a **member** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating member counter"
     name = message.replace("{target}", str(ctx.guild.member_count))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(sendmessages=False)})
     await self.bot.pg_conn.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send(f"Created **member** counter -> {channel.mention}")  

    @counter_add.command(name="humans", help="config", description="add a counter for humans", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add humans voice {target} humans")
    @utils.get_perms("manage_guild")
    async def counter_add_humans(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send("{target} variable is **missing** from the channel name")
     check = await self.bot.pg_conn.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send(f"<#{check['channel_id']}> is already a **humans** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating human counter"
     name = message.replace("{target}", str(len([m for m in ctx.guild.members if not m.bot])))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(sendmessages=False)})
     await self.bot.pg_conn.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send(f"Created **humans** counter -> {channel.mention}")  

    @counter_add.command(name="bots", help="config", description="add a counter for bots", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add bots voice {target} bots")
    @utils.get_perms("manage_guild")
    async def counter_add_bots(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send("{target} variable is **missing** from the channel name")
     check = await self.bot.pg_conn.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send(f"<#{check['channel_id']}> is already a **bots** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating bot counter"
     name = message.replace("{target}", str(len([m for m in ctx.guild.members if m.bot])))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(sendmessages=False)})
     await self.bot.pg_conn.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send(f"Created **bots** counter -> {channel.mention}")  

    @counter_add.command(name="voice", help="config", description="add a counter for voice members", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add voice stage {target} in vc")         
    @utils.get_perms("manage_guild")
    async def counter_add_voice(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send("{target} variable is **missing** from the channel name")
     check = await self.bot.pg_conn.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send(f"<#{check['channel_id']}> is already a **voice** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating voice counter"
     name = message.replace("{target}", str(sum(len(c.members) for c in ctx.guild.voice_channels)))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(sendmessages=False)})
     await self.bot.pg_conn.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send(f"Created **voice** counter -> {channel.mention}")  

    @counter_add.command(name="boosters", help="config", description="add a counter for boosters", brief="manage guild", usage="[channel type] <channel name>\nexample: ;counter add boosters voice {target} boosters") 
    @utils.get_perms("manage_guild")
    async def counter_add_boosters(self, ctx: Context, channeltype: str, *, message: str="{target}"): 
     if not channeltype in ["voice", "text", "stage"]: return await ctx.send(f"**{channeltype}** is not a **valid** channel type")     
     if not "{target}" in message: return await ctx.send("{target} variable is **missing** from the channel name")
     check = await self.bot.pg_conn.fetchrow("SELECT * FROM counters WHERE guild_id = $1 AND module = $2", ctx.guild.id, ctx.command.name)
     if check: return await ctx.send(f"<#{check['channel_id']}> is already a **booster** counter")
     overwrites={ctx.guild.default_role: PermissionOverwrite(connect=False)}
     reason="creating booster counter"
     name = message.replace("{target}", str(len(ctx.guild.premium_subscribers)))
     if channeltype == "stage": channel = await ctx.guild.create_stage_channel(name=name, overwrites=overwrites, reason=reason)
     elif channeltype == "voice": channel = await ctx.guild.create_voice_channel(name=name, overwrites=overwrites, reason=reason)
     else: channel = await ctx.guild.create_text_channel(name=name, reason=reason, overwrites={ctx.guild.default_role: PermissionOverwrite(sendmessages=False)})
     await self.bot.pg_conn.execute("INSERT INTO counters VALUES ($1,$2,$3,$4,$5)", ctx.guild.id, channeltype, channel.id, message, ctx.command.name)
     await ctx.send(f"Created **boosters** counter -> {channel.mention}")
     
async def setup(bot): 
    await bot.add_cog(config(bot))        

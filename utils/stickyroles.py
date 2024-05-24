import discord
from discord.ext import commands
from discord import Webhook
from typing import Union, Optional
import re
import sqlite3
import asyncio
from ast import literal_eval
from botinfo import *
from paginators import PaginationView, PaginatorView
from cogs.premium import check_upgraded
import datetime

xdd = {}
async def getrole(guild_id):
    if guild_id not in xdd:
        return 0
    else:
        return xdd[guild_id]

async def updaterole(guild_id, role_id):
    xdd[guild_id] = role_id
    return True

async def delrole(guild_id):
    del xdd[guild_id]
    return True

class roledropdownmenu(discord.ui.RoleSelect):
    def __init__(self, ctx: commands.Context):
        super().__init__(placeholder="Select the role",
            min_values=1,
            max_values=25,
        )
        self.ctx = ctx
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False, thinking=False)
        ls = []
        for i in self.values:
            ls.append(i.id)
        await updaterole(self.ctx.guild.id, ls)
        self.view.stop()

class rolemenuview(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.add_item(roledropdownmenu(self.ctx))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in  [978930369392951366, 979353019235840000]:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="All roles", custom_id='No', style=discord.ButtonStyle.green   )
    async def truth(self, interaction, button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        self.value = 'all'
        self.stop()
    
class stickyroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0xc283fe

    @commands.group(invoke_without_command=True, name="stickyroles", aliases=['stickyrole', 'sticky'], description="Show's the help menu for sticky roles")
    async def stickyroles(self, ctx: commands.Context):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = discord.utils.get(self.bot.users, id=978930369392951366)
        ls = ["sticky", "sticky add", "sticky remove", "sticky list"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            if cmd.description is None:
                cmd.description = "No Description"
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"<:sticky_roles:1047229547168415784> Sticky Roles Commands", colour=0xc283fe,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by stars.gg" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)

    @stickyroles.command(name="list", description="Shows you current sticky roles in the server")
    @commands.has_guild_permissions(administrator=True)
    async def _list(self, ctx: commands.Context):
        c = await check_upgraded(ctx.guild.id)
        if ctx.author.id == ctx.guild.owner.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in  [978930369392951366, 979353019235840000]:
                em = discord.Embed(description=f"<:error:1153009680428318791>You must Have Higher Role than Bot To run This Command", color=0xff0000)
                return await ctx.send(embed=em)
        query = "SELECT * FROM  main WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./sticky.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query, val)
            self_db = cursor1.fetchone()
        no_ = discord.Embed(description=f"There are no sticky roles in the server", color=0xc283fe)
        if self_db is None:
            return await ctx.reply(embed=no_)
        else:
            a = self_db["all"]
            ls = literal_eval(self_db['roles'])
            lsb = literal_eval(self_db['blroles'])
            if ls == "[]" and a == 0:
                return await ctx.reply(embed=no_)
            if a == 1:
                lss = []
                for i in lsb:
                    r = discord.utils.get(ctx.guild.roles, id=i)
                    if r is not None:
                        if r.is_assignable():
                            lss.append(r.mention)
                ok = 0
                for i in ctx.guild.roles:
                    r = discord.utils.get(ctx.guild.roles, id=i.id)
                    if r is not None:
                        if r.is_assignable():
                            ok +=1
                c = ok - len(lss)
                em = discord.Embed(title=f"Sticky roles for {ctx.guild.name} - {c}", color=0xc283fe)
                if len(lss) != 0:
                    s = ','.join(lss)
                    des = f"All roles in the server below me are sticky roles except {s} role(s)"
                else:
                    des = f"All roles in the server below me are sticky roles"
                em.description = des
                return await ctx.reply(embed=em)
            else:
                lss = []
                for i in ls:
                    if i not in lsb:
                        r = discord.utils.get(ctx.guild.roles, id=i)
                        if r is not None:
                            lss.append(r.mention)
                c = len(lss)
                em = discord.Embed(title=f"Sticky roles for {ctx.guild.name} - {c}", color=0xc283fe)
                if lss != "[]":
                    s = '\n'.join(lss)
                    des = f"{s}"
                else:
                    return await ctx.reply(embed=no_)
                em.description = des
                return await ctx.reply(embed=em)

    @stickyroles.command(name="add", description="Adds a sticky roles in the server")
    @commands.has_guild_permissions(administrator=True)
    async def _add(self, ctx: commands.Context, *, role: discord.Role=None):
        c = await check_upgraded(ctx.guild.id)
        if ctx.author.id == ctx.guild.owner.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in  [978930369392951366, 979353019235840000]:
                em = discord.Embed(description=f"<:error:1153009680428318791>You must Have Higher Role than Bot To run This Command", color=0xff0000)
                return await ctx.send(embed=em)
        query = "SELECT * FROM  main WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./sticky.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query, val)
            self_db = cursor1.fetchone()
        a = 0
        if self_db is None:
            ls = []
            lsb = []
        else:
            ls = literal_eval(self_db['roles'])
            lsb = literal_eval(self_db['blroles'])
            if self_db['all'] == 1 and len(lsb) == 0:
                em = discord.Embed(description=f"All roles in the server are already added as sticky roles", color=0xc283fe)
                return await ctx.reply(embed=em)
        if role is not None:
            if role.id in ls:
                em = discord.Embed(description=f"{role.mention} is already a sticky role in the server", color=0xc283fe)
                return await ctx.reply(embed=em)
            else:
                ls.append(role.id)
                if role.id in lsb:
                    lsb.remove(role.id)
                em = discord.Embed(description=f"Successfully added {role.mention} as a sticky role", color=0xc283fe)
                await ctx.send(embed=em)
        else:
            v = rolemenuview(ctx)
            init = await ctx.reply(embed=discord.Embed(description=f"Select the role as sticky roles\nIf you can't see any role in the dropdown, type its name in the dropdown selection box.", color=0xc283fe), view=v)
            await v.wait()
            x = await getrole(ctx.guild.id)
            if x == 0:
                if v.value is None:
                    await init.delete()
                    return
                else:
                    em = discord.Embed(description=f"Successfully added all roles as sticky roles in the server", color=0xc283fe)
                    await init.edit(embed=em, view=None)
                    a = 1
                    ls = []
                    lsb = []
            else:
                xxxx = []
                for i in x:
                    if i in lsb:
                        lsb.remove(i)
                    r = discord.utils.get(ctx.guild.roles, id=i)
                    xxxx.append(r.mention)
                xx = ','.join(xxxx)
                em = discord.Embed(description=f"Successfully added {xx} as sticky roles in the server", color=0xc283fe)
                await init.edit(embed=em, view=None)
                ls.append(x)
        if self_db is None:
            sql = (f"INSERT INTO main(guild_id, 'all', 'roles', 'blroles', 'data') VALUES(?, ?, ?, ?, ?)")
            val = (ctx.guild.id, a, f"{ls}", f"{lsb}", "{}",)
            cursor1.execute(sql, val)
        else:
            sql = (f"UPDATE 'main' SET 'all' = ? WHERE guild_id = ?")
            val = (a, ctx.guild.id)
            cursor1.execute(sql, val)
            sql = (f"UPDATE 'main' SET 'roles' = ? WHERE guild_id = ?")
            val = (f"{ls}", ctx.guild.id)
            cursor1.execute(sql, val)
            sql = (f"UPDATE 'main' SET 'blroles' = ? WHERE guild_id = ?")
            val = (f"{lsb}", ctx.guild.id)
            cursor1.execute(sql, val)
        db1.commit()
        cursor1.close()
        db1.close()

    @stickyroles.command(name="remove", description="Remove a sticky role(s) in the server")
    @commands.has_guild_permissions(administrator=True)
    async def _remove(self, ctx: commands.Context, *, role: discord.Role=None):
        c = await check_upgraded(ctx.guild.id)
        if ctx.author.id == ctx.guild.owner.id:
            pass
        else:
            if ctx.author.top_role.position <= ctx.guild.me.top_role.position and ctx.author.id not in  [978930369392951366, 979353019235840000]:
                em = discord.Embed(description=f"<:error:1153009680428318791>You must Have Higher Role than Bot To run This Command", color=0xff0000)
                return await ctx.send(embed=em)
        query = "SELECT * FROM  main WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./sticky.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query, val)
            self_db = cursor1.fetchone()
        if self_db is None:
            em = discord.Embed(description=f"No roles in the server are added as sticky roles", color=0xc283fe)
            return await ctx.reply(embed=em)
        else:
            a = self_db["all"]
            ls = literal_eval(self_db['roles'])
            lsb = literal_eval(self_db['blroles'])
            if ls == "[]" and self_db['all'] == 0:
                em = discord.Embed(description=f"No roles in the server are added as sticky roles", color=0xc283fe)
                return await ctx.reply(embed=em)
            if role is not None:
                if role.id in lsb:
                    em = discord.Embed(description=f"{role.mention} is not added as sticky roles", color=0xc283fe)
                    return await ctx.reply(embed=em)
                if self_db['all'] == 1:
                    lsb.append(role.id)
                else:
                    if role.id in ls:
                        ls.remove(role.id)
                        lsb.append(role.id)
                    else:
                        lsb.append(role.id)
                em = discord.Embed(description=f"Successfully removed {role.mention} from sticky roles of the server", color=0xc283fe)
                await ctx.reply(embed=em)
            else:
                v = rolemenuview(ctx)
                init = await ctx.reply(embed=discord.Embed(description=f"Select the role to remove from sticky roles\nIf you can't see any role in the dropdown, type its name in the dropdown selection box.", color=0xc283fe), view=v)
                await v.wait()
                x = await getrole(ctx.guild.id)
                if x == 0:
                    if v.value is None:
                        await init.delete()
                        return
                    else:
                        em = discord.Embed(description=f"Successfully removed all roles from sticky roles in the server", color=0xc283fe)
                        await init.edit(embed=em, view=None)
                        a = 0
                        ls = []
                        lsb = []
                else:
                    xxxx = []
                    for i in x:
                        if i in ls:
                            ls.remove(i)
                        if i not in lsb:
                            lsb.append(i)
                        r = discord.utils.get(ctx.guild.roles, id=i)
                        xxxx.append(r.mention)
                    xx = ','.join(xxxx)
                    em = discord.Embed(description=f"Successfully removed {xx} from sticky roles in the server", color=0xc283fe)
                    await init.edit(embed=em, view=None)
        if self_db is None:
            pass
        else:
            sql = (f"UPDATE 'main' SET 'all' = ? WHERE guild_id = ?")
            val = (a, ctx.guild.id)
            cursor1.execute(sql, val)
            sql = (f"UPDATE 'main' SET 'roles' = ? WHERE guild_id = ?")
            val = (f"{ls}", ctx.guild.id)
            cursor1.execute(sql, val)
            sql = (f"UPDATE 'main' SET 'blroles' = ? WHERE guild_id = ?")
            val = (f"{lsb}", ctx.guild.id)
            cursor1.execute(sql, val)
        db1.commit()
        cursor1.close()
        db1.close()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.guild:
            return
        if member.bot:
            return
        if member.guild.me.guild_permissions.manage_roles:
            p = True
        else:
            p = False
        query = "SELECT * FROM  main WHERE guild_id = ?"
        val = (member.guild.id,)
        with sqlite3.connect('./sticky.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query, val)
            self_db = cursor1.fetchone()
        if self_db is None:
            return
        else:
            a = self_db["all"]
            ls = literal_eval(self_db['roles'])
            lsb = literal_eval(self_db['blroles'])
            data = literal_eval(self_db['data'])
            if ls == "[]" and a == 0:
                return
            if member.id not in data:
                return
            if member.id in data:
                if data[member.id] == "[]":
                    del data[member.id]
                else:
                    for i in data[member.id]:
                        if a == 1:
                            if i not in lsb:
                                r = discord.utils.get(member.guild.roles, id=i)
                                if p and r is not None:
                                    if r.is_assignable():
                                        await member.add_roles(r, reason=f"Sticky Roles")
                        else:
                            if i in ls and i not in lsb:
                                r = discord.utils.get(member.guild.roles, id=i)
                                if p and r is not None:
                                    if r.is_assignable():
                                        await member.add_roles(r, reason=f"Sticky Roles")
                del data[member.id]
            sql = (f"UPDATE 'main' SET 'data' = ? WHERE guild_id = ?")
            val = (f"{data}", member.guild.id)
            cursor1.execute(sql, val)
        db1.commit()
        cursor1.close()
        db1.close()
        query = "SELECT * FROM  'muteroles' WHERE guild_id = ?"
        val = (member.guild.id,)
        with sqlite3.connect('./muterole.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is None:
            return
        else:
            xd = literal_eval(m_db['muterole'])
            if len(xd) == 1:
                role = discord.utils.get(member.guild.roles, id=xd[0])
                if role is None:
                    return
                else:
                    if role in member.roles:
                        await member.remove_roles(role, reason="Reassigning mute role")
                        await asyncio.sleep(5)
                        await member.add_roles(role, reason="Reassigning mute role")
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if not member.guild:
            return
        if member.bot:
            return
        query = "SELECT * FROM  main WHERE guild_id = ?"
        val = (member.guild.id,)
        with sqlite3.connect('./sticky.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query, val)
            self_db = cursor1.fetchone()
        if self_db is None:
            return
        else:
            a = self_db["all"]
            ls = literal_eval(self_db['roles'])
            lsb = literal_eval(self_db['blroles'])
            data = literal_eval(self_db['data'])
            if ls == "[]" and a == 0:
                return
        kick = False
        if member.guild.me.guild_permissions.view_audit_log:
            async for entry in member.guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(seconds=3),
                action=discord.AuditLogAction.kick):
                x = datetime.datetime.now() - datetime.timedelta(seconds=10)
                if entry.target.id == member.id and x.timestamp() <= entry.created_at.timestamp():
                    kick = True
        if not kick:
            lss = []
            for i in member.roles:
                if a == 1:
                    if i.id not in lsb:
                        lss.append(i.id)
                else:
                    if i.id in ls and i.id not in lsb:
                        lss.append(i.id)
            data[member.id] = lss
            sql = (f"UPDATE 'main' SET 'data' = ? WHERE guild_id = ?")
            val = (f"{data}", member.guild.id)
            cursor1.execute(sql, val)
        db1.commit()
        cursor1.close()
        db1.close()

async def setup(bot):
	await bot.add_cog(stickyroles(bot))
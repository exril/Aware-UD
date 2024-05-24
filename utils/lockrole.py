from re import I
import discord
import datetime
from discord.ext import commands, tasks
from ast import literal_eval
import sqlite3
from cogs.premium import check_upgraded
from paginators import PaginationView, PaginatorView

class lockrole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        invoke_without_command=True, description="Shows the help menu for lockrole commands"
    )
    async def lockrole(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = discord.utils.get(self.bot.users, id=978930369392951366)
        ls = ["lockrole", "lockrole add", "lockrole remove", "lockrole wluser add", "lockrole wluser remove", "lockrole wlrole add", "lockrole wlrole remove", "lockrole config"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"<:gateway_security:1041631826625691669> Lockrole Commands", colour=0xc283fe,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by stars.gg" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)
    
    @lockrole.command(name="config", description="Shows the settings for locked roles in the server")
    @commands.has_guild_permissions(administrator=True)
    async def r_config(self, ctx: commands.Context):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/6Q9D7R8hYc)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/6Q9D7R8hYc"))
            return await ctx.reply(embed=em, view=v)
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"There are no locked roles for this server"))
        if rl_db['role_id'] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"There are no locked roles for this server"))
        em = discord.Embed(title=f"Locked Roles settings for the server", color=0xc283fe)
        br_id = literal_eval(rl_db['role_id'])
        lr = []
        for i in br_id:
            r = discord.utils.get(ctx.guild.roles, id=i)
            try:
                lr.append(r.mention)
            except:
                pass
        em.add_field(name="Locked Roles:", value="\n".join(lr), inline=False)
        u_id = literal_eval(rl_db['bypass_uid'])
        um = []
        for i in u_id:
            u = discord.utils.get(ctx.guild.members, id=i)
            try:
                um.append(u.mention)
            except:
                pass
        if len(um) == 0:
            em.add_field(name="Whitelisted Users", value="No Users are whitelisted", inline=False)
        else:
            em.add_field(name="Whitelisted Users", value="\n".join(um), inline=False)
        r_id = literal_eval(rl_db['bypass_rid'])
        rm = []
        for r in u_id:
            ru = discord.utils.get(ctx.guild.roles, id=i)
            try:
                rm.append(ru.mention)
            except:
                pass
        if len(rm) == 0:
            em.add_field(name="Whitelisted Roles", value="No Roles are whitelisted", inline=False)
        else:
            em.add_field(name="Whitelisted Roles", value="\n".join(um), inline=False)
        await ctx.reply(embed=em)

    @lockrole.command(name="add", description="Locks a role")
    @commands.has_guild_permissions(administrator=True)
    async def r_add(self, ctx: commands.Context, *, role: discord.Role):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/6Q9D7R8hYc)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/6Q9D7R8hYc"))
            return await ctx.reply(embed=em, view=v)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role")
        if not role.is_assignable():
            return await ctx.reply("I cant assign this role to anyone so please check my permissions and position.")
        if ctx.author.id != ctx.guild.owner.id:
            return await ctx.reply("Only guild owner can lock a role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        m_ids = []
        for i in role.members:
            m_ids.append(i.id)
        if rl_db is None:
            x = {}
            x[role.id] = m_ids
            sql = (f"INSERT INTO lockr(guild_id, role_id, m_list) VALUES(?, ?, ?)")
            val = (ctx.guild.id, f"[{role.id}]", f"{x}")
            cursor.execute(sql, val)
        else:
            xd = literal_eval(rl_db["role_id"])
            x = literal_eval(rl_db["m_list"])
            if role.id in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already Locked", color=0xc283fe))
            xd.append(role.id)
            x[role.id] = m_ids
            sql = (f"UPDATE lockr SET role_id = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
            cursor.execute(sql, val)
            sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
            val = (f"{x}", ctx.guild.id)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successlfully Locked the role {role.mention}"))

    @lockrole.command(name="remove", description="Unlocks a role")
    @commands.has_guild_permissions(administrator=True)
    async def r_remove(self, ctx: commands.Context, *, role: discord.Role):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/6Q9D7R8hYc)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/6Q9D7R8hYc"))
            return await ctx.reply(embed=em, view=v)
        if role.is_bot_managed() or role.is_premium_subscriber():
            return await ctx.reply("It is a integrated role. Please provide a different role")
        if ctx.author.id != ctx.guild.owner.id:
            return await ctx.reply("Only guild owner can unlock a role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already Unlocked", color=0xc283fe))
        else:
            xd = literal_eval(rl_db["role_id"])
            x = literal_eval(rl_db["m_list"])
            if role.id not in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already Unlocked", color=0xc283fe))
            xd.remove(role.id)
            del x[role.id]
            sql = (f"UPDATE lockr SET role_id = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
            cursor.execute(sql, val)
            sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
            val = (f"{x}", ctx.guild.id)
            cursor.execute(sql, val)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successlfully Unlocked the role {role.mention}"))

    @lockrole.group(invoke_without_command=True, description="Shows The help menu for lockrole wluser")
    async def wluser(self, ctx: commands.Context):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/6Q9D7R8hYc)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/6Q9D7R8hYc"))
            return await ctx.reply(embed=em, view=v)
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = discord.utils.get(self.bot.users, id=978930369392951366)
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=0xc283fe,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}lockrole wluser`\n" 
                                                  f"Shows The help menu for lockrole wluser\n\n" 
                                                  f"`{prefix}lockrole wluser add <user>`\n" 
                                                  f"Adds a whitelisted user for locked roles\n\n"
                                                  f"`{prefix}lockrole wluser remove <user>`\n"
                                                  f"Removes a whitelisted user for locked roles\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by stars.gg" ,  icon_url=pfp)
        await ctx.send(embed=listem)
    
    @wluser.command(name="add", description="Adds a whitelisted user for locked roles")
    @commands.has_guild_permissions(administrator=True)
    async def uwl_add(self, ctx: commands.Context, *, user: discord.Member):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/6Q9D7R8hYc)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/6Q9D7R8hYc"))
            return await ctx.reply(embed=em, view=v)
        if ctx.author.id != ctx.guild.owner.id:
            return await ctx.reply("Only guild owner can add a whitelisted user for locked role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"There should be atleast one locked role in order to add Whitelisted User", color=0xc283fe))
        elif rl_db["role_id"] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"There should be atleast one locked role in order to add Whitelisted User", color=0xc283fe))
        else:
            xd = literal_eval(rl_db["bypass_uid"])
            if user.id in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{user.mention} is already whitelisted for locked roles", color=0xc283fe))
            xd.append(user.id)
            sql = (f"UPDATE lockr SET bypass_uid = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successlfully whitelisted {user.mention} for locked roles"))

    @wluser.command(name="remove", description="Removes a whitelisted user for locked roles")
    @commands.has_guild_permissions(administrator=True)
    async def uwl_remove(self, ctx: commands.Context, *, user: discord.Member):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/6Q9D7R8hYc)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/6Q9D7R8hYc"))
            return await ctx.reply(embed=em, view=v)
        if ctx.author.id != ctx.guild.owner.id:
            return await ctx.reply("Only guild owner can remove a whitelisted user for locked role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"{user.mention} is not whitelisted for locked roles", color=0xc283fe))
        elif rl_db["role_id"] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"{user.mention} is not whitelisted for locked roles", color=0xc283fe))
        else:
            xd = literal_eval(rl_db["bypass_uid"])
            if user.id not in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{user.mention} is not whitelisted for locked roles", color=0xc283fe))
            xd.remove(user.id)
            sql = (f"UPDATE lockr SET bypass_uid = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successlfully unwhitelisted {user.mention} for locked roles"))
    

    @lockrole.group(invoke_without_command=True, description="Shows The help menu for lockrole wlrole")
    async def wlrole(self, ctx: commands.Context):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/6Q9D7R8hYc)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/6Q9D7R8hYc"))
            return await ctx.reply(embed=em, view=v)
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        xd = discord.utils.get(self.bot.users, id=978930369392951366)
        anay = str(xd)
        pfp = xd.display_avatar.url
        listem = discord.Embed(colour=0xc283fe,
                                     description=f"<...> Duty | [...] Optional\n\n" 
                                                  f"`{prefix}lockrole wlrole`\n" 
                                                  f"Shows The help menu for lockrole wlrole\n\n" 
                                                  f"`{prefix}lockrole wlrole add <user>`\n" 
                                                  f"Adds a whitelisted role for locked roles\n\n"
                                                  f"`{prefix}lockrole wluser remove <user>`\n"
                                                  f"Removes a whitelisted role for locked roles\n\n")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by stars.gg" ,  icon_url=pfp)
        await ctx.send(embed=listem)
    
    @wlrole.command(name="add", description="Adds a whitelisted role for locked roles")
    @commands.has_guild_permissions(administrator=True)
    async def rwl_add(self, ctx: commands.Context, *, role: discord.Role):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/6Q9D7R8hYc)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/6Q9D7R8hYc"))
            return await ctx.reply(embed=em, view=v)
        if ctx.author.id != ctx.guild.owner.id:
            return await ctx.reply("Only guild owner can add a whitelisted role for locked role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"There should be atleast one locked role in order to add Whitelisted role", color=0xc283fe))
        elif rl_db["role_id"] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"There should be atleast one locked role in order to add Whitelisted role", color=0xc283fe))
        else:
            xd = literal_eval(rl_db["bypass_rid"])
            if role.id in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is already whitelisted for locked roles", color=0xc283fe))
            xd.append(role.id)
            sql = (f"UPDATE lockr SET bypass_rid = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successlfully whitelisted {role.mention} for locked roles"))

    @wlrole.command(name="remove", description="Removes a whitelisted role for locked roles")
    @commands.has_guild_permissions(administrator=True)
    async def rwl_remove(self, ctx: commands.Context, *, role: discord.Role):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/6Q9D7R8hYc)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/6Q9D7R8hYc"))
            return await ctx.reply(embed=em, view=v)
        if ctx.author.id != ctx.guild.owner.id:
            return await ctx.reply("Only guild owner can remove a whitelisted role for locked role")
        query = "SELECT * FROM  lockr WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            rl_db = cursor.fetchone()
        if rl_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is not whitelisted for locked roles", color=0xc283fe))
        elif rl_db["role_id"] == "[]":
            return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is not whitelisted for locked roles", color=0xc283fe))
        else:
            xd = literal_eval(rl_db["bypass_rid"])
            if role.id not in xd:
                return await ctx.reply(embed=discord.Embed(description=f"{role.mention} is not whitelisted for locked roles", color=0xc283fe))
            xd.remove(role.id)
            sql = (f"UPDATE lockr SET bypass_rid = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"Successlfully unwhitelisted {role.mention} for locked roles"))
        
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member,
                               after: discord.Member) -> None:
        await self.bot.wait_until_ready()

        guild = after.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log or not guild.me.guild_permissions.manage_roles:
            return
        async for entry in after.guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.member_role_update):
            if entry.reason == "The role is locked":
              return
            query = "SELECT * FROM  lockr WHERE guild_id = ?"
            val = (after.guild.id,)
            with sqlite3.connect('./database.sqlite3') as db:
                db.row_factory = sqlite3.Row
                cursor = db.cursor()
                cursor.execute(query, val)
                rl_db = cursor.fetchone()
            if rl_db is not None:
                c = await check_upgraded(after.guild.id)
                if not c:
                    pass
                else:
                  if rl_db["role_id"] != "[]":
                    u_id = literal_eval(rl_db["bypass_uid"])
                    r_id = literal_eval(rl_db["bypass_rid"])
                    checkk = False
                    if entry.user.id == self.bot.user.id:
                        checkk = True
                    elif entry.user.id == guild.owner.id:
                        checkk = True
                    elif entry.user.id in u_id:
                        checkk = True
                    else:
                        for i in entry.user.roles:
                            if i.id in r_id:
                                checkk = True
                                break
                    br_id = literal_eval(rl_db["role_id"])
                    ls = []
                    for i in after.roles:
                        if i not in before.roles:
                            if i.id in br_id:
                                if not checkk:
                                    ls.append(i.id)
                                    await after.remove_roles(i, reason=f"The role is locked")
                                else:
                                    x = literal_eval(rl_db["m_list"])
                                    h = x[i.id]
                                    if after.id not in h:
                                        h.append(after.id)
                                    x[i.id] = h
                                    sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
                                    val = (f"{x}", after.guild.id)
                                    cursor.execute(sql, val)
                    for i in before.roles:
                        if i not in after.roles:
                            if i.id in br_id:
                                x = literal_eval(rl_db["m_list"])
                                h = x[i.id]
                                if after.id not in h:
                                    h.remove(after.id)
                                x[i.id] = h
                                sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
                                val = (f"{x}", after.guild.id)
                                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        await self.bot.wait_until_ready()

        guild = role.guild
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log or not guild.me.guild_permissions.manage_roles:
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.role_delete):
            if entry.user.id == self.bot.user.id:
                return
            query = "SELECT * FROM  lockr WHERE guild_id = ?"
            val = (guild.id,)
            with sqlite3.connect('./database.sqlite3') as db:
                db.row_factory = sqlite3.Row
                cursor = db.cursor()
                cursor.execute(query, val)
                rl_db = cursor.fetchone()
            check1 = False
            if rl_db is not None:
                c = await check_upgraded(role.guild.id)
                if not c:
                    pass
                else:
                  if rl_db["role_id"] != "[]":
                    u_id = literal_eval(rl_db["bypass_uid"])
                    r_id = literal_eval(rl_db["bypass_rid"])
                    checkk = False
                    if entry.user.id in u_id or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                        checkk = True
                    else:
                        for i in entry.user.roles:
                            if i.id in r_id:
                                checkk = True
                                break
                    if not checkk:
                        br_id = literal_eval(rl_db["role_id"])
                        if role.id in br_id:
                            br_id.remove(role.id)
                            check1 = True
                    else:
                        br_id = literal_eval(rl_db["role_id"])
                        x = literal_eval(rl_db['m_list'])
                        del x[role.id]
                        br_id.remove(role.id)
                        sql = (f"UPDATE lockr SET role_id = ? WHERE guild_id = ?")
                        val = (f"{br_id}", guild.id)
                        cursor.execute(sql, val)
                        sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
                        val = (f"{x}", guild.id)
                        cursor.execute(sql, val)
                        db.commit()
                        cursor.close()
                        db.close()
                if check1:
                    rrr = await guild.create_role(name=role.name, permissions=role.permissions, color=role.color, hoist=role.hoist, mentionable=role.mentionable ,reason=f"{self.bot.user.name} | Locked Role Recovery")
                    ok = True
                    cou = 0
                    while ok:
                        try:
                            await rrr.edit(position=role.position-cou)
                            ok = False
                        except:
                            cou+=1
                    x = literal_eval(rl_db['m_list'])
                    h = x[role.id]
                    del x[role.id]
                    x[rrr.id] = h
                    br_id.append(rrr.id)
                    sql = (f"UPDATE lockr SET role_id = ? WHERE guild_id = ?")
                    val = (f"{br_id}", guild.id)
                    cursor.execute(sql, val)
                    sql = (f"UPDATE lockr SET m_list = ? WHERE guild_id = ?")
                    val = (f"{x}", guild.id)
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    for i in h:
                        u = discord.utils.get(guild.members, id=i)
                        try:
                            await u.add_roles(rrr, reason=f"{self.bot.user.name} | Locked Role Recovery")
                        except:
                            pass
                        
    @commands.Cog.listener()
    async def on_guild_role_update(self, after: discord.Role,
                                   before: discord.Role) -> None:
        await self.bot.wait_until_ready()

        guild = after.guild
        name = before.name
        colour = before.colour
        perm = before.permissions
        if not guild:
            return
        if not guild.me.guild_permissions.view_audit_log or not guild.me.guild_permissions.manage_roles:
            return
        async for entry in guild.audit_logs(
                limit=1,
                after=datetime.datetime.now() - datetime.timedelta(minutes=2),
                action=discord.AuditLogAction.role_update):
            if entry.user.id == self.bot.user.id:
                return
            query = "SELECT * FROM  lockr WHERE guild_id = ?"
            val = (after.guild.id,)
            with sqlite3.connect('./database.sqlite3') as db:
                db.row_factory = sqlite3.Row
                cursor = db.cursor()
                cursor.execute(query, val)
                rl_db = cursor.fetchone()
            check1 = False
            if rl_db is not None:
                if rl_db["role_id"] != "[]":
                    u_id = literal_eval(rl_db["bypass_uid"])
                    r_id = literal_eval(rl_db["bypass_rid"])
                    checkk = False
                    if entry.user.id in u_id or entry.user.id == guild.owner.id or entry.user.id == self.bot.user.id:
                        checkk = True
                    else:
                        for i in entry.user.roles:
                            if i.id in r_id:
                                checkk = True
                                break
                    if not checkk:
                        br_id = literal_eval(rl_db["role_id"])
                        if after.id in br_id:
                            check1 = True
                if check1:
                    if name != after.name:
                        await after.edit(name=name, reason=f"{self.bot.user.name} | Locked Role Recovery")
                    if colour != after.colour:
                        await after.edit(colour=colour, reason=f"{self.bot.user.name} | Locked Role Recovery")
                    if perm != after.permissions:
                        await after.edit(permissions=perm, reason=f"{self.bot.user.name} | Locked Role Recovery")
                        
async def setup(bot):
    await bot.add_cog(lockrole(bot))

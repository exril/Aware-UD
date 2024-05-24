import discord
from discord.ext import commands, tasks
from dataclasses import dataclass
from typing import Any
import requests
import jishaku
import asyncio
import os
import wavelink
import sqlite3
import datetime
import pytz
from ast import literal_eval
from paginators import PaginationView
from io import BytesIO
from botinfo import *

def convert(date):
    date.replace("day", "d")
    date.replace("days", "d")
    date.replace("month", "m")
    date.replace("months", "m")
    date.replace("year", "y")
    date.replace("years", "y")
    pos = ["d", "m", "y"]
    time_dic = {"d": 3600 *24, "m": 3600 * 24* 30, "y": 3600 * 24 * 365}
    unit = date[-1]
    if unit not in pos:
        return -1
    try:
        val = int(date[:-1])
    except:
        return -2

    return val * time_dic[unit]

async def check_upgraded(guild_id):
    query = "SELECT * FROM  guild WHERE guild_id = ?"
    val = (guild_id,)
    with sqlite3.connect('premium.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        g_db = cursor.fetchone()
    if g_db is None:
        return True
    else:
        return True
    
async def check_vote(bot, ctx):
    x = await bot.topggpy.get_user_vote(ctx.author.id)
    return x

async def give_prem(user, tier, duration):
    duration = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    query = "SELECT * FROM  main WHERE user_id = ?"
    val = (user.id,)
    with sqlite3.connect('premium.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        p_db = cursor.fetchone()
    if p_db is not None:
        t = p_db['tier'].capitalize()
        return t
    else:
        if tier == "a":
            srvrs = 1
            duration = round(duration.timestamp())
        elif tier == "b":
            srvrs = 3
            duration = round(duration.timestamp())
        elif tier == "life":
            srvrs = 5
            duration = 4102424999
        sql = (f"INSERT INTO main(user_id, duration, tier, total, guilds) VALUES(?, ?, ?, ?, ?)")
        val = (user.id, duration, tier.capitalize(), srvrs, "[]",)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        db = sqlite3.connect('./database.sqlite3')
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM  badges WHERE user_id = {user.id}")
        result = cursor.fetchone()
        if result is None:
            sql = (f"INSERT INTO badges(user_id, PREMIUM) VALUES(?, ?)")
            val = (user.id, 1,)
            cursor.execute(sql, val)
        else:
            sql = (f"UPDATE badges SET 'PREMIUM' = ? WHERE user_id = ?")
            val = (1, user.id,)
            cursor.execute(sql, val)
        query = "SELECT * FROM  noprefix WHERE user_id = ?"
        val = (user.id,)
        cursor.execute(query, val)
        np_db = cursor.fetchone()
        if np_db is None:
            sql = (f"INSERT INTO noprefix(user_id, main) VALUES(?, ?)")
            val = (user.id, 1)
            cursor.execute(sql, val)
        else:
            sql = (f"UPDATE noprefix SET main = ? WHERE user_id = ?")
            val = (1, user.id)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        return True

async def remove_prem(user):
    query = "SELECT * FROM  main WHERE user_id = ?"
    val = (user.id,)
    with sqlite3.connect('premium.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        p_db = cursor.fetchone()
    if p_db is None:
        return False
    else:
        t = p_db['tier'].capitalize()
        gg = literal_eval(p_db['guilds'])
        for i in gg:
            query1 = "SELECT * FROM  guild WHERE guild_id = ?"
            val1 = (i,)
            cursor.execute(query1, val1)
            g_db = cursor.fetchone()
            if g_db is not None:
                sql1 = (f"DELETE FROM 'guild' WHERE guild_id = ?")
                val1 = (i,)
                cursor.execute(sql1, val1)
        sql = (f"DELETE FROM 'main' WHERE user_id = ?")
        val = (user.id,)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        db1 = sqlite3.connect('./database.sqlite3')
        db1.row_factory = sqlite3.Row
        cursor1 = db1.cursor()
        cursor1.execute(f"SELECT * FROM  badges WHERE user_id = {user.id}")
        result = cursor1.fetchone()
        if result is None:
            pass
        else:
            sql = (f"UPDATE badges SET 'PREMIUM' = ? WHERE user_id = ?")
            val = (0, user.id,)
            cursor1.execute(sql, val)
        db1.commit()
        cursor1.close()
        db.close()
        query = "SELECT * FROM  noprefix WHERE user_id = ?"
        val = (user.id,)
        with sqlite3.connect('database.sqlite3') as db2:
            db2.row_factory = sqlite3.Row
            cursor2 = db2.cursor()
            cursor2.execute(query, val)
            np_db = cursor2.fetchone()
        if np_db is None:
            pass
        else:
            sql = (f"UPDATE noprefix SET main = ? WHERE user_id = ?")
            val = (0, user.id)
            cursor2.execute(sql, val)
        db2.commit()
        cursor2.close()
        db2.close()
        return t

class premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @tasks.loop(minutes=1)
    async def check_prem(self):
        query = "SELECT * FROM  main"
        with sqlite3.connect('premium.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query)
            p_db = cursor.fetchall()
        today = datetime.datetime.now()
        for i, j, k, l, m in p_db:
            if round(today.timestamp()) >= round(j):
                u = discord.utils.get(self.bot.users, id=i)
                await remove_prem(user=u)

    #@tasks.loop(minutes=1)
    async def patreon(self):
        access_token = "lMOhujysq4HHwF6mexaPadsVoUpkC0LrK4qevLP9T3s"
        discord_patreon_members = {}
        campaign_base = "https://www.patreon.com/api/oauth2/v2/campaigns"
        campaigns = requests.get(
            campaign_base,
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        campaign_id = campaigns["data"][0]["id"]
        cursor = ""
        while True:
            resp = requests.get(
                campaign_base + f"/{campaign_id}/members?fields[user]=social_connections&include=user,currently_entitled_tiers&page[cursor]={cursor}",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if not resp.ok:
                print(resp.text)
                resp.raise_for_status()

            resp_json = resp.json()
            for member in resp_json["data"]:
                user_id = member["relationships"]["user"]["data"]["id"]
                user = discord.utils.find(lambda u: u["id"] == user_id, resp_json["included"])

                assert user is not None

                if (socials := user["attributes"].get("social_connections")) is not None:
                    if (discord_info := socials["discord"]) is not None:
                        if member["relationships"]["currently_entitled_tiers"]['data'] != []:
                            discord_patreon_members[int(discord_info["user_id"])] = member["relationships"]["currently_entitled_tiers"]['data']['amount_cents']

            pagination_info = resp_json["meta"]["pagination"]
            if (cursors := pagination_info.get("cursors")) is None:
                break

            cursor = cursors["next"]
            total = pagination_info["total"]
        for i in discord_patreon_members:
            user_dc = discord.utils.get(self.bot.users, id=i)
            if discord_patreon_members[i] == 249:
                tier = "a"
            elif discord_patreon_members[i] == 499:
                tier = "b"
            elif discord_patreon_members[i] == 5000:
                tier = "life"
            converted_time = convert("1m")
            c = await give_prem(user_dc, tier, converted_time)
            if c is not True:
                if c != tier:
                    await remove_prem(user_dc)
                    c = await give_prem(user_dc, tier, converted_time)
            else:
                pass

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_prem.start()
        #self.patreon.start()
        db = sqlite3.connect('premium.sqlite3')
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "main" (
                    "user_id"	INTEGER,
                    "duration"	INTEGER,
                    "total"	INTEGER,
                    "guilds"	TEXT DEFAULT [],
                    "tier"	TEXT,
                    PRIMARY KEY("user_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "guild" (
                    "guild_id"	INTEGER,
                    "activator"	INTEGER,
                    "since"	INTEGER,
                    "till"	INTEGER,
                    PRIMARY KEY("guild_id")
            )
            ''')
        db.commit()
        cursor.close()
        db.close()
    
    
    @commands.group(invoke_without_command=True, name="premium", aliases=["prem"], description="Premium")
    async def _prem(self, ctx: commands.Context):
        em = discord.Embed(title="<:vtg_moneybagg:1200640275572326410> Premium Features, Tiers and Prices", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium", icon_url="https://cdn.discordapp.com/emojis/1156882571175665704.png")
        ds = {"Premium A": "2.49$ for 1 server", "Premium B": "4.99$ for 3 servers", "Custom Aware": "14.99$", "Lifetime Premium": "50$ for 5 servers"}
        em.add_field(name="<:Sukoon_whiteflow:1200641010959650856> Features", value=f"The exclusive or you can say premium features of {self.bot.user.name} are:\n<:next:1154735525505269871> Lockrole\n<:next:1154735525505269871> Nightmode\n<:next:1154735525505269871> Create more than 3 selfrole panels in a single server\n<:next:1154735525505269871> Add upto 20 custom alias for giving or taking a specific role\n<:next:1154735525505269871> Fully customizable Bypass for ignorance\n<:next:1154735525505269871> InVC Roles\n<:next:1154735525505269871> 24/7 Bot in voice channel\n<:next:1154735525505269871> Premium Badge\n<:next:1154735525505269871> Premium Role in the support server", inline=False)
        des = ""
        for i in ds:
            des+=f"**{i}: {ds[i]}**\n"
        em.add_field(name="<:vtg_moneybagg:1200640275572326410> Tiers & Prices", value=des, inline=False)
        em.description = "<:tick_gandway:1156895119853752410> To purchase premium kindly go on the link given below or make a ticket in the [Support Server](https://discord.gg/AdYUu7RDpq)"
        v = discord.ui.View()
        v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
        v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/AdYUu7RDpq"))
        return await ctx.reply(embed=em, view=v)

    @_prem.command(name="users")
    @commands.is_owner()
    async def _userss(self, ctx: commands.Context):
        query = "SELECT * FROM  main"
        with sqlite3.connect('premium.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query)
            p_db = cursor.fetchall()
        today = datetime.datetime.now()
        ls2 = []
        ls = []
        count = 0
        for id, duration, total, guilds, tier in p_db:
            u = discord.utils.get(self.bot.users, id=id)
            if u is not None:
                count+=1
                g = literal_eval(guilds)
                ls2.append(f"`[{'0' + str(count) if count < 10 else count}]` | {str(u)} {tier.capitalize()} Premium - Total guilds upgraded - {len(g)}/{total} guilds - Premium till: <t:{round(duration)}:R>")
        for i in range(0, len(ls2), 10):
           ls.append(ls2[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=0xc283fe)
           embed.title = f"Premium users of bot - {count}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)

    @_prem.command(name="guilds")
    @commands.is_owner()
    async def _guilds(self, ctx: commands.Context):
        query = "SELECT * FROM  guild"
        with sqlite3.connect('premium.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query)
            p_db = cursor.fetchall()
        ls2 = []
        ls = []
        count = 0
        for id, activator, since, till in p_db:
            g = discord.utils.get(self.bot.guilds, id=id)
            u = discord.utils.get(self.bot.users, id=activator)
            if u is not None and g is not None:
                count+=1
                ls2.append(f"`[{'0' + str(count) if count < 10 else count}]` | {g.name} - Activated by {str(u)} - Premium since <t:{round(since)}:R> till: <t:{round(till)}:R>")
        for i in range(0, len(ls2), 10):
           ls.append(ls2[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=0xc283fe)
           embed.title = f"Premium guilds of bot - {count}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await page.start(ctx)

    @_prem.command(name="status")
    async def _status(self, ctx: commands.Context):
        query = "SELECT * FROM  guild WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('premium.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            g_db = cursor.fetchone()
        if g_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"The guild is not upgraded", color=0xc283fe))
        else:
            u = discord.utils.get(self.bot.users, id=g_db['activator'])
            query = "SELECT * FROM  main WHERE user_id = ?"
            val = (u.id,)
            with sqlite3.connect('premium.sqlite3') as db1:
                db1.row_factory = sqlite3.Row
                cursor1 = db1.cursor()
                cursor1.execute(query, val)
                p_db = cursor1.fetchone()
            since = g_db['since']
            till = p_db['duration']
            em = discord.Embed(title=f"Premium status of the server", description=f"<:confirm:1156150922200748053> The server is upgraded by: {u.mention} [{u.id}]\nThe server is upgraded since: <t:{round(since)}:R>\nThe server is upgraded till: <t:{round(till)}:R>", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium status", icon_url="https://cdn.discordapp.com/emojis/1156882571175665704.png")
            await ctx.reply(embed=em)

    @_prem.command(name="show")
    async def _show(self, ctx: commands.Context, *, user: discord.User=None):
        user = (user or ctx.author)
        query = "SELECT * FROM  main WHERE user_id = ?"
        val = (user.id,)
        with sqlite3.connect('premium.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            p_db = cursor.fetchone()
        if p_db is None:
            em = discord.Embed(description=f"{user.mention} don't have premium of the bot\nTo purchase premium kindly go on the link given below or make a ticket in the [Support Server](https://discord.gg/AdYUu7RDpq)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/AdYUu7RDpq"))
            return await ctx.reply(embed=em, view=v)
        else:
            tier = p_db['tier']
            total = p_db['total']
            duration = f"<t:{round(p_db['duration'])}:R>"
            g = []
            gu = literal_eval(p_db['guilds'])
            count = 0
            for i in gu:
                count +=1 
                gg = discord.utils.get(self.bot.guilds, id=i)
                if gg is None:
                    g.append("None")
                else:
                    g.append(f"[{'0' + str(count) if count < 10 else count}] | {gg.name} [{gg.id}]")
            left = total - len(gu)
            em = discord.Embed(title=f"{tier.capitalize()} Tier Premium", description=f"Ends at: {duration}\nTotal Upgradable Guilds: {total} guilds\nUpgrades Left: {left}", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium", icon_url=self.bot.user.avatar.url)
            if left != total:
                xd = '\n'.join(g)
                em.description  += f"\nUpgraded Guilds [{total - left}]: ```{xd}```"
            await ctx.reply(embed=em)
        
    @_prem.command(name="activate", aliases=['active'])
    async def _activate(self, ctx: commands.Context, *,guild: discord.Guild=None):
        guild = (guild or ctx.guild)
        query = "SELECT * FROM  main WHERE user_id = ?"
        val = (ctx.author.id,)
        with sqlite3.connect('premium.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            p_db = cursor.fetchone()
        if p_db is None:
            return
        else:
            total = p_db['total']
            g = literal_eval(p_db['guilds'])
            duration = round(p_db['duration'])
            if len(g) >= total:
                return await ctx.reply(f"You have already upgraded {total} server")
            else:
                query1 = "SELECT * FROM  guild WHERE guild_id = ?"
                val1 = (guild.id,)
                with sqlite3.connect('premium.sqlite3') as db1:
                    db1.row_factory = sqlite3.Row
                    cursor1 = db1.cursor()
                    cursor1.execute(query1, val1)
                    g_db = cursor1.fetchone()
                if g_db is not None:
                    u = discord.utils.get(self.bot.users, id=g_db['activator'])
                    if u is not None:
                        return await ctx.reply(embed=discord.Embed(description=f"<:cross:1156150663802265670> The guild is already upgraded by {u.mention}", color=0xc283fe))
                else:
                    sql = (f"INSERT INTO guild(guild_id, activator, since, till) VALUES(?, ?, ?, ?)")
                    val = (guild.id, ctx.author.id, round(datetime.datetime.now().timestamp()), duration)
                    cursor1.execute(sql, val)
                db1.commit()
                cursor1.close()
                db1.close()
                g.append(guild.id)
                sql = (f"UPDATE main SET 'guilds' = ? WHERE user_id = ?")
                val = (f"{g}", ctx.author.id,)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                em = discord.Embed(description=f"<:tick_gandway:1156895119853752410> Successfully Upgraded the guild till <t:{round(duration)}:R>", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium upgraded", icon_url=self.bot.user.avatar.url)
                await ctx.reply(embed=em)
                em.description = f"Upgraded the guild {guild.name} - [{guild.id}] till <t:{round(duration)}:R> by {str(ctx.author)} - [{ctx.author.id}]"
                webhook = discord.SyncWebhook.from_url(webhook_imp_logs)
                webhook.send(embed=em, username=f"{str(self.bot.user)} | Premium guild activated Logs", avatar_url=self.bot.user.avatar.url)

    @_prem.command(name="deactivate", aliases=['remove'])
    async def _remove(self, ctx: commands.Context, *,guild: discord.Guild=None):
        guild = (guild or ctx.guild)
        query = "SELECT * FROM  main WHERE user_id = ?"
        val = (ctx.author.id,)
        with sqlite3.connect('premium.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            p_db = cursor.fetchone()
        if p_db is None:
            return
        else:
            total = p_db['total']
            g = literal_eval(p_db['guilds'])
            duration = round(p_db['duration'])
            query1 = "SELECT * FROM  guild WHERE guild_id = ?"
            val1 = (guild.id,)
            cursor.execute(query1, val1)
            g_db = cursor.fetchone()
            if g_db is None:
                return await ctx.reply(embed=discord.Embed(description=f"The guild is not upgraded", color=0xc283fe))
            else:
                if guild.id not in g:
                    return await ctx.reply(embed=discord.Embed(description=f"The guild is upgraded but not by you so you cannot downgrade it", color=0xc283fe))
                else:
                    g.remove(guild.id)
                    sql1 = (f"DELETE FROM 'guild' WHERE guild_id = ?")
                    val1 = (guild.id,)
                    cursor.execute(sql1, val1)
                    sql = (f"UPDATE main SET 'guilds' = ? WHERE user_id = ?")
                    val = (f"{g}", ctx.author.id,)
                    cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    query = "SELECT * FROM  noprefix WHERE user_id = ?"
                    val = (ctx.author.id,)
                    with sqlite3.connect('database.sqlite3') as db2:
                        db2.row_factory = sqlite3.Row
                        cursor2 = db2.cursor()
                        cursor2.execute(query, val)
                        np_db = cursor2.fetchone()
                    if np_db is None:
                            pass
                    else:
                        if np_db['servers'] is None:
                            pass
                        else:
                            np = literal_eval(np_db['servers'])
                            np.remove(ctx.guild.id)
                            sql = (f"UPDATE noprefix SET servers = ? WHERE user_id = ?")
                            val = (f"{np}", ctx.author.id)
                            cursor2.execute(sql, val)
                    db2.commit()
                    cursor2.close()
                    db2.close()
                    query = "SELECT * FROM  '247' WHERE guild_id = ?"
                    val = (guild.id,)
                    with sqlite3.connect('database.sqlite3') as db2:
                        db2.row_factory = sqlite3.Row
                        cursor2 = db2.cursor()
                        cursor2.execute(query, val)
                        _db = cursor2.fetchone()
                    if _db is not None:
                        sql1 = (f"DELETE FROM '247' WHERE guild_id = ?")
                        val1 = (guild.id,)
                        cursor2.execute(sql1, val1)
                    db2.commit()
                    cursor2.close()
                    db2.close()
                    em = discord.Embed(description=f"<:tick_gandway:1156895119853752410> Successfully Downgraded the guild", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium upgraded", icon_url=self.bot.user.avatar.url)
                    await ctx.reply(embed=em)
                    em.description = f"Downgraded the guild {ctx.guild.name} - [{ctx.guild.id}] by {str(ctx.author)} - [{ctx.author.id}]"
                    webhook = discord.SyncWebhook.from_url(webhook_imp_logs)
                    webhook.send(embed=em, username=f"{str(self.bot.user)} | Premium guild deactivated Logs", avatar_url=self.bot.user.avatar.url)

    @_prem.command(name="give", aliases=['add', 'a', 'g'])
    @commands.is_owner()
    async def _give(self, ctx: commands.Context, user: discord.User, tier: str, duration: str=None):
        ds = ['a', 'b', 'life']
        if tier.lower() not in ds:
            return await ctx.send("The Tiers available are: Premium A, premium B, Lifetime premium")
        if duration is None:
            converted_time = convert("1m")
        else:
            converted_time = convert(duration)
        if converted_time == -1:
            await ctx.send("You did not enter the correct unit of time (d|m|y)")
        elif converted_time == -2:
            await ctx.send("Your time value should be an integer.")
            return
        tier = tier.lower()
        c = await give_prem(user, tier, converted_time)
        if c is not True:
            em = discord.Embed(description=f"{user.mention} already have {c} tier Premium", color=0xc283fe)
            await ctx.reply(embed=em)
        else:
            duration = datetime.datetime.now() + datetime.timedelta(seconds=converted_time)
            if tier == "a":
                srvrs = 1
                duration = duration.timestamp()
            elif tier == "b":
                srvrs = 3
                duration = duration.timestamp()
            elif tier == "life":
                srvrs = 5
                duration = 4102424999
            em = discord.Embed(description=f"<:tick_gandway:1156895119853752410> Successfully given {tier.capitalize()} Tier premium to {user.mention} for {srvrs} Servers till <t:{round(duration)}:R>", color=0xc283fe)
            await ctx.reply(embed=em)
            em.description = f"Given `{tier.capitalize()}` Tier premium to `{str(user)}` [{user.id}] by `{str(ctx.author)}` [{ctx.author.id}] for {srvrs} Servers till <t:{round(duration)}:R>"
            webhook = discord.SyncWebhook.from_url(webhook_imp_logs)
            webhook.send(embed=em, username=f"{str(self.bot.user)} | Premium given Logs", avatar_url=self.bot.user.avatar.url)
    
    @_prem.command(name="take", aliases=['delete', 'del', 't', 'd'])
    @commands.is_owner()
    async def _removee(self, ctx: commands.Context, *, user: discord.User):
        c = await remove_prem(user)
        if not c:
            em = discord.Embed(description=f"{user.mention} don't have any tier Premium", color=0xc283fe)
            await ctx.reply(embed=em)
        else:
            em = discord.Embed(description=f"<:tick_gandway:1156895119853752410> Successfully removed {c.capitalize()} Tier premium from {user.mention}", color=0xc283fe)
            await ctx.reply(embed=em)
            em.description = f"Removed `{c.capitalize()}` Tier premium from `{str(user)}` [{user.id}] by `{str(ctx.author)}` [{ctx.author.id}]"
            webhook = discord.SyncWebhook.from_url(webhook_imp_logs)
            webhook.send(embed=em, username=f"{str(self.bot.user)} | Premium removed Logs", avatar_url=self.bot.user.avatar.url)
        
async def setup(bot):
    await bot.add_cog(premium(bot))

import discord
from discord.ext import commands, tasks
import aiohttp
import jishaku
import requests
from requests.structures import CaseInsensitiveDict
import asyncio
import os
import sqlite3
import datetime
import pytz
from ast import literal_eval
from paginators import PaginationView
from io import BytesIO
from botinfo import *
from cogs.ticket import ticketpanel, tickredel, ticketchannelpanel
from cogs.selfroles import DropdownSelfRoleView, ButtonSelfRoleView
from cogs.premium import check_upgraded

async def postdata(bot: commands.AutoShardedBot):
    url = "https://api.awarebot.pro/api/post/stats"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer e2tleTogImIxZGQ0NWRlNjY4ZTQ1MDk4YzdjNWQ1OGE2ZGRhOTBmIiwgdHlwZTogInBvc3QiLCBjbGllbnQ6ICJnYXRld2F5YXBpIn0="
    headers["Content-Type"] = "application/json"
    c=0
    for guild in bot.guilds:
        if guild.voice_client:
            c += 1
    data = {
        "guilds": len(bot.guilds),
        "users": len(bot.users),
        "channels": len(set(bot.get_all_channels())),
        "players": c,
        "shardCount": len(bot.shards),        
        "uptime": starttime.timestamp()
    }
    requests.post(url, headers=headers, json=data)

async def postcmddata(bot: commands.AutoShardedBot):
    url = "https://api.awarebot.pro/api/post/commands"
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer e2tleTogImIxZGQ0NWRlNjY4ZTQ1MDk4YzdjNWQ1OGE2ZGRhOTBmIiwgdHlwZTogInBvc3QiLCBjbGllbnQ6ICJnYXRld2F5YXBpIn0="
    headers["Content-Type"] = "application/json"
    count = 0
    commands = []
    for i in bot.walk_commands():
        if "Jishaku" in i.cog_name:
            continue
        else:
            count+=1
            name = i.qualified_name
            cat = i.cog_name.title()
            des = i.description or "Not Provided"
            usage = f"{i.qualified_name} {i.signature}"
            data = {
                "name": name,
                "category": cat,
                "description": des,
                "usage": usage
            }
            commands.append(data)
    m_data = {
        "commands": commands,
        "commandCount": len(commands)
    }
    res = requests.post(url, headers=headers, json=m_data)
    return (res.status_code, count, len(commands))

async def loadselfroles(bot: commands.AutoShardedBot):
    query = "SELECT * FROM  srmain"
    with sqlite3.connect('./database.sqlite3') as db1:
        db1.row_factory = sqlite3.Row
        cursor1 = db1.cursor()
        cursor1.execute(query)
        self_db = cursor1.fetchall()
    for i, j, k in self_db:
        dbb = literal_eval(j)
        dbd = literal_eval(k)
        for i in dbb:
            v = ButtonSelfRoleView(stuff=i["data"])
            try:
                c = bot.get_channel(i['channel_id'])
                m = await c.fetch_message(i['message_id'])
                await m.edit(view=v)
                bot.add_view(v)
            except:
                pass
        for i in dbd:
            dd = i['data']
            reqrole = dd[0]["reqrole"]
            v = DropdownSelfRoleView(place=i["placeholder"], max=i["max_options"], stuff=i["data"], reqrole=reqrole)
            try:
                c = bot.get_channel(i['channel_id'])
                m = await c.fetch_message(i['message_id'])
                await m.edit(view=v)
                bot.add_view(v)
            except:
                pass

            
class event(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=pytz.timezone("Asia/Kolkata")))
    async def daily(self):
        query = ("SELECT * FROM daily WHERE id = ?")
        val = (self.bot.user.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            _db = cursor.fetchone()
        if _db is None:
            pass
        else:
            sql = (f"UPDATE 'daily' SET guild = ? WHERE id = ?")
            val = (0, self.bot.user.id)
            cursor.execute(sql, val)
            sql = (f"UPDATE 'daily' SET user = ? WHERE id = ?")
            val = (0, self.bot.user.id)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    #@tasks.loop(minutes=60)
    async def posting(self):
        await postdata(self.bot)
        await postcmddata(self.bot)
        
    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        webhook = discord.SyncWebhook.from_url(webhook_shard_logs)
        webhook.send(f"Shard {shard_id} is Now ready", username=f"{str(self.bot.user)} | Shard Logs", avatar_url=self.bot.user.avatar.url)

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
            webhook = discord.SyncWebhook.from_url(webhook_shard_logs)
            webhook.send(f"Shard {shard_id} is Disconnected", username=f"{str(self.bot.user)} | Shard Logs", avatar_url=self.bot.user.avatar.url)

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        bot = self.bot
        bot.add_view(ticketpanel(bot))
        bot.add_view(ticketchannelpanel(bot))
        bot.add_view(tickredel(bot))
#        bot.add_view(interface(bot))
        try:
            await loadselfroles(bot)
        except:
            pass
        try:
            await loadgw(bot)
        except:
            pass
        webhook = discord.SyncWebhook.from_url(webhook_shard_logs)
        webhook.send(f"Shard {shard_id} is Resumed", username=f"{str(self.bot.user)} | Shard Logs", avatar_url=self.bot.user.avatar.url)

    @commands.Cog.listener()
    async def on_ready(self):
        bot = self.bot
        await bot.change_presence(activity=discord.CustomActivity(name='🔗 awarebot.pro '), status=discord.Status.idle)
        bot.add_view(ticketpanel(bot))
        bot.add_view(ticketchannelpanel(bot))
        bot.add_view(tickredel(bot))
        #bot.add_view(interface(bot))
        try:
            await loadselfroles(bot)
        except:
            pass
        try:
            await loadgw(bot)
        except:
            pass
        print(f"Loaded Buttons and Dropdowns views")
        #await postdata(bot)
        #await postcmddata(bot)
        await asyncio.sleep(10)
        query = "SELECT * FROM  '247'"
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            coun = 0
            try:
                cursor.execute(query)
                m_db = cursor.fetchall()
                for i in m_db:
                    try:
                        c = bot.get_channel(i['channel_id'])
                        vc: wavelink.Player = await c.connect(cls=wavelink.Player, self_deaf=True)
                        coun+=1
                    except:
                        pass
            except:
                pass
        print(f"Connected to {coun} voice channels (24/7)")
        # self.back.start()
        #self.daily.start()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "main" (
                    "xd"	INTEGER DEFAULT 77,
                    "nopre"	TEXT DEFAULT [994130204949745705, 979353019235840000, 933738517845118976, 966230921084796999],
                    "bperm"	TEXT DEFAULT [994130204949745705, 979353019235840000, 933738517845118976, 966230921084796999],
                    PRIMARY KEY("xd")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "count" (
                    "xd" INTEGER DEFAULT 1,
                    "guild_count"	TEXT DEFAULT "{}",
                    "cmd_count"	TEXT DEFAULT "{}",
                    "user_count"	TEXT DEFAULT "{}",
                    PRIMARY KEY("xd")
            )
            ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS auto_res(
                "id" bigint,
                "guild_id" bigint,
                "name" TEXT DEFAULT `[]`,
                "content" TEXT DEFAULT `[]`,
                "time" TEXT DEFAULT `[]`,
                PRIMARY KEY("guild_id")
        )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "noprefix" (
                    "user_id"	INTEGER,
                    "servers"	TEXT,
                    "main"	INTEGER DEFAULT 0,
                    PRIMARY KEY("user_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "afk" (
                    "user_id"	INTEGER,
                    "afkk"	TEXT DEFAULT '{}',
                    "globally" INTEGER DEFAULT 0,
                    PRIMARY KEY("user_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "warn" (
                    "guild_id"	INTEGER,
                    "data"	TEXT DEFAULT '{}',
                    "count"	INTEGER DEFAULT 0,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "bl" (
                    "main"  INTEGER DEFAULT 1,
                    "user_ids"	TEXT DEFAULT '[]',
                    PRIMARY KEY("main")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prefixes(
                    "guild_id" INTEGER,
                    "prefix" TEXT DEFAULT "-",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "titles" (
                    "user_id"	INTEGER,
                    "title"	TEXT,
                    PRIMARY KEY("user_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "badges" (
                    "user_id"	INTEGER,
                    "BUG"	INTEGER DEFAULT 0,
                    "DONATOR"	INTEGER DEFAULT 0,
                    "SPECIAL"	INTEGER DEFAULT 0,
                    "SUPPORTER"	INTEGER DEFAULT 0,
                    "FRIEND"	INTEGER DEFAULT 0,
                    "VIP"	INTEGER DEFAULT 0,
                    "OWNER"	INTEGER DEFAULT 0,
                    "DEVELOPER"	INTEGER DEFAULT 0,
                    "STAFF"	INTEGER DEFAULT 0,
                    "ADMIN"	INTEGER DEFAULT 0,
                    "MOD"	INTEGER DEFAULT 0,
                    "PREMIUM"	INTEGER DEFAULT 0,
                    PRIMARY KEY("user_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles(
                    "guild_id"	INTEGER,
                    "role"	INTEGER DEFAULT 0,
                    "official"	INTEGER DEFAULT 0,
                    "vip"	INTEGER DEFAULT 0,
                    "guest"	INTEGER DEFAULT 0,
                    "girls"	INTEGER DEFAULT 0,
                    "tag"	TEXT,
                    "friend"	INTEGER DEFAULT 0,
                    "custom"	TEXT DEFAULT "{}",
                    "ar"	INTEGER DEFAULT 0,
                    "stag"	TEXT,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS imp(
                        "guild_id"	INTEGER,
                    "cmd" TEXT DEFAULT 0,
                    "admin" TEXT DEFAULT 0,
                    "kick" TEXT DEFAULT 0,
                    "ban" TEXT DEFAULT 0,
                    "mgn" TEXT DEFAULT 0,
                    "mgnch" TEXT DEFAULT 0,
                    "mgnro" TEXT DEFAULT 0,
                    "mention" TEXT DEFAULT 0,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pfp(
                        "guild_id"	INTEGER,
                    "channel_id" INTEGER,
                    "type" TEXT,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily(
                        "id"	INTEGER,
                    "guild" INTEGER DEFAULT 0,
                    "user" INTEGER DEFAULT 0,
                    PRIMARY KEY("id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todo(
                        "user_id"	INTEGER,
                    "todo" TEXT DEFAULT "[]",
                    PRIMARY KEY("user_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "help" (
                    "main"  INTEGER DEFAULT 1,
                    "no" INTEGER,
                    PRIMARY KEY("main")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auto(
                    "guild_id" INTEGER,
                    "humans" TEXT,
                    "bots" TEXT,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS welcome(
                        "guild_id"	INTEGER,
                    "channel_id"	INTEGER,
                    "msg"	TEXT DEFAULT 'Hey $user_mention',
                    "emdata"	TEXT DEFAULT "{'footer': {'text': 'Gateway Welcome'}, 'color': 3092790, 'type': 'rich', 'description': 'Hey $user_mention', 'title': 'Welcome to $server_name'}",
                    "embed"	INTEGER DEFAULT 0,
                    "ping"	INTEGER DEFAULT 0,
                    "autodel"  INTEGER DEFAULT 0,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auto(
                    "guild_id" INTEGER,
                    "humans" TEXT,
                    "bots" TEXT,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS toggle(
                    "guild_id" INTEGER,
                    "BAN" INTEGER DEFAULT 0,
                    "BOT" INTEGER DEFAULT 0,
                    "KICK" INTEGER DEFAULT 0,
                    "ROLE CREATE" INTEGER DEFAULT 0,
                    "ROLE DELETE" INTEGER DEFAULT 0,
                    "ROLE UPDATE" INTEGER DEFAULT 0,
                    "CHANNEL CREATE" INTEGER DEFAULT 0,
                    "CHANNEL DELETE" INTEGER DEFAULT 0,
                    "CHANNEL UPDATE" INTEGER DEFAULT 0,
                    "MEMBER UPDATE" INTEGER DEFAULT 0,
                    "GUILD UPDATE" INTEGER DEFAULT 0,
                    "WEBHOOK" INTEGER DEFAULT 0,
                    "ALL" INTEGER DEFAULT 0,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wl(
                    "guild_id" INTEGER,
                    "BAN" TEXT DEFAULT "[]",
                    "BOT" TEXT DEFAULT "[]",
                    "KICK" TEXT DEFAULT "[]",
                    "ROLE CREATE" TEXT DEFAULT "[]",
                    "ROLE DELETE" TEXT DEFAULT "[]",
                    "ROLE UPDATE" TEXT DEFAULT "[]",
                    "CHANNEL CREATE" TEXT DEFAULT "[]",
                    "CHANNEL DELETE" TEXT DEFAULT "[]",
                    "CHANNEL UPDATE" TEXT DEFAULT "[]",
                    "MEMBER UPDATE" TEXT DEFAULT "[]",
                    "GUILD UPDATE" TEXT DEFAULT "[]",
                    "WEBHOOK" TEXT DEFAULT "[]",
                    "ALL" TEXT DEFAULT "[]",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS punish(
                    "guild_id" INTEGER,
                    "PUNISHMENT" TEXT DEFAULT "BAN",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lockr(
                    "guild_id" INTEGER,
                    "role_id" TEXT DEFAULT "[]",
                    "bypass_uid" TEXT DEFAULT "[]",
                    "bypass_rid" TEXT DEFAULT "[]",
                    "m_list" TEXT DEFAULT "{}",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raidmode(
                    "guild_id" INTEGER,
                    "toggle" INTEGER DEFAULT 0,
                    "time" INTEGER DEFAULT 10,
                    "max" INTEGER DEFAULT 15,
                    "PUNISHMENT" TEXT DEFAULT "KICK",
                    "lock" INTEGER DEFAULT 0,
                    "lockdown" INTEGER DEFAULT 1,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "logs" (
                    "guild_id"	INTEGER,
                    "mod"	INTEGER,
                    "role"	INTEGER,
                    "channel"	INTEGER,
                    "server"	INTEGER,
                    "member"	INTEGER,
                    "message"	INTEGER,
                    "antinuke"	INTEGER,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "gwmain" (
                    "guild_id"  INTEGER,
                    "gw" TEXT DEFAULT "{}",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "invc" (
                    "guild_id"  INTEGER,
                    "vc" TEXT DEFAULT "{}",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "bot" (
                    "bot_id"  INTEGER,
                    "totaltime" INTEGER DEFAULT 0,
                    "server" TEXT DEFAULT "{}",
                    "user" TEXT DEFAULT "{}",
                    PRIMARY KEY("bot_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "setup" (
                    "guild_id"  INTEGER,
                    "channel_id" INTEGER,
                    "msg_id" INTEGER,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "247" (
                    "guild_id"  INTEGER,
                    "channel_id" INTEGER,
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "pl" (
                    "user_id"  INTEGER,
                    "pl" TEXT DEFAULT "{}",
                    PRIMARY KEY("user_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "user" (
                    "user_id"  INTEGER,
                    "totaltime" INTEGER DEFAULT 0,
                    "server" TEXT DEFAULT "{}",
                    "friend" TEXT DEFAULT "{}",
                    "artist" TEXT DEFAULT "{}",
                    "track", TEXT DEFAULT "{}",
                    PRIMARY KEY("user_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "panel" (
                    "guild_id"  INTEGER,
                    "channel_id" INTEGER,
                    "msg_id" INTEGER,
                    "opencategory" INTEGER,
                    "closedcategory" INTEGER,
                    "claimedrole" INTEGER,
                    "supportrole" INTEGER,
                    "pingrole" INTEGER,
                    "name" TEXT,
                    "msg" TEXT DEFAULT '\nTo create a ticket interact with the button below 📩',
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "ticket" (
                    "guild_id"  INTEGER,
                    "name" TEXT,
                    "count" INTEGER DEFAULT 0000,
                    "opendata" TEXT DEFAULT "{}",
                    "closeddata" TEXT DEFAULT "{}",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "ignore" (
                    "guild_id"  INTEGER,
                    "cmd" TEXT DEFAULT "[]",
                    "channel" TEXT DEFAULT "[]",
                    "user" TEXT DEFAULT "[]",
                    "role" TEXT DEFAULT "[]",
                    "module" TEXT DEFAULT "[]",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "bypass" (
                    "guild_id"  INTEGER,
                    "bypass_users" TEXT DEFAULT "{}",
                    "bypass_roles" TEXT DEFAULT "{}",
                    "bypass_channels" TEXT DEFAULT "{}",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "srmain" (
                    "guild_id"  INTEGER,
                    "data_button" TEXT DEFAULT "[]",
                    "data_dropdown" TEXT DEFAULT "[]",
                    PRIMARY KEY("guild_id")
            )
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "messages_db" (
                    "guild_id"  INTEGER,
                    "messages" TEXT DEFAULT "{}",
                    "daily_messages" TEXT DEFAULT "{}",
                    "bl_channels" TEXT DEFAULT "[]",
                    PRIMARY KEY("guild_id")
            )
            ''')
        db.commit()
        cursor.close()
        db.close()
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
        print(f'Logged in as {bot.user.name}({bot.user.id})')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.wait_until_ready()
        bot = self.bot
        em = discord.Embed(title="Guild Joined", color=0xc283fe)
        em.add_field(name="Guild Information:", value=f"Server Name: {guild.name}\nServer Id: {guild.id}\nServer Owner: {guild.owner.name} [{guild.owner.id}]\nCreated At: <t:{round(guild.created_at.timestamp())}:R>\nMember Count: {len(guild.members)} Members\nRoles: {len(guild.roles)} Roles\nText Channels: {len(guild.text_channels)} Channels\nVoice Channels: {len(guild.voice_channels)} Channels")
        em.add_field(name="Bot Info:", value=f"Servers: {len(bot.guilds)} Servers\nUsers: {len(bot.users)} Users\nChannels: {str(len(set(bot.get_all_channels())))} Channels")
        try:
            em.set_thumbnail(url=guild.icon.url)
        except:
            pass
        em.set_footer(text=f"{str(bot.user)}", icon_url=bot.user.avatar.url)
        webhook = discord.SyncWebhook.from_url(webhook_join_leave_logs)
        webhook.send(embed=em, username=f"{str(self.bot.user)} | Join Logs", avatar_url=self.bot.user.avatar.url)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
        try:
            cursor.execute(f"INSERT INTO roles(guild_id) VALUES({guild.id})")
        except:
            pass
        try:
            cursor.execute(f"INSERT INTO imp(guild_id) VALUES({guild.id})")
        except:
            pass
        try:
            cursor.execute(f"INSERT INTO prefixes(guild_id) VALUES({guild.id})")
        except:
            pass
        try:
            cursor.execute(f"INSERT INTO ignore(guild_id) VALUES({guild.id})")
        except:
            pass
        try:
            cursor.execute(f"INSERT INTO auto(guild_id) VALUES({guild.id})")
        except:
            pass
        try:
            cursor.execute(f"INSERT INTO logs(guild_id) VALUES({guild.id})")
        except:
            pass
        query = "SELECT * FROM  invc WHERE guild_id = ?"
        val = (guild.id,)
        cursor.execute(query, val)
        in_vc = cursor.fetchone()
        x = {}
        for i in guild.channels:
            if i.type == 'voice':
                x[i.id] = None
        if in_vc is None:
            sql = f"INSERT INTO invc(guild_id, vc) VALUES(?, ?)"
            val = (guild.id, f"{x}")
            cursor.execute(sql, val)
        else:
            pass
        query = ("SELECT * FROM daily WHERE id = ?")
        val = (self.bot.user.id,)
        cursor.execute(query, val)
        _db = cursor.fetchone()
        if _db is None:
            sql = f"INSERT INTO 'daily'(id, guild, user) VALUES(?, ?, ?)"
            val = (self.bot.user.id, 1, len(guild.members),)
            cursor.execute(sql, val)
        else:
            g = _db['guild'] + 1
            u = _db['user'] + len(guild.members)
            sql = (f"UPDATE 'daily' SET guild = ? WHERE id = ?")
            val = (g, self.bot.user.id)
            cursor.execute(sql, val)
            sql = (f"UPDATE 'daily' SET user = ? WHERE id = ?")
            val = (u, self.bot.user.id)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.wait_until_ready()
        bot = self.bot
        if guild is None:
          return
        em = discord.Embed(title="Guild Leave", color=0xc283fe)
        em.add_field(name="Guild Information:", value=f"Server Name: {guild.name}\nServer Id: {guild.id}\nCreated At: <t:{round(guild.created_at.timestamp())}:R>\nMember Count: {len(guild.members)} Members\nRoles: {len(guild.roles)} Roles\nText Channels: {len(guild.text_channels)} Channels\nVoice Channels: {len(guild.voice_channels)} Channels")
        em.add_field(name="Bot Info:", value=f"Servers: {len(bot.guilds)} Servers\nUsers: {len(bot.users)} Users\nChannels: {str(len(set(bot.get_all_channels())))} Channels")
        try:
            em.set_thumbnail(url=guild.icon.url)
        except:
            pass
        query = ("SELECT * FROM daily WHERE id = ?")
        val = (self.bot.user.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            _db = cursor.fetchone()
        if _db is None:
            sql = f"INSERT INTO 'daily'(id, guild, user) VALUES(?, ?, ?)"
            val = (self.bot.user.id, -1, -len(guild.members),)
            cursor.execute(sql, val)
        else:
            g = _db['guild'] - 1
            u = _db['user'] - len(guild.members)
            sql = (f"UPDATE 'daily' SET guild = ? WHERE id = ?")
            val = (g, self.bot.user.id)
            cursor.execute(sql, val)
            sql = (f"UPDATE 'daily' SET user = ? WHERE id = ?")
            val = (u, self.bot.user.id)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        em.set_footer(text=f"{str(bot.user)}", icon_url=bot.user.avatar.url)
        webhook = discord.SyncWebhook.from_url(webhook_join_leave_logs)
        webhook.send(embed=em, username=f"{str(self.bot.user)} | Leave Logs", avatar_url=self.bot.user.avatar.url)

async def setup(bot):
    await bot.add_cog(event(bot))

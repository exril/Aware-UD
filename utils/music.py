import discord
import os
import wavelink
from discord.ext import commands
from wavelink.ext import spotify
import spotify as spotifyyy
import asyncio
import typing
import datetime
import re
import sqlite3
import time
from paginators import PaginationView
from ast import literal_eval
from cogs.premium import check_upgraded

URL_REG = re.compile(r'https?://(?:www\.)?.+')
SPOTIFY_URL_REG = re.compile(r'https?://open.spotify.com/(?P<type>album|playlist|track)/(?P<id>[a-zA-Z0-9]+)')
spotifyyy_client = spotifyyy.Client("9d340e339c10432e9c478742931d64e9", "2e23b2ab872046eca5fdf3379006f7de")
spotifyyy_http_client = spotifyyy.http.HTTPClient("9d340e339c10432e9c478742931d64e9", "2e23b2ab872046eca5fdf3379006f7de")
spotify_client = spotify.SpotifyClient(client_id="9d340e339c10432e9c478742931d64e9", client_secret="2e23b2ab872046eca5fdf3379006f7de")
msg_id = {}

def updatemsgid(guild_id, data):
    msg_id[guild_id] = data
    
def getmsgid(guild_id):
    try:
        d = msg_id[guild_id]
    except:
        d = None
    return d

class BasicView(discord.ui.View):
    def __init__(self, ctx: commands.Context, timeout = 60):
        super().__init__(timeout=timeout)
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id and interaction.user.id not in  [978930369392951366, 979353019235840000]:
            await interaction.response.send_message(f"Um, Looks like you are not the author of the command...", ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        try:
            if self.message:
                await self.message.edit(view=None)
        except:
            pass

class Choice3(BasicView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx, timeout=60)
        self.value = None

    async def on_timeout(self) -> None:
        try:
            if self.message:
                await self.message.edit(view=None)
        except:
            pass

    @discord.ui.button(emoji="<:one:1040409002552598549>", custom_id='Yes', style=discord.ButtonStyle.gray)
    async def one(self, interaction, button):
        self.value = 1
        self.stop()
    @discord.ui.button(emoji="<:two:1040409049465888858>", custom_id='No', style=discord.ButtonStyle.gray)
    async def two(self, interaction, button):
        self.value = 2
        self.stop()
    @discord.ui.button(emoji="<:three:1040409085574651914>", custom_id='noo', style=discord.ButtonStyle.gray)
    async def three(self, interaction, button):
        self.value = 3
        self.stop()
    @discord.ui.button(label="Cancel", custom_id='cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction, button):
        self.value = "cancel"
        self.stop()

class copyview(BasicView):
    def __init__(self, ctx: commands.Context, user: discord.Member):
        super().__init__(ctx, timeout=None)
        self.value = None
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(f"Only {str(self.user)} can interact with this message", ephemeral=True)
            return False
        return True

    @discord.ui.button(emoji="<:ticky:1154027584020021278>", custom_id='Yes', style=discord.ButtonStyle.green)
    async def dare(self, interaction, button):
        self.value = 'Yes'
        self.stop()

    @discord.ui.button(emoji="<:error:1153009680428318791>", custom_id='No', style=discord.ButtonStyle.danger)
    async def truth(self, interaction, button):
        self.value = 'No'
        self.stop()

class interface(discord.ui.View):
    def __init__(self, bot, ctx: commands.Context):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.bot = bot
        self.value = None
        self.vc: wavelink.Player = ctx.voice_client
    
    async def interaction_check(self, interaction: discord.Interaction):
        c = False
        for i in self.ctx.guild.me.voice.channel.members:
            if i.id == interaction.user.id:
                c = True
                break
        if c:
            return True
        else:
            await interaction.response.send_message(f"Um, Looks like you are not in the voice channel...", ephemeral=True)
            return False

    @discord.ui.button(label="Pause", custom_id='rp', style=discord.ButtonStyle.gray)
    async def rp(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = self.ctx
        if button.label == 'Pause':
            query = "SELECT * FROM  music WHERE guild_id = ?"
            val = (ctx.guild.id,)
            with sqlite3.connect('./database.sqlite3') as db:
                db.row_factory = sqlite3.Row
                cursor = db.cursor()
                cursor.execute(query, val)
                m_db = cursor.fetchone()
            embed = discord.Embed(
                    description=f"{ctx.author.mention} There must be a song or queue playing.", color=0xc283fe)
            if m_db is None:
                return await ctx.reply(embed=embed)
            if m_db['now_playing'] == "{}":
                return await ctx.reply(embed=embed)
            xd = literal_eval(m_db['now_playing'])
            x = datetime.datetime.now()
            xd['ptime'] = round(x.timestamp() - xd['starttime'])
            sql = (f"UPDATE music SET now_playing = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
            await ctx.voice_client.pause()
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            button.label = "Resume"
            button.style = discord.ButtonStyle.green
            await interaction.response.edit_message(view=self)
        else:
            query = "SELECT * FROM  music WHERE guild_id = ?"
            val = (ctx.guild.id,)
            with sqlite3.connect('./database.sqlite3') as db:
                db.row_factory = sqlite3.Row
                cursor = db.cursor()
                cursor.execute(query, val)
                m_db = cursor.fetchone()
            embed = discord.Embed(
                    description=f"{ctx.author.mention} There must be a song or queue playing.", color=0xc283fe)
            if m_db is None:
                return await ctx.reply(embed=embed)
            if m_db['now_playing'] == "{}":
                return await ctx.reply(embed=embed)
            xd = literal_eval(m_db['now_playing'])
            x = datetime.datetime.now()
            xd['starttime'] = round(x.timestamp() - xd['ptime'])
            xd['ptime'] = 0
            sql = (f"UPDATE music SET now_playing = ? WHERE guild_id = ?")
            val = (f"{xd}", ctx.guild.id)
            await ctx.voice_client.resume()
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            db.close()
            button.label = "Pause"
            button.style = discord.ButtonStyle.gray
            await interaction.response.edit_message(view=self)
        
    @discord.ui.button(label="Skip", custom_id='skip', style=discord.ButtonStyle.gray)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ctx.voice_client.pause()
        await interaction.message.delete()
        await play_next(self.bot, self.ctx, skip=True)
        self.stop()

    @discord.ui.button(label="Stop", custom_id='stop', style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = self.ctx
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            await ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await deletedb(ctx)
        query = "SELECT * FROM  '247' WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            if ctx.voice_client is not None:
                await ctx.voice_client.disconnect()
            c = self.bot.get_channel(m_db['channel_id'])
            vc: wavelink.Player = await c.connect(cls=wavelink.Player, self_deaf=True)
        await interaction.message.delete()
        em = discord.Embed(color=0x070606)
        em.set_footer(text="| Destroyed the queue and stopped the player!", icon_url=interaction.user.display_avatar.url)
        v = discord.ui.View()
        v.add_item(discord.ui.Button(label="Vote", url="https://top.gg/bot/880765863953858601/vote"))
        await interaction.channel.send(embed=em, view=v)
        self.stop()

    @discord.ui.button(label="Loop", custom_id='loop', style=discord.ButtonStyle.gray)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        ctx = self.ctx
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        l = m_db['loop']
        if l == 'n':
            await interaction.response.send_message(f"Looping songs", ephemeral=True)
            l = 's'
        elif l == 's':
            await interaction.response.send_message(f"Looping Queue", ephemeral=True)
            l = 'q'
        else:
            await interaction.response.send_message(f"Looping Nothing", ephemeral=True)
            l = 'n'
        sql = (f"UPDATE music SET loop = ? WHERE guild_id = ?")
        val = (f"{l}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @discord.ui.button(label="Queue", custom_id='q', style=discord.ButtonStyle.gray)
    async def queuee(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False, thinking=False)
        init = await interaction.channel.send(f"<:loading:1060851548869107782> Processing the command...", mention_author=False)
        ctx = self.ctx
        emb = discord.Embed(
            description=f"{ctx.author.mention} There are no songs in the queue",color=0xc283fe)
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is None:
            return await ctx.reply(embed=emb)
        if m_db['queue'] == "[]":
            return await ctx.reply(embed=emb)
        queue = literal_eval(m_db['queue'])
        ls, q = [], []
        count = 0
        for i in queue:
            song = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, i['uri'])
            count += 1
            tm = str(datetime.timedelta(seconds=song[0].duration))
            try:
                tm = tm[:tm.index(".")]
            except:
                tm = tm
            q.append(f"`[{'0' + str(count) if count < 10 else count}]` | [{song[0].title}](https://discord.gg/wb4UCU3m5z) - [{tm}]")
        for i in range(0, len(q), 10):
           ls.append(q[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=0xc283fe)
           embed.title = f"Current Queue - {count}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)

    @discord.ui.button(label="Volume up", custom_id='up', style=discord.ButtonStyle.green)
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        c = self.ctx.voice_client.volume
        if c <= 90:
            await self.ctx.voice_client.set_volume(c+10)
            await interaction.response.send_message(f"Changed the volume to {c+10}%", ephemeral=True)
        else:
            await self.ctx.voice_client.set_volume(100)
            await interaction.response.send_message(f"Changed the volume to 100%", ephemeral=True)

    @discord.ui.button(label="Volume Down", custom_id='down', style=discord.ButtonStyle.green)
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        c = self.ctx.voice_client.volume
        if c >= 10:
            await self.ctx.voice_client.set_volume(c-10)
            await interaction.response.send_message(f"Changed the volume to {c-10}%", ephemeral=True)
        else:
            await self.ctx.voice_client.set_volume(0)
            await interaction.response.send_message(f"Changed the volume to 0%", ephemeral=True)

async def play_next(self, ctx, skip: bool = None):
        try:
            bot = self.bot
        except:
            bot = self
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
            if m_db['queue'] == "[]":
                await deletedb(ctx)
                await ctx.voice_client.stop()
                em = discord.Embed(title="Queue concluded", description=f"Enjoyed listening music? Consider [voting us](https://top.gg/bot/880765863953858601/vote)", color=0x070606)
                em.set_footer(text="| No more songs left to play in queue.", icon_url=ctx.guild.me.display_avatar.url)
                v = discord.ui.View()
                v.add_item(discord.ui.Button(label="Vote", url="https://top.gg/bot/880765863953858601/vote"))
                return await ctx.reply(embed=em, view=v)
            xd = literal_eval(m_db['queue'])
            x = xd[0]
            track = await bot.wavelink.get_tracks(wavelink.YouTubeTrack, x['uri'])
            track = track[0]
            xd.pop(0)
            await nowplay(ctx, track, x['requester'])
            await queueupdate(ctx, xd)
            rid = x['requester']
        await ctx.voice_client.play(track)
        req = discord.utils.get(bot.users, id=rid)
        tm = str(datetime.timedelta(seconds=track.duration))
        try:
            tm = tm[:tm.index(".")]
        except:
            tm = tm
        emb = discord.Embed(title="Now Playing",
                            description=f"\n[{track.title}](https://discord.gg/wb4UCU3m5z) - [{tm}]", color=0xc283fe)
        if skip is not None:
            if skip:
                emb.set_author(name="| Skipped the song", icon_url=req.display_avatar.url)
        emb.set_footer(text=f"Requested by {str(req)}", icon_url=req.display_avatar.url)
        emb.timestamp= datetime.datetime.now() + datetime.timedelta(seconds=int(track.duration))
        v = interface(bot, ctx)
        init = await ctx.reply(embed=emb, mention_author=False, view=v)
        updatemsgid(ctx.guild.id, [ctx.channel.id, init.id])
        ctx.voice_client.ctx = ctx
        await v.wait()

def checkplaying(guild_id):
    query = "SELECT * FROM  music WHERE guild_id = ?"
    val = (guild_id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        m_db = cursor.fetchone()
    if m_db is None:
        return False
    else:
        return True

async def deletedb(ctx):
    query = "DELETE FROM music WHERE guild_id = ?"
    val = (ctx.guild.id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        m_db = cursor.fetchone()
    db.commit()
    cursor.close()
    db.close()

async def nowplay(ctx, data, id):
    query = "SELECT * FROM  music WHERE guild_id = ?"
    val = (ctx.guild.id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        m_db = cursor.fetchone()
    if m_db is None:
        xd = {}
        xd['uri'] = data.uri
        xd['requester'] = id
        x = datetime.datetime.now()
        xd['starttime'] = x.timestamp()
        xd['ptime'] = 0
        sql = (f"INSERT INTO music(guild_id, now_playing) VALUES(?, ?)")
        val = (ctx.guild.id, f"{xd}")
        cursor.execute(sql, val)
    else:
        xd = {}
        xd['uri'] = data.uri
        xd['requester'] = id
        x = datetime.datetime.now()
        xd['starttime'] = x.timestamp()
        xd['ptime'] = 0
        sql = (f"UPDATE music SET now_playing = ? WHERE guild_id = ?")
        val = (f"{xd}", ctx.guild.id)
        cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

async def queueupdate(ctx, data):
    query = "SELECT * FROM  music WHERE guild_id = ?"
    val = (ctx.guild.id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        m_db = cursor.fetchone()
    if m_db is None:
        sql = (f"INSERT INTO music(guild_id, queue) VALUES(?, ?)")
        val = (ctx.guild.id, f"{data}")
        cursor.execute(sql, val)
    else:
        sql = (f"UPDATE music SET queue = ? WHERE guild_id = ?")
        val = (f"{data}", ctx.guild.id)
        cursor.execute(sql, val)
    db.commit()
    cursor.close()
    db.close()

async def getqueue(ctx):
    query = "SELECT * FROM  music WHERE guild_id = ?"
    val = (ctx.guild.id,)
    with sqlite3.connect('./database.sqlite3') as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(query, val)
        m_db = cursor.fetchone()
    if m_db is None:
        return None
    return literal_eval(m_db['queue'])

async def pladd(self, ctx, query):
        query = query.strip('<>')
        if SPOTIFY_URL_REG.match(query):
            spoturl_check = SPOTIFY_URL_REG.match(query)
            search_type = spoturl_check.group('type')
            spotify_id = spoturl_check.group('id')

            if search_type == "playlist":
                try:
                    results = spotifyyy.Playlist(client=spotifyyy_client, data=await spotifyyy_http_client.get_playlist(spotify_id))
                    search_tracks = await results.get_all_tracks()
                except:
                    return await ctx.reply("I was not able to find this playlist! Please try again or use a different link.")
 
            elif search_type == "album":
                try:
                    results = await spotifyyy_client.get_album(spotify_id=spotify_id)
                    search_tracks = await results.get_all_tracks()
                except:
                    return await ctx.reply("I was not able to find this album! Please try again or use a different link.")
                    
            elif search_type == 'track':
                results = await spotify_client._search(query)
                tracks = results
            if search_type == 'track':
                pass
            else:
                tracks = []
                for track in search_tracks:
                    tracks.append(wavelink.Track(
                            id = 'spotify',
                            info={'title': track.name or 'Unknown', 'author': ', '.join(artist.name for artist in track.artists) or 'Unknown',
                                        'length': track.duration or 0, 'identifier': track.id or 'Unknown', 'uri': track.url or 'spotify',
                                        'isStream': False, 'isSeekable': False, 'position': 0, 'thumbnail': track.images[0].url if track.images else None},
                    ))
            
            if not tracks:
                return await ctx.reply("The URL you put is either not valid or doesn't exist!")
            
            count = 0
            queue = []
            for track in tracks:
                xdd = {}
                xdd['requester'] = ctx.author.id
                xdd['uri'] = track.uri
                queue.append(xdd)
                count+=1
            
        else:
            if query.lower() == "current":
                query2 = "SELECT * FROM  music WHERE guild_id = ?"
                val2 = (ctx.guild.id,)
                with sqlite3.connect('./database.sqlite3') as db:
                    db.row_factory = sqlite3.Row
                    cursor = db.cursor()
                    cursor.execute(query2, val2)
                    m_db = cursor.fetchone()
                if m_db is None:
                    return await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} No song/queue is currently played.", color=0xc283fe))
                else:
                    queue = await getqueue(ctx)
            else:
                if not URL_REG.match(query):
                    query = f'ytsearch:{query}'
                else:
                    return await ctx.send('No songs were found with that query. Please try again.', delete_after=15)
                tracks = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, query)
                if not tracks:
                    return await ctx.send('No songs were found with that query. Please try again.', delete_after=15)
                count = 0
                des = ""
                for i in tracks:
                    if count >= 3:
                        break
                    count+=1
                    des+=f"`[{'0' + str(count) if count < 10 else count}]` | [{i.title}](https://discord.gg/wb4UCU3m5z) - {i.author}\n\n"
                if False:
                    v = Choice3(ctx)
                    embed = discord.Embed(title="Select a song to add in your playlist", description=des, color=0xc283fe)
                    embed.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                    init = await ctx.reply(embed=embed, view=v)
                    await v.wait()
                    if v.value == 'cancel':
                        await init.delete()
                        return
                    val = int(v.value)-1
                    await init.delete()
                    search = tracks[val]
                search = tracks[0]
                count = 1
                queue = []
                xdd = {}
                xdd['requester'] = ctx.author.id
                xdd['uri'] = search.uri
                queue.append(xdd)
        return queue

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        invoke_without_command=True, aliases=['pl'], description="Shows the help menu for playlist commands"
    )
    async def playlist(self, ctx):
        prefix = ctx.prefix
        if prefix == f"<@{self.bot.user.id}> ":
            prefix = f"@{str(self.bot.user)} "
        anay = discord.utils.get(self.bot.users, id=978930369392951366)
        ls = ["playlist", "playlist add", "playlist remove", "playlist create", "playlist delete", "playlist copy", "playlist show"]
        des = ""
        for i in sorted(ls):
            cmd = self.bot.get_command(i)
            des += f"`{prefix}{i}`\n{cmd.description}\n\n"
        listem = discord.Embed(title=f"<:gateway_music:1040855483029913660> Playlist Commands", colour=0xc283fe,
                                     description=f"<...> Duty | [...] Optional\n\n{des}")
        listem.set_author(name=f"{str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        listem.set_footer(text=f"Made by stars.gg" ,  icon_url=anay.avatar.url)
        await ctx.send(embed=listem)
    
    @playlist.command(name="show", description="Shows your playlists")
    async def show(self, ctx: commands.Context, name: str=None):
        init = await ctx.reply(f"<:loading:1060851548869107782> Processing the command...", mention_author=False)
        query = "SELECT * FROM  pl WHERE user_id = ?"
        val = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            p_db = cursor.fetchone()
        if name is None:
            em_no = discord.Embed(description="You have no playlist", color=0xc283fe).set_footer(text=str(self.bot.user), icon_url=self.bot.user.avatar.url)
            if p_db is None:
                return await ctx.reply(embed=em_no)
            xd = literal_eval(p_db['pl'])
            if len(xd) == 0:
                return await ctx.reply(embed=em_no)
            else:
                ls, q = [], []
                count = 0
                for i in xd:
                    tm = 0
                    for j in xd[i]:
                        song = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, j['uri'])
                        tm += song[0].duration
                    tm = str(datetime.timedelta(seconds=tm))
                    try:
                        tm = tm[:tm.index(".")]
                    except:
                        tm = tm
                    count += 1
                    q.append(f"`[{'0' + str(count) if count < 10 else count}]` | [{i}](https://discord.gg/wb4UCU3m5z) - [{tm}]")
                for i in range(0, len(q), 10):
                    ls.append(q[i: i + 10])
                em_list = []
                no = 1
                for k in ls:
                    embed =discord.Embed(color=0xc283fe)
                    embed.title = f"{str(ctx.author)}'s Playlist - {count}"
                    embed.description = "\n".join(k)
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                    em_list.append(embed)
                    no+=1
                page = PaginationView(embed_list=em_list, ctx=ctx)
                await init.delete()
                await page.start(ctx)
        else:
            name = name.title()
            em_no = discord.Embed(description=f"You have no playlist named `{name}`", color=0xc283fe).set_footer(text=str(self.bot.user), icon_url=self.bot.user.avatar.url)
            if p_db is None:
                return await ctx.reply(embed=em_no)
            xd = literal_eval(p_db['pl'])
            if name not in xd:
                return await ctx.reply(embed=em_no)
            else:
                ls, q = [], []
                count = 0
                for i in xd[name]:
                    song = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, i['uri'])
                    tm = str(datetime.timedelta(seconds=song[0].duration))
                    try:
                        tm = tm[:tm.index(".")]
                    except:
                        tm = tm
                    count += 1
                    q.append(f"`[{'0' + str(count) if count < 10 else count}]` | [{song[0].title}](https://discord.gg/wb4UCU3m5z) - [{tm}]")
                for i in range(0, len(q), 10):
                    ls.append(q[i: i + 10])
                em_list = []
                no = 1
                for k in ls:
                    embed =discord.Embed(color=0xc283fe)
                    embed.title = f"{name} Playlist - {count}"
                    embed.description = "\n".join(k)
                    embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
                    em_list.append(embed)
                    no+=1
                page = PaginationView(embed_list=em_list, ctx=ctx)
                await init.delete()
                await page.start(ctx)

    @playlist.command(name="copy", description="Copies a playlist from another user's playlist")
    async def copy(self, ctx: commands.Context, name: str, *, user: discord.Member):
        name = name.title()
        query = "SELECT * FROM  pl WHERE user_id = ?"
        val = (user.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            p_db = cursor.fetchone()
        if p_db is None:
            return await ctx.reply(embed=discord.Embed(description=f"{user.mention} don't have any playlist named {name}", color=0xc283fe))
        else:
            xx = literal_eval(p_db['pl'])
            if name not in xx:
                return await ctx.reply(embed=discord.Embed(description=f"{user.mention} don't have any playlist named {name}", color=0xc283fe))
            else:
                v = copyview(ctx, user)
                em = discord.Embed(description=f"Do you want to allow {ctx.author.mention} to copy your playlist `{name}`?", color=0xc283fe)
                em.set_footer(text=str(self.bot.user), icon_url=self.bot.user.avatar.url)
                init = await ctx.send(f"{user.mention}", embed=em, view=v)
                await v.wait()
                if v.value == 'no':
                    await init.delete()
                    await ctx.reply("The owner of the playlist denied to copy playlist for you")
                if v.value == 'yes':
                    await init.delete()
                    query = "SELECT * FROM  pl WHERE user_id = ?"
                    val = (ctx.author.id,)
                    with sqlite3.connect('./database.sqlite3') as db:
                        db.row_factory = sqlite3.Row
                        cursor = db.cursor()
                        cursor.execute(query, val)
                        p_db = cursor.fetchone()
                    if p_db is None:
                        xxx = {}
                    else:
                        xxx = literal_eval(p_db['pl'])
                    if name in xxx:
                        vv = copyview(ctx, ctx.author)
                        init2 = await ctx.reply(f"You already have a playlist `{name}`\nDo you want to copy it with any other name?", view=vv)
                        await vv.wait()
                        if vv.value == 'no':
                            await init2.delete()
                        if vv.value == 'yes':
                            await init2.edit("What should be the name for the copied playlist?", view=None)
                            def message_check(m):
                                return ( 
                                    m.author.id == ctx.author.id
                                    and m.channel == ctx.channel
                                )
                            user_response = await self.bot.wait_for("message", check=message_check)
                            await user_response.delete()
                            await init2.delete()
                            name1 = user_response.content
                            try:
                                w = name1.index(" ")
                                name1 = name1[:w].strip()
                            except ValueError:
                                name1 = name
                            xxx[name1] = xx[name]
                    else:
                        name1 = name
                        xxx[name1] = xx[name]
                    if p_db is None:
                        sql = (f"INSERT INTO pl(user_id, pl) VALUES(?, ?)")
                        val = (ctx.author.id, f"{xxx}")
                        cursor.execute(sql, val)
                    else:
                        sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
                        val = (f"{xxx}", ctx.author.id)
                        cursor.execute(sql, val)
                    db.commit()
                    cursor.close()
                    db.close()
                    em = discord.Embed(description=f"Successfully copied a playlist `{name1}` from {user.mention} with {len(xx[name])} song(s)", color=0xc283fe)
                    em.set_footer(text=str(self.bot.user), icon_url=self.bot.user.avatar.url)
                    await ctx.reply(embed=em)

    @playlist.command(name="create", description="Creates a playlist for you")
    async def create(self, ctx: commands.Context, name: str, *, query: str):
        name = name.title()
        if "youtube.com" in query:
            return await ctx.reply("Songs from Youtube are not supported")
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query1, val1)
            p_db = cursor.fetchone()
        if p_db is not None:
            try:
                xx = literal_eval(p_db['pl'])
            except:
                xx = {}
            if name.title() in xx:
                return await ctx.reply(f"{ctx.author.mention} You already have a playlist named {name}")
        queue = await pladd(self, ctx, query)
        if p_db is None:
            xd = {}
            xd[name.title()] = queue
            sql = (f"INSERT INTO pl(user_id, pl) VALUES(?, ?)")
            val = (ctx.author.id, f"{xd}")
            cursor.execute(sql, val)
        else:
            xd = literal_eval(p_db['pl'])
            xd[name.title()] = queue
            sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
            val = (f"{xd}", ctx.author.id)
            cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} Created a playlist for you with name `{name.title()}` and {len(xd[name.title()])} Song(s)\nto play this playlist just type {ctx.prefix}play {name.title()}.", color=0xc283fe))
    
    @playlist.command(name="delete", description="Delete a playlist for you")
    async def delete(self, ctx: commands.Context, name: str):
        name = name.title()
        query = "SELECT * FROM  pl WHERE user_id = ?"
        val = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            p_db = cursor.fetchone()
        if p_db is None:
            return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name}")
        else:
            xx = literal_eval(p_db['pl'])
            if name.title() not in xx:
                return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name}")
            else:
                q = literal_eval(p_db['pl'])
                del q[name.title()]
                sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
                val = (f"{q}", ctx.author.id)
                cursor.execute(sql, val)
                db.commit()
                cursor.close()
                db.close()
                await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} Deleted your playlist with name `{name.title()}`", color=0xc283fe))
                
    @playlist.command(name="add", description="Adds a song/queue in your playlist")
    async def _add(self, ctx: commands.Context, name, *, query):
        name = name.title()
        if "youtube.com" in query:
            return await ctx.reply("Songs from Youtube are not supported")
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query1, val1)
            p_db = cursor.fetchone()
        if p_db is not None:
            xx = literal_eval(p_db['pl'])
            if name.title() not in xx:
                return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name.title()}")
        else:
            return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name.title()}")
        queue = await pladd(self, ctx, query)
        xx[name.title()] = xx[name.title()] + queue
        sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
        val = (f"{xx}", ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        await ctx.reply(embed=discord.Embed(description=f"{ctx.author.mention} Added {len(queue)} songs to your playlist with name `{name.title()}`", color=0xc283fe))
                
    @playlist.command(name="remove", description="Removes song(s) from your playlist")
    async def _remove(self, ctx: commands.Context, name, index, endindex=None):
        name = name.title()
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query1, val1)
            p_db = cursor.fetchone()
        if p_db is not None:
            xxx = literal_eval(p_db['pl'])
            if name.title() not in xxx:
                return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name.title()}")
        else:
            return await ctx.reply(f"{ctx.author.mention} You don't have any playlist named {name.title()}")
        xd = xxx[name.title()]
        if endindex is not None:
            if ((not index.isdigit()) or (int(index)) < 1 or (int(index) > len(xd)) or (not endindex.isdigit()) or (int(endindex)) < 1 or (int(endindex) > len(xd))):
                return await ctx.reply(f"{ctx.author.mention} Both the numbers should be between 1 and {len(xd)}")
            elif (int(endindex)<int(index)):
                return await ctx.reply(f"{ctx.author.mention} End index should be greater than start index")
            else:
                for i in reversed(range(int(index)-1, int(endindex)-1)):
                    xd.pop(i)
                await ctx.reply(f"{ctx.author.mention} Successfully removed {int(endindex)-int(index)} songs from your playlist `{name.title()}`")
        else:
            if ((not index.isdigit()) or (int(index)) < 1 or (int(index) > len(xd))):
                return await ctx.reply(f"{ctx.author.mention} The number should be between 1 and {len(xd)}")
            else:
                xd.pop(int(index)-1)
                await ctx.reply(f"{ctx.author.mention} Successfully removed 1 song from your playlist `{name.title()}`")
        xxx[name.title()] = xd
        sql = (f"UPDATE pl SET pl = ? WHERE user_id = ?")
        val = (f"{xxx}", ctx.author.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()

    @commands.command(name="24/7", aliases=['247'], description="Keeps the bot 24/7 in vc")
    @commands.has_permissions(manage_channels=True)
    async def _sss(self, ctx):
        c = await check_upgraded(ctx.guild.id)
        if not c:
            em = discord.Embed(description=f"You just tried to execute a premium command but this guild is not upgarded\nYou can buy bot's premium from the link given below or by creating a ticket in the [Support Server](https://discord.gg/wb4UCU3m5z)", color=0xc283fe).set_footer(text=f"{self.bot.user.name} Premium feature", icon_url=self.bot.user.avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Patreon", url="https://www.patreon.com/gateway_bot"))
            v.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/wb4UCU3m5z"))
            return await ctx.reply(embed=em, view=v)
        if not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        query = "SELECT * FROM  '247' WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is None:
            if not getattr(ctx.guild.me.voice, "channel", None):
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
            sql = (f"INSERT INTO '247'(guild_id, channel_id) VALUES(?, ?)")
            val = (ctx.guild.id, ctx.author.voice.channel.id)
            cursor.execute(sql, val)
            await ctx.reply(f"Now i will stay connected 24/7 in {ctx.author.voice.channel.mention}")
        else:
            sql = (f"DELETE FROM '247' WHERE guild_id = ?")
            val = (ctx.guild.id,)
            cursor.execute(sql, val)
            await ctx.reply(f"Now i will not stay connected 24/7 in {ctx.author.voice.channel.mention}")
        db.commit()
        cursor.close()
        db.close()
    
    @commands.command(name="forcefix")
    async def forcefix(self, ctx: commands.Context):
        try:
            await ctx.voice_client.disconnect()
            await ctx.send("Fixed the player")
        except:
            await ctx.send("Error occured")

    @commands.command(name="play",aliases=["p"], description = "Plays a song")
    async def play(self, ctx, *, query: str):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        elif ctx.author.voice.channel.id != ctx.guild.me.voice.channel.id:
            if checkplaying(ctx.guild.id):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} Songs are already being played in {ctx.guild.me.voice.channel.mention}.", color=0xc283fe)
                return await ctx.reply(embed=embed)
            else:
                await ctx.voice_client.disconnect()
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
        else:
            vc: wavelink.Player = ctx.voice_client
        if "youtube.com" in query:
            return await ctx.reply("Songs from Youtube are not supported")
        query1 = "SELECT * FROM  pl WHERE user_id = ?"
        val1 = (ctx.author.id,)
        with sqlite3.connect('./database.sqlite3') as db1:
            db1.row_factory = sqlite3.Row
            cursor1 = db1.cursor()
            cursor1.execute(query1, val1)
            p_db = cursor1.fetchone()
        x = {}
        if p_db is None:
            pass
        else:
            x = literal_eval(p_db['pl'])
        if query.strip().title() in x:
            if not checkplaying(ctx.guild.id):
                tracks = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, x[query.title()][0]['uri'])
                await nowplay(ctx, tracks[0], ctx.author.id)
                await queueupdate(ctx, x[query.title()][1:])
                embe = discord.Embed(title="Now Playing", description=f"\n[{tracks[0].title}](https://discord.gg/wb4UCU3m5z)\nAnd`{len(x[query.title()])-1}` Songs added to queue", color=0xc283fe)
                embe.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                embe.timestamp = datetime.datetime.now() + datetime.timedelta(seconds=int(tracks[0].duration))
                t = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, tracks[0].uri)
                await vc.play(tracks[0])
                v = interface(self.bot, ctx)
                init = await ctx.reply(embed=embe, mention_author=False, view=v)
                updatemsgid(ctx.guild.id, [ctx.channel.id, init.id])
                await v.wait()
            else:
                xd = await getqueue(ctx)
                await queueupdate(ctx, xd + x[query.title()])
                await ctx.reply(f"`{len(x[query.title()])}` Songs added to Queue", mention_author=False)
            vc.ctx = ctx
            return
        else:
            pass
        query = query.strip('<>')
        if SPOTIFY_URL_REG.match(query):
            spoturl_check = SPOTIFY_URL_REG.match(query)
            search_type = spoturl_check.group('type')
            spotify_id = spoturl_check.group('id')

            if search_type == "playlist":
                try:
                    results = spotifyyy.Playlist(client=spotifyyy_client, data=await spotifyyy_http_client.get_playlist(spotify_id))
                    search_tracks = await results.get_all_tracks()
                except:
                    return await ctx.reply("I was not able to find this playlist! Please try again or use a different link.")
 
            elif search_type == "album":
                try:
                    results = await spotifyyy_client.get_album(spotify_id=spotify_id)
                    search_tracks = await results.get_all_tracks()
                except:
                    return await ctx.reply("I was not able to find this album! Please try again or use a different link.")
                    
            elif search_type == 'track':
                results = await spotify_client._search(query)
                tracks = results
            if search_type == 'track':
                pass
            else:
                tracks = []
                for track in search_tracks:
                    tracks.append(wavelink.Track(
                            id = 'spotify',
                            info={'title': track.name or 'Unknown', 'author': ', '.join(artist.name for artist in track.artists) or 'Unknown',
                                        'length': track.duration or 0, 'identifier': track.id or 'Unknown', 'uri': track.url or 'spotify',
                                        'isStream': False, 'isSeekable': False, 'position': 0, 'thumbnail': track.images[0].url if track.images else None},
                    ))

            if not tracks:
                return await ctx.reply("The URL you put is either not valid or doesn't exist!")
                

            if search_type == "playlist" or search_type == "album":
                count = 0
                xd = []
                for track in tracks:
                    xdd = {}
                    xdd['requester'] = ctx.author.id
                    xdd['uri'] = track.uri
                    xd.append(xdd)
                    count+=1
                if not checkplaying(ctx.guild.id):
                    await nowplay(ctx, tracks[0], ctx.author.id)
                    await queueupdate(ctx, xd[1:])
                    embe = discord.Embed(title="Now Playing", description=f"\n[{tracks[0].title}](https://discord.gg/wb4UCU3m5z)\nAnd`{count-1}` Songs added to queue", color=0xc283fe)
                    embe.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                    embe.timestamp = datetime.datetime.now() + datetime.timedelta(seconds=int(tracks[0].duration))
                    t = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, tracks[0].uri)
                    await vc.play(t[0])
                    v = interface(self.bot, ctx)
                    init = await ctx.reply(embed=embe, view=v, mention_author=False)
                    updatemsgid(ctx.guild.id, [ctx.channel.id, init.id])
                    await v.wait()
                else:
                    xddd = await getqueue(ctx)
                    await queueupdate(ctx, xddd+xd)
                    await ctx.reply(f"`{count}` Songs added to Queue", mention_author=False)
            else:
                tm = str(datetime.timedelta(seconds=tracks[0].duration))
                try:
                    tm = tm[:tm.index(".")]
                except:
                    tm = tm
                if checkplaying(ctx.guild.id):
                    xd = []
                    xdd = {}
                    xdd['requester'] = ctx.author.id
                    xdd['uri'] = track.uri
                    xd.append(xdd)
                    xdddd = await getqueue(ctx)
                    await queueupdate(ctx, xdddd+xd)
                    await vc.queue.put_wait(tracks[0])
                    emb = discord.Embed(description=f"\nAdded [{tracks[0].title}](https://discord.gg/wb4UCU3m5z) - [{tm}] to the queue.", color=0xc283fe)
                    emb.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                    await ctx.reply(embed=emb, mention_author=False)
                else:
                    await nowplay(ctx, tracks[0], ctx.author.id)
                    await vc.play(tracks[0])
                    embe = discord.Embed(title="Now Playing", description=f"\n[{tracks[0].title}](https://discord.gg/wb4UCU3m5z) - [{tm}]", color=0xc283fe)
                    embe.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                    embe.timestamp = datetime.datetime.now() + datetime.timedelta(seconds=int(tracks[0].duration))
                    v = interface(self.bot, ctx)
                    init = await ctx.reply(embed=embe, view=v, mention_author=False)
                    updatemsgid(ctx.guild.id, [ctx.channel.id, init.id])

        else:
            if not URL_REG.match(query):
                query = f'ytsearch:{query}'
            else:
                return await ctx.send('No songs were found with that query. Please try again.', delete_after=15)
            tracks = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, query)
            if not tracks:
                return await ctx.send('No songs were found with that query. Please try again.', delete_after=15)
            count = 0
            des = ""
            for i in tracks:
                if count >= 3:
                    break
                count+=1
                des+=f"`[{'0' + str(count) if count < 10 else count}]` | [{i.title}](https://discord.gg/6Q9D7R8hYc) - {i.author}\n\n"
            if False:
                v = Choice3(ctx)
                embed = discord.Embed(title="Select a song to play", description=des, color=0xc283fe)
                embed.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                init = await ctx.reply(embed=embed, view=v, mention_author=False)
                await v.wait()
                if v.value == 'cancel':
                    await init.delete()
                    return
                val = int(v.value)-1
                await init.delete()
                search = tracks[val]
            search = tracks[0]
            tm = str(datetime.timedelta(seconds=search.duration))
            try:
                tm = tm[:tm.index(".")]
            except:
                tm = tm
            if not checkplaying(ctx.guild.id):
                await nowplay(ctx, search, ctx.author.id)
                await vc.play(search)
                embe = discord.Embed(title="Now Playing", description=f"\n[{search.title}](https://discord.gg/wb4UCU3m5z) - [{tm}]", color=0xc283fe)
                embe.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                embe.timestamp = datetime.datetime.now() + datetime.timedelta(seconds=int(search.duration))
                v = interface(self.bot, ctx)
                init = await ctx.reply(embed=embe, view=v, mention_author=False)
                updatemsgid(ctx.guild.id, [ctx.channel.id, init.id])
                await v.wait()
            else:
                xd = []
                xdd = {}
                xdd['requester'] = ctx.author.id
                xdd['uri'] = search.uri
                xd.append(xdd)
                xdddd = await getqueue(ctx)
                if xdddd is None:
                    xdddd=[]
                await queueupdate(ctx, xdddd+xd)
                await vc.queue.put_wait(search)
                emb = discord.Embed(description=f"\nAdded [{search.title}](https://discord.gg/wb4UCU3m5z) - [{tm}] to the queue.", color=0xc283fe)
                emb.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
                await ctx.reply(embed=emb, mention_author=False)
        vc.ctx = ctx
        
    @play.autocomplete("query")
    async def command_autocomplete(self, interaction: discord.Interaction, needle: str):
        ctx = await self.bot.get_context(interaction, cls=commands.Context)
        if needle:
            tracks = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, f'ytsearch:{needle}')
            if len(tracks) == 0:
                return []
            c = 0
            ls = []
            for i in tracks:
                if c>=10:
                    break
                c+=1
                ls.append(i.title)
            return [
                app_commands.Choice(name=cog_name.title(), value=cog_name)
                for cog_name in sorted(ls)
            ][:25]
        else:
            lss = ['Love', 'Lofi', 'party', 'punjabi', 'Hindi chill', 'English soft']
            pls = [
                app_commands.Choice(name="Love Songs", value="auto: https://open.spotify.com/playlist/37i9dQZF1DXbQDZkQM83q7"),
                app_commands.Choice(name="Sad Songs", value="auto: https://open.spotify.com/playlist/37i9dQZF1DXdFesNN9TzXT"),
                app_commands.Choice(name="Chillin Mood", value="auto: https://open.spotify.com/playlist/37i9dQZF1DWTwzVdyRpXm1"),
                app_commands.Choice(name="Valentine's Special", value="auto: https://open.spotify.com/playlist/37i9dQZF1DX14CbVHtvHRB")
            ]
            for i in lss:
                s = list(self.bot.sp.search(q=i, type='playlist', market="IN", limit=1)['playlists']['items'])
                random.shuffle(s)
                c = 0
                for i in s:
                    if c >=5:
                        break
                    else:
                        c+=1
                        pls.append(app_commands.Choice(name=i['name'], value=f"auto: https://open.spotify.com/playlist/{i['id']}"))
            pls = random.sample(pls, 20)
            query1 = "SELECT * FROM  pl WHERE user_id = ?"
            val1 = (ctx.author.id,)
            with sqlite3.connect('./database.sqlite3') as db1:
                db1.row_factory = sqlite3.Row
                cursor1 = db1.cursor()
                cursor1.execute(query1, val1)
                p_db = cursor1.fetchone()
            if p_db is None:
                return pls
            else:
                x = literal_eval(p_db['pl'])
            if x == "{}":
                return pls
            ls = []
            for i in x:
                ls.append(i)
            ls = [
                app_commands.Choice(name=f"{cog_name.title()} Playlist Made by you", value=cog_name)
                for cog_name in sorted(ls)
            ]
            if len(ls) < 20:
                xx = 20-len(ls)
                pls = random.sample(pls, xx)
                return ls+pls
            else:
                return ls[:25]
    @commands.command(name="current", aliases=['now'], description = "Gives you details of the current song")
    async def current(self, ctx):
        
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        embed = discord.Embed(
                description=f"{ctx.author.mention} No song is currently played.", color=0xc283fe)
        if m_db is None:
            return await ctx.reply(embed=embed)
        if m_db['now_playing'] == "{}":
            return await ctx.reply(embed=embed)
        xd = literal_eval(m_db['now_playing'])
        now = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, xd['uri'])
        now = now[0]
        x = datetime.datetime.now()
        requester = discord.utils.get(self.bot.users, id=xd['requester'])
        if m_db['loop'] == 'n':
            loop = None
        elif m_db['loop'] == 's':
            loop = "Song"
        else:
            loop = "Queue"
        if xd['ptime'] != 0:
            embed = discord.Embed(title=f"Current Song", description=f"Name: `{now.title}`\nRequested By: {requester.mention}\nTime: {round(xd['ptime'])}/{round(now.duration)} Seconds\nPaused: True\nLooping: {loop}\nVolume: {vc.volume}%", color=0xc283fe)
        else:
            embed = discord.Embed(title=f"Current Song", description=f"Name: `{now.title}`\nRequested By: {requester.mention}\nTime: {round(x.timestamp() - xd['starttime'])}/{round(now.duration)} Seconds\nPaused: False\nLooping: {loop}\nVolume: {vc.volume}%", color=0xc283fe)
        embed.set_author(name=f"{str(self.bot.user)}", icon_url=f"{self.bot.user.avatar.url}")
        embed.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=f"{ctx.author.display_avatar.url}")
        await ctx.reply(embed=embed)
    
    @commands.command(description = "Changes the loop setting")
    async def loop(self, ctx: commands.Context, option: str = None):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        embed = discord.Embed(
                description=f"{ctx.author.mention} There must be a song or queue playing.", color=0xc283fe)
        if m_db is None:
            return await ctx.reply(embed=embed)
        if m_db['now_playing'] == "{}":
            return await ctx.reply(embed=embed)
        opt = ['s', 'q', 'n', 'song', 'queue', 'none']
        if option is None:
            option = 'n'
        else:
            if option.lower() not in opt:
                return await ctx.reply("There are only 3 options for looping: None, Song or Queue")
            option = option[0]
        sql = (f"UPDATE music SET loop = ? WHERE guild_id = ?")
        val = (f"{option}", ctx.guild.id)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        if option == 'n':
            await ctx.reply("Loop is set to None.")
        if option == 's':
            await ctx.reply("Looping song.")
        if option == 'q':
            await ctx.reply("Looping queue.")

    @commands.command(description = "Searches a song")
    async def search(self, ctx, *, args):
        init = await ctx.reply(f"<:loading:1060851548869107782> Processing the command...", mention_author=False)
        tracks = await self.bot.wavelink.get_tracks(wavelink.Track, f'ytsearch:{args}')
        if len(tracks) == 0:
            return await ctx.reply(f"Nothing found for `{args}`")
        count = 1
        des = ""
        for i in tracks:
            if count > 10:
                break
            else:
                des+=f"`[{'0' + str(count) if count < 10 else count}]` | [{i.title}]({i.uri}) - {i.author}\n"
                count+=1
        embed = discord.Embed(title=f"Results of searching {args}", description=des, color=0xc283fe)
        embed.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        await init.delete()
        await ctx.reply(embed=embed)

    @commands.command(name="queue", description = "Shows you the current queue")
    async def queue(self, ctx):
        init = await ctx.reply(f"<:loading:1060851548869107782> Processing the command...", mention_author=False)
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        elif not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(
                description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        emb = discord.Embed(
            description=f"{ctx.author.mention} There are no songs in the queue",color=0xc283fe)
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is None:
            await init.delete()
            return await ctx.reply(embed=emb)
        if m_db['queue'] == "[]":
            await init.delete()
            return await ctx.reply(embed=emb)
        queue = literal_eval(m_db['queue'])
        ls, q = [], []
        count = 0
        for i in queue:
            song = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, i['uri'])
            tm = str(datetime.timedelta(seconds=song[0].duration))
            try:
                tm = tm[:tm.index(".")]
            except:
                tm = tm
            count += 1
            q.append(f"`[{'0' + str(count) if count < 10 else count}]` | [{song[0].title}](https://discord.gg/wb4UCU3m5z) - [{tm}]")
        for i in range(0, len(q), 10):
           ls.append(q[i: i + 10])
        em_list = []
        no = 1
        for k in ls:
           embed =discord.Embed(color=0xc283fe)
           embed.title = f"Current Queue - {count}"
           embed.description = "\n".join(k)
           embed.set_footer(text=f"{self.bot.user.name} • Page {no}/{len(ls)}", icon_url=self.bot.user.display_avatar.url)
           em_list.append(embed)
           no+=1
        page = PaginationView(embed_list=em_list, ctx=ctx)
        await init.delete()
        await page.start(ctx)
    
    @commands.command(name="qclear", description="Clears the current queue")
    async def clear(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        await queueupdate(ctx, "[]")
        return await ctx.reply("Cleared the queue successfully")
    
    @commands.command(name="remove", description="Remove a song from the current queue")
    async def remove(self, ctx: commands.Context, index: str):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        xd = await getqueue(ctx)
        if (
            (not index.isdigit()) or 
            (int(index)) < 1 or 
            (int(index) > len(xd))
        ):
            return await ctx.send(f"{ctx.author.mention} The index should be a number between 1 and {len(xd)} position!")
        xd.pop(int(index)-1)
        await queueupdate(ctx, xd)
        await ctx.reply(f"Successfully removed the song at index number `{index}`")
    
    @commands.command(name="moveto", aliases=['skipto'], description="Move the player to different position")
    async def moveto(self, ctx: commands.Context, index: str):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        else:
            vc: wavelink.Player = ctx.voice_client
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        xd = await getqueue(ctx)
        if (
            (not index.isdigit()) or 
            (int(index)) < 1 or 
            (int(index) > len(xd))
        ):
            return await ctx.send(f"{ctx.author.mention} The index should be a number between 1 and {len(xd)} position!")
        xd = xd[int(index)-2:]
        await ctx.voice_client.pause()
        await queueupdate(ctx, xd)
        await play_next(self, ctx)

    @commands.command(name="stop", description = "Stops the song")
    async def stop(self, ctx: commands.Context):
        
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            await ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await deletedb(ctx)
            em = discord.Embed(color=0x070606)
            em.set_footer(text="| Destroyed the queue and stopped the player!", icon_url=ctx.author.display_avatar.url)
            v = discord.ui.View()
            v.add_item(discord.ui.Button(label="Vote", url="https://top.gg/bot/880765863953858601/vote"))
            await ctx.reply(embed=em, view=v)
            d = getmsgid(ctx.guild.id)
            if d is not None:
                try:
                    channel = self.bot.get_channel(d[0])
                    msg = await channel.fetch_message(d[1])
                    await msg.delete()
                except:
                    pass
        else:
            em = discord.Embed(color=0xff0000)
            em.set_footer(text="| The player is already stopped", icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=em)
        query = "SELECT * FROM  '247' WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            if ctx.voice_client is not None:
                await ctx.voice_client.stop()
                await ctx.voice_client.disconnect()
            c = self.bot.get_channel(m_db['channel_id'])
            time.sleep(15)
            vc: wavelink.Player = await c.connect(cls=wavelink.Player, self_deaf=True)

    @commands.command(name="pause", description = "Pauses the song")
    async def pause(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        embed = discord.Embed(
                description=f"{ctx.author.mention} There must be a song or queue playing.", color=0xc283fe)
        if m_db is None:
            return await ctx.reply(embed=embed)
        if m_db['now_playing'] == "{}":
            return await ctx.reply(embed=embed)
        xd = literal_eval(m_db['now_playing'])
        x = datetime.datetime.now()
        xd['ptime'] = round(x.timestamp() - xd['starttime'])
        sql = (f"UPDATE music SET now_playing = ? WHERE guild_id = ?")
        val = (f"{xd}", ctx.guild.id)
        await ctx.voice_client.pause()
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        em = discord.Embed(color=0xff0000)
        em.set_footer(text="| Paused the player", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name="resume", aliases=["continue"], description = "Resumes the song")
    async def resume(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        embed = discord.Embed(
                description=f"{ctx.author.mention} There must be a song or queue playing.", color=0xc283fe)
        if m_db is None:
            return await ctx.reply(embed=embed)
        if m_db['now_playing'] == "{}":
            return await ctx.reply(embed=embed)
        xd = literal_eval(m_db['now_playing'])
        x = datetime.datetime.now()
        xd['starttime'] = round(x.timestamp() - xd['ptime'])
        xd['ptime'] = 0
        sql = (f"UPDATE music SET now_playing = ? WHERE guild_id = ?")
        val = (f"{xd}", ctx.guild.id)
        await ctx.voice_client.resume()
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        em = discord.Embed(color=0x070606)
        em.set_footer(text="| Resumed the player", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name="next", aliases=['skip'], pass_context=True, description = "Plays the next song")
    async def skip(self, ctx: commands.Context):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        if not ctx.voice_client:
            return await ctx.reply("Not in a voice channel.")
        await ctx.voice_client.pause()
        d = getmsgid(ctx.guild.id)
        channel = self.bot.get_channel(d[0])
        msg = await channel.fetch_message(d[1])
        await msg.delete()
        await play_next(self.bot, ctx, skip=True)

    @commands.command(name="disconnect", aliases=["dc"], description = "Disconnects from voice channel")
    async def disconnect(self, ctx: commands.Context):
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        if not ctx.voice_client:
            return await ctx.reply("Already disconnected from the voice channel.")
        await ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            await deletedb(ctx)
            d = getmsgid(ctx.guild.id)
            if d is not None:
                try:
                    channel = self.bot.get_channel(d[0])
                    msg = await channel.fetch_message(d[1])
                    await msg.delete()
                except:
                    pass
        em = discord.Embed(color=0x070606)
        em.set_footer(text="| Destroyed the queue and left the voice channel!", icon_url=ctx.author.display_avatar.url)
        v = discord.ui.View()
        v.add_item(discord.ui.Button(label="Vote", url="https://top.gg/bot/880765863953858601/vote"))
        v.add_item(discord.ui.Button(label="Premium", url="https://www.patreon.com/gateway_bot/membership"))
        await ctx.reply(embed=em, view=v)
        query = "SELECT * FROM  '247' WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            if ctx.guild.me.voice is not None:
                await ctx.voice_client.disconnect()
            c = self.bot.get_channel(m_db['channel_id'])
            time.sleep(15)
            vc: wavelink.Player = await c.connect(cls=wavelink.Player, self_deaf=True)

    @commands.command(name="seek", description = "Changes the position of song")
    async def seek(self, ctx: commands.Context, time):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        query = "SELECT * FROM  music WHERE guild_id = ?"
        val = (ctx.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        embed = discord.Embed(
                description=f"{ctx.author.mention} There must be a song or queue playing.", color=0xc283fe)
        if m_db is None:
            return await ctx.reply(embed=embed)
        if m_db['now_playing'] == "{}":
            return await ctx.reply(embed=embed)
        xd = literal_eval(m_db['now_playing'])
        track = await self.bot.wavelink.get_tracks(wavelink.YouTubeTrack, xd['uri'])
        if (
            (not time.isdigit()) or 
            (int(time)) < 0 or 
            (int(time) > track[0].duration)
        ):
            return await ctx.send(f"{ctx.author.mention} The time should be a number between 0 and {track[0].duration} seconds!")
        x = datetime.datetime.now()
        time = int(time)
        tt = round(x.timestamp() - xd['starttime'])
        if round(time) > tt:
            xd['starttime'] = xd['starttime'] - (round(time)-tt)
        elif round(time) < tt:
            xd['starttime'] = xd['starttime'] + (tt-round(time))
        else:
            xd['starttime'] = xd['starttime']
        sql = (f"UPDATE music SET now_playing = ? WHERE guild_id = ?")
        val = (f"{xd}", ctx.guild.id)
        await ctx.voice_client.seek(int(time)*1000)
        cursor.execute(sql, val)
        db.commit()
        cursor.close()
        db.close()
        em = discord.Embed(color=0x070606)
        em.set_footer(text=f"| Seeked the song to {time} seconds.!", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=em)
    
    @commands.command(name = "volume", aliases=['v'], description = "Change the bot's volume.")
    async def volume(self, ctx: commands.Context, volume):
        if not ctx.voice_client:
            embed = discord.Embed(
                description=f"{ctx.author.mention} I am not connected to any of the voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        c = False
        for i in ctx.guild.me.voice.channel.members:
            if i.id == ctx.author.id:
                c = True
                break
        if c:
            pass
        else:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
            else:
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to the same voice channel.", color=0xc283fe)
            return await ctx.reply(embed=embed)
        if (
            (not volume.isdigit()) or 
            (int(volume)) < 0 or 
            (int(volume) > 100)
        ):
            return await ctx.send(f"{ctx.author.mention} The volume should be a number between 0 and 100!")
        volume = int(volume)
        await ctx.voice_client.set_volume(volume)
        em = discord.Embed(color=0x070606)
        em.set_footer(text=f"| Changed the volume to {volume}%", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=em)

    @commands.command(name="connect",aliases=["join", "j"], description = "Joins a voice channel")
    async def join(self, ctx: commands.Context, channel: typing.Optional[discord.VoiceChannel]):
        
        if channel is None:
            if not getattr(ctx.author.voice, "channel", None):
                embed = discord.Embed(
                    description=f"{ctx.author.mention} You are not connected to any of the voice channel.", color=0xc283fe)
                return await ctx.reply(embed=embed)
            else:
                channel = ctx.author.voice.channel
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)
        if player is not None:
            if player.is_connected():
                return await ctx.reply("I am already connected to a voice channel.")
        vc: wavelink.player = await channel.connect(cls=wavelink.Player, self_deaf=True)
        mbed=discord.Embed(description=f"Gateway Joins {channel.mention}", color=0xc283fe)
        mbed.set_footer(text=f"Requested By {str(ctx.author)}", icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=mbed)
	
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        guild = member.guild
        if member.id != self.bot.user.id:
            return
        node = wavelink.NodePool.get_node()
        player = node.get_player(guild)
        if after.channel is None:
            if player.is_connected():
                await player.stop()
                await player.disconnect()
        else:
            return
        query = "SELECT * FROM music WHERE guild_id = ?"
        val = (member.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            query = "DELETE FROM music WHERE guild_id =?"
            cursor.execute(query,val)
        db.commit()
        cursor.close()
        db.close()
        d = getmsgid(member.guild.id)
        if d is not None:
            try:
                channel = self.bot.get_channel(d[0])
                msg = await channel.fetch_message(d[1])
                await msg.delete()
            except:
                pass
        query = "SELECT * FROM  '247' WHERE guild_id = ?"
        val = (member.guild.id,)
        with sqlite3.connect('./database.sqlite3') as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute(query, val)
            m_db = cursor.fetchone()
        if m_db is not None:
            time.sleep(15)
            c = self.bot.get_channel(m_db['channel_id'])
            pass

async def setup(bot):
	await bot.add_cog(music(bot))

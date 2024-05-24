from __future__ import annotations

import discord
import aiohttp
import io
import random
import datetime
import time
import json
from discord.ext import commands

class nsfw(commands.Cog):
    """Want some fun? These are best commands! :') :warning: 18+"""

    def __init__(self, bot):
        self.bot = bot

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{NO ONE UNDER EIGHTEEN SYMBOL}")

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def anal(self, ctx):
        """To get Random Anal"""
        url = "https://nekobot.xyz/api/image"
        params = {"type": "anal"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(title="Anal", color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def gonewild(self, ctx):
        """
        To get Random GoneWild
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "gonewild"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def hanal(self, ctx):
        """To get Random Hentai Anal"""
        url = "https://nekobot.xyz/api/image"
        params = {"type": "hanal"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def hentai(self, ctx):
        """To get Random Hentai"""
        url = "https://nekobot.xyz/api/image"
        params = {"type": "hentai"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def holo(self, ctx):
        """
        To get Random Holo
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "holo"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def neko(self, ctx):
        """
        To get Random Neko
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "neko"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def hneko(self, ctx):
        """
        To get Random Hneko
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "hneko"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def hkitsune(self, ctx):
        """
        To get Random Hkitsune
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "hkitsune"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def kemonomimi(self, ctx):
        """
        To get Random Kemonomimi
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "kemonomimi"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def pgif(self, ctx):
        """
        To get Random PornGif
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "pgif"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command(name="4k")
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def _4k(self, ctx):
        """
        To get Random 4k
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "4k"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def kanna(self, ctx):
        """
        To get Random Kanna
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "kanna"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def ass(self, ctx):
        """
        To get Random Ass
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "ass"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def pussy(self, ctx):
        """
        To get Random Pussy
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "pussy"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def thigh(self, ctx):
        """
        To get Random Thigh
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "thigh"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def hthigh(self, ctx):
        """
        To get Random Hentai Thigh
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "hthigh"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def paizuri(self, ctx):
        """
        To get Random Paizuri
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "paizuri"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def tentacle(self, ctx):
        """
        To get Random Tentacle Porn
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "tentacle"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def boobs(self, ctx):
        """
        To get Random Boobs
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "boobs"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def hboobs(self, ctx):
        """
        To get Random Hentai Boobs
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "hboobs"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def yaoi(self, ctx):
        """
        To get Random Yaoi
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "yaoi"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def hmidriff(self, ctx):
        """
        To get Random Hmidriff
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "hmidriff"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def hass(self, ctx):
        """
        To get Random Hentai Ass
        """
        url = "https://nekobot.xyz/api/image"
        params = {"type": "hass"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["message"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command(aliases=["randnsfw"])
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def randomnsfw(self, ctx, *, subreddit: str = None):
        """
        To get Random NSFW from subreddit.
        """
        if subreddit is None:
            subreddit = "NSFW"
        end = time() + 60
        while time() < end:
            url = f"https://memes.blademaker.tv/api/{subreddit}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status == 200:
                        res = await r.json()
                    else:
                        return
            if res["nsfw"]:
                break

        img = res["image"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

    @commands.command()
    @commands.is_nsfw()
    @commands.bot_has_permissions(embed_links=True)
    async def random(self, ctx):
        """
        Best command I guess. It return random ^^
        """
        async with aiohttp.ClientSession() as session:
            async with session.get("https://scathach.redsplit.org/v3/nsfw/gif/") as r:
                if r.status == 200:
                    res = await r.json()
                else:
                    return

        img = res["url"]

        em = discord.Embed(color=0xc283fe)
        em.set_footer(text=f"{ctx.author.name}")
        em.set_image(url=img)

        await ctx.reply(embed=em)

async def setup(bot):
    await bot.add_cog(nsfw(bot))
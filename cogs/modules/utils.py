import discord, json, datetime, aiohttp, sys, io, typing
from datetime import datetime
import button_paginator as pg
import yarl

paginator = pg

class Colors: 
    """Just colors"""
    red = 0xffffff
    green = 0xffffff
    yellow = 0xffffff
    gold = 0xb4baf7
    default = 0x495063
    rainbow = 0x2f3136

class Emojis:
    """Just emojis"""
    check = "<:greenTick:1230421239634595860>"
    wrong = "<:redTick:1230421267514003457>"
    warning = "<:rival_warning:1230421852770271272>"
    spotify_emote = "<:emoji_15:1231454735215628299>"


class Func:
 def ordinal(num: int):
   """Convert from number to ordinal (10 - 10th)""" 
   num = str(num) 
   if num in ["11", "12", "13"]:
       return num + "th"
   if num.endswith("1"):
      return num + "st"
   elif num.endswith("2"):
      return num + "nd"
   elif num.endswith("3"): 
       return num + "rd"
   else: return num + "th"    

class Database:
    def get(self, filename: str = None):

        with open(f"{sys.path[0]}/db/{filename}.json", "r") as file:
            data = json.load(file)
        file.close()
        return data

    def put(self, data, filename: str = None):

        with open(f"{sys.path[0]}/db/{filename}.json", "w") as file:
            json.dump(data, file, indent=4)
        file.close()
        return

async def file(url: str, fn: str = None, filename: str = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.read()
    
async def aiter(
    iterable: typing.Iterator[typing.Any],
) -> typing.AsyncIterator[typing.Any]:
    for i in iterable:
        yield i

def read_json(filename: str):
    return Database().get(filename)


def write_json(data, filename: str):
    return Database().put(data, filename)


async def get_parts(params):
    params = params.replace("{embed}", "")
    return [p[1:][:-1] for p in params.split("$v")]

async def getwhi(query):

    url = f"https://weheartit.com/search/entries?query={query.replace(' ', '+')}"
    from bs4 import BeautifulSoup

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as x:
            soup = BeautifulSoup(await x.text(), features="html.parser")
            divs = str(soup.find_all("div", class_="entry grid-item"))
            soup2 = BeautifulSoup(divs, features="html.parser")
            badge = soup2.find_all(class_="entry-badge")
            images = soup2.find_all("img")
            links = []
            async for image in aiter(images):
                if "data.whicdn.com/images/" in str(image):
                    links.append(image["src"])
    return links


async def getwhiuser(query):

    url = f"https://weheartit.com/{query.replace(' ', '+')}"
    from bs4 import BeautifulSoup

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as x:
            soup = BeautifulSoup(await x.text(), features="html.parser")
            divs = str(soup.find_all("div", class_="entry grid-item"))
            soup2 = BeautifulSoup(divs, features="html.parser")
            badge = soup2.find_all(class_="entry-badge")
            images = soup2.find_all("img")
            links = []
            async for image in aiter(images):
                if "data.whicdn.com/images/" in str(image):
                    links.append(image["src"])
    return links
async def to_object(params):

    x = {}
    fields = []
    content = None
    timestamp=None
    files = []
    view = discord.ui.View()

    async for part in aiter(get_parts(params)):

        if part.startswith("content:"):
            content = part[len("content:") :]

        if part.startswith("url:"):
            x["url"] = part[len("url:") :]

        if part.startswith("title:"):
            x["title"] = part[len("title:") :]

        if part.startswith("description:"):
            x["description"] = part[len("description:") :]

        if part.startswith("footer:"):
            x["footer"] = part[len("footer:") :]

        if part.startswith("color:"):
            try:
                x["color"] = int(part[len("color:") :].replace(' ', '').replace('#', ''), 16)
            except:
                x["color"] = 0x2F3136

        if part.startswith("image:"):
            x["image"] = {"url": part[len("description:") :]}

        if part.startswith("thumbnail:"):
            x["thumbnail"] = {"url": part[len("thumbnail:") :]}

        if part.startswith("attach:"):
            async with aiohttp.ClientSession() as session:
                async with session.get(part[len("attach:") :].replace(' ', '')) as resp:
                    balls = await resp.read()
            files.append(
                discord.File(io.BytesIO(balls), yarl.URL(part[len("attach:") :].replace(' ', '')).name)
            )

        if part.startswith("author:"):
            z = part[len("author:") :].split(" && ")
            icon_url=None
            url=None
            for p in z[1:]:
                if p.startswith('icon:'):
                    p=p[len('icon:') :]
                    icon_url=p.replace(' ', '')
                elif p.startswith('url:'):
                    p=p[len('url:') :]
                    url=p.replace(' ', '')
            try:
                name = z[0] if z[0] else None
            except:
                name = None

            x["author"] = {"name": name}
            if icon_url:
                x["author"]["icon_url"] = icon_url
            if url:
                x["author"]["url"] = url

        if part.startswith("field:"):
            z = part[len("field:") :].split(" && ")
            value=None
            inline='true'
            for p in z[1:]:
                if p.startswith('value:'):
                    p=p[len('value:') :]
                    value=p
                elif p.startswith('inline:'):
                    p=p[len('inline:') :]
                    inline=p.replace(' ', '')
            try:
                name = z[0] if z[0] else None
            except:
                name = None
            
            if isinstance(inline, str):
                if inline == "true":
                    inline = True

                elif inline == "false":
                    inline = False

            fields.append({"name": name, "value": value, "inline": inline})

        if part.startswith("footer:"):
            z = part[len("footer:") :].split(" && ")
            text=None
            icon_url=None
            for p in z[1:]:
                if p.startswith('icon:'):
                    p=p[len('icon:') :]
                    icon_url=p.replace(' ', '')
            try:
                text = z[0] if z[0] else None
            except:
                pass
                
            x["footer"] = {"text": text}
            if icon_url:
                x["footer"]["icon_url"] = icon_url

        if part.startswith("label:"):
            z = part[len("label:") :].split(" && ")
            labrl='no label'
            url=None
            for p in z[1:]:
                if p.startswith('link:'):
                    p=p[len('link:') :]
                    url=p.replace(' ', '')
                    
            try:
                label = z[0] if z[0] else None
            except:
                pass
                

            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link, label=label, url=url
                )
            )
            
        if part.startswith('image:'):
            z=part[len('image:') :]
            x['image']={'url': z}
            
        if part.startswith('timestamp:'):
            z=part[len('timestamp:') :].replace(' ', '')
            if z == 'true':
                timestamp=True
                
    if not x:
        embed = None
    else:
        x["fields"] = fields
        embed = discord.Embed.from_dict(x)

    if not params.count("{") and not params.count("}"):
        content = params
        
    if timestamp:
        embed.timestamp=datetime.now(__import__('pytz').timezone('America/New_York'))

    return {"content": content, "embed": embed, "files": files, "view": view}


def get_partss(params):
    x = {}
    notembed, embed = params.split("{extra}")[0].split("{embed}")
    x["notembed"] = [p[1:][:-1] for p in notembed.split("$v")]
    x["embed"] = [p[1:][:-1] for p in embed.split("$v")]
    x["extra"] = [p for p in params.split("{extra}")[1].split()]
    return x

def ordinal(n):

    return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4])
async def to_objectt(params):

    x = {}
    parts = get_partss(params)
    fields = []
    content = None
    files = []
    view = discord.ui.View()

    for part in parts["notembed"]:

        if part.startswith("content:"):
            content = part[len("content:") :]

        if part.startswith("button:"):
            z = part[len("button:") :].split(" && ")
            try:
                label = z[0] if z[0] else None
            except:
                label = "no label"
            try:
                url = z[1] if z[1] else None
            except:
                url = "https://none.none"
            try:
                emoji = z[2] if z[2] else None
            except:
                emoji = None

            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.link, label=label, url=url, emoji=emoji
                )
            )

    for part in parts["embed"]:

        if part.startswith("url:"):
            x["url"] = part[len("url:") :]

        if part.startswith("title:"):
            x["title"] = part[len("title:") :]

        if part.startswith("description:"):
            x["description"] = part[len("description:") :]

        if part.startswith("footer:"):
            x["footer"] = part[len("footer:") :]

        if part.startswith("color:"):
            try:
                x["color"] = int(part[len("color:") :].strip("#").strip(), 16)
            except:
                x["color"] = 0x2F3136

        if part.startswith("image:"):
            x["image"] = {"url": part[len("description:") :]}

        if part.startswith("thumbnail:"):
            x["thumbnail"] = {"url": part[len("thumbnail:") :]}

        if part.startswith("attach:"):
            async with aiohttp.ClientSession() as session:
                async with session.get(part[len("attach:") :]) as resp:
                    balls = await resp.read()
            files.append(
                discord.File(io.BytesIO(balls), yarl.URL(part[len("attach:") :]).name)
            )

        if part.startswith("author:"):
            z = part[len("author:") :].split(" && ")
            try:
                name = z[0] if z[0] else None
            except:
                name = None
            try:
                icon_url = z[1] if z[1] else None
            except:
                icon_url = None
            try:
                url = z[2] if z[2] else None
            except:
                url = None

            x["author"] = {"name": name}
            if icon_url:
                x["author"]["icon_url"] = icon_url
            if url:
                x["author"]["url"] = url

        if part.startswith("field:"):
            z = part[len("field:") :].split(" && ")
            try:
                name = z[0] if z[0] else None
            except:
                name = None
            try:
                value = z[1] if z[1] else None
            except:
                value = None
            try:
                inline = z[2] if z[2] else True
            except:
                inline = True

            if isinstance(inline, str):
                if inline == "true":
                    inline = True

                elif inline == "false":
                    inline = False

            fields.append({"name": name, "value": value, "inline": inline})

        if part.startswith("footer:"):
            z = part[len("footer:") :].split(" && ")
            try:
                text = z[0] if z[0] else None
            except:
                text = None
            try:
                icon_url = z[1] if z[1] else None
            except:
                icon_url = None
            x["footer"] = {"text": text}
            if icon_url:
                x["footer"]["icon_url"] = icon_url

    if not x:
        embed = None
    else:
        x["fields"] = fields
        embed = discord.Embed.from_dict(x)

    if not params.count("{") and not params.count("}"):
        content = params

    return (
        {"content": content, "embed": embed, "files": files, "view": view},
        parts["extra"],
    )
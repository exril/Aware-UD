import discord, os
from discord.ext import commands


def owner():
    async def predicate(ctx: commands.Context):
        c = await ctx.bot.db.cursor()
        await c.execute("SELECT user_id FROM Owner")
        ids_ = await c.fetchall()
        if ids_ is None:
            return

        ids = [int(i[0]) for i in ids_]
        if ctx.author.id in ids:
            return True
        else:
            return False
    return commands.check(predicate)


def time(time):
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    text = ''
    if days > 0:
        text += f"{hours} day{'s' if hours != 1 else ''}, "
    if hours > 0:
        text += f"{hours} hour{'s' if hours != 1 else ''}, "
    if minutes > 0:
        text += f"{minutes} minute{'s' if minutes != 1 else ''} and "
    text += f"{seconds} second{'s' if seconds != 1 else ''}"

    return text


def TimeConvert(time):
    pos = ["s","m","h","d"]
    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]









#EMBED
color = 0x2C2D31

#EMOJIS
Tick="<:greenTick:1230421239634595860>"
Cross="<:redTick:1230421267514003457>"
Load = "<:rival_warning:1230421852770271272>"



#LINKS
Support = "https://discord.gg/aware"
Invite = "https://discord.com/api/oauth2/authorize?client_id=1106094873951621120&&permissions=8&scope=bot"
Vote = ""

import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self,ctx):
        self.embed = discord.Embed(description="https://awarebot.tech/help @ https://awarebot.tech/support", color=0xffffff)
        await ctx.send(embed=self.embed)
        await ctx.send(content='**visit the web for help TwT**', embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Help(bot))

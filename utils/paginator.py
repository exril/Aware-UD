from discord.ext import commands
import discord
import os
import datetime, time
from discord.ui import Button, View
import asyncio

from utils import aware

from typing import List
from collections import deque





class PaginatorView(discord.ui.View):
    def __init__(
        self,
        embeds: List[discord.Embed],
        bot: commands.AutoShardedBot,
        author) -> None:
        super().__init__(timeout=120)

        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        self._current_page = 1
        self.children[0].disabled = True
        self.children[1].disabled = True
        self.bot = bot
        self.author = author
        self._queue[0].set_footer(text=f"{bot.user.name} • Page {self._current_page}/{self._len}",
                                  icon_url=bot.user.display_avatar.url)

  
    async def update_button(self, interaction: discord.Interaction) -> None:
        for i in self._queue:
            i.set_footer(text=f"{interaction.client.user.name} • Page {self._current_page}/{self._len}", icon_url=interaction.client.user.display_avatar.url)
        if self._current_page == self._len:
            self.children[3].disabled = True
            self.children[4].disabled = True
        else:
            self.children[3].disabled = False
            self.children[4].disabled = False

        if self._current_page == 1:
            self.children[0].disabled = True
            self.children[1].disabled = True
        else:
            self.children[0].disabled = False
            self.children[1].disabled = False

        await interaction.message.edit(view=self)



    async def on_timeout(self):
        for i in self.children:
            i.disabled = True
        await self.message.edit(view=self)


    @discord.ui.button(emoji="⏮️")
    async def start(self, interaction: discord.Interaction, _):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
        
        self._queue.rotate(-self._current_page + 1)
        embed = self._queue[0]
        self._current_page = 1
        await self.update_button(interaction)
        self.message = await interaction.response.edit_message(embed=embed)

    @discord.ui.button(emoji="◀️")
    async def previous(self, interaction: discord.Interaction, _):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
        
        self._queue.rotate(-1)
        embed = self._queue[0]
        self._current_page -= 1
        await self.update_button(interaction)
        self.message = await interaction.response.edit_message(embed=embed)


    @discord.ui.button(emoji="⏹")
    async def stop(self, interaction: discord.Interaction, _):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
        
        await self.update_button(interaction)
        self.message = await interaction.message.delete()


    @discord.ui.button(emoji="▶️")
    async def next(self, interaction: discord.Interaction, _):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
        
        self._queue.rotate(1)
        embed = self._queue[0]
        self._current_page += 1
        await self.update_button(interaction)
        self.message = await interaction.response.edit_message(embed=embed)


    @discord.ui.button(emoji="⏭️")
    async def end(self, interaction: discord.Interaction, _):
        if self.author != interaction.user:
            return await interaction.response.send_message(f"{config.Cross} | Its not your interaction.", ephemeral=True)
            
        self._queue.rotate(self._len - 1)
        embed = self._queue[0]
        self._current_page = self._len
        await self.update_button(interaction)
        self.message = await interaction.response.edit_message(embed=embed)





    @property
    def initial(self) -> discord.Embed:
        return self._initial

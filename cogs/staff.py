# -*- coding: utf-8 -*-
from __future__ import annotations

import discord
from bot import Bot
from discord.ext import commands

from cogs.errors import *


class Staff(commands.Cog):
    '''Utility commands and role setup for staff members.'''

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def say(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        '''Echoes a message in a different channel
        
        The <channel> argument may be a channel mention, channel ID or channel name.
        '''
        msg = await channel.send(message)
        await ctx.send(f"Success: ({msg.jump_url})")
    
    @say.error
    async def say_error(self, ctx: commands.Context, err: commands.CommandError):
        err = getattr(err, "original", err)
        if isinstance(err, discord.Forbidden):
            await ctx.send("I'm not allowed to send messages there.")
        elif isinstance(err, discord.HTTPException):
            await ctx.send("Something went wrong sending the message.")
        elif isinstance(err, commands.ChannelNotFound):
            await ctx.send("Bad argument provided. The <channel> argument should be a channel mention, channel ID or channel name.")

    @commands.command(name="enablenicknames")
    @commands.is_owner()
    async def enable_nicknames(self, ctx: commands.Context):
        '''Enables automatic nickname changes'''
        self.bot.nicknames_enabled = True
        await ctx.send("Nickname craziness enabled.")
    
    @commands.command(name="disablenicknames")
    @commands.is_owner()
    async def disable_nicknames(self, ctx: commands.Context):
        '''Disables automatic nickname changes'''
        self.bot.nicknames_enabled = False
        await ctx.send("Nickname craziness disabled.")

async def setup(bot: Bot):
    await bot.add_cog(Staff(bot))

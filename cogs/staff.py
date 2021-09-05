# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
from cogs.utils import *
from cogs.errors import *

class Staff(commands.Cog):
    '''Utility commands and role setup for staff members.'''

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await has_staff_permissions(ctx)

    @commands.command()
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
    async def enable_nicknames(self, ctx: commands.Context):
        '''Enables automatic nickname changes'''
        self.bot.enabled = True
        await ctx.send("Nickname craziness enabled.")
    
    @commands.command(name="disablenicknames")
    async def dis_nicknames(self, ctx: commands.Context):
        '''Disables automatic nickname changes'''
        self.bot.enabled = False
        await ctx.send("Nickname craziness disabled.")

def setup(bot):
    bot.add_cog(Staff(bot))

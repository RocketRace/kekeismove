# -*- coding: utf-8 -*-

import random
import re

import discord
from discord.ext import commands

from cogs.errors import *

from bot import Bot

class NicknameCog(commands.Cog, name="Nicknames"):
    '''KEKE IS CHEEKY'''

    I_AM_PREFIXES = re.compile("|".join(("i'm ", "I'm ", "im ", "Im ", "i am ", "I am ", "i’m ", "I’m ")))

    def __init__(self, bot: Bot):
        self.bot = bot
    
    @commands.command()
    async def optin(self, ctx: commands.Context):
        '''Opts in to nickname changing
        
        You can opt out using the <optout> command.
        '''
        if ctx.author.id in self.bot.opted_in:
            pass # it's fine if they were already opted in
        else:
            self.bot.opted_in.append(ctx.author.id)
        await ctx.send(f"{ctx.author.mention} Opted in to craziness. Use the ``{ctx.prefix}optout`` command to opt out.")

    @commands.command()
    async def optout(self, ctx: commands.Context):
        '''Opts out of nickname changing
        
        You can opt back in using the <optin> command.
        '''
        try:
            self.bot.opted_in.remove(ctx.author.id)
        except ValueError:
            pass # it's fine if the were already opted out
        await ctx.send(f"{ctx.author.mention} Opted out from craziness. Use the ``{ctx.prefix}optin`` command to opt back in.")
    
    @commands.command()
    async def count(self, ctx: commands.Context):
        '''How many nicknames have I changed?'''
        options = [
            "I've annoyed people {} times!",
            "I've changed {} nicknames!",
            "I've made someone roll their eyes {} times!",
            "I've changed someone's nickname {} times!",
            "I've made a pun {} times!",
            "I've made a bad pun {} times!",
            "I've done this {} times!",
            "I've disappointed people {} times!",
            "I've interrupted the conversation {} times!",
        ]
        await ctx.send(random.choice(options).format(self.bot.nicknames_changed))

    
    async def nickname_change(self, message: discord.Message):
        if (
            message.guild is None or
            not self.bot.nicknames_enabled or
            message.author.id not in self.bot.opted_in or
            not message.channel.permissions_for(message.guild.me).send_messages
        ):
            return

        match = self.I_AM_PREFIXES.match(message.content)
        if match is None:
            return

        nick = re.sub(self.I_AM_PREFIXES, "", message.content, 1).replace("\n", " ")
        if len(nick) == 0 or len(nick) > 128:
            return
        
        escaped = inline_codeblock(nick)

        if nick.count("||") >= 2: # don't reveal spoilers
            return await message.channel.send(
                f"{message.author.mention} <a:is:793742253452558356> <a:not:793742269848354856> "
                f"||{escaped.replace('|', '')}|| (that nickname has spoilers!)\n"
                f"*Use the ``!optout`` command to hide me.*"
            )
        if len(nick) > 32:
            return await message.channel.send(
                f"{message.author.mention} <a:is:793742253452558356> <a:not:793742269848354856> " 
                f"{escaped} (that nickname is too long!)\n" 
                f"*Use the ``!optout`` command to hide me.*"
            )
        try:
            await message.author.edit(nick=nick)
        except discord.Forbidden:
            await message.channel.send("I can't change your nickname! " 
                "Do I have permissions to do so, or is your role above mine (or are you the server owner)?"
            )
        else:
            self.bot.nicknames_changed += 1
            await message.channel.send(
                f"{message.author.mention} <a:is:793742253452558356> {escaped}\n" 
                f"*Use the ``!optout`` command to hide me.*"
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.nickname_change(message)

def setup(bot):
    bot.add_cog(NicknameCog(bot))

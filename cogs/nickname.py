# -*- coding: utf-8 -*-

from __future__ import annotations

import random
import re

import discord
from bot import Bot
from discord.ext import commands

from cogs.errors import *


def inline_codeblock(msg: str) -> str:
    clean_backtick = "\u200b`"
    clean = msg.replace("`", clean_backtick)
    return f"``\u200b{clean}\u200b``"


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

        is_ = f"<a:is:{self.bot.emoji_data['is_']}>"
        not_ = f"<a:not:{self.bot.emoji_data['not_']}>"
        prefix = f"{message.author.mention} {is_}"

        if nick.count("||") >= 2: # don't reveal spoilers
            return await self.bot.clearable_send(
                message.author.id,
                message.channel,
                f"{prefix}{not_} ||{escaped.replace('|', '')}|| (that nickname has spoilers!)\n"
                f"*Use the ``!optout`` command to hide me.*"
            )
        if len(nick) > 32:
            return await self.bot.clearable_send(
                message.author.id,
                message.channel,
                f"{prefix}{not_} {escaped} (that nickname is too long!)\n" 
                f"*Use the ``!optout`` command to hide me.*"
            )
        try:
            await message.author.edit(nick=nick) # type: ignore
        except discord.Forbidden:
            return await self.bot.clearable_send(
                message.author.id,
                message.channel,
                "I can't change your nickname! " 
                "Do I have permissions to do so, or is your role above mine (or are you the server owner)?"
            )
        else:
            self.bot.nicknames_changed += 1
            return await self.bot.clearable_send(
                message.author.id,
                message.channel,
                f"{prefix} {escaped}\n" 
                f"*Use the ``!optout`` command to hide me.*"
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.nickname_change(message)

async def setup(bot: Bot):
    await bot.add_cog(NicknameCog(bot))

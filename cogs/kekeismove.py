# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
from cogs.errors import *

class KekeIsMove(commands.Cog, name="KEKE IS MOVE"):
    '''KEKE IS MOVE AND HELP

    SOMETIMES KEKE IS SLEEP

    KEKE TRY BEST
    '''

    def __init__(self, bot: commands.Bot):
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
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None: return
        if not self.bot.enabled: return
        flag = None
        for x in ("i'm ", "I'm ", "im ", "Im ", "i am ", "I am ", "i’m ", "I’m "):
            if message.content.startswith(x):
                flag = x
                break
        if flag is not None:
            if message.author.id in self.bot.opted_in:
                nick = message.content.split(flag, 1)[1].replace("\n", " ")
                if len(nick) == 0 or len(nick) > 128:
                    return
                clean_backtick = "\u200b`"
                if not message.channel.permissions_for(message.guild.me).send_messages: return
                if nick.count("||") >= 2: # don't reveal spoilers
                    return await message.channel.send(
                        f"{message.author.mention} <a:is:793742253452558356> <a:not:793742269848354856> " + \
                        f"||``\u200b{nick.replace('`', clean_backtick).replace('|','')}\u200b``|| (that nickname has spoilers!)\n" + \
                        f"*Use the ``!optout`` command to hide me.*"
                    )
                if len(nick) > 32:
                    return await message.channel.send(
                        f"{message.author.mention} <a:is:793742253452558356> <a:not:793742269848354856> " + \
                        f"``{nick.replace('`', clean_backtick)}`` (that nickname is too long!)\n" + \
                        f"*Use the ``!optout`` command to hide me.*"
                    )
                try:
                    await message.author.edit(nick=nick)
                except discord.Forbidden:
                    await message.channel.send("I can't change your nickname! " + \
                        "Do I have permissions to do so, or is your role above mine (or are you the server owner)?"
                    )
                else:
                    self.bot.nicknames_changed += 1
                    await message.channel.send(
                        f"{message.author.mention} <a:is:793742253452558356> ``{nick.replace('`', clean_backtick)}``\n" + \
                        f"*Use the ``!optout`` command to hide me.*"
                    )

def setup(bot):
    bot.add_cog(KekeIsMove(bot))

# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
from cogs.utils import *
from cogs.errors import *
import typing

class KekeIsMove(commands.Cog, name="KEKE IS MOVE"):
    '''KEKE IS MOVE AND HELP

    SOMETIMES KEKE IS SLEEP

    KEKE TRY BEST
    '''

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="rank")
    @commands.bot_has_permissions(manage_roles=True)
    async def add_rank(self, ctx: commands.Context, *, rank: typing.Union[discord.Role, str]):
        '''Adds or removes a rank from you
        
        For a list of valid self-assignable role, see the <ranks> command.
        '''
        if not rank:
            raise EmptyInput
        if isinstance(rank, str):
            rank = discord.utils.find(lambda r: r.name.lower() == rank, ctx.guild.roles)
            if rank is None: 
                raise InvalidRole(rank)
        if rank.id not in self.bot.settings["ranks"]:
            raise InvalidRole(rank)
        role = discord.utils.find(lambda role: role == rank, ctx.author.roles)
        if rank.position > ctx.me.top_role.position:
            raise BadHierarchy
        if role is None:
            await ctx.author.add_roles(rank, reason="Self-assigned role")
            await ctx.send(f"Added role {rank.mention} to {ctx.author.mention}")
        else:
            await ctx.author.remove_roles(rank, reason="Self-assigned role")
            await ctx.send(f"Removed role {rank.mention} from {ctx.author.mention}")
    
    @add_rank.error
    async def rank_error(self, ctx: commands.Context, err: commands.CommandError):
        if isinstance(err, BadHierarchy):
            await ctx.send("That role is above mine! I don't have permissions to give it to you :(")
        elif isinstance(getattr(err, "original", err), commands.RoleNotFound):
            await ctx.send(f"That's not a valid self-assignable role. See the ``{ctx.prefix}ranks`` command for a list.")
        elif isinstance(err, commands.MissingRequiredArgument):
            await ctx.send("<rank> is a required argument that's missing! It should be the ping, ID or name of a self-assignable role.")

    @commands.command()
    async def ranks(self, ctx: commands.Context):
        '''Displays a list of self-assignable ranks
        
        These can be added or removed using the <rank> command.
        '''
        mentions = (f"<@&{i}>" for i in self.bot.settings["ranks"])
        embed = discord.Embed(color=self.bot.settings["color"], title="List of self-assignable roles:", description="\n".join(mentions))
        await ctx.send(embed=embed)

    @commands.command()
    async def optin(self, ctx: commands.Context):
        '''Opts in to nickname changing
        
        You can opt out using the <optout> command.
        '''
        if ctx.author.id in self.bot.settings["nicknames"]["opted_in"]:
            pass # it's fine if they were already opted in
        else:
            self.bot.settings["nicknames"]["opted_in"].append(ctx.author.id)
        await ctx.send(f"{ctx.author.mention} Opted in to craziness. Use the ``{ctx.prefix}optout`` command to opt out.")

    @commands.command()
    async def optout(self, ctx: commands.Context):
        '''Opts out of nickname changing
        
        You can opt back in using the <optin> command.
        '''
        try:
            self.bot.settings["nicknames"]["opted_in"].remove(ctx.author.id)
        except ValueError:
            pass # it's fine if the were already opted out
        await ctx.send(f"{ctx.author.mention} Opted out from craziness. Use the ``{ctx.prefix}optin`` command to opt back in.")
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None: return
        if not self.bot.settings["nicknames"]["enabled"]: return
        flag = None
        for x in ("i'm ", "I'm ", "im ", "Im ", "i am ", "I am ", "i’m ", "I’m "):
            if message.content.startswith(x):
                flag = x
                break
        if flag is not None:
            if message.author.id in self.bot.settings["nicknames"]["opted_in"]:
                nick = message.content.split(flag, 1)[1].replace("\n", " ")
                if len(nick) == 0 or len(nick) > 128:
                    return
                clean_backtick = "\u200b`"
                if not message.channel.permissions_for(message.guild.me).send_messages: return
                if nick.count("||") >= 2: # don't reveal spoilers
                    return await message.channel.send(
                        f"{message.author.mention} <a:is:793742253452558356> <a:not:793742269848354856> " + \
                        f"||``\u200b{nick.replace('`', clean_backtick).replace('|','')}\u200b``|| (that nickname has spoilers!)\n" + \
                        f"*Use the ``{self.bot.settings['prefixes'][0]}optout`` command to hide me.*"
                    )
                if len(nick) > 32:
                    return await message.channel.send(
                        f"{message.author.mention} <a:is:793742253452558356> <a:not:793742269848354856> " + \
                        f"``{nick.replace('`', clean_backtick)}`` (that nickname is too long!)\n" + \
                        f"*Use the ``{self.bot.settings['prefixes'][0]}optout`` command to hide me.*"
                    )
                try:
                    await message.author.edit(nick=nick)
                    self.bot.settings["stats"]["nicknames"] += 1
                except discord.Forbidden:
                    await message.channel.send("I can't change your nickname! " + \
                        "Do I have permissions to do so, or is your role above mine (or are you the server owner)?"
                    )
                else:
                    await message.channel.send(
                        f"{message.author.mention} <a:is:793742253452558356> ``{nick.replace('`', clean_backtick)}``\n" + \
                        f"*Use the ``{self.bot.settings['prefixes'][0]}optout`` command to hide me.*"
                        )

def setup(bot):
    bot.add_cog(KekeIsMove(bot))

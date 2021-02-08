# -*- coding: utf-8 -*-

import re
import aiohttp
from discord.ext import commands
import discord
from cogs.utils import *
from cogs.errors import *

class Staff(commands.Cog):
    '''Utility commands and role setup for staff members.'''

    session: aiohttp.ClientSession

    def __init__(self, bot: commands.Bot):
        bot.loop.create_task(self.initialize())
        self.bot = bot

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    async def on_cog_unload(self):
        await self.session.close()

    async def cog_check(self, ctx):
        return await has_staff_permissions(ctx)

    @commands.command()
    async def stats(self, ctx: commands.Context):
        '''Displays server stats'''
        count = members(ctx)
        mention = mention_role(ctx)

        embed = discord.Embed(title="Server Stats", color=self.bot.settings["color"])
        embed.add_field(name="Members", inline=False, value=f"- Member count: `{len(ctx.guild.members)}`")
        embed.add_field(name="Colored roles", inline=False, value="\n".join([
            f"- Total: `{sum(count(rank) for rank in self.bot.settings['ranks'])}`",
            *[
                f"- {mention(rank)}: `{count(rank)}` members"
                for rank in self.bot.settings['ranks']
            ]
        ]))
        embed.add_field(name="Special roles", inline=False, value="\n".join([
            *[
                f"- ({emoji}) {mention(role['colorless'])}: `{count(role['colorless'])}` members, {mention(role['colored'])}: `{count(role['colored'])}` members"
                for emoji, role in self.bot.settings["special_roles"]["emoji"].items()
            ],
            *[
                f"- ({emoji}) {mention(role)}: `{count(role)}` members"
                for emoji, role in self.bot.settings["pronoun_roles"]["emoji"].items()
            ],
            f"- {mention(self.bot.settings['staff_role'])}: `{count(self.bot.settings['staff_role'])}` members",
            f"- {mention(self.bot.settings['contribute_role'])}: `{count(self.bot.settings['contribute_role'])}` members",
            f"- {mention(self.bot.settings['nitro_role'])}: `{count(self.bot.settings['nitro_role'])}` members"
        ]))
        embed.add_field(name="Bot", inline=False, value="\n".join([
            f"- `{self.bot.settings['stats']['commands']}` commands run",
            f"- `{self.bot.settings['stats']['nicknames']}` nicknames changed",
            f"- `{len(self.bot.settings['nicknames']['opted_in'])}` people opted in to nickname changes"
        ]))

        await ctx.send(embed=embed)
    
    @stats.error
    async def stats_error(self, ctx: commands.Context, err: commands.CommandError):
        err = getattr(err, "original", err)
        if isinstance(err, AttributeError):
            await ctx.send("Not all IDs in the bot settings are valid. See the <export> and <import> commands to fix this.")
    
    @commands.command()
    async def say(self, ctx: commands.Context, channel: discord.TextChannel, *, message: str):
        '''Echoes a message in a different channel
        
        The <channel> argument may be a channel mention, channel ID or channel name.
        '''
        message = await channel.send(message)
        await ctx.send(f"Success: ({message.jump_url})")
    
    @say.error
    async def say_error(self, ctx: commands.Context, err: commands.CommandError):
        err = getattr(err, "original", err)
        if isinstance(err, discord.Forbidden):
            await ctx.send("I'm not allowed to send messages there.")
        elif isinstance(err, discord.HTTPException):
            await ctx.send("Something went wrong sending the message.")
        elif isinstance(err, commands.ChannelNotFound):
            await ctx.send("Bad argument provided. The <channel> argument should be a channel mention, channel ID or channel name.")

    @commands.command(name="addrank")
    async def add_rank(self, ctx: commands.Context, rank: discord.Role):
        '''Adds a role to self-assignable ranks'''
        if rank.id in self.bot.settings["ranks"]:
            raise InvalidRole
        self.bot.settings["ranks"].append(rank.id)
        await ctx.send(f"{rank.mention} is now a self-assignable role.")

    @add_rank.error
    async def add_rank_error(self, ctx: commands.Context, err: commands.CommandError):
        if isinstance(err, InvalidRole):
            await ctx.send(f"The role provided is already a self-assignable role.")

    @commands.command(name="removerank")
    async def remove_rank(self, ctx: commands.Context, rank: discord.Role):
        '''Removes a role from self-assignable ranks'''
        if rank.id not in self.bot.settings["ranks"]:
            raise InvalidRole
        self.bot.settings["ranks"].remove(rank.id)
        await ctx.send(f"{rank.mention} is no longer a self-assignable role.")

    @remove_rank.error
    async def remove_rank_error(self, ctx: commands.Context, err: commands.CommandError):
        if isinstance(err, InvalidRole):
            await ctx.send(f"The role provided is not currently a self-assignable role.")

    @commands.command(name="enablenicknames")
    async def enable_nicknames(self, ctx: commands.Context):
        '''Enables automatic nickname changes'''
        self.bot.settings["nicknames"]["enabled"] = True
        await ctx.send("Nickname craziness enabled.")
    
    @commands.command(name="disablenicknames")
    async def dis_nicknames(self, ctx: commands.Context):
        '''Disables automatic nickname changes'''
        self.bot.settings["nicknames"]["enabled"] = False
        await ctx.send("Nickname craziness disabled.")
    
    @commands.command(name="enableuploads")
    async def enable_uploads(self, ctx: commands.Context):
        '''Enables automatic level code uploads to the baba-is-bookmark website.'''
        self.bot.settings["uploads"]["enabled"] = True
    
    @commands.command(name="disableuploads")
    async def disable_uploads(self, ctx: commands.Context):
        '''Disables automatic level code uploads to the baba-is-bookmark website.'''
        self.bot.settings["uploads"]["enabled"] = False

    @commands.group(name="specialroles", aliases=["sr"], invoke_without_command=True)
    async def special_roles(self, ctx: commands.Context):
        '''Manage and check special reaction roles'''
        mention = mention_role(ctx)

        embed = discord.Embed(title="Reaction Roles", color=self.bot.settings["color"])
        embed.add_field(name="Message", value=str(self.bot.settings["special_roles"]["message"]))
        embed.add_field(name="Roles", value="\n".join(
            f"({emoji}): {mention(role['colorless'])} / {mention(role['colored'])}"
            for emoji, role in self.bot.settings["special_roles"]["emoji"].items())
        )
        await ctx.send(embed=embed)

    @special_roles.command(name="set")
    async def set_special(self, ctx: commands.Context, message: discord.Message):
        '''Sets the current special reaction role message
        
        The <message> argument should either be a message link, a message ID (in the current channel)
        or a channel-message ID (obtained by shift-clicking the "Copy ID" option for messages).
        '''
        for emoji in self.bot.settings["special_roles"]["emoji"]:
            await message.add_reaction(emoji)
        self.bot.settings["special_roles"]["message"] = message.id
        await ctx.send(f"The special reaction role message has been updated to the following message:\n<{message.jump_url}>.")
    
    @special_roles.command(name="unset")
    async def unset_special(self, ctx: commands.Context):
        '''Disables the current special reaction role message'''
        self.bot.settings["special_roles"]["message"] = None
        await ctx.send(f"The special reaction role message has been unset.")

    @commands.group(name="pronounroles", aliases=["pr"], invoke_without_command=True)
    async def pronoun_roles(self, ctx: commands.Context):
        '''Manage and check pronoun reaction roles'''
        mention = mention_role(ctx)

        embed = discord.Embed(title="Reaction Roles", color=self.bot.settings["color"])
        embed.add_field(name="Reaction message", value=str(self.bot.setttings["pronoun_roles"]["message"]))
        embed.add_field(name="Roles", value="\n".join(
            f"({emoji}): {mention(role)}" for emoji, role in self.bot.settings["pronoun_roles"]["emoji"].items())
        )
        await ctx.send(embed=embed)

    @pronoun_roles.command(name="set")
    async def set_pronouns(self, ctx: commands.Context, message: discord.Message):
        '''Sets the current pronoun reaction role message
        
        The <message> argument should either be a message link, a message ID (in the current channel)
        or a channel-message ID (obtained by shift-clicking the "Copy ID" option for messages).
        '''
        for emoji in self.bot.settings["pronoun_roles"]["emoji"]:
            await message.add_reaction(emoji)
        self.bot.settings["pronoun_roles"]["message"] = message.id
        await ctx.send(f"The pronoun reaction role message has been updated to the following message:\n<{message.jump_url}>.")
    
    @pronoun_roles.command(name="unset")
    async def unset_pronouns(self, ctx: commands.Context):
        '''Disables the current special reaction role message'''
        self.bot.settings["special_roles"]["message"] = None
        await ctx.send(f"The reaction role message has been unset.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id: return
        member = payload.member # only works for raw_reaction_add, not raw_reaction_remove because discord
        guild = self.bot.get_guild(payload.guild_id)
        emoji = str(payload.emoji).replace("<:", "<a:") # for some reason, discord does not provide the right data
        for _ in range(1):
            if payload.message_id != self.bot.settings["special_roles"]["message"]: break
            roles = self.bot.settings["special_roles"]["emoji"].get(emoji)
            if roles is None: break
            colored = guild.get_role(roles["colored"])
            colorless = guild.get_role(roles["colorless"])
            if colorless in member.roles:
                if colored not in member.roles:
                    await member.add_roles(colored)
        if payload.message_id != self.bot.settings["pronoun_roles"]["message"]: return
        role_id = self.bot.settings["pronoun_roles"]["emoji"].get(emoji)
        if role_id is None: return
        role = guild.get_role(role_id)
        if role not in member.roles:
            await member.add_roles(role)
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        # why must I make such a mess
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = str(payload.emoji).replace("<:", "<a:") # for some reason, discord does not provide the right data
        for _ in range(1): # goto but not really
            if payload.message_id != self.bot.settings["special_roles"]["message"]: break
            roles = self.bot.settings["special_roles"]["emoji"].get(emoji)
            if roles is None: break
            colored = guild.get_role(roles["colored"])
            colorless = guild.get_role(roles["colorless"])
            if colorless in member.roles:
                if colored in member.roles:
                    await member.remove_roles(colored)
        if payload.message_id != self.bot.settings["pronoun_roles"]["message"]: return
        role_id = self.bot.settings["pronoun_roles"]["emoji"].get(emoji)
        if role_id is None: return
        role = guild.get_role(role_id)
        if role in member.roles:
            await member.remove_roles(role)
    
    LEVEL_CODE_REGEX = re.compile(r"[0-9A-Z]{4}-[0-9A-Z]{4}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != self.bot.settings["uploads"]["channel"]:
            return
        codes = re.findall(self.LEVEL_CODE_REGEX, message.content)
        if not codes:
            return
        for code in codes:
            async with self.session.post(
                f"https://baba-is-bookmark.herokuapp.com/api/level/",
                json={"code":code}
            ) as resp:
                pass
                # might do something with response later

def setup(bot):
    bot.add_cog(Staff(bot))

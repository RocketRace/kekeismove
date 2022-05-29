# -*- coding: utf-8 -*-

import re
import unicodedata

import discord
from discord.ext import commands

from cogs.errors import *

from bot import Bot

def inline_codeblock(msg: str) -> str:
    clean_backtick = "\u200b`"
    clean = msg.replace("`", clean_backtick)
    return f"``\u200b{clean}\u200b``"

class RoleIconCog(commands.Cog, name="Role icons"):
    '''Self-assigned role icon management

    To give yourself a self-assigned role, type:

    `@yourname is someicon`
    
    To remove your self-assigned role, type:

    `@yourname is not someicon`
    '''

    def __init__(self, bot: Bot):
        self.bot = bot
    
    @commands.command()
    async def icons(self, ctx: commands.Context):
        '''Gives a list of icons you can use'''
        embed = discord.Embed(
            title="Role icons",
            color=15029051,
        ).set_footer(text="Use `@yourname is <icon>` to assign yourself a role icon")
        
        # 10 icons per field
        icons = sorted(
            f"{name} <@&{icon['role_id']}>"
            for name, icon in self.bot.object_roles.items()
        )
        for i in range(0, len(icons), 10):
            embed.add_field(
                name="\u200b",
                value="\n".join(icons[i:i+10]),
                inline=True
            )

        await ctx.send(embed=embed)

    I_AM_PREFIXES = re.compile("|".join(("i'm ", "I'm ", "im ", "Im ", "i am ", "I am ", "i’m ", "I’m ")))
    
    async def role_assign(self, message: discord.Message):
        if not isinstance(message.author, discord.Member):
            return
        
        if not self.bot.roles_enabled:
            return
        
        author = message.author
        names = "|".join(
            re.escape(x.lower())
            for x in [
                f"<@{author.id}>",
                f"<@!{author.id}>",
                author.mention,
                author.name,
                author.display_name,
                unicodedata.normalize("NFC", author.name),
                unicodedata.normalize("NFC", author.display_name),
            ]
        ) 
        pattern = re.compile(fr"({names})\s+is\s+")
        
        content = message.content.lower()
        match = pattern.match(content)
        if match is None: 
            return

        tile = re.sub(pattern, "", content, 1)

        add = True
        if tile.startswith("not"):
            tile = tile[3:].strip()
            add = False

        if len(tile) == 0 or len(tile) > 10:
            return

        if tile not in self.bot.object_roles:
            if add:
                return await message.channel.send(
                    f"{message.author.mention}" 
                    "<a:is:793742253452558356>" 
                    "<a:not:793742269848354856>"
                    f"{inline_codeblock(tile).upper()} (that isn't an icon I know!)"
                )
            else:
                return await message.channel.send(
                    f"{message.author.mention}" 
                    "<a:is:793742253452558356>" 
                    "<a:not:793742269848354856>"
                    "<a:not:793742269848354856>"
                    f"{inline_codeblock(tile).upper()} (that isn't an icon I know)"
                )

        role_icon = self.bot.object_roles[tile]
        role_id = role_icon['role_id']
        emoji_id = role_icon['text_id']
        
        role = message.guild.get_role(role_id)
        if role is None:
            return

        try:
            if add:
                object_ids = [
                    id for [id, _] in self.bot.object_roles.values()
                ]
                held_roles = [
                    role
                    for role in message.author.roles
                    if role.id in object_ids
                ]
                await author.remove_roles(*held_roles)
                await author.add_roles(role)
                await message.channel.send(
                    f"{message.author.mention} <a:is:793742253452558356> <a:{tile}:{emoji_id}>"
                )
            else:
                await author.remove_roles(role)
                await message.channel.send(
                    f"{message.author.mention} <a:is:793742253452558356> <a:not:793742269848354856> <a:{tile}:{emoji_id}>"
                )
        except discord.Forbidden:
            if add:
                return await message.channel.send(
                    f"{message.author.mention}" 
                    "<a:is:793742253452558356>" 
                    "<a:not:793742269848354856>"
                    f"<a:{tile}:{emoji_id}> (I can't edit your roles due to permissions!)"
                )
            else:
                return await message.channel.send(
                    f"{message.author.mention}" 
                    "<a:is:793742253452558356>" 
                    "<a:not:793742269848354856>"
                    "<a:not:793742269848354856>"
                    f"<a:{tile}:{emoji_id}> (I can't edit your roles due to permissions!)"
                )   

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.role_assign(message)

def setup(bot):
    bot.add_cog(RoleIconCog(bot))

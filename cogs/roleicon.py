# -*- coding: utf-8 -*-

from __future__ import annotations

import re
import unicodedata

import discord
from bot import Bot
from discord.ext import commands

from cogs.errors import *


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
            (name, f"<@&{icon['role_id']}>")
            for name, icon in self.bot.object_roles.items()
        )
        icon_mentions = [x for _, x in icons]

        for i in range(0, len(icons), 10):
            embed.add_field(
                name="\u200b",
                value="\n".join(icon_mentions[i:i+10]),
                inline=True
            )

        await ctx.send(embed=embed)
    
    async def role_assign(self, message: discord.Message):
        if not isinstance(message.author, discord.Member) or message.guild is None:
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
        
        mention = message.author.mention
        is_ =  "<a:is:793742253452558356>"
        not_ = "<a:not:793742269848354856>"
        prefix = f"{mention} {is_}{not_ if not add else ''}"

        if tile not in self.bot.object_roles:
            msg = f"{prefix}{not_} {inline_codeblock(tile).upper()} (that isn't an icon I know)"
            
            return await self.bot.clearable_send(message.author.id, message.channel, msg)
            
        role_icon = self.bot.object_roles[tile]
        role_id = role_icon['role_id']
        emoji_id = role_icon['text_id']
        target = f"<a:{tile}:{emoji_id}>"
        
        role = message.guild.get_role(role_id)
        if role is None:
            return

        try:
            if add:
                object_ids = [
                    icon["role_id"] for icon in self.bot.object_roles.values()
                ]
                held_roles = [
                    role
                    for role in message.author.roles
                    if role.id in object_ids
                ]
                await author.remove_roles(*held_roles)
                await author.add_roles(role)
            else:
                await author.remove_roles(role)
            await self.bot.clearable_send(
                message.author.id,
                message.channel,
                f"{prefix}{target}"
            )
        except discord.Forbidden:
            return await  self.bot.clearable_send(
                message.author.id,
                message.channel,
                f"{prefix}{not_}{target} (I can't edit your roles due to permissions!)"
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.role_assign(message)

async def setup(bot: Bot):
    await bot.add_cog(RoleIconCog(bot))

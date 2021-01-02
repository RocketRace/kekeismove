import discord
from cogs.errors import *
from discord.ext import commands

async def has_staff_permissions(ctx: commands.Context) -> bool:
    return discord.utils.get(
        ctx.author.roles,
        id=ctx.bot.settings["staff_role"]
    ) is not None or await ctx.bot.is_owner(ctx.author)

def mention_role(ctx: commands.Context):
    def inner(role: int):
        return ctx.guild.get_role(role).mention
    return inner

def members(ctx: commands.Context):
    def inner(role: int):
        return len(ctx.guild.get_role(role).members)
    return inner

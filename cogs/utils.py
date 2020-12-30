import discord
from cogs.errors import *
from discord.ext import commands

async def has_staff_permissions(ctx: commands.Context) -> bool:
    return discord.utils.find(
        lambda r: str(r.id) == ctx.bot.settings["staff_role"],
        ctx.author.roles
    ) is not None or await ctx.bot.is_owner(ctx.author)

def mention_role(ctx: commands.Context):
    def inner(role: str):
        return ctx.guild.get_role(int(role)).mention
    return inner

def members(ctx: commands.Context):
    def inner(role: str):
        return len(ctx.guild.get_role(int(role)).members)
    return inner

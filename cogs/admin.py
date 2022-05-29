# -*- coding: utf-8 -*-

import io
import traceback

import discord
from discord.ext import commands

from bot import Bot


class EmbedHelp(commands.DefaultHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(title="Help command", color=15029051, description=page)
            await destination.send(embed=embed)

class Admin(commands.Cog, command_attrs=dict(hidden=True)):
    '''Bot administration'''

    def __init__(self, bot: Bot):
        self.bot = bot
        self._original = bot.help_command
        bot.help_command = EmbedHelp()
    
    def cog_unload(self):
        self.bot.help_command = self._original

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err: commands.CommandError):
        err = getattr(err, "original", err)
        ignored = (commands.CheckFailure, commands.DisabledCommand, commands.CommandNotFound, commands.NotOwner)
        if isinstance(err, ignored):
            return

        elif isinstance(err, discord.Forbidden):
            await ctx.send("I don't have permissions to do that!")
        elif isinstance(err, discord.HTTPException):
            await ctx.send("Something went wrong performing a request...")
        else:
            if hasattr(ctx.command, "on_error"):
                return
            await ctx.send("Something went wrong.")

        tb = "".join(traceback.format_exception(type(err), err, err.__traceback__))
        print(tb)
        await ctx.send(f"{err.__class__.__name__}: {err}")

    @commands.command()
    async def load(self, ctx: commands.Context, *cogs: str):
        '''Load cogs'''
        if len(cogs) == 0:
            for cog in self.bot.cog_names:
                self.bot.reload_extension(cog)
        else:
            for cog in cogs:
                self.bot.reload_extension(f"cogs/{cog}")
        await ctx.send("Done.")

    @commands.command(name="exit")
    async def exit_(self, ctx: commands.Context):
        '''Bye bye!'''
        await ctx.send("Exiting...")
        await self.bot.close()

    @commands.command()
    async def dev(self, ctx: commands.Context, *, content: str):
        '''Evals code'''
        import contextlib
        buf = io.StringIO()
        coro = '''async def _():\n{}'''
        code = coro.format("    " + content.replace('\n', '\n    '))
        with contextlib.redirect_stdout(buf):
            try:
                glob = globals()
                glob['self'] = self
                glob['ctx'] = ctx
                exec(code, glob)
                await glob['_']()
            except Exception as e:
                await ctx.send('```' + ''.join(traceback.format_exception(type(e), e, e.__traceback__))[:1994] + '```')
            else:
                await ctx.send(f"Success. Output:\n```\n{buf.getvalue()}\n```"[:2000])

    @commands.command(name="newicon")
    async def new_icon(self, ctx: commands.Context, name: str, role: discord.Role, emoji: discord.Emoji):
        '''Registers a new icon'''
        self.bot.object_roles[name] = {'role_id': role.id, 'text_id': emoji.id}
        self.bot.save_settings()
        await ctx.send(f"Added `{name}` icon")

def setup(bot):
    bot.add_cog(Admin(bot))

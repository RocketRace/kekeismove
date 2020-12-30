# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import traceback

class EmbedHelp(commands.DefaultHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            embed = discord.Embed(title="Help command", color=self.context.bot.settings["color"], description=page)
            await destination.send(embed=embed)

class Admin(commands.Cog, command_attrs=dict(hidden=True)):
    '''Bot administration'''

    def __init__(self, bot: commands.Bot):
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
        if len(cogs) == 0:
            for cog in self.bot.cog_names:
                self.bot.reload_extension(cog)
        else:
            for cog in cogs:
                self.bot.reload_extension(f"cogs/{cog}")
        await ctx.send("Done.")

    @commands.command(name="exit")
    async def exit_(self, ctx: commands.Context):
        await ctx.send("Exiting...")
        await self.bot.close()

def setup(bot):
    bot.add_cog(Admin(bot))

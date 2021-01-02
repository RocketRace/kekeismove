# -*- coding: utf-8 -*-

import io
from discord.ext import commands, tasks
import discord
import json

from cogs.utils import *
from cogs.errors import *

class Settings(commands.Cog):
    '''Advanced configuration for the bot'''

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        try:
            with open("settings.json", encoding="utf8") as fp:
                self.bot.settings = self.validate_settings(json.load(fp))
        except (FileNotFoundError, json.JSONDecodeError, BadSettings):
            print("settings.json is missing or corrupt. Defaulting to default_settings.json")
            with open("default_settings.json", encoding="utf8") as fp:
                self.bot.settings = json.load(fp)
        self.save_settings.start()

    async def cog_check(self, ctx):
        return await has_staff_permissions(ctx)
    
    def validate_settings(self, obj):
        '''Returns the argument if it contains all valid fields, and raises otherwise'''
        try:
            # raise keyerror if any fields are missing
            for field in (
                "prefixes", "color", "disabled_commands", "stats", 
                "server", "staff_role", "contribute_role", "nitro_role",
                "ranks", "special_roles", "pronoun_roles", "nicknames"
            ):
                obj[field]
            obj["stats"]["commands"]
            obj["stats"]["nicknames"]
            obj["special_roles"]["message"]
            obj["special_roles"]["emoji"]
            obj["pronoun_roles"]["message"]
            obj["pronoun_roles"]["emoji"]
            obj["nicknames"]["enabled"]
            obj["nicknames"]["opted_out"]
        except (KeyError, TypeError) as err:
            raise BadSettings(*err.args)
        return obj

    @tasks.loop(minutes=15)
    async def save_settings(self):
        with open("settings.json", "w") as fp:
            json.dump(self.bot.settings, fp, indent=4)
    
    @commands.Cog.listener()
    async def on_command_completion(self, *_):
        self.bot.settings["stats"]["commands"] += 1

    @commands.command()
    async def settings(self, ctx: commands.Context):
        '''Displays the current bot settings'''
        mention = mention_role(ctx)

        embed = discord.Embed(title="Bot settings", color=self.bot.settings["color"])
        embed.add_field(name="Prefixes", value=f"`{ctx.me}`\n" + "\n".join(f"`{p}`" for p in self.bot.settings["prefixes"]))
        embed.add_field(name="Commands", value=f"{len(self.bot.settings['disabled_commands'])} disabled")
        embed.add_field(name="Ranks", value=f"{len(self.bot.settings['ranks'])} set")
        enabled = 'enabled' if self.bot.settings['nicknames']['enabled'] else 'disabled'
        opted_out = len(self.bot.settings['nicknames']['opted_out'])
        embed.add_field(name="Nicknames", value=f"Auto-changes {enabled}\n`{opted_out}` members opted out")
        embed.set_footer(text="See the <export> command for more detailed information.")
        await ctx.send(embed=embed)

    @settings.error
    async def settings_error(self, ctx: commands.Context, err: commands.CommandError):
        err = getattr(err, "original", err)
        if isinstance(err, AttributeError):
            await ctx.send("Not all IDs in the settings are valid. See the <import> and <export> commands to fix this.")
        elif isinstance(err, MissingReactionRole):
            await ctx.send("The reaction role message is set but the message is missing. " + \
                "Unset it using the <rr unset> command, or set a new one using the <rr set> command.")

    @commands.command(name="import", usage="import <file>")
    async def import_(self, ctx: commands.Context):
        '''Imports bot settings from a JSON file'''
        if len(ctx.message.attachments) != 1:
            raise MissingFile
        file = ctx.message.attachments[0]
        try:
            self.bot.settings = self.validate_settings(json.load(file))
            self.save_settings.restart()
        except json.JSONDecodeError:
            raise BadFile
        else:
            await ctx.send("Successfully imported settings.")

    @import_.error
    async def import_error(self, ctx: commands.Context, err: commands.CommandError):
        if isinstance(err, MissingFile):
            await ctx.send("You must provide a file to import from in the command, as an attachment.")
        elif isinstance(err, BadFile):
            await ctx.send("The file you provided is not valid JSON.")
        elif isinstance(err, BadSettings):
            try:
                await ctx.send(f"The settings file is missing the required <{err.args[0]}> field.")
            except IndexError:
                await ctx.send(f"The settings file is missing a required field.")

    @commands.command()
    async def export(self, ctx: commands.Context):
        '''Exports bot settings to a JSON file'''
        buf = io.StringIO()
        json.dump(self.bot.settings, buf, indent=4)
        buf.seek(0)
        await ctx.send("Successfully exported bot settings:", file=discord.File(buf, filename="settings.json"))
        self.save_settings.restart()
    
    @commands.command(name="addprefix")
    async def add_prefix(self, ctx: commands.Command, prefix: str):
        '''Adds a prefix to the bot'''
        if prefix not in self.bot.settings["prefixes"]:
            self.bot.settings["prefixes"].append(prefix)
        await ctx.send(f"Prefix `{prefix}` successfully registered.")

    @commands.command(name="removeprefix")
    async def remove_prefix(self, ctx: commands.Command, prefix: str):
        '''Removes a prefix from the bot'''
        try:
            self.bot.settings["prefixes"].remove(prefix)
        except ValueError:
            raise BadPrefix(prefix)
        await ctx.send(f"Prefix `{prefix}` removed. Note that you can always ping the bot to execute commands.")

    @remove_prefix.error
    async def remove_prefix_error(self, ctx: commands.Context, err: commands.CommandError):
        if isinstance(err, BadPrefix):
            await ctx.send(f"`{err.prefix}` is not a currently active prefix.")

    @commands.command(name="enablecommand", aliases=["enable"])
    async def enable_command(self, ctx: commands.Command, command: str):
        '''Enables a command'''
        cmd = self.bot.get_command(command)
        if cmd is None:
            raise BadCommand(command)
        cmd.enabled = True
        if command in self.bot.settings["disabled_commands"]:
            self.bot.settings["disabled_commands"].remove(command)
        await ctx.send(f"Successfully enabled <{command}>.")
    
    @enable_command.error
    async def enable_command_error(self, ctx: commands.Context, err: commands.CommandError):
        err = getattr(err, "original", err)
        if isinstance(err, BadCommand):
            await ctx.send(f"<{err.args[0]}> is an invalid command.")
        
    @commands.command(name="disablecommand", aliases=["disable"])
    async def disable_command(self, ctx: commands.Command, command: str):
        '''Disables a command'''
        cmd = self.bot.get_command(command)
        if cmd is None or isinstance(cmd.cog, Settings):
            raise BadCommand(command)
        cmd.enabled = False
        if command not in self.bot.settings["disabled_commands"]:
            self.bot.settings["disabled_commands"].append(command)
        await ctx.send(f"Successfully disabled <{command}>.")

    @disable_command.error
    async def disable_command_error(self, ctx: commands.Context, err: commands.CommandError):
        err = getattr(err, "original", err)
        if isinstance(err, BadCommand):
            await ctx.send(f"<{err.args[0]}> is either an invalid command or cannot be disabled (such as this command).")

def setup(bot):
    bot.add_cog(Settings(bot))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
import discord
import config

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cog_names = config.cogs
        for cog in config.cogs:
            try:
                self.load_extension(cog)
            except Exception as err:
                print(f"Could not load extension {cog} due to {err.__class__.__name__}: {err}")

    async def on_ready(self):
        print(f"Logged on as {self.user} (ID: {self.user.id})")
        print(discord.utils.oauth_url(self.user.id ,permissions=discord.Permissions(470150208)))

intents = discord.Intents(
    guilds=True, # required for basic functions
    members=True, # required for role management
    messages=True, # required for commands
    reactions=True # required for reaction roles
)

def get_prefix(bot, message):
    return commands.when_mentioned_or(*bot.settings["prefixes"])(bot, message)

bot = Bot(
    command_prefix=get_prefix,
    intents=intents,
    allowed_mentions=discord.AllowedMentions.none() # the bot pings nobody unless specified
)

@bot.check
async def global_check(ctx: commands.Context):
    return ctx.guild is not None and ctx.guild.id == bot.settings["server"]
    # No DM commands, only allowed in one guild

bot.run(config.token)

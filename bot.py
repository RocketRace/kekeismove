#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import TypedDict

import discord
from discord.ext import commands

import config

class RoleIcon(TypedDict):
    role_id: int
    object_id: int
    text_id: int

class Bot(commands.Bot):
    nicknames_changed: int
    opted_in: list[int]
    nicknames_enabled: bool
    roles_enabled: bool
    object_roles: dict[str, RoleIcon]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cog_names = config.cogs
        try:
            with open("settings.json") as f:
                obj = json.load(f)
                self.nicknames_changed = obj["nicknames_changed"]
                self.opted_in = obj["opted_in"]
                self.nicknames_enabled = obj["enabled"]
                self.roles_enabled = obj["roles"]
                self.object_roles = obj["objects"]
        except FileNotFoundError:
            self.nicknames_changed = 0
            self.opted_in = []
            self.roles_enabled = True
            self.nicknames_enabled = True
            self.object_roles = {}

        for cog in config.cogs:
            try:
                self.load_extension(cog, package="bot")
            except Exception as err:
                print(f"Could not load extension {cog} due to {err.__class__.__name__}: {err}")

    async def on_ready(self):
        print(f"Logged on as {self.user} (ID: {self.user.id})")
        print(discord.utils.oauth_url(str(self.user.id) ,permissions=discord.Permissions(470150208)))

    def save_settings(self):
        obj = {
            "nicknames_changed": self.nicknames_changed,
            "opted_in": self.opted_in,
            "enabled": self.nicknames_enabled,
            "roles": self.roles_enabled,
            "objects": self.object_roles
        }
        json.dump(obj, open("settings.json", "w"))

    async def close(self):
        self.save_settings()

intents = discord.Intents(
    guilds=True, # required for basic functions
    guild_messages=True, # required for commands & rr
    members=True, # required to keep track of icon roles
)

def get_prefix(bot, message):
    return commands.when_mentioned_or("!")(bot, message)

bot = Bot(
    command_prefix=get_prefix,
    intents=intents,
    activity=discord.Game(name="!help"),
    allowed_mentions=discord.AllowedMentions.none() # the bot pings nobody unless specified
)

@bot.check
async def global_check(ctx: commands.Context):
    return ctx.guild is not None
    # No DM commands, only allowed in one guild

bot.run(config.token)

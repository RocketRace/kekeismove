# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import json
from typing import TypedDict

import discord
from discord.ext import commands

import config


class RoleIcon(TypedDict):
    role_id: int
    text_id: int

class EmojiConfig(TypedDict):
    delete: int
    is_: int
    not_: int

class Bot(commands.Bot):
    nicknames_changed: int
    opted_in: list[int]
    nicknames_enabled: bool
    roles_enabled: bool
    object_roles: dict[str, RoleIcon]
    emoji_data: EmojiConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cog_names = config.cogs
        self.emoji_data = config.emoji
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

    async def setup_hook(self):
        for cog in config.cogs:
            try:
                await self.load_extension(cog, package="bot")
            except Exception as err:
                print(f"Could not load extension {cog} due to {err.__class__.__name__}: {err}")

    async def on_ready(self):
        if self.user is not None:
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
        json.dump(obj, open("settings.json", "w"), indent=4)

    async def clearable_send(self, author_id: int, channel: discord.abc.MessageableChannel, content: str):
        message = await channel.send(content)
        emoji = self.get_emoji(self.emoji_data["delete"])
        if emoji:
            await message.add_reaction(emoji)

            def check(react: discord.RawReactionActionEvent):
                return (
                    react.message_id == message.id and
                    react.emoji.id == emoji.id and
                    react.user_id == author_id
                ) 
            
            try:
                await self.wait_for("raw_reaction_add", check=check, timeout=180.0)
                await message.delete()
            except asyncio.TimeoutError:
                await message.remove_reaction(emoji, message.author)

    async def close(self):
        self.save_settings()
        await super().close()

intents = discord.Intents(
    guilds=True,
    guild_messages=True,
    reactions=True,
    message_content=True,
    members=True,
)

def get_prefix(bot: Bot, message: discord.Message):
    return commands.when_mentioned_or(config.prefix)(bot, message)

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

if __name__ == "__main__":
    bot.run(config.token)

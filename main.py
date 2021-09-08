import os
import asyncio
import sys

from config import *
from data import *

import discord
from discord import utils
from discord.ext import commands

ask_for_channel = "What channel should anonymous messages be sent to?"
complete = "The bot has been configured."
overwrite = "The bot has been configured already, continue? (y/n)"
stop = "The configuration has been aborted."
unconfigured = "The bot needs to be configured first."
channel_not_found = "The specified channel does not exist."
description = "A basic Discord bot allowing anonymous messages to be collected (through DMs) and sent to a specific channel in a server."

class AnonyBot(commands.Bot):
    def __init__(self, cache, server = None, channel = None, configured = None):
        super().__init__(description = description, command_prefix = '&')
        self.cache = cache
        self.server = None
        self.channel = None
        self.configured = False

    def is_me(self, author):
        return author == self.user

    def is_owner(self, author):
        return not self.server or author == self.server.owner

    def load_config(self, cache):
        saved = cache.load('saved_config.json').value
        if saved:
            self.server = self.get_guild(saved['server'])
            self.role = self.find_role(saved['role'])
            self.channel = self.find_channel(saved['channel'])
            self.counter = 0
            return True
        else:
            return False

    def save_config(self):
        saved = {
            "server": self.server.id,
            "channel": self.channel.name,
            "role": self.role.name,
        }
        self.cache.save('saved_config.json', saved)

    def is_command(self, commad, string):
        return string.strip().split(' ')[0] == f"{self.command_prefix}{command}"

    def like_command(self, command, string):
        return string.strip().split(' ')[0].startswith(f"{self.command_prefix}{command}")

    def find_role(self, name_or_id):
        roles = self.server.roles
        if name_or_id.startswith('<@&'):
            _id = name_or_id[3:-1]
            return utils.find(lambda x: x.id == _id, roles)
        else:
            return utils.find(lambda x: x.name == name_or_id, roles)

    def find_channel(self, name_or_id):
        if name_or_id.startswith('<#'):
            _id = name_or_id[2:-1]
            return self.get_channel(_id)
        else:
            return utils.find(lambda x: x.name == name_or_id, self.get_all_channels())

    async def configure(self, channel, author):
        async def say(message):
            await channel.send(message)

        def check(message):
            return message.author == author and message.channel == channel

        async def ask(message):
            await say(message)
            return await self.wait_for('message', check = check)

        def is_yn(message):
            return check(message) and message.content.lower() in ['y', 'yes', 'n', 'no']

        async def ask_yn(message):
            await say(message)
            return await self.wait_for('message', check = is_yn)

        if self.configured:
            answer = await ask_yn(overwrite)
            if answer.content.lower() in ['n', 'no']:
                await say(stop)
                return

        self.server = channel.guild
        self.channel = channel
        while True:
            role = await ask(ask_for_role)
            self.role = self.find_role(role.content)
            if self.role:
                break
            else:
                await say(role_not_found)
        while True:
            message = await ask(ask_for_channel)
            self.channel = self.find_channel(message.content)
            if self.channel:
                break
            else:
                await say(channel_not_found)
        
        self.save_config()
        await say(complete)
        self.configured = True

    def check_allowed(self, user):
        _member = utils.find(lambda x: x.id == user.id, self.get_all_members())
        if not _member:
            return False
        return self.role in _member.roles

    def header(self):
        return f'```css\nMessage # {self.counter:05}\n```'

    async def forward(self, message):
        self.counter += 1
        frame = '\n'.join([self.header(), message])
        await self.channel.send(frame)

def configure():
    cache = Data(data)
    bot = AnonyBot(cache)

    @bot.event
    async def on_ready():
        print("AnonyBot is up and running!")
        bot.configured = bot.load_config(cache)

    @bot.event
    async def on_message(message):
        if bot.is_me(message.author):
            return
        
        # print("Got a message")

        async def say(message_id):
            await message.channel.send(message_id)

        if isinstance(message.channel, discord.abc.PrivateChannel):
            if not bot.configured:
                await say(unconfigured)
            else:
                await bot.forward(message.content)
            return

        if bot.like_command("configure", message.content):
            await bot.configure(message.channel, message.author)

    return bot

if __name__ == '__main__':
    bot = configure()
    bot.run(token)

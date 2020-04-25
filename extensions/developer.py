'''
MIT License

Copyright (c) 2020 Martin Velikov & Patrick Thompson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import discord
from discord.ext import commands
import asyncio
import datetime
import random
import subprocess
import dbcontrol

# helpful functions
import utils

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Developer-related commands. Devs only.'

    @commands.check(utils.is_developer)
    @commands.command(brief='Reloads a cog (for developer use only)', usage='[cog]', aliases=['rl', 'rload'], hidden=True)
    async def reload(self, ctx, cog):
        self.bot.reload_extension(f'extensions.{cog}')
        self.bot.logger.info(f"Cog {cog} reloaded by {ctx.message.author} ({ctx.message.author.id})")
        await ctx.send(f":thumbsup: **Extension ``{cog}`` successfully reloaded**")

    @commands.check(utils.is_developer)
    @commands.command(brief='Die bitch', aliases=['die', 'fuckoff'], hidden=True)
    async def suicide(self, ctx):
        await ctx.send(':weary::gun: **Farewell...**')
        if ctx.message.guild:
            self.bot.logger.info(f"Bot terminated from {ctx.message.guild} ({ctx.message.guild.id}) by {ctx.message.author} ({ctx.message.author.id})")
        else:
            self.bot.logger.info(
                f"Bot terminated from dms by {ctx.message.author} ({ctx.message.author.id})")
        self.bot.logger.info('Bot has shut down successfully.')
        await self.bot.logout()

    @commands.check(utils.is_developer)
    @commands.command(brief='Update presences rotation', hidden=True)
    async def updatepres(self, ctx):
        self.bot.presence_looping = False
        self.bot.loop.create_task(self.bot.presence_changer())
        await ctx.send(':thumbsup: **Presence loop restarted.**')

    @commands.check(utils.is_developer)
    @commands.command(brief='Loads an extension', usage='[cog]', hidden=True)
    async def load(self, ctx, cog):
        self.bot.load_extension(f'extensions.{cog}')
        self.bot.logger.info(f"Cog {cog} loaded by {ctx.message.author} ({ctx.message.author.id})")
        await ctx.send(f":thumbsup: **Extension ``{cog}`` successfully loaded**")

    @commands.check(utils.is_developer)
    @commands.command(brief='Unloads a loaded extension', aliases=['uload'], usage='[cog]', hidden=True)
    async def unload(self, ctx, cog):
        self.bot.unload_extension(f'extensions.{cog}')
        self.bot.logger.info(f"Cog {cog} unloaded by {ctx.message.author} ({ctx.message.author.id})")
        await ctx.send(f":thumbsup: **Extension ``{cog}`` successfully loadn't**")

    @commands.check(utils.is_developer)
    @commands.command(brief='Runs an SQL command', aliases=['sequel', 'database', 'db'], usage='[sql command]', hidden=True)
    async def sql(self, ctx, *, command):
        await dbcontrol.run_command(command)
        self.bot.logger.info(f"SQL command ({command}) run by {ctx.message.author} ({ctx.message.author.id})")

    @commands.check(utils.is_developer)
    @commands.command(hidden=True)
    async def blacklist(self, ctx, user: discord.User):
        if user.bot:
            await ctx.send(':x:**You cannot blacklist a bot**')
        elif utils.check_dev(user.id):
            await ctx.send(':x:**You cannot blacklist a developer**')
        else:
            await dbcontrol.modify_user(user.id, 'blacklist', 1)
            await ctx.send(f':thumbsup:**User {user} has been successfully blacklisted**')

    @commands.check(utils.is_developer)
    @commands.command(hidden=True)
    async def unblacklist(self, ctx, user: discord.User):
        if not await dbcontrol.is_blacklist(user.id):
            await ctx.send(f':x:**User {user} is not currently blacklisted')
        else:
            await dbcontrol.modify_user(user.id, 'blacklist', 0)
            await ctx.send(f':thumbsup:**User {user} has been successfully unblacklisted**')


def setup(bot):
    bot.add_cog(Developer(bot))

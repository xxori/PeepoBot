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
    @commands.command(brief='Reloads a cog (for developer use only)', usage='[cog]', aliases=['rl', 'rload'])
    async def reload(self, ctx, cog):
        self.bot.reload_extension(f'extensions.{cog}')
        self.bot.logger.info(f"Cog {cog} reloaded by {ctx.message.author} ({ctx.message.author.id})")
        await ctx.send(f":white_check_mark: **Extension ``{cog}`` successfully reloaded**")

    @commands.check(utils.is_developer)
    @commands.command(brief='Die bitch', aliases=['die', 'fuckoff'])
    async def suicide(self, ctx):
        await ctx.send(':weary::gun: **Farewell...**')
        if ctx.message.guild:
            self.bot.logger.info(f"Bot terminated from {ctx.message.guild} ({ctx.message.guild.id}) by {ctx.message.author} ({ctx.message.author.id})")
        else:
            self.bot.logger.info(
                f"Bot terminated from dms by {ctx.message.author} ({ctx.message.author.id})")
        await self.bot.logout()

    @commands.check(utils.is_developer)
    @commands.command(brief='Update presences rotation')
    async def updatepres(self, ctx):
        self.bot.presence_looping = False
        self.bot.loop.create_task(self.bot.presence_changer())
        await ctx.send(':thumbsup: **Presence loop restarted.**')

    @commands.check(utils.is_developer)
    @commands.command(brief='niga', usage='[cog]')
    async def load(self, ctx, cog):
        self.bot.load_extension(f'extensions.{cog}')
        self.bot.logger.info(f"Cog {cog} loaded by {ctx.message.author} ({ctx.message.author.id})")
        await ctx.send(f":white_check_mark: **Extension ``{cog}`` successfully loaded**")

    @commands.check(utils.is_developer)
    @commands.command(brief='Unloads a loaded extension', aliases=['uload'], usage='[cog]')
    async def unload(self, ctx, cog):
        self.bot.unload_extension(f'extensions.{cog}')
        self.bot.logger.info(f"Cog {cog} unloaded by {ctx.message.author} ({ctx.message.author.id})")
        await ctx.send(f":white_check_mark:** Extension ``{cog}`` successfully loadn't**")

    @commands.check(utils.is_developer)
    @commands.command(brief='Runs an SQL command', aliases=['sequel', 'database', 'db'], usage='[sql command]')
    async def sql(self, ctx, *, command):
        await dbcontrol.run_command(command)
        self.bot.logger.info(f"SQL command ({command}) run by {ctx.message.author} ({ctx.message.author.id})")


def setup(bot):
    bot.add_cog(Developer(bot))

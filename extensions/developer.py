import discord
from discord.ext import commands
import asyncio
import datetime
import random

# helpful functions
import utils

class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Developer-related commands. Devs only.'

    @commands.check(utils.is_developer)
    @commands.command(brief='Reloads a cog (for developer use only)', usage='[cog]')
    async def reload(self, ctx, cog):
        try:
            self.bot.reload_extension(f'extensions.{cog}')
        except commands.ExtensionNotLoaded:
            await ctx.send(f':x: **Extension ``{cog}`` is not loaded.**')
            return

        await ctx.send(f":white_check_mark: **Extension ``{cog}`` successfully reloaded**")

    @commands.check(utils.is_developer)
    @commands.command(brief='Die bitch')
    async def suicide(self, ctx):
        await ctx.send(':weary::gun: **Farewell...**')
        await self.bot.logout()

    @commands.check(utils.is_developer)
    @commands.command(brief='Update presences rotation')
    async def updatepres(self, ctx):
        self.bot.presence_looping = False
        self.bot.loop.create_task(self.bot.presence_changer())
        await ctx.send(':thumbsup: **Presence loop restarted.**')


def setup(bot):
    bot.add_cog(Developer(bot))

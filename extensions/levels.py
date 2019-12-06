import discord
from discord.ext import commands
import asyncio
import dbcontrol
import datetime
import aiohttp
import random
import utils
import time


class Leveling(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @property
    def description(self):
        return 'Fun levelling-related commands'

    @commands.command(brief='View you or a user''s level and exp.', usage='[user]')
    async def level(self, ctx, user:discord.Member = None):
        if user is None:
            user = ctx.message.author

        user_info = await dbcontrol.get_user(user.id)
        level = user_info['level']
        exp = user_info['exp']
        exp_required = user_info['exp_required']

        embed=discord.Embed(colour=discord.Colour.blurple())
        embed.set_author(name=str(user), icon_url=user.avatar_url)

        embed.description = f':small_blue_diamond: **Level:** {level}\n:small_orange_diamond: **EXP:** {exp}/{exp_required}'
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Leveling(bot))
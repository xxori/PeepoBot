import discord
from discord.ext import commands
import asyncio
import dbcontrol
import datetime
import aiohttp
import random
import utils
import time


class Profiles(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @property
    def description(self):
        return 'manage and view user profiles'

    @commands.command(brief='View a user profile', alias=['p'], usage='[user]')
    async def profile(self, ctx, user:discord.Member=None):
        if user is None:
            user = ctx.message.author

        user_info = await dbcontrol.get_user(user.id)
        bio = user_info['bio']
        image_url = user_info['image_url']

        embed = discord.Embed(
            color=user.colour,
            description=bio if len(bio) else f"Hi! I'm {user.name}, nice to meet you!"
        )

        embed.set_author(name=f'{user}', icon_url=user.avatar_url)
        if len(image_url) > 0:
            try:
                embed.set_image(image_url)
            except:
                # invalid image url
                pass
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Profiles(bot))

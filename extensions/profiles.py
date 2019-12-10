import discord
from discord.ext import commands
import asyncio
import dbcontrol
import datetime
import aiohttp
import random
import utils
import time
from colour import Color

class Profiles(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @property
    def description(self):
        return 'manage and view user profiles'

    @commands.group(invoke_without_command=True)
    async def profile(self, ctx, user:discord.Member=None):
        if ctx.invoked_subcommand is None:
            if user is None:
                user = ctx.message.author

            user_info = await dbcontrol.get_user(user.id)
            bio = user_info['bio']
            image_url = user_info['image_url']
            color = user_info['profile_color']

            embed = discord.Embed(
                color=color if color else user.color,
                description=bio if len(bio) else f"Hi! I'm {user.name}, nice to meet you!"
            )

            embed.set_author(name=f'{user}', icon_url=user.avatar_url)
            if len(image_url):
                try:
                    embed.set_image(url=image_url)
                except:
                    # invalid image url
                    pass
            await ctx.send(embed=embed)

    @profile.command(brief='Sets profile embed colour', aliases=['colour'], usage='<colour>')
    async def color(self, ctx, *, color: discord.Color):
        await dbcontrol.modify_user(ctx.author.id, 'profile_color', color.value)
        await ctx.send(f":white_check_mark: **Profile color set to `{color}`.**")

    @profile.command(brief='Sets bio text on profile')
    async def bio(self, ctx, *, bio):
        await dbcontrol.modify_user(ctx.author.id, 'bio', bio)
        await ctx.send(f':white_check_mark: **Bio successfully updated to** ```\n{bio}```')

    @profile.command(brief='Sets image displayed on profile', usage='<image url or attachment>')
    async def image(self, ctx, url=None):
        if url == None and len(ctx.message.attachments):
            url = ctx.message.attachments[0].url
        await dbcontrol.modify_user(ctx.author.id, 'image_url', url)
        await ctx.send(f":white_check_mark: **Profile image set to** ```\n{url}```")

def setup(bot):
    bot.add_cog(Profiles(bot))

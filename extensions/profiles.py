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

    @commands.group(invoke_without_command=True)
    async def profile(self, ctx, user:discord.Member=None):
        if ctx.invoked_subcommand is None:
            if user is None:
                user = ctx.message.author

            user_info = await dbcontrol.get_user(user.id)
            bio = user_info.get('bio')
            image_url = user_info.get('image_url')
            color = user_info.get('profile_color')

            embed = discord.Embed(
                color=color if color else user.color,
                description=bio if len(bio) else f"Hi! I'm {user.name}, nice to meet you!"
            )
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=f"{user}'s profile", icon_url=user.avatar_url)
            if len(image_url):
                try:
                    embed.set_image(url=image_url)
                except:
                    # invalid image url
                    pass
            await ctx.send(embed=embed)

    @profile.command(brief='Sets profile embed colour', aliases=['colour'], usage='<colour>')
    async def color(self, ctx, *, colour):

        colour = utils.colour(colour)
        if colour:
            await dbcontrol.modify_user(ctx.author.id, 'profile_color', colour.value)
            await ctx.send(f":thumbsup: **Profile color set to `{colour.value}`.**")
        else:
            await ctx.send(":x: **Invalid colour**")

    @profile.command(brief='Sets bio text on profile')
    async def bio(self, ctx, *, bio):
        await dbcontrol.modify_user(ctx.author.id, 'bio', bio)
        await ctx.send(f':thumbsup: **Bio successfully updated to** ```\n{bio}```')

    @profile.command(brief='Sets image displayed on profile', usage='<image url or attachment>')
    async def image(self, ctx, url=None):
        if url == None and len(ctx.message.attachments):
            url = ctx.message.attachments[0].url
        await dbcontrol.modify_user(ctx.author.id, 'image_url', url)
        await ctx.send(f":thumbsup: **Profile image set to** ```\n{url}```")

def setup(bot):
    bot.add_cog(Profiles(bot))

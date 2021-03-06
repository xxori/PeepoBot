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

import asyncio
import aiohttp
import discord
from discord.ext import commands
import dbcontrol
import random
import utils
import datetime
import json

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Random, fun commands'

    @commands.command(brief='Defines with Urban Dictionary', aliases=['dict', 'ud'], usage='[term]')
    async def urban(self, ctx, *, term):
        async with ctx.typing():
            async with self.bot.session.get(url='http://api.urbandictionary.com/v0/define', params={'term': term}) as response:
                data = await response.json()
            if len(data['list']) == 0:
                embed = discord.Embed(description='No Results Found!', color=0xFF0000)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(color=discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
                embed.set_author(name=f'Definition of {term}')
                embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
                embed.add_field(name='Top Definitions: ', value=data['list'][0]['definition'].replace('[', '').replace(']', ''), inline=False)
                embed.add_field(name='Examples: ', value=data['list'][0]['example'].replace('[', '').replace(']', ''), inline=False)
                await ctx.send(embed=embed)

    @commands.command(brief='Shows posts from the dankmemes subreddit', aliases=['dankmemes'])
    async def meme(self, ctx):
        async with ctx.typing():
            async with self.bot.session.get(url='https://meme-api.herokuapp.com/gimme/dankmemes')  as response:
                data = await response.json()
            embed = discord.Embed(title=data['title'], timestamp=datetime.datetime.utcnow())
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
            embed.set_image(url=data['url'])
            await ctx.send(embed=embed)

    @commands.command(brief="Gets a random dog", usage="[breed or empty fof random]", description="All breeds available at https://dog.ceo/dog-api/breeds-list")
    async def dog(self, ctx, breed=None):
        if breed is None:
            async with self.bot.session.get("https://dog.ceo/api/breeds/image/random") as response:
                if response.status != 200:
                    return await ctx.send(":x: **Dog not found**")
                body = await response.json()
        else:
            async with self.bot.session.get(f"https://dog.ceo/api/breed/{breed}/images/random") as response:
                if response.status != 200:
                    return await ctx.send(":x: **Dog not found :(**")
                body = await response.json()

        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_image(url=body['message'])
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(brief="Gets a random cat")
    async def cat(self, ctx):
        async with self.bot.session.get("https://api.thecatapi.com/v1/images/search") as response:
            if response.status != 200:
                return await ctx.send(":x: **No cat found :(**")
            body = await response.json()
        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_image(url=body[0]['url'])
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def annoy(self, ctx, user: discord.User, text="bepis"):
        dmchannel = user.dm_channel
        if not dmchannel:
            dmchannel = await user.create_dm()
        for _ in range(50):
            await dmchannel.send(text)
            await asyncio.sleep(random.randint(1,10))

def setup(bot):
    bot.add_cog(Fun(bot))

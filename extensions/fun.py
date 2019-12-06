import aiohttp
import discord
from discord.ext import commands
import dbcontrol
from pytz import timezone
import aiosqlite
import random


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Random, fun commands'

    @commands.command(brief='Defines with Urban Dictionary', aliases=['dict', 'ud'], usage='[term]')
    async def urban(self, ctx, *, term):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url='http://api.urbandictionary.com/v0/define', params={'term': term})
            data = await response.json()
            await session.close()
        if len(data['list']) == 0:
            embed = discord.Embed(description='No Results Found!', color=0xFF0000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=0x00FF00)
            embed.set_author(name=f'Definition of {term}')
            embed.add_field(name='Top Definitions: ', value=data['list'][0]['definition'].replace('[', '').replace(']', ''), inline=False)
            embed.add_field(name='Examples: ', value=data['list'][0]['example'].replace('[', '').replace(']', ''), inline=False)
            await ctx.send(embed=embed)

    @commands.command(brief='Shows posts from the dankmemes subreddit', aliases=['dankmemes'])
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url='https://meme-api.herokuapp.com/gimme/dankmemes')
            data = await response.json()
            await session.close()
        embed = discord.Embed(title=data['title'])
        embed.set_image(url=data['url'])
        await ctx.send(embed=embed)

    @commands.command(brief='Ping a random person', aliases=['rping'])
    @commands.has_permissions(mention_everyone=True)
    async def randomping(self, ctx):
        await ctx.send(random.choice(ctx.guild.members).mention)

    @commands.command(brief='Talk to cleverbot', aliases=['cbot'], usage='<sentence>')
    async def cleverbot(self, ctx, *, sentence):
        async with ctx.typing():
            response = await self.bot.cb.getResponse(sentence)
            if response.strip() == '':
                response = '``(no reply)``'
            await ctx.send(response)

def setup(bot):
    bot.add_cog(Fun(bot))
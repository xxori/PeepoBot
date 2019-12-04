import aiohttp
import discord
from discord.ext import commands
import dbcontrol
from pytz import timezone
import aiosqlite

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Random, fun commands'

    @commands.command(brief='Defines with Urban Dictionary')
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

    @commands.command(brief='Shows posts from the dankmemes subreddit')
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url='https://meme-api.herokuapp.com/gimme/dankmemes')
            data = await response.json()
            await session.close()
        embed = discord.Embed(title=data['title'])
        embed.set_image(url=data['url'])
        await ctx.send(embed=embed)

    @commands.command(brief='Adds a tag')
    async def addtag(self, ctx, name, *, content):
        await dbcontrol.add_tag(author=ctx.message.author, name=name, content=content)
        await ctx.send(f":white_check_mark: **Tag {name} successfully added!**")

    @commands.command(brief='Gets a tag')
    async def tag(self, ctx, *, name):
        try:
            tag = await dbcontrol.get_tag(name)
            author = self.bot.get_user(tag['author'])
            embed = discord.Embed(title=tag['name'], color=author.color)
            embed.set_thumbnail(url=author.avatar_url)
            embed.set_footer(text=f"Created on {tag['created']}")
            embed.add_field(name=tag['content'], value=f"Created by {author.mention}")
            await ctx.send(embed=embed)

        except aiosqlite.OperationalError:
            await ctx.send(f"**No tag with the name `{name}` currently exists.**")


def setup(bot):
    bot.add_cog(Fun(bot))
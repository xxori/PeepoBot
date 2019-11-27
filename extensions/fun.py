import aiohttp
import discord
from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Defines with Urban Dictionary')
    async def urban(self, ctx, *, term):
        url = 'http://api.urbandictionary.com/v0/define'
        async with aiohttp.ClientSession().get(url, params={'term': term}) as response:
            data = await response.json()
        if len(data['list']) == 0:
            embed = discord.Embed(description='No Results Found!', color=0xFF0000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Word: ", description=term, color=0x00FF00)
            embed.add_field(name='Top Definitions: ', value=data['list'][0]['definition'], inline=False)
            embed.add_field(name='Examples: ', value=data['list'][0]['example'], inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
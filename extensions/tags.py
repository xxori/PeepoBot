import discord
from discord.ext import commands
import utils
import dbcontrol
import aiosqlite
import datetime

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Tag-related commands'

    @commands.command(brief='Adds a tag', aliases=['tagadd'], usage='[name] <tag content>')
    async def addtag(self, ctx, name, *, content):
        await dbcontrol.add_tag(author=ctx.message.author, guild=ctx.guild, name=name, content=content)
        await ctx.send(f":thumbsup: **Tag ``{name}`` successfully created!**")

    @commands.command(brief='Gets a tag', aliases=['gettag'], usage='<name>')
    async def tag(self, ctx, *, name):
        try:
            tag = await dbcontrol.get_tag(ctx.message.author.id, ctx.guild.id, name)
            if tag is None:
                await ctx.send(':x: **Tag ``{}`` could not be found.**'.format(name))
                return
        except aiosqlite.OperationalError:
            await ctx.send(':x: **Tag ``{}`` could not be found.**'.format(name))
        else:
            await ctx.send(tag['content'])

    @commands.command(brief='View info for the tag', aliases=['tinfo'], usage='<name>')
    async def taginfo(self, ctx, *, name):
        try:
            tag = await dbcontrol.get_tag(ctx.message.author.id, ctx.guild.id, name)
            if tag is None:
                await ctx.send(':x: **Tag ``{}`` could not be found.**'.format(name))
                return
        except aiosqlite.OperationalError:
            await ctx.send(':x: **Tag ``{}`` could not be found.**'.format(name))
        else:
            author = self.bot.get_user(tag['author'])

            embed = discord.Embed(colour=discord.Colour.blurple())
            embed.set_author(name=f'Tag: {name}', icon_url=author.avatar_url)
            embed.add_field(name='Created by', value=str(ctx.message.author))
            embed.add_field(name='Created on', value=datetime.datetime.fromtimestamp(tag['created']).strftime('%A %d %B %Y at %I:%M %p (UTC)'), inline=False)
            embed.add_field(name='Character Count', value=f'{utils.punctuate_number(len(tag["content"]))} characters', inline=False)
            embed.add_field(name='Word Count', value=f'{utils.punctuate_number(len(tag["content"].split(" ")))} words', inline=False)

            await ctx.send(embed=embed)

    @commands.command(brief='Deletes a tag', aliases=['deletetag', 'notag'], usage='[tag name]')
    async def deltag(self, ctx, *, name):
        try:
            tag = await dbcontrol.get_tag(ctx.message.author.id, ctx.guild.id, name)
            if tag:
                await dbcontrol.delete_tag(ctx.author.id, ctx.guild.id, name)
                await ctx.send(f":white_check_mark: **Tag ``{name}`` successfully deleted!**")
            else:
              await ctx.send(':x: **Tag ``{}`` could not be found.**'.format(name))
        except aiosqlite.OperationalError:
            await ctx.send(':x: **Tag ``{}`` could not be found.**'.format(name))

def setup(bot):
    bot.add_cog(Tags(bot))

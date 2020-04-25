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

    @commands.group(invoke_without_command=True, brief="Category for commands related to tags", usage="[subcommand] <arguments>")
    async def tag(self, ctx, *, name):
        if ctx.invoked_subcommand is None:
            tag = await dbcontrol.get_guild_tag(ctx.guild.id, name)
            if tag is None:
                await ctx.send(f':x: **Tag ``{name}`` could not be found.**')
                return
            else:
                await ctx.send(tag['content'])

    @tag.command(brief='Creates a tag in your guild', usage='<tag name> [tag content]')
    async def create(self, ctx, name, *, content):
        tag = await dbcontrol.get_guild_tag(ctx.guild.id, name)
        if tag is not None:
            await ctx.send(f':x: **Tag ``{name}`` already exists and is owned by ``{self.bot.get_user(tag["author"])}``**')
            return
        if name.strip() in ['create', 'delete', 'info', 'list']:
            await ctx.send(f":x: **`{name.strip()}` is a subcommand of `tag`, pick a different name.**")
            return
        await dbcontrol.add_tag(author=ctx.message.author, guild=ctx.guild, name=name, content=content)
        await ctx.send(f":thumbsup: **Tag ``{name}`` successfully created!**")

    @tag.command(brief='Removes one of your tags from your guild', usage='<tag name>')
    async def delete(self, ctx, *, name):
        tag = await dbcontrol.get_guild_tag(ctx.guild.id, name)
        if tag is None:
            await ctx.send(':x: **Tag ``{}`` could not be found.**'.format(name))
            return
        elif tag['author'] != ctx.message.author.id and not ctx.message.author.guild_permissions.manage_messages:
            await ctx.send(':x: **You do not own tag ``{}``.**'.format(name))
            return
        await dbcontrol.delete_tag(tag['author'], ctx.guild.id, name)
        await ctx.send(f":recycle: **Tag ``{name}`` deleted successfully.**")

    @tag.command(brief='Provides information on one of your tags', usage='<tag>')
    async def info(self, ctx, *, name):
        tag = await dbcontrol.get_guild_tag(ctx.guild.id, name)
        if tag is None:
            await ctx.send(':x: **Tag ``{}`` could not be found.**'.format(name))
            return
        author = self.bot.get_user(tag['author'])

        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f'Tag: {name}', icon_url=author.avatar_url)
        embed.add_field(name='Created by', value=str(author))
        embed.add_field(name='Created on', value=datetime.datetime.fromtimestamp(tag['created']).strftime('%A %d %B %Y at %I:%M %p (UTC)'), inline=False)
        embed.add_field(name='Character Count', value=f'{utils.punctuate_number(len(tag["content"]))} characters', inline=False)
        embed.add_field(name='Word Count', value=f'{utils.punctuate_number(len(tag["content"].split(" ")))} words', inline=False)
        await ctx.send(embed=embed)

    @tag.command(brief='Lists all of your tags in the current guild')
    async def list(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author
        tags = await dbcontrol.get_all_tags(user.id, ctx.guild.id)
        embed = discord.Embed(color=discord.Colour.blurple())
        embed.set_author(name=f'Tags by {ctx.author}', icon_url=user.avatar_url)
        for tag in tags:
            embed.add_field(value=tag['name'], name=datetime.datetime.fromtimestamp(tag['created']).strftime('%A %d %B %Y at %I:%M %p (UTC)'), inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Tags(bot))

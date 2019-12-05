import discord
from discord.ext import commands
import utils
import dbcontrol
import aiosqlite

class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Tag-related commands'

    @commands.command(brief='Adds a tag')
    async def addtag(self, ctx, name, *, content):
        await dbcontrol.add_tag(author=ctx.message.author, name=name, content=content)
        await ctx.send(f":white_check_mark: **Tag {name} successfully added!**")

    @commands.command(brief='Gets a tag')
    async def tag(self, ctx, *, name):
        try:
            tag = await dbcontrol.get_tag(ctx.message.author.id, name)
            if tag is None:
                await ctx.send(':x: **Tag ``{}`` could not be found.**')
                return

            author = self.bot.get_user(tag['author'])
            embed = discord.Embed(title=tag['name'], color=0x00FF00)
            embed.set_thumbnail(url=author.avatar_url)
            embed.set_footer(text=f"Created on {tag['created']}")
            embed.add_field(name=tag['content'], value=f"Created by {author.mention}")
            await ctx.send(embed=embed)

        except aiosqlite.OperationalError:
            await ctx.send(':x: **Tag ``{}`` could not be found.**')

def setup(bot):
    bot.add_cog(Tags(bot))

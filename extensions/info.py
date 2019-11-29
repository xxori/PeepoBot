import discord
from discord.ext import commands
import asyncio
import datetime
import aiohttp
import random


class Tools(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @property
    def description(self):
        return 'Useful commands to provide information'

    @commands.command(brief='Get information about the current guild.', description='Shows useful information like membercount, rolecount and creation date')
    async def ginfo(self, ctx):
        embed = discord.Embed()
        embed.set_author(name='Guild Info')

        embed.add_field(name='Name', value=ctx.guild.name, inline=False)
        embed.add_field(name='Owner', value=f'{str(ctx.guild.owner)} ({ctx.guild.owner_id})')
        embed.add_field(name='Created At', value=ctx.guild.created_at.strftime('%A %d %B %Y at %I:%M %p'), inline=False)

        botcount = len([m for m in ctx.guild.members if m.bot])
        humancount = ctx.guild.member_count - botcount

        embed.add_field(name='Members', value=f'{ctx.guild.member_count} total, {humancount} humans, {botcount} bots', inline=False)
        embed.add_field(name='Channels', value=f'{len(ctx.guild.text_channels)} text, {len(ctx.guild.voice_channels)} voice', inline=False)
        embed.add_field(name='Roles', value=str(len(ctx.guild.roles)), inline=False)
        embed.add_field(name='Region', value=str(ctx.guild.region).capitalize(), inline=False)

        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(brief='Get information about your Discord account.', description='Shows information about ')
    async def uinfo(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.message.author
        embed = discord.Embed(color=user.color)
        embed.set_author(name=f'User Info: {user.name}')
        embed.add_field(name='ID', value=user.id, inline=False)
        embed.add_field(name='Highest role', value=user.top_role, inline=False)
        embed.add_field(name='Joined Server', value=user.joined_at.strftime('%A %d %B %Y at %I:%M %p'), inline=False)
        embed.add_field(name='Account Created', value=user.created_at.strftime('%A %d %B %Y at %I:%M %p'), inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name='Nickname: ', value=user.nick, inline=False)
        if user.activity:
            embed.add_field(name='Current Activity: ', value=user.activity.name, inline=False)
        else:
            embed.add_field(name='Current Activity: ', value=user.activity, inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief='Finds bot latency', description='Displays the bots latency in milleseconds.')
    async def ping(self, ctx):
        embed = discord.Embed(color=0xff0000 if self.bot.latency * 1000 > 400 else 0x00ff00)
        if random.randint(1,2) == 1:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url='https://uselessfacts.jsph.pl/random.json?language=en')
                fact = await response.json()
                await session.close()
            value = fact['text']
        else:
            async with aiohttp.ClientSession() as session:
                response = await session.get(url='https://sv443.net/jokeapi/category/Any?blacklistFlags=nsfw')
                data = await response.json()
                await session.close()
            if data['type'] == 'twopart':
                value = data['setup'] + '\n' + data['delivery']
            else:
                value = data['joke']
        embed.add_field(name=':hourglass:' + str(round(self.bot.latency * 1000, 2)) + 'ms', value=value)
        await ctx.send(embed=embed)

    @commands.command(brief='Find an active channel', description='List all channels and sort by most recent activity.')
    async def active(self, ctx):
        now = datetime.datetime.utcnow()

        embed = discord.Embed()
        desc = ''

        msg = await ctx.send('``Getting channel history...``')

        channels = {}
        for channel in ctx.guild.text_channels:
            lastmsg = [i async for i in channel.history(limit=1)][-1]
            channels[lastmsg.created_at] = channel.id

        for last in reversed(sorted(channels, key=lambda x: x.timestamp())):
            channel_id = channels[last]
            if channel_id != ctx.channel.id:
                time_str = self.bot.strfdelta((last - now - datetime.timedelta(seconds=25)), ' {hours}h {minutes}m {seconds}s').replace(' 0h', '').replace(' 0m', '').replace(' 0s', '').lstrip()
                desc += f'**<#{channel_id}> was active ``{time_str}`` ago.**\n\n'
        embed.description = desc
        await msg.edit(content=f'', embed=embed)

    @commands.command(brief='Reloads a cog (for developer use only)', usage='[cog]')
    async def reload(self, ctx, cog):
        if ctx.message.author.id not in [308034225137778698, 304219290649886720]:
            await ctx.send(f'Sorry, {ctx.message.author.mention}, this command is for developer use only.')
        else:
            self.bot.reload_extension(f'extensions.{cog}')
            await ctx.send(f":white_check_mark: **Extension `{cog}` successfully reloaded**")

    @commands.command(brief='Die bitch')
    async def die(self, ctx):
        if ctx.message.author.id not in [308034225137778698, 304219290649886720]:
            await ctx.send(f'Sorry, {ctx.message.author.mention}, this command is for developer use only.')
        else:
            await ctx.send(':weary::gun: **Farewell...**')
            await self.bot.logout()


def setup(bot):
    bot.add_cog(Tools(bot))
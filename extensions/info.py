import discord
from discord.ext import commands
import asyncio
import datetime

class Tools(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @property
    def description(self):
        return 'meme'

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
        embed.add_field(name='Roles', value=len(ctx.guild.roles), inline=False)
        embed.add_field(name='Region', value=str(ctx.guild.region).capitalize(), inline=False)

        embed.set_thumbnail(url=ctx.guild.icon_url)
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




def setup(bot):
    bot.add_cog(Tools(bot))
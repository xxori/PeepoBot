import discord
from discord.ext import commands
import asyncio
import datetime
import aiohttp
import random
import utils
import time
import re
import dbcontrol
import json

class Utility(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @property
    def description(self):
        return 'Useful commands to provide information'

    @commands.command(brief='Get information about the current guild.', description='Shows useful information like membercount, rolecount and creation date')
    async def ginfo(self, ctx):
        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name='Guild Info')

        embed.add_field(name='Name', value=ctx.guild.name, inline=False)
        embed.add_field(name='Owner', value=str(ctx.guild.owner))
        embed.add_field(name='Created At', value=ctx.guild.created_at.strftime('%A %d %B %Y at %I:%M %p'), inline=False)

        botcount = len([m for m in ctx.guild.members if m.bot])
        humancount = ctx.guild.member_count - botcount

        embed.add_field(name='Members', value=f'{ctx.guild.member_count} total, {humancount} humans, {botcount} bots', inline=False)
        embed.add_field(name='Channels', value=f'{len(ctx.guild.text_channels)} text, {len(ctx.guild.voice_channels)} voice', inline=False)
        embed.add_field(name='Roles', value=str(len(ctx.guild.roles)), inline=False)
        embed.add_field(name='Region', value=str(ctx.guild.region).capitalize(), inline=False)


        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(brief='Get information about your Discord account.', description='Shows information about ', usage='[user]')
    async def uinfo(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.message.author
        embed = discord.Embed(color=user.color)
        embed.set_author(name=f'User Info')
        embed.add_field(name='Name', value=str(user), inline=False)
        embed.add_field(name='ID', value=user.id, inline=False)
        embed.add_field(name='Highest role', value=user.top_role, inline=False)
        embed.add_field(name='Joined Server', value=user.joined_at.strftime('%A %d %B %Y at %I:%M %p (UTC)'), inline=False)
        embed.add_field(name='Account Created', value=user.created_at.strftime('%A %d %B %Y at %I:%M %p (UTC)'), inline=False)
        embed.set_thumbnail(url=user.avatar_url)
        if user.nick != None:
            embed.add_field(name='Nickname: ', value=user.nick, inline=False)
        if user.activity != None:
            embed.add_field(name='Current Activity: ', value=user.activity.name, inline=False)
        await ctx.send(embed=embed)

    @commands.command(
        aliases=['ping', 'binfo', 'latency'],
        brief='Get information about the bot such as latency and uptime.'
    )
    async def botinfo(self, ctx):
        runtime = datetime.datetime.utcnow() - self.bot.run_time
        uptime = datetime.datetime.utcnow() - self.bot.connect_time
        embed = discord.Embed(colour=discord.Colour.blurple())

        embed.set_author(name=str(self.bot.user), icon_url=self.bot.user.avatar_url)

        embed.add_field(name='Uptime', value=f'''
        Since Initialization
        ``{utils.strfdelta(runtime, '%Dd %Hh %Mm %Ss')}``

        Since Connection Start
        ``{utils.strfdelta(uptime, '%Dd %Hh %Mm %Ss')}``''')

        latency_text = f'''
        Websocket
        ``{int(self.bot.latency * 1000)}ms``

        Message Receive
        ``...``
        '''

        embed.add_field(name='Latency', value=latency_text)

        start = time.perf_counter()
        msg = await ctx.send(embed=embed)
        end = time.perf_counter()
        message_receive = int((end - start) * 1000)
        embed.set_field_at(1, name='Latency', value=latency_text.replace('``...``', f'``{message_receive}ms``', 1))

        await msg.edit(embed=embed)

        if random.randint(1,2) == 1:
            async with aiohttp.ClientSession(loop=self.bot.loop) as session:
                response = await session.get(url='https://uselessfacts.jsph.pl/random.json?language=en')
                fact = await response.json()
                await session.close()
            value = fact['text']
            embed.add_field(name='Fact of the Day', value=value, inline=False)
        else:
            async with aiohttp.ClientSession(loop=self.bot.loop) as session:
                response = await session.get(url='https://sv443.net/jokeapi/category/Any?blacklistFlags=nsfw')
                data = await response.json()
                await session.close()
            if data['type'] == 'twopart':
                value = data['setup'] + '\n' + data['delivery']
            else:
                value = data['joke']
            embed.add_field(name='Joke of the Day', value=value, inline=False)
        await msg.edit(embed=embed)


    @commands.command(brief='Shows recently deleted messages')
    async def snipe(self, ctx):
        snipes = self.bot.snipe_list
        now = datetime.datetime.utcnow()
        snipes_serv = []

        for msg in snipes:
            if msg.guild == ctx.message.guild:
                snipes_serv.append(msg)

        embed = discord.Embed(title=f"Deleted messages from {ctx.message.guild.name}")
        if len(snipes_serv):
            for msg in snipes_serv:
                embed.add_field(name=f"{msg.author}", value=msg.content, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(':x:**There were no messages to snipe**')

    @commands.command(brief='Adds a role to the user, or lists all available roles', usage="[name]")
    async def role(self, ctx, name: str = None):
        rolesJSON = (await dbcontrol.get_guild(ctx.guild.id))['roles']
        rolesDict = json.loads(rolesJSON) if rolesJSON else {}
        if name is None:
            if rolesDict == {}:
                await ctx.send(":x: **No roles currently available**")
            else:
                await ctx.send(f"**Currently available roles:** ```\n" + "\n".join(rolesDict.keys()) + "```")
        else:
            if name not in rolesDict.keys():
                await ctx.send(f":x: **Role ``{name}`` not found**")
            else:
                role = ctx.guild.get_role(rolesDict[name])

                if role not in ctx.author.roles:
                    if role > ctx.guild.me.top_role:
                        await ctx.send(f":x: **I am not allowed to give you the {name} role**")
                    else:
                        await ctx.author.add_roles(role, reason="Automated role command")
                        await ctx.send(f":white_check_mark: **You have been given the role ``{role.name}``**")
                else:
                    if role > ctx.guild.me.top_role:
                        await ctx.send(f":x: **I am not allowed to remove the {name} role from you**")
                    else:
                        await ctx.author.remove_roles(role, reason="Automated role command")
                        await ctx.send(f":white_check_mark: **You have been removed from the role ``{role.name}``**")

    @commands.command(brief="Creates a new role with specified color", usage="[hex or colour name]", aliases=['color'])
    async def colour(self, ctx, *, colour):
        coloursJSON = (await dbcontrol.get_guild(ctx.guild.id))['colours']
        coloursDict = json.loads(coloursJSON)

        colour = utils.colour(colour)

        if colour:
            for key in list(coloursDict.keys()):
                role = ctx.guild.get_role(coloursDict[str(key)])
                if role is None:
                    coloursDict.pop(key)
                    coloursJSON = json.dumps(coloursDict)
                    await dbcontrol.modify_guild(ctx.guild.id, 'colours', coloursJSON)
                if role in ctx.author.roles:
                    await ctx.author.remove_roles(role, reason="Automated colour role removal")
                    await ctx.send("**Your existing colour role was removed**")

            if str(colour.value) in list(coloursDict.keys()):
                role = ctx.guild.get_role(coloursDict[str(colour.value)])
                if role > ctx.guild.me.top_role:
                    return await ctx.send(":x: **I don't have permission to give you thata role**")
                if role in ctx.author.roles:
                    return await ctx.send(":x: **You already have this role**")
                await ctx.author.add_roles(role, reason="Automated colour command")
                await ctx.send(f":white_check_mark: **You have been given the role ``{colour.value}``**")

            else:
                role = await ctx.guild.create_role(name=str(colour.value), colour=colour)
                coloursDict[colour.value] = role.id
                coloursJSON = json.dumps(coloursDict)
                await dbcontrol.modify_guild(ctx.guild.id, 'colours', coloursJSON)
                await ctx.author.add_roles(role, reason="Automated colour command")
                await ctx.send(f":white_check_mark: **You have been given the role ``{colour.value}``**")



def setup(bot):
    bot.add_cog(Utility(bot))

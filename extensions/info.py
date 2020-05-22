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
import asyncio
import datetime
import aiohttp
import random
import utils
import time
import re
import dbcontrol
import json
import bs4

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
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)


        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(brief='Get information about your Discord account.', description='Shows information about ', usage='[user]')
    async def uinfo(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.message.author
        embed = discord.Embed(color=user.color if user.color else discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f'User Info')
        embed.add_field(name='Name', value=str(user), inline=False)
        embed.add_field(name='ID', value=user.id, inline=False)
        embed.add_field(name='Highest role', value=user.top_role, inline=False)
        embed.add_field(name='Joined Server', value=user.joined_at.strftime('%A %d %B %Y at %I:%M %p (UTC)'), inline=False)
        embed.add_field(name='Account Created', value=user.created_at.strftime('%A %d %B %Y at %I:%M %p (UTC)'), inline=False)
        embed.set_footer(text=user, icon_url=user.avatar_url)
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
        embed = discord.Embed(colour=discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
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
                response = await session.get(url='https://sv443.net/jokeapi/v2/joke/Any?blacklistFlags=nsfw')
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
        snipes_serv = self.bot.snipe_info.get(ctx.guild.id)
        if snipes_serv is None:
            await ctx.send(':x: **There was nothing to snipe!**')
            return 

        now = datetime.datetime.utcnow()

        embed = discord.Embed(title=f"Deleted messages from {ctx.message.guild.name}", timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        if len(snipes_serv):
            for msg in snipes_serv:
                embed.add_field(name=f"{msg.author}", value=msg.content[-300:], inline=False)
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
                await ctx.send(f"**Currently available roles:** ```\n" + "- \n".join(rolesDict.keys()) + "```")
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
                        await ctx.send(f":thumbsup: **You have been given the role ``{role.name}``**")
                else:
                    if role > ctx.guild.me.top_role:
                        await ctx.send(f":x: **I am not allowed to remove the {name} role from you**")
                    else:
                        await ctx.author.remove_roles(role, reason="Automated role command")
                        await ctx.send(f":thumbsup: **You have been removed from the role ``{role.name}``**")

    @commands.command(brief="Creates a new role with specified color", usage="[hex or colour name]", aliases=['color'])
    async def colour(self, ctx, *, colour):
        coloursJSON = (await dbcontrol.get_guild(ctx.guild.id))['colours']
        coloursDict = json.loads(coloursJSON)

        colour = utils.colour(colour)

        if not colour:
            await ctx.send(":x: **Invalid Colour**")
        else:
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
                    return await ctx.send(":x: **I don't have permission to give you that role**")
                if role in ctx.author.roles:
                    return await ctx.send(":x: **You already have this role**")
                await ctx.author.add_roles(role, reason="Automated colour command")
                await ctx.send(f":thumbsup: **You have been given the role ``{colour.value}``**")

            else:
                role = await ctx.guild.create_role(name=str(colour.value), colour=colour)
                coloursDict[colour.value] = role.id
                coloursJSON = json.dumps(coloursDict)
                await dbcontrol.modify_guild(ctx.guild.id, 'colours', coloursJSON)
                await ctx.author.add_roles(role, reason="Automated colour command")
                await ctx.send(f":thumbsup: **You have been given the role ``{colour.value}``**")

    @commands.command(aliases=["dw", "distribution", "distro"], brief="Finds information about a linux distro", usage="<distro>")
    async def distrowatch(self, ctx, *, distro):
        url = "https://distrowatch.com/table.php?distribution="
        root = "http://distrowatch.com/"
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            if distro.lower() == "random":
                response = await session.get(url="https://distrowatch.com/random.php")
            else:
                response = await session.get(url=url+distro)
            response = await response.read()
        soup = bs4.BeautifulSoup(response, "html.parser")
        if len(soup.select(".TablesTitle")) == 0:
            return await ctx.send(":x:**Invalid distribution**")
        # Valid distro
        properties = list(filter(None, soup.find("td", {"class": "TablesTitle"}).get_text().split("\n")))
        embed = discord.Embed(title=soup.find("h1").text, description=properties[3], timestamp=datetime.datetime.utcnow(), color=discord.Color.blurple())
        if len(soup.select(".TablesTitle > img:nth-child(6)")):
            embed.set_footer(text=soup.find("h1").text, icon_url=root+soup.select(".TablesTitle > img:nth-child(6)")[0].attrs["src"])
        else:
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Os Type: ", value=properties[1].split(": ")[1].replace("Based on", ""), inline=False)
        embed.add_field(name="Based on: ", value=properties[1].split(": ")[2].replace("Origin", ""), inline=False)
        embed.add_field(name="Origin: ", value=properties[1].split(": ")[3], inline=False)
        embed.add_field(name="Architecture: ", value=properties[2].split(": ")[1].replace("Desktop", ""), inline=False)
        embed.add_field(name="Desktop Environment: ", value=properties[2].split(": ")[2].replace("Category", ""), inline=False)
        embed.add_field(name="Category: ", value=properties[2].split(": ")[3].replace("Status", ""), inline=False)
        embed.add_field(name="Status: ", value=properties[2].split(": ")[4].replace("Popularity", ""), inline=False)

        info = soup.find("table", {"class": "Info"})
        data = []
        rows = info.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            cols = [element.text.strip() for element in cols]
            data.append([element for element in cols if element])
        if data[2][0] != "--":
            embed.add_field(name="Homepage: ", value=data[2][0], inline=True)
        if data[4][0] != "--":
            embed.add_field(name="Forums: ", value=data[4][0], inline=True)
        if data[6][0] != "--":
            embed.add_field(name="Documentation: ", value=data[6][0].replace("•", " "), inline=True)
        if data[9][0] != "--":
            embed.add_field(name="Download: ", value=data[9][0].replace("•", " "), inline=True)
        if data[10][0] != "--":
            embed.add_field(name="Bug Tracker: ", value=data[10][0].replace("•", " "), inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))

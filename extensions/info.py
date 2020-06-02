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
import datetime
import aiohttp
import random
import utils
import time
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

        embed.add_field(name='Name', value=ctx.guild.name, inline=False) # Name of guild
        embed.add_field(name='Owner', value=str(ctx.guild.owner)) # User who created guild or has current ownership
        embed.add_field(name='Created At', value=ctx.guild.created_at.strftime('%A %d %B %Y at %I:%M %p'), inline=False) # Date of guild creation

        botcount = len([m for m in ctx.guild.members if m.bot]) # Amount of bot users in guild, using shorthand for loop
        humancount = ctx.guild.member_count - botcount # Gets amount of humans by subtracting the amount of bots from total amount

        embed.add_field(name='Members', value=f'{ctx.guild.member_count} total, {humancount} humans, {botcount} bots', inline=False)
        embed.add_field(name='Channels', value=f'{len(ctx.guild.text_channels)} text, {len(ctx.guild.voice_channels)} voice', inline=False)
        embed.add_field(name='Roles', value=str(len(ctx.guild.roles)), inline=False)
        embed.add_field(name='Region', value=str(ctx.guild.region).capitalize(), inline=False)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(brief='Get information about your Discord account.', description='Shows information about ', usage='[user]')
    async def uinfo(self, ctx, user: discord.Member = None):
        # If no user is supplied it gives info about the author
        if not user:
            user = ctx.message.author
        embed = discord.Embed(color=user.color if user.color else discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f'User Info')
        embed.add_field(name='Name', value=user, inline=False) # Username
        embed.add_field(name='ID', value=user.id, inline=False) # Internal identification number
        embed.add_field(name='Highest role', value=user.top_role, inline=False) # Highest role of the member in current guild
        embed.add_field(name='Joined Server', value=user.joined_at.strftime('%A %d %B %Y at %I:%M %p (UTC)'), inline=False) # Time the user joined current guild
        embed.add_field(name='Account Created', value=user.created_at.strftime('%A %d %B %Y at %I:%M %p (UTC)'), inline=False) # Time the user joined discord
        embed.set_footer(text=user, icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
        if user.nick != None:
            # If the user has a nickname in current guild it is added
            embed.add_field(name='Nickname: ', value=user.nick, inline=False)
        if user.activity != None:
            # If the user has a current status it is displayed
            embed.add_field(name='Current Activity: ', value=user.activity.name, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['ping', 'binfo', 'latency'], brief='Get information about the bot such as latency and uptime.')
    async def botinfo(self, ctx):
        # Subtracts the bots run time in seconds from the current timestamp to get time elapsed
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
        # Edits embed to add in recieve time
        embed.set_field_at(1, name='Latency', value=latency_text.replace('``...``', f'``{message_receive}ms``', 1))

        await msg.edit(embed=embed)

        # Adds in random fun fact or joke after initial information is sent
        if random.randint(1,2) == 1:
            async with aiohttp.ClientSession(loop=self.bot.loop) as session:
                # A random fact from this cool api
                response = await session.get(url='https://uselessfacts.jsph.pl/random.json?language=en')
                # Uses inbuilt aiohttp parser to parse json
                fact = await response.json()
                await response.close()
                await session.close()
            value = fact['text']
            embed.add_field(name='Fact of the Day', value=value, inline=False)
        else:
            async with aiohttp.ClientSession(loop=self.bot.loop) as session:
                # Gets a random joke from this api with the nsfw jokes blacklisted
                response = await session.get(url='https://sv443.net/jokeapi/v2/joke/Any?blacklistFlags=nsfw')
                data = await response.json()
                await session.close()
            # If the joke is a two part joke addition work is required
            # The setup and delivery are both sent on different lines
            if data['type'] == 'twopart':
                value = data['setup'] + '\n' + data['delivery']
            else:
                # One-liner
                value = data['joke']
            embed.add_field(name='Joke of the Day', value=value, inline=False)
        await msg.edit(embed=embed)


    @commands.command(brief='Shows recently deleted messages')
    async def snipe(self, ctx):
        # Grabs the list of deleted messages from the bot variable
        snipes_serv = self.bot.snipe_info.get(ctx.guild.id)

        embed = discord.Embed(title=f"Deleted messages from {ctx.message.guild.name}", timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        if len(snipes_serv):
            for msg in snipes_serv:
                embed.add_field(name=f"{msg.author}", value=msg.content[-300:], inline=False)
            await ctx.send(embed=embed)
        # No deleted messages exist
        else:
            await ctx.send(':x:**There were no messages to snipe**')

    @commands.command(brief='Adds a role to the user, or lists all available roles', usage="[name]")
    async def role(self, ctx, name: str = None):
        # Grabs the json of existing roles in the guild from the database and parses it into a dictionary
        rolesJSON = (await dbcontrol.get_guild(ctx.guild.id))['roles']
        rolesDict = json.loads(rolesJSON) if rolesJSON else {} # If the json doesn't exist in db an empty dict is created
        if name is None:
            if rolesDict == {}:
                await ctx.send(":x: **No roles currently available**")
            else:
                # Sends each dictionary key on a new line
                await ctx.send(f"**Currently available roles:** ```\n" + " \n".join(rolesDict.keys()) + "```")
        else:
            if name not in rolesDict.keys():
                await ctx.send(f":x: **Role ``{name}`` not found**")
            else:
                # Role does exist
                role = ctx.guild.get_role(rolesDict[name])

                if role not in ctx.author.roles:
                    # Role is above bots top role, can't assign to user
                    if role > ctx.guild.me.top_role:
                        await ctx.send(f":x: **I am not allowed to give you the {name} role**")
                    else:
                        await ctx.author.add_roles(role, reason="Automated role command")
                        await ctx.send(f":thumbsup: **You have been given the role ``{role.name}``**")
                # If user already has role it is removed from them
                else:
                    if role > ctx.guild.me.top_role:
                        await ctx.send(f":x: **I am not allowed to remove the {name} role from you**")
                    else:
                        await ctx.author.remove_roles(role, reason="Automated role command")
                        await ctx.send(f":thumbsup: **You have been removed from the role ``{role.name}``**")

    @commands.command(brief="Creates a new role with specified color", usage="[hex or colour name]", aliases=['color'])
    async def colour(self, ctx, *, colour):
        # Grabbing existing colors and parsing into a dictionary
        coloursJSON = (await dbcontrol.get_guild(ctx.guild.id))['colours']
        coloursDict = json.loads(coloursJSON)

        # Getting the hex code for the color using the utils function
        colour = utils.colour(colour)

        if not colour:
            # utils.colour returns False if the colour is invalid
            await ctx.send(":x: **Invalid Colour**")
        else:
            # Checking through each existing colour role to delete it from db if it doesn't exist or remove it from the
            # user if they have it
            for key in list(coloursDict.keys()):
                role = ctx.guild.get_role(coloursDict[str(key)])
                # If the role doesn't exist for some reason its removed from the db
                if role is None:
                    coloursDict.pop(key)
                    coloursJSON = json.dumps(coloursDict)
                    await dbcontrol.modify_guild(ctx.guild.id, 'colours', coloursJSON)
                # If the user already has a colour role it is removed
                if role in ctx.author.roles:
                    await ctx.author.remove_roles(role, reason="Automated colour role removal")
                    await ctx.send("**Your existing colour role was removed**")

            # If a role already exists for chosen colour we don't want to make a new one so the existing role is given
            if str(colour.value) in list(coloursDict.keys()):
                role = ctx.guild.get_role(coloursDict[str(colour.value)])
                # If the target colour role is higher than the bots top role then it can't assign it
                if role > ctx.guild.me.top_role:
                    return await ctx.send(":x: **I don't have permission to give you that role**")
                if role in ctx.author.roles:
                    return await ctx.send(":x: **You already have this role**")
                await ctx.author.add_roles(role, reason="Automated colour command")
                await ctx.send(f":thumbsup: **You have been given the role ``{colour.value}``**")

            # If role doesn't exist then the new role is created, added to db, and given to the user
            else:
                role = await ctx.guild.create_role(name=str(colour.value), colour=colour)
                coloursDict[colour.value] = role.id
                coloursJSON = json.dumps(coloursDict)
                await dbcontrol.modify_guild(ctx.guild.id, 'colours', coloursJSON)
                await ctx.author.add_roles(role, reason="Automated colour command")
                await ctx.send(f":thumbsup: **You have been given the role ``{colour.value}``**")

    # This command sucks ass but it works
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
            await session.close()
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
        # Some dumbshit grabbing different attributes of the distro
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
        if len(data) >= 9 and data[9][0] != "--":
            embed.add_field(name="Download: ", value=data[9][0].replace("•", " "), inline=True)
        if len(data) >= 10 and data[10][0] != "--":
            embed.add_field(name="Bug Tracker: ", value=data[10][0].replace("•", " "), inline=True)
        await ctx.send(embed=embed)

    @commands.command(brief="Gets a random xkcd comic, or the specified number", usage="<comic number or random>")
    async def xkcd(self, ctx, num="random"):
        root = "https://xkcd.com/"
        async with ctx.typing():
            if num.lower() in ["random", "r", "rand"]:
                num = random.randint(1, 2314)
            elif not num.isnumeric():
                return await ctx.send(":x: **Don't try to break me**")
            url = root+str(num)
            async with aiohttp.ClientSession(loop=self.bot.loop) as session:
                response = await session.get(url)
                html = await response.read()
                await session.close()
            if response.status != 200:
                return await ctx.send(":x: **Invalid comic number**")
            # Instantiating beautifulsoup object to parse th html
            soup = bs4.BeautifulSoup(html, "html.parser")
            # Selecting the comic title with css selector
            title = soup.select("#ctitle")[0].text
            # The second image on the page is the comic image
            img = "https:" + soup.find_all("img")[1].attrs["src"]
            embed = discord.Embed(title=f"#{num}: {title}", timestamp=datetime.datetime.utcnow(), description=f"[Site Link]({url})\n[Image URL]({img})", color=discord.Color.blurple())
            embed.set_image(url=img)
            embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)




def setup(bot):
    bot.add_cog(Utility(bot))

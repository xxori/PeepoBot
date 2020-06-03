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
import json
import asyncio
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Moderation-related commands. Admin-only.'

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(brief='Permanently ban a user from the server', usage='[user] <reason>')
    async def ban(self, ctx, target: discord.Member, *, reason=None):
        if ctx.guild.owner_id == target.id:
            await ctx.send(f':x: **You cannot ban ``{target}`` because they are the server owner.**')
            return

        elif (target.top_role >= ctx.message.author.top_role) and ctx.guild.owner_id != ctx.message.author.id:
            await ctx.send(f':x: **You are not authorised to ban ``{target}``.**')
            return

        try:
            await target.ban(reason=f'{ctx.author}: {reason or "unspecified reason"}')
        except discord.Forbidden:
            raise utils.HierarchyPermissionError(ctx, target)
        else:
            await ctx.send(f':thumbsup: **Banned ``{target}``{f" for ``{reason}``" if reason is not None else ""}**')

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.command(brief='Kicks a user from the server', usage='[user] <reason>', aliases=['cya'])
    async def kick(self, ctx, target: discord.Member, *, reason=None):
        if ctx.guild.owner_id == target.id:
            await ctx.send(f':x: **You cannot kick ``{target}`` because they are the server owner.**')
            return

        elif (target.top_role >= ctx.message.author.top_role) and ctx.guild.owner_id != ctx.message.author.id:
            await ctx.send(f':x: **You are not authorised to kick ``{target}``.**')
            return

        try:
            await target.kick(reason=f'{ctx.author}: {reason or "unspecified reason"}')
        except discord.Forbidden:
            raise utils.HierarchyPermissionError(ctx, target)
        else:
            await ctx.send(f':thumbsup: **Kicked ``{target}``{f" for ``{reason}``" if reason is not None else ""}**')

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command(brief='Deletes messages from the channel in bulk.', usage='[amount]', aliases=['clear'])
    async def purge(self, ctx, amount=50):
        purged = len(await ctx.channel.purge(limit=amount))
        await ctx.send(f':thumbsup: **Purged {purged} messages from <#{ctx.channel.id}>**', delete_after=2)

    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_messages=True)
    @commands.command(brief='Permanently mutes a server member', usage='[user] <reason>')
    async def mute(self, ctx, target: discord.Member, *, reason=None):
        muteRole = await dbcontrol.get_setting(ctx.guild.id, 'muterole')
        if muteRole is None:
            await ctx.send(f':x: **A muterole is required for this command to run. Please assign a muterole with {ctx.prefix}muterole**')
            return

        muted = ctx.guild.get_role(muteRole)
        if muted is None:
            await ctx.send(f":x: **The muterole does not exist anymore. Assign a new one with {ctx.prefix}muterole.**")
            return

        if muted > ctx.guild.me.top_role:
            await ctx.send(':x: **I am not allowed to assign the ``Muted`` role. Please lower it below mine.**')
            return

        elif ctx.guild.owner_id == target.id:
            await ctx.send(f':x: **You cannot mute ``{target}`` because they are the server owner.**')
            return

        elif (target.top_role >= ctx.message.author.top_role) and ctx.guild.owner_id != ctx.message.author.id:
            await ctx.send(f':x: **You are not authorised to mute ``{target}``.**')
            return

        elif target.top_role > muted:
            await ctx.send(f':x: **``{target}`` has the role ``{target.top_role.name}`` which overrides permissions of the muterole**')

        else:
            await target.add_roles(muted, reason=f'{ctx.author}: {reason or "unspecified reason"}')
            await ctx.send(f':thumbsup: **Muted ``{target}``{f" for ``{reason}``" if reason is not None else ""}**')

    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.command(brief='Unmutes a server member', usage='[user]', aliases=['umute'])
    async def unmute(self, ctx, target: discord.Member):
        muteID = await dbcontrol.get_setting(ctx.guild.id, 'muterole')
        mutesJSON = (await dbcontrol.get_guild(ctx.guild.id))['tempmutes']
        mutesDict = json.loads(mutesJSON)

        if str(target.id) in list(mutesDict.keys()):
            # If user is in mute db they are removed, if not nothing happens to db
            mutesDict.pop(str(target.id))
            mutesJSON = json.dumps(mutesDict)
            await dbcontrol.modify_guild(ctx.guild.id, 'tempmutes', mutesJSON)

        if muteID is None:
            # No muterole exists in db
            await ctx.send(f":x: **There is no muterole. Assign one with {ctx.prefix}muterole**")
        # Converts id from db to a role object
        muted = ctx.guild.get_role(muteID)
        if muted is None:
            # If muted is None then the id stored in db points to a role that doesn't exist
            return await ctx.send(f":x: **The muterole does not exist anymore. Assign a new one with {ctx.prefix}muterole.**")
        if muted in target.roles:
            await target.remove_roles(muted)
            await ctx.send(f':thumbsup: **Unmuted ``{target}``**')
        else:
            await ctx.send(f':x: **``{target}`` is not muted.**')

    @commands.has_permissions(manage_channels=True)
    @commands.command(brief='Execute command as another user.', usage='[user] <command>', aliases=['runas', 'please'])
    async def sudo(self, ctx, user: discord.Member, *, cmd):
        # Command name taken from the unix command sudo

        if not self.bot.check_dev(ctx.message.author.id):
            # Can't sudo other developers
            if self.bot.check_dev(user.id):
                return await ctx.send(f':x: **You cannot execute commands as ``{user}`` because they are a bot developer.**')

            # Can't sudo server owner
            elif ctx.guild.owner_id == user.id:
                return await ctx.send(f':x: **You cannot execute commands as ``{user}`` because they are the server owner.**')

            # Can't sudo people who have higher roles than user (unless the user isn't owner)
            elif (user.top_role > ctx.message.author.top_role) and ctx.guild.owner_id != ctx.message.author.id:
                return await ctx.send(f':x: **You are not authorised to execute commands as ``{user}``.**')

        await ctx.send(f'**Sudoing ``{cmd}`` as ``{user}``.**')

        # Creates new context object using modified parameters
        sudo_msg = ctx.message
        sudo_msg.author = user
        sudo_msg.content = ctx.prefix + cmd.replace(ctx.prefix, '', 1)
        sudo_ctx = await self.bot.get_context(sudo_msg)
        # Invokes new context
        await self.bot.invoke(sudo_ctx)

    @commands.has_permissions(manage_roles=True)
    @commands.command(brief='Adds a role for people to add to themselves with the role command', usage="[name] <role>")
    async def addrole(self, ctx, name, role : discord.Role):
        # Grabs the role json from db and parses it
        rolesJSON = (await dbcontrol.get_guild(ctx.guild.id))['roles']
        rolesDict = json.loads(rolesJSON) if rolesJSON != "" else {}
        # Converts to lower case for consistency
        name = name.lower()
        # Writes to db
        rolesDict[name] = role.id
        rolesJSON = json.dumps(rolesDict)
        await dbcontrol.modify_guild(ctx.guild.id, 'roles', rolesJSON)
        await ctx.send(f":thumbsup: **Role {name} successfully added**")

    @commands.has_permissions(manage_roles=True)
    @commands.command(brief='Deletes a role for people to add to themselves with the role command', usage="[name]")
    async def delrole(self, ctx, name):
        rolesJSON = (await dbcontrol.get_guild(ctx.guild.id))['roles']
        rolesDict = json.loads(rolesJSON) if rolesJSON != "" else {}
        # Converts name to lowercase
        name = name.lower()
        if name not in rolesDict.keys():
            # Specified role not in db
            await ctx.send(f":x: **Role ``{name}`` not found. Check your spelling and try again.**")
        else:
            # Removes role from db and writes changes
            rolesDict.pop(name)
            rolesJSON = json.dumps(rolesDict)
            await dbcontrol.modify_guild(ctx.guild.id, 'roles', rolesJSON)
            await ctx.send(f":thumbsup: **Role ``{name}`` successfully deleted**")

    @commands.has_permissions(manage_roles=True)
    @commands.command(brief='Temporarily mutes a user', usage='[user] <minutes>', aliases=["tmute"])
    async def tempmute(self, ctx, user: discord.Member, time: int, unit = "s", reason=None):
        # Grabs the id of the current guild muterole and converts it to a role object
        muteroleid = await dbcontrol.get_setting(ctx.guild.id, 'muterole')
        muterole = ctx.guild.get_role(muteroleid)
        # Role doesn't exist or there is no muterole
        if muterole is None:
            await ctx.send(f":x: **The current muterole is invalid**")

        # Muterole is above bots permission
        if muterole > ctx.guild.me.top_role:
            await ctx.send(f":x: **The current muterole is higher than my highest role**")

        # We don't want admins to be able to mute the owner
        elif ctx.guild.owner_id == user.id:
            await ctx.send(f':x: **You cannot mute ``{user}`` because they are the server owner.**')


        # We don't want people to be able to mute people with more permissions than them
        elif (user.top_role >= ctx.author.top_role) and ctx.guild.owner_id != ctx.author.id:
            await ctx.send(f':x: **You are not authorised to mute ``{user}``.**')


        # If the users top role is higher than the muterole then it will override it
        elif user.top_role > muterole:
            await ctx.send(f':x: **``{user}`` has the role ``{user.top_role.name}`` which overrides permissions of the muterole**')

        # No muting the bot
        elif user == ctx.guild.me:
            await ctx.send("Frick off, hecker")

        # If it passed all check it mutes them
        else:
            await user.add_roles(muterole, reason=f"{ctx.author}:" + f":{time}{unit}")
            await ctx.send(f":thumbsup:** User {user} temporarily muted for {time}{unit}**")
            mutesJSON = (await dbcontrol.get_guild(ctx.guild.id))['tempmutes']
            mutesDict = json.loads(mutesJSON) or {} # Empty dict if it doesn't exist
            # Converting units into seconds
            if unit.lower() in ["m", "minutes", "minute"]:
                time *= 60
            if unit.lower() in ["h", "hours", "hour"]:
                time *= 3600
            # Adds the user and current timestamp plus the amount of time the user is muted for
            mutesDict[user.id] = int(datetime.datetime.utcnow().timestamp()) + time
            mutesJSON = json.dumps(mutesDict)
            # Writes to db
            await dbcontrol.modify_guild(ctx.guild.id, 'tempmutes', mutesJSON)

            # Waits specified time before unmuting them
            await asyncio.sleep(time)
            mutesJSON = (await dbcontrol.get_guild(ctx.guild.id))['tempmutes']
            mutesDict = json.loads(mutesJSON)
            # Removes from db
            if user.id in mutesDict.keys():
                mutesDict.pop(user.id)
            if muterole in user.roles:
                await user.remove_roles(muterole, reason="Tempmute expired")
            mutesJSON = json.dumps(mutesDict)
            await dbcontrol.modify_guild(ctx.guild.id, "tempmutes", mutesJSON)

    @commands.command(brief="Checks all tempmuted users", usage="[user]", aliases=["listmutes", "listmute"])
    async def checkmute(self, ctx, user: discord.Member = None):
        # Grabs the json of muted users in current guild and parses it to dict
        mutesJSON = (await dbcontrol.get_guild(ctx.guild.id))["tempmutes"]
        mutesDict = json.loads(mutesJSON)
        # Checks for both an empty string or an empty dict to make sure
        if mutesDict in [{}, ""]:
            return await ctx.send("**There are currently no members temp muted**")
        embed = discord.Embed(title=f"Tempmutes in {ctx.guild.name}", color=discord.Color.blurple(), timestamp=datetime.datetime.utcnow())
        for mute in list(mutesDict.keys()):
            # Adds a field for each tempmuted user
            user = ctx.guild.get_member(int(mute))
            diff = mutesDict[mute] - int(datetime.datetime.utcnow().timestamp())
            embed.add_field(value=user, name=f"Time remaining: {datetime.timedelta(seconds=diff)}", inline=False)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Moderation(bot))

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
    @commands.command(brief='Mutes a server member', usage='[user] <reason>')
    async def mute(self, ctx, target: discord.Member, *, reason=None):
        muteRole = await dbcontrol.get_setting(ctx.guild.id, 'muterole')
        if muteRole is None:
            await ctx.send(f':x: **A muterole is required for this command to run. Please assign a muterole with {self.bot.prefix}muterole**')
            return

        muted = ctx.guild.get_role(muteRole)
        if muted is None:
            await ctx.send(f":x: **The muterole does not exist anymore. Assign a new one with {self.bot.preifx}muterole.**")
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
            mutesDict.pop(str(target.id))
            mutesJSON = json.dumps(mutesDict)
            await dbcontrol.modify_guild(ctx.guild.id, 'tempmutes', mutesJSON)

        if muteID is None:
            await ctx.send(f":x: **There is no muterole. Assign one with {self.bot.prefix}muterole**")
        muted = ctx.guild.get_role(muteID)
        if muted is None:
            await ctx.send(f":x: **The muterole does not exist anymore. Assign a new one with {self.bot.preifx}muterole.**")
            return
        if muted in target.roles:
            await target.remove_roles(muted)
            await ctx.send(f':thumbsup: **Unmuted ``{target}``**')
        else:
            await ctx.send(f':x: **``{target}`` is not muted.**')

    @commands.has_permissions(manage_channels=True)
    @commands.command(brief='Execute command as another user.', usage='[user] <command>', aliases=['runas', 'please'])
    async def sudo(self, ctx, user: discord.Member, *, cmd):
        if not utils.check_dev(ctx.message.author.id):
            if utils.check_dev(user.id):
                await ctx.send(f':x: **You cannot execute commands as ``{user}`` because they are a bot developer.**')
                return

            elif ctx.guild.owner_id == user.id:
                await ctx.send(f':x: **You cannot execute commands as ``{user}`` because they are the server owner.**')
                return

            elif (user.top_role > ctx.message.author.top_role) and ctx.guild.owner_id != ctx.message.author.id:
                await ctx.send(f':x: **You are not authorised to execute commands as ``{user}``.**')
                return

        await ctx.send(f'**Sudoing ``{cmd}`` as ``{user}``.**')

        sudo_msg = ctx.message
        sudo_msg.author = user
        sudo_msg.content = ctx.prefix + cmd.replace(ctx.prefix, '', 1)
        sudo_ctx = await self.bot.get_context(sudo_msg)
        await self.bot.invoke(sudo_ctx)

    @commands.has_permissions(manage_roles=True)
    @commands.command(brief='Adds a role for people to add to themselves with the role command', usage="[name] <role>")
    async def addrole(self, ctx, name, role : discord.Role):
        rolesJSON = (await dbcontrol.get_guild(ctx.guild.id))['roles']
        rolesDict = json.loads(rolesJSON) if rolesJSON != "" else {}
        name = name.lower()
        rolesDict[name] = role.id
        rolesJSON = json.dumps(rolesDict)
        await dbcontrol.modify_guild(ctx.guild.id, 'roles', rolesJSON)
        await ctx.send(f":white_check_mark: **Role {name} successfully added**")

    @commands.has_permissions(manage_roles=True)
    @commands.command(brief='Deletes a role for people to add to themselves with the role command', usage="[name]")
    async def delrole(self, ctx, name):
        rolesJSON = (await dbcontrol.get_guild(ctx.guild.id))['roles']
        rolesDict = json.loads(rolesJSON) if rolesJSON != "" else {}
        name = name.lower()
        if name not in rolesDict.keys():
            await ctx.send(f":x: **Role ``{name}`` not found. Check your spelling and try again.**")
        else:
            rolesDict.pop(name)
            rolesJSON = json.dumps(rolesDict)
            await dbcontrol.modify_guild(ctx.guild.id, 'roles', rolesJSON)
            await ctx.send(f":white_check_mark: **Role ``{name}`` successfully deleted**")

    @commands.has_permissions(manage_roles=True)
    @commands.command(brief='Temporarily mutes a user', usage='[user] <minutes>', aliases=["tmute"])
    async def tempmute(self, ctx, user: discord.Member, time: int, unit = "s", reason=None):
        muteroleid = await dbcontrol.get_setting(ctx.guild.id, 'muterole')
        muterole = ctx.guild.get_role(muteroleid)
        if muterole is None:
            await ctx.send(f":x: **The current muterole is invalid**")

        if muterole > ctx.guild.me.top_role:
            await ctx.send(f":x: **The current muterole is higher than my highest role**")

        elif ctx.guild.owner_id == user.id:
            await ctx.send(f':x: **You cannot mute ``{user}`` because they are the server owner.**')


        elif (user.top_role >= ctx.author.top_role) and ctx.guild.owner_id != ctx.author.id:
            await ctx.send(f':x: **You are not authorised to mute ``{user}``.**')


        elif user.top_role > muterole:
            await ctx.send(f':x: **``{user}`` has the role ``{user.top_role.name}`` which overrides permissions of the muterole**')

        elif user == ctx.guild.me:
            await ctx.send("Frick off, hecker")

        else:
            await user.add_roles(muterole, reason=f"{ctx.author}:" + f":{time}{unit}")
            await ctx.send(f":white_check_mark:** User {user} temporarily muted for {time}{unit}**")
            mutesJSON = (await dbcontrol.get_guild(ctx.guild.id))['tempmutes']
            mutesDict = json.loads(mutesJSON) or {}
            if unit.lower() in ["m", "minutes", "minute"]:
                time *= 60
            if unit.lower() in ["h", "hours", "hour"]:
                time *= 3600
            mutesDict[user.id] = int(datetime.datetime.utcnow().timestamp()) + time
            mutesJSON = json.dumps(mutesDict)
            await dbcontrol.modify_guild(ctx.guild.id, 'tempmutes', mutesJSON)

            await asyncio.sleep(time)
            mutesJSON = (await dbcontrol.get_guild(ctx.guild.id))['tempmutes']
            mutesDict = json.loads(mutesJSON)
            if user.id in mutesDict.keys():
                mutesDict.pop(user.id)
            if muterole in user.roles:
                await user.remove_roles(muterole, reason="Tempmute expired")

    @commands.command(brief="Checks all tempmuted users", usage="[user]", aliases=["listmutes", "listmute"])
    async def checkmute(self, ctx, user: discord.Member = None):
        mutesJSON = (await dbcontrol.get_guild(ctx.guild.id))["tempmutes"]
        mutesDict = json.loads(mutesJSON)
        if mutesDict in [{}, ""]:
            return await ctx.send("**There are currently no members temp muted**")
        embed = discord.Embed(title=f"Tempmutes in {ctx.guild.name}", color=discord.Color.blurple(), timestamp=datetime.datetime.utcnow())
        for mute in list(mutesDict.keys()):
            user = ctx.guild.get_member(int(mute))
            diff = mutesDict[mute] - int(datetime.datetime.utcnow().timestamp())
            embed.add_field(value=user, name=f"Time remaining: {datetime.timedelta(seconds=diff)}", inline=False)
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Moderation(bot))

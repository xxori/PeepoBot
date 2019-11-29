import discord
from discord.ext import commands
import utils

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Moderation-related commands. Admin-only.'

    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.command(brief='Permanently ban a user from the server', usage='<user> [reason]')
    async def ban(self, ctx, target: discord.Member, *, reason=None):
        if ctx.guild.owner_id == target.id:
            await ctx.send(f':x: **You cannot kick ``{target}`` because they are the server owner.**')
            return

        elif (target.top_role >= ctx.message.author.top_role) and ctx.guild.owner_id != ctx.message.author.id:
            await ctx.send(f':x: **You are not authorised to ban ``{target}``.**')
            return

        try:
            await target.ban(reason=f'{ctx.author}: {reason or "unspecified reason"}')
        except discord.Forbidden:
            raise utils.HierarchyPermissionError(ctx, target)
        else:
            await ctx.send(f':thumbsup: **Banned ``{target}``{f" for {reason}" if reason is not None else ""}**')

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.command(brief='Kicks a user from the server', usage='<user> [reason]')
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
            await ctx.send(f':thumbsup: **Kicked ``{target}``{f" for {reason}" if reason is not None else ""}**')

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command(brief='Deletes messages from the channel in bulk.', usage='[amount]')
    async def purge(self, ctx, amount=50):
        purged = len(await ctx.channel.purge(limit=amount))
        await ctx.send(f':thumbsup: **Purged {purged} messages from <#{ctx.channel.id}>**', delete_after=2)

    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_messages=True)
    @commands.command(brief='Mutes a server member', usage='[user] <reason>')
    async def mute(self, ctx, target: discord.Member, *, reason=None):
        muted = discord.utils.get(ctx.guild.roles, name='Muted')
        if muted is None:
            await ctx.send(':x: **A role called ``Muted`` is required for this command to run. Please create it before proceeding.**')
            return

        elif muted > ctx.guild.me.top_role:
            await ctx.send(':x: **I am not allowed to assign the ``Muted`` role. Please lower it below mine.**')
            return

        elif ctx.guild.owner_id == target.id:
            await ctx.send(f':x: **You cannot mute ``{target}`` because they are the server owner.**')
            return

        elif (target.top_role >= ctx.message.author.top_role) and ctx.guild.owner_id != ctx.message.author.id:
            await ctx.send(f':x: **You are not authorised to mute ``{target}``.**')
            return

        elif target.top_role > muted:
            await ctx.send(f':x: **``{target}`` has the role ``{target.top_role.name}`` which overrides permissions of the ``Muted`` role.**')

        else:
            await target.add_roles(muted, reason=f'{ctx.author}: {reason or "unspecified reason"}')
            await ctx.send(f':thumbsup: **Muted ``{target}``{f" because {reason}" if reason is not None else ""}**')

    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.command(brief='Unmutes a server member', usage='[user]')
    async def unmute(self, ctx, target: discord.Member):
        muted = discord.utils.get(ctx.guild.roles, name='Muted')
        if muted is None:
            await ctx.send(':x: **A role called ``Muted`` is required for this command to run. Please create it before proceeding.**')
            return

        if muted in target.roles:
            await target.remove_roles(muted)
            await ctx.send(f':thumbsup: **Unmuted ``{target}``**')
        else:
            await ctx.send(f':x: **``{target}`` is not muted.**')

    @commands.has_permissions(manage_channels=True)
    @commands.command(brief='Execute command as another user.', usage='<user> <command>')
    async def sudo(self, ctx, user: discord.Member, *, cmd):
        if utils.check_dev(user.id):
            await ctx.send(f':x: **You cannot execute commands as ``{user}`` because they are a bot developer.**')
            return

        elif ctx.guild.owner_id == user.id:
            await ctx.send(f':x: **You cannot execute commands as ``{user}`` because they are the server owner.**')
            return

        elif (user.top_role > ctx.message.author.top_role) and ctx.guild.owner_id != ctx.message.author.id:
            await ctx.send(f':x: **You are not authorised to execute commands as ``{user}``.**')
            return

        else:
            await ctx.send(f'**Sudoing ``{cmd}`` as ``{user}``.**')

        sudo_msg = ctx.message
        sudo_msg.author = user
        sudo_msg.content = ctx.prefix + cmd.replace(ctx.prefix, '', 1)
        sudo_ctx = await self.bot.get_context(sudo_msg)
        await self.bot.invoke(sudo_ctx)

def setup(bot):
    bot.add_cog(Moderation(bot))

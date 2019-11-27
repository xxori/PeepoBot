import discord
from discord.ext import commands


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
        try:
            await target.ban(reason=f'{ctx.author}: {reason or "unspecified reason"}')
        except discord.Forbidden:
            await ctx.send(f':x: **I am not authorized to ban ``{target}``.**')
        else:
            await ctx.send(f':thumbsup: **Banned ``{target}``{f" for {reason}" if reason is not None else ""}**')

    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.command(brief='Kicks a user from the server', usage='<user> [reason]')
    async def kick(self, ctx, target: discord.Member, *, reason=None):
        try:
            await target.kick(reason=f'{ctx.author}: {reason or "unspecified reason"}')
        except discord.Forbidden:
            await ctx.send(f':x: **I am not authorized to kick ``{target}``.**')
        else:
            await ctx.send(f':thumbsup: **Kicked ``{target}``{f" for {reason}" if reason is not None else ""}**')

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command(brief='Deletes messages from the channel in bulk.', usage='[amount]')
    async def purge(self, ctx, amount=50):
        purged = len(await ctx.channel.purge(limit=amount))
        await ctx.send(f':thumbsup: **Purged {purged} messages from <#{ctx.channel.id}>**', delete_after=2)

def setup(bot):
    bot.add_cog(Moderation(bot))

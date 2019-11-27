import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Commmands for admins to use to moderate server'

    @commands.command(brief='Permanently bans a user')
    async def ban(self, ctx, target: discord.Member, *, reason=None):
        try:
            if dict(iter(ctx.message.author.permissions_in(ctx.message.channel)))['ban_members']:
                await discord.Guild.ban(ctx.guild, target, reason=f'With reason {reason}')
                embed = discord.Embed(color=0xFF0000, description=reason if reason else None)
                embed.set_author(name=f'User {target.display_name} successfully banned')
                embed.set_thumbnail(url=target.avatar_url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Sorry, {ctx.message.author.mention}, you don't have permissions to ban someone")

        # This is shit, there is probably a better way or using an actual error handler
        except discord.errors.Forbidden:
            await ctx.send(f"{ctx.message.author.mention}, you can't ban an administrator")

    @commands.command(brief='Kicks a user from the server')
    async def kick(self, ctx, target: discord.Member, *, reason=None):
        try:
            if dict(iter(ctx.message.author.permissions_in(ctx.message.channel)))['kick_members']:
                await discord.Guild.kick(ctx.guild, target, reason=f'With reason {reason}')
                embed = discord.Embed(color=0xFF0000, description=reason if reason else None)
                embed.set_author(name=f'User {target.display_name} successfully kicked')
                embed.set_thumbnail(url=target.avatar_url)
                await ctx.send(embed=embed)

            else:
                await ctx.send(f"{ctx.message.author.mention}")

        # Trash
        except discord.errors.Forbidden:
            await ctx.send(f"{ctx.message.author.mention}, you can't kick an administrator")

def setup(bot):
    bot.add_cog(Moderation(bot))

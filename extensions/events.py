import discord
from discord.ext import commands
import asyncio
import traceback
import utils
import dbcontrol

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, e):
        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(e, commands.CommandInvokeError):
            e = e.original

        if isinstance(e, commands.MissingRequiredArgument):
            await ctx.send(f':x: **``{ctx.command.name}`` requires the ``{e.param}`` argument!**')

        elif isinstance(e, commands.MissingPermissions):
            perm_name = e.args[0].replace('You are missing ', '').replace(' permission(s) to run this command.', '').strip()
            await ctx.send(f':closed_lock_with_key: **You need ``{perm_name}`` to be able to execute ``{ctx.command.name}``**')

        elif isinstance(e, commands.BotMissingPermissions):
            perm_name = e.args[0].replace('Bot requires ', '').replace(' permission(s) to run this command.', '').strip()
            await ctx.send(f":closed_lock_with_key: **I need ``{perm_name}`` to be able to execute ``{ctx.command.name}``**")

        elif isinstance(e, commands.NotOwner):
            await ctx.send(f':closed_lock_with_key: **``{ctx.command.name}`` can be executed only by bot developers.**')

        elif isinstance(e, commands.BadArgument):
            await ctx.send(f':x: **{e.args[0]}**')

        elif isinstance(e, utils.HierarchyPermissionError):
            command = e.args[1][0].command
            target = e.args[1][1]
            await ctx.send(f':x: **I am not authorized to {command.name} ``{target}``.**')

        elif isinstance(e, commands.CheckFailure) :
            # checks should handle their own error messages
            pass

        elif isinstance(e, commands.ExtensionNotFound):
            await ctx.send(f':x: ``{e.args[0]}`` does not exist.')

        elif isinstance(e, discord.Forbidden):
            await ctx.send(f':x: **I am not authorized to do that.**')

        elif isinstance(e, commands.CommandNotFound):
            await ctx.message.add_reaction("🤔")
            await asyncio.sleep(2)
            await ctx.message.remove_reaction("🤔", self.bot.user)

        elif isinstance(e, discord.HTTPException):
            traceback.print_exception(type(e), e, e.__traceback__)

        elif isinstance(e, commands.ExtensionAlreadyLoaded):
            await ctx.send(f':x:** {e.args[0]}**')

        elif isinstance(e, commands.ExtensionNotLoaded):
            await ctx.send(f':x: **{e.args[0]}**')


        else:
            await ctx.send(f':x: **An internal error has occurred.** ```py\n{type(e)}: {e}```')
            traceback.print_exception(type(e), e, e.__traceback__)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        serv = member.guild
        defaultrole = await dbcontrol.get_setting(serv.id, 'defaultrole')
        announcechan = await dbcontrol.get_setting(serv.id, 'announcechannel')
        if defaultrole:
            role = serv.get_role(defaultrole)
            await member.add_roles(role, reason="Default role assignment for new member")
        if announcechan:
            channel = serv.get_channel(announcechan)
            embed = discord.Embed(title=f"Welcome, {member.name}", description=f"Welcome to {serv.name}!", color=discord.Color.blurple())
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=str(member), icon_url=member.avatar_url)
            await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(
        ErrorHandler(bot)
    )

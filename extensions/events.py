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
import traceback
import utils
import dbcontrol

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, e):
        # error parsing & preparations
        if hasattr(ctx.command, "on_error"):
            return

        if isinstance(e, commands.CommandInvokeError):
            e = e.original

        # missing/malformed things
        if isinstance(e, commands.MissingRequiredArgument):
            clean_param = e.param[0].split(':')[0]
            await ctx.send(f':x: **``{ctx.command.name}`` requires the ``{clean_param}`` argument!**')
            await ctx.send_help(ctx.command.name)

        elif isinstance(e, commands.BadArgument):
            await ctx.send(f':x: **{e.args[0]}**')

        elif isinstance(e, commands.CommandNotFound):
            pass # annoying reactions when randomly typing prefix, removed old code

        # permission errors
        elif isinstance(e, commands.MissingPermissions):
            perm_name = e.args[0].replace('You are missing ', '').replace(' permission(s) to run this command.', '').strip()
            await ctx.send(f':closed_lock_with_key: **You need ``{perm_name}`` to be able to execute ``{ctx.command.name}``**')

        elif isinstance(e, utils.HierarchyPermissionError):
            command = e.args[1][0].command
            target = e.args[1][1]
            await ctx.send(f':x: **I am not authorized to {command.name} ``{target}``.**')

        elif isinstance(e, commands.BotMissingPermissions):
            perm_name = e.args[0].replace('Bot requires ', '').replace(' permission(s) to run this command.', '').strip()
            await ctx.send(f":closed_lock_with_key: **I need ``{perm_name}`` to be able to execute ``{ctx.command.name}``**")

        elif isinstance(e, discord.Forbidden):
            await ctx.send(f':closed_lock_with_key: **I am not authorized to do that.**')

        elif isinstance(e, commands.NotOwner):
            await ctx.send(f':closed_lock_with_key: **``{ctx.command.name}`` can be executed only by bot developers.**')

        elif isinstance(e, commands.ExtensionAlreadyLoaded):
            await ctx.send(f':x:** {e.args[0]}**')

        elif isinstance(e, commands.ExtensionNotLoaded):
            await ctx.send(f':x: **{e.args[0]}**')

        elif isinstance(e, commands.ExtensionNotFound):
            await ctx.send(f':x: ``{e.args[0]}`` does not exist.')

        # uh oh something broke
        elif isinstance(e, discord.HTTPException):
            traceback.print_exception(type(e), e, e.__traceback__)

        elif isinstance(e, commands.CheckFailure) :
            # checks should never just return, but instead raise an error to be caught here
            # if a check is still raising this then it's written badly
            # what are you still waiting for, a kiss?
            # go fix it

            # here, let me help you out
            traceback.print_exception(type(e), e, e.__traceback__)
            # there, stop slacking off now
            return

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
        EventHandler(bot)
    )

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
import dbcontrol
import json

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return "Server settings command for administrators only"

    @commands.group(invoke_without_command=True, brief=f"Server settings category of commands", usage="[subcommand] <argument>")
    async def settings(self, ctx):
        g = await dbcontrol.get_guild(ctx.guild.id)
        settings = g['settings']

    @commands.has_permissions(manage_messages=True)
    @settings.command(brief="Changes/gets the guild prefix", usage="[new prefix]")
    async def prefix(self, ctx, prefix = None):
        p = await self.bot.get_prefix(ctx.message)
        if prefix is None:
            embed = discord.Embed(
                title=f'Prefix for {ctx.guild.name}',
                description=f'The prefix here is `{p}`'
            )
            await ctx.send(ctx.author.mention, embed=embed)
            return
        else:
            prefix = prefix.strip()
            if p == prefix:
                await ctx.send(':x: **Have some originality, the new prefix can''t be the same as before.**')
                return

            await dbcontrol.modify_setting(ctx.guild.id, 'prefix', prefix)
            await ctx.send(f':thumbsup: **Set the prefix to `{prefix}`, I will no longer respond to `{p}`.**')


    @commands.has_permissions(manage_roles=True)
    @settings.command(brief="Sets the default role for new users", usage='[role]')
    async def defaultrole(self, ctx, role: discord.Role = None):
        if role is not None:
            await dbcontrol.modify_setting(ctx.guild.id, "defaultrole", role.id)
            await ctx.send(f":white_check_mark: **Default role set to ``{role.name}``**")
        else:
            rol = await dbcontrol.get_setting(ctx.guild.id, 'defaultrole')
            role = ctx.guild.get_role(rol)
            await ctx.send(f"**The current default role is ``{role.name}``**" if rol else ":x: **No default role found**")


    @commands.has_permissions(manage_roles=True)
    @settings.command(brief="Sets the channel for logging.", usage='[channel]')
    async def logchannel(self, ctx, channel: discord.TextChannel = None):
        if channel is not None:
            await dbcontrol.modify_setting(ctx.guild.id, "logchannel", channel.id)
            await  ctx.send(f":white_check_mark: **Log channel set to ``{channel.name}``**")
        else:
            chan = await dbcontrol.get_setting(ctx.guild.id, 'logchannel')
            channel = ctx.guild.get_channel(chan)
            await ctx.send(f"**The current log channel is ``{channel.name}``**" if chan else ":x: **No log channel found**")

    @commands.has_permissions(manage_roles=True)
    @settings.command(brief="Sets the channel for announcements.", usage='[channel]')
    async def announcechannel(self, ctx, channel: discord.TextChannel = None):
        if channel is not None:
            await dbcontrol.modify_setting(ctx.guild.id, "announcechannel", channel.id)
            await ctx.send(f":white_check_mark: **Announcement channel set to ``{channel.name}``**")
        else:
            chan = (await dbcontrol.get_guild(ctx.guild.id))['announcechannel']
            channel = ctx.guild.get_channel(chan)
            await ctx.send(f"**The current announcements channel is ``{channel.name}``**" if chan else ":x: **No announcement channel found**")

    @commands.has_permissions(manage_roles=True)
    @settings.command(brief="Assigns a muterole for the mute and unmute commands", usage="[role]")
    async def muterole(self, ctx, role: discord.Role = None):
        if role is not None:
            if role > ctx.guild.me.top_role:
                await ctx.send(":x: **This muterole is higher than my top role**")
                return
            await dbcontrol.modify_setting(ctx.guild.id, "muterole", role.id)
            await ctx.send("The muterole has been set to " + role.mention)
        else:
            muteRole = (await dbcontrol.get_guild(ctx.guild.id))['muterole']
            role = ctx.guild.get_role(muteRole)
            await ctx.send(f"**The current muterole is ``{role.name}``**" if muteRole else ":x: **No muterole found**")


def setup(bot):
    bot.add_cog(Settings(bot))


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
        settingsJSON = await dbcontrol.get_guild(ctx.guild.id)['settings']

    @commands.has_permissions(manage_roles=True)
    @settings.command(brief="Sets the default role for new users", usage='[role]')
    async def defaultrole(self, ctx, role: discord.Role = None):
        if role is not None:
            await dbcontrol.modify_guild(ctx.guild.id, "defaultrole", role.id)
            await ctx.send(f":white_check_mark: **Default role set to ``{role.name}``**")
        else:
            rol = (await dbcontrol.get_guild(ctx.guild.id))['defaultrole']
            role = ctx.guild.get_role(rol)
            await ctx.send(f"**The current default role is ``{role.name}``**" if rol else ":x: **No default role found**")


    @commands.has_permissions(manage_roles=True)
    @settings.command(brief="Sets the channel for logging.", usage='[channel]')
    async def logchannel(self, ctx, channel: discord.TextChannel = None):
        if channel is not None:
            await dbcontrol.modify_guild(ctx.guild.id, "logchannel", channel.id)
            await  ctx.send(f":white_check_mark: **Log channel set to ``{channel.name}``**")
        else:
            chan = (await dbcontrol.get_guild(ctx.guild.id))['logchannel']
            channel = ctx.guild.get_channel(chan)
            await ctx.send(f"**The current log channel is ``{channel.name}``**" if chan else ":x: **No log channel found**")

    @commands.has_permissions(manage_roles=True)
    @settings.command(brief="Sets the channel for announcements.", usage='[channel]')
    async def announcechannel(self, ctx, channel: discord.TextChannel = None):
        if channel is not None:
            await dbcontrol.modify_guild(ctx.guild.id, "announcechannel", channel.id)
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
            await dbcontrol.modify_guild(ctx.guild.id, "muterole", role.id)
            await ctx.send("The muterole has been set to " + role.mention)
        else:
            muteRole = (await dbcontrol.get_guild(ctx.guild.id))['muterole']
            role = ctx.guild.get_role(muteRole)
            await ctx.send(f"**The current muterole is ``{role.name}``**" if muteRole else ":x: **No muterole found**")


def setup(bot):
    bot.add_cog(Settings(bot))


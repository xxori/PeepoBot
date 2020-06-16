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
import dbcontrol
import json

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return "Command to manage the counting feature"

    @commands.command(brief="Gets current number of a count")
    async def nc(self, ctx):
        if str(ctx.channel.id) in self.bot.ongoing_counts[ctx.guild.id].keys():
            await ctx.send(self.bot.ongoing_counts[ctx.guild.id][ctx.channel.id]["current"])
        else:
            await ctx.send(":x:")

    @commands.group(invoke_without_command=True, brief="Group containing management and info of counting", usage="[subcommand] <argument(s)>")
    async def count(self, ctx):
        if str(ctx.channel.id) not in self.bot.ongoing_counts[ctx.guild.id].keys():
            return await ctx.send(":x: **No count currently ongoing in this channel**")

        count = self.bot.ongoing_counts[ctx.guild.id][str(ctx.channel.id)]
        embed = discord.Embed(title=f"Count in {ctx.channel.name}", color=discord.Color.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Current Number", value=str(count["current"]), inline=False)
        embed.add_field(name="Highest Number", value=str(count["highest"]), inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        if count["last_user"]:
            embed.add_field(name="Last Counter", value=self.bot.get_user(count["last_user"]).mention)
        if count["last_fail"]:
            embed.add_field(name="Last Fail", value=self.bot.get_user(count["last_user"]).mention)
        embed.add_field(name="Started By", value=self.bot.get_user(count["started_by"]).mention)
        await ctx.send(embed=embed)


    @commands.has_permissions(manage_channels=True)
    @count.command(brief="Starts a count in the current channel or a specified channel")
    async def start(self, ctx, channel = None):
        if channel:
            converter = commands.TextChannelConverter
            channel = converter.convert(ctx, channel)
        else:
            channel = ctx.channel
        if str(channel.id) in self.bot.ongoing_counts[ctx.guild.id].keys():
            return await ctx.send(f":x: **There is already a count ongoing in ``{channel.name}``**")

        self.bot.ongoing_counts[ctx.guild.id][str(channel.id)] = {"current" : 0, "highest" : 0, "last_user" : None, "started_by" : ctx.author.id, "last_fail": None}
        await ctx.send(f":white_check_mark: **Count started in ``{channel.name}``**")

    @commands.has_permissions(manage_channels=True)
    @count.command(brief="Stops the count in the current channel or a specified channel")
    async def stop(self, ctx, channel = None):
        if channel:
            converter = commands.TextChannelConverter
            channel = converter.convert(ctx, channel)
        else:
            channel = ctx.channel

        if str(channel.id) not in self.bot.ongoing_counts[ctx.guild.id].keys():
            await ctx.send(f":x: **There is no count ongoing in ``{channel.name}``**")
        else:
            del self.bot.ongoing_counts[ctx.guild.id][str(ctx.channel.id)]
            await ctx.send(f":white_check_mark: **Count stopped in ``{channel.name}``**")

    @commands.has_permissions(manage_channels=True)
    @count.command(brief="Sets current count number (cheaty cheaty)")
    async def set(self, ctx, number: int):
        if str(ctx.channel.id) not in self.bot.ongoing_counts[ctx.guild.id].keys():
            return await ctx.send(f":x: **No count currently ongoing in this channel**")
        if number < 0:
            return await ctx.send(":x: **No negative numbers, dummy**")

        count = self.bot.ongoing_counts[ctx.guild.id][str(ctx.channel.id)]
        count["current"] = number
        count["last_user"] = ctx.author.id
        await ctx.message.add_reaction("✅")


    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)

        if ctx.author.bot: # No counting bots
            return

        if str(ctx.channel.id) not in self.bot.ongoing_counts[ctx.guild.id].keys(): # No ongoing count in current channel
            return

        if await dbcontrol.is_blacklist(ctx.author.id):
            return

        if ctx.author.bot:
            return

        list = message.content.split(" ")
        try:
            number = int(list[0])
        except:
            return
        count = self.bot.ongoing_counts[ctx.guild.id][str(ctx.channel.id)]
        if count["last_user"] == ctx.author.id:
            return await ctx.send(f":x: **{ctx.author.mention} You can't count twice in a row dumbass**")
        count["last_user"] = ctx.author.id
        if number == count["current"] + 1:
            count["current"] += 1
            if len(str(number)) >= 2 and str(number)[-2:] == "69":
                await message.add_reaction("😎")
            elif len(str(number)) >= 3 and str(number)[-3:] == "420":
                await message.add_reaction("🌿")
            elif len(str(number)) > 2 and str(number)[-2:] == "00":
                await message.add_reaction("🏅")
            elif len(str(number)) >= 3 and str(number)[-3:] == "666":
                await message.add_reaction("😈")
            else:
                await message.add_reaction("✅")
            if number > count["highest"]:
                count["highest"] = number
        else:
            if count["current"] != 0:
                await message.add_reaction("❌")
                await ctx.send(f"**{ctx.author.mention} has messed up the count at {count['current']}**")
                count["last_fail"] = ctx.author.id
                count["current"] = 0

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        ctx = await self.bot.get_context(message)
        if str(ctx.channel.id) not in self.bot.ongoing_counts[ctx.guild.id].keys():
            return
        if ctx.author.bot:
            return
        if await dbcontrol.is_blacklist(ctx.author.id):
            return

        await ctx.send(f"Some retard ({ctx.author.mention}) deleted a message. The current number is ``{self.bot.ongoing_counts[ctx.guild.id][str(ctx.channel.id)]['current']}``")


def setup(bot):
    bot.add_cog(Counting(bot))

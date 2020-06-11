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

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ongoing_games = []

    @commands.command()
    async def tictactoe(self, ctx, opponent: discord.Member):
        self.ongoing_games.append(
            {
                "channel": ctx.channel.id,
                "members": [ctx.author.id, opponent.id],
                "game": "TicTacToe"
            })

    @commands.command()
    async def stopgame(self, ctx):
        no_games = True
        for ongoing_game in self.ongoing_games:
            if ctx.channel.id == ongoing_game["channel"]:
                no_games = False
                self.ongoing_games.remove(ongoing_game)
                await ctx.send(f":white_check_mark: **Game of ``{ongoing_game['game']}`` successfully halted**")
        if no_games:
            await ctx.send(":x: **No games currently ongoing in this channel**")


    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if ctx.author.bot:
            return
        for game in self.ongoing_games:
            if ctx.channel.id == game["channel"]:
                await ctx.send("ongoing game")

def setup(bot):
    bot.add_cog(Games(bot))
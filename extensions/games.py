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
        self.ongoing_games = {"ttt": [], "hangman": []}

    @commands.command()
    async def tictactoe(self, ctx):
        self.ongoing_games["ttt"].append(ctx.channel.id)

    @commands.command()
    async def stopgame(self, ctx):
        no_game = True
        for game in self.ongoing_games.keys():
            if ctx.channel.id in self.ongoing_games[game]:
                no_game = False
                self.ongoing_games[game].remove(ctx.channel.id)
                await ctx.send(f":white_check_mark: **Game of ``{game}`` stopped**")
        if no_game:
            await ctx.send(":x: **There are currently no ongoing games in this channel**")

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if ctx.author.bot:
            return
        for game in self.ongoing_games.keys():
            if ctx.channel.id in self.ongoing_games[game]:
                await ctx.send("ongoing game")

def setup(bot):
    bot.add_cog(Games(bot))
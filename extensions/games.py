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
import random
import utils

WORDS = open("words.txt").read().split("\n")

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ongoing_games = {}

    @commands.command()
    async def hangman(self, ctx):
        if ctx.channel.id in self.ongoing_games.keys():
            return await ctx.send(":x: **There is already an ongoing game in the current channel**")
        word = random.choice(WORDS)
        disp = ["\_" for _ in range(len(word))]
        disp[0] = ">\_<"
        self.ongoing_games[ctx.channel.id] = {
            "game": "hangman",
            "user": ctx.author,
            "word": word,
            "current_letter": 0,
            "turnNo": 0,
            "damage": 0,
            "guessed_letters": [],
            "display_string": " ".join(disp)
        }
        print(self.ongoing_games[ctx.channel.id])
        await ctx.send(f":white_check_mark: **Hangman Started**\n"+self.ongoing_games[ctx.channel.id]["display_string"])

    @commands.command()
    async def stopgame(self, ctx):
        if ctx.channel.id not in self.ongoing_games.keys():
            return await ctx.send(":x: **There is not ongoing game in the current channel**")
        self.ongoing_games.pop(ctx.channel.id)
        await ctx.send("**:white_check_mark: Game successfully ended**")

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return
        if ctx.author.bot:
            return
        if ctx.channel.id not in self.ongoing_games.keys():
            return

        gameData = self.ongoing_games[ctx.channel.id]

        if ctx.author != gameData["user"]:
            return

        if gameData["game"] == "hangman":
            guess = message.content.split(" ")[0]
            if len(guess) > 1:
                return await ctx.send("Please send only a single letter to guess the next letter in the word")
            if not guess.isalpha():
                return await ctx.send("Letters only please")
            gameData["turnNo"] += 1
            if message.content[0].lower() == gameData["word"][gameData["current_letter"]]:
                if (gameData["current_letter"]+1) >= len(gameData["word"]):
                    await ctx.send(f"**Congratulations! You won! The word was ``{gameData['word']}``**")
                    del self.ongoing_games[ctx.channel.id]
                else:
                    disp = gameData["display_string"].split(" ")
                    disp[gameData["current_letter"]] = "__" + guess + "__"
                    gameData["current_letter"] += 1
                    disp[gameData["current_letter"]] = ">\_<"
                    gameData["display_string"] = " ".join(disp)
                    await ctx.send(gameData["display_string"])
            else:
                gameData["damage"] += 1
                if gameData["damage"] >= 7:
                    await ctx.send(f"**You died! The word was ``{gameData['word']}``**")
                    del self.ongoing_games[ctx.channel.id]
                else:
                    gameData["guessed_letters"].append(guess)
                    await ctx.send(f"**Incorrect: ``{7-gameData['damage']}`` lives left**\nGuessed letters: {' '.join(gameData['guessed_letters'])}\n{gameData['display_string']}")




def setup(bot):
    bot.add_cog(Games(bot))
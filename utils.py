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

# This file defines random helper functions

import discord
from discord.ext import commands
import aiohttp

import asyncio
#import pyppeteer as pyp
#from functools import wraps
#import re
#from collections import Counter
from datetime import datetime
import dbcontrol
import json
from colour import COLOURS

# Cycle class for the prescence cycle
class Cycle:
    def __init__(self, elements):
        self.elements = elements
        self.index = 0

    @property
    def current(self):
        try:
            return self.elements[self.index]
        except IndexError:
            return None

    def __repr__(self):
        return self.elements

    def next(self):
        if self.index + 1 < len(self.elements):
            self.index += 1
        else:
            self.index = 0

    def prev(self):
        if self.index - 1 >= 0:
            self.index -= 1
        else:
            self.index = len(self.elements)-1

def format_thousands(num):
    num = str(num)
    l = len(num)
    if l > 3 and l < 5:
        return "{}.{}k".format(num[0], num[1])
    elif l > 4 and l < 7:
        return "{}k".format(num[:3])
    else:
        return num

# Checks if any given user is a bot developer using the developer ids from the config
async def is_developer(ctx):
    if not ctx.bot.check_dev(ctx.message.author.id):
        raise commands.NotOwner
    return True

# Formats large numbers into human readable numbers, such as 1000 to 1,000
def punctuate_number(number, div=','):
    out = ''
    c = 0
    for char in reversed(str(number)):
        if c > 2:
            out += div
            c = 0
        out += char
        c+=1
    return ''.join(reversed(out))

class HierarchyPermissionError(commands.CommandError):
    def __init__(self, ctx, target):
        super().__init__('', [ctx, target])

# copied over from bartender, formats timestamps into human readable text
def strfdelta(tdelta, fmt):
    delta = {"D": tdelta.days}
    delta['H'], remainder = divmod(tdelta.seconds, 3600)
    delta['M'], delta["S"] = divmod(remainder, 60)
    return fmt.replace('%D', str(delta['D'])).replace('%H', str(delta['H'])).replace('%M', str(delta['M'])).replace('%S', str(delta['S']))


# Checks if music is currently playing
async def audio_playing(ctx):
    client = ctx.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        raise NotPlayingAudio

# Checks if bot is in same vc as command sender
async def in_voice_channel(ctx):
    voice = ctx.author.voice
    bot_voice = ctx.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        raise NotInSameVoiceChannel

# The main check loop for the bot, checking for expired tempmutes and colour roles that no users own
async def check(bot):
    # Runs forever while bot is running
    while bot.initialization_finished and bot.is_ready():
        # Does check for every guild
        for guild in bot.guilds:
            guildid = guild.id
            now = datetime.utcnow().timestamp()

            gdata = await dbcontrol.get_guild(guildid)
            mutesJSON = gdata['tempmutes']
            mutesDict = json.loads(mutesJSON)

            muteroleid = await dbcontrol.get_setting(guildid,'muterole')
            muterole = guild.get_role(muteroleid)
            # Checking for expired tempmutes
            for i in list(mutesDict.keys()):
                if mutesDict[i] < now:
                    mutesDict.pop(i)
                    user = guild.get_member(int(i))
                    if muterole:
                        await user.remove_roles(muterole, reason="Tempmute expired")
            # Commits changes to db
            mutesJSON = json.dumps(mutesDict)
            await dbcontrol.modify_guild(guildid, 'tempmutes', mutesJSON)

            coloursJSON = (await dbcontrol.get_guild(guildid))['colours']
            coloursDict = json.loads(coloursJSON)
            # Checks for colour roles which no users own, which are deleted
            for colour in list(coloursDict.keys()):
                used = False
                role = guild.get_role(coloursDict[colour])
                if role:
                    for member in guild.members:
                        if role in member.roles:
                            used = True
                    if not used:
                        await role.delete(reason="Automated colour role removal, no users have role")
                        coloursDict.pop(colour)
                else:
                    coloursDict.pop(colour)
            coloursJSON = json.dumps(coloursDict)
            await dbcontrol.modify_guild(guildid, 'colours', coloursJSON)
            await asyncio.sleep(30)

# Converts a colour string to a discord.Colour object. If the string is hex, nothing is changed. If the string is a
# colour name it uses the COLOURS dict found in colour.py
def colour(colour):
    colourHex = hex(colour.replace("#", ""))
    if colourHex != None:
        colour = discord.Colour(colourHex)
    elif colour.lower() in COLOURS.keys():
        colour = discord.Colour(hex(COLOURS[colour.lower()]))
    else:
        return False
    return colour

# Converts string to hexadecimal, or returns None if it is invalid
def hex(num: str):
    try:
        hex = int(num, base=16)
        if hex < 0:
            return None
        if len(num) > 6:
            return None
        return hex
    except:
        return None

class NotPlayingAudio(commands.CheckFailure):
    def __init__(self):
        super().__init__()

class NotInSameVoiceChannel(commands.CheckFailure):
    def __init__(self):
        super().__init__()
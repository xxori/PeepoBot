import discord
from discord.ext import commands
import aiohttp

import asyncio
import pyppeteer as pyp
from bs4 import BeautifulSoup

import re
from collections import Counter

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

def check_dev(id):
    return id in [308034225137778698, 304219290649886720]

async def is_developer(ctx):
    if not check_dev(ctx.message.author.id):
        await ctx.send(f':x: **You need to be a bot developer to run ``{ctx.command.name}``.**')
        return False
    return True

def punctuate_number(number, div=','):
    '''
    1234 -> 1,234
    123456789 ->
    '''
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

# copied over from bartender
def strfdelta(tdelta, fmt):
	delta = {"D": tdelta.days}
	delta['H'], remainder = divmod(tdelta.seconds, 3600)
	delta['M'], delta["S"] = divmod(remainder, 60)
	return fmt.replace('%D', str(delta['D'])).replace('%H', str(delta['H'])).replace('%M', str(delta['M'])).replace('%S', str(delta['S']))

'''
class CleverBot:
    browser = None
    page = None
    element = None

    def __init__(self):
        pass

    async def init(self):
        self.browser = await pyp.launcher.launch()
        self.page = await self.browser.newPage()
        await self.page.goto("https://www.cleverbot.com")
        self.element =  await self.page.querySelector("input.stimulus")


    async def getResponse(self, text):
        """
        Send text to Cleverbot and recieve response
        """
        await self.element.type(text)
        await self.element.press("Enter")

        diff_history = [1, 1, 1]
        text = ''
        text_last = ''
        diff = 0

        for i in range(200):
            html = await self.page.content()
            soup = BeautifulSoup(html, features="html.parser")
            text = soup.find("p", {"id":"line1"}).getText().strip()
            if len(text) > 0:
                diff = len(text) - len(text_last)
                diff_history.append(diff)
                text_last = text

                if diff_history[-3:] == [0, 0, 0]:
                    break
        return text

    async def close(self):
        await self.page.close()
        await self.browser.close()
'''
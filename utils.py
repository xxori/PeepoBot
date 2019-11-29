import discord
from discord.ext import commands
import aiohttp

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

class HierarchyPermissionError(commands.CommandError):
    def __init__(self, ctx, target):
        super().__init__('', [ctx, target])

# copied over from bartender
def strfdelta(tdelta, fmt):
	delta = {"D": tdelta.days}
	delta['H'], remainder = divmod(tdelta.seconds, 3600)
	delta['M'], delta["S"] = divmod(remainder, 60)
	return fmt.replace('%D', str(delta['D'])).replace('%H', str(delta['H'])).replace('%M', str(delta['M'])).replace('%S', str(delta['S']))
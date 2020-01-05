import aiohttp
import discord
from discord.ext import commands
import dbcontrol
import aiosqlite
import random
import utils


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @property
    def description(self):
        return 'Random, fun commands'

    @commands.command(brief='Defines with Urban Dictionary', aliases=['dict', 'ud'], usage='[term]')
    async def urban(self, ctx, *, term):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url='http://api.urbandictionary.com/v0/define', params={'term': term})
            data = await response.json()
            await session.close()
        if len(data['list']) == 0:
            embed = discord.Embed(description='No Results Found!', color=0xFF0000)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=0x00FF00)
            embed.set_author(name=f'Definition of {term}')
            embed.add_field(name='Top Definitions: ', value=data['list'][0]['definition'].replace('[', '').replace(']', ''), inline=False)
            embed.add_field(name='Examples: ', value=data['list'][0]['example'].replace('[', '').replace(']', ''), inline=False)
            await ctx.send(embed=embed)

    @commands.command(brief='Shows posts from the dankmemes subreddit', aliases=['dankmemes'])
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as session:
            response = await session.get(url='https://meme-api.herokuapp.com/gimme/dankmemes')
            data = await response.json()
            await session.close()
        embed = discord.Embed(title=data['title'])
        embed.set_image(url=data['url'])
        await ctx.send(embed=embed)

    @commands.command(brief='Ping a random person', aliases=['rping'])
    @commands.has_permissions(mention_everyone=True)
    async def randomping(self, ctx):
        await ctx.send(random.choice(ctx.guild.members).mention)

    @commands.command(brief='Talk to cleverbot', aliases=['cbot'], usage='<sentence>')
    async def cleverbot(self, ctx, *, sentence):
        async with ctx.typing():
            response = await self.bot.cb.getResponse(sentence)
            if response.strip() == '':
                response = '``(no reply)``'
            await ctx.send(response)

    @commands.command(brief='Compare two CPUs', aliases=['cpu'], usage='<cpu1> vs <cpu2>')
    async def benchmarkcpu(self, ctx, *, cpus):
        cpu_div_raw = [i for i in cpus.replace('VS', 'vs').split('vs') if len(i) > 0]
        cpu_div = [i.strip().lower().replace('amd', '').replace('intel', '') for i in cpus.replace('VS', 'vs').split('vs') if len(i) > 0]

        with open('bench_cpu.csv', 'r') as f:
            cpulist = {}
            for ln in f.read().splitlines()[1:]:
                v = ln.split(',')
                name = v[3]
                if v[2].lower() == 'intel':
                    name.replace('core', '')
                cpulist[name.lower()] = {'type': v[0], 'partid': v[1], 'brand':v[2], 'proper_name':v[3], 'rank': v[4], 'bench': v[5], 'samples': v[6], 'url': v[7]}

        def try_getting(name):
            try:
                return cpulist[name]
            except KeyError:
                return None

        cpu_data = []
        for cpu_name, cpu_name_raw in zip(cpu_div, cpu_div_raw):
            cpu_name = cpu_name.strip()

            candidates = []
            data = try_getting(cpu_name) or try_getting('core '+cpu_name)
            if data is None:
                candidates = [k for k in cpulist.keys() if (cpu_name.replace(' ', '').replace('-', '') in k.replace(' ', '').replace('-', ''))]
                if len(candidates) == 1:
                    data = cpulist[candidates[0]]
                candidates = [cpulist[k] for k in candidates]
            cpu_data.append([cpu_name_raw, data, candidates])

        embed = discord.Embed(colour=discord.Colour.blurple())

        for cpu in cpu_data:
            name_raw = cpu[0]
            data = cpu[1]
            candidates = cpu[2]

            if data is None:
                if len(candidates) > 0:
                    possibilites = '\n'.join([f'- *``{c["brand"]} {c["proper_name"]}``* **({c["bench"]}%)**' for c in candidates][:20])
                    await ctx.send(f':x: **Multiple possibilities for query ``{name_raw.strip()}``.**\n\n{possibilites}')
                    return
                else:
                    await ctx.send(f':x: **No match for query ``{name_raw.strip()}``.**')
                    return
            else:
                embed.add_field(
                    name=f'**{data["proper_name"]}**',
                    value=f'Benchmark: ``{data["bench"]}%``\nRank: ``#{utils.punctuate_number(int(data["rank"]))}``\nSamples: ``{utils.punctuate_number(int(data["samples"]))}``\n[More Info]({data["url"]})',
                )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))
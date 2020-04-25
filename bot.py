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
import traceback
import dbcontrol
import datetime
import asyncio
import logging
import random
import utils
import json
import time
import sys
import os
import aiohttp

SPLASH_ASCII = '''
/$$$$$$$                                         /$$$$$$$              /$$    
| $$__  $$                                       | $$__  $$            | $$    
| $$  \ $$ /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$ | $$  \ $$  /$$$$$$  /$$$$$$  
| $$$$$$$//$$__  $$ /$$__  $$ /$$__  $$ /$$__  $$| $$$$$$$  /$$__  $$|_  $$_/  
| $$____/| $$$$$$$$| $$$$$$$$| $$  \ $$| $$  \ $$| $$__  $$| $$  \ $$  | $$    
| $$     | $$_____/| $$_____/| $$  | $$| $$  | $$| $$  \ $$| $$  | $$  | $$ /$$
| $$     |  $$$$$$$|  $$$$$$$| $$$$$$$/|  $$$$$$/| $$$$$$$/|  $$$$$$/  |  $$$$/
|__/      \_______/ \_______/| $$____/  \______/ |_______/  \______/    \___/  
                             | $$                                              
                             | $$                                              
                             |__/                                              
'''

class Peepo(commands.AutoShardedBot):
    def __init__(self, logger, config):
        super(Peepo, self).__init__(command_prefix=None)
        self.logger = logger
        self.config = config
        self.version = '1.0.0'
        self.run_time = None
        self.connect_time = None
        self.presences = []
        self.presence_looping = True
        self.module_directories = ['extensions']
        self.default_prefix = None

        self.snipe_info = {}
        # USE THIS INSTEAD OF IS_READY!!!!!!!!! DATABASE ISSUES
        self.initialization_finished = False

    def strfdelta(self, tdelta, fmt):
        d = {"D": tdelta.days}
        d["H"], rem = divmod(tdelta.seconds, 3600)
        d["M"], d["S"] = divmod(rem, 60)
        return fmt.format(**d)

    def check_dev(self, id):
        return (id in self.config['authorized_dev_ids'])

    def load_cogs(self):
        for module_dir in self.module_directories:
            if os.path.isdir(f'./{module_dir}'):
                self.logger.info(f'Loading extensions from "{module_dir}"')
                for module in [i.replace('.py', '', 1) for i in os.listdir(f'./{module_dir}') if i.endswith('.py')]:
                    try:
                        self.load_extension(f'{module_dir}.{module}')
                    except Exception as e:
                        self.logger.warning(f'Failed to load extension {module_dir}.{module}')
                        traceback.print_exception(type(e), e, e.__traceback__)
                    else:
                        self.logger.info(f'Loaded extension {module_dir}.{module}')
                self.logger.info(f'Finished loading from "{module_dir}"')
        self.logger.info('Finished loading modules.')



    def run(self):
        self.default_prefix = self.config['default_prefix']
        self.load_cogs()
        self.run_time = datetime.datetime.utcnow()
        with open('presences.txt', 'r+') as f:
            self.presences = f.read().splitlines()
        self.logger.info(f'Loaded ({len(self.presences)}) presences.')
        self.logger.info('Pre-start checks cleared, start login.')

        try:
            super(Peepo, self).run(self.config['token'].strip())
        except discord.LoginFailure as e:
            self.logger.critical(f'Login Failure - {e} (check your config)')
        except aiohttp.ClientConnectionError as e:
            self.logger.critical(f'Connection Error - {e}')

        runtime = datetime.datetime.utcnow() - self.run_time
        self.logger.info(f'Running duration: {utils.strfdelta(runtime, "%Dd %Hh %Mm %Ss")}')
        #self.logger.info('Closing cleverbot session...')
        #asyncio.get_event_loop().run_until_complete(self.cb.close())

    async def get_prefix(self, message):
        prefix = await dbcontrol.get_setting(message.guild.id, 'prefix')
        return prefix

    async def close(self):
        if hasattr(self, 'session'):
            await self.session.close()
        await super().close()
        self.logger.info('Bot has shut down successfully.')

    # events
    async def on_message(self, message):
        if self.initialization_finished and self.is_ready:
            ctx = await self.get_context(message)
            if ctx.valid:
                if ctx.guild is None:
                    return

                if await dbcontrol.is_blacklist(message.author.id):
                   await message.channel.send(f'Sorry, {message.author}, you are blacklisted and cannot use commands.')
                   return

            await super().on_message(message)

    async def on_message_delete(self, message):
        if self.snipe_info.get(message.guild.id) is None:
            self.snipe_info[message.guild.id] = [message]
        else:
            self.snipe_info[message.guild.id].append(message)
            self.snipe_info[message.guild.id] = self.snipe_info[message.guild.id][-10:] # only retain last 10 messages

    async def on_ready(self):
        self.logger.info('Readying database for operations.')
        await dbcontrol.initialize_tables(self)

        old_time = self.connect_time
        self.connect_time = datetime.datetime.utcnow()
        self.logger.info(f'Connection time reset. ({old_time or "n/a"} -> {self.connect_time})')
        self.logger.info(f'Client ready: {self.user} ({self.user.id})')

        #self.logger.info('Starting cleverbot session...')
        #self.cb = utils.CleverBot()
        #await self.cb.init()
        self.session = aiohttp.ClientSession(loop=self.loop)
        # Starting 30 second cycle for colours and mutes checking
        self.logger.info("Starting role check loop.")
        self.loop.create_task(utils.check(self))

        self.logger.info(f'Starting presence loop.')
        self.loop.create_task(self.presence_changer())

        self.logger.info('Initialization finished.')
        self.initialization_finished = True

    async def presence_changer(self):
        possible = [discord.Game(name=i) for i in self.presences]
        presences = utils.Cycle(possible)
        presences.index = random.randint(0, len(possible)-1)

        while self.presence_looping:
            if self.is_ready():
                await self.change_presence(activity=presences.current)
                presences.next()
                await asyncio.sleep(20)

    async def log(self, guild, message):
        logchannel = await dbcontrol.get_setting(id, settings)
        if logchannel ==  "":
            return
        channel = guild.get_channel(logchannel)
        await channel.send(f"[{datetime.utcnow().strptime('%d/%m/y %H:%M')} UTC] " + str(message))

def read_config():
    conf_template = {
        'token': 'create an application at https://discordapp.com/developers/',
        'default_prefix': '!',
        'logfiles': {
            'enabled': True,
            'overwrite': False
        },
        'authorized_dev_ids': [308034225137778698, 304219290649886720], # developers that can execute dev commands
        'main_guild': -1, # main guild bot operates around, set to -1 to disable,
        'show_splash_screen': True
    }

    if not os.path.isfile('config.json'):
        with open('config.json', 'w+') as f:
            json.dump(conf_template, f, indent=4)
        return conf_template
    else:
        with open('config.json', 'r') as f:
            data = json.load(f)
        return data


if __name__ == '__main__':
    config = read_config()

    if config['show_splash_screen']:
        print(SPLASH_ASCII)

    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    stdhandler = logging.StreamHandler()
    stdhandler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] : %(message)s', '%d/%m/%Y %H:%M:%S'))
    logger.addHandler(stdhandler)

    if config['logfiles']['enabled']:
        if not os.path.isdir('logs'):
            os.mkdir('logs')

        if not config['logfiles']['overwrite']:
            date = datetime.datetime.now().strftime("%d-%m-%y")
            lastid = 0
            for filename in os.listdir('logs'):
                if filename.startswith(date):
                    x = int(filename.split('.log')[0].split('#')[-1])
                    lastid = x if x > lastid else lastid
            logfile = f'logs/{date} #{lastid+1}.log'
        else:
            logfile = 'logs/latest.log'
        print(f'Logging to {logfile}')

        filehandler = logging.FileHandler(filename=logfile, encoding='utf-8', mode='w')
        filehandler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] : %(message)s', '%d/%m/%Y %H:%M:%S'))
        logger.addHandler(filehandler)

    time.sleep(0.1)
    bot = Peepo(logger=logger, config=config)

    bot.run()


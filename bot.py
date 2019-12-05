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

class GTXBot(commands.AutoShardedBot):
    def __init__(self, logger, config):
        super(GTXBot, self).__init__(command_prefix=commands.when_mentioned_or('$'))

        self.logger = logger
        self.config = config

        self.version = '1.0.0'
        self.run_time = None
        self.connect_time = None
        self.presences = []
        self.presence_looping = True

        self.module_directories = ['extensions']

        # USE THIS INSTEAD OF IS_READY!!!!!!!!! DATABASE ISSUES
        self.initialization_finished = False

    def strfdelta(self, tdelta, fmt):
        d = {"D": tdelta.days}
        d["H"], rem = divmod(tdelta.seconds, 3600)
        d["M"], d["S"] = divmod(rem, 60)
        return fmt.format(**d)

    def load_cogs(self):
        self.logger.info('Started loading modules.')
        for module_dir in self.module_directories:
            if os.path.isdir(f'./{module_dir}'):
                self.logger.info(f'Loading from "{module_dir}"')
                for module in [i.replace('.py', '', 1) for i in os.listdir(f'./{module_dir}') if i.endswith('.py')]:
                    try:
                        self.load_extension(f'{module_dir}.{module}')
                    except Exception as e:
                        self.logger.warning(f'Failed to load extension {module_dir}.{module}')
                        traceback.print_exception(type(e), e, e.__traceback__)
                    else:
                        self.logger.info(f'Loaded module {module_dir}.{module} successfully.')
                self.logger.info(f'Finished loading from "{module_dir}"')
        self.logger.info('Finished loading modules.')

    def run(self):
        self.load_cogs()
        self.run_time = datetime.datetime.utcnow()
        self.logger.info('Loading presences.')

        with open('presences.txt', 'r+') as f:
            self.presences = f.read().splitlines()
        self.logger.info(f'Loaded ({len(self.presences)}) presences.')
        self.logger.info('Pre-start checks cleared, start login.')

        try:
            super(GTXBot, self).run(self.config['token'])
        except discord.LoginFailure as e:
            self.logger.critical(f'Login Failure - {e}')

        runtime = datetime.datetime.utcnow() - self.run_time
        self.logger.info(f'Running duration: {utils.strfdelta(runtime, "%Dd %Hh %Mm %Ss")}')
        self.logger.info('Bot has shut down successfully.')

    # events

    async def on_message(self, message):
        if self.initialization_finished and self.is_ready:
            await super().on_message(message)

    #async def on_message_delete(self, message):
    #    if message.author.id != self.user.id:
    #        await message.channel.send('No sniping in my server, young punk', delete_after=0)

    async def on_message(self, message):
        threads = {
            647776725031190558: 'f',
            647776760947015701: 'hmm',
            648308440267227147: 'kek',
            648415976127201290: 'hi'
        }
        if message.channel.id not in threads:
            pass
        else:
            if message.content.lower() != threads[message.channel.id]:
                await message.delete()
                await message.author.send(f"**Oi, {message.author.mention}, stop breaking the thread rules.**")


    async def on_ready(self):
        self.logger.info('Initializing database.')
        await dbcontrol.initialize_tables(self)

        old_time = self.connect_time
        self.connect_time = datetime.datetime.utcnow()
        self.logger.info(f'Connection time reset. ({old_time or "n/a"} -> {self.connect_time})')
        self.logger.info(f'Client ready: {self.user} ({self.user.id})')
        self.loop.create_task(self.presence_changer())
        self.logger.info(f'Started presence loop.')

        self.logger.info('Marking initialization_finished.')
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


def read_config():
    conf_template = {
        'token': 'create an application at https://discordapp.com/developers/',
        'logfiles': {
            'enabled': True,
            'overwrite': False
        }
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
    bot = GTXBot(logger=logger, config=config)

    bot.run()


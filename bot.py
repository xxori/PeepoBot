import discord
from discord.ext import commands
import datetime
import asyncio
import logging
import json
import time
import sys
import os
import traceback
import random


class SystemDBot(commands.AutoShardedBot):
	def __init__(self, logger, config):
		super(SystemDBot, self).__init__(command_prefix=commands.when_mentioned_or('sudo '))

		self.logger = logger
		self.config = config

		self.version = '1.0.0'
		self.run_time = None
		self.connect_time = None

		self.module_directories = ['extensions']

	def strfdelta(self, tdelta, fmt):
		d = {"days": tdelta.days}
		d["hours"], rem = divmod(tdelta.seconds, 3600)
		d["minutes"], d["seconds"] = divmod(rem, 60)
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
		#self.logger.info('Initializing database.')
		#self.loop.run_until_complete(dbcontrol.initialize_tables(bot))
		self.logger.info('Pre-start checks cleared, start login.')

		try:
			super(SystemDBot, self).run(self.config['token'])
		except discord.LoginFailure as e:
			self.logger.critical(f'Login Failure - {e}')
		self.logger.info('Bot has shut down successfully.')

	# events

	async def on_message(self, message):
		if self.is_ready():
			await super().on_message(message)

	async def on_ready(self):
		old_time = self.connect_time
		self.connect_time = datetime.datetime.utcnow()
		self.logger.info(f'Connection time reset. ({old_time or "n/a"} -> {self.connect_time})')
		self.logger.info(f'Client ready: {self.user} ({self.user.id})')
		await self.change_presence(activity=discord.Game(random.choice(self.config['presence_cycle'])))
		self.logger.info(f'Changed presence.')


def read_config():
	conf_template = {
		'token': 'create an application at https://discordapp.com/developers/',
		'logfiles': {
			'enabled': True,
			'overwrite': False
		},
		'presence_cycle': ['GTX+ MasterRace', 'sudo help', 'also see rtx+']
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
	bot = SystemDBot(logger=logger, config=config)

	bot.run()


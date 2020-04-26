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

import aiosqlite
import json
from discord.ext import commands
import discord
from datetime import datetime

DB_PATH = './common.db'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

async def initialize_tables(bot):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory

        await c.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER, seen_in TEXT, settings TEXT, bio TEXT, image_url TEXT, profile_color INTEGER, blacklist INTEGER)')
        await c.execute('CREATE TABLE IF NOT EXISTS tags(author INTEGER, guild INTEGER, created REAL, name TEXT, content TEXT)')
        await c.execute('CREATE TABLE IF NOT EXISTS guilds(id INTEGER, settings TEXT, roles TEXT, tempmutes TEXT, colours TEXT)')

        bot.logger.info('Cleaning guild database.')
        await rebuild_guilds(bot)
        bot.logger.info('Cleaning user database.')
        await rebuild_users(bot)
        await c.commit()

async def rebuild_users(bot):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory

        for member in bot.get_all_members():
            await add_user(member.id, bot)

        await c.commit()

async def rebuild_guilds(bot):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory

        for guild in bot.guilds:
            data = await get_guild(guild.id)

            if not data:
                if guild.system_channel:
                    await c.execute(f'INSERT INTO guilds VALUES (?, ?, ?, ?, ?)', (str(guild.id), '{"prefix": "' + bot.default_prefix + '", "announcechannel": ' + str(guild.system_channel.id) + '}', '{}', '{}', "{}"))
                else:
                    await c.execute(f'INSERT INTO guilds VALUES (?, ?, ?, ?, ?)', (str(guild.id), '{"prefix": "' + bot.default_prefix + '"}', '{}', '{}', "{}"))

        await c.commit()

async def add_guild(bot, id):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        guild = bot.get_guild(id)

        announcements_channel = -1
        for channel in sorted(guild.channels, key=lambda x: x.name):
            if channel.name.strip() == 'announcements':
                announcements_channel = channel.id

        await c.execute(f'INSERT INTO guilds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', id, '$', -1, -1, announcements_channel, -1, -1, -1, -1)

        for member in guild.members:
            add_user(member.id, bot)

        await c.commit()


# Guild Utilities

async def get_guild(id):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        cursor = await c.execute(f'SELECT * FROM guilds WHERE id = ' + str(id))
        data = await cursor.fetchone()
    return data

async def modify_guild(id, parameter, value):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        await c.execute(f'UPDATE guilds SET {parameter} = ? WHERE id = ?', (value, id))
        await c.commit()

# User Utilities

async def add_user(id, bot):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        settings_template = {
            'embedcolor': 'blurple',
            'pingmonitor': False,
        }

        user = bot.get_user(id)
        if user is None:
            return False

        cursor = await c.execute(f'SELECT * FROM users WHERE id = ' + str(id))
        data = await cursor.fetchone()

        guilds = [guild for guild in bot.guilds if user in guild.members]

        if not data:
            settings = json.dumps(settings_template).replace("'", "''")
            await c.execute(f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", (id, str([i.id for i in guilds]), str(settings), '', '', '', 0))
        else:
            await c.execute(f'UPDATE users SET seen_in = ? WHERE id = ?', (str([i.id for i in guilds]), id))
        await c.commit()


async def modify_user(id, parameter, value):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory

        await c.execute(f'UPDATE users SET {parameter} = ? WHERE id = ?', (value, id))
        await c.commit()

async def get_user(id):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        cursor = await c.execute(f'SELECT * FROM users WHERE id = {id}')
        data = await cursor.fetchone()
    return data

async def add_tag(author, guild, name, content):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        await c.execute(f'INSERT INTO tags VALUES (?, ?, ?, ?, ?)', (author.id, guild.id, datetime.utcnow().timestamp(), name, content))
        await c.commit()

async def get_tag(author, guild, name):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        cursor = await c.execute(f'SELECT * FROM tags WHERE name = ? AND author = ? AND guild = ?', name, author, guild)
        data = await cursor.fetchone()
    return data

async def get_guild_tag(guild, name):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        cursor = await c.execute(f'SELECT * FROM tags WHERE name = ? AND guild = ?', (name, guild))
        data = await cursor.fetchone()
    return data

async def run_command(command):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        await c.execute(command)
        await c.commit()

async def delete_tag(author, guild, name):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        await c.execute(f'DELETE FROM tags WHERE author = ? AND name = ? AND guild = ?', (author, name, guild))
        await c.commit()

async def get_all_tags(author, guild):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        cursor = await c.execute(f'SELECT * FROM tags WHERE author = ? AND guild = ?', (author, guild))
        data = await cursor.fetchall()
    return data

async def is_blacklist(id):
    async with aiosqlite.connect(DB_PATH) as c:
        c.row_factory = dict_factory
        cursor = await c.execute(f'SELECT * FROM users WHERE id = ' + str(id))
        data = await cursor.fetchone()
        if data:
            if 'blacklist' in data.keys():
                if data['blacklist'] == 1:
                    bl = True
                else:
                    bl = False
            else:
                bl = False
        else:
            bl = False
    return bl

async def get_setting(id, setting):
    settingsJSON = (await get_guild(id))['settings']
    settingsDict = json.loads(settingsJSON)
    if setting in settingsDict.keys():
        return settingsDict[setting]
    else:
        return None

async def modify_setting(id, setting, value):
    settingsJSON = (await get_guild(id))['settings']
    settingsDict = json.loads(settingsJSON)
    if value:
        settingsDict[setting] = value
    else:
        settingsDict.pop(setting)
    settingsJSON = json.dumps(settingsDict)
    await modify_guild(id, 'settings', settingsJSON)

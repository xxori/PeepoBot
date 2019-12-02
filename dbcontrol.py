import aiosqlite
import json

from discord.ext import commands
import discord

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

async def get_connector():
    connector = await aiosqlite.connect('./common.db')
    connector.row_factory = dict_factory
    return connector

async def initialize_tables(bot):
    c = await get_connector()
    await c.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER, seen_in TEXT, level INTEGER, exp INTEGER, settings TEXT)')
    await c.execute('CREATE TABLE IF NOT EXISTS tags(author INTEGER, created REAL, name TEXT, content TEXT)')
    await c.execute('CREATE TABLE IF NOT EXISTS guilds(id INTEGER, prefix TEXT, logchannel INTEGER, muterole INTEGER, announcechannel INTEGER)')

    bot.logger.info('Rebuilding guild database.')
    await rebuild_guilds(bot)
    bot.logger.info('Rebuilding user database.')
    await rebuild_users(bot)

    await c.commit()
    await c.close()

async def rebuild_users(bot):
    c = await get_connector()

    for member in bot.get_all_members():
        add_user(member.id, bot)

    await c.commit()
    await c.close()

async def rebuild_guilds(bot):
    c = await get_connector()

    for guild in bot.guilds:
        cursor = await c.execute(f'SELECT * FROM guilds WHERE id = {guild.id}')
        data = await cursor.fetchone()

        if not data:
            await c.execute(f'INSERT INTO guilds VALUES ({guild.id}, "$", "", "", "")')

    await c.commit()
    await c.close()

async def add_guild(bot, id):
    c = await get_connector()
    guild = bot.get_guild(id)

    announcements_channel = -1
    for channel in sorted(guild.channels, key=lambda x: x.name):
        if 'announcements' in channel.name.strip():
            announcements_channel = channel.id

    await c.execute(f'INSERT INTO guilds VALUES ({id}, "$", -1, -1, {announcements_channel})')

    for member in guild.members:
        add_user(member.id, bot)

    await c.commit()
    await c.close()


# Guild Utilities

async def get_guild(id):
    c = await get_connector()
    cursor = await c.execute(f'SELECT * FROM guilds WHERE id = {guild.id}')
    data = await cursor.fetchone()
    await c.close()
    return data

async def modify_guild(id, parameter, value):
    c = await get_connector()

    if isinstance(value, str):
        value = f'"{value}"'

    await c.execute(f'UPDATE guilds SET {parameter} = {value} WHERE id = {id}')
    await c.commit()
    await c.close()

# User Utilities

async def add_user(id, bot):
    c = await get_connector()
    settings_template = {
        'embedcolor': 'blurple',
        'pingmonitor': False,
    }

    user = await bot.get_user(id)
    if user is None:
        return False

    cursor = await c.execute(f'SELECT * FROM users WHERE id = {id}')
    data = await cursor.fetchone()

    guilds = [guild for guild in bot.guilds if user in guild.members]

    if not data:
        await c.execute(f'INSERT INTO users VALUES ({id}, "[]", 1, 0, {json.dumps(settings_template)})')
    else:
        await c.execute(f'UPDATE users SET seen_in = "{[i.id for i in guilds]}" WHERE id = {id}')
    await c.commit()
    await c.close()

async def modify_user(id, parameter, value):
    c = await get_connector()

    if isinstance(value, str):
        value = f'"{value}"'

    await c.execute(f'UPDATE users SET {parameter} = {value} WHERE id = {id}')
    await c.commit()
    await c.close()
import discord
from discord.ext import commands
import asyncio

class Quickstart(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_guild_join(self, guild: discord.Guild):
        if guild.me.guild_permissions.view_audit_log:
            async for entry in guild.audit_logs(limit=5):
                if entry.action == 28 and entry.target.id == self.user.id:
                    invite_user = entry.user
                    break

            invite_msg = '''
    :thumbsup: **Thanks for adding me to ``ree``!**
    
            My prefix is ``sudo`` by default.
            To get started with using me, do ``sudo help`` in your server.
    
    :wave: See ya around!
                '''

            await invite_user.send(invite_msg)

def setup(bot):
    bot.add_cog(Quickstart(bot))
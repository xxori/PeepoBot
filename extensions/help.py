import discord
from discord.ext import commands
import asyncio
import traceback

class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()
        self.command_attrs['brief'] = 'Help for bot commands.'
        self.command_attrs['description'] = 'Displays a list of all bot commands and their usages.'
        self.command_attrs['usage'] = '[command]'
        self.command_attrs['cog'] = "Utility"

    def divide(self, l, size):
        for i in range(0, len(l), size):
            yield l[i:i + size]

    async def send_bot_help(self, mapping):
        text = ''
        for cog, cmds in mapping.items():
                if len(cmds) > 0:
                    if cog is not None:
                        cname = cog.qualified_name
                        cdesc = cog.description
                    else:
                        cname = 'No Category'
                        cdesc = 'uncategorized commands'

                    text += f'{cname}\n{"="*len(cname)}\n* {cdesc or f"for whenever you need {cname.lower()}."}'

                    if len(cmds) > 0:
                        for cmd in cmds:
                            cmd_name = cmd.name + "|" + "|".join(cmd.aliases) if len(cmd.aliases) else cmd.name
                            cmd_desc = cmd.brief or cmd.description[:20] or "No Description"

                            cmd_info = f'{self.clean_prefix}{cmd_name} {cmd.usage or ""}'

                            spacer = 30-len(cmd_info)
                            if spacer < 0: spacer = 0

                            text += f'\n{cmd_info} {" "*spacer}:: {cmd_desc}'
                    else:
                        text += '\nNo Commands'
                    text += '\n\n\n'
        text += '\n'

        await self.get_destination().send(f"{self.context.author.mention} :point_right: **Check your DM's!**")
        for idx, chunk in enumerate(self.divide(text.splitlines(), 32)):
            doc = '\n```asciidoc\n'+'\n'.join(chunk).strip('```') + '```'
            if idx == 0:
                doc = '``Bot Commands``' + doc

            if len(doc.replace('```', '').replace('asciidoc', '').strip()) > 0:
                await self.context.author.send(doc)

    async def send_command_help(self, cmd):
        cmd_name = "|".join(cmd.aliases) if len(cmd.aliases) else cmd.name
        cmd_desc = cmd.description or cmd.brief or "No Description"
        cmd_info = f'{self.clean_prefix}{cmd_name} {cmd.usage or ""}'

        text = f'```asciidoc\n{cmd_info}\n* {cmd_desc}```'

        await self.context.author.send(text)
        await self.get_destination().send(f"{self.context.author.mention} :point_right: **Check your DM's!**")

    async def send_group_help(self, cmd):
        cmd_name = "|".join(cmd.aliases) if len(cmd.aliases) else cmd.name
        cmd_desc = cmd.description or cmd.brief or "No Description"
        cmd_info = f'{self.clean_prefix}{cmd_name} {cmd.usage or ""}'

        cmds = cmd.commands

        if len(cmds) > 0:
            sub = '\n\n== Subcommands =='
            for cmd in cmds:
                cmd_name = cmd.name + "|" + "|".join(cmd.aliases) if len(cmd.aliases) else cmd.name
                cmd_desc = cmd.brief or cmd.description[:20] or "No Description"

                cmd_info = f'{self.clean_prefix}{cmd_name} {cmd.usage or ""}'

                spacer = 30-len(cmd_info)
                if spacer < 0: spacer = 0

                sub += f'\n{cmd_info} {" "*spacer}:: {cmd_desc}'
        else:
            sub = ''

        text = f'```asciidoc\n{cmd_info}\n* {cmd_desc}{sub}```'

        await self.context.author.send(text)
        await self.get_destination().send(f"{self.context.author.mention} :point_right: **Check your DM's!**")

    async def command_not_found(self, string):
        await self.get_destination().send(f":x: ``{string}`` isn't a command, check your spelling.")

    async def send_error_message(self, error):
        pass

    async def on_help_command_error(self, ctx, e):
        traceback.print_exception(type(e), e, e.__traceback__)


def setup(bot):
    bot.help_command = HelpCommand()

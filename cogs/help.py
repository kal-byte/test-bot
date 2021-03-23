import discord
import typing as t
from bot import BigBoy
from discord.ext import commands


bot_mapping = t.Mapping[t.Optional[commands.Cog], t.List[commands.Command]]


class HelpCommand(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    def get_command_signature(self, command: commands.Command):
        sig = super().get_command_signature(command)
        return f"{self.clean_prefix}{command.qualified_name} {sig}"

    async def send_bot_help(self, mapping: bot_mapping):
        embed = discord.Embed()

        for cog in mapping:
            if cog is None:
                continue

            embed.add_field(
                name=cog.qualified_name,
                value=f"{self.clean_prefix}help {cog.qualified_name}",
                inline=False
            )

        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog: commands.Cog):
        embed = discord.Embed(title=f"Help for {cog.qualified_name}")
        for command in cog.get_commands():
            embed.add_field(name=command.signature,
                            value=command.short_doc or "No help provided...",
                            inline=False)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        embed = discord.Embed(name=command.signature,
                              description=command.help or "No help provided...")
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        embed = discord.Embed(name=group.signature,
                              description=group.help or "No help provided...")
        for command in group.commands:
            embed.add_field(name=command.signature,
                            value=command.short_doc or "No help provided...",
                            inline=False)
        await self.get_destination().send(embed=embed)


def setup(bot: BigBoy):
    bot.help_command = HelpCommand()


def teardown(bot: BigBoy):
    bot.help_command = commands.MinimalHelpCommand()

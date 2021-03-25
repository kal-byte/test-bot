import discord
from bot import BigBoy
from discord.ext import commands
from .pronouns import UserNotRegistered


class ErrorHandler(commands.Cog):
    def __init__(self, bot: BigBoy):
        self.bot: BigBoy = bot
        self.ignored = (
            commands.CommandNotFound,
        )
        self.plain = (
            UserNotRegistered,
            commands.BadArgument,
            commands.CheckFailure,
            commands.NotOwner
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, self.ignored):
            return
        if isinstance(error, self.plain):
            return await ctx.send(f"{error}")
        self.bot.latest_exception = error
        await ctx.send("There was an error executing this command.")
        raise error


def setup(bot: BigBoy):
    bot.add_cog(ErrorHandler(bot))

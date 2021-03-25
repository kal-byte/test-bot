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
        if isinstance(error, discord.HTTPException):
            return await ctx.send("Sorry, that file was too large.")
        raise error


def setup(bot: BigBoy):
    bot.add_cog(ErrorHandler(bot))

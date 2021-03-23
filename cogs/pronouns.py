import discord
import typing as t
from bot import BigBoy
from discord.ext import commands


pronouns = {
    "unspecified": "Unspecified",
    "hh": "he/him",
    "hi": "he/it",
    "hs": "he/she",
    "ht": "he/they",
    "ih": "it/him",
    "ii": "it/its",
    "is": "it/she",
    "it": "it/they",
    "shh": "she/he",
    "sh": "she/her",
    "si": "she/it",
    "st": "she/they",
    "th": "they/he",
    "ti": "they/it",
    "ts": "they/she",
    "tt": "they/them",
    "any": "Any pronouns",
    "other": "Other pronouns",
    "ask": "Ask me my pronouns",
    "avoid": "Avoid pronouns, use my name"
}


class UserNotRegistered(commands.CommandError):
    def __init__(self, member: discord.Member):
        message = f"{member.display_name} is not registered on <https://www.pronoundb.org/>"
        super().__init__(message)


class MemberID(discord.User):
    @classmethod
    async def convert(cls, ctx: commands.Context, arg: str) -> t.Union[discord.Member, discord.User]:
        try:
            member = await commands.MemberConverter().convert(ctx, arg)
        except commands.MemberNotFound:
            try:
                arg = int(arg, base=10)
            except ValueError:
                raise commands.BadArgument("That is not a valid user.")
            else:
                member = await ctx.bot.fetch_user(arg)
                if member is None:
                    raise commands.BadArgument("That is not a valid user.")
        return member


class Pronouns(commands.Cog):
    def __init__(self, bot: BigBoy):
        self.bot: BigBoy = bot

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, UserNotRegistered):
            return await ctx.send(f"{error}")
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(f"{error}")
        return await super().cog_command_error(ctx, error)

    @commands.command()
    async def pronouns(self, ctx: commands.Context, *, member: MemberID):
        """Gets the pronouns from a given user if they're registered on pronoundb.org."""
        params = {"platform": "discord", "id": member.id}
        url = "https://www.pronoundb.org/api/v1/lookup"
        async with self.bot.session.get(url, params=params) as resp:
            if resp.status == 404:
                raise UserNotRegistered(member)
            data = await resp.json()

        user_pronouns = pronouns.get(data["pronouns"])
        fmt = f"{member.display_name}'s pronouns are `{user_pronouns}`."
        await ctx.send(fmt)


def setup(bot: BigBoy):
    bot.add_cog(Pronouns(bot))

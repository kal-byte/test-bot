import discord
import typing as t
from bot import BigBoy
from discord.ext import commands


# https://pronoundb.org/docs
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


# Custom exception, BadArgument *could* be used
# but it makes less sense to.
class UserNotRegistered(commands.CommandError):
    def __init__(self, member: discord.Member):
        message = f"{member.display_name} is not registered on <https://www.pronoundb.org/>"
        super().__init__(message)


# This allows us to fetch people who aren't
# in the same guild or in cache.
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

    async def get_pronouns(self, member: t.Union[discord.Member, discord.User]) -> t.Optional[str]:
        """Simple method to get someones pronouns via the pronoundb or the bots db.
        The order is:
        - Check DB
        - Check PronounDB"""
        sql = "SELECT pronouns FROM users WHERE id = ?;"
        result = await self.bot.db.execute(sql, member.id)

        if result and (row := await result.fetchone()):
            return row["pronouns"]

        # Params for the URL, aiohttp takes care of all the sanitization and such.
        params = {"platform": "discord", "id": member.id}
        # Base URL so we can actually make the request.
        url = "https://www.pronoundb.org/api/v1/lookup"
        async with self.bot.session.get(url, params=params) as resp:
            # The API 404's if the user isn't found so we'll
            # raise our custom exception.
            if resp.status == 404:
                raise UserNotRegistered(member)
            # Well we have it so we'll get the data.
            data = await resp.json()

        return data["pronouns"]

    @commands.group(invoke_without_command=True)
    async def pronouns(self, ctx: commands.Context, *, member: t.Optional[MemberID]):
        """Gets the pronouns from a given user if they're registered on pronoundb.org."""
        pnouns = await self.get_pronouns(member)
        user_pronouns = pronouns.get(pnouns)
        fmt = f"{member.display_name}'s pronouns are `{user_pronouns}`."
        await ctx.send(fmt)

    @pronouns.command(name="set")
    async def pronouns_set(self, ctx: commands.Context, *, pnouns: str):
        """Set your pronouns in the bot database if you don't want to use pronoundb."""
        user_pronouns = pronouns.get(pnouns)
        if not user_pronouns:
            pnoun_list = "\n".join(
                f"{k:<11} -> {v}" for k, v in pronouns.items())
            fmt = ("Please make sure you select one from this list:\n"
                   f"```\n{pnoun_list}```")
            return await ctx.send(fmt)

        sql = ("INSERT INTO users(id, pronouns) VALUES(:1, :2) "
               "ON CONFLICT (id) DO UPDATE SET pronouns = :2;")
        values = {"1": ctx.author.id, "2": pnouns}
        await self.bot.db.execute(sql, values)
        await ctx.send("Okay, set your pronouns.")

    @pronouns.command(name="reset")
    async def pronouns_reset(self, ctx: commands.Context):
        """Resets your pronouns in the bot database."""
        sql = "UPDATE users SET pronouns = NULL WHERE id = ?;"
        await self.bot.db.execute(sql, ctx.author.id)
        await ctx.send("Reset your pronouns.")


def setup(bot: BigBoy):
    bot.add_cog(Pronouns(bot))

import config
import asqlite
import aiohttp
import discord
import typing as t
from discord.ext import commands


extensions = ["cogs.pronouns", "cogs.developer", "cogs.error_handler"]


async def get_prefix(bot: commands.Bot, message: discord.Message) -> str:
    return "=="


class BigBoy(commands.Bot):
    session: aiohttp.ClientSession
    db: asqlite.Connection

    def __init__(self, command_prefix: t.Union[t.Callable, t.Coroutine, str] = get_prefix, **kwargs):
        kwargs.setdefault("intents", discord.Intents.all())
        super().__init__(command_prefix, **kwargs)
        self.db = self.loop.run_until_complete(asqlite.connect("db.db"))
        self.loop.create_task(self.__ainit__())

        for cog in extensions:
            try:
                self.load_extension(cog)
            except Exception as err:
                print(f"{type(err).__name__} - {err}")

    async def __ainit__(self):
        await self.wait_until_ready()
        headers = {
            "User-Agent": "Testing Bot Python 3.9.2"
        }
        self.session = aiohttp.ClientSession(headers=headers)
        with open("schema.sql") as fh:
            await self.db.executescript(fh.read())

    async def on_ready(self):
        print("I'm ready.")

    async def process_commands(self, message: discord.Message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def close(self):
        await self.db.commit()
        await self.db.close()
        await self.session.close()
        return await super().close()

    def run(self, **kwargs):
        return super().run(config.token, **kwargs)

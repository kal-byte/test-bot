import config
import asqlite
import aiohttp
import discord
import typing as t
from collections import deque
from discord.ext import commands
from cogs.utils.context import Context


extensions = ["cogs.pronouns", "cogs.developer",
              "cogs.error_handler", "cogs.help", "cogs.youtube"]
description = (
    "kal#1806's testing bot. With some features such as pronoun fetching etc\n"
    "it's hardly complete and probably never will be, so uhh yeah."
)


async def get_prefix(bot: commands.Bot, message: discord.Message) -> str:
    return "=="


class BigBoy(commands.Bot):
    session: aiohttp.ClientSession
    db: asqlite.Connection
    latest_exception: Exception
    _edit_invoke: deque

    def __init__(self, command_prefix: t.Union[t.Callable, t.Coroutine, str] = get_prefix, **kwargs):
        kwargs.setdefault("intents", discord.Intents.all())
        kwargs.setdefault("description", description)
        super().__init__(command_prefix, **kwargs)
        self._edit_invoke = deque(maxlen=5)
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

    async def get_context(self, message: discord.Message, *, cls: Context = None):
        return await super().get_context(message, cls=Context)

    async def on_message_edit(self, _: discord.Message, after: discord.Message):
        await self.process_commands(after)

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

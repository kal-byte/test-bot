import asyncio
import typing as t


def to_thread(func: t.Callable) -> t.Coroutine:
    async def inner(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return inner


async def run_shell(command: str) -> bytes:
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    return stderr if stderr else stdout

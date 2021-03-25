from discord.ext import commands


class Context(commands.Context):
    async def send(self, content: str = None, **kwargs):
        kwargs.setdefault("embed", None)

        message = sorted(self.bot._edit_invoke,
                         key=lambda e: e[0] == self.message.id)

        check_list = [
            kwargs.get("files", []) != [],
            not message
        ]

        if message:
            message = message[0]
            check_list.append(message[0] != self.message.id)

        check = any(check_list)

        if check:
            message = await super().send(content, **kwargs)
            self.bot._edit_invoke.append((self.message.id, message))
            return message

        return await message[1].edit(content=content, **kwargs)

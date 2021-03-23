import io
import discord
import textwrap
import traceback
import contextlib
from bot import BigBoy
from discord.ext import commands


def get_code(codeblock: str):
    code = codeblock.splitlines()
    if code[0].startswith("```"):
        code.pop(0)

    if code[len(code) - 1].endswith("```"):
        if len(code[len(code) - 1]) > 3:
            code = code[len(code) - 1][:-3]
        else:
            code.pop(len(code) - 1)

    return "\n".join(code)


class Developer(commands.Cog, command_attrs=dict(hidden=True)):
    """Commands which aid development of the bot."""

    def __init__(self, bot: BigBoy):
        self.bot: BigBoy = bot

    async def cog_check(self, ctx: commands.Context):
        # Due to the nature of this cog, we don't really
        # want random people being able to access it
        # a major reason is due to the eval which could
        # easily destroy the bot's machine given into the
        # wrong hands. So we make a check to make sure
        # only people who are owners of this bot have access
        # to any command here.
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    async def reload(self, ctx: commands.Context):
        """Reloads all of the extensions on the bot."""
        # If we don't do (something like) this then
        # we'd get an exception thrown at us that says
        # the keys changed during iteration.
        extensions = [*self.bot.extensions.keys()]
        # This is generally just QOL but I enjoy
        # sending everything at once rather than
        # an individual message for each error.
        unsuccessful = []
        for extension in extensions:
            # Try to reload the extension
            try:
                self.bot.reload_extension(extension)
            except:
                # If it failed then just add the traceback
                # to the unsuccessful list.
                tb = traceback.format_exc()
                unsuccessful.append(f"```py\n{tb}```")

        # Base message just to say that
        # all extensions were reloaded
        base = "Reloaded all extensions.\n"
        # If there were unsuccessful ones.
        if unsuccessful:
            # Add them to the base and show the user.
            base += "However one or more failed.\n"
            base += "\n".join(unsuccessful)
        await ctx.send(base)

    @commands.command(name="eval")
    async def _eval(self, ctx: commands.Context, *, code: get_code):
        """Evaluates Python code. Useful for debugging."""
        # Just set our environment since we generally only
        # want to give what's needed.
        # The invoker can import stuff in the eval anyways.
        env = {
            "ctx": ctx,
            "bot": ctx.bot,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "author": ctx.author,
            "message": ctx.message,
            "discord": discord,
            "commands": commands,
        }

        # Actually make the block of code to evaluate. This is based on
        # what the user wrote so we just throw it into an async function.
        block = (
            "async def _eval_expr():\n" +
            textwrap.indent(code, "  ")
        )

        # use StringIO since we'll need it to
        # redirect stdout later on.
        # As a side note this context manager
        # makes life so much easier, if you don't already
        # use them more since they allow for
        # much cleaner code.
        with io.StringIO() as stream:
            try:
                # Execute the code so it's in our env now.
                # The 2 `env`'s here just put it into our env dict
                # which allows us to access it later to be able
                # to get the result of the evalution.
                exec(block, env, env)
                # Redirect stdout to our stream so if we
                # for example use a print() statement
                # it will be sent to our stream.
                with contextlib.redirect_stdout(stream):
                    # Call the function and put the result in a variable
                    # to be able to access so we can actually
                    # return the result to the invoker.
                    res = await env["_eval_expr"]()
            except Exception:
                # If it errored we'll send the traceback to ctx.
                tb = traceback.format_exc()
                fmt = f"```py\n{tb}```"
                return await ctx.send(fmt)

            # If the a value is found in the stream
            # then we'll send it to ctx.
            if value := stream.getvalue():
                return await ctx.send(value)

            # The result is None? return.
            if not res:
                return

            # If the result is an empty string,
            # we'll just send a ZWS.
            if res == "":
                return await ctx.send("\u200b")

            # If the result is an discord.Embed,
            # send to ctx as an embed.
            if isinstance(res, discord.Embed):
                return await ctx.send(embed=res)

            # If the result is a discord.File,
            # send to ctx as a file.
            elif isinstance(res, discord.File):
                return await ctx.send(file=res)

            # If it's a str or an int then just
            # send it normally.
            elif isinstance(res, (str, int)):
                return await ctx.send(res)

            # Else send the repr of it.
            else:
                return await ctx.send(repr(res))


def setup(bot: BigBoy):
    bot.add_cog(Developer(bot))

import io
import typing
import discord
from bot import BigBoy
from cogs import utils
from discord.ext import commands
from pytube import YouTube, Stream


@utils.to_thread
def download_video(url: str) -> io.BytesIO:
    yt = YouTube(url)
    buffer = io.BytesIO()
    stream = yt.streams.filter(resolution="720p")
    stream.first().stream_to_buffer(buffer)
    buffer.seek(0)
    return buffer, yt.title, yt.description, yt.views


class Youtube(commands.Cog):
    def __init__(self, bot: BigBoy):
        self.bot: BigBoy = bot

    @commands.command()
    async def download(self, ctx: commands.Context, *, url: str):
        """Downloads a given youtube link."""
        message = await ctx.send("Please wait whilst I download this video.")
        video = await download_video(url)
        embed = discord.Embed(title=video[1], description=video[2][:250])
        embed.set_footer(text=f"{video[3]} Views")
        file = discord.File(video[0], "video.mp4")
        await ctx.reply(file=file, embed=embed)
        await message.delete()


def setup(bot: BigBoy):
    bot.add_cog(Youtube(bot))

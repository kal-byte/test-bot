import io
import discord
from bot import BigBoy
from cogs import utils
from pytube import YouTube
from discord.ext import commands
from pytube.exceptions import RegexMatchError


@utils.to_thread
def download_video(url: str):
    url = url.strip("<>")
    yt = YouTube(url)
    buffer = io.BytesIO()
    stream = yt.streams.filter(resolution="720p")
    stream.first().stream_to_buffer(buffer)
    buffer.seek(0)
    return buffer, yt.title, yt.description, yt.views


@utils.to_thread
def video_info(url: str):
    url = url.strip("<>")
    yt = YouTube(url)
    title = yt.title
    description = yt.description[:250]
    views = yt.views
    author = yt.author
    thumbnail = yt.thumbnail_url
    watch_url = yt.watch_url
    vid_id = yt.video_id
    publish_date = yt.publish_date
    return (
        title, description, views,
        author, thumbnail, watch_url,
        vid_id, publish_date
    )


class Youtube(commands.Cog):
    def __init__(self, bot: BigBoy):
        self.bot: BigBoy = bot

    @commands.group(aliases=["yt"])
    async def youtube(self, _: commands.Context):
        """Base command for youtube."""
        ...

    @youtube.command(name="download")
    async def yt_download(self, ctx: commands.Context, *, url: str):
        """Downloads a video from a given youtube link."""
        await ctx.send("Please wait whilst I download this video.")
        async with ctx.typing():
            try:
                video = await download_video(url)
            except RegexMatchError:
                return await ctx.send("Invalid URL provided.")
            embed = discord.Embed(title=video[1], description=video[2][:250])
            embed.set_footer(text=f"{video[3]} Views")
            file = discord.File(video[0], "video.mp4")
            try:
                await ctx.reply(file=file, embed=embed)
            except discord.HTTPException:
                return await ctx.send("Sorry, that file was too large.")

    @youtube.command(name="info")
    async def yt_info(self, ctx: commands.Context, *, url: str):
        """Gets information on a given youtube video link."""
        try:
            info = await video_info(url)
        except RegexMatchError:
            return await ctx.send("Invalid URL provided.")
        embed = discord.Embed(title=info[0], description=info[1], url=info[5])
        embed.set_footer(text=f"{info[2]} views | ID: {info[6]}")
        embed.set_image(url=info[4])
        embed.set_author(name=info[3])
        embed.timestamp = info[7]
        await ctx.send(embed=embed)


def setup(bot: BigBoy):
    bot.add_cog(Youtube(bot))

import discord
from discord.ext import commands
import asyncio
import youtube_dl as yt
from urllib import request
import utils
import datetime

YOUTUBEDL_OPTIONS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist"
}

class Video:

    def __init__(self, url_or_search, requested_by):
        """Plays audio from (or searches for) a URL."""
        with yt.YoutubeDL(YOUTUBEDL_OPTIONS) as ydl:
            video = self._get_info(url_or_search)
            video_format = video["formats"][0]
            self.stream_url = video_format["url"]
            self.video_url = video["webpage_url"]
            self.title = video["title"]
            self.uploader = video["uploader"] if "uploader" in video else ""
            self.thumbnail = video["thumbnail"] if "thumbnail" in video else None
            self.requested_by = requested_by

    def _get_info(self, video_url):
        with yt.YoutubeDL(YOUTUBEDL_OPTIONS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"])  # get info for first video
            else:
                video = info
            return video

    def get_embed(self):
        """Makes an embed out of this Video's information."""
        embed = discord.Embed(title=self.title, description=self.uploader, url=self.video_url, timestamp=datetime.datetime.utcnow())
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.avatar_url)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed


class GuildState:
    """Helper class managing per-guild state."""

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.now_playing = None

    def is_requester(self, user):
        return self.now_playing.requested_by == user


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states = {}

    def get_state(self, guild):
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @commands.command(aliases=["stop", "dc"])
    @commands.guild_only()
    async def leave(self, ctx):
        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        if client and client.channel:
            await client.disconnect()
            state.playlist = []
            state.now_playing = None
        else:
            await ctx.send(":x:**I'm not currently in a voice channel**")

    @commands.command(aliases=["resume"])
    @commands.guild_only()
    @commands.check(utils.audio_playing)
    @commands.check(utils.in_voice_channel)
    async def pause(self, ctx):
        client = ctx.guild.voice_client
        self._pause_audio(client)

    def _pause_audio(self, client):
        if client.is_paused():
            client.resume()
        else:
            client.pause()

    @commands.command(aliases=["vol", "v"])
    @commands.guild_only()
    @commands.check(utils.audio_playing)
    @commands.check(utils.in_voice_channel)
    async def volume(self, ctx, volume: int):
        state = self.get_state(ctx.guild)

        # make sure volume is nonnegative
        if volume < 0:
            volume = 0
        #values have to be 0-250
        max_vol = 250
        # clamp volume to [0, 250]
        if volume > max_vol:
            volume = max_vol

        client = ctx.guild.voice_client

        state.volume = float(volume) / 100.0
        client.source.volume = state.volume  # update the AudioSource's volume to match

    @commands.command(aliases=["s"])
    @commands.guild_only()
    @commands.check(utils.audio_playing)
    @commands.check(utils.in_voice_channel)
    async def skip(self, ctx):
        await ctx.message.add_reaction("✅")
        state = self.get_state(ctx.guild)
        client = ctx.guild.voice_client
        client.stop()

    def _play_song(self, client, state, song):
        state.now_playing = song
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url), volume=state.volume)

        def after_playing(err):
            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(client, state, next_song)
            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(), self.bot.loop)

        client.play(source, after=after_playing)

    @commands.command(aliases=["np"])
    @commands.guild_only()
    @commands.check(utils.audio_playing)
    async def nowplaying(self, ctx):
        state = self.get_state(ctx.guild)
        message = await ctx.send("", embed=state.now_playing.get_embed())
        await self._add_reaction_controls(message)

    @commands.command(aliases=["q"])
    @commands.guild_only()
    @commands.check(utils.audio_playing)
    async def queue(self, ctx):
        state = self.get_state(ctx.guild)
        await ctx.send(self._queue_text(state.playlist))

    def _queue_text(self, queue):
        if len(queue) > 0:
            message = [f"{len(queue)} songs in queue:"]
            message += [
                f"  {index+1}. **{song.title}** (requested by **{song.requested_by.name}**)"
                for (index, song) in enumerate(queue)
            ]  # add individual songs
            return "\n".join(message)
        else:
            return "The play queue is empty."

    @commands.command(aliases=["cq", "clearq"])
    @commands.guild_only()
    @commands.check(utils.audio_playing)
    @commands.has_permissions(administrator=True)
    async def clearqueue(self, ctx):
        state = self.get_state(ctx.guild)
        state.playlist = []

    @commands.command(aliases=["jq"])
    @commands.guild_only()
    @commands.check(utils.audio_playing)
    @commands.has_permissions(administrator=True)
    async def jumpqueue(self, ctx, song: int, new_index: int):
        #Moves song at an index to new_index in queue
        state = self.get_state(ctx.guild)  # get state for this guild
        if 1 <= song <= len(state.playlist) and 1 <= new_index:
            song = state.playlist.pop(song-1)  # take song at index...
            state.playlist.insert(new_index-1, song)  # and insert it.

            await ctx.send(self._queue_text(state.playlist))
        else:
            await ctx.send(":x:**You must use a valid song index")

    @commands.command(aliases=["p"])
    @commands.guild_only()
    async def play(self, ctx, *, url):
        #Plays audio hosted at url or searches for url and plays first result

        client = ctx.guild.voice_client
        state = self.get_state(ctx.guild)
        await ctx.send(f"**Searching for {url} :mag:**")
        if client and client.channel:
            try:
                video = Video(url, ctx.author)
            except yt.DownloadError as e:
                self.bot.logger.warn(f"Error downloading video: {e}")
                await ctx.send("There was an error downloading your video, sorry.")
                return
            state.playlist.append(video)
            message = await ctx.send("Added to queue.", embed=video.get_embed())
            await self._add_reaction_controls(message)
        else:
            if ctx.author.voice != None and ctx.author.voice.channel != None:
                channel = ctx.author.voice.channel
                try:
                    video = Video(url, ctx.author)
                except yt.DownloadError as e:
                    await ctx.send("There was an error downloading your video, sorry.")
                    return
                client = await channel.connect()
                self._play_song(client, state, video)
                message = await ctx.send("", embed=video.get_embed())
                await self._add_reaction_controls(message)
                self.bot.logger.info(f"Now playing '{video.title}'")
            else:
                await ctx.send(":x:**You need to be in a voice channel to do that**")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        #Responds to reactions added to the bot's messages, allowing reactions to control playback
        message = reaction.message
        if user != self.bot.user and message.author == self.bot.user:
            await message.remove_reaction(reaction, user)
            if message.guild and message.guild.voice_client:
                user_in_channel = user.voice and user.voice.channel and user.voice.channel == message.guild.voice_client.channel
                permissions = message.channel.permissions_for(user)
                guild = message.guild
                state = self.get_state(guild)
                client = message.guild.voice_client
                if permissions.administrator or (user_in_channel and state.is_requester(user)):
                    if reaction.emoji == "⏯":
                        self._pause_audio(client)
                    elif reaction.emoji == "⏭":
                        client.stop()
                    elif reaction.emoji == "⏮":
                        state.playlist.insert(
                            0, state.now_playing
                        )  # insert current song at beginning of playlist
                        client.stop()
                elif reaction.emoji == "⏭"and user_in_channel and message.guild.voice_client and message.guild.voice_client.channel:
                    client.stop()

    async def _add_reaction_controls(self, message):
        CONTROLS = ["⏮", "⏯", "⏭"]
        for control in CONTROLS:
            await message.add_reaction(control)

def setup(bot):
    bot.add_cog(Music(bot))
import asyncio
import os
import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, option
from datetime import datetime
from enum import Enum
from debug import print_debug
from pydub import AudioSegment

PATH_AUDIO = "assets/sounds"
SOUND_CHECK_TIME = 5  # 300
CHANNEL_BACKUP_FILES_IS = 1099749409912266883

connections = {}
record_connections = {}


def get_audio_files():
    return [f for f in os.listdir(PATH_AUDIO) if os.path.isfile(f"{PATH_AUDIO}/{f}")]


def get_audio_duration(filepath):
    audio = AudioSegment.from_file(filepath)
    return audio.duration_seconds


def get_audio_duration(filepath):
    audio = AudioSegment.from_file(filepath)
    return audio.duration_seconds


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to play a sound
    @slash_command(
        description="Play a sound in your current voice channel",
    )
    @option(
        name="sound",
        description="The sound to play or number of the sound",
        required=True,
        autocomplete=discord.utils.basic_autocomplete(get_audio_files()),
    )
    async def play_sound(self, ctx, sound: str):
        if ctx.author.voice is None:
            await ctx.respond("You are not in a voice channel!", ephemeral=True)
            return

        # Check if the sound is a number
        if sound.isdigit():
            sound_index = int(sound)
            if sound_index < len(get_audio_files()):
                sound = get_audio_files()[sound_index]
            else:
                await ctx.respond("That sound does not exist!", ephemeral=True)
                return

        # Check if the bot is already connected to a voice channel
        if ctx.voice_client is not None:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
            vc = ctx.voice_client
        else:
            vc = await ctx.author.voice.channel.connect()

        audio_source = discord.FFmpegPCMAudio(f"{PATH_AUDIO}/{sound}")

        # Check if the bot is already playing a sound
        if vc.is_playing():
            vc.stop()
            del connections[vc]

        vc.play(
            audio_source, after=lambda e: print(f"Player error: {e}") if e else None
        )

        # Save the channel where the bot is connected
        connections[vc] = {
            "voice_channel": ctx.channel,
            "time": get_audio_duration(f"{PATH_AUDIO}/{sound}"),
            "start_time": datetime.now(),
        }

        await ctx.respond(f"Playing *{sound}*!", ephemeral=True)

    # Command to stop the bot from playing sounds
    @slash_command(description="Disconnect the bot from the voice channel")
    async def disconnect(self, ctx):
        if ctx.voice_client is None:
            await ctx.respond("The bot is not connected to a voice channel!")
            return

        await ctx.voice_client.disconnect()
        await ctx.respond("Disconnected from voice channel!", ephemeral=True)

    # Add files sounds in the server
    @slash_command(description="Add a sound to the server")
    @commands.has_permissions(administrator=True)
    @option(
        "file",
        discord.Attachment,
        description="A file to attach to the message",
        required=True,
    )
    async def add_sound(self, ctx, file: discord.Attachment):
        files_extension = [".mp3", ".wav", ".ogg"]

        if not file.filename.endswith(tuple(files_extension)):
            await ctx.respond("This is not an audio file!", ephemeral=True)
            return

        if not os.path.exists(PATH_AUDIO):
            os.makedirs(PATH_AUDIO)

        if file.filename in get_audio_files():
            await ctx.respond("This sound already exists!", ephemeral=True)
            return

        await file.save(f"{PATH_AUDIO}/{file.filename}")

        embed = discord.Embed(color=discord.Color.purple(), title="Sound added! 🎶")
        embed.add_field(name="Name", value=file.filename, inline=False)
        embed.add_field(name="Size", value=f"{file.size / 1000} KB", inline=False)
        embed.add_field(
            name="Duration",
            value=f"{round(get_audio_duration(f'{PATH_AUDIO}/{file.filename}'))} seconds",
            inline=False,
        )
        embed.add_field(
            name="Number",
            value=f"{get_audio_files().index(file.filename)}",
            inline=False,
        )
        embed.set_footer(text=f"Added by {ctx.author.name}")

        await ctx.respond(embed=embed)

        # Send file in channel backup files
        channel = self.bot.get_channel(CHANNEL_BACKUP_FILES_IS)
        await channel.send(file=discord.File(f"{PATH_AUDIO}/{file.filename}"))

    # Remove files sounds in the server
    @slash_command(description="Remove a sound from the server")
    @commands.has_permissions(administrator=True)
    @option(
        name="sound",
        description="The sound to play",
        required=True,
        autocomplete=discord.utils.basic_autocomplete(get_audio_files()),
    )
    async def remove_sound(self, ctx, sound: str):
        if sound not in get_audio_files():
            await ctx.respond("This sound does not exist!", ephemeral=True)
            return

        os.remove(f"{PATH_AUDIO}/{sound}")
        await ctx.respond(f"Removed '{sound}' from the server!", ephemeral=True)

    # Gets the list of sounds
    @slash_command(description="Get the list of sounds")
    async def get_sounds(self, ctx):
        # Create tuple number and sound
        sounds = [(i, sound) for i, sound in enumerate(get_audio_files())]

        embed = discord.Embed(
            color=discord.Color.purple(),
            title="Sounds that exist!🎶",
            description="\n".join(
                [f"{i}. {sound[1]}" for i, sound in enumerate(sounds)]
            ),
        )
        await ctx.respond(embed=embed, ephemeral=True)

    # Change the name of a sound
    @slash_command(description="Change the name of a sound")
    @commands.has_permissions(administrator=True)
    @option(
        name="sound",
        description="The sound to change the name",
        required=True,
        autocomplete=discord.utils.basic_autocomplete(get_audio_files()),
    )
    @option(
        name="new_name",
        description="The new name of the sound",
        required=True,
    )
    async def change_sound_name(self, ctx, sound: str, new_name: str):
        if sound not in get_audio_files():
            await ctx.respond("This sound does not exist!", ephemeral=True)
            return

        os.rename(f"{PATH_AUDIO}/{sound}", f"{PATH_AUDIO}/{new_name}")
        await ctx.respond(f"Changed the name of '{sound}' to '{new_name}'!")

    @tasks.loop(seconds=SOUND_CHECK_TIME)
    async def check_sounds(self):
        if not connections:
            return

        for guild in self.bot.guilds:
            if guild.voice_client is not None:
                connection = connections[guild.voice_client]
                if (datetime.now() - connection["start_time"]).seconds >= connection[
                    "time"
                ]:
                    await guild.voice_client.disconnect()
                    embed = discord.Embed(
                        color=discord.Color.purple(),
                        title="Sound finished playing",
                        description=f"I left the voice channel *{connection['voice_channel'].name}* because the sound finished playing.",
                    )
                    await connection["voice_channel"].send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_sounds.start()
        print_debug("Initialized voice sounds loop")


def setup(bot):
    bot.add_cog(Voice(bot))

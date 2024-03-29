import json
import sys
import discord
import os
import socket
from discord.ext import commands, tasks
from discord.commands import slash_command, option
from debug import print_debug
from random import randint
from datetime import datetime, timedelta
from time import sleep

MIN_SIZE_DICK = 0
MAX_SIZE_DICK = 25

ID_TEMP_CHANNEL = 1030927721682960505
ID_GENERAL_CHANNEL = 718460119993548804
TEMP_DELAY = 120.0  # Seconds

# Read the password in config.json
if os.path.exists(os.getcwd() + "/config.json"):
    with open(os.getcwd() + "/config.json", "r") as f:
        config = json.load(f)
    PASSWORD = config["PASSWORD"]

photo_finish_channels = []


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="pong 🏓")
    async def ping(self, ctx):
        await ctx.respond("Pong 🏓")
        print_debug(f"{ctx.author.name} ha usado /ping")

    @slash_command(description="El bot te saluda.")
    async def hello(self, ctx):
        await ctx.respond(f"Hi {ctx.author.mention}, I'm {self.bot.user.name}!")
        print_debug(f"{ctx.author.name} ha usado /hello")

    @slash_command(description="Cuanto mide tu pinga?")
    @option("member", description="A quien quieres medirle la pinga?")
    async def dick(self, ctx, member: discord.Member):
        await ctx.respond(
            f"{member.mention} has a 8{'='*randint(MIN_SIZE_DICK,MAX_SIZE_DICK)}D"
        )
        print_debug(f"{ctx.author.name} ha usado \dick")

    @slash_command(description="Quien será el último en irse?")
    async def photo_finish(self, ctx):
        voice = ctx.author.voice
        if voice is None:
            await ctx.respond(
                "Debes estar en un canal de voz para usar este comando.", ephemeral=True
            )
            return

        if len(voice.channel.members) < 2:
            await ctx.respond(
                "Debes estar en un canal de voz con al menos 2 personas para usar este comando.",
                ephemeral=True,
            )
            return

        if voice.channel in [
            channel["voice_channel"] for channel in photo_finish_channels
        ]:
            await ctx.respond(
                "Ya hay una photo finish activada en este canal de voz 😏",
                ephemeral=True,
            )
            return

        photo_finish_channels.append(
            {
                "voice_channel": voice.channel,
                "members": voice.channel.members,
                "author": ctx.author,
                "channel_id": ctx.channel.id,
                "start_time": datetime.now(),
            }
        )
        await ctx.respond("Photo finish activada!", ephemeral=True)

    @slash_command(description="Mensajes a limpiar")
    @option("number", description="Número de mensajes a limpiar")
    async def clear(self, ctx, number: int):
        """Clear messages from a channel"""

        if number > 100:
            await ctx.respond("No puedes borrar mas de 100 mensajes", ephemeral=True)
            print_debug(f"{ctx.author.name} no ha podido usar /clear")
            return
        if number < 0:
            await ctx.respond(
                "No puedes borrar menos de 0 mensajes subnormal", ephemeral=True
            )
            print_debug(f"{ctx.author.name} no ha podido usar /clear")
            return
        if number == 0:
            await ctx.respond("No puedes borrar 0 mensajes", ephemeral=True)
            print_debug(f"{ctx.author.name} no ha podido usar /clear")
            return

        await ctx.defer()
        await ctx.channel.purge(limit=number + 1)
        await ctx.send(f"`Se han borrado {number} mensajes 🧼`", delete_after=1.5)
        print_debug(f"{ctx.author.name} ha usado /clear")

    # Reboot bot
    @slash_command(description="Reinicia el bot")
    @commands.has_permissions(administrator=True)
    async def reboot(self, ctx):
        if ctx.guild is None:
            await ctx.respond("This command only works in servers", ephemeral=True)
            return
        await ctx.respond("Reiniciando...", ephemeral=True)
        os.execl(sys.executable, sys.executable, *sys.argv)

    # My IP address
    @slash_command(description="Muestra la IP del servidor")
    @commands.has_permissions(administrator=True)
    async def ip(self, ctx, password):
        if password != PASSWORD:
            await ctx.respond("Wrong password! 🎃", ephemeral=True)
            return
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            await ctx.respond(f"IP: {s.getsockname()[0]}", ephemeral=True)

    # Command in shell
    @slash_command(description="Run a command in shell")
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, *, command, password):
        if password != PASSWORD:
            await ctx.respond("Wrong password! 🎃", ephemeral=True)
            return

        # Output in menssage
        await ctx.respond(f"```{os.popen(command).read()}```")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id != ID_TEMP_CHANNEL:
            return
        await message.delete(delay=TEMP_DELAY)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not photo_finish_channels:
            return

        if before.channel == after.channel:
            return

        for i, channel in enumerate(photo_finish_channels):
            # Add member to "game"
            if after.channel == channel["voice_channel"]:
                if member not in channel["members"]:
                    photo_finish_channels[i]["members"].append(member)

            # Remove member from "game"
            if before.channel == channel["voice_channel"]:
                embed = discord.Embed(
                    color=discord.Colour.purple(),
                    title="Photo Finish 📸",
                    description="El último en irse será el perdedor!",
                )

                if not len(before.channel.members):
                    position = "Último 🤡"
                    photo_finish_channels.remove(channel)
                else:
                    position = len(channel["members"]) - len(before.channel.members)

                embed.add_field(name="Miembro", value=member.mention, inline=True)
                embed.add_field(name="Posición", value=position, inline=True)
                embed.add_field(
                    name="Time",
                    value=timedelta(
                        seconds=(datetime.now() - channel["start_time"]).total_seconds()
                    ),
                    inline=True,
                )
                embed.set_footer(
                    text=f"Created: {channel['start_time'].strftime('%d/%m/%Y %H:%M:%S')}\nBy: {channel['author'].name} - {before.channel.name}"
                )
                embed.set_thumbnail(url=member.display_avatar.url)

                channel = await member.guild.fetch_channel(channel["channel_id"])
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))

import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, option
from debug import print_debug
from random import randint
from datetime import datetime

MIN_SIZE_DICK = 0
MAX_SIZE_DICK = 25

ID_TEMP_CHANNEL = "1030927721682960505"
TEMP_DELAY = 60.0  # Seconds


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

    # @slash_command(description="Cambiar la actividad del bot.")
    # async def set_activity(
    #    self, ctx, typ: Option(str, choices=["game", "stream"]), name: Option(str)
    # ):
    #    if typ == "game":
    #        act = discord.Game(name=name)
    #    elif type == "stream":
    #        act = discord.Streaming(name=name, url="https://twitch.tv/")
    #
    #    await self.bot.change_presence(activity=act, status=discord.Status.online)

    @slash_command(description="Cuanto mide tu pinga?")
    @option("member", description="A quien quieres medirle la pinga?")
    async def dick(self, ctx, member: discord.Member):
        await ctx.respond(
            f"{member.mention} has a 8{'='*randint(MIN_SIZE_DICK,MAX_SIZE_DICK)}D"
        )
        print_debug(f"{ctx.author.name} ha usado \dick")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id != ID_TEMP_CHANNEL:
            return
        message.delete(delelete_after=TEMP_DELAY)
        print_debug(f"Mensaje de temp borrado: {message.content}")

def setup(bot):
    bot.add_cog(Misc(bot))

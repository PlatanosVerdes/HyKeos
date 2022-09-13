from discord.ext import commands
from discord.commands import slash_command
from debug import print_debug


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


def setup(bot):
    bot.add_cog(Misc(bot))

import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, option
from debug import print_debug
from random import randint
from datetime import datetime

MIN_SIZE_DICK = 0
MAX_SIZE_DICK = 25

ID_TEMP_CHANNEL = 1030927721682960505
TEMP_DELAY = 120.0  # Seconds

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

    @slash_command(description="Quien será el último en irse?")
    async def photo_finish(self, ctx):

        voice = ctx.author.voice
        if voice is None:
            await ctx.respond(
                "Debes estar en un canal de voz para usar este comando.", ephemeral=True
            )
            return
        
        if voice.channel.members < 2:
            await ctx.respond(
                "Debes estar en un canal de voz con al menos 2 personas para usar este comando.", ephemeral=True
            )
            return

        photo_finish_channels.append(
            {
                "voice_channel": voice.channel,
                "members": voice.channel.members,
                "author": ctx.author,
            }
        )
        await ctx.respond("Photo finish activada!", ephemeral=True)

    @slash_command(description="Mensajes a limpiar")
    @option("number", description="Número de mensajes a limpiar")
    async def clear(self, ctx, number: int):
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
        await ctx.channel.purge(limit=number)
        await ctx.send(f"`Se han borrado {number} mensajes 🧼`", delete_after=1.5)
        print_debug(f"{ctx.author.name} ha usado /clear")

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

        for channel in photo_finish_channels:
            if before.channel is None:
                return
            
            if before.channel == channel["voice_channel"]:
                embed = discord.Embed(
                        color=discord.Colour.purple(),
                        title="Photo Finish 📸",
                    )
                
                if not len(before.channel.members):
                    dm_channel = member.dm_channel or await member.create_dm()
                    
                    embed.add_field(name='Canal de voz', value=before.channel.mention, inline=False)
                    embed.add_field(name='Posición', value="Último 🤡", inline=False)
                    embed.add_field(name='Autor', value=channel['author'].mention, inline=False)

                    photo_finish_channels.remove(channel)
                else:
                    
                    embed.add_field(name='Canal de voz', value=before.channel.mention, inline=False)
                    embed.add_field(name='Posición', value=channel['members'] - len(before.channel.members), inline=False)
                    embed.add_field(name='Autor', value=channel['author'].mention, inline=False)

                dm_channel = member.dm_channel or await member.create_dm()
                await dm_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
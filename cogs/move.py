import discord
from discord.commands import slash_command, option
from discord.ext import commands
from debug import print_debug

CINEMA_CHANNEL_ID = 974351272285204490
NAME_SUPORT_ADMIN = "Suport Admin 😎"


class Moves(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Todos al cine! 🎞")
    async def move_to_cinema(self, ctx):
        current_channel = ctx.author.voice.channel
        if current_channel is None:
            await ctx.respond(
                f"{ctx.author.mention} No estas en un canal de voz.", ephemeral=True
            )
            return

        role_cinema = discord.utils.get(ctx.guild.roles, name="Cineasta")
        if not (
            (ctx.author.guild_permissions.administrator)
            or (role_cinema in [role for role in ctx.author.roles])
        ):
            await ctx.respond(
                f"{ctx.author.mention} No tienes permisos", ephemeral=True
            )
            print_debug(
                f"{ctx.author.name} ha usado /move_to_cinema pero no tiene permisos"
            )
            return

        voice_channel = discord.utils.get(
            ctx.guild.voice_channels, id=CINEMA_CHANNEL_ID
        )
        for member in current_channel.members:
            await member.move_to(voice_channel)
        await ctx.respond(
            f"{ctx.author.mention} Todos los miembros han sido movidos a {voice_channel.name}",
            delay=5.0,
        )
        print_debug(
            f"{ctx.author.name} ha usado /move_to_cinema y ha movido a todos a {voice_channel.name}"
        )

    @slash_command(description="Mueve a todos a un canal 📦")
    @option("canal", description="Canal al que quieras mover a todos los conectados")
    async def move_to(self, ctx, voice_channel: discord.VoiceChannel):
        current_channel = ctx.author.voice.channel
        if current_channel is None:
            await ctx.respond(
                f"{ctx.author.mention} No estas en un canal de voz.", ephemeral=True
            )
            print_debug(
                f"{ctx.author.name} ha usado /move_to pero no esta en un canal de voz"
            )
            return

        if not (
            (ctx.author.guild_permissions.administrator)
            or (NAME_SUPORT_ADMIN in [role.name for role in ctx.author.roles])
        ):
            await ctx.respond(
                f"{ctx.author.mention} No tienes los roles para mover a la gente",
                ephemeral=True,
            )
            print_debug(f"{ctx.author.name} ha usado /move_to pero no tiene permisos")
            return

        for member in current_channel.members:
            await member.move_to(voice_channel)
        await ctx.respond(
            f"{ctx.author.mention} has movido a todos a {voice_channel.name}",
            ephemeral=True,
        )
        print_debug(
            f"{ctx.author.name} ha usado /move_to y ha movido a todos a {voice_channel.name}"
        )


def setup(bot):
    bot.add_cog(Moves(bot))

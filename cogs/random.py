import discord
from discord.ext import commands
from discord.commands import slash_command
from random import randint, choice
from debug import print_debug


class Randoms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Te gusta jugar? 🎲 Este es tu juego! Prueba suerte! 🎰")
    async def rnd(self, ctx):
        if randint(0, 1):
            await ctx.respond(f"{ctx.author.mention} Ha muerto 💀")
            await ctx.guild.kick(ctx.author)
            print_debug(f"{ctx.author.name} ha usado /rnd y ha muerto")
        else:
            await ctx.author.add_roles(
                discord.utils.get(ctx.guild.roles, name="Vencio a la muerte"),
                atomic=True,
            )
            await ctx.respond(f"{ctx.author.mention} Has tenido suerte 🌟")
            print_debug(f"{ctx.author.name} ha usado /rnd y ha tenido suerte")

    @slash_command(
        description="Te gusta jugar pero le temes a la muerte porque tienes 💩? Prueba suerte con este juego! 🎰"
    )
    async def rnd_easy(self, ctx):
        if randint(0, 1):
            await ctx.author.move_to(None)
            await ctx.respond(f"{ctx.author.mention} A la calle 🚴")
            print_debug(
                f"{ctx.author.name} ha usado /rnd_easy y ha sido movido a la calle"
            )
        else:
            await ctx.respond(f"{ctx.author.mention} Has tenido suerte 🌟")
            print_debug(f"{ctx.author.name} ha usado /rnd_easy y ha tenido suerte")

    @slash_command(description="Alguno del canal os movereis a un lugar aleatorio 🏃")
    async def rnd_move_someone(self, ctx):
        current_channel = ctx.author.voice.channel
        if current_channel is None:
            await ctx.respond(
                f"{ctx.author.mention} No estas en un canal de voz.", ephemeral=True
            )
            print_debug(
                f"{ctx.author.name} ha usado /rnd_move_someone pero no esta en un canal de voz"
            )
            return

        member = choice(current_channel.members)
        voice_channel = choice(ctx.guild.voice_channels)

        await member.move_to(voice_channel)
        await ctx.respond(f"{member.mention} ha sido movido a {voice_channel.name}")
        print_debug(
            f"{ctx.author.name} ha usado /rnd_move_someone y ha movido a {member.name} a {voice_channel.name}"
        )


def setup(bot):
    bot.add_cog(Randoms(bot))

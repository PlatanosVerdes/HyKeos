import discord
from discord import option, Colour
from discord.commands import Option
import random
from random import randint

TOKEN = 'OTQzODI0NDg0NTEzNzUxMDYy.Yg4rDA.p60NNYyoKLvPZrXovh6yy5EIE-g'
ID_GUIRIS = 718460119993548800
ID_ADMIN = 588492819606405133

bot = discord.Bot(debug_guilds=[ID_GUIRIS])

# METHODS
@bot.slash_command(description='pong 🏓')
async def ping(ctx):
    await ctx.respond('Pong 🏓')

@bot.slash_command(description='El bot te saluda.')
async def hello(ctx):
    await ctx.respond(f'Hi {ctx.author.mention}, I\'m {bot.user.name}!')


@bot.slash_command(description='Te gusta jugar? 🎲 Este es tu juego! Prueba suerte! 🎰')
async def rnd(ctx):
    if randint(0, 1):
        await ctx.respond(f'{ctx.author.mention} Ha muerto 💀')
        await ctx.guild.kick(ctx.author)
    else:
        await ctx.respond(f'{ctx.author.mention} Has tenido suerte 🌟')


@bot.slash_command(description='Para ver todos los roles 👀')
async def roles(ctx):
    roles = ctx.guild.roles
    embed = discord.Embed(color=Colour.purple(), title='Roles',
                          description='\n'.join(f'`{role.name}`' for role in roles))
    await ctx.respond(embed=embed)


@bot.slash_command(description='Pide un rol al admin 🙋🏻‍♂️')
@option("rol", description="Rol que solicitas")
@option("motivo", description="Escribe una breve descripción argumentando tu petición")
async def pls_rol(ctx, rol: str, descripcion: str):
    roles = ctx.guild.roles
    if any(rol.lower() == role.name.lower() for role in roles):
        ID_CHANNEL = 982345257142325269
        embed = discord.Embed(color=discord.Colour.purple(), title='Petición de Rol de:\n`{}`'.format(ctx.author),
                              description=f'Rol: `{rol}`\n Motivo: `{descripcion}`')
        request = await ctx.guild.get_channel(ID_CHANNEL).send(embed=embed)
        await request.add_reaction('✅')
        await request.add_reaction('❌')
        await ctx.respond(f'Petición enviada correctamente ✅', ephemeral=True)
    else:
        await ctx.respond(f'No se ha encontradom el rol `{rol}`...😔', ephemeral=True)


@bot.slash_command(description='Abre una votación 📩 con ✅ y ❌')
@option("propuesta", description="Tema de votación")
async def vote(ctx, propuesta: str):
    embed = discord.Embed(color=discord.Colour.purple(), title='Votación Abierta\n',
                              description=f'{propuesta}\n\n📩 By: {ctx.author}')
    request = await ctx.guild.get_channel(ctx.channel.id).send(embed=embed)
    await request.add_reaction('✅')
    await request.add_reaction('❌')

    await ctx.respond(f'Votación realizada! 🎉', ephemeral=True)

@bot.slash_command(description='Abre una votación 📩 con reacciones personalizadas 🎨')
@option("propuesta", description="Tema de votación")
@option("reaccion 1", description="Pon la primer reacción")
@option("reaccion 2", description="Pon la segunda reacción")
async def vote_reacts(ctx, propuesta: str, react1: str, react2: str):
    embed = discord.Embed(color=discord.Colour.purple(), title='Votación Abierta\n',
                              description=f'{propuesta}\n\n📩 By: {ctx.author}')
    request = await ctx.guild.get_channel(ctx.channel.id).send(embed=embed)
    await request.add_reaction(react1)
    await request.add_reaction(react2)

    await ctx.respond(f'Votación realizada! 🎉', ephemeral=True)

# EVENTS
@bot.event
async def on_ready():
    print("Bot is Ready, lets go!")

bot.run(TOKEN)
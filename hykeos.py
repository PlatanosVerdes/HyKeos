import discord
import random
from random import randint 

TOKEN = 'OTQzODI0NDg0NTEzNzUxMDYy.Yg4rDA.p60NNYyoKLvPZrXovh6yy5EIE-g'
ID_GUIRIS= 718460119993548800
ID_ADMIN= 588492819606405133

bot = discord.Bot(debug_guilds=[ID_GUIRIS])

#METHODS
@bot.slash_command(description='pong 🏓')
async def ping(ctx):
    await ctx.respond('pong')

@bot.slash_command(description='El bot te saluda.')
async def hello(ctx):
    await ctx.respond(f'Hi {ctx.author.mention}, I\'m {bot.user.name}!')

@bot.slash_command(description='Prueba suerte para ser tu propio jefe.')
async def rnd(ctx):
    if randint(0,1):
        await ctx.respond(f'{ctx.author.mention} Has muerto')
        await ctx.guild.kick(ctx.author) 
    else:
        await ctx.respond(f'{ctx.author.mention} Has tenido suerte')

@bot.slash_command(description='Para ver todos los roles')
async def rols(ctx):
        await ctx.respond(f'Pendiente...')

@bot.slash_command(description='Pide un rol al admin.')
async def pls_rol(ctx):
        ID_CHANNEL = 982345257142325269
        chan = bot.get_channel(ID_CHANNEL)
        #await ctx.respond(f'{rol}!')
        await chan.send(f'Hi')
        

#EVENTS
@bot.event
async def on_ready():
    print("Bot is Ready, lets go!")
    
bot.run(TOKEN)
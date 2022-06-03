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
        

#EVENTS
@bot.event
async def on_ready():
    print("Bot is Ready, lets go!")
    
bot.run(TOKEN)
from multiprocessing.connection import Client
import discord
from discord.ext import commands
import random              
from random import randint 


TOKEN = 'OTQzODI0NDg0NTEzNzUxMDYy.Yg4rDA.p60NNYyoKLvPZrXovh6yy5EIE-g'

#Invite: https://discord.com/api/oauth2/authorize?client_id=943824484513751062&permissions=8&scope=bot

PREFIX = '^'

bot = commands.Bot(command_prefix=PREFIX,description="This is a helper bot")

#METHODS
@bot.command()
#ctx is a context
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def on_message(message):
    isExit = randint(0,1)
    if isExit:
        #Client.kick(member)
        await ctx.send('Muerto')
    else:
        await ctx.send('Has tenido suerte')



#EVENTS
@bot.event
async def on_guild_integrations_update():
    print("Bot is Ready, lets go!")
    
bot.run(TOKEN)

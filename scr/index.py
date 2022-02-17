import discord
from discord.ext import commands

#Invite: https://discord.com/api/oauth2/authorize?client_id=943824484513751062&permissions=8&scope=bot

PREFIX = '^'
TOKEN = 'OTQzODI0NDg0NTEzNzUxMDYy.Yg4rDA.p60NNYyoKLvPZrXovh6yy5EIE-g'

bot = commands.Bot(command_prefix=PREFIX,description="This is a helper bot")

#METHODS
@bot.command()
#ctx is a context
async def ping(ctx):
    await ctx.send('pong')

#EVENTS
@bot.event()
async def on_ready():
    print('Bot is ready')
    
bot.run(TOKEN)

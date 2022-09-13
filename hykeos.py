import discord
import os
import json
from discord.ext import commands
from debug import print_debug


# Local variables
if os.path.exists(os.getcwd() + "/config.json"):
    with open(os.getcwd() + "/config.json", "r") as f:
        config = json.load(f)
    TOKEN = config["TOKEN"]
    ID_GUIRIS = config["ID_GUIRIS"]
else:
    # Create config.json
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump({"TOKEN": "", "ID_GUIRIS": ""}, f)

    # Si no existe el archivo de configuración, se utilizaran las variables de entorno -> Heroku
    TOKEN = os.getenv("TOKEN")
    ID_GUIRIS = os.getenv("ID_GUIRIS")  # ID del server de 'guiris'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(debug_guilds=[ID_GUIRIS], intents=intents)

@bot.event
async def on_ready():
    print("Bot is Ready, lets go!")    


# Add cogs
cogfiles = [
    f"cogs.{filename[:-3]}"
    for filename in os.listdir("./cogs")
    if filename.endswith(".py")
]

print_debug(f"Loading cogs: {cogfiles}")
for cogfile in cogfiles:
    bot.load_extension(cogfile)
    try:
        bot.load_extension(cogfile)
    except Exception as err:
        print(err) 
print_debug("Cogs loaded")


bot.run(TOKEN)
# member = discord.utils.get(message.guild.members, name='Foo')

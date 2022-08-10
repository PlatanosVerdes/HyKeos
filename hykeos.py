import discord
from discord import Colour
from discord.commands import option
from random import randint
from datetime import datetime
import os
from discord.ext import commands

TOKEN = 'OTQzODI0NDg0NTEzNzUxMDYy.Yg4rDA.p60NNYyoKLvPZrXovh6yy5EIE-g'
ID_GUIRIS = 718460119993548800
ID_ADMIN = 588492819606405133

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(debug_guilds=[ID_GUIRIS], intents=intents)


ROLE_CHANNEL_ID = 982345257142325269
FOOD_CHANNEL_ID = 975135205692149801
REFORMATORY_CHANNEL_ID = 985583574021443584

ONE_STAR_REACTION_ID = 982649189383151636
TWO_STAR_REACTION_ID = 982649186942087188
THREE_STAR_REACTION_ID = 982649184362590358

TOPS = (3, 5, 10)

# -------------------------------
# CLASSES
# -------------------------------


class Month:
    months = ('Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre')

    def get_month(month: str):
        for i in range(len(Month.months)):
            if month.lower() == Month.months[i].lower():
                return i + 1
        return -1


class FoodPlayer:
    one_stars_value = 1
    two_stars_value = 2
    three_stars_value = 3

    def __init__(self, member, one_stars=0, two_stars=0, three_stars=0, n_foods=0):
        self.member = member
        self.one_stars = one_stars
        self.two_stars = two_stars
        self.three_stars = three_stars
        self.n_foods = n_foods

    def get_points(self):
        return self.one_stars_value * self.one_stars + self.two_stars_value * self.two_stars + self.three_stars_value * self.three_stars

    def get_mean_points(self):
        return 0 if self.n_foods == 0 else round(self.get_points() / self.n_foods, 2)


class PlsRoleView(discord.ui.View):

    def __init__(self, rol_name, reason):
        super().__init__()
        self.rol_name = rol_name
        self.reason = reason

    @discord.ui.button(label="Aceptar", row=0, style=discord.ButtonStyle.success)
    async def first_button_callback(self, button, interaction):

        await interaction.user.add_roles([rol for rol in bot.guilds[0].roles if rol.name == self.rol_name][0], atomic=True)
        await interaction.response.send_message("Aceptada")

    @discord.ui.button(label="Rechazar", row=0, style=discord.ButtonStyle.danger)
    async def second_button_callback(self, button, interaction):
        await interaction.user.send(f'Se ha rechazado tu solicitud de ser {self.rol_name}')
        await interaction.response.send_message("Rechazada")

# -------------------------------
# METHODS
# -------------------------------


def ranking_icon(rank):
    if rank == 1:
        return '🥇'
    if rank == 2:
        return '🥈'
    if rank == 3:
        return '🥉'
    return '👤'

# -------------------------------
# GETTERS for AutoComplete
# -------------------------------
async def get_roles(ctx: discord.AutocompleteContext):
    return [rol.name for rol in bot.guilds[0].roles]

async def get_months(ctx: discord.AutocompleteContext):
    return [month for month in Month.months if month.startswith(ctx.value.lower())]


# -------------------------------
# COMMANDS
# -------------------------------


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
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Vencio a la muerte'), atomic=True)
        await ctx.respond(f'{ctx.author.mention} Has tenido suerte 🌟')


@bot.slash_command(description='Te gusta jugar pero le temes a la muerte porque tienes 💩? Prueba suerte con este juego! 🎰')
async def rnd_easy(ctx):
    if randint(0, 1):
        await ctx.author.move_to(None)
        await ctx.respond(f'{ctx.author.mention} A la calle 🚴')
    else:
        await ctx.respond(f'{ctx.author.mention} Has tenido suerte 🌟')


@bot.slash_command(description='Para ver todos los roles 👀')
async def roles(ctx):
    roles = ctx.guild.roles
    embed = discord.Embed(color=Colour.purple(), title='Roles',
                          description='\n'.join(f'`{role.name}`' for role in roles))
    await ctx.respond(embed=embed)


@bot.slash_command(description='Al reformatorio! ⛓. Debe de existir el canal con el nombre: ⛓ Reformatorio ⛓')
@option("member", description="Quien se ha portado mal? 🤔")
async def reformatory(ctx, *, member: discord.Member):
    # Mirar si tiene el rol de reformatorio
    # not ctx.author.guild_permissions.administrator or
    if ctx.author.get_role(REFORMATORY_CHANNEL_ID) == None:
        await ctx.respond(f'{ctx.author.mention} No tienes permisos para hacer eso! 🤔')
    else:
        name_channel = "⛓ Reformatorio ⛓"
        voice_channels = ctx.guild.voice_channels
        channel = discord.utils.get(voice_channels, name=name_channel)
        if channel == None:
            await ctx.respond(f'No existe el canal {name_channel}', ephemeral=True)
        else:
            await member.move_to(channel)
            await ctx.respond(f'{member.mention} se ha movido al canal {name_channel} se ha portado mal 😡')


@bot.slash_command(description='Pide un rol al admin 🙋🏻‍♂️')
@option("rol", description="Rol que solicitas", autocomplete=get_roles)
@option("motivo", description="Escribe una breve descripción argumentando tu petición")
async def pls_rol(ctx, rol: str, reason: str):
    roles = ctx.guild.roles
    if any(rol.lower() == role.name.lower() for role in roles):
        embed = discord.Embed(color=discord.Colour.purple(), title='Petición de Rol de:\n`{}`'.format(ctx.author),
                              description=f'Rol: `{rol}`\n Motivo: `{reason}`')
        await ctx.guild.get_channel(ROLE_CHANNEL_ID).send(embed=embed, view=PlsRoleView(rol, reason))
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
async def vote_custom(ctx, propuesta: str, react1: str, react2: str):
    embed = discord.Embed(color=discord.Colour.purple(), title='Votación Abierta\n',
                          description=f'{propuesta}\n\n📩 By: {ctx.author}')
    request = await ctx.guild.get_channel(ctx.channel.id).send(embed=embed)
    await request.add_reaction(react1)
    await request.add_reaction(react2)

    await ctx.respond(f'Votación realizada! 🎉', ephemeral=True)


@bot.slash_command(description='Top 10 mejores comidas 🍽')
async def food_ratings(ctx):

    async with ctx.channel.typing():

        members = [member for member in ctx.guild.members if not member.bot]
        players = [FoodPlayer(member) for member in members]

        channel = ctx.guild.get_channel(FOOD_CHANNEL_ID)
        one_stars = await ctx.guild.fetch_emoji(ONE_STAR_REACTION_ID)
        two_stars = await ctx.guild.fetch_emoji(TWO_STAR_REACTION_ID)
        three_stars = await ctx.guild.fetch_emoji(THREE_STAR_REACTION_ID)

        await ctx.defer()
        async for message in channel.history(limit=None):

            if message.attachments == []:
                continue  # No Imagenes
            if message.reactions == []:
                continue    # No reacciones

            players[members.index(message.author)].n_foods += 1

            for reaction in message.reactions:
                if reaction.emoji == one_stars:
                    players[members.index(message.author)
                            ].one_stars += reaction.count
                elif reaction.emoji == two_stars:
                    players[members.index(message.author)
                            ].two_stars += reaction.count
                elif reaction.emoji == three_stars:
                    players[members.index(message.author)
                            ].three_stars += reaction.count

        players.sort(key=FoodPlayer.get_points, reverse=True)
        embed = discord.Embed(color=Colour.purple(), title='Top 10 Mejores Comidas 🍽',
                              description='\n'.join(
            f'`{ranking_icon(player_rank+1)} {player.member.name} - {player.get_points()} puntos`' for player_rank, player in enumerate(players[:10])))
        #f'`{ranking_icon(player_rank+1)} {player.member.name} - {player.get_points()} puntos`\n `   {player.n_foods} comidas - {player.get_mean_points()}`'
        # for player_rank, player in enumerate(players[:10])))
        await ctx.respond(embed=embed)

@bot.slash_command(description='Top Comidas 🍽: Elige top y mes 🍴')
@option("top", description="Top que deseas consultar",  autocomplete=discord.utils.basic_autocomplete(TOPS))
@option("month", description="Mes que desas consultar", autocomplete=get_months)
async def food_ratings_custom(ctx, top: int, month: str):
    n_month = Month.get_month(month)

    if n_month == -1:
        await ctx.respond(f'El mes {month} no existe...', ephemeral=True)
        return

    async with ctx.channel.typing():
        date_limit_up = datetime(datetime.today().year, n_month, 1)
        date_limit_down = datetime(datetime.today().year, n_month+1, 1)

        members = [member for member in ctx.guild.members if not member.bot]
        players = [FoodPlayer(member) for member in members]

        channel = ctx.guild.get_channel(FOOD_CHANNEL_ID)
        one_stars = await ctx.guild.fetch_emoji(ONE_STAR_REACTION_ID)
        two_stars = await ctx.guild.fetch_emoji(TWO_STAR_REACTION_ID)
        three_stars = await ctx.guild.fetch_emoji(THREE_STAR_REACTION_ID)

        async for message in channel.history(before=date_limit_down, after=date_limit_up):
            if message.attachments == []:
                continue  # No Imagenes
            if message.reactions == []:
                continue    # No reacciones

            players[members.index(message.author)].n_foods += 1

            for reaction in message.reactions:
                if reaction.emoji == one_stars:
                    players[members.index(message.author)
                            ].one_stars += reaction.count
                elif reaction.emoji == two_stars:
                    players[members.index(message.author)
                            ].two_stars += reaction.count
                elif reaction.emoji == three_stars:
                    players[members.index(message.author)
                            ].three_stars += reaction.count

        players.sort(key=FoodPlayer.get_points, reverse=True)
        embed = discord.Embed(color=Colour.purple(), title=f'Top {top} Mejores Comidas de {Month.months[n_month-1]} 📅',
                              description='\n'.join(f'`{ranking_icon(player_rank+1)} {player.member.name} - {player.get_points()} puntos`' for player_rank, player in enumerate(players[:top])))
        await ctx.respond(embed=embed)


async def set_food_rating(message, id_channel):
    if message.attachments == []:
        return
    # Verificar que el mensaje es una imagen
    if message.channel.id == id_channel:
        _, file_extension = os.path.splitext(
            message.attachments[0].filename)

        if file_extension == '.png' or file_extension == '.jpg' or file_extension == '.jpeg':
            await message.add_reaction(f'<:one_stars:{ONE_STAR_REACTION_ID}>')
            await message.add_reaction(f'<:two_stars:{TWO_STAR_REACTION_ID}>')
            await message.add_reaction(f'<:three_stars:{THREE_STAR_REACTION_ID}>')

# -------------------------------
# EVENTS
# -------------------------------


@bot.event
async def on_ready():
    print("Bot is Ready, lets go!")


@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return

    # Food Rating
    await set_food_rating(message, FOOD_CHANNEL_ID)


bot.run(TOKEN)
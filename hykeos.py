import discord
import os
from discord import Colour
from discord.commands import option
from random import randint, randrange, choice, shuffle, sample
from datetime import datetime, timedelta
from discord.ext import tasks

# REFORMATORY
reformatory_cells = []
REFORMATORY_CHECK_TIME = 2
MIN_TIME_REFORMATORY = 10
MAX_TIME_REFORMATORY = 60

# VOTES
VOTES_CHECK_TIME = 5
votes = []
roles_temp = []

# Russian Roulettes
countdown_roulette = []
COUNTDOWN_RROULETTE = 15

# DEBUG stuff
DEBUG = True


def print_debug(message):
    if DEBUG:
        print(f"[{str(datetime.now()).split(' ')[1]} - DEBUG] {message}")
    return


TOKEN = 'OTQzODI0NDg0NTEzNzUxMDYy.Yg4rDA.p60NNYyoKLvPZrXovh6yy5EIE-g'
ID_GUIRIS = 718460119993548800  # ID del server de 'guiris'

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(debug_guilds=[ID_GUIRIS], intents=intents)

ROLE_CHANNEL_ID = 982345257142325269
FOOD_CHANNEL_ID = 975135205692149801
REFORMATORY_CHANNEL_ID = 985583574021443584
CINEMA_CHANNEL_ID = 974351272285204490

ONE_STAR_REACTION_ID = 982649189383151636
TWO_STAR_REACTION_ID = 982649186942087188
THREE_STAR_REACTION_ID = 982649184362590358

TOPS = (3, 5, 10)
MONTHS = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
TIMES = ("Dias", "Horas", "Minutos")

NAME_SUPORT_ADMIN = 'Suport Admin 😎'

# -------------------------------
# CLASSES
# -------------------------------


class RRoulette:
    revolvers = [["Nagant M1895", 7], ["Swiss Mini Gun C1ST", 6],
                 ["Remington Model 1887", 6], ["Magnum", 5], ["LeMat", 9]]

    def __init__(self, id_rr, countdown, voice_channel, players=[], new_voice_channel=None, original_message=None, mode="Easy", readys=0):
        self.id = id_rr
        self.players = players
        self.voice_channel = voice_channel
        self.new_voice_channel = new_voice_channel
        self.countdown = countdown
        self.revolver = choice(self.revolvers)
        self.original_message = original_message
        self.mode = mode
        self.readys = readys

    def get_drum(self):
        bullet = randint(0, self.revolver[1]-1)
        drum = []
        for i in range(self.revolver[1]):
            if i == bullet:
                drum.append(1)
            else:
                drum.append(0)
        return drum


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


# ------------- VIEWS ---------------

class RRouletteView(discord.ui.View):
    def __init__(self, rroulette, drum=[], drum_order=[], drum_index=0):
        super().__init__()
        self.rroulette = rroulette
        self.drum = drum
        self.drum_order = drum_order
        self.drum_index = drum_index

        if len(drum) == 0:
            self.set_drum()

    @discord.ui.button(emoji="🔫", style=discord.ButtonStyle.red)
    async def shoot_callback(self, button, interaction):
        # Check if the player is in the voice channel is the corresponding order
        if interaction.user != self.drum_order[self.drum_index]:
            await interaction.response.send_message(
                f"{interaction.user.mention} Espera a tu turno impaciente", delete_after=3)
            print_debug(f"{interaction.user} tiene que esperar a su turno")
            return

        # Check if the player is the last in the order
        if self.drum_index == len(self.drum):
            self.set_drum()  # Set the new drum

        # Get the embed message
        original_embed = interaction.message.embeds[0]

        # Checks if the player has already been shot
        if self.drum[self.drum_index] == 1:
            original_embed.add_field(name="Resultado", value=f"💀")
            print_debug(f"{interaction.user} ha muerto")

            # Check if the mode is Easy
            if self.rroulette.mode == "Easy":
                await interaction.user.move_to(self.rroulette.voice_channel)
            else:
                await interaction.user.kick(reason="Has sido expulsado jugando a la ruleta rusa")

            # Remove the player from the rroulette
            self.rroulette.players.remove(interaction.user)
            self.set_drum()

        # If the player has not been shot, shoot next player
        else:
            self.drum_index += 1
            print_debug(f"{interaction.user} sigue vivo")
            original_embed.add_field(name="Resultado", value=f"❤")

        # Check if there is one left in the roulette wheel
        if len(self.rroulette.players) == 1:
            await interaction.channel.send(
                f"{self.rroulette.players[0].mention} ha ganado la ruleta rusa 🎉")
            print_debug(f"{self.rroulette.players}")

            await self.add_role(interaction)

            print_debug(
                f"{self.rroulette.players[0]} ha ganado la rroulette")
            # Check if the mode is Easy
            if self.rroulette.mode == "Easy":
                await self.rroulette.players[0].move_to(self.rroulette.voice_channel)
                await self.rroulette.new_voice_channel.delete()
                print_debug(
                    f"Se ha eliminado el canal de voz de la ruleta rusa")

            button.disabled = True
            await interaction.response.edit_message(embed=original_embed, view=self)
            return

        # Edit original message with the result and disable button
        button.disabled = True
        await interaction.response.edit_message(embed=original_embed, view=self)

        # New message with next player
        embed = discord.Embed(color=discord.Colour.purple(), title=f'Russian Roulette\n',
                              description=f'Cuidado no mueras!\n')
        embed.add_field(
            name='Turno', value=f'{self.drum_order[self.drum_index].mention}', inline=True)
        embed.add_field(
            name='Modo', value=f'{self.rroulette.mode}', inline=True)
        embed.add_field(
            name='Revolver', value=f'{self.rroulette.revolver[0]}', inline=True)
        embed.add_field(
            name='Recamara', value=f'[{self.drum_index}/{self.rroulette.revolver[1]}]', inline=True)

        view = RRouletteView(self.rroulette, self.drum,
                             self.drum_order, self.drum_index)
        await interaction.channel.send(embed=embed, view=view)

    # Set the new drum
    def set_drum(self):

        self.drum = self.rroulette.get_drum()
        self.drum_order = self.rroulette.players

        shuffle(self.drum_order)

        if len(self.drum) > len(self.rroulette.players):
            self.drum_order = self.drum_order * \
                (len(self.drum) - len(self.rroulette.players))
        elif len(self.drum) < len(self.rroulette.players):
            self.drum_order = self.drum_order[:len(self.drum)]

        self.drum_index = 0

    # Add the role to the player
    async def add_role(self, interaction):
        level = 0
        roles_user = self.rroulette.players[0].roles
        for role in roles_user:
            if role.name.startswith("Ruleta Rusa"):
                level = int(role.name[-1])
                break
        print_debug(f"El ganador tiene Nivel: {level}")
        roles = interaction.guild.roles
        next_level = 0
        for role in roles:
            if role.name.startswith("Ruleta Rusa") and int(role.name[-1]) == level + 1:
                next_level = role
                break
        if next_level != 0:
            await self.rroulette.players[0].add_roles(next_level)
            print_debug(f"{self.rroulette.players[0]} ha subido de nivel")
        else:
            new_role = await interaction.guild.create_role(name=f"Ruleta Rusa - N{level + 1}", color=discord.Colour.yellow(
            ), permissions=discord.Permissions(permissions=2150878272), mentionable=True, reason=f'Siguiente Nivel de la Ruleta Rusa')
            await self.rroulette.players[0].add_roles(new_role)


class PrepareRRouletteView(discord.ui.View):

    def __init__(self, potential_players, rroulette_id):
        super().__init__()
        self.potential_players = potential_players
        self.rroulette_id = rroulette_id

        self.players_count = 0

    @discord.ui.button(label="Aceptar", row=0, style=discord.ButtonStyle.success)
    async def acept_button_callback(self, _, interaction):

        if not interaction.user in self.potential_players:
            await interaction.response.send_message(f"{interaction.user.mention} no estás en el canal de voz.", ephemeral=True)
            return

        await interaction.response.send_message(f"{interaction.user.mention} ha aceptado la partida de Russian Roulette.", delete_after=3)
        print_debug(
            f"{interaction.user.name} ha aceptado a jugar en partida de Russian Roulette.")

        for rroulette in countdown_roulette:
            if rroulette.id == self.rroulette_id:

                # Add the player to the rroulette
                rroulette.players.append(interaction.user)
                self.players_count += 1

                # Check is the last player has joined the rroulette
                if self.players_count == len(self.potential_players):
                    print_debug(f"Ya han votado a todos los jugadores.")
                    await interaction.channel.send(f"Ya han votado a todos los jugadores.", delete_after=3)
                    rroulette.countdown = datetime.today()
                break


class VoteView(discord.ui.View):

    def __init__(self, ctx, propuesta, role_1, role_2, end_time=timedelta(hours=1), emoji_1="✅", emoji_2="❌", message_id=None):
        super().__init__()
        self.ctx = ctx
        message_id = message_id
        self.propuesta = propuesta
        self.role_1 = role_1
        self.role_2 = role_2
        self.emoji_1 = emoji_1
        self.emoji_2 = emoji_2
        self.end_time = end_time
        self.voters_1 = []
        self.voters_2 = []

        self.button1 = discord.ui.Button(
            style=discord.ButtonStyle.grey, emoji=emoji_1)
        self.button2 = discord.ui.Button(
            style=discord.ButtonStyle.grey, emoji=emoji_2)

        self.button1.callback = self.button1_callback
        self.button2.callback = self.button2_callback

        self.add_item(self.button1)
        self.add_item(self.button2)

    async def notify_vote(self):

        if not (len(self.voters_1) or len(self.voters_2)):
            print_debug(f"Nadie ha votado")
            embed = discord.Embed(color=discord.Colour.purple(), title=f'Votación Eliminada\n',
                                  description=f'Autor: {self.ctx.author.mention}\nPropuesta: `{self.propuesta}`\n\nHa sido eliminada, nadie ha interactuado con ella')

        elif len(self.voters_1) > len(self.voters_2):
            embed = discord.Embed(color=discord.Colour.purple(), title=f'Votación Terminada\n',
                                  description=f'Autor: {self.ctx.author.mention}\nPropuesta: `{self.propuesta}`\n\n')

            embed.add_field(name='Propuesta ganadora',
                            value=f'{self.emoji_1}', inline=True)

            embed.add_field(
                name=f'Votantes de {self.emoji_1} - `{len(self.voters_1)} 👤`', value=f'||{self.role_1.mention}||')
            embed.add_field(
                name=f'Votantes de {self.emoji_2} - `{len(self.voters_2)} 👤`', value=f'||{self.role_2.mention}||')

        elif len(self.voters_1) < len(self.voters_2):
            embed = discord.Embed(color=discord.Colour.purple(), title=f'Votación Terminada\n',
                                  description=f'Autor: {self.ctx.author.mention}\nPropuesta: `{self.propuesta}`\n\n')

            embed.add_field(name='Propuesta ganadora',
                            value=f'{self.emoji_1}')

            embed.add_field(
                name=f'Votantes de {self.emoji_1} - `{len(self.voters_1)} 👤`', value=f'||{self.role_1.mention}||')
            embed.add_field(
                name=f'Votantes de {self.emoji_2} - `{len(self.voters_2)} 👤`', value=f'||{self.role_2.mention}||')
        else:
            embed = discord.Embed(color=discord.Colour.purple(), title=f'Votación Empatada\n',
                                  description=f'Autor: {self.ctx.author.mention}\nPropuesta: `{self.propuesta}`\n\n')

            embed.add_field(
                name=f'Votantes de {self.emoji_1} - `{len(self.voters_1)} 👤`', value=f'||{self.role_1.mention}||')
            embed.add_field(
                name=f'Votantes de {self.emoji_2} - `{len(self.voters_2)} 👤`', value=f'||{self.role_2.mention}||')

        print_debug(
            f"Votacion {self.propuesta[:15]} terminada - Notificando a {len(self.voters_1) + len(self.voters_2)} usuarios")

        await self.ctx.channel.send(embed=embed)

    # Buttons reactions

    async def button1_callback(self, interaction: discord.Interaction):
        if interaction.user in self.voters_1:
            await interaction.response.send_message(f"{interaction.user.mention} ya has votado", ephemeral=True)
            return

        if interaction.user in self.voters_2:
            # Remove user from second list
            self.voters_2.remove(interaction.user)

            await interaction.user.remove_roles(self.role_2)

        self.voters_1.append(interaction.user)  # Add user to first list
        await interaction.user.add_roles(self.role_1)  # Add role to user

        embed = discord.Embed(color=discord.Colour.purple(), title='Votación Abierta\n',
                              description=f'**Propuesta:** {self.propuesta}\n\n📩 By: {self.ctx.author.mention}\n--------------------------')
        embed.add_field(name=f"{self.emoji_1}",
                        value=f"{len(self.voters_1)}", inline=True)
        embed.add_field(name=f"{self.emoji_2}",
                        value=f"{len(self.voters_2)}", inline=True)
        await interaction.response.edit_message(embed=embed)
        print_debug(f"{interaction.user.name} ha votado {self.emoji_1}")

    async def button2_callback(self, interaction: discord.Interaction):
        if interaction.user in self.voters_2:
            await interaction.response.send_message(f"{interaction.user.mention} ya has votado", ephemeral=True)
            return

        if interaction.user in self.voters_1:
            # Remove user from first list
            self.voters_1.remove(interaction.user)
            await interaction.user.remove_roles(self.role_1)

        self.voters_2.append(interaction.user)  # Add user to second list
        await interaction.user.add_roles(self.role_2)  # Add role to user

        embed = discord.Embed(color=discord.Colour.purple(), title='Votación Abierta\n',
                              description=f'**Propuesta:** {self.propuesta}\n\n📩 By: {self.ctx.author.mention}\n--------------------------')
        embed.add_field(name=f"{self.emoji_1}",
                        value=f"{len(self.voters_1)}", inline=True)
        embed.add_field(name=f"{self.emoji_2}",
                        value=f"{len(self.voters_2)}", inline=True)
        await interaction.response.edit_message(embed=embed)
        print_debug(f"{interaction.user.name} ha votado {self.emoji_2}")


class PlsRoleView(discord.ui.View):

    def __init__(self, user, role, reason, roles):
        super().__init__()
        self.user = user
        self.role = role
        self.reason = reason
        self.roles = roles
        self.date = datetime.today()

    @discord.ui.button(label="Aceptar", row=0, style=discord.ButtonStyle.success)
    async def first_button_callback(self, _, interaction):

        await interaction.user.add_roles(self.role)
        await interaction.channel.send(f"{interaction.user.mention} ha aceptado a {self.user.mention}, ahora es {self.role.mention} 🎉")
        await interaction.message.delete()
        fecha = "Inicio: `"+self.date.strftime("%m/%d/%Y %H:%M:%S") + \
            "`\nAprovada: `" + datetime.today().strftime("%m/%d/%Y %H:%M:%S") + "`"
        embed = discord.Embed(color=Colour.purple(), title='Solicitud: Aceptada ✅',
                              description=f'\nRol: `{self.role.name.upper()}`\nMotivo: `{self.reason}`\n\n{fecha}')
        await interaction.user.send(embed=embed)
        print_debug(f"{interaction.user.name} ha aceptado a {self.user.name}")

    @discord.ui.button(label="Rechazar", row=0, style=discord.ButtonStyle.danger)
    async def second_button_callback(self, _, interaction):

        await interaction.channel.send(f"{interaction.user.mention} ha denegado a {self.user.mention} a ser {self.role.mention} 💀")
        await interaction.message.delete()
        fecha = "Inicio: `"+self.date.strftime("%m/%d/%Y %H:%M:%S") + \
            "`\nDenegada: `" + datetime.today().strftime("%m/%d/%Y %H:%M:%S") + "`"
        embed = discord.Embed(color=Colour.purple(), title='Solicitud: Denegada ❌',
                              description=f'\nRol: `{self.role.name.upper()}`\nMotivo: `{self.reason}`\n\n{fecha}')
        await interaction.user.send(embed=embed)
        print_debug(
            f"{interaction.user.name} ha denegado a {self.user.name} a ser {self.role.name}")

# -------------------------------
# METHODS
# -------------------------------


def get_month(month):
    try:
        return MONTHS.index(month.capitalize()) + 1
    except Exception:
        return -1


def ranking_icon(rank):
    if rank == 1:
        return '🥇'
    if rank == 2:
        return '🥈'
    if rank == 3:
        return '🥉'
    return '👤'


async def set_food_rating(message, id_channel):
    if message.attachments == []:
        return

    # Verificar que el mensaje es una imagen
    if message.channel.id == id_channel:
        _, file_extension = os.path.splitext(
            message.attachments[0].filename)

        # CHECK why inconsitency in emoji
        if file_extension in ['.png', '.jpg', 'jpeg']:
            await message.add_reaction('🤮')
            await message.add_reaction(f'<:one_stars:{ONE_STAR_REACTION_ID}>')
            await message.add_reaction(f'<:two_stars:{TWO_STAR_REACTION_ID}>')
            await message.add_reaction(f'<:three_stars:{THREE_STAR_REACTION_ID}>')


async def check_food_reactions(payload):
    if payload.channel_id != FOOD_CHANNEL_ID:
        return

    if (payload.emoji.id in (ONE_STAR_REACTION_ID, TWO_STAR_REACTION_ID, THREE_STAR_REACTION_ID) or (payload.emoji.name == "🤮")):

        member = payload.member
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        for reaction in message.reactions:
            async for user in reaction.users():
                # User must be able to react once and the author cant react to his own message
                if (reaction.emoji != payload.emoji and user == member) or (message.author == member):
                    await message.remove_reaction(reaction.emoji, member)

# -------------------------------
# GETTERS for AutoComplete
# -------------------------------


async def get_months(ctx: discord.AutocompleteContext):
    return [month for month in MONTHS if month.capitalize().startswith(ctx.value.capitalize())]


async def get_type_times(ctx: discord.AutocompleteContext):
    return [time for time in TIMES if time.capitalize().startswith(ctx.value.capitalize())]

# -------------------------------
# COMMANDS
# -------------------------------


@bot.slash_command(description='pong 🏓')
async def ping(ctx):
    await ctx.respond('Pong 🏓')
    print_debug(f"{ctx.author.name} ha usado /ping")


@bot.slash_command(description='El bot te saluda.')
async def hello(ctx):
    await ctx.respond(f'Hi {ctx.author.mention}, I\'m {bot.user.name}!')
    print_debug(f"{ctx.author.name} ha usado /hello")


@bot.slash_command(description='Te gusta jugar? 🎲 Este es tu juego! Prueba suerte! 🎰')
async def rnd(ctx):
    if randint(0, 1):
        await ctx.respond(f'{ctx.author.mention} Ha muerto 💀')
        await ctx.guild.kick(ctx.author)
        print_debug(f"{ctx.author.name} ha usado /rnd y ha muerto")
    else:
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Vencio a la muerte'), atomic=True)
        await ctx.respond(f'{ctx.author.mention} Has tenido suerte 🌟')
        print_debug(f"{ctx.author.name} ha usado /rnd y ha tenido suerte")


@bot.slash_command(description='Te gusta jugar pero le temes a la muerte porque tienes 💩? Prueba suerte con este juego! 🎰')
async def rnd_easy(ctx):
    if randint(0, 1):
        await ctx.author.move_to(None)
        await ctx.respond(f'{ctx.author.mention} A la calle 🚴')
        print_debug(
            f"{ctx.author.name} ha usado /rnd_easy y ha sido movido a la calle")
    else:
        await ctx.respond(f'{ctx.author.mention} Has tenido suerte 🌟')
        print_debug(f"{ctx.author.name} ha usado /rnd_easy y ha tenido suerte")


@bot.slash_command(description='Alguno del canal os movereis a un lugar aleatorio 🏃')
async def rnd_move_someone(ctx):
    current_channel = ctx.author.voice.channel
    if current_channel is None:
        await ctx.respond(f'{ctx.author.mention} No estas en un canal de voz.', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /rnd_move_someone pero no esta en un canal de voz")
        return

    member = choice(current_channel.members)
    voice_channel = choice(ctx.guild.voice_channels)

    await member.move_to(voice_channel)
    await ctx.respond(f'{member.mention} ha sido movido a {voice_channel.name}')
    print_debug(
        f"{ctx.author.name} ha usado /rnd_move_someone y ha movido a {member.name} a {voice_channel.name}")


@bot.slash_command(description='Todos al cine! 🎞')
async def move_to_cinema(ctx):
    current_channel = ctx.author.voice.channel
    if current_channel is None:
        await ctx.respond(f'{ctx.author.mention} No estas en un canal de voz.', ephemeral=True)
        return

    role_cinema = discord.utils.get(ctx.guild.roles, name="Cineasta")
    if not ((ctx.author.guild_permissions.administrator) or (role_cinema in [role for role in ctx.author.roles])):
        await ctx.respond(f'{ctx.author.mention} No tienes permisos', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /move_to_cinema pero no tiene permisos")
        return

    voice_channel = discord.utils.get(
        ctx.guild.voice_channels, id=CINEMA_CHANNEL_ID)
    for member in current_channel.members:
        await member.move_to(voice_channel)
    await ctx.respond(f'{ctx.author.mention} Todos los miembros han sido movidos a {voice_channel.name}', delay=5.0)
    print_debug(
        f"{ctx.author.name} ha usado /move_to_cinema y ha movido a todos a {voice_channel.name}")


@bot.slash_command(description='Mueve a todos a un canal 📦')
@option("canal", description="Canal al que quieras mover a todos los conectados")
async def move_to(ctx, voice_channel: discord.VoiceChannel):
    current_channel = ctx.author.voice.channel
    if current_channel is None:
        await ctx.respond(f'{ctx.author.mention} No estas en un canal de voz.', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /move_to pero no esta en un canal de voz")
        return

    if not ((ctx.author.guild_permissions.administrator) or (NAME_SUPORT_ADMIN in [role.name for role in ctx.author.roles])):
        await ctx.respond(f'{ctx.author.mention} No tienes los roles para mover a la gente', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /move_to pero no tiene permisos")
        return

    for member in current_channel.members:
        await member.move_to(voice_channel)

    await ctx.respond(f'{ctx.author.mention} has movido a todos a {voice_channel.name}', ephemeral=True)
    print_debug(
        f"{ctx.author.name} ha usado /move_to y ha movido a todos a {voice_channel.name}")


@bot.slash_command(description='Para ver todos los roles 👀')
async def roles(ctx):
    # Slice roles to not take into account the "@everyone" role
    roles = [rol for rol in ctx.guild.roles[1::] if not rol.is_bot_managed()]

    roles = sorted(roles, key=lambda x: x.position, reverse=True)
    counted_roles = [len(rol.members) for rol in roles]

    embed = discord.Embed(color=Colour.purple(), title=f"Roles de {ctx.guild.name}",
                          description='\n'.join(f'{role.mention} - `{counted_roles[i]} 👤`' for i, role in enumerate(roles)))
    await ctx.respond(embed=embed)
    print_debug(f"{ctx.author.name} ha usado /roles")


@bot.slash_command(description='Al reformatorio! ⛓. Debe de existir el canal con el nombre: ⛓ Reformatorio ⛓')
@option("member", description="Quien se ha portado mal? 🤔")
async def reformatory(ctx, member: discord.Member):
    # Mirar si tiene el rol de reformatorio o administrador
    if not ((ctx.author.guild_permissions.administrator) or ('Staff Reformatory' in [role.name for role in ctx.author.roles])):
        await ctx.respond(f'{ctx.author.mention} No tienes permisos para hacer eso! 🤔')
        print_debug(
            f"{ctx.author.name} ha usado /reformatory pero no tiene permisos")
        return

    name_channel = "⛓ Reformatorio ⛓"
    channel_reformatory = discord.utils.get(
        ctx.guild.voice_channels, name=name_channel)

    if channel_reformatory == None:
        await ctx.respond(f'No existe el canal {name_channel}', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /reformatory pero no existe el canal {name_channel}")
        return

    if member.voice == None:
        await ctx.respond(f'{member.mention} no esta en un canal de voz', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /reformatory pero {member.name} no esta en un canal de voz")
        return

    current_channel = member.voice.channel
    await member.move_to(channel_reformatory)

    # Añadir a la cola de reformatorio
    # user, current_channel, time
    jail_time = randrange(MIN_TIME_REFORMATORY, MAX_TIME_REFORMATORY)

    embed = discord.Embed(color=discord.Colour.purple(), title=f'{name_channel}\n',
                          description=f'{member.mention} se ha portado mal. \n\n Tiempo de reformación: `{jail_time}` segundos 🕐')
    message = await ctx.respond(embed=embed)

    reformatory_cells.append([member, current_channel, jail_time, message])
    print_debug(
        f"{ctx.author.name} ha usado /reformatory y ha añadido a {member.name} a la cola de reformatorio")


@bot.slash_command(description='Pide un rol al admin 🙋🏻‍♂️')
@option("rol", description="Rol que solicitas")
@option("motivo", description="Escribe una breve descripción argumentando tu petición")
async def pls_rol(ctx, rol: discord.Role, reason: str):

    roles = ctx.guild.roles
    if rol not in roles:
        await ctx.respond(f'No se ha encontrado el rol `{rol.name}`...😔', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /pls_rol pero no existe el rol {rol.name}")
        return

    if rol in ctx.author.roles:
        await ctx.respond(f'Ya tienes el rol {rol.mention}', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /pls_rol pero ya tiene el rol {rol.name}")
        return

    embed = discord.Embed(color=discord.Colour.purple(), title='Petición de Rol',
                          description=f'Autor: {ctx.author.mention} \n\nRol: {rol.mention} \n Motivo: `{reason}`')
    await ctx.guild.get_channel(ROLE_CHANNEL_ID).send(embed=embed, view=PlsRoleView(ctx.author, rol, reason, roles))
    await ctx.respond(f'Petición enviada correctamente ✅', ephemeral=True)
    print_debug(
        f"{ctx.author.name} ha usado /pls_rol y ha enviado una petición de rol para {rol.name}")


@bot.slash_command(description='Abre una votación 📩 con ✅ y ❌')
@option("type_time", description="Tipo de duración", autocomplete=get_type_times)
@option("timeout", description="Duración", autocomplete=discord.utils.basic_autocomplete(range(1, 60)))
@option("propuesta", description="Tema de votación")
async def vote(ctx, propuesta: str, type_time: str, timeout: int):
    if type_time.lower() not in [type_t.lower() for type_t in TIMES]:
        await ctx.respond(f'Tipo de duración no reconocido `{type_time}`', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /vote pero el tipo de duración {type_time} no es reconocido")
        return

    embed = discord.Embed(color=discord.Colour.purple(), title='Votación Abierta\n',
                          description=f'**Propuesta:** {propuesta}\n\n📩 By: {ctx.author.mention}')

    time = datetime.now().strftime("%y%f%d")
    role_1 = await ctx.guild.create_role(name=f'V_R1{time}', color=discord.Colour.green(), permissions=discord.Permissions(
        permissions=2150878272), mentionable=True, reason=f'Para mencionar en la votacion')
    role_2 = await ctx.guild.create_role(name=f'V_R2{time}', color=discord.Colour.red(), permissions=discord.Permissions(
        permissions=2150878272), mentionable=True, reason=f'Para mencionar en la votacion')

    if type_time.lower() == 'dias':
        vote = VoteView(ctx, propuesta, role_1, role_2,
                        end_time=timedelta(days=timeout))
    elif type_time.lower() == 'horas':
        vote = VoteView(ctx, propuesta, role_1, role_2,
                        end_time=timedelta(hours=timeout))
    elif type_time.lower() == 'minutos':
        vote = VoteView(ctx, propuesta, role_1, role_2,
                        end_time=timedelta(minutes=timeout))

    interaction = await ctx.respond(embed=embed, view=vote)
    vote.message_id = interaction.id
    votes.append(vote)
    print_debug(f"{ctx.author.name} ha usado /vote y ha abierto una votación")


@bot.slash_command(description='Abre una votación 📩 con reacciones personalizadas 🎨')
@option("type_time", description="Tipo de duración", autocomplete=get_type_times)
@option("timeout", description="Duración", autocomplete=discord.utils.basic_autocomplete(range(1, 60)))
@option("propuesta", description="Tema de votación")
@option("reaccion 1", description="Pon la primer reacción")
@option("reaccion 2", description="Pon la segunda reacción")
async def vote_custom(ctx, type_time: str, timeout: int, propuesta: str, emoji_1: str, emoji_2: str):
    if type_time.lower() not in [type_t.lower() for type_t in TIMES]:
        await ctx.respond(f'Tipo de duración no reconocido `{type_time}`', ephemeral=True)
        return
    if emoji_1 == emoji_2:
        await ctx.respond(f'No puedes poner las mismas reacciones', ephemeral=True)
        return

    embed = discord.Embed(color=discord.Colour.purple(), title='Votación Abierta\n',
                          description=f'**Propuesta:** {propuesta}\n\n📩 By: {ctx.author.mention}')

    time = datetime.now().strftime("%y%f%d")
    role_1 = await ctx.guild.create_role(name=f'V_R1{time}', color=discord.Colour.green(), permissions=discord.Permissions(
        permissions=2150878272), mentionable=True, reason=f'Para mencionar en la votacion')
    role_2 = await ctx.guild.create_role(name=f'V_R2{time}', color=discord.Colour.red(), permissions=discord.Permissions(
        permissions=2150878272), mentionable=True, reason=f'Para mencionar en la votacion')

    if type_time.lower() == 'dias':
        vote = VoteView(ctx, propuesta, role_1, role_2,
                        end_time=timedelta(days=timeout), emoji_1=emoji_1, emoji_2=emoji_2)
    elif type_time.lower() == 'horas':
        vote = VoteView(ctx, propuesta, role_1, role_2,
                        end_time=timedelta(hours=timeout), emoji_1=emoji_1, emoji_2=emoji_2)
    elif type_time.lower() == 'minutos':
        vote = VoteView(ctx, propuesta, role_1, role_2,
                        end_time=timedelta(minutes=timeout), emoji_1=emoji_1, emoji_2=emoji_2)

    message = await ctx.respond(embed=embed, view=vote)
    vote.message = message
    votes.append(vote)
    print_debug(
        f"{ctx.author.name} ha usado /vote_custom y ha abierto una votación")


@bot.slash_command(description='Top 10 mejores comidas 🍽')
async def food_ratings(ctx):

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

        print_debug("Reaccion")

        players[members.index(message.author)].n_foods += 1

        for reaction in message.reactions:
            if reaction.emoji == one_stars:
                players[members.index(message.author)
                        ].one_stars += reaction.count - 1
            elif reaction.emoji == two_stars:
                players[members.index(message.author)
                        ].two_stars += reaction.count - 1
            elif reaction.emoji == three_stars:
                players[members.index(message.author)
                        ].three_stars += reaction.count - 1

    players.sort(key=FoodPlayer.get_points, reverse=True)
    embed = discord.Embed(color=Colour.purple(), title='Top 10 Mejores Comidas 🍽',
                          description='\n'.join(
        f'`{ranking_icon(player_rank+1)} {player.member.name} - {player.get_points()} puntos`' for player_rank, player in enumerate(players[:10])))
    await ctx.respond(embed=embed)
    print_debug(
        f"{ctx.author.name} ha usado /food_ratings y ha mostrado los top 10 mejores comidas")


@bot.slash_command(description='Top Comidas 🍽: Elige top y mes 🍴')
@option("top", description="Top que deseas consultar",  autocomplete=discord.utils.basic_autocomplete(TOPS))
@option("month", description="Mes que desas consultar", autocomplete=get_months)
async def food_ratings_custom(ctx, top: int, month: str):
    n_month = get_month(month)

    if n_month == -1:
        await ctx.respond(f'El mes `{month}` no existe...', ephemeral=True)
        return

    if n_month > datetime.today().month:
        await ctx.respond(f'No se ha inventado el viaje temporal...😅', ephemeral=True)
        return

    if n_month == datetime.today().month:
        day = datetime.today().day
    else:
        day = 31

    async with ctx.channel.typing():
        date_limit_up = datetime(datetime.today().year, n_month, day)
        date_limit_down = datetime(datetime.today().year, n_month, 1)

        members = [member for member in ctx.guild.members if not member.bot]
        players = [FoodPlayer(member) for member in members]

        channel = ctx.guild.get_channel(FOOD_CHANNEL_ID)
        one_stars = await ctx.guild.fetch_emoji(ONE_STAR_REACTION_ID)
        two_stars = await ctx.guild.fetch_emoji(TWO_STAR_REACTION_ID)
        three_stars = await ctx.guild.fetch_emoji(THREE_STAR_REACTION_ID)

        await ctx.defer()
        async for message in channel.history(after=date_limit_down, before=date_limit_up, limit=None):
            if message.attachments == []:
                continue   # No Imagenes
            if message.reactions == []:
                continue    # No reacciones

            players[members.index(message.author)].n_foods += 1

            for reaction in message.reactions:
                if reaction.emoji == one_stars:
                    players[members.index(message.author)
                            ].one_stars += reaction.count - 1
                elif reaction.emoji == two_stars:
                    players[members.index(message.author)
                            ].two_stars += reaction.count - 1
                elif reaction.emoji == three_stars:
                    players[members.index(message.author)
                            ].three_stars += reaction.count - 1

        players.sort(key=FoodPlayer.get_points, reverse=True)
        embed = discord.Embed(color=Colour.purple(), title=f'Top {top} Mejores Comidas de {MONTHS[n_month-1]} 📅',
                              description='\n'.join(f'`{ranking_icon(player_rank+1)} {player.member.name} - {player.get_points()} puntos`' for player_rank, player in enumerate(players[:top])))
        await ctx.respond(embed=embed)
        print_debug(
            f"{ctx.author.name} ha usado /food_ratings_custom y ha mostrado los top {top} mejores comidas")


@bot.slash_command(description='Todas las Estadisticas de Comida de un usuario 🍳')
@option("top", description="Top que deseas consultar",  autocomplete=discord.utils.basic_autocomplete(TOPS))
@option("month", description="Mes que desas consultar", autocomplete=get_months)
async def food_statistics_of(ctx, member: discord.Member):
    player = FoodPlayer(member)
    async with ctx.channel.typing():

        channel = ctx.guild.get_channel(FOOD_CHANNEL_ID)
        one_stars = await ctx.guild.fetch_emoji(ONE_STAR_REACTION_ID)
        two_stars = await ctx.guild.fetch_emoji(TWO_STAR_REACTION_ID)
        three_stars = await ctx.guild.fetch_emoji(THREE_STAR_REACTION_ID)

        await ctx.defer()
        async for message in channel.history(after=None, before=None, limit=None):
            if message.attachments == []:
                continue   # No Imagenes
            if message.reactions == []:
                continue    # No reacciones
            if message.author != member:
                continue   # No es el usuario que queremos

            player.n_foods += 1

            for reaction in message.reactions:
                if reaction.emoji == one_stars:
                    player.one_stars += reaction.count - 1
                elif reaction.emoji == two_stars:
                    player.two_stars += reaction.count - 1
                elif reaction.emoji == three_stars:
                    player.three_stars += reaction.count - 1

        color = member.color
        if color == discord.Colour.default():
            color = Colour.purple()

        embed = discord.Embed(color=color, title=f'Estadísticas de la comida 🍽',
                              description=f'{member.mention} tiene las siguientes estadísticas\n')
        embed.add_field(
            name='Puntos', value=f'{player.get_points()}', inline=True)
        embed.add_field(name='Comidas', value=player.n_foods, inline=True)
        embed.add_field(
            name="Media:", value=f'{player.get_mean_points()}', inline=True)
        embed.add_field(name=f'{one_stars}',
                        value=player.one_stars, inline=True)
        embed.add_field(name=f'{two_stars}',
                        value=player.two_stars, inline=True)
        embed.add_field(name=f'{three_stars}',
                        value=player.three_stars, inline=True)
        embed.set_footer(
            text=f'{member.name}#{member.discriminator}', icon_url=member.display_avatar)

        await ctx.respond(embed=embed)
        print_debug(
            f"{ctx.author.name} ha usado /food_statistics_of y ha mostrado las estadísticas de {member.name}")


@bot.slash_command(description='Eliminar las reacciones de estellas generadas por el bot')
async def delete_ratings(ctx, id_message: str = None):
    channel = ctx.guild.get_channel(FOOD_CHANNEL_ID)
    if channel != ctx.channel:
        await ctx.respond('No puedes eliminar las reacciones de estrellas en este canal', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha intentado eliminar las reacciones de estrellas en un canal distinto al de comidas")
        return

    if id_message in ("", " ", None):
        messages = await channel.history(limit=1).flatten()
        message = messages[0]
    else:
        partial_message = channel.get_partial_message(id_message)
        if partial_message is None:
            await ctx.respond(f'No se ha encontrado el mensaje con ID `{id_message}`', ephemeral=True)
            print_debug(
                f"{ctx.author.name} ha usado /delete_ratings y ha intentado eliminar las reacciones de un mensaje con ID {id_message}")
            return

        message = await partial_message.fetch()

    if not ((ctx.author.guild_permissions.administrator) or (message.author == ctx.author)):
        await ctx.respond('No puedes eliminar las reacciones de estrellas de otros usuarios', ephemeral=True)
        return

    if message.reactions == []:
        await ctx.respond('El último mensaje no tiene reacciones de estrellas', ephemeral=True)
        return

    await message.clear_reactions()
    await ctx.respond(f'Reacciones eliminadas del mensaje {message.jump_url} de {message.author.mention} ✨')
    print_debug(
        f"{ctx.author.name} ha usado /delete_ratings y ha eliminado las reacciones de {message.author.name}")


@bot.slash_command(description='Eliminar roles de votacion')
async def delete_vote_roles(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond('No tienes permisos para eliminar roles de votación', ephemeral=True)
        return

    for role in ctx.guild.roles:
        if role.name.startswith('V_R'):
            await role.delete()
    await ctx.respond('Roles de votación eliminados')
    print_debug(
        f"{ctx.author.name} ha usado /delete_vote_roles y ha eliminado los roles de votación")


@bot.slash_command(description='Eliminar canales de ruleta rusa')
async def delete_roulette_channels(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond('No tienes permisos para eliminar roles de votación', ephemeral=True)
        return

    await ctx.defer()
    for channel in ctx.guild.channels:
        if channel.name.startswith('Ruleta'):
            await channel.delete()
    await ctx.respond('Canales de ruleta rusa eliminados')
    print_debug(
        f"{ctx.author.name} ha usado /delete_vote_roles y ha eliminado los roles de votación")


@bot.slash_command(description='Vamos a jugar a la ruleta rusa 👤🔫')
@option("mode", description="Elige el tipo de modo",  autocomplete=discord.utils.basic_autocomplete(["Easy", "Hard"]))
async def russian_roulette(ctx, mode: str):
    await ctx.respond('Actualmente esta en mantenimiento :( ...', ephemeral=True)
    return
    if mode not in ("Easy", "Hard"):
        await ctx.respond('El modo debe ser Easy o Hard', ephemeral=True)
        return

    if ctx.author.voice is None:
        print_debug(
            f"{ctx.author.name} ha intentado jugar a la ruleta rusa sin estar en un canal de voz")
        await ctx.respond('Debes estar en un canal de voz para jugar a la ruleta rusa', ephemeral=True)
        return

    potential_players = ctx.author.voice.channel.members

    if len(potential_players) < 2:
        await ctx.respond('Debe de haber por lo menos dos jugadores para poder jugar', ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha intentado jugar a la ruleta rusa en un canal de voz con menos de dos jugadores")
        return

    rroulette = RRoulette(datetime.now().strftime("%y%f%d"), datetime.today(
    ) + timedelta(seconds=COUNTDOWN_RROULETTE), ctx.author.voice.channel, mode=mode)

    embed = discord.Embed(color=discord.Colour.purple(), title=f'Countdown Russian roulette {mode} 🕔 🔫',
                          description=f'Quereis jugar a la ruleta rusa?\n\nLa ruleta rusa comienza en `{COUNTDOWN_RROULETTE}` segundos')
    message = await ctx.respond(embed=embed, view=PrepareRRouletteView(potential_players, rroulette.id))
    rroulette.original_message = message

    countdown_roulette.append(rroulette)


# -------------------------------
# TASKS
# -------------------------------


@tasks.loop(seconds=1)
async def start_russian_roulettes():
    if not len(countdown_roulette):
        return

    for rroulette in countdown_roulette:
        if rroulette.countdown < datetime.now():
            if len(rroulette.players) < 1:
                print_debug(
                    f"No se ha podido iniciar la ruleta rusa porque no hay suficientes jugadores")
                await rroulette.original_message.delete_original_message()
                countdown_roulette.remove(rroulette)
                return

            if rroulette.mode == "Easy":
                new_voice_channel = await rroulette.voice_channel.category.create_voice_channel(name='Ruleta rusa 👤🔫')
                rroulette.new_voice_channel = new_voice_channel

                for player in rroulette.players:
                    await player.move_to(new_voice_channel)

            view = RRouletteView(rroulette)
            embed = discord.Embed(color=discord.Colour.purple(), title=f'Russian Roulette - {rroulette.mode}\n',
                                  description=f'Cuidado no mueras!\n')
            embed.add_field(
                name='Turno', value=f'{view.drum_order[0].mention}', inline=True)
            embed.add_field(
                name='Modo', value=f'{rroulette.mode}', inline=True)
            embed.add_field(
                name='Revolver', value=f'{rroulette.revolver[0]}', inline=True)
            embed.add_field(
                name='Recamara', value=f'[{0}/{rroulette.revolver[1]}]', inline=True)

            await rroulette.original_message.channel.send(embed=embed, view=view)
            await rroulette.original_message.delete_original_message()

            countdown_roulette.remove(rroulette)

            return

        countdown = rroulette.countdown - datetime.today()
        await rroulette.original_message.edit_original_message(embed=discord.Embed(color=discord.Colour.purple(), title=f'Countdown Russian roulette - {rroulette.mode}🕔 🔫',
                                                                                   description=f'Quereis jugar a la ruleta rusa?\n\nLa ruleta rusa comienza en `{countdown.seconds}` segundos'))
        print_debug(f"Roulette mode:{rroulette.mode} - {countdown.seconds}")


@tasks.loop(seconds=VOTES_CHECK_TIME)
async def check_votes():
    if not len(votes):
        return

    print_debug(
        f"Votes {[(vote.propuesta[:15], vote.end_time) for vote in votes]}")
    for vote in votes:
        vote.end_time -= timedelta(seconds=VOTES_CHECK_TIME)
        if vote.end_time.total_seconds() <= 0:
            print_debug(
                f"Vote {vote.propuesta[:15]} has ended, now I run notify_vote()")
            await vote.notify_vote()
            votes.remove(vote)  # Remove vote from list
            roles_temp.append([vote.role_1, vote.role_2, datetime.today(
            ) + timedelta(days=1)])  # Deletion of the temporary role

            print_debug(f"Vote {vote.propuesta[:35]} has ended")


@tasks.loop(hours=1)
async def check_temporal_roles():
    if not len(roles_temp):
        return

    print_debug(f"Temporal roles: {roles_temp}")
    for role in roles_temp:
        if role[2] <= datetime.today():
            await role[0].delete()
            await role[1].delete()
            roles_temp.remove(role)
            print_debug(f'Deleted roles: {role[0].name} - {role[1].name}')


@tasks.loop(seconds=REFORMATORY_CHECK_TIME)
async def check_ref_queue():
    if not len(reformatory_cells):
        return

    print_debug(
        f"Reformatory {[(prisoner[0].name, prisoner[2]) for prisoner in reformatory_cells]}")

    for prisoner in reformatory_cells:
        if prisoner[0].voice == None:
            return

        ref_channel = discord.utils.get(
            bot.get_all_channels(), name='⛓ Reformatorio ⛓')

        if prisoner[0].voice.channel != ref_channel:

            await prisoner[0].move_to(discord.utils.get(bot.get_all_channels(), name='⛓ Reformatorio ⛓'))
            jail_time = randrange(MIN_TIME_REFORMATORY, MAX_TIME_REFORMATORY)
            prisoner[2] += jail_time
            print_debug(
                f"{prisoner[0].name} se ha movido a otro canal y se le ha sumado {jail_time} segundos a su condena. Ahora estará durante {prisoner[2]} segundos")

            embed = discord.Embed(color=discord.Colour.purple(), title=f'{ref_channel.name}\n',
                                  description=f'{ prisoner[0].mention} se ha portado mal. \n\n Edit: Se ha movido de canal `+{jail_time}`\nTiempo de reformación: `{prisoner[2]}` segundos 🕐')
            await prisoner[3].edit_original_message(embed=embed)

            prisoner[2] -= REFORMATORY_CHECK_TIME
            embed = discord.Embed(color=discord.Colour.purple(), title=f'{ref_channel.name}\n',
                                  description=f'{ prisoner[0].mention} se ha portado mal. \n\nTiempo de reformación: `{prisoner[2]}` segundos 🕐')
            await prisoner[3].edit_original_message(embed=embed)

        prisoner[2] -= REFORMATORY_CHECK_TIME

        if prisoner[2] <= 0:
            print_debug(
                f"{prisoner[0].name} returns to {prisoner[1]}")
            await prisoner[0].move_to(prisoner[1])
            reformatory_cells.remove(prisoner)
            embed = discord.Embed(color=discord.Colour.purple(), title=f'{ref_channel.name}\n',
                                  description=f'{ prisoner[0].mention} se ha portado mal. \n\n Edit: Tiempo acabado ‼')
            await prisoner[3].edit_original_message(embed=embed, delete_after=5.0)
            print_debug(
                f'{ref_channel.name} has {len(reformatory_cells)} prisoners')
        else:
            embed = discord.Embed(color=discord.Colour.purple(), title=f'{ref_channel.name}\n',
                                  description=f'{ prisoner[0].mention} se ha portado mal. \n\n Tiempo de reformación: `{prisoner[2]}` segundos 🕐')
            await prisoner[3].edit_original_message(embed=embed)


# -------------------------------
# EVENTS
# -------------------------------


@bot.event
async def on_ready():
    print("Bot is Ready, lets go!")
    print_debug("Initialize reformatory task loop")
    check_ref_queue.start()
    print_debug("Initialize vote task loop")
    check_votes.start()
    print_debug("Initialize temporal roles task loop")
    check_temporal_roles.start()
    print_debug("Initialize russian roulette task loop")
    start_russian_roulettes.start()


@bot.event
async def on_raw_reaction_add(payload):
    if payload.member == bot.user:
        return

    # Check reactions in food channel
    await check_food_reactions(payload)


@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return

    # Food Rating
    await set_food_rating(message, FOOD_CHANNEL_ID)


bot.run(TOKEN)
#member = discord.utils.get(message.guild.members, name='Foo')

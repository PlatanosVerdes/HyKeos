import discord
import os
from discord import Colour
from discord.ext import commands
from discord.commands import slash_command, option
from datetime import datetime
from debug import print_debug

FOOD_CHANNEL_ID = 975135205692149801

ONE_STAR_REACTION_ID = 982649189383151636
TWO_STAR_REACTION_ID = 982649186942087188
THREE_STAR_REACTION_ID = 982649184362590358

TOPS = (3, 5, 10)
MONTHS = (
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)

# METHODS
def ranking_icon(rank):
    if rank == 1:
        return "🥇"
    if rank == 2:
        return "🥈"
    if rank == 3:
        return "🥉"
    return "👤"


def get_month(month):
    try:
        return MONTHS.index(month.capitalize()) + 1
    except Exception:
        return -1


async def set_food_rating(message, id_channel):
    if message.attachments == []:
        return

    # Verificar que el mensaje es una imagen
    if message.channel.id == id_channel:
        _, file_extension = os.path.splitext(message.attachments[0].filename)

        # CHECK why inconsitency in emoji
        if file_extension in [".png", ".jpg", "jpeg"]:
            await message.add_reaction("🤮")
            await message.add_reaction(f"<:one_stars:{ONE_STAR_REACTION_ID}>")
            await message.add_reaction(f"<:two_stars:{TWO_STAR_REACTION_ID}>")
            await message.add_reaction(f"<:three_stars:{THREE_STAR_REACTION_ID}>")


# METHODS AUTOCOMPLETE
async def get_months(ctx: discord.AutocompleteContext):
    return [
        month
        for month in MONTHS
        if month.capitalize().startswith(ctx.value.capitalize())
    ]


# PLAYER CLASS
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
        return (
            self.one_stars_value * self.one_stars
            + self.two_stars_value * self.two_stars
            + self.three_stars_value * self.three_stars
        )

    def get_mean_points(self):
        return 0 if self.n_foods == 0 else round(self.get_points() / self.n_foods, 2)


# MAIN CLASS
class Food(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def check_food_reactions(self, payload):
        if payload.channel_id != FOOD_CHANNEL_ID:
            return

        if payload.emoji.id in (
            ONE_STAR_REACTION_ID,
            TWO_STAR_REACTION_ID,
            THREE_STAR_REACTION_ID,
        ) or (payload.emoji.name == "🤮"):

            member = payload.member
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            for reaction in message.reactions:
                async for user in reaction.users():
                    # User must be able to react once and the author cant react to his own message
                    if (reaction.emoji != payload.emoji and user == member) or (
                        message.author == member
                    ):
                        await message.remove_reaction(reaction.emoji, member)

    @slash_command(description="Top 10 mejores comidas 🍽")
    async def food_ratings(self, ctx):

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
                continue  # No reacciones

            players[members.index(message.author)].n_foods += 1

            for reaction in message.reactions:
                if reaction.emoji == one_stars:
                    players[members.index(message.author)].one_stars += (
                        reaction.count - 1
                    )
                elif reaction.emoji == two_stars:
                    players[members.index(message.author)].two_stars += (
                        reaction.count - 1
                    )
                elif reaction.emoji == three_stars:
                    players[members.index(message.author)].three_stars += (
                        reaction.count - 1
                    )

        players.sort(key=FoodPlayer.get_points, reverse=True)
        embed = discord.Embed(
            color=Colour.purple(),
            title="Top 10 Mejores Comidas 🍽",
            description="\n".join(
                f"`{ranking_icon(player_rank+1)} {player.member.name} - {player.get_points()} puntos`"
                for player_rank, player in enumerate(players[:10])
            ),
        )
        await ctx.respond(embed=embed)
        print_debug(
            f"{ctx.author.name} ha usado /food_ratings y ha mostrado los top 10 mejores comidas"
        )

    @slash_command(description="Top Comidas 🍽: Elige top y mes 🍴")
    @option(
        "top",
        description="Top que deseas consultar",
        autocomplete=discord.utils.basic_autocomplete(TOPS),
    )
    @option("month", description="Mes que desas consultar", autocomplete=get_months)
    async def food_ratings_custom(self, ctx, top: int, month: str):
        n_month = get_month(month)

        if n_month == -1:
            await ctx.respond(f"El mes `{month}` no existe...", ephemeral=True)
            return

        if n_month > datetime.today().month:
            await ctx.respond(
                "No se ha inventado el viaje temporal...😅", ephemeral=True
            )
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
            async for message in channel.history(
                after=date_limit_down, before=date_limit_up, limit=None
            ):
                if message.attachments == []:
                    continue  # No Imagenes
                if message.reactions == []:
                    continue  # No reacciones

                players[members.index(message.author)].n_foods += 1

                for reaction in message.reactions:
                    if reaction.emoji == one_stars:
                        players[members.index(message.author)].one_stars += (
                            reaction.count - 1
                        )
                    elif reaction.emoji == two_stars:
                        players[members.index(message.author)].two_stars += (
                            reaction.count - 1
                        )
                    elif reaction.emoji == three_stars:
                        players[members.index(message.author)].three_stars += (
                            reaction.count - 1
                        )

            players.sort(key=FoodPlayer.get_points, reverse=True)
            embed = discord.Embed(
                color=Colour.purple(),
                title=f"Top {top} Mejores Comidas de {MONTHS[n_month-1]} 📅",
                description="\n".join(
                    f"`{ranking_icon(player_rank+1)} {player.member.name} - {player.get_points()} puntos`"
                    for player_rank, player in enumerate(players[:top])
                ),
            )
            await ctx.respond(embed=embed)
            print_debug(
                f"{ctx.author.name} ha usado /food_ratings_custom y ha mostrado los top {top} mejores comidas"
            )

    @slash_command(description="Todas las Estadisticas de Comida de un usuario 🍳")
    @option(
        "top",
        description="Top que deseas consultar",
        autocomplete=discord.utils.basic_autocomplete(TOPS),
    )
    @option("month", description="Mes que desas consultar", autocomplete=get_months)
    async def food_statistics_of(self, ctx, member: discord.Member):
        player = FoodPlayer(member)
        async with ctx.channel.typing():

            channel = ctx.guild.get_channel(FOOD_CHANNEL_ID)
            one_stars = await ctx.guild.fetch_emoji(ONE_STAR_REACTION_ID)
            two_stars = await ctx.guild.fetch_emoji(TWO_STAR_REACTION_ID)
            three_stars = await ctx.guild.fetch_emoji(THREE_STAR_REACTION_ID)

            await ctx.defer()
            async for message in channel.history(after=None, before=None, limit=None):
                if message.attachments == []:
                    continue  # No Imagenes
                if message.reactions == []:
                    continue  # No reacciones
                if message.author != member:
                    continue  # No es el usuario que queremos

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

            embed = discord.Embed(
                color=color,
                title="Estadísticas de la comida 🍽",
                description=f"{member.mention} tiene las siguientes estadísticas\n",
            )
            embed.add_field(name="Puntos", value=f"{player.get_points()}", inline=True)
            embed.add_field(name="Comidas", value=player.n_foods, inline=True)
            embed.add_field(
                name="Media", value=f"{player.get_mean_points()}", inline=True
            )
            embed.add_field(name=f"{one_stars}", value=player.one_stars, inline=True)
            embed.add_field(name=f"{two_stars}", value=player.two_stars, inline=True)
            embed.add_field(
                name=f"{three_stars}", value=player.three_stars, inline=True
            )
            embed.set_footer(
                text=f"{member.name}#{member.discriminator}",
                icon_url=member.display_avatar,
            )

            await ctx.respond(embed=embed)
            print_debug(
                f"{ctx.author.name} ha usado /food_statistics_of y ha mostrado las estadísticas de {member.name}"
            )

    @slash_command(
        description="Eliminar las reacciones de estellas generadas por el bot"
    )
    async def delete_ratings(self, ctx, id_message: str = None):
        channel = ctx.guild.get_channel(FOOD_CHANNEL_ID)
        if channel != ctx.channel:
            await ctx.respond(
                "No puedes eliminar las reacciones de estrellas en este canal",
                ephemeral=True,
            )
            print_debug(
                f"{ctx.author.name} ha intentado eliminar las reacciones de estrellas en un canal distinto al de comidas"
            )
            return

        # If the message is not specified, delete the last message
        if id_message in ("", " ", None):
            messages = await channel.history(limit=1).flatten()
            message = messages[0]
        else:
            partial_message = channel.get_partial_message(id_message)
            if partial_message is None:
                await ctx.respond(
                    f"No se ha encontrado el mensaje con ID `{id_message}`",
                    ephemeral=True,
                )
                print_debug(
                    f"{ctx.author.name} ha usado /delete_ratings y ha intentado eliminar las reacciones de un mensaje con ID {id_message}"
                )
                return

            message = await partial_message.fetch()

        # If member havent permissions
        if not (
            (ctx.author.guild_permissions.administrator)
            or (message.author == ctx.author)
        ):
            await ctx.respond(
                "No puedes eliminar las reacciones de estrellas de otros usuarios",
                ephemeral=True,
            )
            return

        # If message dont have reactions
        if message.reactions == []:
            await ctx.respond(
                "No se han encontrado reacciones en el mensaje",
                ephemeral=True,
            )
            return

        await message.clear_reactions()
        embed = discord.Embed(
            color=Colour.purple(),
            title="Reacciones de eliminadas",
            description=f"Las reacciones de valoracion han sido eliminadas",
        )
        embed.add_field(
            name="Mensaje eliminado",
            value=f"{message.jump_url}",
            inline=False,
        )
        embed.add_field(
            name="Autor del mensaje eliminado",
            value=f"{message.author.mention}",
            inline=False,
        )
        await ctx.respond(embed=embed)
        print_debug(
            f"{ctx.author.name} ha usado /delete_ratings y ha eliminado las reacciones de {message.author.name}"
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Food Rating
        await set_food_rating(message, FOOD_CHANNEL_ID)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        # Check reactions in food channel
        await self.check_food_reactions(payload)


def setup(bot):
    bot.add_cog(Food(bot))

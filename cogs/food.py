import discord
from discord.commands import commands
from discord import Colour


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


class Food(commands.Cog, name="Food"):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Top 10 mejores comidas 🍽")
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
                continue  # No reacciones

            print_debug("Reaccion")

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

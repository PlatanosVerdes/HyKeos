import json
from discord.ext import commands
from discord.commands import slash_command, option
from debug import print_debug


class Movies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Añade una pelicula a la lista de peliculas 🎞")
    @option("Pelicula", description="Escribe el nombre de la pelicula")
    async def add_movie(self, ctx, title: str):
        if title == "":
            await ctx.respond("Debes escribir el nombre de la pelicula", ephemeral=True)
            return

        # Añadir pelicula al json de peliculas
        with open("movies.json") as f:
            movies = json.load(f)
        # data = {"ID": len(movies), "Title": title, "Adder": ctx.author.name,"Date": datetime.now().strftime("%y%f%d%W%S")}
        # movies[0].append(data)
        # with open('movies.json', 'w') as f:
        #    json.dump(movies, f, ensure_ascii=False,)
        await ctx.respond(f"Pelicula añadida a la lista de peliculas")
        print_debug(
            f"{ctx.author.name} ha usado /add_movie y ha añadido la pelicula {title}"
        )


def setup(bot):
    bot.add_cog(Movies(bot))
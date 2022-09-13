import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, option
from random import randint, choice, shuffle
from datetime import datetime, timedelta
from debug import print_debug

countdown_roulette = []
RROULETTE_CHECK_TIME = 1
COUNTDOWN_RROULETTE = 15

# CLASS of RussianRoulete
class RRoulette:
    revolvers = [
        ["Nagant M1895", 7],
        ["Swiss Mini Gun C1ST", 6],
        ["Remington Model 1887", 6],
        ["Magnum", 5],
        ["LeMat", 9],
    ]

    def __init__(
        self,
        id_rr,
        countdown,
        voice_channel,
        players=[],
        new_voice_channel=None,
        original_message=None,
        mode="Easy",
    ):
        super().__init__()
        self.id = id_rr
        self.players = players
        self.voice_channel = voice_channel
        self.new_voice_channel = new_voice_channel
        self.countdown = countdown
        self.revolver = choice(self.revolvers)
        self.original_message = original_message
        self.mode = mode

    def get_drum(self):
        bullet = randint(0, self.revolver[1] - 1)
        drum = []
        for i in range(self.revolver[1]):
            if i == bullet:
                drum.append(1)
            else:
                drum.append(0)
        return drum


# CLASS VIEW
class RRouletteView(discord.ui.View):
    def __init__(self, rroulette, drum=[], drum_order=[], drum_index=0):
        super().__init__(timeout=None)
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
                f"{interaction.user.mention} Espera a tu turno impaciente",
                delete_after=3,
            )
            print_debug(f"{interaction.user} tiene que esperar a su turno")
            return

        # Check if the player is the last in the order
        if self.drum_index == len(self.drum):
            self.set_drum()  # Set the new drum

        # Get the embed message
        original_embed = interaction.message.embeds[0]

        # Checks if the player has already been shot
        if self.drum[self.drum_index] == 1:
            original_embed.add_field(name="Resultado", value="💀")
            print_debug(f"{interaction.user} ha muerto")

            # Check if the mode is Easy
            if self.rroulette.mode == "Easy":
                await interaction.user.move_to(self.rroulette.voice_channel)
            else:
                await interaction.user.kick(
                    reason="Has sido expulsado jugando a la ruleta rusa"
                )

            # Remove the player from the rroulette
            self.rroulette.players.remove(interaction.user)
            self.set_drum()

        # If the player has not been shot, shoot next player
        else:
            self.drum_index += 1
            print_debug(f"{interaction.user} sigue vivo")
            original_embed.add_field(name="Resultado", value="❤")

        # Check if there is one left in the roulette wheel
        if len(self.rroulette.players) == 1:
            await interaction.channel.send(
                f"{self.rroulette.players[0].mention} ha ganado la ruleta rusa 🎉"
            )

            await self.add_role(interaction, self.rroulette.mode)

            print_debug(f"{self.rroulette.players[0]} ha ganado la rroulette")
            # Check if the mode is Easy
            if self.rroulette.mode == "Easy":
                await self.rroulette.players[0].move_to(self.rroulette.voice_channel)
                await self.rroulette.new_voice_channel.delete()
                print_debug("Se ha eliminado el canal de voz de la ruleta rusa")

            button.disabled = True
            await interaction.response.edit_message(embed=original_embed, view=self)
            self.rroulette.players.clear()
            return

        # Edit original message with the result and disable button
        button.disabled = True
        await interaction.response.edit_message(embed=original_embed, view=self)

        # New message with next player
        embed = discord.Embed(
            color=discord.Colour.purple(),
            title="Russian Roulette\n",
            description="Cuidado no mueras!\n",
        )
        embed.add_field(
            name="Turno",
            value=f"{self.drum_order[self.drum_index].mention}",
            inline=True,
        )
        embed.add_field(name="Modo", value=f"{self.rroulette.mode}", inline=True)
        embed.add_field(
            name="Revolver", value=f"{self.rroulette.revolver[0]}", inline=True
        )
        embed.add_field(
            name="Recamara",
            value=f"[{self.drum_index}/{self.rroulette.revolver[1]}]",
            inline=True,
        )

        view = RRouletteView(
            self.rroulette, self.drum, self.drum_order, self.drum_index
        )
        await interaction.channel.send(embed=embed, view=view)

    # Set the new drum
    def set_drum(self):

        self.drum = self.rroulette.get_drum()
        self.drum_order = self.rroulette.players

        shuffle(self.drum_order)

        if len(self.drum) > len(self.rroulette.players):
            self.drum_order = self.drum_order * (
                len(self.drum) - len(self.rroulette.players)
            )
        elif len(self.drum) < len(self.rroulette.players):
            self.drum_order = self.drum_order[: len(self.drum)]

        self.drum_index = 0

    # Add the role to the player
    async def add_role(self, interaction, mode):
        # Catch the level of player
        level = 0
        # Get the roles of the last player
        roles_user = self.rroulette.players[0].roles
        for role in roles_user:
            if role.name.startswith(f"Ruleta Rusa {mode}"):
                if level < int(role.name[-1]):
                    level = int(role.name[-1])

        print_debug(f"El ganador tiene Nivel: {level}")
        roles = interaction.guild.roles

        # Check the next level exist
        next_level = 0
        for role in roles:
            if (
                role.name.startswith(f"Ruleta Rusa {mode}")
                and int(role.name[-1]) == level + 1
            ):
                next_level = role
                break

        if next_level != 0:
            print_debug(f"El siguiente nivel es: {next_level}")
            await self.rroulette.players[0].add_roles(next_level)
            print_debug(
                f"{self.rroulette.players[0]} ha subido de nivel - Modo: {mode}"
            )
        else:
            print_debug(
                f"No hay nivel siguiente - se crea el siguiente nivel: {level + 1}"
            )
            if mode == "Easy":
                color = discord.Color.yellow()
            else:
                color = discord.Color.red()
            new_role = await interaction.guild.create_role(
                name=f"Ruleta Rusa {mode} - N{level + 1}",
                color=color,
                permissions=discord.Permissions(permissions=2150878272),
                mentionable=True,
                reason=f"Siguiente Nivel de la Ruleta Rusa {mode}",
            )
            await self.rroulette.players[0].add_roles(new_role)


class PrepareRRouletteView(discord.ui.View):
    def __init__(self, potential_players, rroulette_id):
        super().__init__(timeout=None)
        self.potential_players = potential_players
        self.rroulette_id = rroulette_id

        self.players_count = 0

    @discord.ui.button(label="Aceptar", row=0, style=discord.ButtonStyle.success)
    async def acept_button_callback(self, _, interaction):

        if interaction.user not in self.potential_players:
            await interaction.response.send_message(
                f"{interaction.user.mention} no estás en el canal de voz.",
                ephemeral=True,
            )
            print_debug(f"{interaction.user} no está en el canal de voz")
            return

        for rroulette in countdown_roulette:
            if rroulette.id == self.rroulette_id:
                if interaction.user in rroulette.players:
                    await interaction.response.send_message(
                        f"{interaction.user.mention} ya estás en la ruleta rusa.",
                        delete_after=3,
                    )
                    print_debug(f"{interaction.user} ya está en la ruleta rusa ‼")
                    return

                await interaction.response.send_message(
                    f"{interaction.user.mention} ha aceptado la partida de Russian Roulette ✅",
                    delete_after=3,
                )
                print_debug(
                    f"{interaction.user.name} ha aceptado a jugar en partida de Russian Roulette."
                )

                # Add the player to the rroulette
                rroulette.players.append(interaction.user)
                self.players_count += 1

                # Check is the last player has joined the rroulette
                if self.players_count == len(self.potential_players):
                    print_debug("Ya han votado a todos los jugadores.")
                    await interaction.channel.send(
                        "Ya han votado a todos los jugadores.", delete_after=3
                    )
                    rroulette.countdown = datetime.today()
                return


# MAIN CLASS
class RussianRoulete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Vamos a jugar a la ruleta rusa 👤🔫")
    @option(
        "mode",
        description="Elige el tipo de modo",
        autocomplete=discord.utils.basic_autocomplete(["Easy", "Hard"]),
    )
    async def russian_roulette(ctx, mode: str):
        if mode not in ("Easy", "Hard"):
            await ctx.respond("El modo debe ser Easy o Hard", ephemeral=True)
            return

        if ctx.author.voice is None:
            print_debug(
                f"{ctx.author.name} ha intentado jugar a la ruleta rusa sin estar en un canal de voz"
            )
            await ctx.respond(
                "Debes estar en un canal de voz para jugar a la ruleta rusa",
                ephemeral=True,
            )
            return

        potential_players = ctx.author.voice.channel.members

        if len(potential_players) < 2:
            await ctx.respond(
                "Debe de haber por lo menos dos jugadores para poder jugar",
                ephemeral=True,
            )
            print_debug(
                f"{ctx.author.name} ha intentado jugar a la ruleta rusa en un canal de voz con menos de dos jugadores"
            )
            return

        rroulette = RRoulette(
            datetime.now().strftime("%y%f%d%W%S"),
            datetime.today() + timedelta(seconds=COUNTDOWN_RROULETTE),
            ctx.author.voice.channel,
            mode=mode,
        )

        embed = discord.Embed(
            color=discord.Colour.purple(),
            title=f"Countdown Russian roulette {mode} 🕔 🔫",
            description=f"Quereis jugar a la ruleta rusa?\n\nLa ruleta rusa comienza en `{COUNTDOWN_RROULETTE}` segundos",
        )
        message = await ctx.respond(
            embed=embed, view=PrepareRRouletteView(potential_players, rroulette.id)
        )
        rroulette.original_message = message

        countdown_roulette.append(rroulette)

    @slash_command(description="Eliminar canales de ruleta rusa")
    async def delete_roulette_channels(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "No tienes permisos para eliminar roles de votación", ephemeral=True
            )
            return

        await ctx.defer()
        for channel in ctx.guild.channels:
            if channel.name.startswith("Ruleta"):
                await channel.delete()
        await ctx.respond("Canales de ruleta rusa eliminados")
        print_debug(
            f"{ctx.author.name} ha usado /delete_vote_roles y ha eliminado los roles de votación"
        )

    @tasks.loop(seconds=RROULETTE_CHECK_TIME)
    async def start_russian_roulettes(self):
        if not len(countdown_roulette):
            return

        for rroulette in countdown_roulette:
            if rroulette.countdown < datetime.now():
                if len(rroulette.players) < 2:
                    print_debug(
                        "No se ha podido iniciar la ruleta rusa porque no hay suficientes jugadores"
                    )
                    await rroulette.original_message.delete_original_message()
                    countdown_roulette.remove(rroulette)
                    return

                if rroulette.mode == "Easy":
                    new_voice_channel = (
                        await rroulette.voice_channel.category.create_voice_channel(
                            name="Ruleta rusa 👤🔫"
                        )
                    )
                    rroulette.new_voice_channel = new_voice_channel

                    for player in rroulette.players:
                        await player.move_to(new_voice_channel)

                view = RRouletteView(rroulette)
                embed = discord.Embed(
                    color=discord.Colour.purple(),
                    title=f"Russian Roulette - {rroulette.mode}\n",
                    description="Cuidado no mueras!\n",
                )
                embed.add_field(
                    name="Turno", value=f"{view.drum_order[0].mention}", inline=True
                )
                embed.add_field(name="Modo", value=f"{rroulette.mode}", inline=True)
                embed.add_field(
                    name="Revolver", value=f"{rroulette.revolver[0]}", inline=True
                )
                embed.add_field(
                    name="Recamara", value=f"[{0}/{rroulette.revolver[1]}]", inline=True
                )

                await rroulette.original_message.channel.send(embed=embed, view=view)
                await rroulette.original_message.delete_original_message()

                countdown_roulette.remove(rroulette)
                return

            countdown = rroulette.countdown - datetime.today()
            await rroulette.original_message.edit_original_message(
                embed=discord.Embed(
                    color=discord.Colour.purple(),
                    title=f"Countdown Russian roulette - {rroulette.mode}🕔 🔫",
                    description=f"Quereis jugar a la ruleta rusa?\n\nLa ruleta rusa comienza en `{countdown.seconds}` segundos",
                )
            )
            print_debug(f"Roulette mode:{rroulette.mode} - {countdown.seconds}")
    
    @commands.Cog.listener()
    async def on_ready(self):
        
        self.start_russian_roulettes.start()
        print_debug("Initialize russian roulette task loop")


def setup(bot):
    bot.add_cog(RussianRoulete(bot))

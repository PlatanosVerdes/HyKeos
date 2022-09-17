import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, option
from datetime import datetime, timedelta
from debug import print_debug

TIMES = ("Dias", "Horas", "Minutos")

VOTES_CHECK_TIME = 5
TEMP_ROLES_CHECK_TIME = 24
votes = []
roles_temp = []

# To get type of times in vote
async def get_type_times(ctx: discord.AutocompleteContext):
    return [
        time for time in TIMES if time.capitalize().startswith(ctx.value.capitalize())
    ]


# Class to View Votes
class VoteView(discord.ui.View):
    def __init__(
        self,
        ctx,
        propuesta,
        role_1,
        role_2,
        end_time=timedelta(hours=1),
        emoji_1="✅",
        emoji_2="❌",
        message_id=None,
    ):
        super().__init__(timeout=None)
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

        self.button1 = discord.ui.Button(style=discord.ButtonStyle.grey, emoji=emoji_1)
        self.button2 = discord.ui.Button(style=discord.ButtonStyle.grey, emoji=emoji_2)

        self.button1.callback = self.button1_callback
        self.button2.callback = self.button2_callback

        self.add_item(self.button1)
        self.add_item(self.button2)

    async def notify_vote(self):

        if not (len(self.voters_1) or len(self.voters_2)):
            print_debug("Nadie ha votado")
            embed = discord.Embed(
                color=discord.Colour.purple(),
                title="Votación Eliminada\n",
                description=f"Autor: {self.ctx.author.mention}\nPropuesta: `{self.propuesta}`\n\nHa sido eliminada, nadie ha interactuado con ella",
            )

        elif len(self.voters_1) > len(self.voters_2):
            embed = discord.Embed(
                color=discord.Colour.purple(),
                title="Votación Terminada\n",
                description=f"Autor: {self.ctx.author.mention}\nPropuesta: `{self.propuesta}`\n\n",
            )

            embed.add_field(
                name="Propuesta ganadora", value=f"{self.emoji_1}", inline=True
            )

            embed.add_field(
                name=f"Votantes de {self.emoji_1} - `{len(self.voters_1)} 👤`",
                value=f"||{self.role_1.mention}||",
            )
            embed.add_field(
                name=f"Votantes de {self.emoji_2} - `{len(self.voters_2)} 👤`",
                value=f"||{self.role_2.mention}||",
            )

        elif len(self.voters_1) < len(self.voters_2):
            embed = discord.Embed(
                color=discord.Colour.purple(),
                title="Votación Terminada\n",
                description=f"Autor: {self.ctx.author.mention}\nPropuesta: `{self.propuesta}`\n\n",
            )

            embed.add_field(name="Propuesta ganadora", value=f"{self.emoji_1}")

            embed.add_field(
                name=f"Votantes de {self.emoji_1} - `{len(self.voters_1)} 👤`",
                value=f"||{self.role_1.mention}||",
            )
            embed.add_field(
                name=f"Votantes de {self.emoji_2} - `{len(self.voters_2)} 👤`",
                value=f"||{self.role_2.mention}||",
            )
        else:
            embed = discord.Embed(
                color=discord.Colour.purple(),
                title="Votación Empatada\n",
                description=f"Autor: {self.ctx.author.mention}\nPropuesta: `{self.propuesta}`\n\n",
            )

            embed.add_field(
                name=f"Votantes de {self.emoji_1} - `{len(self.voters_1)} 👤`",
                value=f"||{self.role_1.mention}||",
            )
            embed.add_field(
                name=f"Votantes de {self.emoji_2} - `{len(self.voters_2)} 👤`",
                value=f"||{self.role_2.mention}||",
            )

        print_debug(
            f"Votacion {self.propuesta[:15]} terminada - Notificando a {len(self.voters_1) + len(self.voters_2)} usuarios"
        )

        await self.ctx.channel.send(embed=embed)

    # Buttons reactions
    async def button1_callback(self, interaction: discord.Interaction):
        if interaction.user in self.voters_1:
            await interaction.response.send_message(
                f"{interaction.user.mention} ya has votado", ephemeral=True
            )
            return

        if interaction.user in self.voters_2:
            # Remove user from second list
            self.voters_2.remove(interaction.user)

            await interaction.user.remove_roles(self.role_2)

        self.voters_1.append(interaction.user)  # Add user to first list
        await interaction.user.add_roles(self.role_1)  # Add role to user

        embed = discord.Embed(
            color=discord.Colour.purple(),
            title="Votación Abierta\n",
            description=f"**Propuesta:** {self.propuesta}\n\n📩 By: {self.ctx.author.mention}\n--------------------------",
        )
        embed.add_field(
            name=f"{self.emoji_1}", value=f"{len(self.voters_1)}", inline=True
        )
        embed.add_field(
            name=f"{self.emoji_2}", value=f"{len(self.voters_2)}", inline=True
        )
        await interaction.response.edit_message(embed=embed)
        print_debug(f"{interaction.user.name} ha votado {self.emoji_1}")

    async def button2_callback(self, interaction: discord.Interaction):
        if interaction.user in self.voters_2:
            await interaction.response.send_message(
                f"{interaction.user.mention} ya has votado", ephemeral=True
            )
            return

        if interaction.user in self.voters_1:
            # Remove user from first list
            self.voters_1.remove(interaction.user)
            await interaction.user.remove_roles(self.role_1)

        self.voters_2.append(interaction.user)  # Add user to second list
        await interaction.user.add_roles(self.role_2)  # Add role to user

        embed = discord.Embed(
            color=discord.Colour.purple(),
            title="Votación Abierta\n",
            description=f"**Propuesta:** {self.propuesta}\n\n📩 By: {self.ctx.author.mention}\n--------------------------",
        )
        embed.add_field(
            name=f"{self.emoji_1}", value=f"{len(self.voters_1)}", inline=True
        )
        embed.add_field(
            name=f"{self.emoji_2}", value=f"{len(self.voters_2)}", inline=True
        )
        await interaction.response.edit_message(embed=embed)
        print_debug(f"{interaction.user.name} ha votado {self.emoji_2}")


# Main class
class Votes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Abre una votación 📩 con ✅ y ❌")
    @option("type_time", description="Tipo de duración", autocomplete=get_type_times)
    @option(
        "timeout",
        description="Duración",
        autocomplete=discord.utils.basic_autocomplete(range(1, 60)),
    )
    @option("propuesta", description="Tema de votación")
    async def vote(self, ctx, propuesta: str, type_time: str, timeout: int):
        if type_time.lower() not in [type_t.lower() for type_t in TIMES]:
            await ctx.respond(
                f"Tipo de duración no reconocido `{type_time}`", ephemeral=True
            )
            print_debug(
                f"{ctx.author.name} ha usado /vote pero el tipo de duración {type_time} no es reconocido"
            )
            return

        embed = discord.Embed(
            color=discord.Colour.purple(),
            title="Votación Abierta\n",
            description=f"**Propuesta:** {propuesta}\n\n📩 By: {ctx.author.mention}",
        )

        time = datetime.now().strftime("%y%f%d")
        role_1 = await ctx.guild.create_role(
            name=f"V_R1{time}",
            color=discord.Colour.green(),
            permissions=discord.Permissions(permissions=2150878272),
            mentionable=True,
            reason="Para mencionar en la votacion",
        )
        role_2 = await ctx.guild.create_role(
            name=f"V_R2{time}",
            color=discord.Colour.red(),
            permissions=discord.Permissions(permissions=2150878272),
            mentionable=True,
            reason="Para mencionar en la votacion",
        )

        if type_time.lower() == "dias":
            vote = VoteView(
                ctx, propuesta, role_1, role_2, end_time=timedelta(days=timeout)
            )
        elif type_time.lower() == "horas":
            vote = VoteView(
                ctx, propuesta, role_1, role_2, end_time=timedelta(hours=timeout)
            )
        elif type_time.lower() == "minutos":
            vote = VoteView(
                ctx, propuesta, role_1, role_2, end_time=timedelta(minutes=timeout)
            )

        interaction = await ctx.respond(embed=embed, view=vote)
        vote.message_id = interaction.id
        votes.append(vote)
        print_debug(f"{ctx.author.name} ha usado /vote y ha abierto una votación")

    @slash_command(description="Abre una votación 📩 con reacciones personalizadas 🎨")
    @option("type_time", description="Tipo de duración", autocomplete=get_type_times)
    @option(
        "timeout",
        description="Duración",
        autocomplete=discord.utils.basic_autocomplete(range(1, 60)),
    )
    @option("propuesta", description="Tema de votación")
    @option("reaccion 1", description="Pon la primer reacción")
    @option("reaccion 2", description="Pon la segunda reacción")
    async def vote_custom(
        self,
        ctx,
        type_time: str,
        timeout: int,
        propuesta: str,
        emoji_1: str,
        emoji_2: str,
    ):
        if type_time.lower() not in [type_t.lower() for type_t in TIMES]:
            await ctx.respond(
                f"Tipo de duración no reconocido `{type_time}`", ephemeral=True
            )
            return
        if emoji_1 == emoji_2:
            await ctx.respond("No puedes poner las mismas reacciones", ephemeral=True)
            return

        embed = discord.Embed(
            color=discord.Colour.purple(),
            title="Votación Abierta\n",
            description=f"**Propuesta:** {propuesta}\n\n📩 By: {ctx.author.mention}",
        )

        time = datetime.now().strftime("%y%f%d")
        role_1 = await ctx.guild.create_role(
            name=f"V_R1{time}",
            color=discord.Colour.green(),
            permissions=discord.Permissions(permissions=2150878272),
            mentionable=True,
            reason="Para mencionar en la votacion",
        )
        role_2 = await ctx.guild.create_role(
            name=f"V_R2{time}",
            color=discord.Colour.red(),
            permissions=discord.Permissions(permissions=2150878272),
            mentionable=True,
            reason="Para mencionar en la votacion",
        )

        if type_time.lower() == "dias":
            vote = VoteView(
                ctx,
                propuesta,
                role_1,
                role_2,
                end_time=timedelta(days=timeout),
                emoji_1=emoji_1,
                emoji_2=emoji_2,
            )
        elif type_time.lower() == "horas":
            vote = VoteView(
                ctx,
                propuesta,
                role_1,
                role_2,
                end_time=timedelta(hours=timeout),
                emoji_1=emoji_1,
                emoji_2=emoji_2,
            )
        elif type_time.lower() == "minutos":
            vote = VoteView(
                ctx,
                propuesta,
                role_1,
                role_2,
                end_time=timedelta(minutes=timeout),
                emoji_1=emoji_1,
                emoji_2=emoji_2,
            )

        message = await ctx.respond(embed=embed, view=vote)
        vote.message = message
        votes.append(vote)
        print_debug(
            f"{ctx.author.name} ha usado /vote_custom y ha abierto una votación"
        )
    
    @slash_command(description="Eliminar roles de votacion")
    async def delete_vote_roles(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond(
                "No tienes permisos para eliminar roles de votación", ephemeral=True
            )
            return

        # Delete all roles
        for role in ctx.guild.roles:
            if role.name.startswith("V_R"):
                await role.delete()
        await ctx.respond("Roles de votación eliminados")
        print_debug(
            f"{ctx.author.name} ha usado /delete_vote_roles y ha eliminado los roles de votación"
        )

    @tasks.loop(seconds=VOTES_CHECK_TIME)
    async def check_votes(self):
        if not len(votes):
            return

        print_debug(f"Votes {[(vote.propuesta[:15], vote.end_time) for vote in votes]}")
        for vote in votes:
            vote.end_time -= timedelta(seconds=VOTES_CHECK_TIME)
            if vote.end_time.total_seconds() <= 0:
                print_debug(
                    f"Vote {vote.propuesta[:15]} has ended, now I run notify_vote()"
                )
                await vote.notify_vote()
                votes.remove(vote)  # Remove vote from list
                roles_temp.append(
                    [vote.role_1, vote.role_2, datetime.today() + timedelta(days=1)]
                )  # Deletion of the temporary role
                print_debug(f"Vote {vote.propuesta[:35]} has ended")

    @tasks.loop(hours=TEMP_ROLES_CHECK_TIME)
    async def check_temporal_roles(self):
        if not len(roles_temp):
            return

        print_debug(f"Temporal roles: {roles_temp}")
        for role in roles_temp:
            if role[2] <= datetime.today():
                await role[0].delete()
                await role[1].delete()
                roles_temp.remove(role)
                print_debug(f"Deleted roles: {role[0].name} - {role[1].name}")

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_votes.start()
        print_debug("Initialize vote task loop")

        self.check_temporal_roles.start()
        print_debug("Initialize temporal roles task loop")


def setup(bot):
    bot.add_cog(Votes(bot))

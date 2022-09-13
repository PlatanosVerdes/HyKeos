import discord
from discord import Colour, Embed
from discord.ext import commands
from discord.commands import slash_command, option
from datetime import datetime
from debug import print_debug

ROLE_CHANNEL_ID = 982345257142325269

# CLASS VIEW
class PlsRoleView(discord.ui.View):
    def __init__(self, user, role, reason, roles):
        super().__init__(timeout=None)
        self.user = user
        self.role = role
        self.reason = reason
        self.roles = roles
        self.date = datetime.today()

    @discord.ui.button(label="Aceptar", row=0, style=discord.ButtonStyle.success)
    async def first_button_callback(self, _, interaction):
        print_debug(f"Acepted")
        await self.user.add_roles(self.role)
        print_debug(f"se ha añadido el rol {self.role.name} a {self.user.name}")

        await interaction.response.send_message(
            f"{interaction.user.mention} ha aceptado a {self.user.mention}, ahora es {self.role.mention} 🎉"
        )
        print_debug(f"se ha enviado un mensaje por el canal {interaction.channel.name}")

        await interaction.message.delete()
        print_debug(f"se ha eliminado el mensaje {interaction.message.id}")

        fecha = (
            f"Inicio: `{self.date.strftime('%m/%d/%Y %H:%M:%S')}"
            + f"`\nAprovada: `{datetime.today().strftime('%m/%d/%Y %H:%M:%S')}`"
        )
        embed = discord.Embed(
            color=Colour.purple(),
            title="Solicitud: Aceptada ✅",
            description=f"\nRol: `{self.role.name.upper()}`\nMotivo: `{self.reason}`\n\n{fecha}",
        )

        await self.user.send(embed=embed)
        print_debug(f"se ha enviado un mensaje privado a {self.user.name}")

        print_debug(f"{interaction.user.name} ha aceptado a {self.user.name}")

    @discord.ui.button(label="Rechazar", row=0, style=discord.ButtonStyle.danger)
    async def second_button_callback(self, _, interaction):

        await interaction.response.send_message(
            f"{interaction.user.mention} ha denegado a {self.user.mention} a ser {self.role.mention} 💀"
        )
        await interaction.message.delete()

        fecha = (
            f"Inicio: `{self.date.strftime('%m/%d/%Y %H:%M:%S')}"
            + f"`\nDenegada: `{datetime.today().strftime('%m/%d/%Y %H:%M:%S')}`"
        )
        embed = discord.Embed(
            color=Colour.purple(),
            title="Solicitud: Denegada ❌",
            description=f"\nRol: `{self.role.name.upper()}`\nMotivo: `{self.reason}`\n\n{fecha}",
        )
        await self.user.send(embed=embed)
        print_debug(
            f"{interaction.user.name} ha denegado a {self.user.name} a ser {self.role.name}"
        )


# Main class
class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Para ver todos los roles 👀")
    async def roles(self, ctx):
        # Slice roles to not take into account the "@everyone" role
        roles = [rol for rol in ctx.guild.roles[1::] if not rol.is_bot_managed()]

        roles = sorted(roles, key=lambda x: x.position, reverse=True)
        counted_roles = [len(rol.members) for rol in roles]

        embed = Embed(
            color=Colour.purple(),
            title=f"Roles de {ctx.guild.name}",
            description="\n".join(
                f"{role.mention} - `{counted_roles[i]} 👤`"
                for i, role in enumerate(roles)
            ),
        )
        await ctx.respond(embed=embed)
        print_debug(f"{ctx.author.name} ha usado /roles")

    @slash_command(description="Pide un rol al admin 🙋🏻‍♂️")
    @option("rol", description="Rol que solicitas")
    @option(
        "motivo", description="Escribe una breve descripción argumentando tu petición"
    )
    async def pls_rol(self, ctx, rol: discord.Role, reason: str):
        roles = ctx.guild.roles
        if rol not in roles:
            await ctx.respond(
                f"No se ha encontrado el rol `{rol.name}`...😔", ephemeral=True
            )
            print_debug(
                f"{ctx.author.name} ha usado /{ctx.command.name} pero no existe el rol {rol.name}"
            )
            return

        if rol in ctx.author.roles:
            await ctx.respond(f"Ya tienes el rol {rol.mention}", ephemeral=True)
            print_debug(
                f"{ctx.author.name} ha usado /{ctx.command.name} pero ya tiene el rol {rol.name}"
            )
            return

        embed = discord.Embed(
            color=discord.Colour.purple(),
            title="Petición de Rol",
            description=f"Autor: {ctx.author.mention} \n\nRol: {rol.mention} \n Motivo: `{reason}`",
        )
        await ctx.guild.get_channel(ROLE_CHANNEL_ID).send(
            embed=embed, view=PlsRoleView(ctx.author, rol, reason, roles)
        )
        await ctx.respond("Petición enviada correctamente ✅", ephemeral=True)
        print_debug(
            f"{ctx.author.name} ha usado /{ctx.command.name} y ha enviado una petición de rol para {rol.name}"
        )

    @slash_command(description="Quitate un rol ❌🙋🏻‍♂️")
    @option("rol", description="Rol que deseas eliminarte")
    async def delete_rol(self, ctx, rol: discord.Role):
        roles = ctx.guild.roles
        if rol not in roles:
            await ctx.respond(
                f"No se ha encontrado el rol `{rol.name}`...😔", ephemeral=True
            )
            print_debug(
                f"{ctx.author.name} ha usado /{ctx.command.name} pero no existe el rol {rol.name}"
            )
            return

        if not rol in ctx.author.roles:
            await ctx.respond(f"No tienes el rol {rol.mention}", ephemeral=True)
            print_debug(
                f"{ctx.author.name} ha usado /{ctx.command.name} pero no tiene el rol {rol.name}"
            )
            return

        await ctx.author.remove_roles(rol)

        await ctx.respond(f"{rol.mention} eliminado correctamente ✅", ephemeral=True)
        print_debug(f"{ctx.author.name} ha usado /{ctx.command.name} {rol.name}")


def setup(bot):
    bot.add_cog(Roles(bot))

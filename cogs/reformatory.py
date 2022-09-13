import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, option
from random import randrange
from debug import print_debug

# REFORMATORY
REFORMATORY_CHANNEL_ID = 985583574021443584

NAME_OF_CHANNEL = "⛓ Reformatorio ⛓"

reformatory_cells = []
REFORMATORY_CHECK_TIME = 2
MIN_TIME_REFORMATORY = 10
MAX_TIME_REFORMATORY = 60

# CLASS
class Reformatory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
    description="Al reformatorio! ⛓. Debe de existir el canal con el nombre: ⛓ Reformatorio ⛓"
    )
    @option("member", description="Quien se ha portado mal? 🤔")
    async def reformatory(self, ctx, member: discord.Member):
        # Mirar si tiene el rol de reformatorio o administrador
        if not (
            (ctx.author.guild_permissions.administrator)
            or ("Staff Reformatory" in [role.name for role in ctx.author.roles])
        ):
            await ctx.respond(f"{ctx.author.mention} No tienes permisos para hacer eso! 🤔")
            print_debug(f"{ctx.author.name} ha usado /reformatory pero no tiene permisos")
            return
    
        name_channel = NAME_OF_CHANNEL
        channel_reformatory = discord.utils.get(ctx.guild.voice_channels, name=name_channel)
    
        if channel_reformatory is None:
            await ctx.respond(f"No existe el canal {name_channel}", ephemeral=True)
            print_debug(
                f"{ctx.author.name} ha usado /reformatory pero no existe el canal {name_channel}"
            )
            return
    
        if member.voice is None:
            await ctx.respond(
                f"{member.mention} no esta en un canal de voz", ephemeral=True
            )
            print_debug(
                f"{ctx.author.name} ha usado /reformatory pero {member.name} no esta en un canal de voz"
            )
            return
    
        current_channel = member.voice.channel
        await member.move_to(channel_reformatory)
    
        # Añadir a la cola de reformatorio
        # user, current_channel, time
        jail_time = randrange(MIN_TIME_REFORMATORY, MAX_TIME_REFORMATORY)
    
        embed = discord.Embed(
            color=discord.Colour.purple(),
            title=f"{name_channel}\n",
            description=f"{member.mention} se ha portado mal. \n\n Tiempo de reformación: `{jail_time}` segundos 🕐",
        )
        message = await ctx.respond(embed=embed)
    
        reformatory_cells.append([member, current_channel, jail_time, message])
        print_debug(
            f"{ctx.author.name} ha usado /reformatory y ha añadido a {member.name} a la cola de reformatorio"
        )
    

    @tasks.loop(seconds=REFORMATORY_CHECK_TIME)
    async def check_ref_queue(self):
        if not len(reformatory_cells):
            return

        print_debug(
            f"Reformatory {[(prisoner[0].name, prisoner[2]) for prisoner in reformatory_cells]}"
        )

        for prisoner in reformatory_cells:
            if prisoner[0].voice is None:
                return

            ref_channel = discord.utils.get(self.bot.get_all_channels(), name=NAME_OF_CHANNEL)

            if prisoner[0].voice.channel != ref_channel:

                await prisoner[0].move_to(
                    discord.utils.get(self.bot.get_all_channels(), name=NAME_OF_CHANNEL)
                )
                jail_time = randrange(MIN_TIME_REFORMATORY, MAX_TIME_REFORMATORY)
                prisoner[2] += jail_time
                print_debug(
                    f"{prisoner[0].name} se ha movido a otro canal y se le ha sumado {jail_time} segundos a su condena. Ahora estará durante {prisoner[2]} segundos"
                )

                embed = discord.Embed(
                    color=discord.Colour.purple(),
                    title=f"{ref_channel.name}\n",
                    description=f"{ prisoner[0].mention} se ha portado mal. \n\n Edit: Se ha movido de canal `+{jail_time}`\nTiempo de reformación: `{prisoner[2]}` segundos 🕐",
                )
                await prisoner[3].edit_original_message(embed=embed)

                prisoner[2] -= REFORMATORY_CHECK_TIME
                embed = discord.Embed(
                    color=discord.Colour.purple(),
                    title=f"{ref_channel.name}\n",
                    description=f"{ prisoner[0].mention} se ha portado mal. \n\nTiempo de reformación: `{prisoner[2]}` segundos 🕐",
                )
                await prisoner[3].edit_original_message(embed=embed)

            prisoner[2] -= REFORMATORY_CHECK_TIME

            if prisoner[2] <= 0:
                print_debug(f"{prisoner[0].name} returns to {prisoner[1]}")
                await prisoner[0].move_to(prisoner[1])
                reformatory_cells.remove(prisoner)
                embed = discord.Embed(
                    color=discord.Colour.purple(),
                    title=f"{ref_channel.name}\n",
                    description=f"{ prisoner[0].mention} se ha portado mal. \n\n Edit: Tiempo acabado ‼",
                )
                await prisoner[3].edit_original_message(embed=embed, delete_after=5.0)
                print_debug(f"{ref_channel.name} has {len(reformatory_cells)} prisoners")
            else:
                embed = discord.Embed(
                    color=discord.Colour.purple(),
                    title=f"{ref_channel.name}\n",
                    description=f"{ prisoner[0].mention} se ha portado mal. \n\n Tiempo de reformación: `{prisoner[2]}` segundos 🕐",
                )
                await prisoner[3].edit_original_message(embed=embed)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.check_ref_queue.start()
        print_debug("Initialize reformatory task loop")

def setup(bot):
    bot.add_cog(Reformatory(bot))
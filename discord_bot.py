import os
import hashlib
import logging
import discord
from discord.ext import commands
from rich.logging import RichHandler
from dotenv import load_dotenv

docker = True

if docker == False:
    load_dotenv(dotenv_path='.env')

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NB_VOICE_CHANNELS = int(os.getenv("NB_VOICE_CHANNELS"))
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX") 
ROLE_INTERVENANT_PREFIX = os.getenv("ROLE_INTERVENANT_PREFIX")
ROLE_INTERVENANT_NAME = os.getenv("ROLE_INTERVENANT_NAME")

bot = commands.Bot(command_prefix=COMMAND_PREFIX, description="Bot pour faciliter la gestion du forum de poursuite d'études.")
client = discord.Client()

logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
log = logging.getLogger("rich")

@bot.event
async def on_ready():
    activity = discord.Activity(name="!aide", type=discord.ActivityType.watching)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    log.info("The bot is ready for use.")
    log.info("Create for the IUT of Toulouse, for the project of the forum of continuation of studies.")


@bot.command("bot-setup")
async def rolesetup(ctx):
    log.info("Setup roles.")
    await ctx.guild.create_role(name="Intervenant", color=discord.Colour(0xFFA07A), hoist=True, mentionable=False)


@bot.command(name="status", help="Affiche le ping du bot.")
async def status(ctx):
    log.info("Ping. Pong.")
    await ctx.channel.send("Le bot est fonctionnel avec une latence de **{} ms** !".format(round(bot.latency * 1000)))


@bot.command(name="rejoindre", help="Rejoindre un établissement.")
async def rejoindre(ctx, hasharg):
    try:
        log.info("{} asked to join a role.".format(ctx.author.name))
        for role in ctx.guild.roles:
            hash_object = hashlib.md5(str(role.name).encode('utf-8'))
            if hash_object.hexdigest() == hasharg:
                await ctx.author.add_roles(role)
                await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="Intervenant"))
                await ctx.send(":tada: Le rôle **{}** a été ajouté à **{}**.".format(role.name, ctx.author.name))
                log.info("{} now has the role {}".format(ctx.author.name, role.name))
                await ctx.message.delete()
                return

        await ctx.send("Ce rôle n'existe pas.", delete_after=20)
        log.warning("{} asked to join a role that doesn't exist.".format(ctx.author.name))
    except Exception as e:
        log.error("{} failed to join a role.".format(ctx.author.name))
        log.error(e)
        await ctx.send("Une erreur est survenue.", delete_after=20)


@bot.command(name="ajouter", help="Ajouter un établissement.")
async def ajouter(ctx, role_name):
    try:
        role_name = str(role_name).lower()
        category_name = str(role_name)

        await ctx.guild.create_category(category_name)
        log.info("Category {} created.".format(category_name))
        
        await ctx.guild.create_role(name=("{}{}".format(ROLE_INTERVENANT_PREFIX, role_name)), color=discord.Colour(0x04C471))
        log.info("Role {} created.".format(role_name))

        category = discord.utils.get(ctx.guild.categories, name=category_name) 

        await ctx.guild.create_text_channel(f'💬・informations-'+role_name, category=category)
        log.info("Channel {} created.".format(role_name))

        await ctx.guild.create_text_channel(f'💬・echanges-'+role_name, category=category)
        log.info("Channel {} created.".format(role_name))

        channel = discord.utils.get(ctx.guild.channels, name='💬・informations-'+role_name)

        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        log.info("Permissions set for {}.".format(role_name))

        role = discord.utils.get(ctx.guild.roles, name="{}{}".format(ROLE_INTERVENANT_PREFIX, role_name))
        channel = discord.utils.get(ctx.guild.channels, name='💬・informations-'+role_name)

        await channel.set_permissions(role, send_messages=True)
        log.info("Permissions set for {}.".format(role_name))

        for i in range(1, NB_VOICE_CHANNELS + 1):
            await ctx.guild.create_voice_channel(name="🔊・"+role_name+" - "+str(i), category=category)
            log.info("Voice channel {} created.".format(role_name))

        hash_object = hashlib.md5("{}{}".format(ROLE_INTERVENANT_PREFIX, role_name).encode('utf-8'))

        await ctx.channel.send("L'établissement {} a été crée avec succès !".format(role_name))
        await ctx.channel.send("Vous pouvez rejoindre l'établissement en tapant `!rejoindre {}`.".format(hash_object.hexdigest()))
    except Exception as e:
        await ctx.channel.send("Impossible de créer le salon {}".format(role_name))
        log.error("Impossible to create the channel {}".format(role_name))
        log.error(e)


@bot.command(name="supprimer", help="Supprimer un établissement.")
async def supprimer(ctx, name):
    try:
        name = str(name).lower()
        category_name = str(name)

        await discord.utils.get(ctx.guild.categories, name=category_name).delete()
        log.info("Category {} deleted.".format(category_name))

        await discord.utils.get(ctx.guild.roles, name="{}{}".format(ROLE_INTERVENANT_PREFIX, name)).delete()
        log.info("Role {} deleted.".format(name))

        await discord.utils.get(ctx.guild.channels, name='💬・informations-'+name).delete()
        log.info("Channel {} deleted.".format(name))

        await discord.utils.get(ctx.guild.channels, name='💬・echanges-'+name).delete()
        log.info("Channel {} deleted.".format(name))

        for x in range(1, NB_VOICE_CHANNELS + 1):
            await discord.utils.get(ctx.guild.channels, name="🔊・"+name+" - "+str(x)).delete()
            log.info("Voice channel {} deleted.".format(name))
    
        await ctx.channel.send("L'établissement **{}** a été supprimé ! 🗑".format(name))
        log.info("{} just deleted {}".format(ctx.author.name, name))
    except Exception as e:
        log.error(e)
        await ctx.channel.send("Impossible de supprimer le salon "+name+" !")

@bot.command(name="clear", help="Supprimer un nombre de messages.")
async def clear(ctx, amount):
    try:
        if amount == "all":
            await ctx.channel.purge(limit=99999)
            await ctx.send("Tous les messages ont été supprimés par {}.".format(ctx.author.name))
            log.info("{} just deleted all messages.".format(ctx.author.name))
        else:
            await ctx.channel.purge(limit=int(amount))
            await ctx.send("{} messages ont été supprimés par {}.".format(amount, ctx.author.name))
            log.info("{} just deleted {} messages.".format(ctx.author.name, amount))
    except Exception as e:
        log.error(e)
        await ctx.send("Impossible de supprimer les messages.")


@bot.command(name="aide", help="Affiche l'aide.")
async def aide(ctx):
    log.info("{} asked for help.".format(ctx.author.name))
    await ctx.send("Voici la liste des commandes disponibles :\n\n`!rejoindre <code>` : Permet de rejoindre un établissement.\n`!ajouter` : Permet de créer un établissement.\n`!supprimer` : Permet de supprimer un établissement.\n`!clear` : Permet de supprimer un nombre de messages.\n`!aide` : Permet d'afficher l'aide.")

bot.run(DISCORD_TOKEN)

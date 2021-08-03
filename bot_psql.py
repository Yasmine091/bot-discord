import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure, MissingPermissions
from discord.ext.commands.core import command
from discord.utils import get
from discord import NotFound
from decouple import config
import random
import asyncio
import asyncpg
import ssl

credentials = {"user": config('DB_USER'), "password": config('DB_PASS'), "database": config('DB_NAME'), "host": config('DB_HOST')}

async def connDB():
    global db
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    db = await asyncpg.create_pool(**credentials, ssl=ctx)
    #await getData()
    return (db)

async def getWords(type, message):
    words = await db.fetch('SELECT * FROM "public"."chatting_words" WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    #print(words)
    return (words)

async def getAnswers(type, message):
    answers = await db.fetch('SELECT * FROM "public"."chatting_answers" WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    #print(answers)
    return (answers)

async def formatWords(type, message):
    words = []
    r_words = await db.fetch('SELECT * FROM "public"."chatting_words" WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    for word in r_words:
        words.append(word['word'])
    #print(words)
    return (words)

async def formatAnswers(type, message):
    answers = []
    r_answers = await db.fetch('SELECT * FROM "public"."chatting_answers" WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    for answer in r_answers:
        answers.append(answer['answer'])
    #print(answers)
    return (answers)

async def getSettings(message):
    settings = await db.fetch('SELECT * FROM "public"."settings" WHERE server_id = $1', message.guild.id)
    #print(len(settings))
    if(len(settings) == 0):
        await db.execute('INSERT INTO "public"."settings" (server_id) VALUES ($1)', message.guild.id)
        settings = await db.fetch('SELECT * FROM "public"."settings" WHERE server_id = $1', message.guild.id)
        client.command_prefix = settings[0]['bot_prefix']
    else :
        client.command_prefix = settings[0]['bot_prefix']
    #print(len(settings))
    return (settings)

async def setWords(type, message):
    words = await db.execute('SELECT * FROM "public"."chatting_words" WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    return (words)

async def setAnswers(type, message):
    answers = await db.execute('SELECT * FROM "public"."chatting_answers" WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    return (answers)    

async def getData(ctx):
    global sad_w, happy_w, sing_w, sad_wl, happy_wl, sing_wl, sad_a, happy_a, sing_a, sad_al, happy_al, sing_al, settings

    sad_w = await getWords('sad', ctx)
    happy_w = await getWords('happy', ctx)
    sing_w = await getWords('sing', ctx)

    sad_wl = await formatWords('sad', ctx)
    happy_wl = await formatWords('happy', ctx)
    sing_wl = await formatWords('sing', ctx)

    sad_a = await getAnswers('sad', ctx)
    happy_a = await getAnswers('happy', ctx)
    sing_a = await getAnswers('sing', ctx)

    sad_al = await formatAnswers('sad', ctx)
    happy_al = await formatAnswers('happy', ctx)
    sing_al = await formatAnswers('sing', ctx)

    settings = await getSettings(ctx)
    return (sad_w, happy_w, sing_w, sad_wl, happy_wl, sing_wl, sad_a, happy_a, sing_a, sad_al, happy_al, sing_al, settings)

notAllowed = 'No tienes permiso para usar ese comando.'

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '!', intents=intents)

@client.event
async def on_ready():
    print('Hola, soy {0.user}'.format(client))
    await bot_run()


async def bot_run():
    await connDB()

    @client.event
    async def on_message(message):
        
        try:
            settings
        except NameError:
            print("Settings missing!")
            await getData(message)
            print('Settings loaded!')

        usr = message.author
        msg = message.content

        #print('{}: {}'.format(usr, msg))

        if message.author == client.user:
            return

        if message.content.startswith('hola'):
            await message.channel.send('¡Hola!')

        if any(word in msg for word in sing_wl):
            await message.channel.send('¡PRRRIIIIIIIII PIPIPIPI PIO PIO PIO PIO PI PI PI, PIIII PIIII PIIII!')
        
        if any(word in msg for word in sad_wl):
            await message.channel.send(random.choice(sad_al))

        if any(word in msg for word in happy_wl):
            await message.channel.send(random.choice(happy_al))

        await client.process_commands(message)


    @client.event
    async def on_member_join(member):
        print(f"{member.name} se ha unido al servidor")
        # channel = await client.get_channel(871758974456844338)
        # channel.send(f"Bienvenid@ {member.name} a la cueva de patos :D")

        embedVar = discord.Embed(color=0x12d600, description=f"Bienvenid@ {member.mention}, eres el patito #{len(list(member.guild.members))}!")
        embedVar.set_footer(text=f"{member.guild}", icon_url=f"{member.guild.icon_url}")
        embedVar.set_image(url=f"{member.avatar_url}")
        #embedVar.timestamp = datetime.datetime.utcnow()
        
        channel = client.get_channel(871758974456844338)
        await channel.send(embed=embedVar)


    @client.event
    async def on_member_remove(member):
        print(f"{member.name} ha abandonado el servidor")

    @client.command()
    @has_permissions(administrator=True)
    async def cmd(ctx):     
        embedVar = discord.Embed(title="Lista de comandos", description="Lista de comandos de **{0.user}".format(client) + "**", color=0xfde435)
        embedVar.add_field(name='\u200B', value='\u200B', inline=False)
        embedVar.add_field(name=settings['prefix'] + 'currentPrefix', value='Ver el prefijo actual', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'updatePrefix <prefix>', value='Cambiar el prefijo actual', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'addWord <list> <word>', value='Añadir palabras a una lista', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'addAnswer <list> <answer>', value='Añadir frases a una lista', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'deleteWord <list> <number>', value='Eliminar palabras de una lista', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'deleteAnswer <list> <number>', value='Eliminar frases de una lista', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'words <list>', value='Ver la lista completa de palabras', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'answers <list>', value='Ver la lista completa de frases', inline=True)
        await ctx.send(embed=embedVar)

    @cmd.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    # Admin commands
    @client.command()
    @has_permissions(administrator=True)
    async def currentPrefix(ctx):
        await ctx.send('El prefijo actual es **' + settings[0]['bot_prefix'] + '**, puedes cambiarlo con `' + settings[0]['bot_prefix'] + 'updatePrefix <prefix>`')

    @currentPrefix.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)
        
    @client.command()
    @has_permissions(administrator=True)
    async def updatePrefix(ctx, newPrefix):

        await db.execute('UPDATE "public"."settings" SET bot_prefix = $1 WHERE server_id = $2', newPrefix, ctx.guild.id)
        await getData(ctx)

        await ctx.send('Se ha actualizado el prefijo, ahora es **' + settings[0]['bot_prefix'] + '**, puedes cambiarlo con `' + settings[0]['bot_prefix'] + 'updatePrefix <prefix>`')

    @updatePrefix.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def addWord(ctx, list, word):

        await db.execute('INSERT INTO "public"."chatting_words"("server_id", "type", "word") VALUES($1, $2, $3)', ctx.guild.id, list, word)
        await getData(ctx)

        await ctx.send('Se ha añadido la palabra **' + word + '** a la lista **' + list + '**.')

    @addWord.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def addAnswer(ctx, list, *answer):
        s_answer = " ".join(answer)

        await db.execute('INSERT INTO "public"."chatting_answers"("server_id", "type", "answer") VALUES($1, $2, $3)', ctx.guild.id, list, s_answer)
        await getData(ctx)

        await ctx.send('Se ha añadido la frase **' + s_answer + '** a la lista **' + list + '**.')

    @addAnswer.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def deleteWord(ctx, list, word):

        await db.execute('DELETE FROM "public"."chatting_words" WHERE server_id = $1 AND type = $2 AND id = $3', ctx.guild.id, list, int(word))
        await getData(ctx)

        await ctx.send('Se ha eliminado la palabra **#' + word + '** de la lista **' + list + '**.')

    @deleteWord.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def deleteAnswer(ctx, list, answer): # hacerlo por ID si posible
        
        await db.execute('DELETE FROM "public"."chatting_answers" WHERE server_id = $1 AND type = $2 AND id = $3', ctx.guild.id, list, int(answer))
        await getData(ctx)

        await ctx.send('Se ha eliminado la frase **#' + answer + '** de la lista **' + list + '**.')

    @deleteAnswer.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def words(ctx, list):
        embedVar = discord.Embed(title="Diccionario **" + list + "**", description="\u200B", color=0xfde435)

        if(list == 'sad'):
            data = sad_w
        if(list == 'happy'):
            data = happy_w
        if(list == 'sing'):
            data = sing_w

        i = 1;
        for word in data:
            embedVar.add_field(name='Palabra #{}'.format(word['id']), value=word['word'], inline=True)
            i = i + 1;

        await ctx.send(embed=embedVar)

    @words.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def answers(ctx, list):
        embedVar = discord.Embed(title="Repertorio **" + list + "**", description="\u200B", color=0xfde435)


        if(list == 'sad'):
            data = sad_a
        if(list == 'happy'):
            data = happy_a
        if(list == 'sing'):
            data = sing_a


        i = 1;
        for answer in data:
            embedVar.add_field(name='Frase #{}'.format(answer['id']), value=answer['answer'], inline=False)
            i = i + 1;

        await ctx.send(embed=embedVar)

    @answers.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

client.run(config('TOKEN'))
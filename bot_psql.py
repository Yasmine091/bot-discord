import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure, MissingPermissions
from discord.ext.commands.core import command
from discord.utils import get
from discord import NotFound
from decouple import config
import random
import json
import functions

import asyncio
import asyncpg

credentials = {"user": config('DB_USER'), "password": config('DB_PASS'), "database": config('DB_NAME'), "host": config('DB_HOST')}

async def connDB():
    global db
    db = await asyncpg.create_pool(**credentials)
    #await getData()
    return (db)

async def getWords(type, message):
    words = await db.fetch('SELECT * FROM chatting_words WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    print(words)
    return (words)

async def getAnswers(type, message):
    answers = await db.fetch('SELECT * FROM chatting_answers WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    print(answers)
    return (answers)

async def getSettings(message):
    settings = await db.fetch('SELECT * FROM settings WHERE server_id = $1', message.guild.id)
    client.command_prefix = settings[0]['bot_prefix']
    if(settings == 'SELECT 0'):
        await db.execute('INSERT INTO settings (server_id) VALUES ($1)', message.guild.id)
        settings = await db.fetch('SELECT * FROM settings WHERE server_id = $1', message.guild.id)
        client.command_prefix = settings[0]['bot_prefix']
    return (settings)

async def setWords(type, message):
    words = await db.execute('SELECT * FROM chatting_words WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    return (words)

async def setAnswers(type, message):
    answers = await db.execute('SELECT * FROM chatting_answers WHERE server_id = $1 AND type = $2', int(message.guild.id), str(type))
    return (answers)    

async def getData(ctx):
    global sad_w, happy_w, sing_w, sad_a, happy_a, sing_a, settings
    sad_w = await getWords('sad', ctx)
    happy_w = await getWords('happy', ctx)
    sing_w = await getWords('sing', ctx)
    sad_a = await getAnswers('sad', ctx)
    happy_a = await getAnswers('happy', ctx)
    sing_a = await getAnswers('sing', ctx)
    settings = await getSettings(ctx)
    return (sad_w, happy_w, sing_w, sad_a, happy_a, sing_a, settings)

#words = data['chatting_words']
#answers = data['chatting_answers']

#sing = ['canta', 'cantar', 'canta!', 'cantar!']

notAllowed = 'No tienes permiso para usar ese comando.'

client = commands.Bot(command_prefix = '!')

@client.event
async def on_ready():
    print('Hola, soy {0.user}'.format(client))
    await bot_run()


async def bot_run():
    await connDB()
    
    @client.event
    async def on_ready():
        print('Hola, soy {0.user}'.format(client))

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
        
        if any(word in msg for word in sing_w):
            await message.channel.send('¡PRRRIIIIIIIII PIPIPIPI PIO PIO PIO PIO PI PI PI, PIIII PIIII PIIII!')
        
        if any(word in msg for word in sad_w['words']):
            await message.channel.send(random.choice(sad_a['answers']))

        if any(word in msg for word in happy_w['words']):
            await message.channel.send(random.choice(happy_a['answers']))

        await client.process_commands(message)


    @client.command()
    @has_permissions(administrator=True)
    async def commands(ctx):
        embedVar = discord.Embed(title="Lista de comandos", description="Lista de comandos de **{0.user}".format(client) + "**", color=0xfde435)
        embedVar.add_field(name='\u200B', value='\u200B', inline=False)
        embedVar.add_field(name=settings['prefix'] + 'currentPrefix', value='Ver el prefijo actual', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'updatePrefix <prefix>', value='Cambiar el prefijo actual', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'addWord <list> <word>', value='Añadir palabras a una lista', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'addAnswer <list> <answer>', value='Añadir frases a una lista', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'deleteWord <list> <word>', value='Eliminar palabras de una lista', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'deleteAnswer <list> <answer>', value='Eliminar frases de una lista', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'words <list>', value='Ver la lista completa de palabras', inline=True)
        embedVar.add_field(name=settings['prefix'] + 'answers <list>', value='Ver la lista completa de frases', inline=True)
        
        await ctx.send(embed=embedVar)

    @commands.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    # Admin commands
    @client.command()
    @has_permissions(administrator=True)
    async def currentPrefix(ctx):
        await ctx.send('El prefijo actual es **' + settings['prefix'] + '**, puedes cambiarlo con `' + settings['prefix'] + 'updatePrefix <prefix>`')

    @currentPrefix.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)
        
    @client.command()
    @has_permissions(administrator=True)
    async def updatePrefix(ctx, newPrefix):

        await db.execute('UPDATE settings SET bot_prefix = $1 WHERE server_id = $2', newPrefix, ctx.guild.id)
        await getData(ctx)

        await ctx.send('Se ha actualizado el prefijo, ahora es **' + settings[0]['bot_prefix'] + '**, puedes cambiarlo con `' + settings[0]['bot_prefix'] + 'updatePrefix <prefix>`')

    @updatePrefix.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def addWord(ctx, list, word):

        await db.execute('INSERT INTO "chatting_words"("server_id", "type", "word") VALUES($1, $2, $3)', ctx.guild.id, list, word)
        await getData(ctx)

        await ctx.send('Se ha añadido la palabra **' + word + '** a la lista **' + list + '**.')

    @addWord.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def addAnswer(ctx, list, answer):

        await db.execute('INSERT INTO "chatting_answers"("server_id", "type", "word") VALUES($1, $2, $3)', ctx.guild.id, list, answer)
        await getData(ctx)

        await ctx.send('Se ha añadido la frase **' + answer + '** a la lista **' + list + '**.')

    @addAnswer.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def deleteWord(ctx, list, word):

        data['chatting'][list][0]['words'].remove(word)

        with open("assets/api.json", 'w') as wf:
            json.dump(data, wf, indent=3)

        await ctx.send('Se ha eliminado la palabra **' + word + '** de la lista **' + list + '**.')

    @deleteWord.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def deleteAnswer(ctx, list, answer):

        data['chatting'][list][0]['answers'].remove(answer)

        with open("assets/api.json", 'w') as wf:
            json.dump(data, wf, indent=3)

        await ctx.send('Se ha eliminado la frase **' + answer + '** de la lista **' + list + '**.')

    @deleteAnswer.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

    @client.command()
    @has_permissions(administrator=True)
    async def words(ctx, list):
        embedVar = discord.Embed(title="Diccionario **" + list + "**", description="\u200B", color=0xfde435)

        i = 1;
        for word in data['chatting'][list][0]['words']:
            embedVar.add_field(name='Palabra #{}'.format(i), value=word, inline=True)
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

        i = 1;
        for answer in data['chatting'][list][0]['answers']:
            embedVar.add_field(name='Frase #{}'.format(i), value=answer, inline=False)
            i = i + 1;

        await ctx.send(embed=embedVar)

    @answers.error
    async def noAdmin(ctx, error):
        if isinstance(error, MissingPermissions):
            await ctx.send(notAllowed)

client.run(config('TOKEN'))
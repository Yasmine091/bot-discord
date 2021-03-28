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

def getAPI():
    with open("assets/api.json", encoding="utf8") as f:
        global data
        data = json.load(f)
        return (data)

getAPI()

chatting = data['chatting']
settings = data['basic settings']
sad = chatting['sad'][0]
happy = chatting['happy'][0]
# sing = chatting['sing'][0]

sing = ['canta', 'cantar', 'canta!', 'cantar!']

notAllowed = 'No tienes permiso para usar ese comando.'

client = commands.Bot(command_prefix = settings['prefix'])

@client.event
async def on_ready():
    print('Hola, soy {0.user}'.format(client))

@client.event
async def on_message(message):
    usr = message.author
    msg = message.content

    #print('{}: {}'.format(usr, msg))

    if message.author == client.user:
        return

    if message.content.startswith('hola'):
        await message.channel.send('¡Hola!')
    
    if any(word in msg for word in sing):
        await message.channel.send('¡PRRRIIIIIIIII PIPIPIPI PIO PIO PIO PIO PI PI PI, PIIII PIIII PIIII!')
    
    if any(word in msg for word in sad['words']):
        await message.channel.send(random.choice(sad['answers']))

    if any(word in msg for word in happy['words']):
        await message.channel.send(random.choice(happy['answers']))

    await client.process_commands(message)


@client.command()
@has_permissions(administrator=True)
async def commands(ctx):
    embedVar = discord.Embed(title="Lista de comandos", description="Lista de comandos de **{0.user}".format(client) + "**", color=0x00ff00)
    embedVar.add_field(name='\u200B', value='\u200B', inline=False)
    embedVar.add_field(name='!currentPrefix', value='Ver el prefijo actual', inline=False)
    embedVar.add_field(name='!updatePrefix <prefix>', value='Cambiar el prefijo actual', inline=False)
    embedVar.add_field(name='!addWord <list> <word>', value='Añadir palabras a una lista', inline=False)
    embedVar.add_field(name='!addAnswer <list> <answer>', value='Añadir frases a una lista', inline=False)
    embedVar.add_field(name='!deleteWord <list> <word>', value='Eliminar palabras de una lista', inline=False)
    embedVar.add_field(name='!deleteAnswer <list> <answer>', value='Eliminar frases de una lista', inline=False)
    embedVar.add_field(name='!wordsList <list>', value='Ver la lista completa de palabras', inline=False)
    embedVar.add_field(name='!answersList <list>', value='Ver la lista completa de frases', inline=False)
    
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

    data['basic settings']['prefix'] = newPrefix

    with open("assets/api.json", 'w') as wf:
        json.dump(data, wf, indent=3)

    client.command_prefix = newPrefix
    await ctx.send('Se ha actualizado el prefijo, ahora es **' + settings['prefix'] + '**, puedes cambiarlo con `' + settings['prefix'] + 'updatePrefix <prefix>`')

@updatePrefix.error
async def noAdmin(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send(notAllowed)

@client.command()
@has_permissions(administrator=True)
async def addWord(ctx, list, word):

    data['chatting'][list][0]['words'].append(word)

    with open("assets/api.json", 'w') as wf:
        json.dump(data, wf, indent=3)

    await ctx.send('Se ha añadido la palabra **' + word + '** a la lista **' + list + '**.')

@addWord.error
async def noAdmin(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send(notAllowed)

@client.command()
@has_permissions(administrator=True)
async def addAnswer(ctx, list, answer):

    data['chatting'][list][0]['answers'].append(answer)

    with open("assets/api.json", 'w') as wf:
        json.dump(data, wf, indent=3)

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
async def wordsList(ctx, list):
    embedVar = discord.Embed(title="Lista : **" + list + "**", description="Lista de palabras del grupo **" + list + "**", color=0x00ff00)
    embedVar.add_field(name='\u200B', value='\u200B', inline=False)

    for word in data['chatting'][list][0]['words']:
        embedVar.add_field(name=word, value='\u200B', inline=True)

    await ctx.send(embed=embedVar)

@wordsList.error
async def noAdmin(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send(notAllowed)

@client.command()
@has_permissions(administrator=True)
async def answersList(ctx, list):
    embedVar = discord.Embed(title="Lista : **" + list + "**", description="Lista de frases del grupo **" + list + "**", color=0x00ff00)
    embedVar.add_field(name='\u200B', value='\u200B', inline=False)

    for word in data['chatting'][list][0]['answers']:
        embedVar.add_field(name=word, value='\u200B', inline=False)

    await ctx.send(embed=embedVar)

@answersList.error
async def noAdmin(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send(notAllowed)

client.run(config('TOKEN'))
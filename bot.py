import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
from discord.utils import get
from discord import NotFound
from decouple import config
import random
import requests
import json
import dotenv
#import functions

def getAPI():
    response = requests.get(config('API_URL'))
    json_data = json.loads(response.text)
    return(json_data)

data = getAPI()

chatting = data['chatting']
settings = data['basic settings']
sad = chatting['sad'][0]
happy = chatting['happy'][0]
# sing = chatting['sing'][0]

sing = ['canta', 'cantar', 'canta!', 'cantar!']

client = commands.Bot(command_prefix = settings['prefix'])

@client.event
async def on_ready():
    print('Hola, soy {0.user}'.format(client))

@client.event
async def on_message(message):
    usr = message.author
    msg = message.content

    print('{}: {}'.format(usr, msg))

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
#@has_permissions(ADMINISTRATOR=True) 
async def currentPrefix(ctx):
    await ctx.send('El prefijo actual es **' + settings['prefix'] + '**, puedes cambiarlo con `' + settings['prefix'] + 'updatePrefix <prefix>`')


client.run(config('TOKEN'))
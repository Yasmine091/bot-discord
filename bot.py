import discord
from decouple import config
import random
import requests
import json
import dotenv

client = discord.Client()

@client.event
async def on_ready():
    print('Hola, soy {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return



    msg = message.content
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

    if message.content.startswith('hola'):
        await message.channel.send('¡Hola!')

    if message.content.startswith(settings['prefix']+ 'currentPrefix'):
        await message.channel.send('El prefijo actual es **' + settings['prefix'] + '**, puedes cambiarlo con `' + settings['prefix'] + 'updatePrefix <prefix>`')

    if any(word in msg for word in sing):
        await message.channel.send('¡PRRRIIIIIIIII PIPIPIPI PIO PIO PIO PIO PI PI PI, PIIII PIIII PIIII!')
    
    if any(word in msg for word in sad['words']):
        await message.channel.send(random.choice(sad['answers']))

    if any(word in msg for word in happy['words']):
        await message.channel.send(random.choice(happy['answers']))


client.run(config('TOKEN'))
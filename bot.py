import discord
import os
import random

client = discord.Client()

@client.event
async def on_ready():
    print('Hola, soy {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return


    msg = message.content
    sad = ['triste', 'deprimido', 'deprimida', 'harto', 'harta']
    sad_answers = ['¡Ánimo, no te rindas!', '¿Qué te ocurre?']
    happy = ['contenta', 'contento' 'feliz', 'alegria', 'alivio', 'felicidad']
    happy_answers = ['¡Me alegro por tí!', '¡Que bien!', 'Enhorabuena por lo que sea que hayas conseguido, tu felicidad es la nuestra XD']
    sing = ['canta', 'cantar', 'canta!', 'cantar!']

    if message.content.startswith('$hola'):
        await message.channel.send('¡Hola!')

    if any(word in msg for word in sing):
        await message.channel.send('¡PRRRIIIIIIIII PIPIPIPI PIO PIO PIO PIO PI PI PI, PIIII PIIII PIIII!')
    
    if any(word in msg for word in sad):
        await message.channel.send(random.choice(sad_answers))

    if any(word in msg for word in happy):
        await message.channel.send(random.choice(happy_answers))


# client.run(os.getenv('TOKEN'))
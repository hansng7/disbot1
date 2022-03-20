import os
import discord

token = os.environ['TOKEN']
reminders_channel_id = 854328114837585921
test_channel_id = 955128791204765797
travelers_role_id = 872748500033630218

def get_rolemention_str(id):
  return '<@&{0}>'.format(id)
  
def get_usermention_str(id):
  return '<@!{0}>'.format(id)

client = discord.Client()

@client.event
async def on_ready():
  print('Logged in as {0}'.format(client.user))
  await client.get_channel(test_channel_id).send('{0} entered chat'.format(client.user))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if (message.content == '$remind') and (message.author.guild_permissions.administrator):
    await client.get_channel(reminders_channel_id).send('{0} Check in'.format(get_rolemention_str(travelers_role_id)))
  
  elif message.content.startswith('$') or (client.user in message.mentions):
    await message.channel.send('Hello {0}'.format(message.author.mention)) 

client.run(token, bot=True)

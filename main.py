import os
import discord
from keep_alive import keep_alive

token = os.environ['TOKEN']
reminders_channel_id = 854328114837585921
bot_channel_id = 955128791204765797
travelers_role_id = 872748500033630218

def get_rolemention_str(id):
  return '<@&{0}>'.format(id)
  
def get_usermention_str(id):
  return '<@!{0}>'.format(id)

# function to send a message to bot channel
async def bot_message(message_str):
  channel = client.get_channel(bot_channel_id)
  return await channel.send(message_str)

# function to broadcast a message to a specific channel
async def broadcast_message(channel_id, message_str):
  channel = client.get_channel(channel_id)
  parsed_message_str = message_str.format(get_rolemention_str(travelers_role_id))
  return await channel.send(parsed_message_str)

# function to send message to reminder channel and add reaction to it
async def remind_message(message_str):
  new_message = await broadcast_message(reminders_channel_id, message_str)
  await new_message.add_reaction('\u2705')
  return new_message

client = discord.Client()

@client.event
async def on_ready():
  print('Logged in as {0}'.format(client.user))
  await bot_message('{0} entered chat'.format(client.user))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if (message.content == '$daily') and (message.author.guild_permissions.administrator):
    await remind_message('{0} Check in')

  elif (message.content == '$weekly') and (message.author.guild_permissions.administrator):
    await remind_message('{0} Buy omni-ubiquity net & do parametric transformer')

  elif (message.content == '$teapot') and (message.author.guild_permissions.administrator):
    await remind_message('{0} Collect teapot coin')
  
#  elif (message.content == '$test') and (message.author.guild_permissions.administrator):
#    await broadcast_message_remind('{0} test')
  
  elif message.content.startswith('$'):
    await message.channel.send('Command not found')
  
  elif client.user in message.mentions:
    await message.channel.send('Hello {0}'.format(message.author.mention))

keep_alive()
client.run(token, bot=True)

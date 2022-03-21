import os
import random
import discord
from keep_alive import keep_alive

gi_characters = [ 'Albedo' , 'Aloy' , 'Amber' , 'Arataki Itto' , 'Barbara' , 'Beidou' , 'Bennett' , 'Chongyun' , 'Diluc' , 'Diona' , 'Eula' , 'Fischl' , 'Ganyu' , 'Gorou' , 'Hu Tao' , 'Jean' , 'Kaedehara Kazuha' , 'Kaeya' , 'Kamisato Ayaka' , 'Kamisato Ayato' , 'Keqing' , 'Klee' , 'Kujou Sara' , 'Lisa' , 'Mona' , 'Ningguang' , 'Noelle' , 'Qiqi' , 'Raiden Shogun' , 'Razor' , 'Rosaria' , 'Sangonomiya Kokomi' , 'Sayu' , 'Shenhe' , 'Sucrose' , 'Tartaglia' , 'Thoma' , 'Traveler' , 'Venti' , 'Xiangling' , 'Xiao' , 'Xingqiu' , 'Xinyan' , 'Yae Miko' , 'Yanfei' , 'Yoimiya' , 'Yun Jin' , 'Zhongli' ]
gi_char_rates = [ 0.005, 0.005, 0.038, 0.005, 0.038, 0.038, 0.038, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.005, 0.005, 0.038, 0.005, 0.005, 0.005, 0.005, 0.038, 0.038, 0.005, 0.038, 0.038, 0.005, 0.005, 0.038, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.005, 0.038, 0.005, 0.038, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005 ]

token = os.environ['TOKEN']
reminders_channel_id = 854328114837585921
bot_channel_id = 955128791204765797
travelers_role_id = 872748500033630218

def get_rolemention_str(id):
  return '<@&{0}>'.format(id)
  
def get_usermention_str(id):
  return '<@!{0}>'.format(id)

client = discord.Client()

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

# function to find a message by id
async def find_message(message_id):
  message = None
  error = None
  for channel in client.get_all_channels():
    if channel.type == discord.ChannelType.text:
      try:
        message = await channel.fetch_message(message_id)
        break
      except (discord.NotFound, discord.Forbidden):
        pass
      except Exception as e:
        error = 'Something went wrong!'
        print(e)
        break
  if message == None:
    error = 'Message not found!'
  return message, error

# function to add/remove reaction to a message
async def toggle_reaction(message, emoji):
  # calling remove_reaction() for non-existence reaction does not cause error, therefore it cannot be used to determine if the reaction is already there
  reaction_found = False
  reaction_active = False
  error = None
  for reaction in message.reactions:
    if reaction.emoji == emoji:
      reaction_users = await reaction.users().flatten()
      if client.user in reaction_users:
        # the reaction is found
        reaction_found = True
        break
  # remove the reaction if the reaction is found
  if reaction_found == True:
    try:
      await message.remove_reaction(emoji, client.user)
    except Exception as e:
      error = 'Something went wrong!'
      print(e)
    finally:
      reaction_active = False
  # add reaction if the reaction is not found
  else:
    try:
      await message.add_reaction(emoji)
    except discord.NotFound:
      error = 'Emoji not found!'
    except Exception as e:
      error = 'Something went wrong!'
      print(e)
    finally:
      reaction_active = True
  return reaction_active, error

# function to find a message by id and add/remove reaction to it
async def find_and_toggle_reaction(message_id, emoji):
  message, error = await find_message(message_id)
  # toggle the reaction if the message is found
  if message != None:
    reaction, error = await toggle_reaction(message, emoji)
  else:
    reaction = False
  return message, reaction, error

@client.event
async def on_ready():
  print('Logged in as {0}'.format(client.user))
  await bot_message('{0} entered chat'.format(client.user))

@client.event
async def on_message(message):
  # ignore own message
  if message.author == client.user:
    return

  if (message.content == '$daily') and (message.author.guild_permissions.administrator):
    await remind_message('{0} Check in')

  elif (message.content == '$weekly') and (message.author.guild_permissions.administrator):
    await remind_message('{0} Buy omni-ubiquity net & do parametric transformer')

  elif (message.content == '$teapot') and (message.author.guild_permissions.administrator):
    await remind_message('{0} Collect teapot coin')
  
  elif (message.content.startswith('$react')) and (message.author.guild_permissions.administrator):
    tokens = message.content.split(' ')
    if len(tokens) == 3:
      message_id, emoji = tokens[1], tokens[2]
      reacted_message, reaction, error = await find_and_toggle_reaction(message_id, emoji)
    else:
      error = 'Command error!'
    if error == None:
      reaction_status = 'added' if reaction else 'removed'
      await message.channel.send('Reaction {0} {1}\nLink: {2}'.format(emoji, reaction_status, reacted_message.jump_url))
    else:
      await message.channel.send(error)

  elif (message.content == '$roll'):
    await message.channel.send(random.choices(gi_characters, weights=gi_char_rates)[0], reference=message)

  elif (message.content == '$roll10'):
    await message.channel.send("\n".join(random.choices(gi_characters, weights=gi_char_rates, k=10)), reference=message)
  
  elif message.content.startswith('$'):
    await message.channel.send('Command not found!')
  
  elif client.user in message.mentions:
    await message.channel.send('Hello {0}'.format(message.author.mention))

keep_alive()
client.run(token, bot=True)

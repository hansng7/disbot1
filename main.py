import os
import random
from datetime import datetime, timedelta, timezone
import discord
from discord import ActivityType, NotFound, Forbidden
from discord.ext import tasks
from keep_alive import keep_alive

# gi_characters = [ 'Albedo' , 'Aloy' , 'Amber' , 'Arataki Itto' , 'Barbara' , 'Beidou' , 'Bennett' , 'Chongyun' , 'Diluc' , 'Diona' , 'Eula' , 'Fischl' , 'Ganyu' , 'Gorou' , 'Hu Tao' , 'Jean' , 'Kaedehara Kazuha' , 'Kaeya' , 'Kamisato Ayaka' , 'Kamisato Ayato' , 'Keqing' , 'Klee' , 'Kujou Sara' , 'Lisa' , 'Mona' , 'Ningguang' , 'Noelle' , 'Qiqi' , 'Raiden Shogun' , 'Razor' , 'Rosaria' , 'Sangonomiya Kokomi' , 'Sayu' , 'Shenhe' , 'Sucrose' , 'Tartaglia' , 'Thoma' , 'Traveler' , 'Venti' , 'Xiangling' , 'Xiao' , 'Xingqiu' , 'Xinyan' , 'Yae Miko' , 'Yanfei' , 'Yoimiya' , 'Yun Jin' , 'Zhongli' ]
gi_characters = [ 'Albedo (5☆)' , 'Aloy (5☆)' , 'Amber (4☆)' , 'Itto (5☆)' , 'Barbara (4☆)' , 'Beidou (4☆)' , 'Bennett (4☆)' , 'Chongyun (4☆)' , 'Diluc (5☆)' , 'Diona (4☆)' , 'Eula (5☆)' , 'Fischl (4☆)' , 'Ganyu (5☆)' , 'Gorou (4☆)' , 'Hu Tao (5☆)' , 'Jean (5☆)' , 'Kazuha (5☆)' , 'Kaeya (4☆)' , 'Ayaka (5☆)' , 'Ayato (5☆)' , 'Keqing (5☆)' , 'Klee (5☆)' , 'Sara (4☆)' , 'Lisa (4☆)' , 'Mona (5☆)' , 'Ningguang (4☆)' , 'Noelle (4☆)' , 'Qiqi (5☆)' , 'Raiden (5☆)' , 'Razor (4☆)' , 'Rosaria (4☆)' , 'Kokomi (5☆)' , 'Sayu (4☆)' , 'Shenhe (5☆)' , 'Sucrose (4☆)' , 'Tartaglia (5☆)' , 'Thoma (4☆)' , 'Traveler (5☆)' , 'Venti (5☆)' , 'Xiangling (4☆)' , 'Xiao (5☆)' , 'Xingqiu (4☆)' , 'Xinyan (4☆)' , 'Yae (5☆)' , 'Yanfei (4☆)' , 'Yoimiya (5☆)' , 'Yun Jin (4☆)' , 'Zhongli (5☆)' ]
gi_char_rates = [ 0.005, 0.005, 0.038, 0.005, 0.038, 0.038, 0.038, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.005, 0.005, 0.038, 0.005, 0.005, 0.005, 0.005, 0.038, 0.038, 0.005, 0.038, 0.038, 0.005, 0.005, 0.038, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.005, 0.038, 0.005, 0.038, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005 ]

token = os.environ['TOKEN']
reminders_channel_id = 854328114837585921
bot_channel_id = 955128791204765797
travelers_role_id = 872748500033630218
reminders_user_ids = [ 808939288774705182 , 359961846096330752 , 848608705843167282 ]

##############################

# same as discord.User.mention
def get_mention_str(id):
  return '<@{0}>'.format(id)

# alternative to discord.User.mention
def get_usermention_str(id):
  return '<@!{0}>'.format(id)

# same as discord.Role.mention
def get_rolemention_str(id):
  return '<@&{0}>'.format(id)

# same as discord.GuildChannel.mention
def get_channelmention_str(id):
  return '<@#{0}>'.format(id)

def is_author_admin(message):
  return message.author.guild_permissions.administrator

# substring method, mainly for case-insensitive usage
def str_contains(string, substring, case_sensitive=False):
  if case_sensitive:
    return substring in string
  else:
    return string.lower().find(substring) >= 0

# check if a string mentions an id (can be user, role, channel)
def str_mentions(string, id):
  if get_mention_str(id) in string:
    return True
  elif get_usermention_str(id) in string:
    return True
  elif get_rolemention_str(id) in string:
    return True
  elif get_channelmention_str(id) in string:
    return True
  else:
    return False

##############################

client = discord.Client()

# function to send a message to bot channel
async def send_bot_message(message_str):
  channel = client.get_channel(bot_channel_id)
  return await channel.send(message_str)

# function to broadcast a message to a specific channel
async def send_broadcast(channel_id, message_str):
  channel = client.get_channel(channel_id)
  parsed_message_str = message_str.format(get_rolemention_str(travelers_role_id))
  return await channel.send(parsed_message_str)

# function to send message to reminder channel and add reaction to it
async def send_startremind(message_str):
  new_message = await send_broadcast(reminders_channel_id, message_str)
  await new_message.add_reaction('\u2705')
  return new_message

# function to find a message by id
async def find_message(message_id):
  message = None
  error = None
  for channel in client.get_all_channels():
    # only search in text channels
    if channel.type == ChannelType.text:
      try:
        message = await channel.fetch_message(message_id)
        break
      # ignore not found and forbidden errors
      except (NotFound, Forbidden):
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
      reaction_active = False
    except Exception as e:
      error = 'Something went wrong!'
      print(e)
  # add reaction if the reaction is not found
  else:
    try:
      await message.add_reaction(emoji)
      reaction_active = True
    except NotFound:
      error = 'Emoji not found!'
    except Exception as e:
      error = 'Something went wrong!'
      print(e)
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

# function to find all users who have not reacted to a reminder message's reactions
async def find_users_to_endremind(reactions):
  user_ids_to_remind = reminders_user_ids.copy()
  # loop through every reactions
  for reaction in reactions:
    reaction_users = await reaction.users().flatten()
    # loop through every users of this reaction
    for user in reaction_users:
      if user.id in user_ids_to_remind:
        user_ids_to_remind.remove(user.id)
  return user_ids_to_remind

# function to check a reminder message and remind all users who have not reacted
async def send_endremind(message):
  user_ids = await find_users_to_endremind(message.reactions)
  if len(user_ids):
    buffer = ''
    for user_id in user_ids:
      buffer += (get_usermention_str(user_id) + ' ')
    await message.reply(buffer)
  else:
    await send_bot_message('No one to remind\nLink: {0}'.format(message.jump_url))

##############################

@client.event
async def on_ready():
  print('Logged in as {0}'.format(client.user))
  await send_bot_message('{0} entered chat'.format(client.user))
  await client.change_presence(activity=discord.Activity(type=ActivityType.watching, name="you"))

@client.event
async def on_message(message):
  # ignore own message
  if message.author == client.user:
    return

  # admin commands
  if (message.content == '$daily') and is_author_admin(message):
    await send_startremind('{0} Check in')

  elif (message.content == '$weekly') and is_author_admin(message):
    await send_startremind('{0} Buy omni-ubiquity net & do parametric transformer')

  elif (message.content == '$teapot') and is_author_admin(message):
    await send_startremind('{0} Collect teapot coin')

  elif message.content.startswith('$checkremind') and is_author_admin(message):
    tokens = message.content.split(' ')
    if len(tokens) == 2:
      message_id = tokens[1]
      message, error = await find_message(message_id)
      if message != None:
        await send_endremind(message)
    else:
      error = 'Command error!'
    if error != None:
      await message.channel.send(error)

  elif message.content.startswith('$react') and is_author_admin(message):
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

  elif message.content.startswith('$debug') and is_author_admin(message):
    # print the content to console
    print('Content: {0}'.format(message.content))
    # print user mentions if any
    if len(message.mentions):
      print('User: {0}'.format(message.mentions))
      buffer = ''
      for user in message.mentions:
        buffer += (user.mention + ' ')
      print('    {0}'.format(buffer))
    # print role mentions if any
    if len(message.role_mentions):
      print('Role: {0}'.format(message.role_mentions))
      buffer = ''
      for role in message.role_mentions:
        buffer += (role.mention + ' ')
      print('    {0}'.format(buffer))

  # all member commands
  elif (message.content == '$roll'):
    await message.reply(random.choices(gi_characters, weights=gi_char_rates)[0])

  elif (message.content == '$roll10'):
    rolls = random.choices(gi_characters, weights=gi_char_rates, k=10)
    # format 1 : 10 new lines
    # formatted_1 = "\n".join(rolls)
    # format 2 : 2 columns by 5 lines inside code block
    formatted_2 = ''
    count_even = True
    for char in rolls:
      formatted_2 += char.ljust(17, ' ')
      count_even = not(count_even)
      if count_even:
        formatted_2 += '\n'
    formatted_2 = '```\n' + formatted_2 + '\n```'
    await message.reply(formatted_2)

  # etc commands    
  elif message.content.startswith('$'):
    await message.channel.send('Command not found!')

  elif str_contains(message.content, 'spymon'):
    await toggle_reaction(message, '\U0001f47e')

  elif client.user.mentioned_in(message) and str_mentions(message.content, client.user.id):
    await message.channel.send('Hello {0}'.format(message.author.mention))

##############################

def seconds_since_midnight():
  now = datetime.now(timezone(timedelta(hours=8)))
  seconds = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
  return seconds

@tasks.loop(seconds=15)
async def periodic():
  periodic.my_count += 1

  # it is currently within task inverval from midnight, send reminder
  if seconds_since_midnight() < periodic.seconds:
    await send_startremind('{0} Check in')

@periodic.before_loop
async def before_periodic():
  await client.wait_until_ready()
  periodic.my_count = 0

##############################

keep_alive()
periodic.start()
client.run(token, bot=True)

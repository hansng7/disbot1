import os
import random
import re
from datetime import datetime, time, timedelta, timezone
import discord
from discord import ActivityType, ChannelType, NotFound, Forbidden
from discord.ext import tasks
from keep_alive import keep_alive
from replit import db

# gi_characters = [ 'Albedo' , 'Aloy' , 'Amber' , 'Arataki Itto' , 'Barbara' , 'Beidou' , 'Bennett' , 'Chongyun' , 'Diluc' , 'Diona' , 'Eula' , 'Fischl' , 'Ganyu' , 'Gorou' , 'Hu Tao' , 'Jean' , 'Kaedehara Kazuha' , 'Kaeya' , 'Kamisato Ayaka' , 'Kamisato Ayato' , 'Keqing' , 'Klee' , 'Kujou Sara' , 'Lisa' , 'Mona' , 'Ningguang' , 'Noelle' , 'Qiqi' , 'Raiden Shogun' , 'Razor' , 'Rosaria' , 'Sangonomiya Kokomi' , 'Sayu' , 'Shenhe' , 'Sucrose' , 'Tartaglia' , 'Thoma' , 'Traveler' , 'Venti' , 'Xiangling' , 'Xiao' , 'Xingqiu' , 'Xinyan' , 'Yae Miko' , 'Yanfei' , 'Yoimiya' , 'Yun Jin' , 'Zhongli' ]
gi_characters = [ 'Albedo (5☆)' , 'Aloy (5☆)' , 'Amber (4☆)' , 'Itto (5☆)' , 'Barbara (4☆)' , 'Beidou (4☆)' , 'Bennett (4☆)' , 'Chongyun (4☆)' , 'Diluc (5☆)' , 'Diona (4☆)' , 'Eula (5☆)' , 'Fischl (4☆)' , 'Ganyu (5☆)' , 'Gorou (4☆)' , 'Hu Tao (5☆)' , 'Jean (5☆)' , 'Kazuha (5☆)' , 'Kaeya (4☆)' , 'Ayaka (5☆)' , 'Ayato (5☆)' , 'Keqing (5☆)' , 'Klee (5☆)' , 'Sara (4☆)' , 'Lisa (4☆)' , 'Mona (5☆)' , 'Ningguang (4☆)' , 'Noelle (4☆)' , 'Paimon (6☆)' , 'Qiqi (5☆)' , 'Raiden (5☆)' , 'Razor (4☆)' , 'Rosaria (4☆)' , 'Kokomi (5☆)' , 'Sayu (4☆)' , 'Shenhe (5☆)' , 'Sucrose (4☆)' , 'Tartaglia (5☆)' , 'Thoma (4☆)' , 'Traveler (5☆)' , 'Venti (5☆)' , 'Xiangling (4☆)' , 'Xiao (5☆)' , 'Xingqiu (4☆)' , 'Xinyan (4☆)' , 'Yae (5☆)' , 'Yanfei (4☆)' , 'Yoimiya (5☆)' , 'Yun Jin (4☆)' , 'Zhongli (5☆)' ]
gi_char_rates = [ 0.005, 0.005, 0.038, 0.005, 0.038, 0.038, 0.038, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.005, 0.005, 0.038, 0.005, 0.005, 0.005, 0.005, 0.038, 0.038, 0.005, 0.038, 0.038, 0.001, 0.005, 0.005, 0.038, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005, 0.005, 0.038, 0.005, 0.038, 0.038, 0.005, 0.038, 0.005, 0.038, 0.005 ]

reminders_channel_id = 854328114837585921
bot_channel_id = 955128791204765797
travelers_role_id = 872748500033630218
reminders_user_ids = [ 808939288774705182 , 359961846096330752 , 848608705843167282 ]

########## database ##########

async def set_presence(activity_type_str, activity_name):
  error = None
  activity_str = ''
  # process activity type
  if activity_type_str == 'playing':
    activity_type = ActivityType.playing
    activity_str = activity_type_str + ' ' + activity_name
  elif activity_type_str == 'listening':
    activity_type = ActivityType.listening
    activity_str = activity_type_str + ' to ' + activity_name
  elif activity_type_str == 'watching':
    activity_type = ActivityType.watching
    activity_str = activity_type_str + ' ' + activity_name
  elif activity_type_str == 'competing':
    activity_type = ActivityType.competing
    activity_str = activity_type_str + ' in ' + activity_name
  else:
    error = 'Invalid activity type!'
  # set presence if no error found
  if error == None:
    activity = discord.Activity(type=activity_type, name=activity_name)
    await client.change_presence(activity=activity)
  # save presence data to database
  db['presence'] = { 'type' : activity_type_str, 'name' : activity_name }
  return activity_str, error

async def restore_presence():
  error = None
  activity_str = ''
  # look for presence data in database
  if 'presence' in db.keys():
    activity_type_str = db['presence']['type']
    activity_name = db['presence']['name']
    # set presence based on presence data in database
    activity_str, error = await set_presence(activity_type_str, activity_name)
  else:
    error = 'Existing presence data not found!'
  return activity_str, error

######### utilities ##########

# same as discord.User.mention
def get_usermention_str(id):
  return '<@{0}>'.format(id)

# alternative to discord.User.mention
def get_nicknamemention_str(id):
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
    return substring.lower() in string.lower()

# check if a string mentions an id (can be user, role, channel)
def str_mentions(string, id):
  if get_usermention_str(id) in string:
    return True
  elif get_nicknamemention_str(id) in string:
    return True
  elif get_rolemention_str(id) in string:
    return True
  elif get_channelmention_str(id) in string:
    return True
  else:
    return False

# function to return a discord id in int type if it is valid
def parse_discord_id(id):
  # convert to int type
  if type(id) == str:
    try:
      discord_id = int(id)
    except:
      discord_id = None
  elif type(id) == int:
    discord_id = id
  # validate the id (it seems to have 17 or 18 digits)
  if (discord_id != None) and (discord_id < 10000000000000000):
    discord_id = None
  return discord_id
    
###### functionalities #######

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

# function to check a reminder message and remind all users who have not reacted
async def send_endremind(message, user_ids):
  message_str = ''
  for user_id in user_ids:
    message_str += (get_usermention_str(user_id) + ' ')
  return await message.reply(message_str, mention_author=False)

# function to find a message by id
async def find_message_by_id(message_id, channel_id=None):
  message = None
  error = None
  if type(message_id) != int:
    error = 'Parameter error!'
  else:
    if channel_id == None:
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
      # if message not found
      if (error == None) and (message == None):
        error = 'Message not found!'
    else:
      channel = client.get_channel(channel_id)
      try:
        message = await channel.fetch_message(message_id)
      except NotFound:
        error = 'Message not found!'
      except Exception as e:
        error = 'Something went wrong!'
        print(e)
  return message, error

# function to find a message by content in the specified channel id
async def find_message_by_content(string, channel_id, author_id=None, limit_today=True):
  message = None
  error = None
  history_after = None
  if limit_today:
    # get midnight time in UTC-8
    utc_8 = timezone(timedelta(hours=8))
    now = datetime.now(utc_8)
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # convert back to UTC
    midnight = midnight.astimezone(timezone.utc)
    # remove the timezone attribute to make it timezone-naive
    midnight = midnight.replace(tzinfo=None)
    history_after = midnight
  # get channel by id
  try:
    channel = client.get_channel(channel_id)
  except Exception as e:
    error = 'Something went wrong!'
    print(e)
  # get message history (use default limit of 100)
  if error == None:
    try:
      messages = await channel.history(after=history_after).flatten()
    except Exception as e:
      error = 'Something went wrong!'
      print(e)
  # find the string in message history
  if error == None:
    for msg in messages:
      # match message content
      if str_contains(msg.content, string):
        # match author id
        if (author_id == None) or ((author_id != None) and (msg.author.id == author_id)):
          message = msg
          break
  return message, error

# function to add/remove reaction to a message
async def toggle_reaction(message, emoji):
  # calling remove_reaction() for non-existence reaction does not cause error, therefore it cannot be used to determine if the reaction is already there
  reaction_active = False
  error = None
  reaction_found = False
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
  message = None
  reaction = False
  error = None
  if type(message_id) != int:
    error = 'Parameter error!'
  else:
    # find the message
    message, error = await find_message_by_id(message_id)
    # toggle the reaction if the message is found
    if message != None:
      reaction, error = await toggle_reaction(message, emoji)
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

# function to check a reminder, it performs different actions depending of the input parameter type
# - if input is of str type:
#   -- the input will be assumed to be the message content
#   -- the message content will be searched in the reminder channel
#   -- if a matching message (sent by bot and is within today) is found, all users who have not reacted to this message will be sent a reminder
# - if input is of int type:
#   -- the input will be assumed to be the message id
#   -- the message id will be searched in the reminder channel
#   -- if a matching message is found, all users who have not reacted to this message will be sent a reminder
# - if input is of discord.Message type:
#   - all users who have not reacted to this message will be sent a reminder
async def check_remind(message, author=None):
  error = None
  # find message by string
  if type(message) == str:
    found_message, error = await find_message_by_content(message, reminders_channel_id, author)
    if error == None:
      error = await check_remind(found_message)
  # find message by id
  elif type(message) == int:
    found_message, error = await find_message_by_id(message, reminders_channel_id)
    if error == None:
      error = await check_remind(found_message)
  # lastly, check message and send reminder
  elif type(message) == discord.Message:
    user_ids = await find_users_to_endremind(message.reactions)
    if len(user_ids):
      await send_endremind(message, user_ids)
    else:
      error = 'No one to remind\nLink: {0}'.format(message.jump_url)
  else:
    error = 'Parameter error!'
  return error

########### events ###########

# parse and return the command and subcommands (in a list)
def parse_command(string):
  tokens = string.split(' ')
  if len(tokens) >= 1:
    # command must:
    # - starts with $ and followed by 2 lowercase alphabets
    # - ends with space or EOL
    # - not contain any symbols
    pattern = re.compile(r'^\$[a-z]{2,}[a-z0-9]*$')
    command = pattern.search(tokens[0])
    if command != None:
      command = command.group(0)
      tokens.pop(0)
      return command, tokens
  return None, []

@client.event
async def on_ready():
  print('Logged in as {0}'.format(client.user))
  await send_bot_message('{0} entered chat'.format(client.user))
  # initialize presence
  activity_str, error = await restore_presence()
  if error != None:
    # set new presence if not found
    print('Presence: ' + error)
    activity_str, error = await set_presence('watching', 'you')
  if error == None:
    print('Presence: ' + activity_str)
  else:
    print('Presence: ' + error)

@client.event
async def on_message(message):
  # ignore own message
  if message.author == client.user:
    return

  # try to parse message as a command
  command, subcommands = parse_command(message.content)

  # if command is found
  if command != None:
    # admin commands
    if (command == '$daily') and is_author_admin(message):
      await send_startremind('{0} Check in')

    elif (command == '$weekly') and is_author_admin(message):
      await send_startremind('{0} Buy omni-ubiquity net & do parametric transformer')

    elif (command == '$teapot') and is_author_admin(message):
      await send_startremind('{0} Collect teapot coin')

    elif (command == '$checkremind') and is_author_admin(message):
      error = None
      if len(subcommands) == 1:
        message_id = parse_discord_id(subcommands[0])
        if message_id != None:
          error = await check_remind(message_id)
        else:
          error = 'Wrong ID format!'
      else:
        error = 'Command error!'
      if error != None:
        await message.channel.send(error)

    elif (command == '$react') and is_author_admin(message):
      error = None
      if len(subcommands) == 2:
        message_id = parse_discord_id(subcommands[0])
        emoji = subcommands[1]
        if message_id != None:
          reacted_message, reaction, error = await find_and_toggle_reaction(message_id, emoji)
        else:
          error = 'Wrong ID format!'
      else:
        error = 'Command error!'
      if error == None:
        reaction_status = 'added' if reaction else 'removed'
        await message.channel.send('Reaction {0} {1}\nLink: {2}'.format(emoji, reaction_status, reacted_message.jump_url))
      else:
        await message.channel.send(error)

    elif (command == '$presence') and is_author_admin(message):
      activity_type = None
      activity_name = ''
      activity_str = ''
      error = None
      if len(subcommands) >= 2:
        activity_type = subcommands[0]
        activity_name = ' '.join(subcommands[1:])
        activity_str, error = await set_presence(activity_type, activity_name)
      else:
        error = 'Command error!'
      if error == None:
        await message.channel.send('I\'m now ' + activity_str)
      else:
        await message.channel.send(error)

    elif (command == '$debug') and is_author_admin(message):
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
    elif (command == '$roll'):
      await message.reply(random.choices(gi_characters, weights=gi_char_rates)[0])

    elif (command == '$roll10'):
      rolls = random.choices(gi_characters, weights=gi_char_rates, k=10)
      # sort the elements and make them vertically ordered in two-column manner [0, 5, 1, 6, 2, 7, 3, 8, 4, 9]
      rolls.sort()
      rolls.insert(1, rolls.pop(5))
      rolls.insert(3, rolls.pop(6))
      rolls.insert(5, rolls.pop(7))
      rolls.insert(7, rolls.pop(8))
      # format 1 : 10 new lines
      # formatted_1 = '\n'.join(rolls)
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

    # invalid commends
    else:
      await message.channel.send('Command not found!')

  # etc functionalities (if message is not a command)
  elif str_contains(message.content, 'spymon'):
    await toggle_reaction(message, '\U0001f47e')

  elif client.user.mentioned_in(message) and str_mentions(message.content, client.user.id):
    await message.channel.send('Hello {0}'.format(message.author.mention))

########### tasks ############

# function to calculate the total seconds since the specified time (timezone aware)
def seconds_since_time(time):
  now = datetime.now(time.tzinfo)
  ref = datetime.combine(now.date(), time, time.tzinfo)
  seconds = (now - ref).total_seconds()
  return seconds

# function check if the time now is within (hour:minute:second) and (hour:minute:second+cutoff_seconds-1) in timezone UTC+8
def is_time_now(hour, minute, second, cutoff_seconds):
  utc_8 = timezone(timedelta(hours=8))
  ref = time(hour, minute, second, 0, utc_8)
  return True if (0 <= seconds_since_time(ref) < cutoff_seconds) else False

@tasks.loop(seconds=10)
async def periodic():
  periodic.my_count += 1
  # 00:01:00 => send reminder
  if is_time_now(0, 1, 0, periodic.seconds):
    await send_startremind('{0} Check in')
  # 13:01:00 => check reminder
  elif is_time_now(13, 1, 0, periodic.seconds):
    error = await check_remind('Check in', client.user.id)
    if error != None:
      await send_bot_message(error)
  # 22:01:00 => check reminder
  elif is_time_now(22, 1, 0, periodic.seconds):
    error = await check_remind('Check in', client.user.id)
    if error != None:
      await send_bot_message(error)

@periodic.before_loop
async def before_periodic():
  await client.wait_until_ready()
  periodic.my_count = 0

##############################

keep_alive()
periodic.start()
client.run(os.environ['TOKEN'], bot=True)

import discord
import re
import mysql.connector
from mysql.connector import Error
import time
from discord.utils import get
import discord.utils
import random
from datetime import datetime, timedelta

import string
import asyncio
import aiohttp
import subprocess
from imgpy import Img

server_cooldown = {}
intents = discord.Intents(messages=True,guilds=True, message_content=True)

client = discord.Client(heartbeat_timeout=600,intents=intents)
emoji_reaction = {}
message_dict = {}
user_dict = {}
message_count_dict = {}
message_rand_freq_dict = {} 
message_rand_freq_count = {} 
bot_mood = { }
random_colors = { }
classifier = None
featuresets = None
user_color_roles = { }
react_exclude = { }
custom_reactions = { }
new_startup = True
reaction_records = None

connection = mysql.connector.connect(host='localhost', database='Reactomatic', user='REDACTED', password='REDACTED', charset='utf8mb4',use_pure=True)
try:
    cursor = connection.cursor()
    connection.commit()
    result = cursor.execute("""SELECT * FROM Reactions;""")
    reaction_records = cursor.fetchall()
    
    
except mysql.connector.Error as error:
    pass
print("Returned " + str(len(reaction_records)))
# mood_dict = { 'happy': ':grinning:|:smiley:|:smile:|:grin:|:blush:|:relieved:|:thumbsup:|:raised_hands:',
#    'coy': ':wink:|:heart_eyes:|:relaxed:|:smiling_face_with_3_hearts:|:smirk:|:ohmy:|:jaw_drop:|:smiling_imp:|:bikini:|:eggplant:',
#    'pissy': ':f_bomb:|:unamused:|:triumph:|:angry:|:rage:|:middle_finger:|:face_with_symbols_over_mouth:|:imp:|:japanese_goblin:|:rolling_eyes:',
#    'silly':':sweat_smile:|:joy:|:rofl:|:laughing:|:zany_face:|:stuck_out_tongue_winking_eye:|:stuck_out_tongue_closed_eyes:|:stuck_out_tongue:|:upside_down:|:nerd:|:face_with_monocle:|:yagazuzi:',
#    'sad': ':dark_heart:|:pensive:|:disappointed:|:worried:|:frowning2:|:pleading_face:|:persevere:|:disappointed_relieved:|:cry:|:sob:'}
mood_dict = {} 
async def log_message(log_entry):
    return
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
def reconnect_db():
    global connection
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(host='localhost', database='Reactomatic', user='REDACTED', password='REDACTED',charset='utf8mb4',use_pure=True)
    return connection
  
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    global connection
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        cconnection = reconnect_db()
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        connection.commit()
        return True
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return False
            
                
async def select_sql(sql_query, params = None):
    global connection
    await log_message("Select SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = reconnect_db()
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
        await log_message("Returned " + str(records))
        connection.commit()
        return records
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return None
        
async def send_message(message, response):
    await log_message("Message sent back to server " + message.guild.name + " channel " + message.channel.name + " in response to user " + message.author.name + "\n\n" + response)
    message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
    for chunk in message_chunks:
        try:
            await message.channel.send(chunk)
        except:
            pass
        time.sleep(1)

@client.event
async def on_ready():
    global message_dict
    global user_dict
    global message_count_dict
    global message_rand_freq_dict
    global emoji_reaction
    global bot_mood
    global random_colors
    global user_color_roles
    global react_exclude
    global custom_reactions
    global mood_dict
    global new_startup
    global reaction_records
    
    if new_startup:
        # new_startup = False
        guild_ids = []
        print("Logged in!")
        for guild in client.guilds:
            guild_ids.append(guild.id)
            message_count_dict[guild.id] = {}
            emoji_reaction[guild.id] = True
            message_dict[guild.id] = { }
            user_dict[guild.id] = { }
            server_cooldown[guild.id] = datetime.now()
            message_rand_freq_dict[guild.id] = { }
            bot_mood[guild.id] = {} 
            user_color_roles[guild.id] = {} 
            random_colors[guild.id] = {} 
            react_exclude[guild.id] = { }
            custom_reactions[guild.id] = { }
            for member in guild.members:
                bot_mood[guild.id][member.id] = ""
                random_colors[guild.id][member.id] = False
                user_color_roles[guild.id][member.id] = '0'
                react_exclude[guild.id][member.id] = False
                message_count_dict[guild.id][member.name] = 0
                
        
        get_randomcolors = """SELECT ServerId,UserId,RandomColors,IFNULL(ColorRoles,'everyone') FROM RandomColors;"""
        get_react_exclude =  """SELECT ServerId,UserId,ExcludeMe FROM Exclusions;"""
        get_custom_reactions = """SELECT ServerId,Pattern,CustomReaction FROM CustomReactions;"""
        get_moods = """SELECT MoodName,Emojis FROM Moods;"""

#        records = await select_sql(get_reactions)
#        print("Retrieved " + str(len(records)) + " records.")
        # EmojiString,ReactionPattern,MessageOrUser,ReactionType,Frequency,ServerId,Multiple
        for row in reaction_records:
            user_id = int(row[0])
            emoji_string = row[1]
            pattern = row[2]
            try:
                re.compile(pattern)
            except:
                continue
            message_user =  row[3]
            reaction_type = row[4]
            frequency = int(row[5])
            server_id = int(row[6])
            multiple = int(row[7])
            picture = row[10]
            print(row[10])
            if row[9] is not None:
                channels_text = row[9].split(',')
                channels = []
                for channel_id in channels_text:
                    channels.append(int(channel_id))
            else:
                channels = None
            if int(server_id) not in guild_ids:
                continue
            if message_user == 'Message':
                message_dict[server_id][pattern] = { }
                message_dict[server_id][pattern]["Emoji"] = emoji_string
                message_dict[server_id][pattern]["ReactionType"] = reaction_type
                message_dict[server_id][pattern]["Frequency"] = frequency
                message_dict[server_id][pattern]["Multiple"] = multiple
                message_dict[server_id][pattern]["Channels"] = channels
                message_dict[server_id][pattern]["Picture"] = picture
                # if pattern == 'borger':
                    # print(str(message_dict[server_id][pattern]))
            elif row[3] == 'User':

                user_dict[server_id][pattern] = { }
                user_dict[server_id][pattern]["Emoji"] = emoji_string
                user_dict[server_id][pattern]["ReactionType"] = reaction_type
                user_dict[server_id][pattern]["Frequency"] = frequency
                
                #try: message_rand_freq_dict[server_id]
                # except: message_rand_freq_dict[server_id] = { } 
                if (user_dict[server_id][pattern]["Frequency"] == 0):
                    message_rand_freq_dict[server_id][pattern] = random.randint(3,12)
                user_dict[server_id][pattern]["Multiple"] = multiple
            else:
                print("Nothing found.")
        records = await select_sql(get_moods)
        for row in records:
            mood_dict[row[0]] = row[1].split('|')
                 
        records = await select_sql(get_randomcolors)
        for row in records:
#            print(row)
            if row[2] == 'Yes':
                try: random_colors[int(row[0])]
                except: random_colors[int(row[0])] = {} 
                random_colors[int(row[0])][int(row[1])] = True
            else:
                try: random_colors[int(row[0])]
                except: random_colors[int(row[0])] = {} 
                random_colors[int(row[0])][int(row[1])] = False
            try: user_color_roles[int(row[0])]
            except: user_color_roles[int(row[0])] = { }
            user_color_roles[int(row[0])][int(row[1])] = row[3]
        records = await select_sql(get_react_exclude)
        if records:
            for row in records:
                if row[2] == 'Yes':
                    react_exclude[int(row[0])] = {}
                    react_exclude[int(row[0])][int(row[1])] = True
        records = await select_sql(get_custom_reactions)
        for row in records:
            try:
                custom_reactions[int(row[0])][row[1]] = row[2]
            except:
                pass
            
        records = await select_sql(get_react_exclude)
        if records:
            for row in records:
                if row[2] == 'Yes':
                    react_exclude[int(row[0])][int(row[1])] = True                
#    print(random_colors)        
            
@client.event
async def on_guild_join(guild):
    global user_dict
    global message_dict
    global message_count_dict
    global message_rand_freq_count
    global emoji_reaction 
    global bot_mood
    global user_color_roles
    global server_cooldown
    global react_exclude
    global custom_reactions
    await log_message("Joined guild " + guild.name)
    message_count_dict[guild.id] = {}
    emoji_reaction[guild.id] = True
    bot_mood[guild.id] = { }
    custom_reactions[guild.id] = { }
    react_exclude[guild.id] = { }
    server_cooldown[guild.id] = datetime.now()
    for member in guild.members:
        react_exclude[guild.id][member.id] = False
        bot_mood[guild.id][member.id] = ""
        if member.nick:
            message_count_dict[guild.id][member.nick] = 0
            
        else:
            message_count_dict[guild.id][member.name] = 0
    user_dict[guild.id] = { }
    message_dict[guild.id] = { }
    message_rand_freq_count[guild.id] = { }
    user_color_roles[guild.id] = {} 
    
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)
    result = await commit_sql("""DELETE FROM Reactions WHERE ServerId = %s;""",(str(guild.id),))
    await log_message("removed all reactions from guild.")

@client.event
async def on_member_join(member):
    global user_dict
    global message_dict
    global message_count_dict
    global message_rand_freq_count
    global emoji_reaction 
    global bot_mood
    
    await log_message("Member " + member.name + " joined guild " + member.guild.name)
    bot_mood[member.guild.id][member.id] = ""
    react_exclude[member.guild.id][member.id] = False
    
    message_count_dict[member.guild.id][member.name] = 0
    
@client.event
async def on_member_remove(member):
    await log_message("Member " + member.name + " left guild " + member.guild.name)
    
@client.event
async def on_message(message):
    global classifier
    global emoji_reaction
    global user_dict
    global message_dict
    global message_count_dict
    global message_rand_freq_dict
    global bot_mood
    global random_colors
    global featuresets
    global user_color_roles
    global react_exclude
    global custom_reactions
    global mood_dict
    global server_cooldown

    if message.author == client.user:
        return
        

    try:
        react_exclude[message.guild.id][message.author.id]
    except:
        react_exclude[message.guild.id][message.author.id] = False
        
    if react_exclude[message.guild.id][message.author.id] and message.content != '+toggleme':
        return
        
    try:
        message_rand_freq_dict[message.guild.id]
    except:
        message_rand_freq_dict[message.guild.id] = {}
    
      
   
    if message.content.startswith('+') and not message.author.bot:
        current_time = datetime.now()
        if current_time - server_cooldown[message.guild.id]  <= timedelta(seconds=10):
            await send_message(message, "Cooldown in effect. Please try again in " + str(int((current_time - server_cooldown[message.guild.id]).total_seconds())) + " seconds.")
            return
        else:
            server_cooldown[message.guild.id] = datetime.now()

        command_string = message.content.split(' ')
        command = command_string[0].replace('+','')
        parsed_string = message.content.replace("+"+command,"")

        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string)        
        if message.author.nick:
            username = message.author.nick
        else:
            username = message.author.name
        if (command == 'emoji'):
            if (emoji_reaction[message.guild.id]):
                emoji_reaction[message.guild.id] = False
                await send_message(message,"Emoji reactions off.")
            else:
                emoji_reaction[message.guild.id] = True
                for member in message.guild.members:
                    message_count_dict[message.guild.id][member.nick] = 0
                await send_message(message,"Emoji reactions on.")
        elif command == 'invite':
            await send_message(message, "Click here to invite React-o-matic: https://discord.com/api/oauth2/authorize?client_id=684732238797209663&permissions=805694528&scope=bot")
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await send_message(message,"Admin command only!")
                return   
            await send_message(message, "Server count: " + str(len(client.guilds)))             
        elif command == 'setcolorroles':
            user_id = message.author.id
            color_roles = parsed_string.strip()
            user_color_roles[message.guild.id][message.author.id] = color_roles
            records = await select_sql("""SELECT Id FROM RandomColors WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if records:
            
                result = await commit_sql("""UPDATE RandomColors SET ColorRoles=%s WHERE ServerId=%s AND UserId=%s;""",(str(color_roles),str(message.guild.id),str(user_id)))
                if result:
                    await send_message(message, "Random color roles set!")
                else:
                    await send_message(message, "Database error!")
            else:
                result = await commit_sql("""INSERT INTO RandomColors (ServerId,UserId,ColorRoles) VALUES (%s,%s,%s);""",(str(message.guild.id),str(message.author.id),str(color_roles)))
                if result:
                    await send_message(message, "Random color roles set!")
                else:
                    await send_message(message, "Database error!")
        elif command == 'kickfrom':
            if (message.author.id != 610335542780887050):
                await send_message(message,"Admin command only!")
                return           
            for guild in client.guilds:
                if guild.name == parsed_string.strip():
                    await guild.leave()
                    await message.channel.send("Left guild!")
                if str(guild.id) == parsed_string.strip():
                    await guild.leave()
                    await message.channel.send("Left guild!")                    
                    
        elif command == 'toggleme':
            if react_exclude[message.guild.id][message.author.id]:
                react_exclude[message.guild.id][message.author.id] = False
                records = await select_sql("""SELECT ExcludeMe FROM Exclusions WHERE ServerId=%s AND UserId=%s;""", (str(message.guild.id),str(message.author.id)))
                if not records:
                    result = await commit_sql("""INSERT INTO Exclusions (ServerId,UserId,ExcludeMe) VALUES (%s,%s,%s);""",(str(message.guild.id),str(message.author.id), 'No'))
                else:
                    result = await commit_sql("""UPDATE Exclusions SET ExcludeMe='No' WHERE ServerId=%s AND UserId=%s;""", (str(message.guild.id),str(message.author.id)))
                await send_message(message, "You have been removed from the reaction exclude list.")
            else:
                react_exclude[message.guild.id][message.author.id] = True
                records = await select_sql("""SELECT ExcludeMe FROM Exclusions WHERE ServerId=%s AND UserId=%s;""", (str(message.guild.id),str(message.author.id)))
                if not records:
                    result = await commit_sql("""INSERT INTO Exclusions (ServerId,UserId,ExcludeMe) VALUES (%s,%s,%s);""",(str(message.guild.id),str(message.author.id), 'Yes'))
                else:
                    result = await commit_sql("""UPDATE Exclusions SET ExcludeMe='No' WHERE ServerId=%s AND UserId=%s;""", (str(message.guild.id),str(message.author.id)))                
                result = await commit_sql("""UPDATE Exclusions SET ExcludeMe='Yes' WHERE ServerId=%s AND UserId=%s;""", (str(message.guild.id),str(message.author.id)))
                await send_message(message, "You have been added to the reaction exclude list.")
                
        elif command == 'randomcolors':
            try:
                random_colors[message.guild.id]
            except:
                random_colors[message.guild.id] = {} 
            try:
                random_colors[message.guild.id][message.author.id]
            except:
                random_colors[message.guild.id][message.author.id] = True
            message_count_dict[message.guild.id][message.author.name] = 0
            if not random_colors[message.guild.id][message.author.id]:
                random_colors[message.guild.id][message.author.id] = True
                
                result = await select_sql("""SELECT RandomColors FROM RandomColors WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                if not result:
                    insert_result = await commit_sql("""INSERT INTO RandomColors (ServerId,UserId,RandomColors) VALUES (%s,%s,%s);""",(str(message.guild.id),str(message.author.id),'Yes'))
                else:
                    insert_result = await commit_sql("""UPDATE RandomColors SET RandomColors=%s WHERE ServerId=%s AND UserId=%s;""",('Yes',str(message.guild.id),str(message.author.id)))
                        
                await send_message(message, "Random colors on for <@" + str(message.author.id) + "> .")
            else:
                result = await select_sql("""SELECT RandomColors FROM RandomColors WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                if not result:
                    insert_result = await commit_sql("""INSERT INTO RandomColors (ServerId,UserId,RandomColors) VALUES (%s,%s,%s);""",(str(message.guild.id),str(message.author.id),'No'))
                else:
                    insert_result = await commit_sql("""UPDATE RandomColors SET RandomColors=%s WHERE ServerId=%s AND UserId=%s;""",('No',str(message.guild.id),str(message.author.id)))            
                random_colors[message.guild.id][message.author.id] = False
                await send_message(message, "Random colors off for <@" + str(message.author.id) + "> .")
        elif command == 'flop':
            await send_message(message, "*" + message.author.name + " flops into chat*")
        elif (command == 'initialize'):
            await log_message("initialize called by " + username)
            if (message.author.id != 610335542780887050):
                await send_message(message,"Admin command only!")
                return
            await send_message(message,"Creating databases...")
                
            create_reaction_table = """CREATE TABLE Reactions (Id int NOT NULL, UserID varchar(40), EmojiString varchar(1000), ReactionPattern varchar(200), MessageOrUser varchar(10), ReactionType varchar(30), Frequency Int, ServerId varchar(40));"""
            

            result = await execute_sql(create_reaction_table)

            if result:
                await send_message(message,"Database created successfully.")
            else:
                await send_message(message,"Database error!")
                
        elif (command == 'resetall'):
            await log_message("resetall called by " + username)
            if (message.author.id != 610335542780887050):
                await send_message(message,"Admin command only!")
                return
            await send_message(message,"Deleting databases...")
           
            drop_reaction_table = """DROP TABLE Reactions;"""
            
            result = await execute_sql(drop_reaction_table)

            if result:    
                await send_message(message,"Database dropped successfully.")
            else:
                await send_message(message,"Database error!")

        elif command == 'randomaction':
            if message.author.nick:
                name = message.author.nick
            else:
                name = message.author.name        
            responses = ["flops on","rolls around","curls on","lurks by","farts near","falls asleep on","throws Skittles at","throws popcorn at","huggles","snugs","hugs","snuggles","tucks in","watches","stabs","slaps","sexes up","tickles","thwaps","pinches","smells","cries with","laughs at","fondles","stalks","leers at","creeps by","lays on","glomps","clings to","flirts with","makes fun of","nibbles on","noms","protects","stupefies","snickers at"]
            usernames = message.guild.members
            user = random.choice(usernames)
            if parsed_string:
                user_id = message.mentions[0].id
            else:
                user_id = user.id
            response = "*" + name + " " + random.choice(responses) + " <@" + str(user_id) + ">*"
            await send_message(message, response)
            await message.delete()
        elif command == 'me':
            if message.author.nick:
                name = message.author.nick
            else:
                name = message.author.name        
            await send_message(message, "*-" + name + " " + parsed_string + "-*")
            await message.delete()              
        elif command == 'lurk':
            records = await select_sql("""SELECT LurkMessage FROM Lurk WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if records:
                lurks = []
                for row in records:
                    lurks.append(row[0])
                response = message.author.name +  ": " + random.choice(lurks)
                await send_message(message, response)
                await message.delete()
            else:
                if message.author.nick:
                    name = message.author.nick
                else:
                    name = message.author.name
                responses = ["*" + name + " lurks in the shadowy rafters with luminous orbs with parted tiers, trailing long digits through their platinum tresses.*", "**" +name + ":** ::lurk::", "*" + name + " flops on the lurker couch.*", "*double lurk*","*luuuuuurk*","*posts that they are lurking so someone notices they are lurking*"]
                await send_message(message, random.choice(responses))
                await message.delete()            
        elif command == 'mood':
            parsed_string = message.content.replace("+mood ","")
        
            if not parsed_string:
                await send_message(message, "No mood specified!")
                return
            if not message.mentions:
                await send_message(message, "No user specified!")
                return
            m = re.search(r"(?P<mood>.+?) ",parsed_string)
            if not m:
                await send_message(message, "No mood found!")
                return
            else:
                mood = str(m.group('mood'))
            if mood == 'none':
                bot_mood[message.guild.id][message.mentions[0].id] = ""
                await send_message(message, "Mood disabled for user " + message.mentions[0].name)
                return
            records = await select_sql("""SELECT Emojis FROM Moods WHERE MoodName=%s;""", (mood,))
            if not records:
                await send_message(message, "No mood found!")
                return
            for row in records:
                mood_list = row[0].split('|')
            new_mood_list = []
            for mood_item in mood_list:
                mood_item = mood_item.strip()
                if mood_item:
                    new_mood_list.append(mood_item)
            await log_message("Emojis: " + str(new_mood_list))
            bot_mood[message.guild.id][message.mentions[0].id] = new_mood_list
            await log_message("Emoji list: " + str(bot_mood[message.guild.id][message.mentions[0].id]))
            message_rand_freq_dict[message.guild.id][message.author.id] = random.randint(1,5)
            for user in message.guild.members:
                if user.nick:
                    message_count_dict[message.guild.id][message.author.nick] = 0
                else:
                    message_count_dict[message.guild.id][message.author.name] = 0
            
            await send_message(message, "Bot mood set to " + mood + " for user " + message.mentions[0].name + "!") 
            
            
        elif (command == 'addreaction'):
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to add reactions!")
                return
            message_type = False
            user_type = False
            reaction_add = False
            reply_add = False
            emoji_string = " "
            pattern_string = " "
            frequency = "0"
            message_or_user = " "
            react_or_reply = " "
            await log_message("addreaction called by " + username)
            parsed_string = message.content
            emoji_re = re.compile(r"-emoji (.+?) -pat", re.MULTILINE | re.S)
            pattern_re = re.compile(r"-pattern (.+?) -freq", re.MULTILINE | re.S)
            frequency_re = re.compile(r"-frequency (\d+) -", re.MULTILINE | re.S)
            message_re = re.compile(r"-message", re.MULTILINE | re.S)
            user_re = re.compile(r"-user", re.MULTILINE | re.S)
            reaction_re = re.compile(r"-react", re.MULTILINE | re.S)
            reply_re = re.compile(r"-reply", re.MULTILINE | re.S)
            multiple_re = re.compile(r"-multiple", re.MULTILINE | re.S)
            picture_re = re.compile(r"-picture", re.MULTILINE | re.S)
            user_id = message.author.id
            _id = 1
            m = emoji_re.search(parsed_string)
            if not m:
                await send_message(message,"No emoji specified!")
                return
            emoji_string = m.group()
            emoji_string = emoji_string.replace("-emoji ","")
            emoji_string = emoji_string.replace("-pat","")

            emoji_string = emoji_string.strip()
            
            m = pattern_re.search(parsed_string)
            if not m:
                await send_message(message,"No pattern specified!")
                return
            pattern_string = m.group()
            pattern_string = pattern_string.replace("-pattern ","")
            pattern_string = pattern_string.replace("-freq","")
            
            pattern_string = pattern_string.strip()
            
            m = frequency_re.search(parsed_string)
            if not m:
                await send_message(message,"No frequency specified, setting to every message!")
            else:
                frequency = m.group()
                frequency = frequency.replace("-frequency ","")
                frequency = frequency.replace("-","")
                frequency = frequency.strip()
                
            if message_re.search(parsed_string):
                message_type = True
                message_or_user = "Message"
            if user_re.search(parsed_string):
                user_type = True
                message_or_user = "User"
            
            if reply_re.search(parsed_string):
                reply_add = True
                react_or_reply = "Reply"
            if reaction_re.search(parsed_string):
                reaction_add = True
                react_or_reply = "React"
            if picture_re.search(parsed_string):
                picture = "Yes"
            else:
                picture= "No"
            try:
                re.compile(pattern_string)
            except:
                await send_message(message, "That isn't a valid regular expression for -pattern. Please check and try again.")
                return
            if not message_type and not user_type:
                await send_message(message,"No user or message flag specified!")
                return
            if message_type and user_type:
                await send_message(message,"You cannot specifiy both the user and message flag!")
                return
            if not reaction_add and not reply_add:
                await send_message(message,"No reply or react action flag specified!")
                return
            if reaction_add and reply_add:
                await send_message(message,"You cannot add both a reply and react action!")
                return
            if multiple_re.search(message.content):
                multiple = 1
            else:
                multiple = 0
            records = await select_sql("""SELECT COUNT(ReactionPattern) FROM Reactions WHERE ServerId=%s;""",(str(message.guild.id),))
            for row in records:
                count = int(row[0])
            if count > 50:
                await send_message(message, "You have reached the 50 reaction maximum. Please delete some reactions to add another one.")
                return
            add_reaction_entry = """INSERT INTO Reactions (UserID, EmojiString, ReactionPattern, MessageOrUser, ReactionType, Frequency, ServerId, Multiple, PictureReaction) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s);"""
            post_to_save = (user_id, emoji_string, pattern_string, message_or_user, react_or_reply, frequency, str(message.guild.id), str(multiple), picture)
            if message.channel_mentions:
                channel_ids = ""
                for channel in message.channel_mentions:
                    channel_ids = channel_ids + str(channel.id) + ","
                channel_ids = re.sub(r",$","",channel_ids)    
                add_reaction_entry = """INSERT INTO Reactions (UserID, EmojiString, ReactionPattern, MessageOrUser, ReactionType, Frequency, ServerId, Multiple, Channels,PictureReaction) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                post_to_save = (user_id, emoji_string, pattern_string, message_or_user, react_or_reply, frequency, str(message.guild.id), str(multiple), str(channel_ids), str(picture))
            result = await commit_sql(add_reaction_entry, post_to_save)
            if result:
                await send_message(message,"Reaction saved successfully.")
            else:
                await send_message(message,"Database error!")

            get_reactions = """SELECT EmojiString,ReactionPattern,MessageOrUser,ReactionType,Frequency,Multiple,Channels,PictureReaction FROM Reactions WHERE ServerId=%s;"""
            records = await select_sql(get_reactions, (str(message.guild.id),))
            for row in records:
                if "Message" in row[2]:
                    message_dict[message.guild.id][row[1]] = {}
                    message_dict[message.guild.id][row[1]]["Emoji"] = row[0]
                    message_dict[message.guild.id][row[1]]["ReactionType"] = row[3]
                    message_dict[message.guild.id][row[1]]["Frequency"] = row[4]
                    message_dict[message.guild.id][row[1]]["Multiple"] = row[5]
                    if row[6] is not None:
                        channels = []
                        channel_text = row[6].split(',')
                        for channel_id in channel_text:
                            channels.append(int(channel_id))
                    else:
                        channels = None
                    message_dict[message.guild.id][row[1]]["Channels"] = channels
                    message_dict[message.guild.id][row[1]]["Picture"] = row[7]
                elif "User" in row[2]:
                    user_dict[message.guild.id][row[1]] = {} 
                    user_dict[message.guild.id][row[1]]["Emoji"] = row[0]
                    user_dict[message.guild.id][row[1]]["ReactionType"] = row[3]
                    user_dict[message.guild.id][row[1]]["Frequency"] = row[4]
                    if (user_dict[message.guild.id][row[1]]["Frequency"] == 0):
                        message_rand_freq_dict[message.guild.id][row[1]] = random.randint(1,5)
                    user_dict[message.guild.id][row[1]]["Multiple"] = row[5]
                else:
                    await log_message("Nothing found.")
        elif (command == 'changereaction'):
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to change reactions!")
                return
            message_type = False
            user_type = False
            reaction_add = False
            reply_add = False
            emoji_string = " "
            pattern_string = " "
            frequency = "0"
            message_or_user = " "
            react_or_reply = " "
            await log_message("changereaction called by " + username)
            parsed_string = message.content
            emoji_re = re.compile(r"-emoji (.+?) -", re.MULTILINE | re.S)
            pattern_re = re.compile(r"-pattern (.+?) -", re.MULTILINE | re.S)
            frequency_re = re.compile(r"-frequency (\d+) -", re.MULTILINE | re.S)
            message_re = re.compile(r"-message", re.MULTILINE | re.S)
            user_re = re.compile(r"-user", re.MULTILINE | re.S)
            reaction_re = re.compile(r"-react", re.MULTILINE | re.S)
            reply_re = re.compile(r"-reply", re.MULTILINE | re.S)
            user_id = message.author.id
            id = 1
            m = emoji_re.search(parsed_string)
            if not m:
                await send_message(message,"No emoji specified!")
                return
            emoji_string = m.group()
            emoji_string = emoji_string.replace("-emoji ","")
            emoji_string = emoji_string.replace("-","")
            emoji_string = emoji_string.strip()
            
            m = pattern_re.search(parsed_string)
            if not m:
                await send_message(message,"No pattern specified!")
                return
            pattern_string = m.group()
            pattern_string = pattern_string.replace("-pattern ","")
            pattern_string = pattern_string.replace("-","")
            pattern_string = pattern_string.strip()
            
            m = frequency_re.search(parsed_string)
            if not m:
                await send_message(message,"No frequency specified, setting to every message!")
            else:
                frequency = m.group()
                frequency = frequency.replace("-frequency ","")
                frequency = frequency.replace("-","")
                frequency = frequency.strip()
                
            if message_re.search(parsed_string):
                message_type = True
                message_or_user = "Message"
            if user_re.search(parsed_string):
                user_type = True
                message_or_user = "User"
            
            if reply_re.search(parsed_string):
                reply_add = True
                react_or_reply = "Reply"
            if reaction_re.search(parsed_string):
                reaction_add = True
                react_or_reply = "React"
                
            if not message_type and not user_type:
                await send_message(message,"No user or message flag specified!")
                return
            if message_type and user_type:
                await send_message(message,"You cannot specifiy both the user and message flag!")
                return
            if not reaction_add and not reply_add:
                await send_message(message,"No reply or react action flag specified!")
                return
            if reaction_add and reply_add:
                await send_message(message,"You cannot add both a reply and react action!")
                return
            change_reaction_entry = """UPDATE Reactions SET UserID=%s, EmojiString=%s, ReactionType=%s, Frequency=%s WHERE ReactionPattern=%s AND ServerId=%s ;"""            

            post_to_save = (user_id, emoji_string, react_or_reply, frequency,pattern_string, str(message.guild.id))
            result = await commit_sql(change_reaction_entry, post_to_save)
            if result:
                await send_message(message,"Reaction saved successfully.")
            else:
                await send_message(message,"Database error!")
            message_dict[message.guild.id].clear()
            user_dict[message.guild.id].clear()
            get_reactions = """SELECT EmojiString,ReactionPattern,MessageOrUser,ReactionType,Frequency FROM Reactions WHERE ServerId=%s;"""
            records = await select_sql(get_reactions, (str(message.guild.id),))
            for row in records:
                if "Message" in row[2]:
                    message_dict[message.guild.id][row[1]] = {}
                    message_dict[message.guild.id][row[1]]["Emoji"] = row[0]
                    message_dict[message.guild.id][row[1]]["ReactionType"] = row[3]
                    message_dict[message.guild.id][row[1]]["Frequency"] = row[4]
                elif "User" in row[2]:
                    user_dict[message.guild.id][row[1]] = {} 
                    user_dict[message.guild.id][row[1]]["Emoji"] = row[0]
                    user_dict[message.guild.id][row[1]]["ReactionType"] = row[3]
                    user_dict[message.guild.id][row[1]]["Frequency"] = row[4]            
                else:
                    await log_message("Nothing found.")
        elif (command == 'deletereaction'):
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to delete reactions!")
                return
            message_type = False
            user_type = False
            reaction_add = False
            reply_add = False
            emoji_string = " "
            pattern_string = " "
            frequency = "0"
            message_or_user = " "
            react_or_reply = " "
            await log_message("deletereaction called by " + username)
            parsed_string = message.content
            emoji_re = re.compile(r"-emoji (.+?) -", re.MULTILINE | re.S)
            pattern_re = re.compile(r"-pattern (.+)", re.MULTILINE | re.S)
            frequency_re = re.compile(r"-frequency (\d+) -", re.MULTILINE | re.S)
            message_re = re.compile(r"-message", re.MULTILINE | re.S)
            user_re = re.compile(r"-user", re.MULTILINE | re.S)
            reaction_re = re.compile(r"-react", re.MULTILINE | re.S)
            reply_re = re.compile(r"-reply", re.MULTILINE | re.S)
            user_id = message.author.id
            id = 1
            
            m = pattern_re.search(parsed_string)
            if not m:
                await send_message(message,"No pattern specified!")
                return
            pattern_string = m.group()
            pattern_string = pattern_string.replace("-pattern ","")
            pattern_string = pattern_string.strip()
            await log_message("Pattern string: " + pattern_string)
            delete_reaction_entry = """DELETE FROM Reactions WHERE ReactionPattern = %s AND ServerId=%s;"""            
            result = await commit_sql(delete_reaction_entry, (pattern_string,str(message.guild.id)))
            if result:
                await send_message(message,"Reaction deleted successfully.")
            else:
                await send_message(message, "Error deleting reaction!")
                
            message_dict[message.guild.id] = { }
            user_dict[message.guild.id] = {}                   
            get_reactions = """SELECT EmojiString,ReactionPattern,MessageOrUser,ReactionType,Frequency,Multiple,Channels FROM Reactions WHERE ServerId=%s;"""
            records = await select_sql(get_reactions, (str(message.guild.id),))
            for row in records:
                if "Message" in row[2]:
                    message_dict[message.guild.id][row[1]] = {}
                    message_dict[message.guild.id][row[1]]["Emoji"] = row[0]
                    message_dict[message.guild.id][row[1]]["ReactionType"] = row[3]
                    message_dict[message.guild.id][row[1]]["Frequency"] = row[4]
                    message_dict[message.guild.id][row[1]]["Multiple"] = row[5]
                    if row[6] is not None:
                        channels = []
                        channel_text = row[6].split(',')
                        for channel_id in channel_text:
                            channels.append(int(channel_id))
                    else:
                        channels = None
                    message_dict[message.guild.id][row[1]]["Channels"] = channels
                elif "User" in row[2]:
                    user_dict[message.guild.id][row[1]] = {} 
                    user_dict[message.guild.id][row[1]]["Emoji"] = row[0]
                    user_dict[message.guild.id][row[1]]["ReactionType"] = row[3]
                    user_dict[message.guild.id][row[1]]["Frequency"] = row[4]
                    if (user_dict[message.guild.id][row[1]]["Frequency"] == 0):
                        message_rand_freq_dict[message.guild.id][row[1]] = random.randint(1,5)
                    user_dict[message.guild.id][row[1]]["Multiple"] = row[5]
                else:
                    await log_message("Nothing found.")
      
        elif command == 'initializemood':
            await log_message("resetall called by " + username)
            if (message.author.id != 610335542780887050):
                await send_message(message,"Admin command only!")
                return        
            result = await execute_sql("""CREATE TABLE Moods (Id int auto_increment, MoodName varchar(100), Emojis TEXT, PRIMARY KEY(Id));""")
            if result:
                await log_message("Mood database generated.")
            else:
                await log_message("Database error!")
            

        elif command=='addmood':
            await log_message("resetall called by " + username)
            if (message.author.id != 610335542780887050):
                await send_message(message,"Admin command only!")
                return        
            mood = command_string[1]
            emojis = message.content.replace("+addmood ","").replace(mood,"").replace(" ","|")
            

            result = await commit_sql("""INSERT INTO Moods (MoodName,Emojis) VALUES (%s,%s);""", (mood, emojis))
            await send_message(message, "Moods loaded!")

        elif command == 'serverlist':
            await log_message("servercount called by " + username)
            if (message.author.id != 610335542780887050):
                await send_message(message,"Admin command only!")
                return   
            response = "Server count: " + str(len(client.guilds))
            for x in client.guilds:
                if x.name:
                    response = response + x.name + "\n"
            await send_message(message,response)
            
        elif command == 'mood':
            parsed_string = message.content.replace("+mood ","")
        
            if not parsed_string:
                await send_message(message, "No mood specified!")
                return
            if not message.mentions:
                await send_message(message, "No user specified!")
                return
            m = re.search(r"(?P<mood>.+?) ",parsed_string)
            if not m:
                await send_message(message, "No mood found!")
                return
            else:
                mood = str(m.group('mood'))
            if mood == 'none':
                bot_mood[message.guild.id][message.mentions[0].id] = ""
                await send_message(message, "Mood disabled for user " + message.mentions[0].name)
                return
            records = await select_sql("""SELECT Emojis FROM Moods WHERE MoodName=%s;""", (mood,))
            if not records:
                await send_message(message, "No mood found!")
                return
            for row in records:
                mood_list = row[0].split('|')
            for mood_item in mood_list:
                mood_item = mood_item.strip()
            await log_message("Emojis: " + str(mood_list))
            bot_mood[message.guild.id][message.mentions[0].id] = mood_list
            await log_message("Emoji list: " + str(bot_mood[message.guild.id][message.mentions[0].id]))
            message_rand_freq_dict[message.guild.id][message.author.id] = random.randint(1,5)
            for user in message.guild.members:
                if user.nick:
                    message_count_dict[message.guild.id][message.author.nick] = 0
                else:
                    message_count_dict[message.guild.id][message.author.name] = 0
            
            await send_message(message, "Bot mood set to " + mood + " for user " + message.mentions[0].name + "!")
        elif command == 'addcustomreaction':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to add reactions!")
                return
            if not message.attachments:
                await send_message(message, "No picture supplied!")
                return
            if not parsed_string:
                await send_message(message, "No name supplied!")
                return
            file_url = message.attachments[0].url
            file_name = message.attachments[0].filename
            await send_message(message, "Downloading file " + file_name + "...")
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
 #           await send_message(message, "File saved to " + file_name + "!")
                    with open('/home/REDACTED/BotMaster/customcommands/' + parsed_string.strip() + "." + re.sub(r".*\.(.*)",r"\1",file_name), 'wb') as file:
                        bytes = await resp.read()
                        
                        file.write(bytes)
            await send_message(message, "Reaction added.")   
            
        elif command == 'cr':
            if not parsed_string:
                await send_message(message, "No reaction specified!")
                return
            
            output = subprocess.run(["/home/REDACTED/BotMaster/customcommands/list.sh"], universal_newlines=True, stdout=subprocess.PIPE)
            reaction_list = output.stdout.split('\n')
            reaction_found = False
            for reaction in reaction_list:
                await log_message("Reaction name: " + reaction + " Looking for: " + re.sub(r"(.*)\..*",r"\1",reaction))
                if re.sub(r"(.*)\..*",r"\1",reaction) == parsed_string.strip():
                    filename = reaction
                    reaction_found = True
            if not reaction_found:
                await send_message(message, "That reaction wasn't found. Try adding it with +addcustomreaction!")
                return
            file_path = "/home/REDACTED/BotMaster/customcommands/" + filename
            await message.channel.send(file=discord.File(file_path))
        elif command == 'crlist':
            output = subprocess.run(["/home/REDACTED/BotMaster/customcommands/list.sh"], universal_newlines=True, stdout=subprocess.PIPE)
            reaction_list = output.stdout.split('\n')
            response = "**Custom Reaction List**\n\n"
            for reaction in reaction_list:
                response = response + re.sub(r"(.*)\..*",r"\1",reaction) + "\n"
            await send_message(message, response)
        elif command == 'addcustompattern':
            parsed_string = message.content
            reaction_re = re.compile(r"-reaction (.+?) -", re.MULTILINE | re.S)
            pattern_re = re.compile(r"-pattern (.+)", re.MULTILINE | re.S)
            m = pattern_re.search(parsed_string)
            if not m:
                await send_message(message,"No pattern specified!")
                return
            pattern_string = m.group()
            pattern_string = pattern_string.replace("-pattern ","")
            pattern_string = pattern_string.strip()    
            m = reaction_re.search(parsed_string)
            if not m:
                await send_message(message,"No reaction specified!")
                return
            reaction_string = m.group()
            reaction_string = reaction_string.replace("-reaction ","")
            reaction_string = reaction_string.replace(" -","")
            reaction_string = reaction_string.strip()           
            result = await commit_sql("""INSERT INTO CustomReactions (ServerId,Pattern,CustomReaction) VALUES (%s,%s,%s);""", (str(message.guild.id), pattern_string, reaction_string))
            custom_reactions[message.guild.id][pattern_string] = reaction_string
            if result:
                await send_message(message, "Custom pattern added successfully.")
            else:
                await send_message(message, "Database error!")
        elif command == 'addlurk':
            if not parsed_string:
                await send_message(message, "You didn't specify a lurk message!")
                return
            result = await commit_sql("""INSERT INTO Lurk (ServerId, UserId, LurkMessage) VALUES (%s, %s, %s);""",(str(message.guild.id),str(message.author.id),parsed_string))
            if result:
                await send_message(message, "Lurk message successfully added!")
            else:
                await send_message(message, "Database error!")
        elif command == 'deletelurk':
            if not parsed_string:
                await send_message(message, "You didn't specify a lurk message!")
                return
            result = await commit_sql("""DELETE FROM Lurk WHERE ServerId=%s AND UserId=%s AND LurkMessage=%s;""",(str(message.guild.id),str(message.author.id),parsed_string))
            await send_message(message, "Lurk message deleted.")
            
        elif (command == 'info' or command == 'help'):
            await send_message(message,"**This is React-o-matic, a Discord bot for reactions and auto-replies!**\n\n>>> **AVAILABLE COMMANDS**\n\n`+info` or `+help` This help message.\n\n`+addreaction -emoji EMOJI_STRING -pattern REGULAR_EXPRESSION -frequency NUMBER_OF_MESSAGES -user/-message -react/-reply [-multiple] [-picture] [#channelmentions]`\n\nAdd a reaction.\n\n__**Required Flags**__\n`-emoji`: The Discord emoji or Unicode character. :emoji: is accepted..\n`-frequency`: This is the number of messages to wait until reacting or replying to a message by a user that matches the pattern.For username reactions, this is always 1.\n`-user`: Apply the pattern to usernames.\n`-message`: Apply the pattern to messages sent.\n`-react`: React to a message matching the pattern.\n`-reply`: Reply to a message matching the pattern.\n\n-user/-message cannot be combined, and neither can -react/-reply.\n\n`-multiple`: Optional, treat the emoji list as multiple reactions to the same post instead of as random choice. Works only on message/react type.\n`#channelmentions`: An optional parameter that restricts the reaction to a particular channel or channels. Works on react or reply on message types only.\n`-picture`: An optional parameter that will instruct the bot to react to either -pattern or any message containing a picture as a file. For links, use a pattern of `http.*`\n\n`+emoji` Turn the reactions on or off. The bot starts up in on mode by default.\n\n`+listreactions` Show all reactions defined.\n\n`+deletereaction -pattern REGULAR_EXPRESSION`:  Delete this reaction with the specified pattern.")
            await send_message(message, ">>> `+mood MOOD_NAME @user`: Set the bot's mood towards a particular user. The bot will react with random emojis to the user on a random basis. Valid moods are *happy, coy, silly, pissy,* and *sad*. Set the mood to *none* to clear the bot's mood for that user. (New moods may be added by the developer in the future).\n\n`+randomaction @user`: Perform a random action at the mentioned user. If no user is mentioned, one is chosen at random. Not all actions are positive ones!\n\n`+me TEXT` Post as the bot performing an action with your username.\n\n`+lurk` lurk through the channel.\n\n")
            await send_message(message, ">>> **MORE ABOUT EMOJI**\n\nThe bot can respond to a message or user by selecting randomly from a set of emoji, and can also respond to a random interval of message as well as fixed. To use this functionality, set the -emoji field to multiple emoji separated by forward slashes, such as -emoji 😁 / 😲 / 😙. Ensure you have a space between the emoji (or emoji code) and the forward slash as shown. For random intervals, set -frequency to 0.\n\nThe bot can reply with text as well as emoji. For this, set -emoji to the text you want and use -reply.\n\nFor username reactions, do not use a user mention from Discord. The -pattern field should be the text of the username to match.")
            await send_message(message, ">>> **COLOR ROLES**\n\nThe bot can randomly change your color if color roles are set up. The bot does not have manage roles permission by default, so you must move the bot's role above the color roles and explicitly give it manage role permissions. Also, the user must have a username reaction defined for the colors to be changed.\n\n**COMMANDS**\n\n`+setcolorroles role1,role2,role3`: Set thje color roles you'd like to have the bot select between.\n\n`+randomcolors` Toggle random colors on or off for yourself.")
        elif (command == 'listreactions'):
            response = "**Reaction list**\n\n**USER NAME REACTIONS\n__Pattern__ __Emoji__ __ReactionType__ __Frequency__\n\n"
            for pattern in user_dict[message.guild.id]:
                response = response + pattern + " " + user_dict[message.guild.id][pattern]["Emoji"] + " " + user_dict[message.guild.id][pattern]["ReactionType"] + " " + str(user_dict[message.guild.id][pattern]["Frequency"]) + "\n"
            response = response + "\nMESSAGE REACTIONS\n__Pattern__ __Emoji__ __ReactionType__ __Frequency__\n\n"
            for pattern in message_dict[message.guild.id]:
                response = response + pattern + " " + message_dict[message.guild.id][pattern]["Emoji"] + " " + message_dict[message.guild.id][pattern]["ReactionType"] + " " + str(message_dict[message.guild.id][pattern]["Frequency"]) + "\n"
            await send_message(message, response)
        else:
            pass

    # if message.author.nick:
        # username = message.author.nick
    # else:
        # username = message.author.name
    # username = message.author.display_name

    user = message.author
    username = user.name    

    try:
        message_count_dict[message.guild.id][username]
    except:
        message_count_dict[message.guild.id][username] = 0
    
    

    


    message_count_dict[message.guild.id][username] = message_count_dict[message.guild.id][username] + 1
    try: 
        if bot_mood[message.guild.id][message.author.id]:

            if (message_count_dict[message.guild.id][username] <= 1):
                message_rand_freq_dict[message.guild.id][message.author.id] = random.randint(5, 10)
                frequency = message_rand_freq_dict[message.guild.id][message.author.id]
                await log_message("New Frequency: " + str(frequency))
            elif message_count_dict[message.guild.id][username] >= 2:
                frequency = message_rand_freq_dict[message.guild.id][message.author.id]
#            await log_message("Frequency: " + str(frequency))
#            await log_message("Message count: " + str(message_count_dict[message.guild.id][username]))
            if message_count_dict[message.guild.id][username] == frequency:
                message_count_dict[message.guild.id][username] = 0
                try:
                    await message.add_reaction(random.choice(bot_mood[message.guild.id][message.author.id]))
                except:
                    pass
    except:
        pass
    if emoji_reaction[message.guild.id]:
        user = message.author
        username = user.name
        # try:
            # await log_message("Message count for " + username + " = " + str(message_count_dict[message.guild.id][username]))
        # except:
            # pass
        for pattern in custom_reactions[message.guild.id]:
   
            if re.search(pattern, message.content, re.IGNORECASE | re.S):
                output = subprocess.run(["/home/REDACTED/BotMaster/customcommands/list.sh"], universal_newlines=True,
                                        stdout=subprocess.PIPE)
                reaction_list = output.stdout.split('\n')
                reaction_found = False
                for reaction in reaction_list:
                    await log_message(
                        "Reaction name: " + reaction + " Looking for: " + re.sub(r"(.*)\..*", r"\1", reaction))
                    if re.sub(r"(.*)\..*", r"\1", reaction) == custom_reactions[message.guild.id][pattern].strip():
                        filename = reaction
                        reaction_found = True
                if not reaction_found:
                    return
                file_path = "/home/REDACTED/BotMaster/customcommands/" + filename
                await message.channel.send(file=discord.File(file_path))
                return
        if message.embeds:
            message_content = str(message.embeds[0].to_dict()) + " " + str(message.content)
        else:
                message_content = message.content
        for pattern in message_dict[message.guild.id]:

            try:
                message_dict[message.guild.id][pattern]["Multiple"]
            except:
                message_dict[message.guild.id][pattern]["Multiple"] = 0
            try: message_dict[message.guild.id][pattern]["Channels"]
            except: message_dict[message.guild.id][pattern]["Channels"] = None
            if message_dict[message.guild.id][pattern]["Channels"] is not None:
                if message.channel.id not in message_dict[message.guild.id][pattern]["Channels"]:
                    continue
            if message_dict[message.guild.id][pattern]["Picture"] == 'Yes' and message.attachments:
                message_content = pattern
            if re.search(pattern, message_content, re.IGNORECASE | re.S | re.MULTILINE):
                emoji_string = message_dict[message.guild.id][pattern]["Emoji"]
                if '/' in emoji_string:
                    if message_dict[message.guild.id][pattern]["Multiple"] == 0 and message_dict[message.guild.id][pattern]["ReactionType"]=='React':
                        emoji_choices = emoji_string.split('/')
                        emoji_string = str(random.choice(emoji_choices)).strip()
                    
                        reaction_type = message_dict[message.guild.id][pattern]["ReactionType"]
                        frequency = int(message_dict[message.guild.id][pattern]["Frequency"])
                        if (reaction_type == 'React'):
                            try:
                                await message.add_reaction(emoji_string)
                            except:
                                pass
                            continue
                        elif (reaction_type == 'Reply'):
                            if '/' in emoji_string and (not re.search('http',emoji_string, re.I)):
                                emoji_string = random.choice(emoji_string.split('/'))                        
                            await send_message(message, emoji_string)
                            continue
                        else:
                            pass
                    else:
                        if message_dict[message.guild.id][pattern]["ReactionType"] == 'React':
                            emoji_choices = emoji_string.split('/')
                            for emoji_string_ in emoji_choices:
                                emoji_string = emoji_string_.strip()
                                reaction_type = message_dict[message.guild.id][pattern]["ReactionType"]
                                frequency = int(message_dict[message.guild.id][pattern]["Frequency"])
                                if (message_dict[message.guild.id][pattern]["ReactionType"] == 'React'):
                                    try:
                                        await message.add_reaction(emoji_string)
                                    except:
                                        pass
                                    await asyncio.sleep(1)
                                    continue
                                   # except:
                                   #     pass
                                    
                        elif (message_dict[message.guild.id][pattern]["ReactionType"] == 'Reply'):
                            if '/' in emoji_string and not re.search('http',emoji_string, re.I):
                                emoji_string = random.choice(emoji_string.split('/'))                        
                            await send_message(message, emoji_string)
                            await asyncio.sleep(1)
                        else:
                            pass      
                else:
                    if message_dict[message.guild.id][pattern]["ReactionType"]=='React':
                        emoji_choices = emoji_string.split('/')
                        emoji_string = str(random.choice(emoji_choices)).strip()
                
                    reaction_type = message_dict[message.guild.id][pattern]["ReactionType"]
                    frequency = int(message_dict[message.guild.id][pattern]["Frequency"])
                    if (reaction_type == 'React'):
                        try:
                            await message.add_reaction(emoji_string)
                        except:
                            pass
                        continue

                    elif (reaction_type == 'Reply'):
                        if '/' in emoji_string and not re.search('http',emoji_string, re.I):
                            emoji_string = random.choice(emoji_string.split('/'))
                        await send_message(message, emoji_string)
                    else:
                        pass               
        for pattern in user_dict[message.guild.id]:
            try:
                user_dict[message.guild.id][pattern]["Multiple"]
            except:
                user_dict[message.guild.id][pattern]["Multiple"] = 0
                
            if re.search(pattern, str(username), re.IGNORECASE | re.S):
                emoji_string = user_dict[message.guild.id][pattern]["Emoji"]
                if '/' in emoji_string:
                    if user_dict[message.guild.id][pattern]["Multiple"] == 0 and user_dict[message.guild.id][pattern]["ReactionType"] == 'React':
                        emoji_choices = emoji_string.split('/')
                        emoji_string = str(random.choice(emoji_choices)).strip()

                        reaction_type = user_dict[message.guild.id][pattern]["ReactionType"]
                        frequency = int(user_dict[message.guild.id][pattern]["Frequency"])
                        try:
                            message_count_dict[message.guild.id][username]
                        except:
                            message_count_dict[message.guild.id][username] = 0
                        await log_message("Frequency: " + str(frequency))
                        if (frequency == 0 and message_count_dict[message.guild.id][username] <= 1):
                            message_rand_freq_dict[message.guild.id][pattern] = random.randint(5, 10)
                            frequency = message_rand_freq_dict[message.guild.id][pattern]
                            await log_message("New Frequency: " + str(frequency))

                        elif (frequency == 0 and message_count_dict[message.guild.id][username] >= 2):
                            frequency = message_rand_freq_dict[message.guild.id][pattern]

                        if (reaction_type == 'React') and message_count_dict[message.guild.id][username] >= frequency:
                            message_count_dict[message.guild.id][username] = 0
                            try:
                                await message.add_reaction(emoji_string)
                            except:
                                pass
                            #                   try:
#                            print(str(random_colors[message.guild.id][message.author.id]))
                            color_roles = user_color_roles[message.guild.id][message.author.id].split(',')
                            # await log_message("Color roles: " + str(color_roles))
                            if random_colors[message.guild.id][message.author.id]:
                                await log_message("You have random colors on.")
                                for rolec in color_roles:
                                    await log_message("Color role: " + rolec)
                                    for role in message.author.roles:
                                        # await log_message("Role name: " + str(role.name))
                                        if rolec.strip() == role.name:
                                            color = random.choice(color_roles)
                                            await log_message("Your color is " + color)
                                           # try:
                                            await message.author.remove_roles(get(message.guild.roles, name=rolec.strip()))
                                            await message.author.add_roles(get(message.guild.roles, name=color.strip()))
                                       #     except:
                                      #          pass
                                            return
                        #                   except:
                    #                       pass
                    else:
                        emoji_choices = emoji_string.split('/')
                        for emoji_string_ in emoji_choices:
                            emoji_string = emoji_string_.strip()
                            try:
                                await message.add_reaction(emoji_string)

                            except:
                                pass
                            await asyncio.sleep(1)
                        reaction_type = user_dict[message.guild.id][pattern]["ReactionType"]
                        frequency = int(user_dict[message.guild.id][pattern]["Frequency"])
                        await log_message("Frequency: " + str(frequency))
                        if (frequency == 0 and message_count_dict[message.guild.id][username] <= 1):
                            message_rand_freq_dict[message.guild.id][pattern] = random.randint(1, 5)
                            frequency = message_rand_freq_dict[message.guild.id][pattern]
                            await log_message("New Frequency: " + str(frequency))

 #                       elif (frequency == 0 and message_count_dict[message.guild.id][username] >= 2):
  #                          frequency = message_rand_freq_dict[message.guild.id][pattern]

                        if (reaction_type == 'React') and message_count_dict[message.guild.id][username] >= frequency:
                            message_count_dict[message.guild.id][username] = 0
#                            print(str(random_colors[message.guild.id][message.author.id]))
                            try:
                                color_roles = user_color_roles[message.guild.id][message.author.id].split(',')
                            # await log_message("Color roles: " + str(color_roles))
                                if random_colors[message.guild.id][message.author.id]:
                                    await log_message("You have random colors on.")
                                    for rolec in color_roles:
                                        await log_message("Color role: " + rolec)
                                        for role in message.author.roles:
                                            # await log_message("Role name: " + str(role.name))
                                            if rolec.strip() == role.name:
                                                color = random.choice(color_roles)
                                                await log_message("Your color is " + color)

                                                await message.author.remove_roles(get(message.guild.roles, name=rolec.strip()))
                                                await message.author.add_roles(get(message.guild.roles, name=color.strip()))
                                                return
                                            
                            except:
                                pass         
                else:
                    if user_dict[message.guild.id][pattern]["ReactionType"] == 'React':
                        emoji_choices = emoji_string.split('/')
                        emoji_string = str(random.choice(emoji_choices)).strip()
                
                    reaction_type = user_dict[message.guild.id][pattern]["ReactionType"]
                    frequency = int(user_dict[message.guild.id][pattern]["Frequency"])
                    try:
                        message_count_dict[message.guild.id][username]
                    except:
                        message_count_dict[message.guild.id][username] = 0
                    if (frequency == 0 and message_count_dict[message.guild.id][username] <= 1):
                        message_rand_freq_dict[message.guild.id][pattern] = random.randint(1, 5)
                        frequency = message_rand_freq_dict[message.guild.id][pattern]
                        await log_message("New Frequency: " + str(frequency))                    
                    if (reaction_type == 'React') and message_count_dict[message.guild.id][username] >= frequency:
                        message_count_dict[message.guild.id][username] = 0
                        try:
                            await message.add_reaction(emoji_string)
                        except:
                            pass
                        try:    
                            color_roles = user_color_roles[message.guild.id][message.author.id].split(',')
                            if random_colors[message.guild.id][message.author.id]:
                                await log_message("You have random colors on.")
                                for rolec in color_roles:
                                    await log_message("Color role: " + rolec)
                                    for role in message.author.roles:
                                        # await log_message("Role name: " + str(role.name))
                                        if rolec.strip() == role.name:
                                            color = random.choice(color_roles)
                                            await log_message("Your color is " + color)

                                            await message.author.remove_roles(get(message.guild.roles, name=rolec.strip()))
                                            await message.author.add_roles(get(message.guild.roles, name=color.strip()))
                                            return           
                        except:
                            pass
                    elif (reaction_type == 'Reply') and message_count_dict[message.guild.id][username] >= frequency:
                        message_count_dict[message.guild.id][username] = 0
                        await send_message(message, emoji_string)
                    else:
                        pass                
                if reaction_type == 'Reply' and message_count_dict[message.guild.id][username] >= frequency:
                
                    message_count_dict[message.guild.id][username] = 0
                    await send_message(message, emoji_string)
                else:
                    pass
          
            
client.run('REDACTED') 

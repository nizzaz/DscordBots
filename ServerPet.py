import discord
import re
import mysql.connector
from mysql.connector import Error
import subprocess
import time
import requests
import random
from discord.utils import get
import discord.utils
from datetime import datetime
import asyncio
from slashcommands import SlashCommands

class NakedObject(object):
    pass
intents = discord.Intents.default()
client = discord.Client(heartbeat_timeout=600,intents=intents)
manager = None


async def post_webhook(channel, name, response, picture,embeds):
    try:
        temp_webhook = await channel.create_webhook(name='ServerPet')
        sent_message = await temp_webhook.send(content=response, username=name, avatar_url=picture, wait=True, embeds=embeds)
        await temp_webhook.delete()
    except:
        return None
    return sent_message
    
    
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='ServerPet', user='REDACTED', password='REDACTED')    
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        connection.commit()
        return True
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return False
    finally:
        if(connection.is_connected()):
            cursor.close()
            connection.close()
            
                
async def select_sql(sql_query, params = None):
    await log_message("Select SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='ServerPet', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
        await log_message("Returned " + str(records))
        return records
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return None
    finally:
        if(connection.is_connected()):
            cursor.close()
            connection.close()

async def execute_sql(sql_query):
    try:
        connection = mysql.connector.connect(host='localhost', database='ServerPet', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query)
        return True
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return False
    finally:
        if(connection.is_connected()):
            cursor.close()
            connection.close()
            
            
async def send_message(message, response):
    await log_message("Message sent back to server " + message.guild.name + " channel " + message.channel.name + " in response to user " + message.author.name + "\n\n" + response)
    message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
    for chunk in message_chunks:
        await message.channel.send(">>> " + chunk)
        time.sleep(1)
		
@client.event
async def on_ready():
    global manager
    global slash_commands
    
        
    commands = [{"name": 'sayhi', 'desc': 'Say hello.', 'options': [{}]},
    {"name": 'info', 'desc': 'Bot help.', 'options': [{}]},
    {"name": 'help', 'desc': 'Bot help.', 'options': [{}]},
    {"name": 'mynameis', 'desc': 'Name the pet.', 'options': [{'name': 'name', 'desc': 'Pet\'s name.'}]},
    {"name": 'mygenderis', 'desc': 'Gender of pet.', 'options': [{'name': 'gender', 'desc': 'Pet\'s gender.'}]},
    {"name": 'myspeciesis', 'desc': 'Species of the pet.', 'options': [{'name': 'species', 'desc': 'Pet\'s species.'}]},
    {"name": 'myprofile', 'desc': 'Show pet profile.', 'options': [{}]},
    {"name": 'deletepet', 'desc': 'Delete the pet.', 'options': [{}]},
    {"name": 'checkonme', 'desc': 'Check the pet\'s status.', 'options': [{}]},
    {"name": 'feedme', 'desc': 'Feed the pet.', 'options': [{}]},
    {"name": 'loveme', 'desc': 'Give the pet attention.', 'options': [{}]},
    {"name": 'putmetobed', 'desc': 'Let the pet sleep.', 'options': [{}]},
    {"name": 'allowrunaway', 'desc': 'Toggle if the pet runs away if neglected too long.', 'options': [{}]},
    {"name": 'inviteme', 'desc': 'Invite the pet.', 'options': [{}]}
    ]
    slash_commands = SlashCommands(client)
    # for command in commands:
        # slash_commands.new_slash_command(name=command["name"].lower(), description=command["desc"])
        # for option in command["options"]:
            # try:
                # option["name"]
            # except:
                # continue
            # print(str(option))
            # slash_commands.add_command_option(command_name=command["name"].lower(), option_name=option["name"].lower(), description=option["desc"], required=True)
        # slash_commands.add_global_slash_command(command_name=command["name"].lower())
    await log_message("Logged into Discord!")

@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name)
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)
    
@client.event
async def on_message(message):
    invite_url = "https://discord.com/api/oauth2/authorize?client_id=801954015663226940&permissions=2684471296&scope=bot%20applications.commands"
    if message.author == client.user:
        return
    if message.author.bot and message.author.id != 787355055333965844:
        return
        
    if message.content.startswith(':3'):


        command_string = message.content.split(' ')
        command = command_string[1].replace(':3 ','')
        parsed_string = message.content.replace(":3 " + command + " ","")
        username = message.author.name
        server_name = message.guild.name

        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        if (command == 'sayhi'):
            await message.channel.send("Hello there!")
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await send_message(message,"Admin command only!")
                return   
            await send_message(message, "Server count: " + str(len(client.guilds)))               
        elif command == 'serverlist':
            await log_message("servercount called by " + message.author.name)
            if (message.author.id != 610335542780887050):
                await send_message(message,"Admin command only!")
                return   
            response = "Server count: " + str(len(client.guilds))
            for x in client.guilds:
                if x.name:
                    response = response + x.name + "\n"
            await send_message(message,response)            
        elif command == 'mynameis':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You need manage server permissions to change my name!")
                return
            records = await select_sql("""SELECT Id FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                result = await commit_sql("""INSERT INTO ServerPets (ServerId, UserId, PetName,PetSleep,PetHunger,PetAttention, PetCreated, PetMood,PostsAtZero,AllowRunAway) VALUES (%s, %s, %s,'100','100','100', %s, 'Happy','0','0');""",(str(message.guild.id),str(message.author.id),str(parsed_string),str(datetime.now())))
            else:
                result = await commit_sql("""UPDATE ServerPets SET PetName=%s WHERE ServerId=%s;""",(str(parsed_string),str(message.guild.id)))
            await send_message(message, "My name is now " + parsed_string + "!")
        elif command == 'mygenderis':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You need manage server permissions to change my gender!")
                return        
            records = await select_sql("""SELECT Id FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You need to name me first!")
                return
            else:
                result = await commit_sql("""UPDATE ServerPets SET PetGender=%s WHERE ServerId=%s;""",(str(parsed_string),str(message.guild.id)))
            await send_message(message, "My gender is now " + parsed_string + "!")
        elif command == 'myspeciesis':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You need manage server permissions to change my species!")
                return        
            records = await select_sql("""SELECT Id FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You need to name me first!")
                return
            else:
                result = await commit_sql("""UPDATE ServerPets SET PetSpecies=%s WHERE ServerId=%s;""",(str(parsed_string),str(message.guild.id)))
            await send_message(message, "My species is now " + parsed_string + "!") 
        elif command == 'mypictureis':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You need manage server permissions to change my picture!")
                return        
            records = await select_sql("""SELECT Id FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You need to name me first!")
                return
            else:
                if message.attachments:
                    picture_link = message.attachments[0].url
                else:
                    picture_link = parsed_string
                result = await commit_sql("""UPDATE ServerPets SET PetPicture=%s WHERE ServerId=%s;""",(str(picture_link),str(message.guild.id)))
            await send_message(message, "You've set my picture!")
        elif command == 'myprofile':
            records = await select_sql("""SELECT PetName,IFNULL(PetGender,'Unknown'),IFNULL(PetSpecies,'Unknown'),PetCreated,PetPicture FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You don't have a pet yet!")
                return
            embed = discord.Embed(title=message.guild.name + "'s Pet Profile")
            for row in records:
                embed.add_field(name="Name:",value =row[0])
                embed.add_field(name="Gender:",value=row[1])
                embed.add_field(name="Species:",value=row[2])
                embed.add_field(name="Adopted on:",value=str(row[3]))
                if row[4] is not None:
                    embed.set_thumbnail(url=row[4])
                    
            await message.channel.send(embed=embed)
        elif command == 'deletepet':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You need manage server permissions to give me up!")
                return        
            result = await commit_sql("""DELETE FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            await send_message(message, "Sorry to see you go! I'll miss you!")
        elif command == 'checkonme':
            records = await select_sql("""SELECT PetSleep, PetHunger, PetAttention, PetMood, PetName, PetPicture FROM ServerPets WHERE Serverid=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You don't have a pet yet!")
                return
            for row in records:
                pet_sleep = int(row[0])
                pet_hunger = int(row[1])
                pet_attention = int(row[2])
                pet_mood = row[3]
                pet_name = row[4]
                if row[5] is not None:
                    picture_link = row[5]
                else:
                    picture_link = ""
            
            response = pet_name
            if pet_sleep < 40:
                response = response + random.choice([" would like to sleep,"," would like to rest"," would like to lie down,"," would like a nap,"])
            if pet_hunger < 50:
                response = response + random.choice([" is hungry,"," feels hungry,"," hears their stomach growling,"])
            if pet_attention < 40:
                response = response + random.choice([" would like some attention,"," would like some care,"," would like to have some fun,"])
            if pet_attention < 40:
                pet_mood = random.choice(["lonely","sad","depressed","scared"])
            elif pet_sleep < 40:
                pet_mood = random.choice(["tired","exhausted","weary"])
            elif pet_hunger < 50:
                pet_moood = random.choice(["hungry","famished","starving"])
            else:
                pet_mood = random.choice(["happy","joyous","excited","loving","affectionate"])
            response = response + " feels " + pet_mood + "!"
            embed = discord.Embed(title= pet_name + "'s status",description=response)
            if picture_link.startswith('http'):
                embeds = []
                embeds.append(embed)
                await post_webhook(message.channel, pet_name, "", picture_link,embeds)
            else:
                await message.channel.send(embed=embed)
        elif command == 'feedme':
            food = random.randint(1,30)
            records = await select_sql("""SELECT PetName,PetHunger,PetPicture FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You don't have a pet yet!")
                return
            for row in records:
                pet_name = row[0]
                pet_hunger = int(row[1])
                if row[2] is not None:
                    picture_link = row[2]
                else:
                    picture_link = ""
            if pet_hunger > 95:
                response = pet_name + " is already full and won't eat anymore!"
                embed = discord.Embed(title=response)
                if picture_link.startswith('http'):
                    embeds = []
                    embeds.append(embed)
                    await post_webhook(message.channel, pet_name, "", picture_link,embeds)
                else:
                    await message.channel.send(embed=embed)                
                    return                
                return
            response = ""
            if food < 10:
                response = response + pet_name + " only ate a little bit. "
            elif food >= 10 and food < 20:
                response = response + pet_name + " ate a decent meal. "
            else:
                response = response + pet_name + " ate a lot of food! "
            pet_hunger = pet_hunger + food
            if pet_hunger < 40:
                response = response + "I'm still starving!"
            elif pet_hunger >= 41 and pet_hunger <= 70:
                response = response + "I could eat some more!"
            else:
                response = response + "Thanks, I'm full!"
              
            result = await commit_sql("""UPDATE ServerPets SET PetHunger=%s WHERE ServerId=%s;""",(str(pet_hunger),str(message.guild.id)))
            embed = discord.Embed(title=response)
            if picture_link.startswith('http'):
                embeds = []
                embeds.append(embed)
                await post_webhook(message.channel, pet_name, "", picture_link,embeds)
            else:
                await message.channel.send(embed=embed)
        elif command == 'loveme':
            love = random.randint(1,15)
            records = await select_sql("""SELECT PetName,PetAttention,PetPicture FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You don't have a pet yet!")
                return
            for row in records:
                pet_name = row[0]
                pet_attention = int(row[1])
                if row[2] is not None:
                    picture_link = row[2]
                else:
                    picture_link = ""
            if pet_attention > 95:
                response = pet_name + " has enough love and beams at you!"
                embed = discord.Embed(title=response)
                if picture_link.startswith('http'):
                    embeds = []
                    embeds.append(embed)
                    await post_webhook(message.channel, pet_name, "", picture_link,embeds)
                else:
                    await message.channel.send(embed=embed)                
                    return
            response = ""
            if love < 5:
                response = response + pet_name + random.choice([" appreciates the love. ", " thanks you for the petting. ", " rolls around contentedly. "])
            elif love >= 5 and love < 10:
                response = response + pet_name + random.choice([" enjoys playing catch with you. ", " rolls the tennis ball back towards you. ", " jumps around happily. "])
            else:
                response = response + pet_name + random.choice([" snuggles up next to you. ", "curls up beside you. ", " falls asleep next to you. ", " brings you an odd knicknack they found. ", " blinks contentedly. "])
            pet_attention = pet_attention + love
            if pet_attention < 40:
                response = response + random.choice(["I still feel rather lonely...", "I still feel pretty sad...", "I still would like to play if you do?"])
            elif pet_attention >= 41 and pet_attention <= 70:
                response = response + "I am rather content."
            else:
                response = response + random.choice(["I'm good, that's enough attention for today :)", "Thank you for the care!", "That's enough playing for today, thanks!"])
            result = await commit_sql("""UPDATE ServerPets SET PetAttention=%s WHERE ServerId=%s;""",(str(pet_attention),str(message.guild.id)))
            embed = discord.Embed(title=response)
            if picture_link.startswith('http'):
                embeds = []
                embeds.append(embed)
                await post_webhook(message.channel, pet_name, "", picture_link,embeds)
            else:
                await message.channel.send(embed=embed)
        elif command == 'mychannel':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You need manage server permissions to give me up!")
                return        
            records = await select_sql("""SELECT PetName,PetHunger,PetPicture FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You don't have a pet yet!")
                return
            if not message.channel_mentions:
                await send_message(message, "You did not give me a channel to post in!")
                return
            result = await commit_sql("""UPDATE ServerPets SET PetChannelId=%s WHERE ServerId=%s;""",(str(message.channel_mentions[0].id),str(message.guild.id)))
            await send_message(message, "My channel is now <#" + str(message.channel_mentions[0].id) + ">!")
        elif command == 'putmetobed':
            new_sleep = random.randint(1,70)
            records = await select_sql("""SELECT PetName,PetSleep,PetPicture FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You don't have a pet yet!")
                return
            for row in records:
                pet_name = row[0]
                pet_sleep = int(row[1])
                if row[2] is not None:
                    picture_link = row[2]
                else:
                    picture_link = ""
            if pet_sleep > 95:
                response = pet_name + random.choice([" is wide awake and raring to go!", " is ready to start the day!", " is rested and ready!"])
                embed = discord.Embed(title=response)
                if picture_link.startswith('http'):
                    embeds = []
                    embeds.append(embed)
                    await post_webhook(message.channel, pet_name, "", picture_link,embeds)
                else:
                    await message.channel.send(embed=embed)                
                    return
            response = ""
            if new_sleep < 20:
                response = response + pet_name + " took a short nap. "
            elif new_sleep >= 20 and new_sleep < 50:
                response = response + pet_name + " slept a while. "
            else:
                response = response + pet_name + " slept the whole day away! "
            pet_sleep = pet_sleep + new_sleep
            if pet_sleep < 40:
                response = response + "I'm still pretty tired..."
            elif pet_sleep >= 41 and pet_sleep <= 70:
                response = response + "I am mostly rested!"
            else:
                response = response + "I am wide awake!"
            result = await commit_sql("""UPDATE ServerPets SET PetSleep=%s WHERE ServerId=%s;""",(str(pet_sleep),str(message.guild.id)))
            embed = discord.Embed(title=response)
            if picture_link.startswith('http'):
                embeds = []
                embeds.append(embed)
                await post_webhook(message.channel, pet_name, "", picture_link,embeds)
            else:
                await message.channel.send(embed=embed)
        elif (command == 'info' or command == 'help'):
            await send_message(message, "My Server Pet Commands:\n\n`/mynameis NAME`: Set my name. When you set my name, that's my adoption date! You have to do this first!\n`/mygenderis GENDER`: Set my gender. It's up to you!\n`/myspeciesis SPECIES`: Set my species! It's up to you!\n`/mypictureis LINK`: Set my profile picture to either a link or a direct Discord upload!\n`/mychannel #CHANNEL_MENTION`: Set a channel for me to post in.\n`/myprofile`: See my name, adoption date, gender and species!\n`/checkonme`: Check my mood and if I'm hungry, sleepy or need love!\n`/feedme:` Give me some food!\n`/putmetobed`: Make me go to bed and rest!\n`/loveme`: Give me lots of snuggles!\n`/deletepet`: If you want another pet, run this. I'll miss you!\n`/allowrunaway`: Toggle whether the pet will run away if neglected for too long.\n`/inviteme`: Invite me to your server!")
        elif command == 'allowrunaway':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You need manage server permissions to change my picture!")
                return
            records = await select_sql("""SELECT IFNULL(AllowRunaway,0) FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You don't have a server pet yet!")
                return
            for row in records:
                allow_runaway = int(row[0])
            if allow_runaway == 0:
                await commit_sql("""UPDATE ServerPets SET AllowRunaway=1 WHERE ServerId=%s;""",(str(message.guild.id),))
                await send_message(message, "Runaway enabled.")
            else:
                await commit_sql("""UPDATE ServerPets SET AllowRunaway=0 WHERE ServerId=%s;""",(str(message.guild.id),))
                await send_message(message, "Runaway disabled.")                
        elif command == 'inviteme':
            await send_message(message, "Click here to invite me! I'm excited! https://discord.com/api/oauth2/authorize?client_id=801954015663226940&permissions=2684471296&scope=bot%20applications.commands")
    else:
        records = await select_sql("""SELECT PetSleep, PetHunger, PetAttention, PostsAtZero,PetPicture,IFNULL(AllowRunAway,0),PetName FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
        if not records:
            return
        for row in records:
            pet_sleep = int(row[0])
            pet_hunger = int(row[1])
            pet_attention = int(row[2])
            posts_at_zero = int(row[3])
            if row[4] is not None:
                picture_link = row[4]
            else:
                picture_link = ""
            allow_runaway = int(row[5])
            pet_name = row[6]
        mood = ""    
        count_drop = random.randint(1,3)
        if count_drop == 1:
            pet_sleep = pet_sleep - random.randint(1,5)
        elif count_drop == 2:
            pet_hunger = pet_hunger - random.randint(1,10)
        elif count_drop == 3:
            pet_attention = pet_attention - random.randint(1,10)
        if pet_attention < 50:
            mood = random.choice(["needy","lonely","sad","depressed","scared"])
        elif pet_sleep < 30:
            mood = random.choice(["tired","annoyed","exhausted","weary"])
        elif pet_hunger < 50:
            moood = random.choice(["hungry","famished","starving"])
        else:
            mood = random.choice(["happy","joyous","excited","loving","affectionate"])
        if pet_sleep < 0:
            pet_sleep = 0
        if pet_hunger < 0:
            pet_hunger = 0
        if pet_attention < 0:
            pet_attention = 0
        if pet_sleep == 0 and pet_hunger == 0 and pet_attention == 0:
            posts_at_zero = posts_at_zero + 1
        else:
            posts_at_zero = 0
        if posts_at_zero == 50:
            posts_at_zero = posts_at_zero + 1
            response = "I am feeling neglected. Please give me some food, love and sleep!"
            embed = discord.Embed(title=response)
            records = await select_sql("""SELECT PetChannelId FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                pet_channel = message.channel
            else:
                for row in records:
                    if row[0] is None:
                            break
                    channel_id = int(row[0])
                try:
                    pet_channel = discord.utils.get(message.guild.channels, id=channel_id)
                except:
                    return
            if picture_link.startswith('http'):
                embeds = []
                embeds.append(embed)
                await post_webhook(pet_channel, pet_name, "", picture_link,embeds)
            else:
                await pet_channel.send(embed=embed)
        if posts_at_zero == 100 and allow_runaway == 1:
            records = await select_sql("""SELECT PetChannelId FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                pet_channel = message.channel
            else:
                for row in records:
                    if row[0] is None:
                        break
                    channel_id = int(row[0])
                try:
                    pet_channel = discord.utils.get(message.guild.channels, id=channel_id)        
                except:
                    pass
            if picture_link.startswith('http'):
                
                response = "I have run away to find a better home. Please treat your next pet better!"
                embed = discord.Embed(title=response)
                embeds = []
                embeds.append(embed)
                await post_webhook(pet_channel, pet_name, "", picture_link,embeds)
            else:
                await pet_channel.send(embed=embed)
            result = await commit_sql("""DELETE FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
        elif posts_at_zero == 100 and allow_runaway ==0:
            records = await select_sql("""SELECT PetChannelId FROM ServerPets WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                pet_channel = message.channel
            else:
                for row in records:
                    channel_id = int(row[0])
                try:
                    pet_channel = discord.utils.get(message.guild.channels, id=channel_id)        
                except:
                    pass
            posts_at_zero = posts_at_zero + 1
            if picture_link.startswith('http'):
                response = "I really, really need some attention, love and sleep! Please help me!"
                embed = discord.Embed(title=response)
                embeds = []
                embeds.append(embed)
                await post_webhook(pet_channel, pet_name, "", picture_link,embeds)
            else:
                try:
                    await pet_channel.send(embed=embed)            
                except:
                    pass
        await commit_sql("""UPDATE ServerPets SET PetSleep=%s,PetHunger=%s,PetAttention=%s,PetMood=%s,PostsAtZero=%s WHERE ServerId=%s;""",(str(pet_sleep),str(pet_hunger),str(pet_attention),str(mood),str(posts_at_zero),str(message.guild.id)))
        
        
        
@client.event
async def on_interaction(member, interaction):
    global command_handler
    global slash_commands
    print("called here" + str(interaction))
    slash_commands.convert_to_message(interaction, member, ":3 ") 
    
client.run'REDACTED'

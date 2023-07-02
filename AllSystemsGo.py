import discord
import re
import mysql.connector
from mysql.connector import Error
import urllib.request
import subprocess
import time
import requests
import random
from discord.utils import get
import discord.utils
from datetime import datetime
from discord import Webhook, File
import csv
import asyncio
import pyttsx3
import sox

webhook = { }
dm_tracker = { }
intents = discord.Intents(messages=True,guilds=True, message_content=True)
client = discord.Client(heartbeat_timeout=600,intents=intents)
guild_settings = { }
identity_aliases = { }


async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='AllSystemsGo', user='jwoleben', password='nerdvana4097', charset="utf8mb4")    
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
        connection = mysql.connector.connect(host='localhost', database='AllSystemsGo', user='jwoleben', password='nerdvana4097', charset="utf8mb4")
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
        connection = mysql.connector.connect(host='localhost', database='AllSystemsGo', user='jwoleben', password='nerdvana4097', charset="utf8mb4")
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
            
async def direct_message(message, response):
    channel = await message.author.create_dm()
    await log_message("replied to user " + message.author.name + " in DM with " + response)
    try:
        message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
        for chunk in message_chunks:
            await channel.send(">>> " + chunk)
            time.sleep(1)
    except discord.errors.Forbidden:
        await dm_tracker[message.author.id]["commandchannel"].send(">>> You have DMs off. Please reply with //answer <reply> in the server channel.\n" + response)
    
async def reply_message(message, response):
    if not message.guild:
        channel_name = dm_tracker[message.author.id]["commandchannel"].name
        server_name = str(dm_tracker[message.author.id]["server_id"])
    else:
        channel_name = message.channel.name
        server_name = message.guild.name
        
    await log_message("Message sent back to server " + server_name + " channel " + channel_name + " in response to user " + message.author.name + "\n\n" + response)
    
    message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
    for chunk in message_chunks:
        await message.channel.send(">>> " + chunk)
        time.sleep(1)

async def admin_check(userid):
    if (userid != 610335542780887050):
        await log_message(str(userid) + " tried to call an admin message!")
        return False
    else:
        return True

async def initialize_dm(author_id):
    global dm_tracker
    try:
        del dm_tracker[author_id]
    except:
        pass
    dm_tracker[author_id] = { }
    dm_tracker[author_id]["currentcommand"] = " "
    dm_tracker[author_id]["currentfield"] = 0
    dm_tracker[author_id]["fieldlist"] = []
    dm_tracker[author_id]["fielddict"] = []
    dm_tracker[author_id]["server_id"] = 0
    dm_tracker[author_id]["commandchannel"] = 0
    dm_tracker[author_id]["parameters"] = " "
    
    
def role_check(role_required, user):
    for role in user.roles:
        if role.id == role_required:
            return True
            
    return False
async def insert_into(message, table_name):
    global dm_tracker
    field_list = dm_tracker[message.author.id]["fieldlist"]
    field_dict = dm_tracker[message.author.id]["fielddict"]
    server_id = dm_tracker[message.author.id]["server_id"]
    create_entry = "INSERT INTO " + table_name + " (ServerId, UserId, "
    create_values = ") VALUES (%s, %s, "
    create_tuple = (str(dm_tracker[message.author.id]["server_id"]), str(message.author.id))
    counter = 0
    for field in field_list:
        create_entry = create_entry + field + ", "
        create_tuple = create_tuple + (field_dict[counter],)
        create_values = create_values + "%s, "
        counter = counter + 1
        if counter > len(field_list) - 1:
            break

    create_entry = re.sub(r", $","", create_entry)
    create_entry = create_entry + " " + re.sub(r",\s*$","",create_values) + ");"
    result = await commit_sql(create_entry, create_tuple)
    return result

async def update_table(message, table_name):
    global dm_tracker
    field_list = dm_tracker[message.author.id]["fieldlist"]
    field_dict = dm_tracker[message.author.id]["fielddict"]
    server_id = dm_tracker[message.author.id]["server_id"]    
    update_entry = "UPDATE " + table_name + " SET UserId=%s, "
    try: dm_tracker[message.author.id]["parameters2"]
    except: dm_tracker[message.author.id]["parameters2"] = None
    if not dm_tracker[message.author.id]["parameters2"]:
        
        update_tuple = (str(message.author.id),)
    else:
        update_tuple = (str(dm_tracker[message.author.id]["parameters2"]),)
        
    counter = 0
    for field in field_list:
        update_entry = update_entry + field + "=%s, "
        update_tuple = update_tuple + (str(field_dict[counter]),)
        counter = counter + 1 
    if dm_tracker[message.author.id]["parameters"] is None:
        field_value = field_dict[0]
    else:
        field_value = dm_tracker[message.author.id]["parameters"]
        
    update_entry = re.sub(r", $","", update_entry)
    if dm_tracker[message.author.id]["currentcommand"] == "editcustomchar":
        update_entry = update_entry + " WHERE " + field_list[0] + "=%s;"
        update_tuple = update_tuple + (field_value,)
    else:    
        update_entry = update_entry + " WHERE ServerId=%s AND " + field_list[0] + "=%s;"
    
        update_tuple = update_tuple + (str(dm_tracker[message.author.id]["server_id"]), field_value)

    result = await commit_sql(update_entry, update_tuple)
    return result
async def make_menu(message, table1, table2, id_field1, id_field2, name_field,id ):
    global dm_tracker
    records = await select_sql("""SELECT """ + id_field1 + """ FROM """ + table1 + """ WHERE ServerId=%s AND """ + id_field2 + """=%s;""",  (str(dm_tracker[message.author.id]["server_id"]), id))
    if not records:
        return "Menu error!"
    response = " "
    for row in records:
        item_record = await select_sql("SELECT " + name_field + " FROM " + table2 + " WHERE Id=%s AND ServerId=%s;", (str(row[0]),str(dm_tracker[message.author.id]["server_id"])))
        for item_row in item_record:
            response = response + "**" + str(row[0]) + "** - " + item_row[0] + "\n"
    return response

async def make_simple_menu(message, table1, name_field):
    global dm_tracker
    records = await select_sql("""SELECT Id,""" + name_field + """ FROM """ + table1 + """ WHERE ServerId=%s;""",  (str(dm_tracker[message.author.id]["server_id"]),))
    if not records:
        return "Menu error!"
    response = " "
    for row in records:
        response = response + "**" + str(row[0]) + "** - " + row[1] + "\n"
    return response
    
async def make_less_simple_menu(message, table1, name_field, id_field, id):
    global dm_tracker
    records = await select_sql("""SELECT Id,""" + name_field + """ FROM """ + table1 + """ WHERE ServerId=%s AND """ + id_field + """=%s;""",  (str(dm_tracker[message.author.id]["server_id"]),id))
    if not records:
        return "Menu error!"
    response = " "
    for row in records:
        response = response + "**" + str(row[0]) + "** - " + row[1] + "\n"
    return response  

async def post_webhook(channel, name, response, picture):
    temp_webhook = await channel.create_webhook(name='System')
    sent_message = await temp_webhook.send(content=response, username=name, avatar_url=picture, wait=True)
    await temp_webhook.delete() 
    return sent_message
    
@client.event
async def on_ready():
    global webhook
    global guild_settings
    global identity_aliases
    global dm_tracker
    
    await log_message("Logged in!")
    
    for guild in client.guilds:
        guild_settings[guild.id]  =  {}

        try: identity_aliases[guild.id]
        except: identity_aliases[guild.id] = {}
        for user in guild.members:
            try: identity_aliases[guiild.id][user.id]
            except: identity_aliases[guild.id][user.id] = ""

    # GMRole,SystemRole,SystemRole,GuildBankBalance,StartingHealth,StartingMana,StartingStamina,StartingAttack,StartingDefense,StartingMagicAttack,StartingAgility,StartingIntellect,StartingCharisma,HealthLevelRatio,ManaLevelRatio,StaminaLevelRatio,XPLevelRatio,HealthAutoHeal,ManaAutoHeal,StaminaAutoHeal
    # ALTER TABLE GuildSettings ADD COLUMN StartingHealth Int, StartingMana Int, StartingStamina Int, StartingAttack Int, StartingDefense Int, StartingMagicAttack Int, StartingAgility Int, StartingIntellect Int, StartingCharisma Int, HealthLevelRatio Int, ManaLevelRatio Int, StaminaLevelRatio Int, XPLevelRatio Int, HealthAutoHeal DECIMAL(1,2), ManaAutoHeal DECIMAL (1,2), StaminaAutoHeal DECIMAL(1,2);
    records = await select_sql("""SELECT ServerId,IFNULL(AdminRole,'0'),IFNULL(SystemRole,'0') FROM GuildSettings;""")
    if records:
        for row in records:
            server_id = int(row[0])
            guild_settings[server_id] = {} 
            if row[1] is not None:        
                guild_settings[server_id]["AdminRole"] = int(row[1])    
            if row[2] is not None:   
                guild_settings[server_id]["SystemRole"] = int(row[2])
    await log_message("All SQL loaded for guilds.")
            
            
@client.event
async def on_guild_join(guild):
    global guild_settings
    global identity_aliases

    
    await log_message("Joined guild " + guild.name)
    guild_settings[guild.id] = {}
    identity_aliases[guild.id] = { }

    for user in guild.members:
        identity_aliases[guild.id][user.id] = { }
        for channel in guild.text_channels:
                identity_aliases[guild.id][user.id][channel.id] = ""
    
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)
    
@client.event
async def on_message(message):
    global webhook
    global guild_settings
    global identity_aliases
    global dm_tracker
    
    if message.author.bot:
        return
    if message.author == client.user:
        return
    try:
        identity_aliases[message.guild.id]
    except: 
        try: 
            message.guild.id
            identity_aliases[message.guild.id] = {} 
        except: pass
        
    try:
        identity_aliases[message.guild.id][message.author.id]
    
    except: 
        try: 
            message.guild.id
            identity_aliases[message.guild.id][message.author.id] = ""
        
        except:
            pass

         

    
    das_server = message.guild
    if message.content.startswith('%answer'):
        das_server = None
        message.content = message.content.replace('%answer ','')
 
       
    if not das_server:
        await log_message("Received DM from user " + message.author.name + " with content " + message.content)

        current_command = dm_tracker[message.author.id]["currentcommand"]
        current_field = dm_tracker[message.author.id]["currentfield"]
        field_list = dm_tracker[message.author.id]["fieldlist"]
        field_dict = dm_tracker[message.author.id]["fielddict"]
        server_id = dm_tracker[message.author.id]["server_id"]
        await log_message("Command : " + current_command + " Field: " + str(current_field) + " Field list: " +str(field_list) + " Field dict: " + str(field_dict))
            
        if message.content == 'stop' or message.content == 'Stop':
            try:
                dm_tracker[message.author.id]
                del dm_tracker[message.author.id]
            except:
                pass
            await direct_message(message, "Command stopped!")
            return
        elif current_field < len(field_list):
            if message.attachments:
                dm_tracker[message.author.id]["fielddict"].append(message.attachments[0].url)   
            else:
                dm_tracker[message.author.id]["fielddict"].append(message.content.strip())
            dm_tracker[message.author.id]["currentfield"] = current_field + 1
            if current_field < len(field_list) - 1:
                await direct_message(message, "Setting field **"  + dm_tracker[message.author.id]["fieldlist"][current_field] + "** to **" + message.content.strip() + "**. The next field is **" + dm_tracker[message.author.id]["fieldlist"][current_field + 1] + "**. Reply with the new value.")
            else:
                await direct_message(message, "Setting field **"  + dm_tracker[message.author.id]["fieldlist"][current_field] + "** to **" + message.content.strip() + "**. That was the last field. Reply *end* to commit to the database.")            
            
            return

        elif current_command == 'resetserver':
            if message.content != 'CONFIRM':
                await direct_message(message, "Server reset canceled.")
                await dm_tracker[message.author.id]["commandchannel"].send(">>> Server reset canceled.")
                return
            else:
                await dm_tracker[message.author.id]["commandchannel"].send(">>> Server reset commencing...")
                delete_tuple = ()
                for x in range(1,2):
                    delete_tuple = delete_tuple + (str(dm_tracker[message.author.id]["server_id"]),)
                result = await commit_sql("""DELETE FROM GuildSettings WHERE ServerId=%s; DELETE FROM Identities WHERE ServerId=%s;""", delete_tuple)
                await dm_tracker[message.author.id]["commandchannel"].send(">>> Server reset complete! Please run //setadminrole @adminrole.")
                return




        elif current_command == 'newid':
            if message.attachments:
                field_dict.append(message.attachments[0].url)

            result = await insert_into(message, "Identities")
            if result:
                await direct_message(message, "Identity " + field_dict[0] + " successfully created.")
                await dm_tracker[message.author.id]["commandchannel"].send(">>> Identity " + field_dict[0] + " successfully created.")
            else:
                await direct_message(message, "Database error!")
           


        return
        
    elif identity_aliases[message.guild.id][message.author.id] and not message.content.startswith('%'):
            get_npc = """SELECT UserId, IDName, PictureLink FROM Identities WHERE ServerId=%s AND UserId=%s AND Shortcut=%s;"""
            npc_tuple = (str(message.guild.id), str(message.author.id), identity_aliases[message.guild.id][message.author.id])
            records = await select_sql(get_npc, npc_tuple)
            for row in records:
                if str(message.author.id) != row[0]:
                    await reply_message(message, "<@" + str(message.author.id) + "> is not allowed to use identity " + row[1] + "!")
                    return
                response = message.content
                # current_pfp = await client.user.avatar_url.read()
                

                # current_name = message.guild.me.name
                URL = row[2]
                webhook_list = await message.channel.webhooks()
                webhook_found = False
                for hook in webhook_list:
                    if hook.name == 'System':
                        webhook_found = True
                        temp_webhook = hook
                if not webhook_found:
                    temp_webhook = await message.channel.create_webhook(name='System')
                if URL.startswith('http'):
                    await temp_webhook.send(content=response, username=row[1], avatar_url=URL)
                else:
                    await temp_webhook.send(content=response, username=row[1])
                await message.delete()
                await temp_webhook.delete()

    if message.content.startswith('%'):

            
        command_string = message.content.split(' ')
        command = command_string[0].replace('%','')
        parsed_string = message.content.replace("%" + command + " ","")

        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string)
        
        
        if command == 'createroles':
            roles=["BotAdmin","System"]
            
            for role in roles:
                try:
                    new_role = await message.guild.create_role(name=role)
                    if role == "BotAdmin":
                        result = await commit_sql("""UPDATE GuildSettings SET AdminRole=%s WHERE ServerId=%s;""",(str(new_role.id),str(message.guild.id)))
                        guild_settings[message.guild.id]["AdminRole"] = new_role.id
                    if role == "System":
                        result = await commit_sql("""UPDATE GuildSettings SET SystemRole=%s WHERE ServerId=%s;""",(str(new_role.id),str(message.guild.id)))
                        guild_settings[message.guild.id]["SystemRole"] = new_role.id                    
                except discord.errors.Forbidden:
                    await reply_message(message, "Cannot create roles due to permissions!")
                    return
                    
            await reply_message(message, "Roles created!")        
        elif command == 'setadminrole':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "Only a user with manage server permissions can set the admin role!")
                return
            if len(message.role_mentions) > 1:
                await reply_message(message, "Only one role can be defined as the admin role!")
                return
            role_id = message.role_mentions[0].id
            guild_settings[message.guild.id]["AdminRole"] = role_id
            result = await commit_sql("""INSERT INTO GuildSettings (ServerId,AdminRole) Values (%s,%s);""",  (str(message.guild.id), str(role_id)))
            if result:
                await reply_message(message, "Admin role successfully set!")
            else:
                await reply_message(message, "Database error!")
        elif command == 'help' or command == 'info':
            fields = " "
            if not parsed_string:
            
                response = "`Welcome to All Systems Go, the Discord Bot f0r systems.`\n\n*Using Help:*\n\nType %info or %help followed by one of these categories, such as `%info general`:\n\n`general`: Not commands, but information on how the bot works.\n`setup`: Commands for getting the bot running.\n`system`: Commands for managing system users.\n`voice`: Commands for using voices in VC.\n"
            elif parsed_string == 'setup':
                response = "**SETUP COMMANDS**\n\n`%setadminrole @Role`: *Owner* Set the admin role. This must be done before any other setup. This can only be done by a server manager. See general for role descriptions.\n`%setsystemrole @Role` *Admin* Set the system user role.\n`%listroles` *None* List the server roles`\n%addsystemuser @user1 @user2` Add users to the system role.\n`%deleteadmin @user1 @user2` Delete users from the admin role. Only a server manager can do this.\n`%deletesystemuser @user1 @user2` Delete users from the system role.\n`%resetserver` Wipe all data from the bot for this server. Only the server owner may perform this action.\n`%invite` Get an invite link for the bot.\n"

            elif parsed_string == 'system':
                response = "**SYSTEM COMMANDS**\n\n`%setid SHORTCUT`: Set an identity for all posts in the current server.\n`%unsetid`: Unset the ID for this server.\n`%newid`: Create a new identity.\n`%say SHORTCUT TEXT`  Post as an identity that belongs to you.`\n%deleteid ID_NAME` Delete an identity (yours if a system user, any if administrator).\n`%listids`: List all identities on this server.\n"

            elif parsed_string == 'general':
                response = "**GENERAL INFO**\n\nThis bot supports systems that need to post as alternate identities. Some commands will initiate a DM system for creating or editing an identity, others will post as the identity. If the user has DMs disabled, the bot will reply in the same channel as the user's command.\n\n**ROLES**\n\nThere are two roles required to use the bot.\n`Admin:` The admin can run all commands of the bot, such as adding and deleting spells or items. The server owner must set the admin role.\n`System User:` The system user is able to create, edit and delete identities, or post as the identity.\n"

            elif parsed_string == 'voice':
                response = "**VOICE COMMANDS**\n\n`%speak TEXT`: Speak the typed text into a connected VC. You must be connected for the bot to speak."
            else:
            
                response = "`Welcome to All Systems Go, the Discord Bot for systems.`\n\n*Using Help:*\n\nType %info or %help followed by one of these categories, such as `%info general`:\n\n`general`: Not commands, but information on how the bot works.\n`setup`: Commands for getting the bot running.\n`system`: Commands for managing system users.\n`voice`: Commands for using voices in VC.\n"
            if fields:
                await reply_message(message, response + fields)
            else: 
                await reply_message(message, response)
        elif command == 'initialize':
            if not await admin_check(message.author.id):
                await reply_message(message, "This command is admin only!")
                return
            

            create_npc_table = """CREATE TABLE Identities (Id int auto_increment, ServerId varchar(40), UserId varchar(40), IDName varchar(100), PictureLink varchar(1024), Shortcut varchar(20), PRIMARY KEY (Id));"""
            # "GMRole","SystemRole","SystemRole","GuildBankBalance","StartingHealth","StartingMana","StartingStamina","StartingAttack","StartingDefense","StartingMagicAttack","StartingAgility","StartingIntellect","StartingCharisma","HealthffRatio","ManaLevelRatio","StaminaLevelRatio","XPLevelRatio","HealthAutoHeal","ManaAutoHeal","StaminaAutoHeal"
            create_guild_settings_table = """CREATE TABLE GuildSettings (Id int auto_increment, ServerId VARCHAR(40),  GuildName VarChar(100), AdminRole VARCHAR(40), SystemRole VARCHAR(40), PRIMARY KEY(Id));"""
            

                
            result = await execute_sql(create_npc_table)
            if not result:
                await reply_message(message, "Database error with NPCs!")
                return  
                
 
            result = await execute_sql(create_guild_settings_table)
            if not result:
                await reply_message(message, "Database error with guild settings!")
                return
 
 
            await reply_message(message, "Databases initialized!")

        elif command == 'speak':

            if not parsed_string and not message.attachments:
                await reply_message(message, "No speech included to speak!")
                return
            if message.attachments:
                file_url = message.attachments[0].url
                file_name = message.attachments[0].filename
                await send_message(message, "Downloading file " + file_name + "...")
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_url) as resp:
     #           await send_message(message, "File saved to " + file_name + "!")
                        with open('/home/jwoleben/BotMaster/StarAI/' + file_name, 'wb') as file:
                            bytes = await resp.read()
                            
                            file.write(bytes)
                f = open('/home/jwoleben/BotMaster/' + file_name, 'r')
                parsed_string = f.read()
                            
            async with message.channel.typing():
                engine = pyttsx3.init()
                rate = engine.getProperty('rate') 
                engine.setProperty('rate', rate - 150)
                voices = engine.getProperty('voices')  
                for voice in voices:
                    print("Name: " + str(voice.name) + " Age: " + str(voice.age) + " Gender: " + str(voice.gender))
                engine.setProperty('voice','us-mbrola-1')
                engine.save_to_file(parsed_string, "/home/jwoleben/text-" + str(message.author.id) + ".mp3")
                engine.runAndWait()
                time.sleep(2)
                tfm = sox.Transformer()
                tfm.pitch(-4.5)
                tfm.build(input_filepath="/home/jwoleben/text-" + str(message.author.id) + ".mp3",output_filepath="/home/jwoleben/text-" + str(message.author.id) + "2.mp3")
                
                
                f = open("/home/jwoleben/text-" + str(message.author.id) + "2.mp3",'rb')
                #byt = f.read() # ,"--setf", "int_f0_target_mean=200",

                parsed_string = parsed_string.replace('\n','. ')

                source = discord.FFmpegPCMAudio("/home/jwoleben/text-" + str(message.author.id) + "2.mp3")
                
                if message.author.voice:
                    
                        vc = await message.author.voice.channel.connect()
                        
                        #
                        vc.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
                        while vc.is_playing():
                            await asyncio.sleep(1)
                        await vc.disconnect()                

        elif command == 'deleteall':
            if not await admin_check(message.author.id):
                await reply_message(message, "This command is admin only!")
                return
            drop_all_tables = """DROP TABLE IF EXISTS CharacterProfiles; DROP TABLE IF EXISTS Inventory; DROP TABLE IF EXISTS Equipment; DROP TABLE IF EXISTS Identities; DROP TABLE IF EXISTS Spells; DROP TABLE IF EXISTS Melee; DROP TABLE IF EXISTS MagicSkills; DROP TABLE IF EXISTS MeleeSkills; DROP TABLE IF EXISTS Monsters; DROP TABLE IF Exists CustomProfiles; DROP TABLE IF Exists Vendors; DROP TABLE IF EXISTS Buffs; DROP TABLE IF EXISTS BuffSkills;"""
            result = await execute_sql(drop_all_tables)
            if result:
                await reply_message(message, "All tables dropped.")
            else:
                await reply_message(message, "Database error!")

        elif command == 'listservers':
            if message.author.id != 610335542780887050:
                return
            response = "server list: \n"
            for guild in client.guilds:
                try:
                    response = response + guild.name + "\n"
                except:
                    pass
            response = response + "Server count: " + str(len(client.guilds))
            await reply_message(message, response)

        elif command == 'setid':
            if not role_check(guild_settings[message.guild.id]["SystemRole"], message.author):
                await reply_message(message, "You must be a member of the system user role to use identities!")
                return
            if not parsed_string:
                await reply_message(message, "No identity shortcut specified.")
                return
            records = await select_sql("""SELECT Id FROM Identities WHERE ServerId=%s AND Shortcut=%s;""",(str(message.guild.id),str(parsed_string)))
            if not records:
                await reply_message(message, "That identity hasn't been defined.")
                return

            identity_aliases[message.guild.id][message.author.id] = parsed_string
            await reply_message(message, "User <@" + str(message.author.id) + "> set identity to " + parsed_string + " in channel " + message.channel.name + ".")
        elif command == 'unsetid':
            if not role_check(guild_settings[message.guild.id]["SystemRole"], message.author):
                await reply_message(message, "You must be a member of the system user role to set identities!")
                return
            identity_aliases[message.guild.id][message.author.id] = ""
            await reply_message(message, "User <@" + str(message.author.id) + "> cleared identity in channel " + message.channel.name + ".")            
        elif command == 'newid':
            if not role_check(guild_settings[message.guild.id]["SystemRole"], message.author):
                await reply_message(message, "You must be a member of the system user role to create an identity.")
                return
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'newid'
            dm_tracker[message.author.id]["fieldlist"] = ["IDName","Shortcut","PictureLink"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            dm_tracker[message.author.id]["parameters"] = message.mentions
            
            await reply_message(message, "Please check your DMs for instructions on how to create a new identity, <@" + str(message.author.id) + ">.")
            
            await direct_message(message, "You have requested a new identity! Please type in the response the **name of the identity**, and then enter each field as a reply to the DMs. When you have filled out all fields, the identity will be created!")


        elif command == 'say':
            shortcut = command_string[1]
            parsed_string = message.content.replace("%say " + shortcut + " ","")
            
            if not shortcut:
                await reply_message (message, "No identity specified!")
                return
            get_npc = """SELECT UserId, IDName, PictureLink FROM Identities WHERE ServerId=%s AND Shortcut=%s;"""
            npc_tuple = (str(message.guild.id), shortcut)
            records = await select_sql(get_npc, npc_tuple)
            for row in records:
                if str(message.author.id) != row[0]:
                    await reply_message(message, "<@" + str(message.author.id) + "> is not allowed to use identity " + row[1] + "!")
                    return
                response = parsed_string

                URL = row[2]

                temp_webhook = await message.channel.create_webhook(name='System')
                if URL.startswith('http') and URL:
                    await temp_webhook.send(content=response, username=row[1], avatar_url=URL)
                else:
                    await temp_webhook.send(content=response, username=row[1])
                await message.delete()
                await temp_webhook.delete()
                
        elif command == 'deleteid':
            if not role_check(guild_settings[message.guild.id]["SystemRole"], message.author) and not role_check(guild_settings[message.guild.id]["AdminRole"],message.author):
                await reply_message(message, "You must be a member of the system user role or Bot Admin role to delete identities!")
                return        
            if not parsed_string:
                await reply_message(message, "No identity name specified!")
                return
            records = await select_sql("""SELECT UserId FROM Identities WHERE ServerId=%s AND IDName=%s;""",(str(message.guild.id),parsed_string))
            if not records:
                await reply_message(message, "That identity is not defined.")
                return
            if not role_check(guild_settings[message.guild.id]["AdminRole"],message.author):
                for row in records:
                    if message.author.id != int(row[0]):
                        await reply_message(message, "You are not allowed to delete this identity.")
                        return
            result = await commit_sql("""DELETE FROM Identities WHERE ServerId=%s AND IDName=%s""", (str(message.guild.id),parsed_string))
            if result:
                await reply_message(message, parsed_string + " deleted.")
            else:
                await reply_message(message, "Database error!")
                



                    
 
        elif command == 'setsystemrole':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must be a member of the admin role to set other roles!")
                return        
            if len(message.role_mentions) > 1:
                await reply_message(message, "Only one role can be defined as the system user role!")
                return
            role_id = message.role_mentions[0].id
            guild_settings[message.guild.id]["SystemRole"] = role_id
            result = await commit_sql("""UPDATE GuildSettings SET SystemRole=%s WHERE ServerId=%s;""", (str(role_id),str(message.guild.id)))
            if result:
                await reply_message(message, "System user role successfully set!")
            else:
                await reply_message(message, "Database error!")
        elif command == 'listroles':
            records = await select_sql("""SELECT IFNULL(AdminRole,'0'),IFNULL(SystemRole, '0') FROM GuildSettings WHERE ServerId=%s;""", (str(message.guild.id),))
            if not records:
                await reply_message(message, "Database error!")
                return
            for row in records:
                
                admin_role = message.guild.get_role(int(row[0]))
                npc_role = message.guild.get_role(int(row[1]))

            response = "**Server Roles**\n\n**Admin Role:** " + str(admin_role) + "\n**System User Role:** " + str(npc_role) + "\n"
            await reply_message(message, response)
 
        elif command == 'listsetup':
            server_id = message.guild.id
            records = await select_sql("""SELECT ServerId,IFNULL(AdminRole,'0'),IFNULL(SystemRole,'0') FROM GuildSettings WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await reply_message(message, "Not all settings found.")
                return
            for row in records:
                guild_settings[server_id]["AdminRole"] = int(row[1])
                guild_settings[server_id]["SystemRole"] = int(row[2])
            response = "**CURRENT SERVER SETTINGS**\n\n"
            for setting in list(guild_settings[server_id].keys()):
                if guild_settings[message.guild.id][setting] == 0:
                    setting_value = "Not set or 0"
                else:
                    setting_value = str(guild_settings[message.guild.id][setting])
                response = response + "**" + setting + ":** " + setting_value +  "\n"
            await reply_message(message, response)
            
  
        elif command == 'addsystemuser':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must be a member of the admin role to add system users!")
                return
            if not message.mentions:
                await reply_message(message, "You didn't specify any users to add!")
                return
            role = discord.utils.get(message.guild.roles, id=guild_settings[message.guild.id]["SystemRole"])
            for user in message.mentions:
                await user.add_roles(role)
            await reply_message(message, "Users added to system user role!")                
        elif command == 'addadmin':
            if message.author != message.guild.owner:
                await reply_message(message, "Only the server owner can add admins!")
                return
            if not message.mentions:
                await reply_message(message, "You didn't specify any users to add!")
                return
            role = discord.utils.get(message.guild.roles, id=guild_settings[message.guild.id]["AdminRole"])
            for user in message.mentions:
                await user.add_roles(role)
            await reply_message(message, "Users added to admin role!")                 

        elif command == 'deletesystemuser':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must be a member of the admin role to remove system users!")
                return 
            if not message.mentions:
                await reply_message(message, "You didn't specify any users to remove!")
                return
            role = discord.utils.get(message.guild.roles, id=guild_settings[message.guild.id]["SystemRole"])
            for user in message.mentions:
                await user.remove_roles(role)
            await reply_message(message, "Users removed from NPC role!")                    
        elif command == 'deleteadmin':
            if message.author != message.guild.owner:
                await reply_message(message, "Only the server owner can delete admins!")
                return
            if not message.mentions:
                await reply_message(message, "You didn't specify any users to remove!")
                return
            role = discord.utils.get(message.guild.roles, id=guild_settings[message.guild.id]["AdminRole"])
            for user in message.mentions:
                await user.remove_roles(role)
            await reply_message(message, "Users removed from admin role!") 
        elif command == 'listids':
            response = "***CURRENT IDENTITY LIST***\n\n__ID Name__ - __User__ __Shortcut__\n"
            records = await select_sql("""SELECT IDName,UserId,Shortcut FROM Identities WHERE ServerId=%s;""", (str(message.guild.id),))
            name_re = re.compile(r"Member id=.*?name='(.+?)'")
            if not records:
                await reply_message(message, "No identities defined.")
                return
            for row in records:
                try:
                    username = discord.utils.get(message.guild.members, id=int(row[1])).name
                except:
                    username = "Unknown"
                response = response + row[0] + " - " + username + " - " + row[2] + "\n"
            await reply_message(message, response)            
        elif command == 'resetserver':
            if message.author != message.guild.owner:
                await reply_message(message, "Only the server owner can wipe all server data!")
                return
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            
            dm_tracker[message.author.id]["fieldlist"] = ["Confirm"]
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"]= []
            dm_tracker[message.author.id]["currentcommand"] = 'resetserver'
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            dm_tracker[message.author.id]["parameters"] = parsed_string
            await reply_message(message, "**WARNING! THIS WILL WIPE ALL SERVER SETTINGS FROM THE BOT! PLEASE REPLY TO THE DM WITH** ```CONFIRM``` **TO PROCEED.**")
            await direct_message(message, "**WARNING! THIS WILL WIPE ALL SERVER SETTINGS FROM THE BOT! PLEASE REPLY TO THE DM WITH** ```CONFIRM``` **TO PROCEED.**\n\nAre you sure you want to do this?")

        elif command == 'invite':
            await reply_message(message,"`Click here to invite All Systems Go:` https://discord.com/api/oauth2/authorize?client_id=940791775667322920&permissions=808577024&scope=bot")
        else:
            pass   
          
client.run('OTQwNzkxNzc1NjY3MzIyOTIw.YgMing.9PdOw8SHeJJQU7tftsjPVpZEUvc')
            

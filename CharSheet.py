import discord
import discordslashcommands as dsc
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
from slashcommands import SlashCommands

class NakedObject(object):
    pass
    
manager = None

command_handler = {}
webhook = { }
intents = discord.Intents.all()

client = discord.Client(heartbeat_timeout=600,intents=intents)

    
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='CharSheet', user='REDACTED', password='REDACTED', charset="utf8mb4")    
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
        connection = mysql.connector.connect(host='localhost', database='CharSheet', user='REDACTED', password='REDACTED', charset="utf8mb4")
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
        connection = mysql.connector.connect(host='localhost', database='CharSheet', user='REDACTED', password='REDACTED', charset="utf8mb4")
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
    
async def send_message(message, response):
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
        
        
async def post_webhook(channel, name, response, picture):
    temp_webhook = await channel.create_webhook(name='Chara-Tron')
    sent_message = await temp_webhook.send(content=response, username=name, avatar_url=picture, wait=True)
    await asyncio.sleep(1)
    await temp_webhook.delete() 
    return sent_message
    
    
@client.event
async def on_ready():
    global webhook
    global guild_settings
    global npc_aliases
    global dm_tracker
    global dialog_tracker
    global last_message
    global manager
    global slash_commands
    
        
    # commands = [{"name": 'getchar', 'desc': 'Get a specific character\'s profile.', 'options': [{'name': 'id', 'desc': 'The ID of the character'},]},
    # {"name": 'newprofile', 'desc': 'Create a new profile for the server.', 'options': [{},]},
    # {"name": 'info', 'desc': 'Bot help.', 'options': [{},]},
    # {"name": 'help', 'desc': 'Bot help.', 'options': [{},]},
    # {"name":  'newchar',  'desc': 'Create a new character.', 'options': [{},]},
    # {"name":  'listchars',  'desc': 'Show a list of characters on the server.', 'options': [{},]},
    # {"name":  'editchar',  'desc': 'Edit a character.', 'options': [{'name': 'id', 'desc': 'The ID of the character'},]},
    # {"name":  'deletechar',  'desc': 'Delete a character.', 'options': [{'name': 'id', 'desc': 'The ID of the character'},]},
    # {"name":  'showprofile',  'desc': 'Show the current server template.', 'options': [{},]},
    # {"name":  'deleteprofile',  'desc': 'Delete the server profile.', 'options': [{},]},
    # {"name":  'addfield',  'desc': 'Add a field to the profile.', 'options': [{'name': 'fieldname', 'desc': 'The name of the field to add.'},]},
    # {"name":  'deletefield',  'desc': 'Delete a field from the profile.', 'options': [{'name': 'fieldname', 'desc': 'The name of the field to delete.'},]},
    # {"name":  'invite',  'desc': 'Show an invite link.', 'options': [{},]},
    # {"name": 'listmychars', 'desc': 'List all characters owned by you.', 'options': [{},]},
    # {"name": "changefield", "desc": "Update an existing field name in the profile.", "options": [{"name": "oldfield", "desc": "The name of the existing field."},]}]
    
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

        
                
        # await asyncio.sleep(5)

            
    await log_message("Logged in!")
    print("Bot startup.")

@client.event
async def on_guild_join(guild):
    pass
    

@client.event
async def on_guild_remove(guild):
    if not guild.name:
        return
    await log_message("Left guild " + guild.name)
    
    
@client.event
async def on_message(message):
    global command_handler
    if message.author == client.user:
        return
        
    try:
        command_handler[message.author.id]
    except:
        print("except")
        command_handler[message.author.id] = {}
        command_handler[message.author.id]["current_command"] = None
        # command_handler[message.author.id]["command_channel"] = None
        # command_handler[message.author.id]["current_field"] = 0
        # command_handler[message.author.id]["field_list"] = []
        # command_handler[message.author.id]["field_values"] = []        
    if (message.content == 'cancel' or message.content == 'Cancel' or message.content == 'CANCEL') and command_handler[message.author.id] is not None:      
        command_handler[message.author.id] = None
        del command_handler[message.author.id]
        await send_message(message, "Your command has been stopped.")
        return
    try:
        if message.channel != command_handler[message.author.id]["command_channel"]:
            return
    except:
        pass
    if command_handler[message.author.id]["current_command"] == "editchar" and (message.content != "SKIP" and message.content != "Skip" and message.content != "skip") and command_handler[message.author.id]["current_field"] < len(command_handler[message.author.id]["field_list"]):
        print((message.content != "SKIP" or message.content != "Skip" or message.content != "skip"))
        if message.content != "skip":
            print("Gotcha!")
        count = command_handler[message.author.id]["current_field"]
        if message.attachments:
            command_handler[message.author.id]["field_values"][count] = message.attachments[0].url
        else:
            command_handler[message.author.id]["field_values"][count] = message.content
        command_handler[message.author.id]["current_field"] += 1
        count = command_handler[message.author.id]["current_field"]
        if command_handler[message.author.id]["current_field"] < len(command_handler[message.author.id]["field_list"]):        
            embed = discord.Embed(title="Edit character **Previous field changed.**",description="You are editing a current character. Please enter each field as requested by the profile. Type skip, SKIP or Skip to keep the field the same.")
            if len(command_handler[message.author.id]["field_values"][count]) > 1000:
                response = "**" + command_handler[message.author.id]["field_list"][count] + "**:  " + command_handler[message.author.id]["field_values"][count] + "\n\n"
                await send_message(message, response)
            else:
                embed.add_field(name=command_handler[message.author.id]["field_list"][count], value=command_handler[message.author.id]["field_values"][count])
                await message.channel.send(embed=embed)               
          #  embed.add_field(name=command_handler[message.author.id]["field_list"][count], value=command_handler[message.author.id]["field_values"][count])
          #  await message.channel.send(embed=embed)
            return
        else:
            pass
    if command_handler[message.author.id]["current_command"] == "editchar" and (message.content == "SKIP" or message.content == "Skip" or message.content == "skip") and command_handler[message.author.id]["current_field"] < len(command_handler[message.author.id]["field_list"]):
        command_handler[message.author.id]["current_field"] += 1
        count = command_handler[message.author.id]["current_field"]
        if command_handler[message.author.id]["current_field"] < len(command_handler[message.author.id]["field_list"]):
            embed = discord.Embed(title="Edit character **Previous field not changed.**",description="You are editing a current character. Please enter each field as requested by the profile. Type skip, SKIP or Skip to keep the field the same.")
            if len(command_handler[message.author.id]["field_values"][count]) > 1000:
                response = "**" + command_handler[message.author.id]["field_list"][count] + "**:  " + command_handler[message.author.id]["field_values"][count] + "\n\n"
                await send_message(message, response)
            else:
                embed.add_field(name=command_handler[message.author.id]["field_list"][count], value=command_handler[message.author.id]["field_values"][count])
                await message.channel.send(embed=embed) 
        
            return
        else:
            pass
    if command_handler[message.author.id]["current_command"] == "editchar":
        editchar = "UPDATE Server" + str(message.guild.id) + " SET "
        editchar_tuple = ()
        counter = 0
        for field in command_handler[message.author.id]["field_list"]:
            editchar = editchar + "Field" + str(counter) + "=%s, "
            editchar_tuple = editchar_tuple + (command_handler[message.author.id]["field_values"][counter],)
            counter+=1
        editchar = re.sub(r", $","",editchar)
        editchar = editchar + " WHERE Id=%s;"
        editchar_tuple = editchar_tuple + (command_handler[message.author.id]["parameter"],)
        result = await commit_sql(editchar, editchar_tuple)
        if result:
            await send_message(message, "Character successfully updated.")
        else:
            await send_message(message, "Database error!")
        command_handler[message.author.id] = {}
        command_handler[message.author.id]["current_command"] = None
        return
    if command_handler[message.author.id]["current_command"] == "newprofile" and (message.content == "done" or message.content == "DONE" or message.content == "Done"):
        table_creation = "CREATE TABLE Server" + str(message.guild.id) + " (Id INT AUTO_INCREMENT, "
        counter = 0
        for field in command_handler[message.author.id]["field_list"]:
            table_creation = table_creation + "Field" + str(counter) + " TEXT, "
            counter +=1
        table_creation = table_creation + " PRIMARY KEY(Id));"
        result = await commit_sql(table_creation)
        if result:
            await send_message(message, "Server table created.")
            header_creation = "INSERT INTO Server" + str(message.guild.id) + "("
            counter = 0
            values =  ") VALUES ("
            value_tuple = ()
            for field in command_handler[message.author.id]["field_list"]:
                header_creation = header_creation + "Field" + str(counter) + ", "
                values = values + "%s, "
                value_tuple = value_tuple + (field,)
                counter+=1
            header_creation = re.sub(r", $","",header_creation)
            values = re.sub(", $","",values)
            header_creation = header_creation + values + ");"
            result2 = await commit_sql(header_creation, value_tuple)
            if result2:
                await send_message(message, "Your profile has been successfully created!")
                command_handler[message.author.id] = {}
                command_handler[message.author.id]["current_command"] = None
                result3 = await commit_sql("CREATE TABLE Index" + str(message.guild.id) + " (Id INT AUTO_INCREMENT, UserId VARCHAR(40), CharId INT, PRIMARY KEY(Id));")
                if result3:
                    await send_message(message, "Created the character index successfully!")
                else:
                    await send_message(message, "Unable to create character index!")
            else:
                await send_message(message, "Database error!")
            
        else:
            await send_message(message, "Database error!")
        return    
    if command_handler[message.author.id]["current_command"] == "newprofile":
        command_handler[message.author.id]["current_field"] += 1
        command_handler[message.author.id]["field_list"].append(message.content)
        embed = discord.Embed(title="Create New Profile",description="Please enter the next profile field title, or type `done` to commit to the database. Type `cancel` to abandon this command.")
        await message.channel.send(embed=embed)
        return        
    if command_handler[message.author.id]["current_command"] == "newchar" and command_handler[message.author.id]["current_field"] < len(command_handler[message.author.id]["field_list"]):
        if message.attachments:
            command_handler[message.author.id]["field_values"].append(message.attachments[0].url)
        else:
            command_handler[message.author.id]["field_values"].append(message.content)    
        
        command_handler[message.author.id]["current_field"] += 1
        current_counter = command_handler[message.author.id]["current_field"]
        if command_handler[message.author.id]["current_field"] < len(command_handler[message.author.id]["field_list"]):
            embed = discord.Embed(title="New Character", description="The next field is **" + command_handler[message.author.id]["field_list"][current_counter] + "**")
            await message.channel.send(embed=embed)
            return
        else:
            pass
    if command_handler[message.author.id]["current_command"] == "newchar":
        create_char = "INSERT INTO Server" + str(message.guild.id) + " ("
        counter = 0
        values = ") VALUES ("
        value_tuple = ()
        for field in command_handler[message.author.id]["field_values"]:
            create_char = create_char + "Field" + str(counter) + ", "
            values = values + "%s, "
            value_tuple = value_tuple + (field,)
            counter+=1
        create_char = re.sub(r", $","",create_char)
        values = re.sub(", $","",values)
        create_char = create_char + values + ");"
        result2 = await commit_sql(create_char, value_tuple)
        if result2:
            await send_message(message, "Your character has been successfully created!")
            records = await select_sql("SELECT MAX(Id) FROM Server" + str(message.guild.id) + ";")
            if not records:
                await send_message(message, "Could not find the ID for the new character!")
                return
            for row in records:
                char_id = row[0]
            result3 = await commit_sql("INSERT INTO Index" + str(message.guild.id) + "(UserId,CharId) VALUES (%s,%s);",(str(message.author.id),str(char_id)))
            if result3:
                await send_message(message, "Character has been assigned ID **" + str(char_id) + "**.")
            else:
                await send_message(message, "Database error!")
        else:
            await send_message(message, "Database error!")  
        command_handler[message.author.id] = {}
        command_handler[message.author.id]["current_command"] = None
        return
    if command_handler[message.author.id]["current_command"] == "changefield":
        new_field = message.content
        old_field = command_handler[message.author.id]["field_values"][0]
        field_number = command_handler[message.author.id]["parameter"]
        result = await commit_sql("UPDATE Server" + str(message.guild.id) + " SET Field" + str(field_number) + "=%s WHERE Id=1;",(str(new_field),))
        if result:
            await send_message(message, "Field successfully renamed.")
        else:
            await send_message(message, "Unable to update field name: database error!")
        command_handler[message.author.id] = {}
        command_handler[message.author.id]["current_command"] = None
        return
    if command_handler[message.author.id]["current_command"] == "addfield":
        after_field = message.content
        print(command_handler[message.author.id]["field_list"])
        after_index = list(command_handler[message.author.id]["field_list"]).index(after_field)
        

        for x in range(len(command_handler[message.author.id]["field_list"]) - 1, int(after_index ),-1):
            result3 = await commit_sql("ALTER TABLE Server" + str(message.guild.id) + " RENAME COLUMN Field" + str(x) + " TO Field" + str(x+1)+ ";")
            if result3:
                pass
            else:
                await send_message(message, "Unable to update all new fields! Please contact support!")
        result = await commit_sql("ALTER TABLE Server" + str(message.guild.id) + " ADD COLUMN Field" + str(after_index + 1) + " TEXT AFTER Field" + str(after_index) + ";")
        if result:
            result2 = await commit_sql("UPDATE Server" + str(message.guild.id) + " SET Field" +str(after_index + 1)+  "=%s WHERE Id=1;",( command_handler[message.author.id]["field_values"][0],))
            if result2:
                result4 = await commit_sql("UPDATE Server" + str(message.guild.id) + " SET Field" +str(after_index + 1) + "='NA' WHERE Id!=1;")
                if result4:
                    await send_message(message, "Field succesfully added!")
                else:
                    await send_message(message, "Couldn't initialize characters!")
            else:
                await send_message(message, "Could not initialize new field!")
        else:
            await send_message(message, "Could not add new field!")
        command_handler[message.author.id] = {}
        command_handler[message.author.id]["current_command"] = None            
        return
        
        
        
    if message.content.startswith('-'):
        
        command_string = message.content.split(' ')
        command = command_string[0].replace('-','')
        parsed_string = message.content.replace("-" + command + " ","").strip()
        if parsed_string == "-" + command:
            parsed_string = None
        print(parsed_string)
        if command == 'info' or command == 'help':
            embed = discord.Embed(title="Character Profile Bot Help",description="Character Profile is a Discord bot designed to allow custom character profiles for RP servers, gaming servers and other uses. You can create a custom profile, create characters, and manage characters with this bot.")
            embed.add_field(name="/info",value="This help.", inline=False)
            embed.add_field(name="/newprofile",value="Create a new profile template for your server. You must have manage server permissions to create a template. The bot will ask you in the current channel each field, and you may type `done` when complete.", inline=False)
            embed.add_field(name="/newchar",value="Create a new character using the server profile template. You must be a server member to create a character. You will be asked to complete each field in the template. When it is finished, the bot will automatically commit the profile to the database.", inline=False)
            embed.add_field(name="/getchar ID",value="Get a character's profile by the character ID. To see character IDs, use -listallchars", inline=False)
            embed.add_field(name="/listchars",value="List all characters on the server with their ID, first field and player.", inline=False)
            embed.add_field(name="/editchar ID",value="Edit an existing character. You must be the character's owner or a user with Manage Server permissions to edit a character. The bot will prompt you for each field in the template. To keep a field the same, use `skip`. The bot will automatically commit your changes after the last field is completed.", inline=False)
            embed.add_field(name="/deletechar ID",value="Delete a character from the server. You must be the character's owner or a user with Manage Server permissions to delete a character. There is no way of undoing this short of contacting support for a database restore.", inline=False)
            embed.add_field(name="/showprofile",value="Show the current server profile template with placeholder text.", inline=False)
            embed.add_field(name="/deleteprofile", value="Delete all characters and the profile template from the server. You must have Manage Server permissions to do this. There is no editing a profile template currently. Adding fields may be supported in a later release. There is no restoring any settings except for contacting support for a database restore, **so be careful with this command!**", inline=False)
            embed.add_field(name="/invite",value="Show the bot invite link.", inline=False)
            embed.add_field(name="/addfield FIELD_NAME", value="Add a new field to the existing server profile template. You will be asked for the field to place the new one **AFTER**. It cannot be before the first field. All current characters will receive the new field in their profile with the value 'Blank' at creation.", inline=False)
            embed.add_field(name="/changefield oldfield",value="Change the name of an existing profile field. Only an administrator may modify the profile.")
            embed.add_field(name="/deletefield FIELD_NAME", value="Delete a field from the server profile template. This takes effect immediately and removes that field from the template and all existing character profiles.", inline=False)
            embed.add_field(name="/listmychars", value="List all the characters that are yours on the server.")
            embed.add_field(name="Bot Tips",value="- You may cancel a command at any time (except -deleteprofile or -deletechar) by typing `cancel` before the command is complete.\n- You may skip character fields by typing `skip` during a character edit.\n- The bot will not display profile fields set to `NA`.\n- Profile values are limited by Discord embed limits. You may have up to 25 fields for your profile template. The profile template fields may be up to 256 characters and the text in each field may be up to 1024 characters. The profile in total may not exceed 6000 characters.", inline=False)
            await message.channel.send(embed=embed)
        
        elif command =='invite':
            await send_message(message, "Invite me here: https://discord.com/api/oauth2/authorize?client_id=1016531636587860019&permissions=2684405824&scope=bot%20applications.commands")
        elif command == 'listmychars':
            headers = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if not headers:
                await send_message(message, "This server hasn't set up a profile yet!")
                return
            for row in headers:
                selector = row[1]
            index = await select_sql("SELECT CharId FROM Index" + str(message.guild.id) + " WHERE UserId=%s;",(str(message.author.id),))
            if not index:
                await send_message(message, "You don't have any characters!")
                return
            response = "**ID,**, **" + selector + ",**\n\n"
            for row in index:
                records = await select_sql("SELECT Field0 FROM Server" + str(message.guild.id) + " WHERE Id=%s;",(str(row[0]),))
                for x in records:
                    response = response + str(row[0]) + ", " + x[0] + "\n"
            await send_message(message, response)
            
        elif command == 'newprofile':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to create a profile!")
                return
            records = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if records:
                await send_message(message, "A profile already exists! Please delete it before creating a new one!")
                return
            command_handler[message.author.id] = {}
            command_handler[message.author.id]["current_command"] = "newprofile"
            command_handler[message.author.id]["command_channel"] = message.channel
            command_handler[message.author.id]["current_field"] = 0
            command_handler[message.author.id]["field_list"] = []
            command_handler[message.author.id]["field_values"] = []
            embed = discord.Embed(title="Create New Custom Profile",description="You have activated the creation of a new profile! Please follow the prompts in this channel to create it. Every reply you type here will be considered a response. Below, please type the text for the first field. You will get a prompt for each field. Please type `done` when you are finished!")
            await message.channel.send(embed=embed)
            
        elif command == 'newchar':
            if not message.author.guild_permissions.send_messages:
                await send_message(message, "You must have be a server member to create a character!")
                return        
            command_handler[message.author.id] = {}
            command_handler[message.author.id]["current_command"] = "newchar"
            command_handler[message.author.id]["command_channel"] = message.channel
            command_handler[message.author.id]["current_field"] = 0
            command_handler[message.author.id]["field_list"] = []
            command_handler[message.author.id]["field_values"] = []        
            records = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if records:
                for row in records:
                    for x in row[1:]:
                        command_handler[message.author.id]["field_list"].append(x)
                        print(x)
                embed = discord.Embed(title="New character",description="You are entering a new character. Please enter each field as requested by the profile. Your first field is **" + command_handler[message.author.id]["field_list"][0] + "**")
                await message.channel.send(embed=embed)
                
        elif command == 'editchar':
            if not parsed_string:
                await send_message(message, "You didn't specify a character ID to edit!")
                return
            records = await select_sql("SELECT UserId FROM Index" + str(message.guild.id) + " WHERE CharId=%s;",(str(parsed_string),))
            if not records:
                await send_message(message, "There is no character with that ID!")
                return
            for row in records:
                user_id=row[0]
            
            if not message.author.guild_permissions.manage_guild and int(user_id) != message.author.id:
                await send_message(message, "You must have manage server permissions to edit a character, or this is not your character!")
                return

            command_handler[message.author.id] = {}
            command_handler[message.author.id]["current_command"] = "editchar"
            command_handler[message.author.id]["command_channel"] = message.channel
            command_handler[message.author.id]["current_field"] = 0
            command_handler[message.author.id]["field_list"] = []
            command_handler[message.author.id]["field_values"] = []
            command_handler[message.author.id]["parameter"] = parsed_string
            records = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if records:
                for row in records:
                    for x in row[1:]:
                        command_handler[message.author.id]["field_list"].append(x)
                        print(x)
            records = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=%s;",(str(parsed_string),))
            if records:
                for row in records:
                    for x in row[1:]:
                        command_handler[message.author.id]["field_values"].append(x)
                        print(x)                        
                embed = discord.Embed(title="Edit character",description="You are editing a current character. Please enter each field as requested by the profile. Type skip, SKIP or Skip to keep the field the same.")

                await message.channel.send(embed=embed)
                if len(command_handler[message.author.id]["field_values"][0]) > 1000:
                    response = response + "**" + command_handler[message.author.id]["field_list"][0] + "**:  " + command_handler[message.author.id]["field_values"][0] + "\n\n"
                    await send_message(message, response)
                else:
                    embed.add_field(name=command_handler[message.author.id]["field_list"][0], value=command_handler[message.author.id]["field_values"][0])
                    await message.channel.send(embed=embed)            
            
        elif command == 'showprofile':
            records = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if not records:
                await send_message(message, "No custom profile has been created yet!")
                return
            embed = discord.Embed(title="Character Profile Template for " + message.guild.name)
            for row in records:
                for x in row[1:]:
                    embed.add_field(name=x, value="Text goes here")
            await message.channel.send(embed=embed)
                
        elif command == 'deletechar':
            if not parsed_string:
                await send_message(message, "You didn't specify a character ID to delete!")
                return
            records = await select_sql("SELECT UserId FROM Index" + str(message.guild.id) + " WHERE CharId=%s;",(str(parsed_string),))
            if not records:
                await send_message(message, "There is no character with that ID!")
                return
            for row in records:
                user_id=row[0]
            
            if not message.author.guild_permissions.manage_guild and int(user_id) != message.author.id:
                await send_message(message, "You must have manage server permissions to delete a character, or this is not your character!")
                return
            result = await commit_sql("DELETE FROM Server" + str(message.guild.id) + " WHERE Id=%s;",(str(parsed_string),))
            if result:
                result2 = await commit_sql("DELETE FROM Index" + str(message.guild.id) + " WHERE CharId=%s;",(str(parsed_string),))
                if result2:
                    await send_message(message, "Character has been deleted.")
                else:
                    await send_message(message, "Unable to delete character index!")
            else:
                await send_message(message, "Unable to delete character profile!")
                
        elif command == 'deleteprofile':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to remove the profile!")
                return        
            result = await commit_sql("DROP TABLE Server" + str(message.guild.id) + ";")
            if result:
                await send_message(message, "All profiles deleted.")
            else:
                await send_message(message, "Unable to delete profile!")
            result = await commit_sql("DROP TABLE Index" + str(message.guild.id) + ";")
            if result:
                await send_message(message, "Character index deleted.")
            else:
                await send_message(message, "Unable to delete character index!")
        elif command == 'listchars':
            headers = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if not headers:
                await send_message(message, "This server hasn't set up a profile yet!")
                return
            for row in headers:
                selector = row[1]
            index = await select_sql("SELECT UserId, CharId FROM Index" + str(message.guild.id) + ";")
            if not index:
                await send_message(message, "No characters have been created yet!")
                return
            response = "**ID,** **Player,** **" + selector + ",**\n\n"
            for row in index:
                records = await select_sql("SELECT Field0 FROM Server" + str(message.guild.id) + " WHERE Id=%s;",(str(row[1]),))
                user = discord.utils.get(message.guild.members, id=int(row[0]))
                if not user:
                    username="Unknown"
                else: username = user.name
                # username = discord.utils.get(message.guild.members, id=int(row[0])).name
                for x in records:
                    response = response + str(row[1]) + ", " + username + ", " + x[0] + "\n"
            await send_message(message, response)
        elif command == 'newnpc':
            pass
        elif command == 'post':
            pass
        elif command == 'editnpc':
            pass
        elif command == 'deletenpc':
            pass
        elif command == 'changefield':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to modify the profile!")
                return
            if not parsed_string:
                await send_message(message, "You did not specify a field name to change!")
                return
            records = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if not records:
                await send_message(message, "This server has not created a profile yet!")
                return
            found = False
            counter = 0
            found_item = 0
            for row in records:
                for item in row:
                    if str(item) == parsed_string:
                        found = True
                        found_item = counter - 1
                    counter+=1    
            if not found:
                await send_message(message, "There is no field with that name defined!")
                return
            
                    
            command_handler[message.author.id] = {}
            command_handler[message.author.id]["current_command"] = "changefield"
            command_handler[message.author.id]["command_channel"] = message.channel
            command_handler[message.author.id]["current_field"] = 0
            command_handler[message.author.id]["field_list"] = ["oldfield","newfield"]
            command_handler[message.author.id]["field_values"] = [parsed_string,]
            command_handler[message.author.id]["parameter"] = found_item
            embed = discord.Embed(title="Change a field name.",description="You have requested to change the name of field **" + parsed_string + "**. Please enter below what you want the new field name to be.")
            await message.channel.send(embed=embed)
            
        elif command == 'addfield':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to modify the profile!")
                return
            if not parsed_string:
                await send_message(message, "You did not specify a field name to add!")
                return
              
            records = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if not records:
                await send_message(message, "This server has not created a profile yet!")
                return
            command_handler[message.author.id] = {}
            command_handler[message.author.id]["current_command"] = "addfield"
            command_handler[message.author.id]["command_channel"] = message.channel
            command_handler[message.author.id]["current_field"] = 0
            command_handler[message.author.id]["field_list"] = []
            command_handler[message.author.id]["field_values"] = [parsed_string,]  
            field_list= ""    
            if records:
                for row in records:
                    for x in row[1:]:
                        field_list = field_list + x + "\n"
                        command_handler[message.author.id]["field_list"].append(x)
            print(command_handler[message.author.id]["field_list"])
            embed = discord.Embed(title="Add a profile field",description="You have requested to add a field to the profile template. Please look at the list below and type the name of the field you would like the new field to appear **AFTER.** The new field cannot appear before the first field in the profile. This will add a new field to all profiles that will initially be blank.")
            embed.add_field(name="List of current fields",value=field_list)
            await message.channel.send(embed=embed)
        elif command == 'deletefield':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to modify the profile!")
                return
            if not parsed_string:
                await send_message(message, "You did not specify a field name to delete!")
                return
            records = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if not records:
                await send_message(message, "This server has not created a profile yet!")
                return
            field_list = []
            if records:
                for row in records:
                    for x in row[1:]:
                        field_list.append(x)            
            delete_index = list(field_list).index(parsed_string)
            
            result = await commit_sql("ALTER TABLE Server" + str(message.guild.id) + " DROP COLUMN Field" + str(delete_index) + ";")
            if result:
            
                for x in range(delete_index + 1, len(field_list),1):
                    result3 = await commit_sql("ALTER TABLE Server" + str(message.guild.id) + " RENAME COLUMN Field" + str(x) + " TO Field" + str(x-1)+ ";")
                    if result3:
                        pass
                    else:
                        await send_message(message, "Unable to update all new fields! Please contact support!")
                await send_message(message, "Field " + parsed_string + " has been deleted from the template and all server profiles.")
            else:
                await send_message(message, "Could not delete field!")

            
        elif command == 'getchar':
            if not parsed_string:
                await send_message(message, "You didn't specify a character ID!")
                return
            headers = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=1;")
            if not headers:
                await send_message(message, "This server hasn't set up a profile yet!")
                return
            header_list = []
            for row in headers:
                for x in row[1:]:
                    header_list.append(x)
            profile = await select_sql("SELECT * FROM Server" + str(message.guild.id) + " WHERE Id=%s;",(str(parsed_string),))
            if not profile:
                await send_message(message, "No character with that ID found!")
                return
            values = []    
            for row in profile:
                for x in row[1:]:
                    values.append(x)
            records = await select_sql("SELECT UserId FROM Index" + str(message.guild.id) + " WHERE CharId=%s;",(str(parsed_string),))
            if not records:
                await send_message(message, "Unable to find the user who owns this character!")
                user_id = "Unknown"
            else:
                for row in records:
                    user_id = "<@" + str(row[0]) + ">"
            embed = discord.Embed(title="Character Profile", description="Player: " + user_id)
            counter = 0
            response = ""
            for header in header_list:
                if (re.search(r"http.*(?:png|jpg|jpeg|gif|bmp)",values[counter], re.I)):
                    embed.set_image(url=values[counter])
                elif values[counter] == 'NA':
                    pass
                else:
                    if len(values[counter]) < 1000:
                        embed.add_field(name=header, value=values[counter])
                    else:
                        response = response + "**" + header + "**:  " + values[counter] + "\n\n"
                counter+=1
            await message.channel.send(embed=embed)
            if response:
                await send_message(message, response)
            
            
@client.event
async def on_interaction(member, interaction):
    global command_handler
    global slash_commands
    print("called here" + str(interaction))
    slash_commands.convert_to_message(interaction, member, "-") 

client.run('REDACTED')  
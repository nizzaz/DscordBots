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
import nltk
from nltk.corpus import wordnet as wn
import csv
import discordslashcommands as dsc

intents = discord.Intents(messages=True,guilds=True, message_content=True)
class NakedObject(object):
    pass
manager = None

connection = mysql.connector.connect(host='localhost', database='Chroma', user='REDACTED', password='REDACTED')
client = discord.Client(heartbeat_timeout=600, intents=intents)

async def slash_commands(command_name, command_desc, options):
    global manager
    print("Command name " + command_name)
    command = dsc.Command(command_name, description=command_desc)
    try:
        options[0]['name']
    except:
        manager.add_global_command(command) 
        return
    for opt in options:
        print("Adding option " + opt['name'])
        option = dsc.Option(opt['name'],opt['desc'], dsc.STRING, True)
        command.add_option(option)         


    
    manager.add_global_command(command)


async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    try:
        connection = mysql.connector.connect(host='localhost', database='Chroma', user='REDACTED', password='REDACTED')    
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
    try:
        connection = mysql.connector.connect(host='localhost', database='Chroma', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
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
        connection = mysql.connector.connect(host='localhost', database='Chroma', user='REDACTED', password='REDACTED')
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

def role_check(role_required, user):
    for role in user.roles:
        if role.id == role_required:
            return True
			
# @client.event
# async def on_raw_reaction_add(payload):
    # global server_settings
    # if payload.message_id == server_settings[payload.guild_id]["ConfirmMessage"] and str(payload.emoji) == server_settings[payload.guild_id]["ConfirmReaction"]:
        # user = payload.member
        # server_obj = client.get_guild(payload.guild_id)
        # role = discord.utils.get(server_obj.roles, id=server_settings[payload.guild_id]["FullMemberRole"])
        # old_role = discord.utils.get(server_obj.roles, id=server_settings[payload.guild_id]["NewMemberRole"])
        # for current_role in user.roles:
            # if current_role == role:
                # return
        # await user.remove_roles(old_role)
        # await user.add_roles(role)
        # channel = client.get_channel(server_settings[payload.guild_id]["MessageChannel"])
        # await channel.send(">>> " + server_settings[payload.guild_id]["Greeting"] + " <@" + str(user.id) + ">")


@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name)
    await log_message("Done!")
    
@client.event
async def on_guild_remove(guild):
	await log_message("Left guild " + guild.name)

    
    
@client.event
async def on_ready():
    global manager
    
    manager = dsc.Manager(client)
    
        
    commands = [{"name": 'setcolor', 'desc': 'Set your own color or another user\'s color.', 'options': [{'name': 'color', 'desc': 'Name of color role.'}]},
    {"name": 'info', 'desc': 'Bot help.', 'options': [{}]},
    {"name": 'help', 'desc': 'Bot help.', 'options': [{}]},
    {"name": 'deleteallcolors', 'desc': 'Delete all bot colors.', 'options': [{}]},
    {"name": 'colorchart', 'desc': 'Show the base color chart.', 'options': [{}]},
    {"name": 'invite', 'desc': 'Show the bot invite.', 'options': [{}]},
    {"name": 'addcolor', 'desc': 'Add a custom color to the bot.', 'options': [{'name': 'color name', 'desc': 'Name of new color role.'}, {'name': 'hex code', 'desc': 'hex code for color'}]},
    {"name": 'listbasecolors', 'desc': 'List base colors in the bot.', 'options': [{}]},
    {"name": 'addbasecolor', 'desc': 'Add base colors to your server.', 'options': [{'name': 'color list', 'desc': 'List of color names separated by spaces.'}]},
    {"name": 'deletecolor', 'desc': 'Delete a color role.', 'options': [{'name': 'color name', 'desc': 'Color to delete.'}]},
    {"name": 'showcolor', 'desc': 'Show a color with its hex code.', 'options': [{'name': 'color name', 'desc': 'Name of the color.'}]},
    {"name": 'randomcolor', 'desc': 'Set your color to a random choice.', 'options': [{}]}
    ]
    # for command in commands:
        # await slash_commands(command['name'], command['desc'], command['options'])
        # await asyncio.sleep(5)
    await log_message("Welcome to Discord")
    
@client.event
async def on_message(message):
   

    if message.author == client.user:
        return
    if message.author.bot and message.author.id != 787355055333965844:
        return

            
    if message.content.startswith('c!'):


        command_string = message.content.split(' ')
        command = command_string[0].replace('c!','')
        parsed_string = message.content.replace("c!" + command + " ","")
        username = message.author.name
        server_name = message.guild.name

        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        
        # if command == 'loadbasecolors':
            # await send_message(message, "Loading base colors...")
            # with open('/home/REDACTED/BotMaster/Colors.csv',newline='\n') as csvfile:
                # color_reader = csv.reader(csvfile, delimiter=',')
                # for row in color_reader:
                    # await commit_sql("""INSERT INTO ColorDefaults (ColorName, HexCode) VALUES (%s, %s);""",(str(row[0]),str(row[1]).replace('#','0x')))
            # await send_message(message, "Colors loaded into database!")
            
        # if command == 'createroles':
            # if not message.author.guild_permissions.manage_roles:
                # await send_message(message, "You don't have sufficient permissions to use this command!")
                # return        
            # await send_message(message, "Creating color roles!")
            # records = await select_sql("""SELECT ColorName, HexCode FROM ColorDefaults;""")
            # server_roles = { }
            # counter = 2
            # for row in records:
                # await log_message("Color role " + row[0])
                # new_role = await message.guild.create_role(name=row[0], color=discord.Colour(int(row[1], 16)))
                # server_roles[new_role] = counter
                # result = await commit_sql("""INSERT INTO ServerColors (ServerId, ColorName, HexCode, RoleId) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(row[0]),str(row[1]),str(new_role.id)))
                # counter = counter + 1
                # await asyncio.sleep(0.5)
            # await send_message(message, "Roles created!")
        if command == 'setcolor':
            if message.mentions:
                user = message.mentions[0]
                parsed_string = re.sub(r"<.+>","",parsed_string)
            else:
                user = message.author
            if user != message.author and not message.author.guild_permissions.manage_roles:
                await send_message(message, "You don't have sufficient permissions to use this command!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify a color to set!")
                return
            records = await select_sql("""SELECT RoleId,ColorName FROM ServerColors WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No colors defined here!")
                return
            for row in records:
                if re.search(r"^" + row[1] + "$",parsed_string.strip(), re.IGNORECASE):
                    new_role = message.guild.get_role(int(row[0]))
            if not new_role:
                await send_message(message, "That is not a valid color role!")
                return
            server_colors = []
            for row in records:
                server_colors.append(int(row[0]))
            for role_id in server_colors:
                for user_role in user.roles:
                    if user_role.id == role_id:
                        await user.remove_roles(user_role)
                        break
            await user.add_roles(new_role)
            await send_message(message, "Your color has been set to " + parsed_string)
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
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await send_message(message,"Admin command only!")
                return   
            await send_message(message, "Server count: " + str(len(client.guilds)))                 
        elif command == 'deleteallcolors':
            if not message.author.guild_permissions.manage_roles:
                await send_message(message, "You don't have sufficient permissions to use this command!")
                return        
            records = await select_sql("""SELECT RoleId FROM ServerColors WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "There are no color roles to delete!")
                return
            for row in records:
                delete_role = message.guild.get_role(int(row[0]))
                await delete_role.delete()
                await asyncio.sleep(0.5)
            result = await commit_sql("""DELETE FROM ServerColors WHERE ServerId=%s;""",(str(message.guild.id),))
            await send_message(message, "All roles deleted!")
        elif command == 'colorchart':
            file_path = "/home/REDACTED/BotMaster/colorchart.png"
            await message.channel.send(file=discord.File(file_path)) 
        elif command == 'invite':
            await send_message(message, "Invite me: https://discord.com/api/oauth2/authorize?client_id=789331122084773939&permissions=2415970304&scope=bot%20applications.commands")
            
            
        elif command == 'addcolor':
            if not message.author.guild_permissions.manage_roles:
                await send_message(message, "You don't have sufficient permissions to use this command!")
                return 
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters! Expecting COLORNAME HEXCODE!")
                return
            m = re.search(r"(?P<name>.+) (?P<code>[0-9A-F]+)",parsed_string, re.IGNORECASE)
            if not m:
                await send_message(message, "You didn't specify the correct parameters! Expecting COLORNAME HEXCODE!")
                return
            color_name = m.group('name')
            hex_code = m.group('code')
            if not color_name or not hex_code:
                await send_message(message, "You didn't specify the correct parameters! Expecting COLORNAME HEXCODE!")
                return
            records = await select_sql("""SELECT Id,ColorName,HexCode FROM ServerColors WHERE (ColorName=%s OR HexCode=%s) AND ServerId=%s;""",(str(color_name),str(hex_code),str(message.guild.id)))
            if records:
                for row in records:
                    await send_message(message,"A color named " + row[1] + " with code " + str(row[2]) + " already exists in the database!")
                return
            new_role = await message.guild.create_role(name=color_name, color=discord.Colour(int("0x" + hex_code, 16))) 
            if new_role:
                result = await commit_sql("""INSERT INTO ServerColors (ServerId, ColorName, HexCode, RoleId) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(color_name),str("0x" + hex_code), str(new_role.id)))
                if result:
                    await send_message(message, new_role.name + " created successfully!")
                else:
                    await send_message(messsage, "Error creating database entry!")
            else:
                await send_message(message, "Error creating new role!")
        elif command == 'showcolor':
            if not parsed_string:
                await send_message(message, "No color name was specified!")
                return
            records = await select_sql("""SELECT ColorName, HexCode FROM ServerColors WHERE ServerId=%s AND ColorName=%s;""",(str(message.guild.id),str(parsed_string)))
            if not records:
                await send_message(message, "No color was found by that name!")
                return
            for row in records:
                color_name = row[0]
                hex_code = row[1]
                
            await send_message(message, "Color " + color_name + " has a hex code of " + str(hex_code) + ".")
        elif command == 'listcolors':
            records = await select_sql("""SELECT ColorName FROM ServerColors WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No colors defined on this server!")
                return
            response = "**Server colors:**: "
            for row in records:
                response = response + row[0] + ", "
            await send_message(message, response)
        elif command == 'listbasecolors':
            records = await select_sql("""SELECT ColorName FROM ColorDefaults;""")
            response = "**Base colors:**: "
            for row in records:
                response = response + row[0] + ", "
            await send_message(message, response)
        elif command == 'addbasecolor':
            if not message.author.guild_permissions.manage_roles:
                await send_message(message, "You don't have sufficient permissions to use this command!")
                return 
            if not parsed_string.strip():
                await send_message(message, "You didn't specify any parameters! Expecting COLOR1 COLOR2...!")
                return
            color_list = parsed_string.split(' ')
            response = "Color Add Log:\n\n"
            for color in color_list:
                records = await select_sql("""SELECT ColorName, HexCode FROM ColorDefaults WHERE ColorName=%s;""",(str(color),))
                if not records:
                    response = "Color " + color + " not found, skipping.\n"
                else:
                    for row in records:
                        color_name = row[0]
                        hex_code = row[1]
                new_role = await message.guild.create_role(name=color_name, color=discord.Colour(int(hex_code, 16))) 
                if new_role:
                    result = await commit_sql("""INSERT INTO ServerColors (ServerId, ColorName, HexCode, RoleId) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(color_name),str("0x" + hex_code), str(new_role.id)))
                    if result:
                        response = response + new_role.name + " created successfully!\n"
                    else:
                        response = response +  "Error creating database entry for " + color + "\n"
                else:
                    response = response +  "Error creating new role for " + color + ".\n" 
            await send_message(message, response)
        elif command == 'deletecolor':
            if not message.author.guild_permissions.manage_roles:
                await send_message(message, "You don't have sufficient permissions to use this command!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters! Expecting COLORNAME!")
                return
            color_name = parsed_string.strip()
            records = await select_sql("""SELECT Id,ColorName,RoleId FROM ServerColors WHERE ColorName=%s AND ServerId=%s;""",(str(color_name),str(message.guild.id)))
            if not records:
                await send_message(message,"That color was not found!")
                return
            for row in records:
                
                result = await commit_sql("""DELETE FROM ServerColors WHERE Id=%s;""",(str(row[0]),))
                deleted_role = message.guild.get_role(int(row[2]))
                await deleted_role.delete()
            if result:
                await send_message(message, "Color deleted from server!")
        elif command == 'randomcolor':
            if message.mentions:
                user = message.mentions[0]
            else:
                user = message.author
            if user != message.author and not message.author.guild_permissions.manage_roles:
                await send_message(message, "You don't have sufficient permissions to use this command!")
                return
            records = await select_sql("""SELECT RoleId,ColorName FROM ServerColors WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No colors defined here!")
                return
            server_color_list = []
            server_ids = []
            for row in records:
                server_color_list.append(row[1])
                server_ids.append(int(row[0]))
            new_role_num = random.randint(0,len(server_color_list) -1)
            new_role_id = server_ids[new_role_num]
            new_role_name = server_color_list[new_role_num]
            new_role = message.guild.get_role(new_role_id)
            server_colors = []
            for row in records:
                server_colors.append(int(row[0]))
            for role_id in server_colors:
                for user_role in user.roles:
                    if user_role.id == role_id:
                        await user.remove_roles(user_role)
                        break
            await user.add_roles(new_role)
            await send_message(message, "Your color has been set to " + new_role_name)            
        elif command == 'info' or command == 'help':
            response = "This is **The Notorious R.G.B.**, the ultimate color role bot.\n\nThe Notorious RGB allows you to create color roles from either its database or custom color roles with hex codes. RGB will not work with existing color roles on a server, as it is designed to be self-contained.\n\n**To use**:\n\n1. Run `c!addbasecolor` or `c!addcolor` to add color roles to your server and the bot.\n2. Use `c!setcolor` or `c!setrandomcolor` to set your own color or another user's color if you have the permissions.\n\nBot Prefx: `c!`\n\n**Commands**\n\n`c!setcolor COLORNAME @USER`: Set your color. You must have manage role permissions to set anyone else's color.\n`c!colorchart`: Show an image with all the base colors labeled.\n`c!listcolors`: Show all color roles defined on the server.\n`c!addcolor COLORNAME HEXCODE`: Add a color role with the hex code specified to the server. Requires manage role permissions to run.\n`c!listbasecolors`: Show a list of base colors available.\n`c!addbasecolor COLOR1 COLOR2`: Add a list of colors from the base list to your server as roles. Requires maange role permissions.\n`c!deletecolor COLORNAME`: Delete a color role from your server. Requires manage role permissions.\n`c!deleteallcolors`: Delete ALL color roles defined on your server that are in the bot.\n`c!showcolor COLORNAME`: Show a color's hex code that is defined in your server.\n`c!randomcolor @USER`: Give yourself or another user a random color. You must have manage role permissions to assign other users colors."
            await send_message(message, response)  
            
@client.event
async def on_interaction(member, interaction):
    message = NakedObject()

    message.author = member
    message.guild = interaction.guild
    message.mentions = []
    message.content = "c!" + interaction.command.to_dict()['name']
    if interaction.command.options:
        for option in interaction.command.options:
            m = re.search(r"@(?P<user>\d+)", str(option))
            if m:
                message.mentions = []
                message.mentions.append(discord.utils.get(message.guild.members, id=int(m.group('user'))))
            else:
                message.content = message.content + " " + str(option)
                
            
    message.attachments = None
    message.channel = interaction.channel
    print(str(message.content))
    url = "https://discord.com/api/v8/interactions/" + str(interaction.id) + "/" + str(interaction.token) + "/callback"
    json = {
    "type": 4,
    "data": {
        "content": "<@" + str(member.id) + ">"
        }
    }
    r = requests.post(url, json=json)



    #await interact_reply.send_message(content="Success.", ephemeral=True)
    await on_message(message)            
client.run'REDACTED'

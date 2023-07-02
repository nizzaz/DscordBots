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
from slashcommands import SlashCommands

class NakedObject(object):
    pass
    
manager = None
slash_commands = None

webhook = { }
intents = discord.Intents.default()
# intents.members = True
client = discord.Client(heartbeat_timeout=600,intents=intents)
guild_settings = { }
npc_aliases = { }
dm_tracker = { }
dialog_tracker = { }
narrator_url = "https://cdn.discordapp.com/attachments/701796158691082270/703247309613301790/header-brilliant-game-of-thrones-and-princess-bride-mashup-video.jpg"
last_message = {}

dialog_options = {
    1: u'\u0031\ufe0f\u20e3',
    2: u'\u0032\ufe0f\u20e3',
    3: u'\u0033\ufe0f\u20e3',
    4: u'\u0034\ufe0f\u20e3',
    5: u'\u0035\ufe0f\u20e3',
    6: u'\u0036\ufe0f\u20e3',
    7: u'\u0037\ufe0f\u20e3',
    8: u'\u0038\ufe0f\u20e3',
    9: u'\u0039\ufe0f\u20e3'
    
}
reverse_dialog_options = {
    u'\u0031\ufe0f\u20e3': 1,
    u'\u0032\ufe0f\u20e3': 2,
    u'\u0033\ufe0f\u20e3': 3,
    u'\u0034\ufe0f\u20e3': 4,
    u'\u0035\ufe0f\u20e3': 5,
    u'\u0036\ufe0f\u20e3': 6,
    u'\u0037\ufe0f\u20e3': 7,
    u'\u0038\ufe0f\u20e3': 8,
    u'\u0039\ufe0f\u20e3': 9
}


# async def slash_commands(command_name, command_desc, options):
    # global manager
    # print("Command name " + command_name)
# #    command = dsc.Command(command_name, description=command_desc)



    
    # #manager.add_global_command(command) 
    # # code = manager.add_guild_command(918898876663070721,command)

    
    # url = "https://discord.com/api/v10/applications/1015118620126355538/commands"

    # # This is an example USER command, with a type of 2
    # json = {
        # "name": command_name.lower().replace(' ',''),
        # "type": 1,
        # "description": command_desc,
        # "options": []
    # }
    # headers = {
        # "Authorization": "Bot NzAxMDk3NzQwMzM1MTg2MDMz.Xpsi9A.a72vUMcXWK145vyivtz609bCRgw"
    # }    
    # try:
        # options[0]['name']
        
    # except:
        # r = requests.post(url, headers=headers, json=json)
        # print(r)
        # # manager.add_global_command(command) 
        # # code = manager.add_guild_command(918898876663070721,command)
 # #       print(code)
        # return
         
    # for opt in options:
        # print("Adding option " + opt['name'])
        # opt_json = { "name": opt['name'].lower().replace(' ',''),
                     # "description": opt['desc'],
                     # "type": 3,
                     # "required": True,
                     # "choices": []
                    # }
        # json["options"].append(opt_json)



    # r = requests.post(url, headers=headers, json=json)    
    # print(r)
    
    
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='RPCompanion', user='REDACTED', password='REDACTED', charset="utf8mb4")    
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
        connection = mysql.connector.connect(host='localhost', database='RPCompanion', user='REDACTED', password='REDACTED', charset="utf8mb4")
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
        connection = mysql.connector.connect(host='localhost', database='RPCompanion', user='REDACTED', password='REDACTED', charset="utf8mb4")
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

@client.event
async def on_raw_reaction_add(payload):
    global dialog_tracker
    global dialog_options
    global reverse_dialog_options
    server_id = payload.guild_id
    server_obj = client.get_guild(server_id)
    emoji = payload.emoji
    user = payload.member


    message_id = payload.message_id
    
    try:
        dialog_tracker[server_id][user.id]
    except:
        return
    message_channel = client.get_channel(dialog_tracker[server_id][user.id]["channel"])
    if dialog_tracker[server_id][user.id] and message_id == dialog_tracker[server_id][user.id]["CurrentMessage"].id:
        option_chosen = reverse_dialog_options[str(emoji)]
        response_id = dialog_tracker[server_id][user.id]["DialogMap"][option_chosen]
        records = await select_sql("""SELECT Response, ChildDialogs,Reply FROM Dialog WHERE Id=%s AND ServerId=%s;""",(str(response_id),str(server_id)))
        if not records:
            await post_webhook(await post_webhook(dialog_tracker[server_id][user.id]["channel"], dialog_tracker[server_id][user.id]["CharacterName"], "I didn't understand you.", dialog_tracker[server_id][user.id]["PictureLink"]))
            return
        dialog_tracker[server_id][user.id]["CurrentDialogId"] = str(response_id)
        for row in records:
            dialog_tracker[server_id][user.id]["RootDialogList"] = row[1].split(',')
            response = row[0]
            reply = row[2]
        dialog_menu = '> "' +  reply +'"' + "\n\n```"
        counter = 1
        if dialog_tracker[server_id][user.id]["RootDialogList"][0] == '0':
            await post_webhook(dialog_tracker[server_id][user.id]["channel"], dialog_tracker[server_id][user.id]["CharacterName"], "I have nothing else to say! (Conversation ended)", dialog_tracker[server_id][user.id]["PictureLink"])
            del dialog_tracker[server_id][user.id]
            return
        for dialog_id in dialog_tracker[server_id][user.id]["RootDialogList"]:
            records = await select_sql("""SELECT Response,RoleRequiredId FROM Dialog WHERE Id=%s;""",(str(dialog_id),))
            for row in records:
                role_required = discord.utils.get(server_obj.roles,id=int(row[1]))
                role_found = False
                for role in user.roles:
                    if role == role_required or role_required is None:
                        role_found = True
                if not role_found:
                    dialog_tracker[server_id][user.id]["RootDialogList"].remove(dialog_id)
                    continue            
                dialog_menu = dialog_menu + str(dialog_options[counter]) + " - " + row[0] + "\n"
                dialog_tracker[server_id][user.id]["DialogMap"][counter] = dialog_id
                counter = counter + 1
        
        dialog_tracker[server_id][user.id]["CurrentMessage"] = await post_webhook(dialog_tracker[server_id][user.id]["channel"], dialog_tracker[server_id][user.id]["CharacterName"], dialog_menu + "```", dialog_tracker[server_id][user.id]["PictureLink"])
        counter = 1
        dialog_tracker[server_id][user.id]["RootDialogList"] = list(filter(None,dialog_tracker[server_id][user.id]["RootDialogList"]))        
        for dialog_id in dialog_tracker[server_id][user.id]["RootDialogList"]:
            await dialog_tracker[server_id][user.id]["CurrentMessage"].add_reaction(dialog_options[counter])
            if counter > len(dialog_tracker[server_id][user.id]["RootDialogList"]) - 1:
                break
            counter = counter + 1            
        return        


        
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
    temp_webhook = await channel.create_webhook(name='RPCompanion')
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
    global slash_commands

    
    
        
    commands = [{"name": 'getcharprofile', 'desc': 'Get a specific character\'s profile.', 'options': [{'name': 'charname', 'desc': 'The name of the character'},]},
    {"name": 'resetserver', 'desc': 'Clear all server settings, character profiles, and NPCs.', 'options': [{}]},
    {"name": 'info', 'desc': 'Bot help.', 'options': [{'name': 'Category', 'desc': 'Category of help.'}]},
    {"name": 'help', 'desc': 'Bot help.', 'options': [{'name': 'Category', 'desc': 'Category of help.'}]},
    {"name": 'approvechar', 'desc': 'Approve a new character.', 'options': [{}]},
    {"name":  'newrootdialog',  'desc': 'Add a new root dialog.', 'options': [{}]},
    {"name":  'denychar',  'desc': 'Deny a new character and discard it.', 'options': [{}]},
    {"name":  'newrandomchar',  'desc': 'Create a randomized character for approval.', 'options': [{}]},
    {"name":  'changecharowner',  'desc': 'Change a character\'s owner.', 'options': [{}]},
    {"name":  'newchar',  'desc': 'Create a new character.', 'options': [{}]},
    {"name":  'newdialogchar',  'desc': 'Create a new character for dialog.', 'options': [{}]},
    {"name":  'newnpc',  'desc': 'Create a new NPC.', 'options': [{'name': 'AllowedUsers', 'desc': 'User mentions for users allowed to post as the NPC.'}]},
    {"name":  'editnpc',  'desc': 'Edit an existing NPC.', 'options': [{'name': 'AllowedUsers', 'desc': 'User mentions for users allowed to post as the NPC.'}]},
    {"name":  'editdialogchar',  'desc': 'Edit an existing dialog character.', 'options': [{'name': 'charname', 'desc': 'Name of the character to edit.'}]},
    {"name":  'editsetup',  'desc': 'Edit the server setup.', 'options': [{}]},
    {"name":  'editchar',  'desc': 'Edit an existing character.', 'options': [{'name': 'charname', 'desc': 'Name of the character to edit.'}]},
    {"name":  'editcharinfo',  'desc': 'Edit additional character information.', 'options': [{}]},
    {"name":  'createroles',  'desc': 'Automatically create the roles needed for the bot.', 'options': [{}]},
    {"name":  'setadminrole',  'desc': 'Set the administrator role.', 'options': [{'name': 'role', 'desc': 'Role mention for admin role.'}]},
    {"name":  'listunapprovedchars',  'desc': 'List unapproved characters on this server.', 'options': [{}]},
    {"name":  'roll',  'desc': 'Roll a die or dice.', 'options': [{'name': 'dicestring', 'desc': 'String of the dice to roll.'}]},
    {"name":  'listallchars',  'desc': 'List all characters on the server.', 'options': [{}]},
    {"name":  'listuserchars',  'desc': 'List a particular user\'s characters.', 'options': [{'name': 'User', 'desc': 'User mention of characters to list for..'}]},
    {"name":  'listdialogchars',  'desc': 'List all dialog characters on the server.', 'options': [{}]},
    {"name":  "listdialogchar",  'desc': 'List details for a specific dialog character.', 'options': [{'name': 'charname', 'desc': 'Name of the character to show details for.'}]},
    {"name":  'listalldialogs',  'desc': 'List all dialogs for the server.', 'options': [{}]},
    {"name":  'deletedialogchar',  'desc': 'Delete a dialog character.', 'options': [{'name': 'charname', 'desc': 'Name of the character to delete.'}]},
    {"name":  'deletedialog',  'desc': 'Delete a dialog from the server.', 'options': [{'name': 'DialogID', 'desc': 'ID of dialog to delete.'}]},
    {"name":  'getcharprofile',  'desc': 'Get a character\'s profile.', 'options': [{'name': 'charname', 'desc': 'Name of the character to view.'}]},
    {"name":  'listmychars',  'desc': 'List your characters.', 'options': [{}]},
    {"name":  'deletechar',  'desc': 'Delete a character.', 'options': [{'name': 'charname', 'desc': 'Name of the character to delete.'}]},
    {"name":  'deletecustomprofile',  'desc': 'Remove all custom profiles from the server.', 'options': [{}]},
    {"name":  'setnpc',  'desc': 'Set yourself as an NPC in this channel.', 'options': [{'name': 'Shortcut', 'desc': 'Shortcut for NPC to post as.'}]},
    {"name":  'unsetnpc',  'desc': 'Remove the NPC from yourself in this channel.', 'options': [{}]},
    {"name":  'unpause',  'desc': 'Post a scene unpause.', 'options': [{}]},
    {"name":  'newscene',  'desc': 'Post a new scene divider.', 'options': [{}]},
    {"name":  'endscene',  'desc': 'Post an end scene divider.', 'options': [{}]},
    {"name": 'postnarr',  'desc': 'Post as the narrator.', 'options': [{}]},
    {"name":  'postnpc',  'desc': 'Post as an NPC.', 'options': [{'name': 'Shortcut', 'desc': 'Shortcut for NPC to post as.'},{'name': 'Text', 'desc': 'Text of post.'}]},
    {"name":  'editnpcpost',  'desc': 'Edit a previous NPC\'s post.', 'options': [{}]},
    {"name":  'deletenpc',  'desc': 'Delete an NPC from the server.', 'options': [{'name': 'npcname', 'desc': 'Name of the NPC to delete.'}]},
    {"name":  'lurk',  'desc': 'Post a random lurk message.', 'options': [{}]},
    {"name":  'ooc',  'desc': 'Post a message in OOC brackets.', 'options': [{'name': 'Text', 'desc': 'Text of post.'}]},
    {"name":  'me',  'desc': 'Post a message as yourself in OOC brackets.', 'options': [{'name': 'Text', 'desc': 'Text of post.'}]},
    {"name":  'endconvo',  'desc': 'End a dialog conversation.', 'options': [{}]},
    {"name":  'converse',  'desc': 'Begin a dialog conversation.', 'options': [{}]},
    {"name":  'randomooc',  'desc': 'Do a random OOC action to a mentioned user.', 'options': [{}]},
    {"name":  'setnpcrole',  'desc': 'Set the NPC role.', 'options': [{'name': 'role', 'desc': 'Role mention for NPC role.'}]},
    {"name":  'listroles',  'desc': 'List the current roles.', 'options': [{}]},
    {"name":  'listsetup',  'desc': 'List the current setup.', 'options': [{}]},
    {"name":  'addnpcuser',  'desc': 'Add a user to the NPC role.', 'options': [{'name': 'User', 'desc': 'User mention.'}]},
    {"name":  'addadmin',  'desc': 'Add a user to the admin role.', 'options': [{'name': 'User', 'desc': 'User mention.'}]},
    {"name":  'deletenpcuser',  'desc': 'Remove a user from the NPC role.', 'options': [{'name': 'User', 'desc': 'User mention.'}]},
    {"name":  'deleteadmin',  'desc': 'Remove a user from the admin role.', 'options': [{'name': 'User', 'desc': 'User mention.'}]},
    {"name":  'listnpcs',  'desc': 'List all NPCs on the server.', 'options': [{}]},
    {"name":  'newcustomprofile',  'desc': 'Create a new custom profile.', 'options': [{'name': "profilestring", "desc": "See the help."}]},
    {"name":  'invite',  'desc': 'Show an invite link.', 'options': [{}]}]
    slash_commands = SlashCommands(client)
    # for command in commands:
        # slash_commands.new_slash_command(name=command["name"].lower(), description=command["desc"])
        # for option in command["options"]:
            # try:
                # option["name"]
            # except:
                # continue
            # print(str(option))
            # if command["name"] == 'setadminrole' or command["name"] == 'setnpcrole':
                # slash_commands.add_role_command_option(command_name=command["name"].lower(), option_name=option["name"].lower(), description=option["desc"], required=True)
            # elif command["name"] == 'newnpc' or command["name"] == "editnpc" or command["name"] == 'listuserchars' or command["name"] == 'addadmin' or command['name'] == 'deleteadmin' or command['name'] == 'addnpcuser' or command['name'] == 'deletenpcuser':
                # slash_commands.add_user_command_option(command_name=command["name"].lower(), option_name=option["name"].lower(), description=option["desc"], required=True)
            # else:
                # slash_commands.add_command_option(command_name=command["name"].lower(), option_name=option["name"].lower(), description=option["desc"], required=True)
        # slash_commands.add_global_slash_command(command_name=command["name"].lower())

        
                
        # await asyncio.sleep(10)
            
    await log_message("Logged in!")
    print("Bot startup.")
    for guild in client.guilds:
        guild_settings[guild.id]  =  {}
        dialog_tracker[guild.id] = {}
        last_message[guild.id] = {}
        try: npc_aliases[guild.id]
        except: npc_aliases[guild.id] = {}
    print("Done with Guilds.")
       # for user in guild.members:
           # try: npc_aliases[guiild.id][user.id]
           # except: npc_aliases[guild.id][user.id] = {}
           # for channel in guild.text_channels:
               # try: npc_aliases[guild.id][user.id][channel.id]
               # except: npc_aliases[guild.id][user.id][channel.id] = ""
    # GMRole,NPCRole,NPCRole,GuildBankBalance,StartingHealth,StartingMana,StartingStamina,StartingAttack,StartingDefense,StartingMagicAttack,StartingAgility,StartingIntellect,StartingCharisma,HealthLevelRatio,ManaLevelRatio,StaminaLevelRatio,XPLevelRatio,HealthAutoHeal,ManaAutoHeal,StaminaAutoHeal
    # ALTER TABLE GuildSettings ADD COLUMN StartingHealth Int, StartingMana Int, StartingStamina Int, StartingAttack Int, StartingDefense Int, StartingMagicAttack Int, StartingAgility Int, StartingIntellect Int, StartingCharisma Int, HealthLevelRatio Int, ManaLevelRatio Int, StaminaLevelRatio Int, XPLevelRatio Int, HealthAutoHeal DECIMAL(1,2), ManaAutoHeal DECIMAL (1,2), StaminaAutoHeal DECIMAL(1,2);
    records = await select_sql("""SELECT ServerId,IFNULL(AdminRole,'0'),IFNULL(NPCRole,'0') FROM GuildSettings;""")
    if records:
        for row in records:
            server_id = int(row[0])
            guild_settings[server_id] = {} 
            if row[1] is not None:        
                guild_settings[server_id]["AdminRole"] = int(row[1])    
            if row[2] is not None:   
                guild_settings[server_id]["NPCRole"] = int(row[2])
    await log_message("All SQL loaded for guilds.")
            
            
@client.event
async def on_guild_join(guild):
    global guild_settings
    global npc_aliases
    global dialog_tracker
    global last_message

    
    await log_message("Joined guild " + guild.name)
    guild_settings[guild.id] = {}
    npc_aliases[guild.id] = { }
    dialog_tracker[guild.id] = {} 
    for user in guild.members:
        npc_aliases[guild.id][user.id] = { }
        for channel in guild.text_channels:
                npc_aliases[guild.id][user.id][channel.id] = ""
        last_message[guild.id] = {}
    await commit_sql("""DELETE FROM GuildSettings WHERE ServerId=%s;""",(str(guild.id),))
    await commit_sql("""INSERT INTO GuildSettings (ServerId,AdminRole,NPCRole) VALUES (%s,'0','0');""",(str(guild.id),))
    
@client.event
async def on_guild_remove(guild):
    if not guild.name:
        return
    await log_message("Left guild " + guild.name)
    
@client.event
async def on_message(message):
    global webhook
    global guild_settings
    global npc_aliases
    global dm_tracker
    global narrator_url
    global dialog_tracker
    global dialog_options
    global last_message
    
    
    if message.author.bot and message.author.id != 787355055333965844:
        return
    if message.author == client.user:
        return
    try:
        npc_aliases[message.guild.id]
    except: 
        try: 
            message.guild.id
            npc_aliases[message.guild.id] = {} 
        except: pass
        
    try:
        npc_aliases[message.guild.id][message.author.id]
    
    except: 
        try: 
            message.guild.id
            npc_aliases[message.guild.id][message.author.id] = { }
        
        except:
            pass

    try:
        npc_aliases[message.guild.id][message.author.id][message.channel.id]
    except:        
        try: 
            message.guild.id
            npc_aliases[message.guild.id][message.author.id][message.channel.id] = None
        except:
            pass
         

    
    das_server = message.guild
    if message.content.startswith('//answer'):
        das_server = None
        message.content = message.content.replace('//answer ','')
 
       
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
        elif (message.content == 'skip' or message.content == 'Skip') and current_field < len(field_list) and current_command != 'newrootdialog':
            dm_tracker[message.author.id]["currentfield"] = dm_tracker[message.author.id]["currentfield"] + 1
            if current_field < len(field_list) - 1:
                await direct_message(message, "Skipping field **"  + field_list[current_field] + "** and not changing its value. The next field is **" + dm_tracker[message.author.id]["fieldlist"][current_field + 1] + "** and its value is **" + str(dm_tracker[message.author.id]["fielddict"][current_field + 1]) + "**. Reply with the new value or *skip* to leave the current value.")
                
                return
            else:
                await direct_message(message, "Skipping field **"  + dm_tracker[message.author.id]["fieldlist"][current_field] + "**. That was the last field. Reply *end* to commit to the database.")
                
            return
            

        elif current_command.startswith('edit') and current_field < len(field_list):
            dm_tracker[message.author.id]["fielddict"][current_field] = message.content.strip()
            dm_tracker[message.author.id]["currentfield"] = current_field + 1
            if current_field < len(field_list) - 1:
                await direct_message(message, "Setting field **"  + dm_tracker[message.author.id]["fieldlist"][current_field] + "** to **" + message.content.strip() + "**. The next field is **" + dm_tracker[message.author.id]["fieldlist"][current_field + 1] + "** and its value is **" + str(dm_tracker[message.author.id]["fielddict"][current_field + 1]) + "**. Reply with the new value or *skip* to leave the current value.")
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
                for x in range(1,10):
                    delete_tuple = delete_tuple + (str(dm_tracker[message.author.id]["server_id"]),)
                result = await commit_sql("""DELETE FROM CharacterProfiles WHERE ServerId=%s; DELETE FROM Vendors WHERE ServerId=%s; DELETE FROM Spells WHERE ServerId=%s; DELETE FROM Melee WHERE ServerId-%s; DELETE FROM Inventory WHERE ServerId-%s; DELETE FROM Equipment WHERE ServerId=%s; DELETE FROM MagicSkills WHERE ServerId=%s; DELETE FROM MeleeSkills WHERE ServerId=%s; DELETE FROM Monsters WHERE ServerId=%s; DELETE FROM GuildSettings WHERE ServerId=%s;""", delete_tuple)
                await dm_tracker[message.author.id]["commandchannel"].send(">>> Server reset complete! Please run //setadminrole @adminrole.")
                return


        elif current_command == 'approvechar':
            unapproved_char_id = message.content
            records = await select_sql("""SELECT CharacterName,UserId FROM UnapprovedCharacterProfiles WHERE Id=%s""", (message.content,))
            for row in records:
                char_name = row[0]
                char_user_id = row[1]
            # Copy to Character profiles
            records = await select_sql("""SELECT ServerId,UserId,CharacterName,Age,Race,Gender,Height,Weight,Playedby,Origin,Occupation,PictureLink FROM UnapprovedCharacterProfiles WHERE Id=%s;""", (message.content,))
            insert_statement = """INSERT INTO CharacterProfiles (ServerId,UserId,CharacterName,Age,Race,Gender,Height,Weight,Playedby,Origin,Occupation,PictureLink) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            insert_tuple = ()
            for row in records:
                for item in row:
                    insert_tuple = insert_tuple + (item,)
            result = await commit_sql(insert_statement, insert_tuple)        
#            result = await commit_sql("""INSERT INTO CharacterProfiles (SELECT * FROM UnapprovedCharacterProfiles WHERE Id=%s);""", (message.content,))
            if result:
                await dm_tracker[message.author.id]["commandchannel"].send(">>> <@" + char_user_id + ">, your character is approved! You may now play as " + char_name + ".")
            else:
                await direct_message(message, "Database error!")
                return
            result = await commit_sql("""DELETE FROM UnapprovedCharacterProfiles WHERE Id=%s;""", (message.content,))
            if result:
                await direct_message(message, "Character confirmed deletion and moved to approved characters list. User will be notiified of the approval.")
                deleted = True
            else:
                await direct_message(message, "Database error!")
              
            return
        elif current_command == 'newsubdialog':
            if current_field == 0:
                dm_tracker[message.author.id]["fielddict"].append(message.content)
                current_guild = client.get_guild(int(dm_tracker[message.author.id]["server_id"]))
                roles = ""
                for role in current_guild.roles:
                    roles = roles + role.name + "\n"
                await direct_message(message, "Please select a role from the below by name that can see this dialog, or None for any role.\n\n" + roles)
                dm_tracker[message.author.id]["currentfield"] = 1
                return                
            elif current_field == 1:
                current_guild = client.get_guild(int(dm_tracker[message.author.id]["server_id"]))
                role_id = None
                role_found = False
                for role in current_guild.roles:
                    if role.name == message.content:
                        role_id = role.id
                        role_found = True
                if not role_found and message.content != 'None':
                    await direct_message(message, "This role doesn't exist on this server! Please pick an existing role!")
                    return
                if role_id is None and message.content == 'None':
                    role_id = '0'
                dm_tracker[message.author.id]["fielddict"].append(role_id)
                dm_tracker[message.author.id]["currentfield"] = 2
                await direct_message(message, "Please enter the subdialog text.")
                return
            elif current_field == 2:
                dm_tracker[message.author.id]["fielddict"].append(message.content)
                dm_tracker[message.author.id]["currentfield"] = 3
                await direct_message(message, "Enter the reply prompt at the beginning of the dialog below:")
                return                
            elif current_field == 3:
                dm_tracker[message.author.id]["fielddict"].append(message.content)
                records = await select_sql("""SELECT CharacterId FROM Dialog WHERE Id=%s;""",(str(field_dict[0]),))
                for row in records:
                    char_id = row[0]
                    
                result = await commit_sql("""INSERT INTO Dialog (ServerId,UserId,RoleRequiredId,CharacterId,Response,RootId,ChildDialogs,Reply) VALUES (%s,%s,%s,%s,%s,%s,'0',%s);""",(str(dm_tracker[message.author.id]["server_id"]),str(message.author.id),str(field_dict[1]),str(char_id),str(field_dict[2]),str(field_dict[0]),message.content))
                
                records = await select_sql("""SELECT Id FROM Dialog WHERE ServerId=%s AND Response=%s;""",(str(dm_tracker[message.author.id]["server_id"]),str(field_dict[2])))
                for row in records:
                    new_id = row[0]
                
                records = await select_sql("""SELECT ChildDialogs FROM Dialog WHERE Id=%s;""",(str(field_dict[0]),))
                for row in records:
                    parent_dialog_list = row[0]
                
                if parent_dialog_list == '0':
                    parent_dialog_list = str(new_id)
                else:
                    parent_dialog_list = parent_dialog_list + "," + str(new_id) + ","
                    
                result = await commit_sql("""UPDATE Dialog SET ChildDialogs=%s WHERE Id=%s;""",(str(parent_dialog_list),str(field_dict[0])))
                if result:
                    await direct_message(message, "Subdialog added successfully.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Subdialog added successfully.")
                else:
                    await direct_message(message, "Database error!")
                return
                
        elif current_command == 'newrootdialog':
            if current_field == 0:
                dm_tracker[message.author.id]["fielddict"].append(message.content)
                current_guild = client.get_guild(int(dm_tracker[message.author.id]["server_id"]))
                roles = ""
                for role in current_guild.roles:
                    roles = roles + role.name + "\n"
                await direct_message(message, "Please select a role from the below by name that can see this dialog, or None for any role.\n\n" + roles)
                dm_tracker[message.author.id]["currentfield"] = 1
                return
            elif current_field == 1:
                current_guild = client.get_guild(int(dm_tracker[message.author.id]["server_id"]))
                role_id = None
                role_found = False
                for role in current_guild.roles:
                    if role.name == message.content:
                        role_id = role.id
                        role_found = True
                if not role_found and message.content != 'None':
                    await direct_message(message, "This role doesn't exist on this server! Please pick an existing role!")
                    return
                if role_id is None or message.content == 'None':
                    role_id = '0'
                dm_tracker[message.author.id]["fielddict"].append(role_id)
                dm_tracker[message.author.id]["currentfield"] = 2
                await direct_message(message, "Please enter the root dialog text.")
                return
            elif current_field == 2:
                dm_tracker[message.author.id]["fielddict"].append(message.content)
                dm_tracker[message.author.id]["currentfield"] = 3
                await direct_message(message, "Enter the reply prompt at the beginning of the dialog below:")
                return
            elif current_field == 3:
                result = await commit_sql("""INSERT INTO Dialog (ServerId,UserId,RoleRequiredId,CharacterId,Response,RootId,ChildDialogs,Reply) VALUES (%s,%s,%s,%s,%s,'0','0',%s);""",(str(dm_tracker[message.author.id]["server_id"]),str(message.author.id),str(field_dict[1]),str(field_dict[0]),str(field_dict[2]),message.content))
                
                records = await select_sql("""SELECT Id FROM Dialog WHERE ServerId=%s AND Response=%s;""",(str(dm_tracker[message.author.id]["server_id"]),str(field_dict[2])))
                for row in records:
                    new_id = row[0]
                records = await select_sql("""SELECT RootDialogList FROM DialogCharacters WHERE Id=%s;""",(str(field_dict[0]),))
                root_list = ""
                if not records:
                    root_list = str(new_id)
                else:
                    for row in records:
                        if row[0] is not None and row[0] != 'None':
                            root_list = row[0] + "," + str(new_id) + ","                
                        else:
                            root_list = str(new_id)
                result = await commit_sql("""UPDATE DialogCharacters SET RootDialogList=%s WHERE Id=%s;""",(str(root_list),str(field_dict[0])))
                if result:
                    await direct_message(message, "Root dialog successfully added.")          
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Root dialog successfully added.")
                else:
                    await direct_message(message, "Database error!")
                return            
        elif current_command == 'denychar':
            if current_field == 0:
                dm_tracker[message.author.id]["fielddict"].append(message.content)
                await direct_message(message, "Enter a reason why this character is declined. Please specify what needs to be changed to approve it, and if nothing can be changed, why it was deleted.")
                dm_tracker[message.author.id]["currentfield"] = 1
                return
            if current_field == 1:
                dm_tracker[message.author.id]["fielddict"].append(message.content)
                await direct_message(message, "Please type **DELETE** in reply to this message if the character profile will be deleted from the unapproved character list.")
                dm_tracker[message.author.id]["currentfield"] = 2
                return
            if current_field == 2:
                records = await select_sql("""SELECT UserId,CharacterName FROM UnapprovedCharacterProfiles WHERE Id=%s;""",(dm_tracker[message.author.id]["fielddict"][0],))
                for row in records:
                    user_id = row[0]
                    char_name = row[1]
                    
                if message.content == 'DELETE':
                    result = await commit_sql("""DELETE FROM UnapprovedCharacterProfiles WHERE Id=%s;""", (dm_tracker[message.author.id]["fielddict"][0],))
                    if result:
                        await direct_message(message, "Character confirmed deletion and not moved to approved characters list. User will be notiified of the decline and reason.")
                        deleted = True
                    else:
                        await direct_message(message, "Database error!")
                        return
                else:
                    deleted = False
                response = "Your character was declined. The reason given was:\n```" + dm_tracker[message.author.id]["fielddict"][1] + "```"
                if deleted:
                    response = response + "\n\nThe character was also deleted from unapproved profiles for the above reason. Please create a new application that fits the server rules.\n"
                user_obj = client.get_user(int(user_id))
                channel = await user_obj.create_dm()
                await channel.send(">>> " + response)
                await dm_tracker[message.author.id]["commandchannel"].send(">>> " + char_name + " was declined. <@" + str(user_id) + ">, please check your DMs for the reason.")
                return
                    

        elif current_command == 'newrandomchar':
            if message.content == 'YES':

                result = await insert_into(message, "UnapprovedCharacterProfiles")

                if result:
                    await direct_message(message,
                                         "Character application for " + field_dict[0] + " created successfully.")
                    await dm_tracker[message.author.id]["commandchannel"].send(
                        ">>> Character application for  " + field_dict[
                            0] + " successfully created.\n\nAfter approval, you may edit any character fields with =change.\n\n<@&" + str(
                            guild_settings[dm_tracker[message.author.id]["server_id"]][
                                "AdminRole"]) + ">, please approve or decline the character with //approvechar or //denychar.")
                else:
                    await direct_message(message, "Database error!")

            else:
                await direct_message(message, "Character discarded.")
            await initialize_dm(message.author.id)
            return 
 
        elif current_command == 'changecharowner':
            if current_field == 0:
                dm_tracker[message.author.id]["fielddict"].append(message.content)

                await direct_message(message, "Please enter the user ID of the new player to change the owner to below:\n\n" + menu)
                dm_tracker[message.author.id]["currentfield"] = 1
                return
            if current_field == 1:
                result = await commit_sql("""UPDATE CharacterProfiles SET UserId=%s WHERE Id=%s;""",(message.content, field_dict[0]))
                if result:
                    await direct_message(message, "Character owner updated.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Character ID " + field_dict[0] + " updated to be owned by <@" + message.content + ">")
                else:
                    await direct_message("Database error!")
            
 

            
        dm_tracker[message.author.id]["fielddict"].append(message.content.strip())
        dm_tracker[message.author.id]["currentfield"] = dm_tracker[message.author.id]["currentfield"] + 1
        
        if dm_tracker[message.author.id]["currentfield"] < len(field_list) and current_command !='newrootdialog':
            if dm_tracker[message.author.id]["currentcommand"] != 'newcustomchar':
                await direct_message(message, "Reply received. Next field is " + "**" + dm_tracker[message.author.id]["fieldlist"][dm_tracker[message.author.id]["currentfield"]] + "**.")
            else:
                await direct_message(message, "Reply received. Next field is " + "**" + dm_tracker[message.author.id]["parameters"][dm_tracker[message.author.id]["currentfield"]] + "**.")                
        if (current_field > len(field_list) - 2 and current_command !='newrandomchar'):
            if current_command == 'newcustomchar':
                new_custom_profile = """INSERT INTO Server""" + str(dm_tracker[message.author.id]["server_id"]) + """ (UserId, """
                create_values = """ VALUES (%s, """
                create_tuple = (str(message.author.id),)
                counter = 0
                for key in field_list:
                    new_custom_profile = new_custom_profile + key + """, """
                    create_values = create_values + """%s, """
                    create_tuple = create_tuple + (field_dict[counter],)
                    counter = counter + 1
             #   create_values = create_values + """%s, """
             #   create_tuple = create_tuple + (message.content,)
            #    new_custom_profile = new_custom_profile + field_list[-1] + """, """
                new_custom_profile = re.sub(r"(?:,\s*)*$", "", new_custom_profile) + ")" + re.sub(r", $", "", create_values) + """);"""
                
                await log_message("SQL: " + new_custom_profile)
                result = await commit_sql(new_custom_profile, create_tuple)
                if result:
                    await direct_message(message, "Custom character created successfully!")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Custom character successfully created.")
                else:
                    await direct_message(message, "Database error!")

      
            elif current_command == 'newdefaultchar':
                char_name = field_dict[0]
                if message.attachments:
                    field_dict[len(field_dict) -1] = message.attachments[0].url
                
                create_char_entry = "INSERT INTO UnapprovedCharacterProfiles (ServerId, UserId, "
                create_value = "VALUES (%s, %s, "
                char_tuple = (str(server_id), str(message.author.id),)
                counter = 0
                for field in field_list:
                    create_char_entry = create_char_entry + field + ", "
                    char_tuple = char_tuple + (field_dict[counter],)
                    create_value = create_value + "%s, "
                    counter = counter + 1
                    if counter > len(dm_tracker[message.author.id]["fieldlist"]) - 1:
                        break
                        
                create_char_entry = re.sub(r", $","", create_char_entry)
                create_value = re.sub(r", $","", create_value)
                create_char_entry = create_char_entry + ") " +  create_value +  ");"

                await log_message("SQL: " + create_char_entry)
              
                
                result = await commit_sql(create_char_entry, char_tuple)
                if result:
                    await direct_message(message, "Character " + char_name + " successfully created.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Character " + char_name + " successfully created.\n\n<@&" + str(guild_settings[dm_tracker[message.author.id]["server_id"]]["AdminRole"]) + ">, please approve or decline the character with //approvechar or //denychar.")
                else:
                    await direct_message(message, "Database error!")
                    
            elif current_command == 'newdialogchar':
                if message.attachments:
                    field_dict[len(field_dict) -1 ] = message.attachments[0].url
                else:
                    field_dict[len(field_dict) - 1] = message.content
                
                result = await insert_into(message, "DialogCharacters")
                if result:
                    await direct_message(message, "Dialog character " + field_dict[0] + " successfully created.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Dialog character " + field_dict[0] + " successfully created.")
                else:
                    await direct_message(message, "Database error!") 

            elif current_command == 'newnpc':
                if message.attachments:
                    field_dict[len(field_dict) -1 ] = message.attachments[0].url 
                field_dict.append(str(dm_tracker[message.author.id]["parameters"]))
                field_list.append("UsersAllowed")
                result = await insert_into(message, "NonPlayerCharacters")
                if result:
                    await direct_message(message, "NPC " + field_dict[0] + " successfully created.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> NPC " + field_dict[0] + " successfully created.")
                else:
                    await direct_message(message, "Database error!")
           
            elif current_command == 'editnpc':
                try: field_dict.remove('skip')
                except: pass
                try: field_dict.remove('Skip')
                except: pass
                try: field_dict.remove('end')
                except: pass
                
                if message.attachments:
                     dm_tracker[message.author.id]["fielddict"][len(field_dict) -1 ] = message.attachments[0].url
                elif message.content != 'end' and message.content != 'skip':
                    dm_tracker[message.author.id]["fielddict"][-1] = message.content
                else:
                    pass
                dm_tracker[message.author.id]["fielddict"].append(str(dm_tracker[message.author.id]["parameters"]))
                dm_tracker[message.author.id]["fieldlist"].append("UsersAllowed")
                dm_tracker[message.author.id]["parameters"] = dm_tracker[message.author.id]["parameters2"]                
                result = await update_table(message, "NonPlayerCharacters")
                if result:
                    await direct_message(message, "NPC " + field_dict[0] + " successfully edited.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> NPC " + field_dict[0] + " successfully edited.")
                else:
                    await direct_message(message, "Database error!")
            elif current_command == 'editdialogchar':
                try: field_dict.remove('skip')
                except: pass
                try: field_dict.remove('Skip')
                except: pass
                try: field_dict.remove('end')
                except: pass
                try: field_dict.remove('end')
                except: pass                
                if message.attachments:
                     dm_tracker[message.author.id]["fielddict"][len(field_dict) -1 ] = message.attachments[0].url
                else:
                    dm_tracker[message.author.id]["fielddict"][-1] = message.content
               
                result = await update_table(message, "DialogCharacters")
                if result:
                    await direct_message(message, "Dialog character " + field_dict[0] + " successfully edited.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Dialog character " + field_dict[0] + " successfully edited.")
                else:
                    await direct_message(message, "Database error!")                    
            elif current_command == 'editsetup':
                records = await select_sql("""SELECT ServerId FROM GuildSettings WHERE ServerId=%s;""",(str(dm_tracker[message.author.id]["server_id"]),))
                if not records:
                    result = await commit_sql("""INSERT INTO GuildSettings (ServerId) VALUES (%s);""",(str(dm_tracker[message.author.id]["server_id"]),))
                    if not result:
                        await direct_message(message, "Database error!")
                        return
                result = await update_table(message, "GuildSettings")
                if result:
                    await direct_message(message, "Guild settings successfully edited.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Guild settings successfully edited.")
                else:
                    await direct_message(message, "Database error!")
                return               
            elif current_command == 'editchar':
                if message.attachments:
                    field_dict[len(field_dict)] = message.attachments[0].url
                result = await update_table(message, "CharacterProfiles")
                if result:
                    await direct_message(message, "Character " + field_dict[0] + " successfully edited.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Character " + field_dict[0] + " successfully edited.")
                else:
                    await direct_message(message, "Database error!")
            elif current_command == 'editcustomchar':
                if message.attachments:
                    field_dict.append(message.attachments[0].url)
                else:
                    field_dict.append(message.content)
                result = await update_table(message, "Server" + str(dm_tracker[message.author.id]["server_id"]))
                if result:
                    await direct_message(message, "Character " + field_dict[0] + " successfully edited.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Character " + field_dict[0] + " successfully edited.")
                else:
                    await direct_message(message, "Database error!")                    
            elif current_command == 'editcharinfo':
                result = await update_table(message, "CharacterProfiles")
                if result:
                    await direct_message(message, "Character " + field_dict[0] + " successfully edited.")
                    await dm_tracker[message.author.id]["commandchannel"].send(">>> Character " + field_dict[0] + " successfully edited.")
                else:
                    await direct_message(message, "Database error!")                    
 
            await initialize_dm(message.author.id)        
        else:
            pass
        return
        
    elif npc_aliases[message.guild.id][message.author.id][message.channel.id] and not message.content.startswith('//'):
            get_npc = """SELECT UsersAllowed, CharName, PictureLink FROM NonPlayerCharacters WHERE ServerId=%s AND Shortcut=%s;"""
            npc_tuple = (str(message.guild.id), npc_aliases[message.guild.id][message.author.id][message.channel.id])
            records = await select_sql(get_npc, npc_tuple)
            for row in records:
                if str(message.author.id) not in row[0]:
                    await reply_message(message, "<@" + str(message.author.id) + "> is not allowed to use NPC " + row[1] + "!")
                    return
                response = message.content
                # current_pfp = await client.user.avatar_url.read()
                

                current_name = message.guild.me.name
                URL = row[2]
                temp_webhook = await message.channel.create_webhook(name='RPCompanion')
                await temp_webhook.send(content=response, username=row[1], avatar_url=URL)
               # await message.delete()
                await temp_webhook.delete()

    if message.content.startswith('//') or message.mentions:

            
        command_string = message.content.split(' ')
        if message.mentions:
            if message.mentions[0] != client.user and not message.content.startswith('//'):
                return
            if message.mentions[0].id == 701097740335186033:

                command_string = re.sub(r'<@701097740335186033>','',message.content).split(' ')
                del command_string[0]
                print(str(command_string))
        if command_string == message.content:
            command = command_string.replace('//','')
        else:
            command = command_string[0].replace('//','')
        command = command.strip()

        parsed_string = message.content.replace("//" + command + " ","").replace('<@701097740335186033>','').strip()
        # try: 
            # re.search(command, parsed_string)
            # parsed_string = ""        
        # except:
            # pass
        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string)
        
        
        if command == 'createroles':
            roles=["RPAdministrator","NPCUser",]
            
            for role in roles:
                try:
                    new_role = await message.guild.create_role(name=role)
                    if role == "RPAdministrator":
                        result = await commit_sql("""UPDATE GuildSettings SET AdminRole=%s WHERE ServerId=%s;""",(str(new_role.id),str(message.guild.id)))
                        guild_settings[message.guild.id]["AdminRole"] = new_role.id
                    if role == "NPCUser":
                        result = await commit_sql("""UPDATE GuildSettings SET NPCRole=%s WHERE ServerId=%s;""",(str(new_role.id),str(message.guild.id)))
                        guild_settings[message.guild.id]["NPCRole"] = new_role.id                    
                except discord.errors.Forbidden:
                    await reply_message(message, "Cannot create roles due to permissions!")
                    return
                    
            await reply_message(message, "Roles created!")        
        elif command == 'setadminrole':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "Only a user with manage server permissions can set the admin role!")
                return
            if not message.role_mentions:
                await reply_message(message, "You did not specify a role!")
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
        if command == 'help' or command == 'info':
            fields = " "
            if not parsed_string:
            
                response = "`Welcome to RP Companion, the Discord RP Bot Companion!`\n\n*Using Help:*\n\nType /info or /help followed by one of these categories, such as `/info general`:\n\n`general`: Not commands, but information on how the bot works.\n`setup`: Commands for getting the bot running.\n`characters`: Commands for managing characters.\n`custom`: Commands for creating, managing and deleting custom character profiles.\n`npcs`: Commands for managing NPCs.\n`fun`: Commands for old time RP fun.\n`utility`: Utility commands such as scene and narrator posting.\n`dialogs`: Commands for managing dialogs and dialog characters."
            elif parsed_string == 'setup':
                response = "**SETUP COMMANDS**\n\n`/setadminrole @Role`: *Owner* Set the admin role. This must be done before any other setup. This can only be done by a server manager. See general for role descriptions.\n`/setnpcrole @Role` *Admin* Set the NPC manager role.\n`/listroles` *None* List the server roles`\n/addnpcuser @user1 @user2` Add users to the NPC role.\n`/deleteadmin @user1 @user2` Delete users from the admin role. Only a server manager can do this.\n`/deletenpcuser @user1 @user2` Delete users from the NPC role.\n`/resetserver` Wipe all data from the bot for this server. Only the server owner may perform this action.\n`/invite` Get an invite link for the bot.\n"
            elif parsed_string == 'characters':
                response = "**CHARACTER COMMANDS**\n\n`/newchar`  Set up a new character. The bot will DM you for all new fields. An admin must approve a character to become active.\n`/editchar <charname>`  Edit an existing character's profile. The bot will DM you for the fields.\n`/editcharinfo Character Name`  Edit a character's addtional information fields.\n`/deletechar charname`  Delete a character.\n`/getcharprofile Character Name` *None* Get a character's complete profile.\n`/listmychars`  List the current user's characters.\n`/listallchars` *None* List all server characters and their owners.\n`/listuserchars @User` *None* List a user's characters.`\n/approvechar` *Admin* Approve a character for play.\n`/denychar` *Admin* Decline a character for play. A reason should be provided, and the admin has the option to delete the application entirely if it cannot be fixed.\n`/listunapprovedchars` *None* List the characters waiting to be approved or denied.\n`/newrandomchar`: Create a random character with the bot for admin approval."
            elif parsed_string == 'npcs':
                response = "**NPC COMMANDS**\n\n`/setnpc *shortcut*`: Set an NPC for all posts in the current channel.\n`/unsetnpc`: Unset the NPC for this channel.\n`/newnpc @UserAllowed1 @UserAllowed2` *NPC* Create a new NPC.\n`/postnpc shortcut text`  Post as an NPC if you are in the allowed user list.\n`/editnpc Character Name` *NPC* Edit an NPC.\n`/deletenpc Character Name` *NPC* Delete an NPC.\n`/listnpcs`: *None* List all server NPCs.\n`/editnpcpost MESSAGE`: Edit your last NPC post to the content of MESSAGE."

 #               fields / "**VENDOR FIELDS**\n\n`VendorName:` The name of the vendor as it appears in buying items.\n`ItemList:` A comma delimited list of item IDs available for purchase.\n"
            elif parsed_string == 'fun':                
                response = "**FUN FUN FUN COMMANDS**\n\n`/lurk` *None* Post a random lurk command.\n`/ooc` Post as the bot with OOC brackets.\n`/randomooc @user` Do something random to another user.\n`/roll` x`d`y *None* Roll x number of y-sided dice.\n"
            elif parsed_string == 'general':
                response = "**GENERAL INFO**\n\nThis bot supports character profiles, custom profiles, NPCs and fun/narrator commands.\nSome commands only require the name of the character or spell, like `/editchar Dracula`. Other commands will initiate a DM that has menus that you can reply to for setting up or modifying characters or NPCs. If the user has DMs disabled, the bot will reply in the same channel as the user's command.\n\n**ROLES**\n\nThere are two roles required to use the bot.\n`Admin:` The admin can run all commands of the bot, such as adding and deleting spells or items. The server owner must set the admin role.\n`NPC Manager:` The NPC manager is able to create, edit and delete NPCs.\n An admin role user must approve new characters.\n\n"
            elif parsed_string == 'custom':
                response = "**CUSTOM PROFILE COMMANDS**\n\n```Information: Custom profiles allow you to define a character profile for an entire server. All characters will use the custom profile instead of the default profile provided by the bot, and any existing default profiles will be hidden. Deleting the custom profile template deletes all character profiles with it, so once created the template cannot be edited.```\n\n`/newcustomprofile Field1=Description,Field2=Description...`: *Admin* Create a new custom profile. The fields are what will appear in DMs for creation and editing of characters. The descriptions are what will appear when the profile is listed. All fields are free text.\n`/newchar`: Create a new character using the custom profile.\n`/editchar Character Name`: Edit a custom profile character.\n`/deletechar Character Name`: Delete a custom character profile.\n`/deletecustomprofile yes`: *Admin* Delete the custom profile template and all character profiles from the server. The **yes** must be included (no bolding) to confirm deletion."
            elif parsed_string == 'utility':
                response = "**UTILITY COMMANDS**\n\n`/newscene`: Post --new scene-- as the narrator.\n`/pause`: Post --scene paused-- as the narrator.\n`/unpause`: Post --scene resumed-- as the narrator.\n`/endscene`: Post --end scene-- as the narrator.\n`/postnarr text`: Post text as the narrator."
            elif parsed_string == 'dialogs':
                response = "**DIALOG COMMANDS**\n\n```Information: Dialogs allow a player to pick options within a menu of dialogs to simulate a conversation. Dialog systems have three parts: Dialog characters, which are the NPC associated with the dialog, and have a name and picture; Root dialogs, which are the top-level dialog options for a dialog character, and subdialogs, which are the dialogs below the root dialogs. A sub dialog can have zero, one, or many subdialogs below it, and so on.```\n\n`/newdialogchar`: Create a new dialog character.\n`/editdialogchar Character Name`: Edit an existing dialog character.\n`/deletedialogchar Character Name`: Remove a dialog character from the server. All dialogs must be deleted prior to this command.\n`/newrootdialog`: Create a new root dialog associated with an existing dialog character.\n`/newsubdialog`: Create a new subdialog. The root dialog or parent subdialog must already exist.\n`/deletedialog`: Delete a dialog from the server. All child dialogs must be deleted first or the command will fail.\n`/listdialogchars`: List all currently defined dialog characters.\n`/listdialogchar Character Name`: Show the name, picture and dialogs of an existing dialog character.\n`/listalldialogs`: List all dialogs defined on the server.\n\n```Conversations: A player may start a conversation with the /converse command. The bot will present the dialog options as reactions to its message, and then when a player reacts to the message, the option will be chosen and the next subdialogs will be presented. When a dialog has no subdialogs, the conversation ends. A conversation may also be ended with /endconvo.```\n\n`/converse Character Name`: Start a conversation with a dialog character.\n`/endconvo`: End the current conversation."
            else:
                response = "`Welcome to RP Companion, the Discord RP Bot Companion!`\n\n*Using Help:*\n\nType /info or /help followed by one of these categories, such as `/info general`:\n\n`general`: Not commands, but information on how the bot works.\n`setup`: Commands for getting the bot running.\n`characters`: Commands for managing characters.\n`custom`: Commands for creating, managing and deleting custom character profiles.\n`npcs`: Commands for managing NPCs.\n`fun`: Commands for old time RP fun.\n`utility`: Utility commands such as scene and narrator posting.\n`dialogs`: Commands for managing dialogs and dialog characters."                
            if fields:
                await reply_message(message, response + fields)
            else: 
                await reply_message(message, response)
        if command == 'initialize':
            if not await admin_check(message.author.id):
                await reply_message(message, "This command is admin only!")
                return
            
            create_profile_table = """CREATE TABLE CharacterProfiles (Id int auto_increment, ServerId varchar(40), UserId varchar(40), CharacterName varchar(50), Age Int, Race varchar(30), Gender varchar(20), Height varchar(10), Weight varchar(10), PlayedBy varchar(40), Origin varchar(100), Occupation varchar(100), Personality TEXT, Biography TEXT, Description TEXT, Strengths TEXT, Weaknesses TEXT, Powers TEXT, Skills TEXT, PictureLink varchar(1024), PRIMARY KEY (Id));"""
            create_npc_table = """CREATE TABLE NonPlayerCharacters (Id int auto_increment, ServerId varchar(40), UserId varchar(40), UsersAllowed varchar(1500), CharName varchar(100), PictureLink varchar(1024), Shortcut varchar(20), PRIMARY KEY (Id));"""
            # "GMRole","NPCRole","NPCRole","GuildBankBalance","StartingHealth","StartingMana","StartingStamina","StartingAttack","StartingDefense","StartingMagicAttack","StartingAgility","StartingIntellect","StartingCharisma","HealthffRatio","ManaLevelRatio","StaminaLevelRatio","XPLevelRatio","HealthAutoHeal","ManaAutoHeal","StaminaAutoHeal"
            create_guild_settings_table = """CREATE TABLE GuildSettings (Id int auto_increment, ServerId VARCHAR(40),  GuildName VarChar(100), AdminRole VARCHAR(40), NPCRole VARCHAR(40), PRIMARY KEY(Id));"""
            
            create_custom_profile_table = """CREATE TABLE CustomProfiles (Id int auto_increment, ServerId VARCHAR(40), Fields TEXT, PRIMARY KEY(Id));"""
            
            create_unapproved_char_table = """CREATE TABLE UnapprovedCharacterProfiles (Id int auto_increment, ServerId varchar(40), UserId varchar(40), CharacterName varchar(50), LastName varchar(100), Age Int, Race varchar(30), Gender varchar(20), Height varchar(10), Weight varchar(10), PlayedBy varchar(40), Origin varchar(100), Occupation varchar(100), Personality TEXT, Biography TEXT, Description TEXT, Strengths TEXT, Weaknesses TEXT, Powers TEXT, Skills TEXT, PictureLink varchar(1024), PRIMARY KEY (Id));"""
            
            result = await execute_sql(create_profile_table)
            if not result:
                await reply_message(message, "Database error with profile!")
                return
                
            result = await execute_sql(create_npc_table)
            if not result:
                await reply_message(message, "Database error with NPCs!")
                return  
                
 
            result = await execute_sql(create_guild_settings_table)
            if not result:
                await reply_message(message, "Database error with guild settings!")
                return
            result = await execute_sql(create_custom_profile_table)
            if not result:
                await reply_message(message, "Database error with custom profiles!")
                return  

            result = await execute_sql(create_unapproved_char_table)
            if not result:
                await reply_message(message, "Database error with unapproved char table!")
                return
 
            await reply_message(message, "Databases initialized!")
        if "AdminRole" not in guild_settings[message.guild.id].keys():
            
            await reply_message(message, "Admin role not set! Please set an admin role using the command //setadminrole @Role")
            return

                

        if command == 'deleteall':
            if not await admin_check(message.author.id):
                await reply_message(message, "This command is admin only!")
                return
            drop_all_tables = """DROP TABLE IF EXISTS CharacterProfiles; DROP TABLE IF EXISTS Inventory; DROP TABLE IF EXISTS Equipment; DROP TABLE IF EXISTS NonPlayerCharacters; DROP TABLE IF EXISTS Spells; DROP TABLE IF EXISTS Melee; DROP TABLE IF EXISTS MagicSkills; DROP TABLE IF EXISTS MeleeSkills; DROP TABLE IF EXISTS Monsters; DROP TABLE IF Exists CustomProfiles; DROP TABLE IF Exists Vendors; DROP TABLE IF EXISTS Buffs; DROP TABLE IF EXISTS BuffSkills;"""
            result = await execute_sql(drop_all_tables)
            if result:
                await reply_message(message, "All tables dropped.")
            else:
                await reply_message(message, "Database error!")
        elif command == 'listunapprovedchars':
            dm_tracker[message.author.id] = {}
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            response = "**UNAPPROVED CHARACTERS**\n\n"
            menu = await make_simple_menu(message, "UnapprovedCharacterProfiles", "CharacterName")
            await reply_message(message, response + menu)                
 
        elif command == 'roll':
            if re.search(r"\s+",parsed_string):
                dice_string = parsed_string.split(' ')
            else:
                dice_string = [parsed_string,]
            response = "**Dice roll:** "
            total_sum = 0
            next_operator = ''
            for operator in dice_string:
                sum = 0 
                print(str(operator))
                print(str(next_operator))
                if re.search(r"\d+d\d+",operator):
                    
                    dice_re = re.compile(r"(\d+)d(\d+)")
                    m = dice_re.search(operator)
                    if not m:
                        await reply_message(message, "Invalid dice command!")
                        return
                    number_of_dice = m.group(1)
                    dice_sides = m.group(2)
                    if int(number_of_dice) > 100:
                        await reply_message(message, "You can't specify more than 100 dice to roll!")
                        return

                    response = response + " ( "
                    for x in range(0, int(number_of_dice)):
                        die_roll = random.randint(1, int(dice_sides))
                        sum = sum + die_roll
                        response = response + " `" + str(die_roll) + "` + "
                    response = response.strip(' + ')  + " ) "

                elif operator == '+':
                    next_operator = '+'
                    response = response + " " + operator
                    continue
                elif operator == '-':
                    next_operator = '-'
                    response = response + " " + operator
                    continue
                elif operator == '*':
                    next_operator = '*'
                    response = response + " " + operator
                    continue
                elif operator == '/':
                    response = response + " " + operator
                    next_operator = '/'
                    continue
                elif re.search(r"[0-9]", operator):
                    m = re.search(r"([0-9]+)",operator)
                    if m:
                        sum = int(m.group(1))
                        response = response + " " + str(sum) + " "
                if next_operator == '+':
                    total_sum = total_sum + sum
                    
                elif next_operator == '-':
                    total_sum = total_sum - sum
                    
                elif next_operator == '*':
                    total_sum = total_sum * sum
                    
                elif next_operator == '/':
                    total_sum = total_sum / sum
                    
                if total_sum == 0:
                    total_sum = sum
                    
                
                print("Total sum: " + str(total_sum))
                
            response = response.replace(dice_string[0],'') + " = `" + str(total_sum) + "`"        
                    
            await reply_message(message, response)
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
        elif command == 'listallchars':
            records = None
            records = await select_sql("""SELECT Fields FROM CustomProfiles WHERE ServerId=%s;""",(str(message.guild.id),))
            print(str(records))
            if records:
                records2 = await select_sql("""SELECT Name,UserId FROM Server""" + str(message.guild.id) +""";""")
                if not records2:
                    await reply_message(message, "No characters found on the server.")
                    return
                response = "**Server Character List (Custom)**\n\n"
                for row in records2[1:]:
                    # user  = message.guild.get_member(int(row[1]))
              
                        response = response + row[0] + "\n"
                await reply_message(message, response)
                return    
            records = await select_sql("""SELECT CharacterName,UserId FROM CharacterProfiles WHERE ServerId=%s;""", (str(message.guild.id),))
            if not records:
                await reply_message(message, "No characters found for this server!")
                return
            response = "**SERVER CHARACTER LIST**\n\n"
            for row in records:

                response = response + row[0] + "\n"
            await reply_message(message, response)
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await reply_message(message,"Admin command only!")
                return   
            await reply_message(message, "Server count: " + str(len(client.guilds)))            
        elif command == 'listuserchars':
            if not message.mentions:
                await reply_message(message, "You didn't specify a user!")
                return
            user = message.mentions[0]
            user_id = user.id
            records = await select_sql("""SELECT Fields FROM CustomProfiles WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                get_chars = """SELECT Name FROM Server""" + str(message.guild.id) +  """ WHERE UserId=%s;"""
                records1 = await select_sql(get_chars, (str(user_id),))
                if not records1:
                    await reply_message(message, "No records found for that user!")
                    return                
                response = "**Character list:**\n\n"
                
                for row in records1:
                    response = response + row[0] + "\n"
                await reply_message(message, response)
            else:    
                records = await select_sql("""SELECT CharacterName FROM CharacterProfiles WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(user_id)))
                if not records:
                    await reply_message(message, "No records found for that user!")
                    return
                response = "**USER CHARACTER LIST**\n\n"
                for row in records:
                    response = response + row[0] + "\n"
                await reply_message(message,response)
        elif command == 'approvechar':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must have the admin role to approve a new character.")
                return
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'approvechar'
            dm_tracker[message.author.id]["fieldlist"] = ["CharacterName","Approval"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            menu = await make_simple_menu(message, "UnapprovedCharacterProfiles", "CharacterName")
            
            response = "Please select a new character to approve by replying to this message with the ID below:\n\n" + menu
            await direct_message(message, response)
            await reply_message(message, "Please check your DMs for instructions on how to approve a character, <@" + str(message.author.id) + ">.")
        elif command == 'denychar':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must have the admin role to deny a new character.")
                return
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'denychar'
            dm_tracker[message.author.id]["fieldlist"] = ["CharacterName","Deny","DenyReason","Deletion"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            menu = await make_simple_menu(message, "UnapprovedCharacterProfiles", "CharacterName")
            
            response = "Please select a new character to deny by replying to this message with the ID below:\n\n" + menu
            await direct_message(message, response)
            await reply_message(message, "Please check your DMs for instructions on how to deny a character, <@" + str(message.author.id) + ">.")
        elif command == 'newsubdialog':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must have the admin role to create a new sub dialog.")

            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'newsubdialog'
            dm_tracker[message.author.id]["fieldlist"] = ["RootDialog","RoleRequiredId","Response","Reply"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            menu = await make_simple_menu(message, "Dialog","Response")
            
            response = "Please select a dialog to add a sub dialog to this message with the ID below:\n\n" + menu
            await direct_message(message, response)
            await reply_message(message, "Please check your DMs for instructions on how to create a sub dialog, <@" + str(message.author.id) + ">.")              
        elif command == 'newrootdialog':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must have the admin role to create a new root dialog.")

            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'newrootdialog'
            dm_tracker[message.author.id]["fieldlist"] = ["CharacterId","RoleRequiredId","Response","Reply"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            menu = await make_simple_menu(message, "DialogCharacters", "CharacterName")
            
            response = "Please select a new character to add a root dialog to this message with the ID below:\n\n" + menu
            await direct_message(message, response)
            await reply_message(message, "Please check your DMs for instructions on how to create a root dialog, <@" + str(message.author.id) + ">.")
        elif command == 'listdialogchars':
            records = await select_sql("""SELECT Id,CharacterName FROM DialogCharacters WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await reply_message(message, "No dialog characters defined yet!")
                return
            response = "**Server Dialog Character Listing**\n\n"
            for row in records:
                response = response + str(row[0]) + " - " + row[1] + "\n"
            await reply_message(message, response)
        elif command == "listdialogchar":
            if not parsed_string:
                await reply_message(message, "You didn't specify a dialog character to show!")
                return
            records = await select_sql("""SELECT Id,CharacterName,RootDialogList,PictureLink FROM DialogCharacters WHERE ServerId=%s AND CharacterName=%s;""",(str(message.guild.id),str(parsed_string)))
            if not records:
                await reply_message(message, "No dialog character found by that name!")
                return
            embed = discord.Embed(title="Dialog Character Listing")
            for row in records:
                char_id = str(row[0])
                name = row[1]
                root_dialog = row[2].split(',')
                picture_link = row[3]
            if picture_link.startswith('http'):
                embed.set_thumbnail(url=picture_link)
            embed.add_field(name="ID",value=char_id)
            embed.add_field(name="Character Name",value=name)
            response = ""
            for dialog_id in root_dialog:
                records = await select_sql("""SELECT Response FROM Dialog WHERE Id=%s;""",(str(dialog_id),))
                for row in records:
                    response = response + dialog_id + " - " + row[0] + "\n"
            embed.add_field(name="Root Dialogs",value=response)
            await message.channel.send(embed=embed)
        elif command == 'listalldialogs':
            records = await select_sql("""SELECT Id,Response,ChildDialogs FROM Dialog WHERE ServerId=%s ORDER BY Id;""",(str(message.guild.id),))
            if not records:
                await reply_message(message, "No dialogs defined yet!")
                return
            response = "**Server Dialog Listing**\n\n"
            for row in records:
                response = response + str(row[0]) + " - *" + row[1] + "*: " + row[2] + "\n"
            await reply_message(message, response)
        elif command == 'deletedialogchar':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must have the admin role to edit a dialog character.")   
                return
            if not parsed_string:
                await reply_message(message, "You didn't specify a dialog character to delete!")
                return
                
            records = await select_sql("""SELECT Id,RootDialogList FROM DialogCharacters WHERE ServerId=%s AND CharacterName=%s;""",(str(message.guild.id),str(parsed_string)))
            if not records:
                await reply_message(message, "No dialog character found by that name!")
                return
            for row in records:
                char_id = row[0]
                root_list = row[1]
            try:
                root_list
                if root_list != '0':
                    await reply_message(message, "This character still has root dialogs defined. Please delete dialog IDs (" + root_list + ") before deleting the character!")
                    return
            except:
                pass
            result = await commit_sql("""DELETE FROM DialogCharacters WHERE Id=%s;""",(str(char_id),))
            if result:
                await reply_message(message, "Dialog character deleted from server!")
            else:
                await reply_message(message, "Database error!")
                
        elif command == 'deletedialog':
            if not parsed_string:
                await reply_message(message, "You didn't specify a dialog ID to delete!")
                return
            records = await select_sql("""SELECT Response,ChildDialogs FROM Dialog WHERE Id=%s;""",(str(parsed_string),))
            if not records:
                await reply_message(message, "That response ID doesn't exist!")
                return
                
            for row in records:
                reply = row[0]
                child_dialogs = row[1].split(',')
            if child_dialogs[0] != '0':
                await reply_message(message, "This dialog has child dialogs. Please delete all child dialogs first!")
                return
            result = await commit_sql("""DELETE FROM Dialog WHERE Id=%s;""",(str(parsed_string),))
            records = await select_sql("""SELECT Id,ChildDialogs FROM Dialog WHERE ServerId=%s AND ChildDialogs LIKE '%""" + parsed_string + """%';""",(str(message.guild.id),))
            for row in records:
                new_child = row[1].split(',').remove(parsed_string)
                if not new_child:
                    new_child = '0'
                else:    
                    new_child = ','.join(new_child)
                result = await commit_sql("""UPDATE Dialog SET ChildDialogs=%s WHERE Id=%s;""",(str(new_child),str(row[0])))
            records = await select_sql("""SELECT Id,RootDialogList FROM DialogCharacters WHERE ServerId=%s AND RootDialogList LIKE '%""" + parsed_string + """%';""",(str(message.guild.id),))
            for row in records:
                new_root = row[1].split(',').remove(parsed_string)
                if not new_root:
                    new_root = '0'
                else:
                    new_root = ','.join(new_root)
                result = await commit_sql("""UPDATE DialogCharacters SET RootDialogList=%s WHERE Id=%s;""",(str(new_root),str(row[0])))
                
            if result:
                await reply_message(message, "Deleted dialog ID " + parsed_string + " with response " + reply)
            else:
                await reply_message(message, "Database error!")
        elif command == 'editdialogchar':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must have the admin role to edit a dialog character.")

            records = await select_sql("""SELECT CharacterName,InitialDialog,PictureLink FROM DialogCharacters WHERE ServerId=%s AND CharacterName=%s;""",(str(message.guild.id),re.sub(r"<.*>","",parsed_string).strip()))
            if not records:
                await reply_message(message, "No NPC found with that name!")
                return
            for row in records:
                fields = row
                
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'editdialogchar'
            dm_tracker[message.author.id]["fieldlist"] = ["CharacterName","InitialDialog","PictureLink"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            counter = 0
            for row in dm_tracker[message.author.id]["fieldlist"]:
                dm_tracker[message.author.id]["fielddict"].append(fields[counter])
                counter = counter + 1            
            await reply_message(message, "Please check your DMs for instructions on how to edit a dialog character, <@" + str(message.author.id) + ">.")
            
            await direct_message(message, "You have requested to edit the dialog character **" + parsed_string + "**. Please type in the response the answer to each field to update, or *skip* to leave as is. When you have filled out all fields, the spell will be updated!\nThe first field is **" + dm_tracker[message.author.id]["fieldlist"][0] + "** and its current value is **" + dm_tracker[message.author.id]["fielddict"][0] + "**.")              
        elif command == 'newdialogchar':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must have the admin role to create a new dialog character.")
   
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'newdialogchar'
            dm_tracker[message.author.id]["fieldlist"] = ["CharacterName","InitialDialog","PictureLink"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            
            await reply_message(message, "Please check your DMs for instructions on how to create a new dialog character, <@" + str(message.author.id) + ">.")
            
            await direct_message(message, "You have requested a new default character! Please type in the response the **name of the dialog character**, and then enter each field as a reply to the DMs. When you have filled out all fields, the dialog character will be created!")            
        elif command == 'newchar':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must have the NPC role to create a new character.")
                return
                
            records = await select_sql("""SELECT Fields FROM CustomProfiles WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                field_dict = { }
                for row in records:
                    fields = row[0].strip(',').split(',')
                if message.author.id not in dm_tracker.keys():
                    await initialize_dm(message.author.id)
                descriptions = "SELECT "
                for field in fields:
                    descriptions = descriptions + field + ","
                descriptions = re.sub(r",$"," ",descriptions)
                descriptions = descriptions + "FROM Server" + str(message.guild.id) + ";"
                descript_records = await select_sql(descriptions)
                for row in descript_records:
                    description_list = row
                    
                dm_tracker[message.author.id]["currentcommand"] = 'newcustomchar'
                dm_tracker[message.author.id]["fieldlist"] = fields
                dm_tracker[message.author.id]["server_id"] = message.guild.id
                dm_tracker[message.author.id]["currentfield"] = 0
                dm_tracker[message.author.id]["commandchannel"] = message.channel
                dm_tracker[message.author.id]["parameters"] = description_list
                await reply_message(message, "Please check your DMs for instructions on how to create a new character, <@" + str(message.author.id) + ">.")
                await direct_message(message, "Hello, you have requested to create a new character! Please start with the **name** of the character below in your reply!")
                return

            else:        
                if message.author.id not in dm_tracker.keys():
                    await initialize_dm(message.author.id)
                dm_tracker[message.author.id]["currentcommand"] = 'newdefaultchar'
                dm_tracker[message.author.id]["fieldlist"] = ["CharacterName","Age","Race","Gender","Height","Weight","Playedby","Origin","Occupation","PictureLink"]                                                   
                dm_tracker[message.author.id]["currentfield"] = 0
                dm_tracker[message.author.id]["fielddict"] = [] 
                dm_tracker[message.author.id]["server_id"] = message.guild.id
                dm_tracker[message.author.id]["commandchannel"] = message.channel
                
                await reply_message(message, "Please check your DMs for instructions on how to create a new character, <@" + str(message.author.id) + ">.")
                
                await direct_message(message, "You have requested a new default character! Please type in the response the **first and last names of the character**, and then enter each field as a reply to the DMs. When you have filled out all fields, the character will be created!")
        elif command == 'newrandomchar':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must have the NPC role to create a new character.")
                return
            records = await select_sql("""SELECT Fields FROM CustomProfiles WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                await reply_message(message, "You have a custom profile enabled. Unable to create a new random character.")
                return
            male_first_name_list = ["Ferris", "Redmond", "Raphael", "Orion", "Caspian", "Aramis", "Lucian", "Storm", "Percival", "Gawain", "Perseus", "Cormac", "Leon", "Patrick", "Robert", "Morgan", "Brandon", "Sven", "Roland", "Ronan", "EdPlayerd", "Adam", "Edric", "Martin", "Odin", "Bayard", "Laurent", "Faramond", "Finn", "Edward", "Tristan", "Emil", "Zephyr", "Soren", "Arthur", "Robin", "Marcel", "Roman", "Beowulf"", ""Seth", "Tristan", "Arthur", "EdPlayerd", "Percival", "Ronan", "Thor", "Leon", "Roman", "Adam", "Ferris", "Zephyr", "Gawain", "Perseus", "Cormac", "Lydan", "Syrin", "Ptorik", "Joz", "Varog", "Gethrod", "Hezra", "Feron", "Ophni", "Colborn", "Fintis", "Gatlin", "Jinto", "Hagalbar", "Krinn", "Lenox", "Revvyn", "Hodus", "Dimian", "Paskel", "Kontas", "Weston", "Azamarr ", "Jather ", "Tekren ", "Jareth", "Adon", "Zaden", "Eune ", "Graff", "Tez", "Jessop", "Gunnar", "Pike", "Domnhar", "Baske", "Jerrick", "Mavrek", "Riordan", "Wulfe", "Straus", "Tyvrik ", "Henndar", "Favroe", "Whit", "Jaris", "Renham", "Kagran", "Lassrin ", "Vadim", "Arlo", "Quintis", "Vale", "Caelan", "Yorjan", "Khron", "Ishmael", "Jakrin", "Fangar", "Roux", "Baxar", "Hawke", "Gatlen", "Barak", "Nazim", "Kadric", "Paquin", " ", "", "Kent", "Moki", "Rankar", "Lothe", "Ryven", "Clawsen", "Pakker", "Embre", "Cassian", "Verssek", "Dagfinn", "Ebraheim", "Nesso", "Eldermar", "Rivik", "Rourke", "Barton", "Hemm", "Sarkin", "Blaiz ", "Talon", "Agro", "Zagaroth", "Turrek", "Esdel", " ", "", "Lustros", "Zenner", "Baashar ", "Dagrod ", "Gentar", "Feston"]
            female_first_name_list = ["Ayrana", "Resha", "Varin", "Wren", "Yuni", "Talis", "Kessa", "Magaltie", "Aeris", "Desmina", "Krynna", "Asralyn ", "Herra", "Pret", "Kory", "Afia", "Tessel", "Rhiannon", "Zara", "Jesi", "Belen", "Rei", "Ciscra", "Temy", "Renalee ", "Estyn", "Maarika", "Lynorr", "Tiv", "Annihya", "Semet", "Tamrin", "Antia", "Reslyn", "Basak", "Vixra", "Pekka ", "Xavia", "Beatha ", "Yarri", "Liris", "Sonali", "Razra ", "Soko", "Maeve", "Everen", "Yelina", "Morwena", "Hagar", "Palra", "Elysa", "Sage", "Ketra", "Lynx", "Agama", "Thesra ", "Tezani", "Ralia", "Esmee", "Heron", "Naima", "Rydna ", "Sparrow", "Baakshi ", "Ibera", "Phlox", "Dessa", "Braithe", "Taewen", "Larke", "Silene", "Phressa", "Esther", "Anika", "Rasy ", "Harper", "Indie", "Vita", "Drusila", "Minha", "Surane", "Lassona", "Merula", "Kye", "Jonna", "Lyla", "Zet", "Orett", "Naphtalia", "Turi", "Rhays", "Shike", "Hartie", "Beela", "Leska", "Vemery ", "Lunex", "Fidess", "Tisette", "Partha"]
            unisex_first_name_list = []
            last_name_list = ["Starbringer","Leafgreen","Smith","Thundershaw","Dreamweaver","McAle","Hale","Zendor","Zoaraster","Horserider","Stormwalker","Abawi", "Allard", "Adara", "Abbott", "Acampora", "Ackerman", "Ackroyd", "Abbington", "Axworthy", "Ainge", "Abernathy", "Atkinson", "Abner", "Abella", "Agholor", "Allred", "Asola", "Abrams", "Acker", "Abrell", "Acuff", "Archer", "Asterio", "Adair", "Albright", "Adelson", "Atwood", "Aguillar", "Adler", "Arrowood", "Agnew", "Akuna", "Alcott", "Alstott", "Austin", "Algarotti", "Alvarez", "Armani", "Anderson", "Amherst", "Adkins", "Ayesa", "Argento", "Arrowood", "Andruzzi", "Abraham", "Angle", "Armstrong", "Attard", "Annenberg", "Arrhenius", "Acosta", "Antrican", "Adderley", "Atwater", "Agassi", "Apatow", "Archeletta", "Averescu", "Arrington", "Agrippa", "Aiken", "Albertson", "Alexander", "Amado", "Anders", "Armas", "Akkad", "Aoki", "Aldrich", "Almond", "Alinsky", "Agnello", "Alterio", "Atchley",  "Bynes", "Bray", "Budreau", "Byrne", "Bragg", "Banner", "Bishop", "Burris", "Boggs", "Brembilla", "Booth", "Bullard", "Booker", "Buckner", "Borden", "Breslin", "Bryant", "BIles", "Brunt", "Brager", "Brandt", "Bosa", "Bradshaw", "Brubaker", "Berry", "Brooks", "Bandini", "Bristow", "Barrick", "Biddle", "Brennan", "Brinkmann", "Benz", "Braddock", "Bright", "Berman", "Bracco", "Bartley", "Briggs", "Bonanno", "Boyle", "Beeks", "Bernthal", "Boldon", "Bowser", "Benwikere", "Bowman", "Bamberger", "Bowden", "Batch", "Blaustein", "Blow", "Boulware", "Bezos", "Boulder", "Bauer", "Ballard", "Benton", "Bixby", "Bostwick", "Biles", "Bobusic", "Belinski", "Blood", "Bisley", "Bettis", "Bensen", "Binion", "Bloch", "Blixt", "Bellisario", "Botkin", "Benoit", "BInda", "Baldwin", "Bennett", "Bourland", "Bester", "Bender", "Best", "Bald", "Bersa", "Belt", "Bourne", "Barks", "Beebe", "Banu", "Bozzelli", "Bogaerts",  "Cyrus", "Craggs", "Crisper", "Cotheran", "Curry", "Conard", "Cutler", "Coggins", "Cates", "Crisp", "Curio ", "Creed", "Costner", "Cortse", "Cunningham", "Cooper", "Cullen", "Castle", "Cugat", "Click", "Cassidy", "Crespo", "Crusher", "Cooper", "Coates", "Crowley", "Creel", "Crassus", "Cogdill", "Cross", "Crabtree", "Cranham", "Carver", "Cox", "Coltrane", "Chatwin", "Conklin", "Colt", "Coulter", "Cleveland", "Coppens", "Coolidge", "Copeland", "Celino", "Coffin", "Cena", "Conti ", "Coin", "Connelly", "Cents", "Carney", "Carmichael", "Coffey", "Carling", "Christie", "Chadwick", "Cobo", "Clay", "Capra", "Candy", "Clancy", "Chalk", "Chambers", "Callahan", "Cirque", "Cabrera-Bello", "Cherry", "Cannon", "Chung", "Cave", "Challenger", "Cobb", "Calaway", "Chalut", "Cayce", "Cahill", "Cruz", "Cohen", "Caylor", "Cagle", "Cline", "Crawford", "Cleary", "Cain", "Champ", "Cauley", "Claxton"    "Dubois", "Darby", "Draper", "Dwyer", "Dixon", "Danton", "Devereaux", "Ditka", "Dominguez", "Decker", "Dobermann", "Dunlop", "Dumont", "Dandridge", "Diamond", "Dobra ", "Dukas", "Dyer", "Decarlo", "Delpy", "Dufner", "Driver", "Dalton", "Dark", "Dawkins", "Driskel", "Derbyshire", "Davenport", "Dabney", "Dooley", "Dickerson", "Donovan", "Dallesandro", "Devlin", "Donnelly", "Day", "Daddario", "Donahue", "Denver", "Denton", "Dodge", "Dempsey", "Dahl", "Drewitt",  "Earp", "Eberstark ", "Egan", "Elder", "Eldridge", "Ellenburg", "Eslinger", "England", "Epps", "Eubanks", "Everhart", "Evert", "Eastwood", "Elway", "Eslinger", "Ellerbrock", "Edge", "Endo", "Etter", "Ebersol", "Everson", "Earwood", "Ekker", "Escobar", "Edgeworth",  "Future", "Fitzpatrick", "Fontana", "Fenner", "Furyk", "Finch", "Fullbright", "Fassbinder", "Flood", "Fong", "Fleetwood", "Fugger", "Frost", "Fsik", "Fawcett", "Fishman", "Freeze", "Fissolo", "Foley", "Fairchild", "Freeman", "Flanagan", "Freed", "Fogerty", "Foster", "Finn", "Fletcher", "Floris", "Flynn", "Fairbanks", "Fawzi ", "Finau", "Floquet ", "Fleiss", "Ferguson", "Froning", "Fitzgerald", "Fingermann", "Flagg", "Finchum", "Flair", "Ferber", "Fuller", "Farrell", "Fenton", "Fangio", "Faddis", "Ferenz", "Farley",  "Gundlach", "Gannon", "Goulding", "Greenway", "Guest", "Gillis", "Gellar", "Gaither", "Griffith", "Grubbs", "Glass", "Gotti", "Goodwin", "Grizzly", "Glover", "Grimes", "Gleason", "Gardner", "Geske", "Griffo", "Glunt", "Golden", "Gardel", "Gribble", "Grell", "Gearey", "Grooms", "Glaser", "Greer", "Geel", "Gallagher", "Glick", "Graber ", "Gore", "Gabbard", "Gelpi", "Gilardi", "Goddard", "Gabel", "Hyde", "Hood", "Hull", "Hogan", "Hitchens", "Higgins", "Hodder", "Huxx", "Hester", "Huxley", "Hess", "Hutton", "Hobgood", "Husher", "Hitchcock", "Huffman", "Herrera", "Humber", "Hobbs", "Hostetler", "Henn", "Horry", "Hightower", "Hindley", "Hitchens", "Holiday", "Holland", "Hitchcock", "Hoagland", "Hilliard", "Harvick", "Hardison", "Hickey", "Heller", "Hartman", "Halliwell", "Hughes", "Hart", "Healy", "Head", "Harper", "Hibben", "Harker", "Hatton", "Hawk", "Hardy", "Hadwin", "Hemmings", "Hembree", "Helbig", "Hardin", "Hammer", "Hammond", "Haystack", "Howell", "Hatcher", "Hamilton", "Halleck", "Hooper", "Hartsell", "Henderson", "Hale", "Hokoda", "Heers", "Homa", "Hanifin", "Most Common Last Names Around the World" ,    "Inch", "Inoki", "Ingram", "Idelson", "Irvin", "Ives", "Ishikawa", "Irons", "Irwin", "Ibach", "Ivanenko", "Ibara"    "Jurado", "Jammer", "Jagger", "Jackman", "Jishu", "Jingle", "Jessup", "Jameson", "Jett", "Jackson",  "Kulikov ", "Kellett", "Koo", "Kitt", "Keys", "Kaufman", "Kersey", "Keating", "Kotek ", "Kuchar", "Katts", "Kilmer", "King", "Kubiak", "Koker", "Kerrigan", "Kumara", "Knox", "Koufax", "Keagan", "Kestrel", "Kinder", "Koch", "Keats", "Keller", "Kessler", "Kobayashi", "Klecko", "Kicklighter", "Kincaid", "Kershaw", "Kaminsky", "Kirby", "Keene", "Kenny", "Keogh", "Kipps",   "Salvador Dali", "Salvador Dali"    "Litvak", "Lawler", "London", "Lynch", "Lacroix", "Ledford", "LeMay", "Lovejoy", "Lombardo", "Lovecraft", "Laudermilk", "Locke", "Leishman", "Leary", "Lott", "Ledger", "Lords", "Lacer", "Longwood", "Lattimore", "Laker", "Lecter", "Liston", "Londos", "Lomax", "Leaves ", "Lipman", "Lambert", "Lesnar", "Lazenby", "Lichter", "Lafferty", "Lovin", "Lucchesi", "Landis", "Lopez", "Lentz", "Murray", "Morrison", "McKay", "Merchant", "Murillo", "Mooney", "Murdock", "Matisse", "Massey", "McGee", "Minter", "Playerson", "Mullard", "Mallory", "Meer ", "Mercer", "Mulder", "Malik", "Moreau ", "Metz", "Mudd", "Meilyr", "Motter", "McNamara", "Malfoy", "Moses", "Moody", "Morozov", "Mason", "Metcalf", "McGillicutty", "Montero", "Molinari", "Marsh", "Moffett", "McCabe", "Manus", "Malenko", "Mullinax", "Morrissey", "Mantooth", "Mintz", "Messi", "Mattingly", "Mannix", "Maker", "Montoya", "Marley", "McKnight", "Magnusson ", "Marino", "Maddox", "Macklin", "Mackey", "Morikowa", "Mahan", "Necessary", "Nicely", "Nejem", "Nunn", "Neiderman", "Naillon", "Nyland", "Novak", "Nygard", "Norwood", "Norris", "Namath", "Nabor", "Nash", "Noonan", "Nolan ", "Nystrom", "Niles", "Napier", "Nunley", "Nighy", "Overholt", "Ogletree", "Opilio ", "October", "Ozu", "O'Rourke", "Owusu", "Oduya", "Oaks", "Odenkirk", "Ottinger", "O'Donnell", "Orton", "Oakley", "Oswald", "Ortega", "Ogle", "Orr", "Ogden", "Onassis", "Olson", "Ollenrenshaw", "O'Leary", "O'Brien", "Oldman", "O'Bannon", "Oberman", "O'Malley", "Otto", "Oshima",    "Prado", "Prunk", "Piper", "Putnam", "Pittman", "Post", "Price", "Plunkett", "Pitcher", "Pinzer", "Punch", "Paxton", "Powers", "Previn", "Pulman", "Puller", "Peck", "Pepin", "Platt", "Powell", "Pawar", "Pinder", "Pickering", "Pollock", "Perrin", "Pell", "Pavlov", "Patterson", "Perabo", "Patnick", "Panera", "Prescott", "Portis", "Perkins", "Palmer", "Paisley", "Pladino", "Pope", "Posada", "Pointer", "Poston", "Porter", "Quinn", "Quan", "Quaice", "Quaid", "Quirico", "Quarters", "Quimby", "Qua", "Quivers", "Quall", "Quick", "Qugg", "Quint", "Quintero",  "Leonardo da Vinci", "Leonardo da Vinci"    "Rudd", "Ripperton", "Renfro", "Rifkin", "Rand", "Root", "Rhodes", "Rowland", "Ramos", "Ryan", "Rafus", "Radiguet", "Ripley", "Ruster", "Rush", "Race", "Rooney", "Russo", "Rude", "Roland", "Reader", "Renshaw", "Rossi", "Riddle", "Ripa", "Richter", "Rosenberg", "Romo", "Ramirez", "Reagan", "Rainwater", "Romirez", "Riker", "Riggs", "Redman", "Reinhart", "Redgrave", "Rafferty", "Rigby", "Roman", "Reece",  "Sutton", "Swift", "Sorrow", "Spinks", "Suggs", "Seagate", "Story", "Soo", "Sullivan", "Sykes", "Skirth", "Silver", "Small", "Stoneking", "Sweeney", "Surrett", "Swiatek", "Sloane", "Stapleton", "Seibert", "Stroud", "Strode", "Stockton", "Scardino", "Spacek", "Spieth", "Stitchen", "Stiner", "Soria", "Saxon", "Shields", "Stelly", "Steele", "Standifer", "Shock", "Simerly", "Swafford", "Stamper", "Sotelo", "Smoker", "Skinner", "Shaver", "Shivers", "Savoy", "Small", "Skills", "Sinclair", "Savage", "Sereno", "Sasai", "Silverman", "Silva", "Shippen", "Sasaki", "Sands", "Shute", "Sabanthia", "Sheehan", "Sarkis", "Shea", "Santos", "Snedeker", "Stubbings", "Streelman", "Skaggs", "Spears", "Dave Chappelle", "Dave Chappelle"    "Twigg", "Tracy", "Truth", "Tillerson", "Thorisdottir ", "Tooms", "Tripper", "Tway", "Taymor", "Tamlin", "Toller", "Tussac", "Turpin", "Tippett", "Tabrizi", "Tanner", "Tuco", "Trumbo", "Tucker", "Theo", "Thain", "Trapp", "Trumbald ", "Trench", "Terrella", "Tait", "Tanaka", "Tapp", "Tepper", "Trainor", "Turner", "Teague", "Templeton", "Temple", "Teach", "Tam"    "Udder", "Uso", "Uceda", "Umoh", "Underhill", "Uplinger", "Ulett", "Urtz", "Unger", "Vroman", "Vess", "Voight", "Vegas", "Vasher", "Vandal", "Vader", "Volek", "Vega", "Vestine", "Vaccaro", "Vickers",  "Witt", "Wolownik", "Winding", "Wooten ", "Whitner", "Winslow", "Winchell", "Winters", "Walsh", "Whalen", "Watson", "Wooster", "Woodson", "Winthrop", "Wall", "Wight", "Webb", "Woodard", "Wixx", "Wong", "Whesker", "Wolfenstein", "Winchester", "Wire", "Wolf", "Wheeler", "Warrick", "Walcott", "Wilde", "Wexler", "Wells", "Weeks", "Wainright", "Wallace", "Weaver", "Wagner", "Wadd", "Withers", "Whitby", "Woodland", "Woody", "Xavier", "Xanders", "Xang", "Ximinez", "Xie", "Xenakis", "Xu", "Xiang", "Xuxa",  "Yearwood", "Yellen", "Yaeger", "Yankovich", "Yamaguchi", "Yarborough", "Youngblood", "Yanetta", "Yadao", "Yale", "Yasumoto", "Yates", "Younger", "Yoakum", "York", "Yount",  "Zuckerberg", "Zeck", "Zavaroni", "Zeller", "Zipser", "Zedillo", "Zook", "Zeigler", "Zimmerman", "Zeagler", "Zale", "Zasso", "Zant", "Zappa", "Zapf", "Zahn", "Zabinski", "Zade", "Zabik", "Zader", "Zukoff", "Zullo", "Zmich", "Zoller"]
            race_list = ["Human","Elf","Dwarf","Gnome","Troll","Elemental","Orc","Angel","Demon","Vampire","Shadow walker","Deity","Xendorian","Archangel","Archdemon","Undead","Drow","Ghost","Dragon","Werewolf","Fairy","Dark Fairy","Pixie","Shifter","Merperson","Sentient animal","Goblin","Halfling","Kitsune","Centaur","Satyr","Dryad","Nightmare","Incarnate","Death walker","Yeti","Wendigo","Monster","High Elf","Wood Elf","Dark Elf","Manticore","Gryphon","Phoenix","Ent"]
            height_min_feet = 1
            height_max_feet = 8
            height_inches_max = 11
            weight_min = 50
            weight_max = 400
            age_min = 18
            age_max = 2000
            occupation_list = []
            occupation_list = ["Warrior","Knight","Hunter","Blacksmith","Noble","Royalty","Slave","Mercenary","Caster","Mage","Wizard","Warlock","Protector","Healer","Medium","Psychic","Assassin","Swordsman","Thief","Cobbler","Potion maker","Preacher","Priest","Paladin","Witch","Warlock","Sorcerer","Servant","Escort","Prostitute","Solider","Bartender","Merchant","Sailor","Pirate","Archer","Guard","Slayer","Alchemist","Apothecary","Shopkeeper","Trader","Wizard","Fighter","Teacher","Physician","Philosopher","Farmer","Shepherd","Harbinger","Messenger","Horserider","Chef","Night watch","None","Beggar","Researcher","Advisor","Judge","Executioner","Commander","Captain","Fisher","Ranchhand","Druid"]
            gender_list = ["Male","Female","Non-binary","Genderfluid"]
            origin_list = ["Unknown","Earth","Rhydin","Offworld"]
            powers_list = ["Psychic","Lightning","Light","Healing","Destruction","Darkness","Telepathy","Psychokinesis","Flight","Storms","Water","Air","Wind","Earth","Fire","Talking to the dead","Plane-walking","Illusion","Glamor","Holy","White Magic","Black Magic","Seduction","Speed","Superhuman strength","Immortality","Energy manipulation","Reality warping","Spaceflight","Cloaking","Shadow"]
            strengths_list = ["Melee combat","Magic","Physical strength","Physical speed","Highly intelligent","Expert swordfighter","Martial arts","Strategic","Charismatic","Highly perceptive","Expert with firearms","Expert archer","Resistant to magic"]
            weaknesses_list = ["Black magic","Light","Holy power","Evil power","Easily seduced","Gullible","Socially mnanipulatable","Low intelligence","Fire","Water","Lightning","Darkness","Shadow","Astral attacks","Weak physically","Lost immortality","Reduced powers","Trauma in past","Phobias","Anxiety","Poor training","Little magical capacity"]
            personality_list = ["Warm","Cold","Aloof","Caring","Gregarious","Affable","Talkative","Strong, silent type","Brash","Boisterous","Lazy","Shy","Fearful","Happy-go-lucky","Perky","Perverted","Sociopathic","Formal","Casual","Creative","Nice","Mean","Rude","Kind","Gentle","Harsh","Asexual","Wild in bed","Stoic","Charismatic","Charming","Romantic","Detached","Depressed","Worrywart","Troubled by their past","Carries a grudge","Loving","Hateful","Spiteful","Angry","Short fuse","Patient","Passionate","Empty"]
            skills_list = ["Archery","Swordplay","Reading","Writing","Science","Technology","Music","Telling jokes","Lying when needed","Magic","Alchemy","Healing","Medicine","Potions","Elixirs","Chemistry","Knowledge of the beyond","Master illusionist","Computers","Mixing drinks","Telling stories","Inspiring others","Leading","Fighting","Organizing","Art","Scuplting","Crafts","Metalworking","Buidling structures","Tinkering"]
            
            gender = random.choice(gender_list)
            if gender == 'Male':
                first_name = random.choice(male_first_name_list)
            elif gender == 'Female':
                first_name = random.choice(female_first_name_list)
            else:
                first_name = random.choice(male_first_name_list + female_first_name_list)
            last_name = random.choice(last_name_list)
            
            race = random.choice(race_list)
            
            occupation = random.choice(occupation_list)
            
            if race == 'Human':
                age = random.randint(18,100)
            else:
                age = random.randint(age_min, age_max)
            
            origin = random.choice(origin_list)
            height_feet = random.randint(height_min_feet, height_max_feet)
            height_inches = random.randint(0,11)
            weight = random.randint(weight_min, weight_max)
            
            number_of_strengths = random.randint(1,5)
            strengths = ""
            for x in range(0,number_of_strengths):
                strengths = strengths + random.choice(strengths_list) + ", "
            number_of_weaknesses = random.randint(1,5)
            weaknesses = ""
            for x in range(0,number_of_weaknesses):
                weaknesses = weaknesses  + random.choice(weaknesses_list) + ", " 
            powers = ""
            
            number_of_powers = random.randint(1,3)
            for x in range(0,number_of_powers):
                powers = powers  + random.choice(powers_list) + ", " 
            number_of_skills = random.randint(1,5)
            skills = ""
            for x in range(0,number_of_skills):
                skills = skills  + random.choice(skills_list) + ", "     
            personality = ""
            number_of_personality = random.randint(2,6)
            for x in range(0,number_of_personality):
                personality = personality  + random.choice(personality_list) + ", "                     
                
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'newrandomchar'
            dm_tracker[message.author.id]["fieldlist"] = ["CharacterName","Age","Race","Gender","Height","Weight","Playedby","Origin","Occupation","PictureLink","Strengths","Weaknesses","Powers","Skills","Personality"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [first_name + " " + last_name, str(age), race, gender, str(height_feet) + "'" + str(height_inches) + r"\"", str(weight) + " lbs", "None", origin, occupation, "None", strengths, weaknesses, powers, skills, personality] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            
            counter = 0
            response = "**RANDOM CHARACTER INFORMATION**\n\n"
            for field in dm_tracker[message.author.id]["fieldlist"]:
                response = response + "**" + field + ":** " + dm_tracker[message.author.id]["fielddict"][counter] + "\n"
                counter = counter + 1
            await reply_message(message, response)
            
            await direct_message(message, "Would you like to add this character to the applicant characters list? Respond **YES** to apply, anything else to discard.")
            return
                
            
        elif (command == 'getcharprofile'):
            records = await select_sql("""SELECT Fields FROM CustomProfiles WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                field_dict = { }
                for row in records:
                    fields = row[0].split(',')
                create_custom_profile = "SELECT " 
                get_display_name = "SELECT "
                create_tuple = ()
                for key in fields:
                    if key:
                        get_display_name = get_display_name + key + ", "
                        create_custom_profile = create_custom_profile + "IFNULL(" + key + ",'None'), "
                create_custom_profile = re.sub(r", $", "", create_custom_profile) + " FROM Server" + str(message.guild.id) + " WHERE Name=%s;"
                get_display_name = re.sub(r", $", "", get_display_name) + " FROM Server" + str(message.guild.id) + " WHERE Id=1;"
                get_user_id = """SELECT UserId FROM Server""" + str(message.guild.id) + """ WHERE Name=%s;"""
                user_record = await select_sql(get_user_id, (str(parsed_string),))
                for row in user_record:
                    username = "<@" + str(row[0]) + ">" #str(discord.utils.get(message.guild.members, id=int(row[0])))
                    
                await log_message("SQL: " + create_custom_profile)
                create_tuple = create_tuple + (parsed_string,)
                
                records1 = await select_sql(create_custom_profile, create_tuple)
                records2 = await select_sql(get_display_name)
                if not records1:
                    await reply_message(message, "Character not found!")
                    return
                response = "**CHARACTER PROFILE**\n\n"
                counter = 0
                response = response + "**Player:** " + username + "\n"
                for row in records1:
                    for field in fields:
                 
                        if counter > len(records2[0]) - 1:
                            break;
                        response = response + "**" + records2[0][counter] + ":** " + row[counter] + "\n"
                        counter = counter + 1
                await reply_message(message, response)
            else:    
                char_name = parsed_string
                
                get_character_profile = """SELECT CharacterName,IFNULL(Age,' '),IFNULL(Race,' '), IFNULL(Gender,' '), IFNULL(Height,' '), IFNULL(Weight,' '), IFNULL(PlayedBy,' '), IFNULL(Origin,' '), IFNULL(Occupation,' '), UserId, IFNULL(Biography,' '), IFNULL(Description,' '), IFNULL(Personality,' '), IFNULL(Powers,' '), IFNULL(Strengths,' '), IFNULL(Weaknesses,' '), IFNULL(Skills,' '), IFNULL(PictureLink,' ') FROM CharacterProfiles WHERE CharacterName=%s  AND ServerId=%s;"""
                char_tuple = (char_name, str(message.guild.id))
                
                records = await select_sql(get_character_profile, char_tuple)
                if len(records) < 1:
                    await reply_message(message, "No character found by that name!")
                    return
                for row in records:
                    # username = discord.utils.get(message.guild.members, id=int(row[9])).name
                    
                    embed = discord.Embed(title="Character Profile for " + row[0], description="Player: <@" + str(row[9]) + ">")
                    embed.add_field(name="Age",value=str(row[1]))
                    embed.add_field(name="Race",value=row[2])
                    embed.add_field(name="Gender",value=row[3])
                    embed.add_field(name="Height",value=row[4])
                    embed.add_field(name="Weight",value=row[5])
                    embed.add_field(name="Played by",value=row[6])
                    embed.add_field(name="Origin",value=row[7])
                    embed.add_field(name="Occupation",value=row[8])
                    print(str(row[17]))
                    if row[17].startswith('http'):
                        embed.set_thumbnail(url=row[17])
                        
                    response = ""
                    if row[10] != ' ':
                        response = response + "**Biography:** " + row[10] + "\n\n"
                    if row[11] != ' ':
                        response = response + "**Description:** " + row[11] + "\n\n"
                    if row[12] != ' ':
                        response = response + "**Personality:** " + row[12] + "\n\n"
                    if row[13] != ' ':
                        response = response + "**Powers:** " + row[13] + "\n\n"
                    if row[14] != ' ':
                        response = response + "**Strengths:** " + row[14] + "\n\n"
                    if row[15] != ' ':
                        response = response + "**Weaknesses:** " + row[15] + "\n\n"
                    if row[16] != ' ':
                        response = response + "**Skills:** " + row[16]
                        
                    if response != '':
                        response = "**ADDITIONAL INFORMATION**\n\n" + response
                    await message.channel.send(embed=embed)
                    #response = "***CHARACTER PROFILE***\n\n**Player:** `" + username + "`\n**Name:** " + row[0] + "\n**Age:** " + str(row[1]) + "\n**Race:** "+ row[2] + "\n**Gender:** " +row[3] + "\n**Height:** " + row[4] +  "\n**Weight:** " + row[5] +  "\n**Played by:** " + row[6] + "\n**Origin:** " + row[7] + "\n**Occupation:** " + row[8] +  "\n\n**ADDITIONAL INFORMATION**\n\n**Biography:** " + row[10] + "\n**Description:**" + row[11] + "\n**Personality:** " + row[12] + "\n**Powers:** " + row[13] + "\n**Strengths:** " + row[14] + "\n**Weaknesses:** " + row[15] + "\n**Skills:** " + row[16] + "\n\n**PICTURE**\n\n" + row[17] + "\n"
                await reply_message(message, response)
        elif command == 'editchar':
            user_id = message.author.id
            server_id = message.guild.id
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must have the NPC role to edit a character.")
                return
            records = await select_sql("""SELECT Fields FROM CustomProfiles WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                field_dict = { }
                for row in records:
                    fields = row[0].split(',')
                create_custom_profile = "SELECT " 
                get_display_name = "SELECT "
                create_tuple = ()
                for key in fields:
                    if key:
                        get_display_name = get_display_name + key + ", "
                        create_custom_profile = create_custom_profile + "IFNULL(" + key + ",'None'), "
                create_custom_profile = re.sub(r", $", "", create_custom_profile) + " FROM Server" + str(message.guild.id) + " WHERE Name=%s;"
                get_display_name = re.sub(r", $", "", get_display_name) + " FROM Server" + str(message.guild.id) + " WHERE Id=1;"
                await log_message("SQL: " + create_custom_profile)
                create_tuple = create_tuple + (parsed_string,)
                
                records1 = await select_sql(create_custom_profile, create_tuple)
                records2 = await select_sql(get_display_name)
                if not records1:
                    await reply_message(message, "Character not found!")
                    return
                counter = 0
                if message.author.id not in dm_tracker.keys():
                    await initialize_dm(message.author.id)   

                dm_tracker[message.author.id]["fieldlist"] = fields[:-1]
                dm_tracker[message.author.id]["fielddict"]= []
             
                for row in records1:
                    for field in fields:
                        if counter > len(records2[0]) - 1:
                            break;
                        dm_tracker[message.author.id]["fielddict"].append(row[counter])
                        
                        counter = counter + 1
           
                dm_tracker[message.author.id]["currentfield"] = 0

                dm_tracker[message.author.id]["currentcommand"] = 'editcustomchar'
                dm_tracker[message.author.id]["server_id"] = message.guild.id
                dm_tracker[message.author.id]["commandchannel"] = message.channel
                dm_tracker[message.author.id]["parameters"] = parsed_string
                
                counter = 0
                for row in dm_tracker[message.author.id]["fieldlist"]:
                    dm_tracker[message.author.id]["fielddict"].append(fields[counter])
                    counter = counter + 1
                    if counter > len(dm_tracker[message.author.id]["fieldlist"]) - 2:
                        break
                
                await reply_message(message, "Please check your DMs for instructions on how to edit a character, <@" + str(message.author.id) + ">.")
                
                await direct_message(message, "You have requested to edit the character **" + parsed_string + "**. Please type in the response the answer to each field to update, or *skip* to leave as is. When you have filled out all fields, the character will be updated!\nThe first field is **" + dm_tracker[message.author.id]["fieldlist"][0] + "** and its current value is **" + dm_tracker[message.author.id]["fielddict"][0] + "**.")                        
            else:
                char_name = parsed_string
                current_fields = await select_sql("""SELECT Age,Race,Gender,Height,Weight,Playedby,Origin,Occupation,PictureLink FROM CharacterProfiles WHERE ServerId=%s AND CharacterName=%s ;""", (str(message.guild.id), char_name))
                if not current_fields:
                    await reply_message(message, "No character found by that name!")
                    return
                records = await select_sql("""SELECT UserId FROM CharacterProfiles WHERE ServerId=%s AND CharacterName=%s """,(str(message.guild.id), char_name))
                for row in records:
                    char_user_id = int(row[0])
                if char_user_id != message.author.id and not role_check(guild_settings[message.guild.id]["AdminRole"],message.author):
                    await reply_message(message, "This isn't your character!")
                    return   
                for row in current_fields:
                    fields = row
                 
                if message.author.id not in dm_tracker.keys():
                    await initialize_dm(message.author.id)
                dm_tracker[message.author.id]["fieldlist"] = ["CharacterName","Age","Race","Gender","Height","Weight","Playedby","Origin","Occupation","PictureLink"]
                dm_tracker[message.author.id]["currentfield"] = 0
                dm_tracker[message.author.id]["fielddict"]= []
                dm_tracker[message.author.id]["fielddict"].append(parsed_string)
                dm_tracker[message.author.id]["currentcommand"] = 'editchar'
                dm_tracker[message.author.id]["server_id"] = message.guild.id
                dm_tracker[message.author.id]["commandchannel"] = message.channel
                dm_tracker[message.author.id]["parameters"] = parsed_string
                dm_tracker[message.author.id]["parameters2"] = char_user_id
                counter = 0
                for row in dm_tracker[message.author.id]["fieldlist"]:
                    dm_tracker[message.author.id]["fielddict"].append(fields[counter])
                    counter = counter + 1
                    if counter > len(dm_tracker[message.author.id]["fieldlist"]) - 2:
                        break
                
                await reply_message(message, "Please check your DMs for instructions on how to edit a character, <@" + str(message.author.id) + ">.")
                
                await direct_message(message, "You have requested to edit the character **" + parsed_string + "**. Please type in the response the answer to each field to update, or *skip* to leave as is. When you have filled out all fields, the character will be updated!\nThe first field is **" + dm_tracker[message.author.id]["fieldlist"][0] + "** and its current value is **" + dm_tracker[message.author.id]["fielddict"][0] + "**.")
            

        elif command == 'listmychars':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must have the NPC role to list characters.")
                return
            records = await select_sql("""SELECT Fields FROM CustomProfiles WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                get_chars = """SELECT Name FROM Server""" + str(message.guild.id) +  """ WHERE UserId=%s;"""
                records = await select_sql(get_chars, (str(message.author.id),))
                if not records:
                    await reply_message(message, "No records found for that user!")
                    return                
                response = "**Your character list:**\n\n"
                
                for row in records:
                    response = response + row[0] + "\n"
                await reply_message(message, response)
            else:    
                records = await select_sql("""SELECT CharacterName FROM CharacterProfiles WHERE ServerId=%s AND UserId=%s;""", (str(message.guild.id),str(message.author.id)))
                if not records:
                    await reply_message(message, "You don't have any characters! Use //newchar to create a character!")
                    return
                response = "**Characters for " + message.author.name + ":**\n\n" 
                for row in records:
                    response = response + row[0] + "\n"
                await reply_message(message, response)




        elif command == 'deletechar':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must be member of the NPC role to delete a character!")
                return
                
            if not parsed_string:
                await reply_message(message, "No character specified!")
                return
                
            char_name = parsed_string
            records = await select_sql("""SELECT Fields FROM CustomProfiles WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                records2 = await select_sql("""SELECT UserId FROM Server""" + str(message.guild.id) + """ WHERE Name=%s;""",(str(char_name),))
                if not records2:
                    await reply_message(message, "That custom character doesn't exist!")
                    return
                for row in records2:
                    if int(row[0]) != message.author.id and not role_check(guild_settings[message.guild.id]["AdminRole"],message.author):
                        await reply_message(message, "This isn't your character!")
                        return
                
                result = await commit_sql("""DELETE FROM Server""" + str(message.guild.id) + """ WHERE Name=%s AND UserId=%s;""",(parsed_string,str(message.author.id)))
                await reply_message(message, char_name + " deleted from server!")
                return
                
            records = await select_sql("""SELECT UserId,Id FROM CharacterProfiles WHERE ServerId=%s AND CharacterName=%s ;""", (str(message.guild.id), char_name))
            if not records:
                await reply_message(message, "That character does not exist!")
                return
            for row in records:
                user_id = int(row[0])
                char_id = row[1]
            if user_id != message.author.id and not role_check(guild_settings[message.guild.id]["AdminRole"],message.author):
                await reply_message(message, "This isn't your character!")
                return
            result = await commit_sql("""DELETE FROM CharacterProfiles WHERE Id=%s;""",(char_id,))
            if result:
                await reply_message(message, "Character " + char_name + " deleted from server!")
            else:
                await reply_message(message, "Database error!")
        elif command == 'deletecustomprofile':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must be a member of the admin role to delete the custom profile!")
                return        
            if parsed_string == 'yes':
                result = await commit_sql("""DROP TABLE Server""" + str(message.guild.id) + """;""")
                result = await commit_sql("""DELETE FROM CustomProfiles WHERE ServerId=%s;""",(str(message.guild.id),))
                await reply_message(message, "All custom profiles deleted from server!")
            else:
                await reply_message(message, "You need to include **yes** (without bold) after the command to confirm deletion. This deletes all character profiles!")
        elif command == 'setnpc':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must be a member of the NPC role to create NPCs!")
                return
            if not parsed_string:
                await reply_message(message, "No NPC shortcut specified!")
                return
            records = await select_sql("""SELECT Id FROM NonPlayerCharacters WHERE ServerId=%s AND Shortcut=%s;""",(str(message.guild.id),str(parsed_string)))
            if not records:
                await reply_message(message, "That NPC doesn't exist!")
                return

            npc_aliases[message.guild.id][message.author.id][message.channel.id] = parsed_string
            await reply_message(message, "User <@" + str(message.author.id) + "> set alias to " + parsed_string + " in channel " + message.channel.name + ".")
        elif command == 'unsetnpc':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must be a member of the NPC role to create NPCs!")
                return
            npc_aliases[message.guild.id][message.author.id][message.channel.id] = ""
            await reply_message(message, "User <@" + str(message.author.id) + "> cleared alias in channel " + message.channel.name + ".")            
        elif command == 'newnpc':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must be a member of the NPC role to create NPCs!")
                return
            users_allowed = message.mentions
            if not users_allowed:
                await reply_message(message, "No users allowed to use the NPC specified!")
                return
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'newnpc'
            dm_tracker[message.author.id]["fieldlist"] = ["CharName","Shortcut","PictureLink"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            dm_tracker[message.author.id]["parameters"] = message.mentions
            
            await reply_message(message, "Please check your DMs for instructions on how to create a new NPC, <@" + str(message.author.id) + ">.")
            
            await direct_message(message, "You have requested a new NPC! Please type in the response the **name of the character**, and then enter each field as a reply to the DMs. When you have filled out all fields, the character will be created!")

            await post_webhook(message.channel, "Narrator", "--scene paused--", narrator_url)
          #  await message.delete()
        elif command == 'unpause':
            await post_webhook(message.channel, "Narrator", "--scene resumed--", narrator_url)
          #  await message.delete()
        elif command == 'newscene':
            await post_webhook(message.channel, "Narrator", "--new scene--", narrator_url)
          #  await message.delete()
        elif command == 'endscene':
            await post_webhook(message.channel, "Narrator", "--end scene--", narrator_url)
         #   await message.delete()
        elif command =='postnarr':
            await post_webhook(message.channel, "Narrator", parsed_string, narrator_url)    
         #   await message.delete()  
        elif command == 'postnpc':
            shortcut = command_string[1]
            parsed_string = re.sub(r"\b" + shortcut + r"\b ","", message.content.replace("//postnpc ",""))
            
            if not shortcut:
                await reply_message (message, "No NPC specified!")
                return
            get_npc = """SELECT UsersAllowed, CharName, PictureLink FROM NonPlayerCharacters WHERE ServerId=%s AND Shortcut=%s;"""
            npc_tuple = (str(message.guild.id), shortcut)
            records = await select_sql(get_npc, npc_tuple)
            for row in records:
                if str(message.author.id) not in row[0]:
                    await reply_message(message, "<@" + str(message.author.id) + "> is not allowed to use NPC " + row[1] + "!")
                    return
                response = parsed_string
               
#                await message.guild.me.edit(nick=row[1])
                URL = row[2]
                #pfp = requests.get(url = URL)

#                await client.user.edit(avatar=pfp)
 #               await reply_message(message, response)
                webhook_list = await message.channel.webhooks()
                webhook_found = False
                for hook in webhook_list:
                    if hook.name == 'RPCompanion':
                        webhook_found = True
                        temp_webhook = hook
                if not webhook_found:
                    temp_webhook = await message.channel.create_webhook(name='RPCompanion')
                if URL !='None' and URL:
                    last_message[message.guild.id][message.author.id] = await temp_webhook.send(content=response, username=row[1], avatar_url=URL,wait=True)
                else:
                    last_message[message.guild.id][message.author.id] = await temp_webhook.send(content=response, username=row[1],wait=True)
                print(last_message[message.guild.id][message.author.id])
             #   await message.delete()
                await asyncio.sleep(1)
                #await temp_webhook.delete()
#                await client.user.edit(avatar=current_pfp)
#                await message.guild.me.edit(nick=current_name)
        elif command == 'editnpcpost':
            try:
                last_message[message.guild.id][message.author.id]
            except:
                await reply_message(message, "No previous NPC post found for you.")
                return
            webhook_list = await message.channel.webhooks()
            webhook_found = False
            for hook in webhook_list:
                if hook.name == 'Chara-Tron':
                    webhook_found = True
                    temp_webhook = hook
            if not webhook_found:
                await reply_message(message, "No webhook found in this channel.")
                return
            await last_message[message.guild.id][message.author.id].edit(content=parsed_string)
              #  await reply_message(message, "No message to edit found.")
           # await message.delete()   
        elif command == 'deletenpc':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must be a member of the NPC role to delete NPCs!")
                return        
            if not parsed_string:
                await reply_message(message, "No NPC name specified!")
                return
            result = await commit_sql("""DELETE FROM NonPlayerCharacters WHERE ServerId=%s AND CharName=%s""", (str(message.guild.id),parsed_string.strip()))
            if result:
                await reply_message(message, "NPC " + parsed_string + " deleted.")
            else:
                await reply_message(message, "Database error!")
        elif command == 'editnpc':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must be a member of the NPC role to edit NPCs!")
                return
            users_allowed = message.mentions
            if not users_allowed:
                await reply_message(message, "No users allowed to use the NPC specified!")
                return
            records = await select_sql("""SELECT CharName,Shortcut,PictureLink FROM NonPlayerCharacters WHERE ServerId=%s AND CharName=%s;""",(str(message.guild.id),re.sub(r"<.*>","",parsed_string).strip()))
            if not records:
                await reply_message(message, "No NPC found with that name!")
                return
            for row in records:
                fields = row
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["currentcommand"] = 'editnpc'
            dm_tracker[message.author.id]["fieldlist"] = ["CharName","Shortcut","PictureLink"]                                                     
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["fieldmeans"] = ["NPC Name","The shortcut to use when posting as the NPC","Direct upload or Internet http link for the NPC"]
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            dm_tracker[message.author.id]["parameters"] = message.mentions
            dm_tracker[message.author.id]["parameters2"] = re.sub(r"<.*>","",parsed_string).strip()
            counter = 0
            for row in dm_tracker[message.author.id]["fieldlist"]:
                dm_tracker[message.author.id]["fielddict"].append(fields[counter])
                counter = counter + 1
      
            await reply_message(message, "Please check your DMs for instructions on how to edit a NPC, <@" + str(message.author.id) + ">.")
            
            await direct_message(message, "You have requested to edit the NPC **" + parsed_string + "**. Please type in the response the answer to each field to update, or *skip* to leave as is. When you have filled out all fields, the spell will be updated!\nThe first field is **" + dm_tracker[message.author.id]["fieldlist"][0] + "** and its current value is **" + dm_tracker[message.author.id]["fielddict"][0] + "**.")  
                

 

        elif command == 'changecharowner':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must be a member of the admin role to change character owners!")
                return
                
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
               
            dm_tracker[message.author.id]["currentcommand"] = 'changecharowner'
            # BuffName VARCHAR(100), ManaCost Int, MinimumLevel Int, StatMod VARCHAR(30), Modifier Int, Description TEXT,
            dm_tracker[message.author.id]["fieldlist"] = ["Id","UserId"]                                                   
            dm_tracker[message.author.id]["currentfield"] = 0
            dm_tracker[message.author.id]["fielddict"] = [] 
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            menu = await make_simple_menu(message, "CharacterProfiles","CharacterName")
            await reply_message(message, "Please check your DMs for instructions on how to change a character owner, <@" + str(message.author.id) + ">.")
            
            await direct_message(message, "You have requested a character owner change! Please type in the response the **ID of the character**, and then enter each field as a reply to the DMs. When you have filled out all fields, the owner will be updated!\n\n" + menu)                
   

        elif command == 'lurk':
            if message.author.nick:
                name = message.author.nick
            else:
                name = message.author.name
            responses = ["*" + name + " lurks in the shadowy rafters with luminous orbs with parted tiers, trailing long digits through their platinum tresses.*", "**" +name + ":** ::lurk::", "*" + name + " flops on the lurker couch.*", name + ": *double lurk*",name + ": *luuuuuurk*",name + ": *posts that they are lurking so someone notices they are lurking*"]
            await reply_message(message, random.choice(responses))
          #  await message.delete()
        elif command == 'ooc':
            if message.author.nick:
                name = message.author.nick
            else:
                name = message.author.name        
            await reply_message(message, "**" + name + ":** ((*" + parsed_string + "*))")
          #  await message.delete()
        elif command == 'me':
            if message.author.nick:
                name = message.author.nick
            else:
                name = message.author.name        
            await reply_message(message, "((*-" + name + " " + parsed_string + "-*))")
           # await message.delete()
        elif command == 'endconvo':
            await post_webhook(message.channel, dialog_tracker[message.guild.id][message.author.id]["CharacterName"], "Nice talking with you.", dialog_tracker[message.guild.id][message.author.id]["PictureLink"])
            del dialog_tracker[message.guild.id][message.author.id]
        elif command == 'converse':
            if not parsed_string:
                await reply_mesage(message, "You didn't specify anyone to converse with!")
                return
            records = await select_sql("""SELECT Id,RootDialogList,PictureLink,CharacterName,InitialDialog FROM DialogCharacters WHERE ServerId=%s AND CharacterName=%s;""",(str(message.guild.id),str(parsed_string)))
            dialog_tracker[message.guild.id][message.author.id] = {}
            if not records:
                await reply_message(message, "There's no one to talk to by that name!")
                return
            for row in records:
                dialog_tracker[message.guild.id][message.author.id]["channel"] = message.channel
                dialog_tracker[message.guild.id][message.author.id]["CharacterId"] = row[0]
                dialog_tracker[message.guild.id][message.author.id]["RootDialogList"] = row[1].split(',')
                dialog_tracker[message.guild.id][message.author.id]["DialogMap"] = { }
                dialog_tracker[message.guild.id][message.author.id]["PictureLink"] = row[2]
                dialog_tracker[message.guild.id][message.author.id]["CharacterName"] = row[3]
                dialog_tracker[message.guild.id][message.author.id]["CurrentDialogId"] = '0'
                initial_dialog = row[4]
                
            dialog_menu = "> " + initial_dialog + "\n\n```"
            counter = 1
            for dialog_id in dialog_tracker[message.guild.id][message.author.id]["RootDialogList"]:
                records = await select_sql("""SELECT Response,RoleRequiredId FROM Dialog WHERE Id=%s;""",(str(dialog_id),))
                for row in records:
                    role_required = discord.utils.get(message.guild.roles,id=int(row[1]))
                    role_found = False
                    for role in message.author.roles:
                        if role == role_required or role_required is None:
                            role_found = True
                    if not role_found:
                        dialog_tracker[message.guild.id][message.author.id]["RootDialogList"].remove(dialog_id)
                        continue
                    dialog_menu = dialog_menu + str(dialog_options[counter]) + " - " + row[0] + "\n"
                    
                    dialog_tracker[message.guild.id][message.author.id]["DialogMap"][counter] = dialog_id
                    counter = counter + 1
            dialog_tracker[message.guild.id][message.author.id]["CurrentMessage"] = await post_webhook(message.channel, dialog_tracker[message.guild.id][message.author.id]["CharacterName"], dialog_menu + "```", dialog_tracker[message.guild.id][message.author.id]["PictureLink"])
            await asyncio.sleep(2)
            counter = 1
            dialog_tracker[message.guild.id][message.author.id]["RootDialogList"] = list(filter(None,dialog_tracker[message.guild.id][message.author.id]["RootDialogList"]))
            for dialog_id in dialog_tracker[message.guild.id][message.author.id]["RootDialogList"]:
                await dialog_tracker[message.guild.id][message.author.id]["CurrentMessage"].add_reaction(str(dialog_options[counter]))
           
                counter = counter + 1
                
        elif command == 'randomooc':
            if not message.mentions:
                await reply_message(message,"You didn't specify a user to OOC!")
                return
            if message.author.nick:
                name = message.author.nick
            else:
                name = message.author.name        
            responses = ["flops on","rolls around","curls on","lurks by","farts near","falls asleep on","throws Skittles at","throws popcorn at","huggles","snugs","hugs","snuggles","tucks in","watches","stabs","slaps","sexes up","tickles","thwaps","pinches","smells","cries with","laughs at","fondles","stalks","leers at","creeps by","lays on","glomps","clings to","flirts with","makes fun of","nibbles on","noms","protects","stupefies","snickers at"]
            #usernames = message.guild.members
            #user = random.choice(usernames)
            if parsed_string:
                user_id = message.mentions[0].id
            else:
                user_id = user.id
            response = "((*" + name + " " + random.choice(responses) + " <@" + str(user_id) + ">*))"
            await reply_message(message, response)
 
        elif command == 'editcharinfo':
            if not role_check(guild_settings[message.guild.id]["NPCRole"], message.author):
                await reply_message(message, "You must be a member of the NPC role to edit character info!")
                return        

            current_fields = await select_sql("""SELECT IFNULL(Biography,'None'),IFNULL(Skills,'None'),IFNULL(Strengths,'None'),IFNULL(Weaknesses,'None'),IFNULL(Powers,'None'),IFNULL(Personality,'None'),IFNULL(Description,'None'),UserId FROM CharacterProfiles WHERE ServerId=%s AND CharacterName=%s;""", (str(message.guild.id), parsed_string))
            if not current_fields:
                await reply_message(message, "No character found by that name!")
                return
            for row in current_fields:
                fields = row
            player=  fields[-1]
            fields = fields[:-1]
            if message.author.id not in dm_tracker.keys():
                await initialize_dm(message.author.id)
            dm_tracker[message.author.id]["fieldlist"] = ["CharacterName","Biography","Skills","Strengths","Weaknesses","Powers","Personality","Description"]
            dm_tracker[message.author.id]["currentfield"] = 1
            dm_tracker[message.author.id]["fielddict"]= []
            dm_tracker[message.author.id]["fielddict"].append(parsed_string)
            dm_tracker[message.author.id]["currentcommand"] = 'editcharinfo'
            dm_tracker[message.author.id]["server_id"] = message.guild.id
            dm_tracker[message.author.id]["commandchannel"] = message.channel
            dm_tracker[message.author.id]["parameters"] = parsed_string
            dm_tracker[message.author.id]["parameters2"] = str(player)
            counter = 0
            for row in dm_tracker[message.author.id]["fieldlist"]:
                dm_tracker[message.author.id]["fielddict"].append(fields[counter])
                counter = counter + 1
                if counter > len(dm_tracker[message.author.id]["fieldlist"]) - 2:
                    break
            
            await reply_message(message, "Please check your DMs for instructions on how to edit a character, <@" + str(message.author.id) + ">.")
            
            await direct_message(message, "You have requested to edit the character**" + parsed_string + "**. Please type in the response the answer to each field to update, or *skip* to leave as is. When you have filled out all fields, the character will be updated!\nThe first field is **" + dm_tracker[message.author.id]["fieldlist"][1] + "** and its current value is **" + dm_tracker[message.author.id]["fielddict"][1] + "**.")             


                    
 
        elif command == 'setnpcrole':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must be a member of the admin role to set other roles!")
                return        
            if len(message.role_mentions) > 1:
                await reply_message(message, "Only one role can be defined as the GM role!")
                return
            if not message.role_mentions:
                await reply_message(message, "You did not specify a role!")
                return                
            role_id = message.role_mentions[0].id
            guild_settings[message.guild.id]["NPCRole"] = role_id
            result = await commit_sql("""UPDATE GuildSettings SET NPCRole=%s WHERE ServerId=%s;""", (str(role_id),str(message.guild.id)))
            if result:
                await reply_message(message, "NPC role successfully set!")
            else:
                await reply_message(message, "Database error!")
        elif command == 'listroles':
            records = await select_sql("""SELECT IFNULL(AdminRole,'0'),IFNULL(NPCRole, '0'),IFNULL(NPCRole,'0') FROM GuildSettings WHERE ServerId=%s;""", (str(message.guild.id),))
            if not records:
                await reply_message(message, "Database error!")
                return
            for row in records:
                
                admin_role = message.guild.get_role(int(row[0]))
                npc_role = message.guild.get_role(int(row[1]))
                player_role = message.guild.get_role(int(row[2]))
            response = "**Server Roles**\n\n**Admin Role:** " + str(admin_role) + "\n**NPC Role:** " + str(npc_role) + "\n**Player Role:** " + str(player_role) + "\n"
            await reply_message(message, response)
 
        elif command == 'listsetup':
            server_id = message.guild.id
            records = await select_sql("""SELECT ServerId,IFNULL(AdminRole,'0'),IFNULL(NPCRole,'0') FROM GuildSettings WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await reply_message(message, "Not all settings found.")
                return
            for row in records:
                guild_settings[server_id]["AdminRole"] = int(row[1])
                guild_settings[server_id]["NPCRole"] = int(row[2])
            response = "**CURRENT SERVER SETTINGS**\n\n"
            for setting in list(guild_settings[server_id].keys()):
                if guild_settings[message.guild.id][setting] == 0:
                    setting_value = "Not set or 0"
                else:
                    setting_value = str(guild_settings[message.guild.id][setting])
                response = response + "**" + setting + ":** " + setting_value +  "\n"
            await reply_message(message, response)
            
  
        elif command == 'addnpcuser':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must be a member of the admin role to add NPC Managers!")
                return
            if not message.mentions:
                await reply_message(message, "You didn't specify any users to add!")
                return
            role = discord.utils.get(message.guild.roles, id=guild_settings[message.guild.id]["NPCRole"])
            for user in message.mentions:
                print("USer" + str(user.id))
                user_object = await message.guild.fetch_member(int(user.id))
                await asyncio.sleep(1)
                print(user_object)
                await user_object.add_roles(role)
            await reply_message(message, "Users added to NPC role!")                
        elif command == 'addadmin':
            if message.author != message.guild.owner:
                await reply_message(message, "Only the server owner can add admins!")
                return
            if not message.mentions:
                await reply_message(message, "You didn't specify any users to add!")
                return
            role = discord.utils.get(message.guild.roles, id=guild_settings[message.guild.id]["AdminRole"])
            for user in message.mentions:
                user_object = await message.guild.fetch_member(int(user.id))
                await user.add_roles(role)
            await reply_message(message, "Users added to admin role!")                 

        elif command == 'deletenpcuser':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must be a member of the admin role to remove NPC Managers!")
                return 
            if not message.mentions:
                await reply_message(message, "You didn't specify any users to remove!")
                return
            role = discord.utils.get(message.guild.roles, id=guild_settings[message.guild.id]["NPCRole"])
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
        elif command == 'listnpcs':
            response = "***CURRENT NPC LIST***\n\n__Alt Name__ - __Allowed Users__ __Shortcut__\n"
            records = await select_sql("""SELECT CharName,UsersAllowed,Shortcut FROM NonPlayerCharacters WHERE ServerId=%s;""", (str(message.guild.id),))
            name_re = re.compile(r"Member id=.*?name='(.+?)'")

            for row in records:
                m = name_re.findall(row[1])
                if m:
                    names = re.sub(r"[\[\]']","",str(m))
                response = response + row[0] + " - " + str(names) + " - " + row[2] + "\n"
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
            await reply_message(message, "**WARNING! THIS WILL WIPE ALL SERVER SETTINGS, INCLUDING CHARACTERS, ITEMS, VENDORS, SPELLS, MONSTERS, MELEE ATTACKS, AND SERVER SETTINGS FROM THE BOT! PLEASE REPLY TO THE DM WITH** ```CONFIRM``` **TO PROCEED.**")
            await direct_message(message, "**WARNING! THIS WILL WIPE ALL SERVER SETTINGS, INCLUDING CHARACTERS, ITEMS, VENDORS, SPELLS, MONSTERS, MELEE ATTACKS, AND SERVER SETTINGS FROM THE BOT! PLEASE REPLY TO THE DM WITH** ```CONFIRM``` **TO PROCEED.**\n\nAre you sure you want to do this?")
        elif command == 'newcustomprofile':
            if not role_check(guild_settings[message.guild.id]["AdminRole"], message.author):
                await reply_message(message, "You must be a member of the admin role to set the custom profile!")
                return
            if not parsed_string:
                await reply_message(message, "No fields were specified for the custom profile!")
                return
           
            fields = parsed_string.split(',')
            field_name = " "
            for line in fields:
                if line.split('=')[0] == 'Name':
                    field_name=field_name + "CustomNameField, "
                else:
                    field_name = field_name + line.split('=')[0] + ","
            custom_profile_entry = """INSERT INTO CustomProfiles (ServerId, Fields) VALUES (%s,%s);"""
            result = await commit_sql(custom_profile_entry, (str(message.guild.id), "Name," + field_name))
            if not result:
                await reply_message(mesage, "Could not create custom profile!")
                return
            create_custom_profile = "CREATE TABLE Server" + str(message.guild.id) + " (Id int auto_increment, ServerId varchar(40), UserId varchar(40), Name TEXT, "
            custom_profile_tuple = (str(message.guild.id), str(message.author.id), "Name")
            display_name_entry = "INSERT INTO Server" + str(message.guild.id) + " (ServerId, UserId, Name, " 
            display_name_values = " VALUES (%s, %s, %s, "
            for field in fields:
                split_fields = field.split('=')
                display_name = split_fields[1]
                if split_fields[0] == 'Name':
                    next_name = 'CustomNameField'
                else:
                    next_name = split_fields[0]
                create_custom_profile = create_custom_profile + next_name + " TEXT, "
                custom_profile_tuple = custom_profile_tuple + (display_name,)
                display_name_values = display_name_values + "%s, "
                display_name_entry = display_name_entry + next_name + ", "
            create_custom_profile = create_custom_profile + " PRIMARY KEY(Id));"
            await log_message("SQL: " + create_custom_profile)
            result = await execute_sql(create_custom_profile)
            if result:
                await reply_message(message, "Custom profile for server successfully created!")
            else:
                await reply_message(message, "Database error! Please ensure your field names have no spaces and are separated by commas!")
            
            display_name_entry = re.sub(r", $","", display_name_entry) + ")" + re.sub(r", $","", display_name_values) + ");"
            
            result = await commit_sql(display_name_entry, custom_profile_tuple)
            if result:
                await reply_message(message, "Display names for fields set successfully.")
            else:
                await reply_message(message, "Database error!")
        elif command == 'invite':
            await reply_message(message,"`Click here to invite Companion:` https://discord.com/api/oauth2/authorize?client_id=701097740335186033&permissions=805432320&scope=bot")
        else:
            pass   
@client.event
async def on_interaction(member, interaction):
    global command_handler
    global slash_commands
    print("called here" + str(interaction))
    slash_commands.convert_to_message(interaction, member, "//")

    #await interact_reply.send_message(content="Success.", ephemeral=True)
    
    
 #       await irs.send_message("<@" + str(member.id) + ">", embed=msg, ephemeral=True)



# def exception_handler(loop,context):
   # print("Caught the following exception")
   # print(context['message'])          
client.run'REDACTED'

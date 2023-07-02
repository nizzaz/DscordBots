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



client = discord.Client()

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    try:
        connection = mysql.connector.connect(host='localhost', database='HiBot', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='HiBot', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='HiBot', user='REDACTED', password='REDACTED')
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
            
server_settings = {}

@client.event
async def on_ready():
    global server_settings
    await log_message("Logged into Discord!")
    records = await select_sql("""SELECT ServerId,Greeting,Farewell,Rules,MessageChannel,CommandRole FROM ServerSettings;""")
    for row in records:
        server_id = int(row[0])
        server_settings[server_id] = { }
        server_settings[server_id]["Greeting"] = row[1]
        server_settings[server_id]["Farewell"] = row[2]
        server_settings[server_id]["Rules"] = row[3]
        if row[4] is None:
            server_settings[server_id]["MessageChannel"] = None
        else: 
            server_settings[server_id]["MessageChannel"] = int(row[4])
        if row[5] is None:
            server_settings[server_id]["CommandRole"] = None
        else: 
            server_settings[server_id]["CommandRole"] = int(row[5])

    await log_message("SQL loaded!")
    
    for guild in client.guilds:
        try: server_settings[guild.id]
        except KeyError:
            server_settings[guild.id] = { }
            result = await commit_sql("""INSERT INTO ServerSettings (ServerId) VALUES (%s);""", (str(guild.id),))
        try: server_settings[guild.id]["MessageChannel"]
        except KeyError: server_settings[guild.id]["MessageChannel"] = guild.system_channel
            
            

        
@client.event
async def on_guild_join(guild):
    global server_settings
    
    await log_message("Joined guild " + guild.name)
    try: server_settings[guild.id]
    except KeyError:
        server_settings[guild.id] = { }
        result = await commit_sql("""INSERT INTO ServerSettings (ServerId) VALUES (%s);""", (str(guild.id),))
    try: server_settings[guild.id]["MessageChannel"]
    except KeyError: server_settings[guild.id]["MessageChannel"] = guild.system_channel 
    
@client.event
async def on_guild_remove(guild):
    global server_settings
    await log_message("Left guild " + guild.name)
    result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s""",(str(guild.id),))
    server_settings[guild.id] = { }
    
@client.event
async def on_member_join(member):
    global server_settings
    
    await log_message("Member " + member.name + " joined guild " + member.guild.name)
    try: 
        server_settings[member.guild.id]["Greeting"]
        message_channel = client.get_channel(server_settings[member.guild.id]["MessageChannel"])
        await message_channel.send(">>> " + server_settings[member.guild.id]["Greeting"] + " <@" + str(member.id) + ">")
    except KeyError:
        pass

@client.event
async def on_member_remove(member):
    global server_settings
    await log_message("Member " + member.name + " left guild " + member.guild.name)
    try: 
        server_settings[member.guild.id]["Farewell"]
        message_channel = client.get_channel(server_settings[member.guild.id]["MessageChannel"])
        await message_channel.send(">>> " + server_settings[member.guild.id]["Farewell"] + " " + member.name)
    except KeyError:
        pass    
    
@client.event
async def on_message(message):
    global server_settings
    
    if message.author == client.user:
        return
    if message.author.bot:
        return
        
    if message.content.startswith('hibot'):


        command_string = message.content.split(' ')
        command = command_string[1]
        parsed_string = message.content.replace("hibot " + command + " ","")
        username = message.author.name
        server_name = message.guild.name
        user_id = message.author.id
        server_id = message.guild.id
        await log_message("Received command of " + message.content + " with command of " + command + " and parsed string of  " + parsed_string)
        
        if command == 'setgreeting':
            if server_settings[server_id]["CommandRole"] is None:
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no command role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["CommandRole"], message.author):
                    await send_message(message, "You are not in the command role!")
                    return               

            if not parsed_string:
                await send_message(message, "No greeting speciifed!")
                return
            server_settings[server_id]["Greeting"] = parsed_string
            result = await commit_sql("""UPDATE ServerSettings SET Greeting=%s WHERE ServerId=%s;""",(parsed_string, str(server_id)))
            if result:
                await send_message(message, "Successfully set greeting to " + parsed_string + "!")
            else:
                await send_message(message, "Database error!")
                

        elif command == 'setfarewell':
            if server_settings[server_id]["CommandRole"] is None:
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no command role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["CommandRole"], message.author):
                    await send_message(message, "You are not in the command role!")
                    return   


            if not parsed_string:
                await send_message(message, "No farewell speciifed!")
                return                    
            server_settings[server_id]["Farewell"] = parsed_string
            result = await commit_sql("""UPDATE ServerSettings SET Farewell=%s WHERE ServerId=%s;""",(parsed_string, str(server_id)))
            if result:
                await send_message(message, "Successfully set greeting to " + parsed_string + "!")
            else:
                await send_message(message, "Database error!")
                

        elif command == 'addrules': 
            if server_settings[server_id]["CommandRole"] is None:
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no command role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["CommandRole"], message.author):
                    await send_message(message, "You are not in the command role!")
                    return   


            if not parsed_string:
                await send_message(message, "No rules speciifed!")
                return
            records = await select_sql("""SELECT IFNULL(Rules,' ') FROM ServerSettings WHERE ServerId=%s;""", (str(server_id),))
            if not records:
                rules = " "
            else:
                for row in records:
                    rules = row[0]
            server_settings[server_id]["Rules"] = rules + parsed_string
            result = await commit_sql("""UPDATE ServerSettings SET Rules=%s WHERE ServerId=%s;""",(rules + parsed_string, str(server_id)))
            if result:
                await send_message(message, "Successfully added rules as " + parsed_string + "!")
            else:
                await send_message(message, "Database error!")
        elif command == 'clearrules':
            if server_settings[server_id]["CommandRole"] is None:
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no command role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["CommandRole"], message.author):
                    await send_message(message, "You are not in the command role!")
                    return   

 
            server_settings[server_id] = {} 
            result = await commit_sql("""UPDATE ServerSettings SET Rules='' WHERE ServerId=%s;""", (str(server_id),))
            if result:
                await send_message(message, "Rules successfully cleared.")
            else:
                await send_message(message, "Database error!")
        elif command == 'clearall':
            if server_settings[server_id]["CommandRole"] is None:
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no command role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["CommandRole"], message.author):
                    await send_message(message, "You are not in the command role!")
                    return    
 
            if not role_check(server_settings[message.guild.id]["CommandRole"], message.author):
                await send_message(message, "You are not in the command role!")
                return
            result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s; INSERT INTO ServerSettings (ServerId) VALUES (%s);""", (str(server_id),str(server_id)))
            if result:
                await send_message(message, "Rules successfully cleared.")
            else:
                await send_message(message, "Database error!")
                
        elif command == 'help' or command == 'info':
            pass
        elif command == 'setmessagechannel':
            if server_settings[server_id]["CommandRole"] is None:
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no command role has been set! Unable to set message channel!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["CommandRole"], message.author):
                    await send_message(message, "You are not in the command role!")
                    return    
            server_settings[server_id]["MessageChannel"] = message.channel_mentions[0].id
            result = await commit_sql("""UPDATE ServerSettings SET MessageChannel=%s WHERE ServerId=%s;""",(str(message.channel_mentions[0].id),str(server_id)))
            if result:
                await send_message(message, "M<essage channel successfully set to " + message.channel_mentions[0].name + ".")
            else:
                await send_message(message, "Database error!")            

                        
        elif command == 'setcomamndrole':
            if message.author != message.guild.owner:
                await send_message(message, "You are not the server owner! Unable to set command role!")
                return
            if not message.role_mentions:
                await send_message(message, "No roles mentioned for the command role!")
                return
            server_settings[server_id]["CommandRole"] = message.role_mentions[0].id
            result = await commit_sql("""UPDATE ServerSettings SET CommandRole=%s WHERE ServerId=%s;""",(str(message.role_mentions[0].id),str(server_id)))
            if result:
                await send_message(message, "Command role successfully set to " + message.role_mentions[0].name + ".")
            else:
                await send_message(message, "Database error!")
        elif command == 'showgreeting':
            if server_settings[server_id]["Greeting"] is None:
                await send_message(message, "Server Greeting not set.")
            else:
                await send_message(message, "Server Greeting:\n\n" + server_settings[server_id]["Greeting"])
                
        elif command == 'showfarewell':
            if server_settings[server_id]["Farewell"] is None:
                await send_message(message, "Server Farewell not set.")
            else:
                await send_message(message, "Server Farewell:\n\n" + server_settings[server_id]["Farewell"])      
        elif command == 'showrules':
            if server_settings[server_id]["Rules"] is None:
                await send_message(message, "Server Rules not set.")
            else:
                await send_message(message, "Server Rules:\n\n" + server_settings[server_id]["Rules"])        
        elif command == 'showcommandrole':
            if server_settings[server_id]["CommandRole"] is None:
                await send_message(message, "Server CommandRole not set.")
            else:
                await send_message(message, "Server CommandRole:\n\n" + server_settings[server_id]["CommandRole"])
                
        else:
            pass

client.run'REDACTED'
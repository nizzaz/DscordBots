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
import json
import decimal
import asyncio

intents = discord.Intents(messages=True,guilds=True, message_content=True)
client = discord.Client(heartbeat_timeout=600, intents=intents)


new_startup = True

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='Snarcus', user='REDACTED', password='REDACTED')    
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
    if sql_query != 'SELECT UsersAllowed, CharName, PictureLink FROM Alts WHERE ServerId=%s AND Shortcut=%s;' and sql_query != 'SELECT Id,CharacterName,Currency,Experience FROM CharacterProfiles WHERE ServerId=%s AND UserId=%s;':
        await log_message("Select SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='Snarcus', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
        if sql_query != 'SELECT UsersAllowed, CharName, PictureLink FROM Alts WHERE ServerId=%s AND Shortcut=%s;' and sql_query != 'SELECT Id,CharacterName,Currency,Experience FROM CharacterProfiles WHERE ServerId=%s AND UserId=%s;':
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
        connection = mysql.connector.connect(host='localhost', database='Snarcus', user='REDACTED', password='REDACTED')
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
            
async def direct_message(message, response, embed=None):
    channel = await message.author.create_dm()
    await log_message("replied to user " + message.author.name + " in DM with " + response)
    if embed:
        await channel.send(embed=embed)
    else:
        try:
            message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
            for chunk in message_chunks:
                await channel.send("" + chunk)
                await asyncio.sleep(1)
            
        except discord.errors.Forbidden:
            await dm_tracker[message.author.id]["commandchannel"].send("You have DMs off. Please reply with =answer <reply> in the server channel.\n" + response)
        
async def post_webhook(channel, name, response, picture):
    temp_webhook = await channel.create_webhook(name='Chara-Tron')
    await temp_webhook.send(content=response, username=name, avatar_url=picture)
    await temp_webhook.delete() 
    
    
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
        await asyncio.sleep(1)

async def admin_check(userid):
    if (userid != 610335542780887050):
        await log_message(str(userid) + " tried to call an admin message!")
        return False
    else:
        return True
		
@client.event
async def on_ready():
    await log_message("Logged in!")
@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name)
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)
    
@client.event
async def on_message(message):

   allowed_users = [609200799897223168,564965733923291146,610335542780887050,201695859589513218, 260853463238311937, 313593929490497538]
    
   if message.content.startswith('?'):


        command_string = message.content.split(' ')
        command = command_string[0].replace('?','')
        parsed_string = message.content.replace("?" + command,"")
        parsed_string = re.sub(r"^ ","",parsed_string)
        username = message.author.name
        server_name = message.guild.name
        if re.search(command, parsed_string):
            parsed_string = ""
        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        
        if command == 'help' or command == 'info':
            response = "**Snarcus Commands**\n\n`?wisdom`: Sayings from entities across time.\n`?addwisdom -entity Name -culture CultureName -type EntityType -quote The entity's wisdom quote.`: Add a quote from an entity to the database.\n`?invite`: Show the invite link.\n"
            await reply_message(message, response)
        elif command == 'invite':
            response = 'Click here to invite Snarcus: https://discord.com/api/oauth2/authorize?client_id=723776205786185849&permissions=537250880&scope=bot'
            await reply_message(message, response)
        elif command == 'wisdom':
            records = await select_sql("""SELECT EntityName,Culture,EntityType,Saying FROM Sayings ORDER BY RAND ( ) LIMIT 1;""")
            response = ""
            for row in records:
                response = response + '"' + row[3] + '"' + ' -' + row[0] + ' (' + row[1] + '/' + row[2] + ')'
            
            await reply_message(message, response)
        elif command == 'addwisdom':
            if message.author.id not in allowed_users:
                await reply_message(message, "You're not an admin of the bot!")
                return
                
            command_re = re.compile(r"-entity (?P<entity>.+) -culture (?P<culture>.+) -type (?P<type>.+) -quote (?P<quote>.+)")
            if not parsed_string:
                await reply_message(message, "No parameters passed!")
                return
            m = command_re.search(parsed_string)
            if m:
                entity = m.group('entity')
                culture = m.group('culture')
                ent_type = m.group('type')
                quote = m.group('quote')
            else:
                await reply_message(message, "Missing parameter!")
                return
                
            if not entity:
                await reply_message(message, "No entity specified!")
                return
            if not culture:
                await reply_message(message, "No culture specified!")
                return
            if not ent_type:
                await reply_message(message, "No entity type specified!")
                return
            if not quote:
                await reply_message(message, "No quote specified!")
                return
            result = await commit_sql("""INSERT INTO Sayings (EntityName, Culture, EntityType, Saying) VALUES (%s, %s, %s, %s);""",(entity,culture,ent_type,quote))
            await reply_message(message, "Saying added!")
       
        else:
            pass

client.run'REDACTED'		

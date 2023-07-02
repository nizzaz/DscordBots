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
import ast
import json
import aiohttp

intents = discord.Intents(messages=True,guilds=True, message_content=True)

client = discord.Client(heartbeat_timeout=600,intents=intents)

connection = mysql.connector.connect(host='localhost', database='VCPinger', user='REDACTED', password='REDACTED', charset="utf8mb4")
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
def reconnect_db():
    global connection
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(host='localhost', database='VCPinger', user='REDACTED', password='REDACTED', charset="utf8mb4")
    return connection

    
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
        return records
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return None


async def execute_sql(sql_query):
    try:
        connection = mysql.connector.connect(host='localhost', database='VCPinger', user='REDACTED', password='REDACTED', charset="utf8mb4")
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
        
# DM a user
async def direct_message(user, response, server=None):
    global server_settings
    if server:
        if server_settings[server.id]["DMStatus"] == 0:
            return
@client.event
async def on_voice_state_update(member, before, after):

    print("Voice update.")
    response = "**Voice state update for** `" + member.name + "`.\n\n"
    if not before.channel and after.channel:
        response = response + "User joined channel `"  + after.channel.name + "`.\n"
        if len(after.channel.members) < 2:
            records = await select_sql("""SELECT RoleToPingId, PingChannelId FROM Pings WHERE ServerId=%s AND VoiceChannelId=%s;""",(str(member.guild.id),str(after.channel.id)))
            if not records:
                return
            else:
                for row in records:
                    role_id = str(row[0])
                    ping_channel_id = str(row[1])
                ping_channel = discord.utils.get(member.guild.channels, id=int(ping_channel_id))
                await ping_channel.send("<@&" + role_id + "> <@" +str(member.id) + "> has joined voice channel " + after.channel.name + ".")


# Bot code
@client.event
async def on_ready():
    print("Logged into Discord!")
    
# Guild events
@client.event
async def on_guild_join(guild):
    pass
@client.event
async def on_guild_remove(guild):
    pass
@client.event
async def on_message(message):

    if message.author.bot and message.author.id != 787355055333965844:
        return
    if message.author == client.user:
        return
    if message.content.startswith('vc.'):
        current_time = datetime.now()

        command_string = message.content.split(' ')
        command = command_string[0].replace('vc.','')
        parsed_string = message.content.replace("vc."+command,"")

        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string)

        if command == 'info' or command == 'help':
            response = "Welcome to **VC Pinger**, the simple Discord bot for pinging on voice chat join.\n\n**COMMANDS**\n\n`vc.info`: This help.\n`vc.setping vc: VOICE_CHANNEL_ID @ROLE_MENTION #NOTIFICATION_CHANNEL_MENTION`: Set a ping of the role in ROLE_MENTION whenever the first person joins the voice channel of VOICE_CHANNEL_ID in the #NOTIFICATION_CHANNEL_MENTION text channel.\n`vc.removeping vc: VOICE_CHANNEL_ID`: Remove all pings for VOICE_CHANNEL_ID.\n`vc.invite`: Show the bot invite link."
            await send_message(message, response)
            

        elif command == 'setping':
            if not message.channel_mentions:
                await send_message(message, "You didn't specify a notification channel mention!")
                return
            if not message.role_mentions:
                await send_message(message, "You didn't specify a role mention to ping!")
                return
            m = re.search(r"vc: (?P<channel>\d+)", parsed_string, re.I)
            if not m:
                await send_message(message, "You did not specify the voice channel ID!")
                return
            else:
                channel_id = m.group('channel')
            role_id = message.role_mentions[0].id
            text_channel_id = message.channel_mentions[0].id
            result = await commit_sql("""INSERT INTO Pings (ServerId, UserId, VoiceChannelId, PingChannelId, RoleToPingId) VALUES (%s, %s, %s, %s, %s);""",(str(message.guild.id), str(message.author.id), str(channel_id), str(text_channel_id), str(role_id)))
            if result:
                await send_message(message, "Notification set!")
            else:
                await send_message(message, "Database error!")
        elif command == 'removeping':
            m = re.search(r"vc: (?P<channel>\d+)", parsed_string, re.I)
            if not m:
                await send_message(message, "You did not specify the voice channel ID!")
                return
            else:
                channel_id = m.group('channel')
            result = await commit_sql("""DELETE FROM Pings WHERE VoiceChannelId=%s;""",(str(channel_id),))
            if result:
                await send_message(message, "Ping deleted!")
            else:
                await send_message(message, "Database error!")
                
        elif command == 'invite':
            await send_message(message, "Click here to invite VC Pinger: https://discord.com/api/oauth2/authorize?client_id=928642746669993995&permissions=3072&scope=bot")

client.run('REDACTED')

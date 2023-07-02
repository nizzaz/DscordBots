import discord
import discordslashcommands as dsc
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
from nltk.wsd import lesk
from nltk.corpus import stopwords

intents = discord.Intents.all()

connection = mysql.connector.connect(host='localhost', database='EnterYe', user='REDACTED', password='REDACTED')
client = discord.Client(heartbeat_timeout=600, intents=intents)

def reconnect_db():
    global connection
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(host='localhost', database='AuthorMaton', user='REDACTED', password='REDACTED')
    return connection
  
async def log_message(log_entry):
    global bot_log_channel
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
#    await bot_log_channel.send(current_time_string + " - " + log_entry)
    
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
    if re.search(r"drop|update|delete",sql_query,re.I):
        return False
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
    global connection
    try:
        connection = reconnect_db()
        cursor = connection.cursor()
        result = cursor.execute(sql_query)
        return True
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return False

async def send_message(message, response):
    await log_message("Message sent back to server " + message.guild.name + " channel " + message.channel.name + " in response to user " + message.author.name + "\n\n" + response)
    counter = 0
    split = 1900
    for x in response:
        if x == " " and counter > 1900:
            split = counter
            break
        counter = counter + 1
    message_chunks = [response[i:i+split] for i in range(0, len(response), split)]
    for chunk in message_chunks:
        await message.channel.send(">>> " + chunk)
        time.sleep(1)

@client.event
async def on_ready():
    await log_message("Logged into Discord!")
@client.event
async def on_guild_join(guild):
    pass

@client.event
async def on_guild_remove(guild):
    pass
    
@client.event
async def on_message(message):

    if message.author == client.user:
        return
    if message.author.bot and message.author.id != 787355055333965844:
        return

         
    if message.content.startswith('.'):
        print("Message called.")
        if not message.author.guild_permissions.administrator:
            await send_message(message, "You must be an administrator to use these commands.")
            return
        command_string = message.content.split(' ')
        command = command_string[0].replace('.','')
        parsed_string = message.content.replace("." + command + " ","")
        username = message.author.name
        server_name = message.guild.name
        print("Command: " + command)

        if (command == 'sayhi'):
            await message.channel.send("Hello there, " + username + "!")
                
        elif (command == 'info' or command == 'help'):
            response = "**Enter Ye**, the custom Discord channel greeter. Enter Ye will greet a user with a custom message in any channel the first time they start typing in it.\n\n**Commands:**\n\n`.creategreeting GREETING_TEXT`: Create a greeting for the current channel and enable it.\n`.deletegreeting`: Immediately delete the greeting for the current channel.\n`.showgreeting`: Show the greeting for the current channel.\n`.enablegreeting`: Enable the greeting from this channel.\n`disablegreeting`: Disable but don't delete the greeting in the current channel.\n`.resetvisible`: Clear the state of everyone who has seen the greeting before in the current channel.\n\n*Administrator permissions required to run these commands.*"
            await send_message(message, response)
        elif command == 'invite':
            await send_message(message, "Invite me to your server: https://discord.com/api/oauth2/authorize?client_id=969091736875962388&permissions=68608&scope=bot")
        elif command == 'creategreeting':
            records = await select_sql("""SELECT Greeting FROM Greetings WHERE ServerId=%s AND ChannelId=%s;""",(str(message.guild.id), str(message.channel.id)))
            if records:
                await send_message(message, "There is already a greeting in place for this channel. Please delete it first before setting a new greeting.")
                return
            else:
                result = await commit_sql("""INSERT INTO Greetings (ServerId, UserId, ChannelId, Greeting, Enabled) VALUES (%s, %s, %s, %s, %s);""",(str(message.guild.id), str(message.author.id), str(message.channel.id), str(parsed_string), str(1)))
                if result:
                    await send_message(message, "Greeting for channel " + message.channel.name + " set to ```" + parsed_string + "```.")
                else:
                    await send_message(message, "Database error!")
        elif command == 'deletegreeting':
            records = await select_sql("""SELECT Greeting FROM Greetings WHERE ServerId=%s AND ChannelId=%s;""",(str(message.guild.id), str(message.channel.id)))
            if not records:
                await send_message(message, "This channel does not have a greeting to delete.")
                return
            else:
                result = await commit_sql("""DELETE FROM Greetings WHERE ServerId=%s AND ChannelId=%s;""",(str(message.guild.id),str(message.channel.id)))
                if result:
                    await send_message(message, "Greeting deleted from this channel.")
                else:
                    await send_message(message, "Database error!")
        elif command == 'showgreeting':
            records = await select_sql("""SELECT Greeting FROM Greetings WHERE ServerId=%s AND ChannelId=%s;""",(str(message.guild.id), str(message.channel.id)))
            if not records:
                await send_message(message, "This channel does not have a greeting to show.")
                return
            else:
                for row in records:
                    greeting = row[0]
                await send_message(message, "The greeting for this channel is:\n\n" + str(greeting))
        elif command == 'enablegreeting':
            records = await select_sql("""SELECT Greeting FROM Greetings WHERE ServerId=%s AND ChannelId=%s;""",(str(message.guild.id), str(message.channel.id)))
            if not records:
                await send_message(message, "This channel does not have a greeting to enable.")
                return        
            result = await commit_sql("""UPDATE Greetings SET Enabled=1 WHERE ServerId=%s AND ChannelId=%s;""",(str(message.guild.id),str(message.channel.id)))
            if result:
                await send_message(message, "Greeting enabled for this channel.")
            else:
                await send_message(message, "Database error.")
        elif command == 'disablegreeting':
            records = await select_sql("""SELECT Greeting FROM Greetings WHERE ServerId=%s AND ChannelId=%s;""",(str(message.guild.id), str(message.channel.id)))
            if not records:
                await send_message(message, "This channel does not have a greeting to disable.")
                return        
            result = await commit_sql("""UPDATE Greetings SET Enabled=0 WHERE ServerId=%s AND ChannelId=%s;""",(str(message.guild.id),str(message.channel.id)))
            if result:
                await send_message(message, "Greeting disabled for this channel.")
            else:
                await send_message(message, "Database error.")

        elif command == 'resetvisible':
            records = await select_sql("""SELECT Id FROM Greetings WHERE ServerId=%s AND ChannelId=%s;""",(str(message.guild.id), str(message.channel.id)))
            if not records:
                await send_message(message, "This channel does not have a greeting to reset.")
                return
            else:
                for row in records:
                    greeting_id = str(row[0])
                result = await commit_sql("""DELETE FROM AlreadySeen WHERE GreetingId=%s;""",(str(greeting_id),))
                if result:
                    await send_message(message, "Visiblity reset for this channel's greeting.")
                else:
                    await send_message(message, "Database error!")
                    
                    
@client.event
async def on_typing(channel, user, when):
    records = await select_sql("""SELECT Id,Greeting,Enabled FROM Greetings WHERE ChannelId=%s;""",(str(channel.id),))
    if not records:
        return
    else:
        for row in records:
            greeting_id = str(row[0])
            greeting = str(row[1])
            enabled = int(row[2])
        if not enabled:
            return
        seen_records = await select_sql("""SELECT Seen FROM AlreadySeen WHERE GreetingId=%s AND UserId=%s;""",(str(greeting_id),str(user.id)))
        if not seen_records:
            await channel.send( "<@" + str(user.id) + "> " + greeting)
            result = await commit_sql("""INSERT INTO AlreadySeen (UserId, GreetingId) VALUES (%s, %s);""",(str(user.id), str(greeting_id)))
        else:
            return
            
client.run('REDACTED') 
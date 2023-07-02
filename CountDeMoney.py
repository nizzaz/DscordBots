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

client = discord.Client(heartbeat_timeout=600)

current_count = {} 
count_channels = {} 

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='CountDeMoney', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='CountDeMoney', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='CountDeMoney', user='REDACTED', password='REDACTED')
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
    global current_count
    records = await select_sql("""SELECT ServerId,CurrentCount,CountingChannelId FROM ServerSettings;""")
    if not records:
        pass
    else:
        for row in records:
            server_id = int(row[0])
            _current_count = int(row[1])
            channel_id = int(row[2])
            current_count[channel_id] = _current_count
            await log_message("Channel: " + str(channel_id) + " Count: " + str(current_count[channel_id] ))
    await log_message("Logged into Discord!")
        

@client.event
async def on_guild_join(guild):
   
    result = await commit_sql("""INSERT INTO ServerSettings (ServerId) VALUES (%s);""",(str(guild.id),))
    await log_message("Joined guild " + guild.name)
    
@client.event
async def on_guild_remove(guild):
        result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s;""",(str(guild.id),))
        await log_message("Left guild " + guild.name)

@client.event
async def on_message(message):
    global current_count
    invite_url = "https://discord.com/api/oauth2/authorize?client_id=852831919066316810&permissions=68608&scope=bot"
    if message.author == client.user:
        return
    if message.author.bot:
        return
        
    if message.content.startswith('$'):


        command_string = message.content.split(' ')
        command = command_string[0].replace('$','')
        parsed_string = message.content.replace("$" + command + " ","")
        username = message.author.name
        server_name = message.guild.name

        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        if (command == 'sayhi'):
            await message.channel.send("Hello there, " + username + "!")
                
        elif (command == 'info' or command == 'help'):
            await send_message(message, "**Welcome to Count De Money, the Discord counting bot.**\n\nCommands:\n`$addcountchannel #channelmention`: Add a counting channel.\n`$deletecountchannel #channelmention`: Delete a count channel.\n`$countdemoney`: Get the proper pronunciation of De Monet.\n`$stats`: See your highest count, number of times you've counted, and miscounts.\n`$invite`: See the invite link to a server.\n")
        elif command == 'stats':
            records = await select_sql("""SELECT HighestNumber,NumberCounts,Miscounts FROM CountingRoom WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await send_message(message, "You haven't counted yet!")
                return
            for row in records:
                highest_count = str(row[0])
                number_counts = str(row[1])
                miscounts = str(row[2])
                
            await send_message(message, "Your stats:\n\nHighest Count: " + highest_count + "\nNumber of counts: " + number_counts + "\nMiscounts: " + miscounts)
        elif command == 'countdemoney':
            await send_message(message, "De Monet! De Monet!")
        elif command == 'addcountchannel':
            if not message.channel_mentions:
                await send_message(message, "You didn't mention a channel to count in!")
                return
            
            current_count[message.channel_mentions[0].id] = 1
            await commit_sql("""INSERT INTO ServerSettings (ServerId,CountingChannelId,CurrentCount) VALUES (%s,%s,'1');""",(str(message.guild.id),str(message.channel_mentions[0].id)))
            await send_message(message, "Counting channel " + message.channel_mentions[0].name + " added.")
            await message.channel_mentions[0].send("1")
        elif command == 'deletecountchannel':
            if not message.channel_mentions:
                await send_message(message, "You didn't mention a channel to delete!")
                return
            
            await commit_sql("""DELETE FROM ServerSettings WHERE CountingChannelId=%s;""",(str(message.channel_mentions[0].id),))
            await send_message(message, "Counting channel " + message.channel_mentions[0].name + " deleted.")        
        elif command == 'invite':
            await send_message(message, "Click here to invite Count De Money: " + invite_url)
            
        else:
            return
    elif current_count[message.channel.id]:
        if re.search(r"^\d+$",message.content):
            m = re.search(r"(?P<number>\d+)",message.content)
            if m:
                number = int(m.group('number'))
            else:
                return
            if number == current_count[message.channel.id] + 1:
                current_count[message.channel.id]+=2
                result = await commit_sql("""UPDATE ServerSettings SET CurrentCount=%s WHERE CountingChannelId=%s;""",(str(current_count[message.channel.id]),str(message.channel.id)))
                if not result:
                    await send_message(message, "Database error!")
                    return
                records = await select_sql("""SELECT HighestNumber,NumberCounts FROM CountingRoom WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                if not records:
                    await commit_sql("""INSERT INTO CountingRoom (ServerId, UserId, HighestNumber,NumberCounts,Miscounts) VALUES (%s, %s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id),str(current_count[message.channel.id]),'1','0'))
                else:
                    for row in records:
                        highest_count = int(row[0])
                        number_counts = int(row[1])
                    if current_count[message.channel.id] - 1 > highest_count:
                        highest_count = current_count[message.channel.id] - 1
                    number_counts+=1
                    result = await commit_sql("""UPDATE CountingRoom SET HighestNumber=%s,NumberCounts=%s WHERE ServerId=%s AND UserId=%s;""",(str(highest_count),str(number_counts),str(message.guild.id),str(message.author.id)))
                    
                await send_message(message, str(current_count[message.channel.id]))
            else:
                new_start = random.randint(0,2000)
                current_count[message.channel.id] = new_start
                result = await commit_sql("""UPDATE ServerSettings SET CurrentCount=%s WHERE CountingChannelId=%s;""",(str(new_start),str(message.channel.id),))
                records = await select_sql("""SELECT Miscounts FROM CountingRoom WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                if not records:
                    await commit_sql("""INSERT INTO CountingRoom (ServerId, UserId, HighestNumber,NumberCounts,Miscounts) VALUES (%s, %s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id),'1','1','1'))
                else:
                    for row in records:
                        miscounts = int(row[0]) + 1
                    result = await commit_sql("""UPDATE CountingRoom SET Miscounts=%s WHERE ServerId=%s AND UserId=%s;""",(str(miscounts),str(message.guild.id),str(message.author.id)))    
                    
                await send_message(message, "Sorry, that was the wrong number. Resetting count to\n**" + str(new_start) + "***...\n")
        else:
            pass
                
            

client.run('REDACTED')
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

intents = discord.Intents.all()
client = discord.Client(heartbeat_timeout=600,intents=intents)


async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    try:
        connection = mysql.connector.connect(host='localhost', database='Thwapper', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='Thwapper', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
        await log_message(str(records))
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
        connection = mysql.connector.connect(host='localhost', database='Thwapper', user='REDACTED', password='REDACTED')
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
    await log_message("Logged in!")
    
@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name)



@client.event
async def on_message(message):
    
    if message.author == client.user:
        return

    if message.author.bot:
        return
        
            
    if message.content.startswith('thwap'):
        

            
        command_string = message.content.split(' ')
        command = command_string[1]
        parsed_string = message.content.replace("thwap " + command + " ","")
        parsed_string = re.sub(r"<.*>","",parsed_string)
        username = message.author.name
        server_name = message.guild.name

        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        
        if command == 'info':
            response = "*The Thwapper*\n\n`thwap @usermention reason`: Attempt to thwap someone for given reason. May or may not work!\n`thwap stats @user`: See thwapping statistics for a user.\n`thwap given @user`: See the thwaps given by a user.\n`thwap receieved @user`: See thwaps received by a user.\n"
            await send_message(message, response)
        elif command == 'stats':
            if not message.mentions:
                await send_message(message, "You didn't mention a user's stats to show!")
                return
                
            records = await select_sql("""SELECT ThwapsGiven,ThwapsReceived FROM ThwapCounter WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),(message.mentions[0].id)))
            if not records:
                await send_message(message, "This user has never been thwapped! Lucky bastard.")
                return
            response = "Thwap counter for " + message.mentions[0].name + ":\n"
            
            for row in records:
                thwaps_given = row[0]
                thwaps_received = row[1]
            response = response + "Thwaps Given: " + str(thwaps_given) + "\nThwaps Received:" + str(thwaps_received)
            await send_message(message, response)
        
        elif command == 'given':
            if not message.mentions:
                await send_message(message, "You didn't mention a user to check thwaps given!")
                return
            records = await select_sql("""SELECT UserId, ThwapReason, ThwapIntensity, ThwapType FROM Thwaps WHERE ServerId=%s AND Thwapper=%s;""",(str(message.guild.id),str(message.mentions[0].id)))
            if not records:
                await send_message(message, "What a kind soul! This user has never thwapped anyone!")
                return
            response = "Thwaps given by " + message.mentions[0].name + ":\n"
            for row in records:
                response = response + str(discord.utils.get(message.guild.members,id=int(row[0])).name) + " thwapped for " + row[1] + ", the intensity was " + row[2] + ", and the type was " + row[3] +".\n"
            await send_message(message, response)
            
        elif command == 'received':
            if not message.mentions:
                await send_message(message, "You didn't mention a user to check thwaps received!")
                return
            records = await select_sql("""SELECT Thwapper, ThwapReason, ThwapIntensity, ThwapType FROM Thwaps WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.mentions[0].id)))
            if not records:
                await send_message(message, "This user must be tolerable! They have never been thwapped!")
                return
            response = "Thwaps received by " + message.mentions[0].name + ":\n"
            for row in records:
                response = response + str(discord.utils.get(message.guild.members,id=int(row[0])).name) + " thwapped for " + row[1] + ", the intensity was " + row[2] + ", and the type was " + row[3] +".\n"
            await send_message(message, response)        
        else:
            if not message.mentions:
                await send_message(message, "You didn't try to thwap anyone!")
                return
            if not parsed_string:
                parsed_string = "no reason at all!"
            thwap_max = 15
            thwapped_user = message.mentions[0]
            thwap_random = random.randint(0,thwap_max)
            if thwap_random == 0:
                response = "You thwapped yourself!"
                thwapped_user = message.author
                thwap_intensity = "klutz"
            elif thwap_random == 1:
                response = "You thwapped " + thwapped_user.name + " so hard that they died!"
                thwap_intensity = "potent"
                
            elif thwap_random == 2:
                response = "You tried to thwap " + thwapped_user + " but all they felt was a cool breeze!"
                thwap_intensity = "weak"
                
            elif thwap_random == 3:
                response = "You thwapped " + thwapped_user.name + " so powerfully they were launched into orbit!"
                thwap_intensity = "potent"
            elif thwap_random == 4:
                response = "You thwapped " + thwapped_user.name + " and they squeaked!"
                thwap_intensity = "decent"
            elif thwap_random == 5:
                response = "You thwapped " + thwapped_user.name + " in the face and knocked them out cold!"
                thwap_intensity = "ouch"
            elif thwap_random == 6:
                response = "You thwapped " + thwapped_user.name + " into next week!"
                thwap_intensity = "decent"
            elif thwap_random == 7:
                response = "You thwapped " + thwapped_user.name + " on the head and left a bump!"
                thwap_intensity = "ouch"
            elif thwap_random == 8:
                thwapped_user = random.choice(message.guild.members)
                response = "You tried to thwap " + thwapped_user.name + " but thwapped " + thwapped_user.name + " instead!"
                thwap_intensity = "decent"
            elif thwap_random == 9:
                response = "You thwapped " + thwapped_user.name + " but they liked it so much they asked for another one!"
                thwap_intensity = "oh myyy"
            elif thwap_random == 10:
                response = "You thwapped " + thwapped_user.name + " on the ass and they moaned."
                thwap_intensity = "oh myyy"
            elif thwap_random == 11:
                response = "You thwapped " + thwapped_user.name + " so hard their fifth cousins felt it!"
                thwap_intensity = "potent"
            elif thwap_random == 12:
                response = "You thwapped " + thwapped_user.name + " but it felt like a wet tentacle."
                thwap_intensity = "oh myyy"
            elif thwap_random == 13:
                response = "You thwapped " + thwapped_user.name + " and they farted!"
                thwap_intensity = "weak"
            elif thwap_random == 14:
                response = "You thwapped " + thwapped_user.name + " so hard it left a bruise!"
                thwap_intensity = "ouch"
            elif thwap_random == 15:
                response = "You tried to thwap " + thwapped_user.name + " but missed!"
                thwap_intensity = "weak"
                
            
            result = await commit_sql("""INSERT INTO Thwaps (ServerId, UserId, Thwapper, ThwapReason, ThwapIntensity, ThwapType) VALUES (%s, %s, %s, %s, %s, %s);""",(str(message.guild.id),str(thwapped_user.id),str(message.author.id),str(parsed_string),str(thwap_intensity),str(response)))
            if result:
                records = await select_sql("""SELECT ThwapsGiven FROM ThwapCounter WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                if not records:
                    result = await commit_sql("""INSERT INTO ThwapCounter (ServerId, UserId, ThwapsGiven, ThwapsReceieved) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id),'1','0'))
                else:
                    for row in records:
                        thwaps_given = int(row[0]) + 1
                    result = await commit_sql("""UPDATE ThwapCounter SET ThwapsGiven=%s WHERE ServerId=%s AND UserId=%s;""",(str(thwaps_given),str(message.guild.id),str(message.author.id)))
                
                records2 = await select_sql("""SELECT ThwapsReceived FROM ThwapCounter WHERE ServerId=%s AND UserId=$s;""",(str(message.guild.id),str(thwapped_user.id)))
                if not records:
                    result = await commit_sql("""INSERT INTO ThwapCounter (ServerId, UserId, ThwapsGiven, ThwapsReceieved) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(thwapped_user.id),'0','1'))
                else:
                    for row in records:
                        thwaps_received = int(row[0]) + 1
                    result = await commit_sql("""UPDATE ThwapCounter SET ThwapsReceived=%s WHERE ServerId=%s AND UserId=%s;""",(str(thwaps_received),str(message.guild.id),str(thwapped_user.id)))
                await send_message(message, response + "\nThe reason given was: " + parsed_string + " and the intensity was " + thwap_intensity + ".")
            else:
                await send_message(message, "Database error!")

            
client.run('REDACTED')           
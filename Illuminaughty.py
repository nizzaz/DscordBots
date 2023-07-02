import discord
import re
import mysql.connector
from mysql.connector import Error
import time
from discord.utils import get
import discord.utils
import random
import string
import asyncio
import aiohttp
from pywizlight.bulb import wizlight, PilotBuilder, discovery
from datetime import datetime, timedelta

client = discord.Client(heartbeat_timeout=600)

bulbs = []

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    try:
        connection = mysql.connector.connect(host='localhost', database='LightBulb', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='LightBulb', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='LightBulb', user='REDACTED', password='REDACTED')
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
        try:
            await message.channel.send(chunk)
        except:
            pass
        time.sleep(1)
		
@client.event
async def on_ready():
    global bulbs
    bulbs = await discovery.find_wizlights(discovery)
    for light in bulbs:
        await log_message(str(light.ip))
@client.event
async def on_guild_join(guild):
    global guild_settings
    global npc_aliases
    global dialog_tracker

    
    await log_message("Joined guild " + guild.name)

    
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)
    
@client.event
async def on_message(message):
    global bulbs

    
    if message.author.bot:
        return
    if message.author == client.user:
        return
    if message.content.startswith('%'):

        command_string = message.content.split(' ')
        command = command_string[0].replace('%','')
        parsed_string = message.content.replace("%"+command,"")

        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string) 	
        
        if command == 'setcolor':
            red = command_string[1]
            green = command_string[2]
            blue = command_string[3]
            for light in bulbs:
                await light.turn_on(PilotBuilder(rgb = (int(red), int(green), int(blue))))
                
            await send_message(message, "Light colors set to: " + str(red) + ", " + str(green) + " ," + str(blue))
        elif command == 'setbrightness':
            brightness = command_string[1]
            for light in bulbs:
                await light.turn_on(PilotBuilder(brightness = int(brightness)))
            await send_message(message, "Light brightness set to: " +str(brightness))
        elif command == 'setscene':
            scene = command_string[1]
            for light in bulbs:
                await light.turn_on(PilotBuilder(scene = int(scene)))
            await send_message(message, "Light scene set to: " + str(scene))
        elif command == 'settorole':
            red = message.author.color.r
            green = message.author.color.g
            blue = message.author.color.b
            for light in bulbs:
                await light.turn_on(PilotBuilder(rgb = (int(red), int(green), int(blue))))
                
            await send_message(message, "Light colors set to: " + str(red) + ", " + str(green) + " ," + str(blue))            
        
        elif command == 'halloween':
            light =bulbs[0]
            await light.turn_on(PilotBuilder(rgb = (56, 0, 89), brightness=255))
            light = bulbs[1]
            await light.turn_on(PilotBuilder(rgb =	(255,110,0), brightness=255))
            light = bulbs[2]
            await light.turn_on(PilotBuilder(rgb =	(255,110,0), brightness=255))
            await send_message(message, "Lighting set to Halloween.")
                
        elif command == 'moonlight':
            light =bulbs[0]
            await light.turn_on(PilotBuilder(colortemp=4100, brightness=20))
            light = bulbs[1]
            await light.turn_on(PilotBuilder(colortemp=4100, brightness=20))
            light = bulbs[2]
            await light.turn_on(PilotBuilder(rgb =	(0,0,40), brightness=150))
            await send_message(message, "Lighting set to moonlight.")
        
        elif command == 'midnight':
            for light in bulbs:
                await light.turn_on(PilotBuilder(rgb = (50,0,255), brightness = 130))
              
            await send_message(message, "Lighting set to Midnight.")
        elif command == 'turnoff':
            for light in bulbs:
                await light.turn_off()
            await send_message(message, "Lights out, fuckers!")
            
client.run'REDACTED'
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
import aiohttp
import csv
intents = discord.Intents.default()

class NakedObject(object):
    pass
    
connection = mysql.connector.connect(host='localhost', database='GameDecider', user='REDACTED', password='REDACTED')
client = discord.Client(heartbeat_timeout=600, intents=intents)

def reconnect_db():
    global connection
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(host='localhost', database='GameDecider', user='REDACTED', password='REDACTED')
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

async def select_sql_prompt(sql_query, params = None):
    global connection
    try:
        cconnection = reconnect_db()
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
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
        await asyncio.sleep(1)
    return False

@client.event
async def on_ready():
    pass
    
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

            
    if message.content.startswith('='):
        print("Message called.")

        command_string = message.content.split(' ')
        command = command_string[0].replace('=','').strip()
        parsed_string = message.content.replace("=" + command + " ","")
        if re.search(command, parsed_string):
            parsed_string = None
        username = message.author.name
        server_name = message.guild.name
        print("Command: " + command)
        if command == 'help' or command == 'info':
            response = "Welcome to **Game Decider**, a Discord bot to help you decide what game to play!\n\nGame Decider supports game titles from any platform. There is no catalog of games, as they must be added. Your library persists across any servers with the bot.\n\n**COMMANDS**\n`=addgame TITLE/PLATFORM`: Add the game with TITLE on the PLATFORM to the bot for your library.\n`=platformlist @USER_MENTION`: View a list of platforms for the mentioned user. If you don't mention a user, it uses your library.\n`=gamesfor PLATFORM`: See a list of games for the specified platform.\n`=randomgame PLATFORM`: Pick a random game. If a platform isn't specified, it picks any game in the library.\n`randomplatform`: Pick a random platform from your list.\n`=gametitlesearch SEARCH_TERM`: Search your library for a game with the specfied word or phrase in the title. Use this command to get an ID for a game.\n`=importcsv`: Upload a file in comma-delimited format to add to your library. The fields are GameTitle,GamePlatform and must have the headers.\n`=gamelist @USER_MENTION`: See all games for a user. This can return a long series of messages. If no user is mentioned, it returns your list.\n`=deletegame TITLE/PLATFORM`: Delete a game from your library by title and platform.\n`=deleteid ID`: Delete a game by database ID (must be yours).\n`=info`: This help.\n`=invite`: Show a bot invite."
            await send_message(message, response)
        if (command == 'sayhi'):
            await message.channel.send("Hello there, " + username + "!")
        if command == 'platformlist':
            if message.mentions:
                user = message.mentions[0]
            else:
                user = message.author
            records = await select_sql("""SELECT DISTINCT(GamePlatform) FROM Games WHERE UserId=%s;""",(str(user.id),))
            if not records:
                await send_message(message, "This user doesn't have any games recorded!")
                return
            response ="**" + user.name + "'s Platform List:**\n\n"
            for row in records:
                response = response + row[0] + "\n"
                
            await send_message(message, response)
        if command == 'gamesfor':
            if not re.search(r"\w+",parsed_string):
                await send_message(message, "You didn't specify a platform!")
                return
            records = await select_sql("""SELECT GameTitle FROM Games WHERE UserId=%s AND GamePlatform=%s;""",(str(message.author.id),str(parsed_string)))
            if not records:
                await send_message(message, "You do not have any games for that platform yet!")
                return
            response = "**" + message.author.name + "'s games for the " + parsed_string + "**:\n\n"
            for row in records:
                response = response + row[0] + "\n"
            await send_message(message, response)
            
        if command == 'randomgame':
            if parsed_string:
                records = await select_sql("""SELECT GameTitle, GamePlatform FROM Games WHERE UserId=%s AND GamePlatform=%s ORDER BY RAND() LIMIT 1;""",(str(message.author.id),parsed_string))
            else:
                records = await select_sql("""SELECT GameTitle, GamePlatform FROM Games WHERE UserId=%s ORDER BY RAND() LIMIT 1;""",(str(message.author.id),))
            if not records:
                await send_message(message, "You don' have any games yet!")
                return
            for row in records:
                title = row[0]
                platform = row[1]
            await send_message(message, "You should play **" + title + "** for the **" + platform + "**!")
                
        if command == 'randomplatform':
            records = await select_sql("""SELECT DISTINCT(GamePlatform) FROM Games WHERE UserId=%s ORDER BY RAND() LIMIT 1;""",(str(message.author.id),))
            if not records:
                await send_message(message, "This user doesn't have any games recorded!")
                return
            for row in records:
                platform = row[0]
            response = "You should play a game on **" + platform + "**!"    
            await send_message(message, response)
        if command == 'addgame':
            m = re.search(r"(?P<title>.+)/(?P<platform>.+)",parsed_string)
            if m:
                title = m.group("title").strip()
                platform = m.group("platform").strip()
            else:
                await send_message(message, "Bad command or file name.")
                return
            result = await commit_sql("""INSERT INTO Games (ServerId, UserId, GameTitle, GamePlatform) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id),str(title),str(platform)))
            if result:
                await send_message(message, "Game " + title + " for platform " + platform + " added to your database!")
            else:
                await send_message(message, "Database error!")
        if command == 'gametitlesearch':
            if not parsed_string:
                await send_message(message, "You didn't specify a search term!")
                return
            records = await select_sql("""SELECT Id,GameTitle,GamePlatform FROM Games WHERE UserId=%s AND GameTitle LIKE '%""" + parsed_string + """%';""", (str(message.author.id),))
            if not records:
                await send_message(message, "No games found with that search term in the title.")
                return
            response = "**Games matching " + parsed_string + "**\n\n"
            for row in records:
                response = response + str(row[0]) + " - " + row[1] + " for " + row[2] + "\n"
            await send_message(message, response)
        if command == 'invite':
            await send_message(message, "Click here to invite Game Decider: https://discord.com/api/oauth2/authorize?client_id=988296424322113566&permissions=51200&scope=bot")
        if command == 'addplatform':
            pass
        if command == 'deletegame':
            m = re.search(r"(?P<title>.+)/(?P<platform>.+)",parsed_string)
            if m:
                title = m.group("title").strip()
                platform = m.group("platform").strip()
            else:
                await send_message(message, "Bad command or file name.")
                return
            result = await commit_sql("""DELETE FROM Games WHERE UserId=%s AND GameTitle=%s AND GamePlatform=%s;""",(str(message.author.id),str(title),str(platform)))
            if result:
                await send_message(message, "Game " + title + " for platform " + platform + " deleted from your database!")
            else:
                await send_message(message, "Database error!")
        if command == 'deleteid':
            if not parsed_string:
                await send_message(message, "You didn't specify an ID!")
                return
            records = await select_sql("""SELECT UserId FROM Games WHERE Id=%s;""",(str(parsed_string),))
            if not records:
                await send_message(message, "No game with that ID found!")
                return
            for row in records:
                if str(message.author.id) != str(row[0]):
                    await send_message(message, "This game doesn't belong to you!")
                    return
                else:
                    result = await commit_sql("""DELETE FROM Games WHERE Id=%s;""",(str(parsed_string),))
            await send_message(message, "Game deleted from database.")
            
        if command == 'deleteplatform':
            pass
        if command == 'importcsv':
            if not message.attachments:
                await send_message(message, "You didn't attach a CSV file!")
                return
            file_url = message.attachments[0].url
            file_name = message.attachments[0].filename
            table_name = 'Games'
            await send_message(message, "Downloading file " + file_name + "...")
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
    #           await reply_message(message, "File saved to " + file_name + "!")
                    with open('/home/REDACTED/' + parsed_string.strip() + "." + re.sub(r".*\.(.*)",r"\1",file_name), 'wb') as file:
                        bytes = await resp.read()
                        
                        file.write(bytes)
                    with open('/home/REDACTED/' + parsed_string.strip() + "." + re.sub(r".*\.(.*)",r"\1",file_name),encoding='latin1') as csv_file:
                        csv_reader = csv.reader(csv_file,delimiter = ',')
                        headers = []
                        sql_command = """INSERT INTO Games (ServerId, UserId, GameTitle, GamePlatform) VALUES (%s, %s, %s, %s);"""
                        header_list = next(csv_reader)

                        sql_tuple = (str(message.guild.id),str(message.author.id))
                        rows = []
                        for row in csv_reader:
                            rows.append(row)
                        for row in rows:
                            row_command = sql_command
                            row_tuple = sql_tuple + (row[0] , row[1])

                             #  row_tuple = row_tuple + (str(element.strip()),)

                            result = await commit_sql(row_command,row_tuple)
            await send_message(message, "Import complete!")
        if command == 'gamelist':
            if not message.mentions:
                user = message.author
            else:
                user = message.mentions[0]
            records = await select_sql("""SELECT GameTitle,GamePlatform FROM Games WHERE UserId=%s;""",(str(user.id),))
            if not records:
                await send_message(message, "No games found for that user!")
                return
            response = "**" + user.name + "'s Game List:**\n\n"
            for row in records:
                response = response +  row[0] + " for " + row[1] + "\n"
            await send_message(message, response)
       
            
client.run'REDACTED'
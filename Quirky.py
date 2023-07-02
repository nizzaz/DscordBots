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
from nltk.corpus import brown
from nltk.corpus import gutenberg
from difflib import SequenceMatcher
import itertools

def join_sentence(sentence):
    final_sentence = ""
    for word in sentence:
        if re.search(r"[A-Za-z0-9]",word):
            final_sentence = final_sentence + " " + word
        else:
            final_sentence = final_sentence + word
    return final_sentence        
        
intents = discord.Intents(messages=True,guilds=True, message_content=True, typing=True)
client = discord.Client(heartbeat_timeout=600,intents=intents)
sentences = []

#for sent in gutenberg.sents():
#    sentences.append(join_sentence(sent))
for sent in brown.sents():
    sentences.append(join_sentence(sent))
    
typing_channels = {} 
typing_tests = {}
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='Quirky', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='Quirky', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='Quirky', user='REDACTED', password='REDACTED')
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
async def on_typing(channel, user, when):
    global typing_channels
    global typing_tests
    try:
        typing_tests[channel.guild.id][user.id]["starttime"]
    except:
        return
    if typing_tests[channel.guild.id][user.id]["starttime"]:
        return
        
    if typing_channels[channel.guild.id] == channel.id and typing_tests[channel.guild.id][user.id]:
        typing_tests[channel.guild.id][user.id]["starttime"] = datetime.now()
        await log_message("Started typing test for user " + user.name + ".")
		
@client.event
async def on_ready():
    global typing_channels
    global typing_tests
    for guild in client.guilds:
        typing_channels[guild.id] = 0
        typing_tests[guild.id] = {}
    records = await select_sql("""SELECT ServerId,TypingChannelId FROM ServerSettings;""")
    if records:
        for row in records:
            server_id = int(row[0])
            typing_channel_id = int(row[1])
            typing_channels[server_id] = typing_channel_id
            
    
    await log_message("Logged into Discord!")
    

@client.event
async def on_guild_join(guild):
    global typing_channels
    global typing_tests
    typing_tests[guild.id] = {} 
    typing_channels[guild.id] = 0
    result = await commit_sql("""INSERT INTO ServerSettings (ServerId,TypingChannelId) VALUES (%s,0);""",(str(guild.id),))
    await log_message("Joined guild " + guild.name + ".")
    
@client.event
async def on_guild_remove(guild):
    result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s;""",(str(guild.id),))
    await log_message("Left guild " + guild.name + ".")
    
@client.event
async def on_message(message):
    global sentences
    global typing_channels
    global typing_tests
    invite_url = "https://discord.com/api/oauth2/authorize?client_id=765063884553060362&permissions=68608&scope=bot"
    if message.author == client.user:
        return
    if message.author.bot and message.author.id != 787355055333965844:
        return

    if message.content.startswith('t!'):


        command_string = message.content.split(' ')
        command = command_string[0].replace('t!','')
        parsed_string = message.content.replace("t!" + command + " ","")
        username = message.author.name
        server_name = message.guild.name

        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        if (command == 'sayhi'):
            await message.channel.send("Hello there, " + username + "!")
                
        elif (command == 'info' or command == 'help'):
            await send_message(message, "**Welcome to Quirky QWERTY, the typing test bot!**\n\nCommands:\n`t!settypingchannel #channelmention`: Set the channel for typing tests.\n`t!typingtest`: Start a typing test in the typing channel. Timer begins when you begin typing and ends when you send the message.\n`t!stats`: See your current stats (best WPM, best accuracy, last WPM, last accuracy.\n`t!scoreboard`: Show the server scoreboard ordered by best WPM.\n`t!stop`: Stop the typing test and do not score it.")
        elif command == 'settypingchannel':
            if not message.channel_mentions:
                await send_message(message, "You didn't mention a channel to type in!")
                return
            
            typing_channels[message.guild.id] = message.channel_mentions[0].id
            await commit_sql("""UPDATE ServerSettings SET TypingChannelId=%s WHERE ServerId=%s;""",(str(message.channel_mentions[0].id),str(message.guild.id)))
            await send_message(message, "Typing channel " + message.channel_mentions[0].name + " set.")
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await send_message(message,"Admin command only!")
                return   
            await send_message(message, "Server count: " + str(len(client.guilds)))  
        elif command == 'typingtest':
            
            if not typing_channels[message.guild.id]:
                await send_message(message, "You haven't set a typing channel yet!")
                return
            await send_message(message, "Getting your typing test. It will appear in <#" + str(typing_channels[message.guild.id]) + ">.")
            typing_tests[message.guild.id][message.author.id] = {}
            typing_tests[message.guild.id][message.author.id]["testtext"] = re.sub(r"[^A-Za-z0-9!,\. \-']","","".join(random.choices(sentences, k=3)))
            typing_tests[message.guild.id][message.author.id]["starttime"] = 0
            typing_tests[message.guild.id][message.author.id]["endtime"] = 0

            
            channel_obj = discord.utils.get(message.guild.channels, id=typing_channels[message.guild.id])
            await channel_obj.send(">>> Your typing test is below. The timer will start when you begin typing and end when you send the message in this channel.\n\n" + typing_tests[message.guild.id][message.author.id]["testtext"])
        elif command == 'stop':
            try:
                typing_tests[message.guild.id][message.author.id]
            except:
                await send_message(message, "You weren't taking a typing test!")
                return
            del typing_tests[message.guild.id][message.author.id]
            await send_message(message, "The typing test has been stopped.")
        elif command == 'stats':
            records = await select_sql("""SELECT BestWPM, LastWPM, BestAccuracy, LastAccuracy FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await send_message(message, "You haven't tried a typing test on this server yet!")
                return
            for row in records:
                best_wpm = str(row[0])
                last_wpm = str(row[1])
                best_accuracy = str(row[2])
                last_accuracy = str(row[3])
                
            await send_message(message, "Your typing stats:\n\nBest WPM: " + best_wpm + "\nBest Accuracy: " + best_accuracy + "\nLast WPM: " + last_wpm + "\nLast Accuracy: " + last_accuracy)
        
        elif command == 'scoreboard':
            records = await select_sql("""SELECT UserId, BestWPM, BestAccuracy FROM Scoreboard WHERE ServerId=%s ORDER BY BestWPM DESC;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No one has taken a typing test here yet!")
                return
            response = "**Server Leaderboard:**\n\n"
            for row in records:
                user_id = int(row[0])
                best_wpm = str(row[1])
                best_acc = str(row[2])
                try:
                    user_name = discord.utils.get(message.guild.members, id=user_id).name
                
                    response = response + user_name + " - " + best_wpm + " WPM - " + best_acc + "%\n"
                except:
                    continue
            await send_message(message, response)
        elif command == 'invite':
            await send_message(message, "Click here to invite Quirky QWERTY: " + invite_url)
 #   try:        
    if message.channel.id == typing_channels[message.guild.id] and typing_tests[message.guild.id][message.author.id] and not message.content.startswith("t!"):
        typing_tests[message.guild.id][message.author.id]["endtime"] = datetime.now()
        delta_time = typing_tests[message.guild.id][message.author.id]["endtime"] - typing_tests[message.guild.id][message.author.id]["starttime"]
        words_in_post = message.content.split(' ')
        word_count = len(words_in_post)
        print("Word count: " + str(word_count))
        total_seconds = delta_time.seconds
        print("Total seconds: " + str(total_seconds))
        wpm = int(word_count/(total_seconds/60))
        if wpm >= 200:
            await send_message(message, "That's not humanly possible. Try not copying and pasting!")
            return
        accuracy = int(SequenceMatcher(None, typing_tests[message.guild.id][message.author.id]["testtext"], message.content).ratio() * 100)
        records = await select_sql("""SELECT BestWPM,BestAccuracy FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
        if not records:
            await commit_sql("""INSERT INTO Scoreboard (ServerId, UserId, BestWPM, LastWPM, BestAccuracy, LastAccuracy) VALUES (%s, %s, %s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id),str(wpm),str(wpm),str(accuracy),str(accuracy)))
        else:
            for row in records:
                best_wpm = int(row[0])
                best_accuracy = int(row[1])
                
            if accuracy > best_accuracy:
                best_accuracy = accuracy
            if wpm > best_wpm:
                best_wpm = wpm
            await commit_sql("""UPDATE Scoreboard SET BestWPM=%s,LastWPM=%s,BestAccuracy=%s,LastAccuracy=%s WHERE ServerId=%s AND UserId=%s;""",(str(best_wpm),str(wpm),str(best_accuracy),str(accuracy),str(message.guild.id),str(message.author.id)))
        del typing_tests[message.guild.id][message.author.id]
        await send_message(message, "Your total words per minute for this test was **" + str(wpm) + "** and your accuracy was **" + str(accuracy) + "%**.")
        
#    except:
 #       pass



client.run'REDACTED'		
		
	
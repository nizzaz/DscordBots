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

intents = discord.Intents(messages=True,guilds=True, message_content=True)

connection = mysql.connector.connect(host='localhost', database='SexBot', user='REDACTED', password='REDACTED')
client = discord.Client(heartbeat_timeout=600, intents=intents)

f = open("/home/REDACTED/BotMaster/nsfw_questions.txt","r")
nsfw_questions = f.read().split('\n')
f.close()

f = open("/home/REDACTED/BotMaster/nsfw_quotes.txt","r")
nsfw_quotes = f.read().split('\n')
f.close()

f = open("/home/REDACTED/BotMaster/StarAI/shortjokes.csv", "r")
nsfw_jokes = f.read().split('\n')
f.close()

async def questions():
    global nsfw_questions
    global nsfw_quotes
    await client.wait_until_ready()
    await log_message("Lanuching timer.")
    while True:
        current_time_obj = datetime.now()
        current_hour = int(current_time_obj.strftime("%H"))
        current_minute = int(current_time_obj.strftime("%M"))
        current_second = int(current_time_obj.strftime("%S"))
        records = await select_sql("""SELECT Hour, Minute, ChannelId,ServerId FROM QuestionSchedule;""")
        for row in records:
            hour = int(row[0])
            minute = int(row[1])
            channel_id = int(row[2])
            server_id = int(row[3])

            if hour == current_hour and minute == current_minute:
                print("WOTD writing...")
                try:
                    channel_obj = client.get_channel(channel_id)
                except:
                    pass
                records = await select_sql("""SELECT Question FROM CustomQuestions WHERE ServerId=%s;""",(str(channel_obj.guild.id),))
                if not records:
                    embed = discord.Embed(title="NSFW Question of the Day",description=random.choice(nsfw_questions))
                    try:
                        await channel_obj.send(embed=embed)
                    except:
                        pass
                else:
                    custom_questions = []
                    for row in records:
                        custom_questions.append(row[0])
                    
                    
                    embed = discord.Embed(title="NSFW Question of the Day",description=random.choice(custom_questions))
                    try:
                        await channel_obj.send(embed=embed)                        
                    except:
                        pass
        records = await select_sql("""SELECT Hour, Minute, ChannelId FROM QuoteSchedule;""")
        for row in records:
            hour = int(row[0])
            minute = int(row[1])
            channel_id = int(row[2])
            

            if hour == current_hour and minute == current_minute:
                print("WOTD writing...")
                try:
                    channel_obj = client.get_channel(channel_id)
                except:
                    pass
                try:
                    embed = discord.Embed(title="NSFW Quote of the Day",description=random.choice(nsfw_questions))
                    await channel_obj.send(embed=embed)
                    continue
                except:
                    pass                
        await asyncio.sleep(60)  

        
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
def reconnect_db():
    global connection
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(host='localhost', database='SexBot', user='REDACTED', password='REDACTED')
    return connection
  
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
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
        
@client.event
async def on_ready():
    await log_message("Logged in!")
    await client.loop.create_task(questions())        
    
@client.event
async def on_message(message):
    global nsfw_quotes
    global nsfw_questions
    global nsfw_jokes

    if message.author == client.user:
        return
    if message.author.bot:
        return

            
    if message.content.startswith(';'):


        command_string = message.content.split(' ')
        command = command_string[0].replace(';','')
        parsed_string = message.content.replace(";" + command + " ","")
        username = message.author.name
        server_name = message.guild.name

            
        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        if (command == 'sayhi'):
            await message.channel.send("Hello there, " + username + "!")
                
        elif (command == 'info' or command == 'help'):
            response = "Welcum to Sexpun T'Cum, the NSFW quote and question bot.\n\nBot prefix: `;`\n\n**Commands**\n\n`;info`: This help.\n`;question`: Get a random NSFW question.\n`;quote`: Get a random NSFW quote.\n`;joke`: Tell a random NSFW joke. Note--can be offensive.\n`;setupquestion HH:MM #channel_mention`: Set up a daily NSFW question in the mentioned NSFW channel at the time in central.\n`;setupquote HH:MM #channel_mention`: Set up a daily NSFW quote in the mentioned NSFW channel at the time in central.\n`;clearquestion`: Clear the scheduled daily question.\n`;clearquote`: Clear the scheduled daily quote.\n\n**Custom Questions**\n\nYou may create custom questions with the following commands. If you specify custom questions, the question of the day and the `;question` command will only pick from your list.\n\n`;setupcustomquestions`: Import the master question list into a custom list for your server.\n`;listcustomquestions`: List the custom questions for your server with their IDs.\n`;addcustomquestion QUESTION_TEXT`: Add a custom question to your list.\n`;deletecustomquestion ID`: Delete a question with the specified ID.\n`;clearcustomquestions`: Delete all your custom questions and return to the bot's defaults."
            await send_message(message, response)
        elif command == 'question':
            if not message.channel.nsfw:
                await message.channel.send("I am not allowed to post in non-NSFW channels.")
                return
            records = await select_sql("""SELECT Question FROM CustomQuestions WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                embed = discord.Embed(title="NSFW Question",description=random.choice(nsfw_questions))
                await message.channel.send(embed=embed)
            else:
                custom_questions = []
                for row in records:
                    custom_questions.append(row[0])
                embed = discord.Embed(title="NSFW Question",description=random.choice(custom_questions))
                await message.channel.send(embed=embed)
        elif command == 'joke':
            if not message.channel.nsfw:
                await message.channel.send("I am not allowed to post in non-NSFW channels.")
                return
            embed = discord.Embed(title="NSFW Joke",description=re.sub(r"\d+,","",random.choice(nsfw_jokes)))
            await message.channel.send(embed=embed)                
        elif command == 'quote':
            if not message.channel.nsfw:
                await message.channel.send("I am not allowed to post in non-NSFW channels.")
                return
            embed = discord.Embed(title="NSFW Quote",description=random.choice(nsfw_quotes))
            await message.channel.send(embed=embed)
        elif command == 'setupquestion':
            if not message.channel_mentions:
                await send_message(message, "No target channel specified!")
                return
            if not message.channel_mentions[0].nsfw:
                await message.channel.send("That channel is not NSFW! Try another channel or setting the NSFW flag.")
                return
            time_re = re.compile(r"(?P<hour>\d+):(?P<minute>\d+)")
            
            m = time_re.search(message.content)
            if m:
                minute = m.group('minute')
                hour = m.group('hour')
            else:
                await send_message(message, "No time specified!")
                return
                
            target_channel = message.channel_mentions[0].id
            
            records = await select_sql("""SELECT Id FROM QuestionSchedule WHERE ServerId=%s;""", (str(message.guild.id),))
            if not records:
                result = await commit_sql("""INSERT INTO QuestionSchedule (ServerId,ChannelId,Hour,Minute) VALUES (%s, %s, %s, %s);""", (str(message.guild.id),str(target_channel),str(hour),str(minute)))
                if result:
                    await send_message(message, "Time for NSFW question of the day set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await send_message(message, "Database error!")
            else:
                result = await commit_sql("""UPDATE QuestionSchedule Set ChannelId=%s,Hour=%s,Minute=%s WHERE ServerId=%s;""", (str(target_channel),str(hour),str(minute), str(message.guild.id)))
                if result:
                    await send_message(message, "Time for NSFW question of the day set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await send_message(message, "Database error!")         
        elif command == 'setupquote':
            if not message.channel_mentions:
                await send_message(message, "No target channel specified!")
                return
            if not message.channel_mentions[0].nsfw:
                await message.channel.send("That channel is not NSFW! Try another channel or setting the NSFW flag.")
                return
            time_re = re.compile(r"(?P<hour>\d+):(?P<minute>\d+)")
            
            m = time_re.search(message.content)
            if m:
                minute = m.group('minute')
                hour = m.group('hour')
            else:
                await send_message(message, "No time specified!")
                return
                
            target_channel = message.channel_mentions[0].id
            

            records = await select_sql("""SELECT Id FROM QuoteSchedule WHERE ServerId=%s;""", (str(message.guild.id),))
            if not records:
                result = await commit_sql("""INSERT INTO QuoteSchedule (ServerId,ChannelId,Hour,Minute) VALUES (%s, %s, %s, %s);""", (str(message.guild.id),str(target_channel),str(hour),str(minute)))
                if result:
                    await send_message(message, "Time for NSFW quote of the day set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await send_message(message, "Database error!")
            else:
                result = await commit_sql("""UPDATE QuoteSchedule Set ChannelId=%s,Hour=%s,Minute=%s WHERE ServerId=%s;""", (str(target_channel),str(hour),str(minute), str(message.guild.id)))
                if result:
                    await send_message(message, "Time for NSFW quote of the day set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await send_message(message, "Database error!")
        elif command == 'setupcustomquestions':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to issue this command.")
                return
            for question in nsfw_questions:
                await commit_sql("""INSERT INTO CustomQuestions (ServerId, UserId, Question) VALUES (%s, %s, %s);""",(str(message.guild.id),str(message.author.id),str(question)))
            await send_message(message, "Your custom question list has been generated from the master list.")
                
        elif command == 'listcustomquestions':
            if not message.channel.nsfw:
                await message.channel.send("I am not allowed to post in non-NSFW channels.")
                return        
            records = await select_sql("""SELECT Id, Question FROM CustomQuestions WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "You have no custom questions!")
                return
            response = "Custom questions for server " + message.guild.name + ":\n\n"
            for row in records:
                response = response + "**" + str(row[0]) + "** - " + str(row[1]) + "\n"
            await send_message(message, response)
        elif command == 'deletecustomquestion': 
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to issue this command.")
                return        
            if not parsed_string:
                await send_message(message, "Please specify an ID to delete. Use `;listcustomquestions` to see your custom questions and their IDs.")
                return
            records = await select_sql("""SELECT ServerId, Question FROM CustomQuestions WHERE Id=%s;""",(str(parsed_string.strip()),))
            if not records:
                await send_message(message, "That ID does not exist.")
                return
            for row in records:
                server_id = int(row[0])
                question = str(row[1])
            if server_id != message.guild.id:
                await send_message(message, "That ID is not a question from your list.")
                return
            result = await commit_sql("""DELETE FROM CustomQuestions WHERE Id=%s;""",(str(parsed_string),))
            await send_message(message, "Question `" + question + " deleted from custom question list.")
        elif command == 'addcustomquestion':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to issue this command.")
                return        
            if not parsed_string:
                await send_message(message, "You did not specify a question.")
                return
            result = await commit_sql("""INSERT INTO CustomQuestions (ServerId, UserId, Question) VALUES (%s, %s, %s);""",(str(message.guild.id),str(message.author.id),parsed_string))
            if result:
                records = await select_sql("""SELECT Id FROM CustomQuestions WHERE ServerId=%s AND Question=%s;""",(str(message.guild.id),parsed_string))
                if not records:
                    await send_message(message, "Database error!")
                    return
                for row in records:
                    new_id = str(row[0])
                await send_message(message, "Question `" + parsed_string + "` added with ID of **" + new_id + "**.")
            else:
                await send_message(message, "Database error!")
        elif command == 'clearcustomquestions':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to issue this command.")
                return        
            await commit_sql("""DELETE FROM CustomQuestions WHERE ServerId=%s;""",(str(message.guild.id),))
            await send_message(message, "All custom questions deleted. I will now use the default question list.")
            
        elif command == 'invite':
            await send_message(message, "Click here to invite me: https://discord.com/api/oauth2/authorize?client_id=831712578400944159&permissions=116736&scope=bot")
        elif command == 'clearquote':
            result = await commit_sql("""DELETE FROM QuoteSchedule WHERE ServerId=%s;""",(str(message.guild.id),))
            await send_message(message, "Quote of the day cleared!")
        elif command == 'clearquestion':
            result = await commit_sql("""DELETE FROM QuestionSchedule WHERE ServerId=%s;""",(str(message.guild.id),))
            await send_message(message, "Question of the day cleared!")
        elif command == 'serverlist':
            await log_message("servercount called by " + message.author.name)
            if (message.author.id != 610335542780887050):
                await send_message(message,"Admin command only!")
                return   
            response = "Server count: " + str(len(client.guilds))
            for x in client.guilds:
                if x.name:
                    response = response + x.name + "\n"
            await send_message(message,response)          

client.run('REDACTED')          
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
from slashcommands import SlashCommands

word_of_the_day_schedule = {}
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def word_of_the_day():
    global word_of_the_day_schedule
    await client.wait_until_ready()
    await log_message("Lanuching timer.")
    while True:
        current_time_obj = datetime.now()
        current_hour = int(current_time_obj.strftime("%H"))
        current_minute = int(current_time_obj.strftime("%M"))
        current_second = int(current_time_obj.strftime("%S"))
        for server_id in word_of_the_day_schedule.keys():
            try: word_of_the_day_schedule[server_id]["Hour"]
            except: word_of_the_day_schedule[server_id]["Hour"] = 0
            try: word_of_the_day_schedule[server_id]["Minute"]
            except: word_of_the_day_schedule[server_id]["Minute"] = 0
            #await log_message(str(current_hour) + ":" + str(current_minute) + ":" + str(current_second))
            
            if word_of_the_day_schedule[server_id]["Hour"] == current_hour and word_of_the_day_schedule[server_id]["Minute"] == current_minute and current_second <= 1:
                print("VOTD writing...")
                try:
                    channel_obj = client.get_channel(word_of_the_day_schedule[server_id]["ChannelId"])
                except:
                    continue

                response = "**VERSE OF THE DAY**\n\n**The verse of the day is **\n\n"
                book = random.choice(list(bible_kjv_text.keys()))
                chapter = random.choice(list(bible_kjv_text[book].keys()))
                verse = random.choice(list(bible_kjv_text[book][str(chapter)].keys()))
                verse_text = bible_kjv_text[book][str(chapter)][str(verse)]
                response = response + verse_text + "\n" + "*" + book + " " + chapter + ":" + verse + ", KJV*\n"
                try:
                    await channel_obj.send(response)
                except:
                    e = discord.exc_info()[0]
                    await log_message("Exception sending verse: " + str(e))

        await asyncio.sleep(1)     
        
bible_kjv_text = {} 
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    try:
        connection = mysql.connector.connect(host='localhost', database='ChurchBot', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='ChurchBot', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='ChurchBot', user='REDACTED', password='REDACTED')
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

async def load_bible():
    global bible_kjv_text
    
    await log_message("Loading Bible...")
    
    bible_file = "/home/REDACTED/BotMaster/pg10.txt"
    
    verse_re = re.compile(r"(?P<chapter>\d+):(?P<verse>\d+) (?P<versetext>.+)", re.MULTILINE | re.S)
    book_re = re.compile(r"Book|Gospel|Epistle|^[A-Z][a-z]+$|The Song of Solomon")
    book_title_re = re.compile(r"Book of Moses:  Called (?P<booktitle1>[A-Za-z]+)|Book of the Prophet (?P<booktitle2>[A-Za-z]+)|Book of the (?P<booktitle3>[A-Za-z]+)|Book of (?P<booktitle4>[A-Za-z]+)")
    gospel_title_re = re.compile(r"Gospel According to Saint (?P<booktitle>[A-Za-z]+)")
    epistle_title_re = re.compile(r"Epistle of Paul the Apostle to (?:the){0,1} {0,1}(?P<booktitle1>[A-Za-z]+)|(?:Epistle|Epistle General) of (?P<booktitle2>.+)")
    other_title_re = re.compile(r"^(?P<booktitle>.+)$|Revelation")
    
    f = open(bible_file, 'r')
    new_chapter = False
    new_verse = False
    chapter = ""
    verse = ""
    current_book = "" 
    for line in f:
        new_verse = False
        book_line = False
        if not line.strip() or re.search(r"Otherwise called",line):
            continue
        m = book_re.search(line)
        
        if m:
            book_line = True
            chapter = 1
            verse = 1
            n1 = book_title_re.search(line)
            if n1:
                if n1.group('booktitle1'):
                    book_title = n1.group('booktitle1')
                elif n1.group('booktitle2'):
                    book_title = n1.group('booktitle2')
                elif n1.group('booktitle3'):
                    book_title = n1.group('booktitle3')
                elif n1.group('booktitle4'):
                    book_title = n1.group('booktitle4')
            n2 = gospel_title_re.search(line)
            if n2 and not n1:
                book_title = n2.group('booktitle')
            n5 = epistle_title_re.search(line)
            if n5 and not n1 and not n2:
                if n5.group('booktitle1'):
                    book_title = n5.group('booktitle1')
                elif n5.group('booktitle2'):
                    book_title = n5.group('booktitle2')

            n3 = re.search(r"^The Revelation", line)
            if n3 and not n1 and not n2 and not n5:
                book_title = "Revelation"
            n4 = other_title_re.search(line)
            if n4 and not n1 and not n2 and not n3 and not n5:
                book_title = n4.group('booktitle')
            n6 = re.search("Song of Solomon",line)
            if n6:
                book_title = "Song of Solomon"
            q1 = re.search(r"First", line)
            if q1 and "Moses" not in line:
                book_title = "1 " + book_title
            q2 = re.search(r"Second", line)
            if q2 and "Moses" not in line:
                book_title = "2 " + book_title
            q3 = re.search(r"Third", line)
            if q3 and "Moses" not in line:
               book_title = "3 "+  book_title
            book_title = book_title.strip()
            bible_kjv_text[book_title]  = {} 
            current_book = book_title
            await log_message("New book: " + book_title)
        m = verse_re.search(line)
        if m:
            new_verse = True
            chapter = m.group('chapter')
            verse = m.group('verse')
            verse_text = m.group('versetext')
            if verse == '1':
                bible_kjv_text[current_book][chapter] = {} 
            bible_kjv_text[current_book][chapter][verse] = verse_text.replace('\n',' ')
        if not new_verse and not book_line:
            bible_kjv_text[current_book][chapter][verse] = bible_kjv_text[current_book][chapter][verse] + line.replace('\n',' ')
            
            
    await log_message("Bible loaded.")

async def search_bible(term):
    global bible_kjv_text
    response = " "
    await log_message(term)
    for book in list(bible_kjv_text.keys()):
        for chapter in list(bible_kjv_text[book].keys()):
            for verse in list(bible_kjv_text[book][chapter].keys()):
                if re.search(term, bible_kjv_text[book][chapter][verse], re.IGNORECASE):
                    response = response + "**" + book + " " + chapter + ":" + verse + "** - " + bible_kjv_text[book][chapter][verse] + "\n"
    return response
    
@client.event
async def on_ready():
    global slash_commands
    global bible_kjv_text
    global word_of_the_day_schedule

    for guild in client.guilds:
        word_of_the_day_schedule[guild.id] = { }
    records = await select_sql("""SELECT ServerId,ChannelId,Hour,Minute FROM WOTDSchedule;""")
    for row in records:
        word_of_the_day_schedule[int(row[0])] = {}
        word_of_the_day_schedule[int(row[0])]["ChannelId"] = int(row[1])
        word_of_the_day_schedule[int(row[0])]["Hour"] = int(row[2])
        word_of_the_day_schedule[int(row[0])]["Minute"] = int(row[3])
    slash_commands = SlashCommands(client)
    slash_commands.new_slash_command(name="searchbible",description="Search the Bible for a word.")
    slash_commands.add_command_option(command_name="searchbible",option_name="text",description="The text to search for.",required=True)
    slash_commands.add_guild_slash_command(guild_id=918898876663070721,command_name="searchbible")
    
    await load_bible()
    await log_message("Logged in!")
    await client.loop.create_task(word_of_the_day()) 

@client.event
async def on_message(message):
    global bible_kjv_text
    global wotd_schedule
    
    if message.author == client.user:
        return
    if message.author.bot and message.author.id != 787355055333965844:
        return
        
    if message.content.startswith('kjv'):
        await log_message("Command recognized!")

        command_string = message.content.split(' ')
        command = command_string[1]
        parsed_string = message.content.replace("kjv " + command + " ","")
        username = message.author.name
        server_name = message.guild.name 
        await log_message("recognized command: " + command)
        print(message.content)
        if command == 'lookup':
            parsed_string = parsed_string.replace('lookup ','').replace('kjv ','')
            m = re.search(r"(?P<booktitle>\d{0,1}\s{0,1}[A-Za-z ]+?) (?P<chapter>\d+):{0,1}(?P<verse>\d+){0,1}-{0,1}(?P<endchapter>\d+){0,1}:{0,1}(?P<endverse>\d+){0,1}", parsed_string)
            if m:
                book = m.group('booktitle')
                book = re.sub(r"^ ","",book)
                chapter = m.group('chapter')
                verse = m.group('verse')
                endchapter = m.group('endchapter')
                endverse = m.group('endverse')
                await log_message(str(book) + " " + str(chapter) + " " + str(verse) + " " + str(endchapter) + " " + str(endverse))
                if endchapter and endverse:
                    verse_text = " "
                    for count_chapter in list(bible_kjv_text[book].keys()):
                        for count_verse in list(bible_kjv_text[book][chapter].keys()):
                            if int(count_chapter) >= int(chapter) and int(count_chapter) <= int(endchapter):

                                if int(count_chapter) == int(chapter) and int(count_verse) >= int(verse):
                                    await log_message("choice 1")
                                    verse_text = verse_text + "**" + count_chapter + ":" + count_verse + "** - " + bible_kjv_text[book][count_chapter][count_verse] + "\n"                                    
                                elif int(count_chapter) < int(endchapter):
                                    await log_message("choice 4")
                                    verse_text = verse_text + "**" + count_chapter + ":" + count_verse + "** - " + bible_kjv_text[book][count_chapter][count_verse] + "\n"
                                elif int(count_chapter) == int(endchapter) and int(count_verse) <= int(endverse):
                                    await log_message("choice 5")
                                    verse_text = verse_text + "**" + count_chapter + ":" + count_verse + "** - " + bible_kjv_text[book][count_chapter][count_verse] + "\n"
                elif endchapter and not endverse:
                    verse_text = " "
                    endverse = endchapter
                    endchapter = chapter
                    for count_chapter in list(bible_kjv_text[book].keys()):
                        for count_verse in list(bible_kjv_text[book][chapter].keys()):
                            if int(count_chapter) >= int(chapter) and int(count_chapter) <= int(endchapter):

                                if int(count_verse) < int(verse) and int(count_chapter) == int(endchapter):
                                    await log_message("choice 2")
                                    pass
                                elif (int(count_verse) > int(endverse) and int(count_chapter) == int(endchapter)):
                                    await log_message("choice 3")
                                    pass
                                elif int(count_chapter) == int(chapter) and int(count_verse) >= int(verse):
                                    await log_message("choice 1")
                                    verse_text = verse_text + "**" + count_chapter + ":" + count_verse + "** - " + bible_kjv_text[book][count_chapter][count_verse] + "\n"                                    
                                elif int(count_chapter) < int(endchapter):
                                    await log_message("choice 4")
                                    verse_text = verse_text + "**" + count_chapter + ":" + count_verse + "** - " + bible_kjv_text[book][count_chapter][count_verse] + "\n"
                                elif int(count_chapter) == int(endchapter) and int(count_verse) <= int(endverse):
                                    await log_message("choice 5")
                                    verse_text = verse_text + "**" + count_chapter + ":" + count_verse + "** - " + bible_kjv_text[book][count_chapter][count_verse] + "\n"                
                elif not verse:
                    verse_text = " "
                    for key in bible_kjv_text[book][chapter].keys():
                        verse_text = verse_text + "**" + key + "** " + bible_kjv_text[book][chapter][key] + "\n"
                else:        
                    verse_text = bible_kjv_text[book][chapter][verse]
                await send_message(message, "**" + parsed_string.replace('cb ','') + "**\n\n" + verse_text)
            else:
                await send_message(message, "Not a valid reference.")
        elif command == 'info' or command == 'help':
            response = "**KJV Bible Help**\n\n`kjv lookup Book Chapter:Verse` or `Chapter` or `Chapter:Verse-Chapter:Verse` -- Look up a verse or range of verses in the KJV\n`kjv randomverse` -- Get a random Bible verse\n`kjv searchbible <word>` -- Search the entire Bible for a word.\n`kjv setupvotd #channel HH:MM` Set up a verse of the day in #channel at time HH:MM (24 hour format, central time)\n`kjv invite` -- Show the bot invite."
            await send_message(message, response)
        elif command == 'randomverse':
            book = random.choice(list(bible_kjv_text.keys()))
            chapter = random.choice(list(bible_kjv_text[book].keys()))
            verse = random.choice(list(bible_kjv_text[book][str(chapter)].keys()))
            verse_text = bible_kjv_text[book][str(chapter)][str(verse)]
            response = "**RANDOM VERSE**\n\n" + verse_text + "\n" + "*" + book + " " + chapter + ":" + verse + ", KJV*\n"
            await send_message(message, response)
        elif command == 'searchbible':
            parsed_string = parsed_string.replace('searchbible ','').replace('kjv ','')
            if len(parsed_string) < 6:
                await send_message(message, "The search term must be at least six characters.")
                return
            response = await search_bible(parsed_string)
            await send_message(message, response)
        elif command == 'setupvotd':
            if not message.channel_mentions:
                await send_message(message, "No target channel specified!")
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
            
            word_of_the_day_schedule[message.guild.id] = { }
            word_of_the_day_schedule[message.guild.id]["Hour"] = int(hour)
            word_of_the_day_schedule[message.guild.id]["Minute"] = int(minute)
            word_of_the_day_schedule[message.guild.id]["ChannelId"] = int(target_channel)
            records = await select_sql("""SELECT Id FROM WOTDSchedule WHERE ServerId=%s;""", (str(message.guild.id),))
            if not records:
                result = await commit_sql("""INSERT INTO WOTDSchedule (ServerId,ChannelId,Hour,Minute) VALUES (%s, %s, %s, %s);""", (str(message.guild.id),str(target_channel),str(hour),str(minute)))
                if result:
                    await send_message(message, "Time for verse of the day set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await send_message(message, "Database error!")
            else:
                result = await commit_sql("""UPDATE WOTDSchedule Set ChannelId=%s,Hour=%s,Minute=%s WHERE ServerId=%s;""", (str(target_channel),str(hour),str(minute), str(message.guild.id)))
                if result:
                    await send_message(message, "Time for verse of the day set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await send_message(message, "Database error!")          
        elif command == 'invite':
            await send_message(message, "Invite KJV Bible: https://discord.com/api/oauth2/authorize?client_id=812571422190862377&permissions=67584&scope=bot")
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
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await send_message(message,"Admin command only!")
                return   
            await send_message(message, "Server count: " + str(len(client.guilds)))             
@client.event
async def on_interaction(member, interaction):
    global slash_commands
    print("called here" + str(interaction))
    slash_commands.convert_to_message(interaction, member, "kjv ")
client.run'REDACTED'

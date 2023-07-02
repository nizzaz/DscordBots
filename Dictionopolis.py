
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

intents = discord.Intents.all()
client = discord.Client(heartbeat_timeout=600,intents=intents)
quiz_event = { }
quiz_difficulty = { }
quiz_answer = { }
poetry_tag_event = { }
poetry_tag_users = { }
poetry_tag_mode = { }
poetry_tag_current_user = {}
poetry_tag_tandem_poem = {}
poetry_tag_topic = { }
quiz_scores = {}
word_of_the_day_schedule = {}
word_of_the_day_score = 70
entry_limit = 100
connection = mysql.connector.connect(host='localhost', database='AuthorMatonTest', user='REDACTED', password='REDACTED') 
pos_translator = { 'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 'r': 'Adverb', 's': 'Satellite Adjective'}
tag_translator = {'CC': "coordinating conjunction",
    'CD': "cardinal digit",
    'DT': "determiner",
    'EX': "existential there",
    'FW': "foreign word",
    'IN': "preposition/subordinating conjunction",
    'JJ': "adjective",
    'JJR': "adjective, comparative",
    'JJS': "adjective, superlative",
    'LS': "list marker 1)",
    'MD': "modal could, will",
    'NN': "noun, singular",
    'NNS': "noun plural",
    'NNP': "proper noun, singular",
    'NNPS': "proper noun, plural",
    'PDT': "predeterminer",
    'POS': "possessive ending",
    'PRP': "personal pronoun",
    'PRP$': "personal pronoun possessive",
    'RB': "adverb",
    'RBR': "adverb, comparative",
    'RBS': "adverb, superlative",
    'RP': "particle",
    'TO': "to go 'to' the store.",
    'UH': "interjection",
    'VB': "verb, base form",
    'VBD': "verb, past tense",
    'VBG': "verb, gerund/present participle",
    'VBN': "verb, past participle",
    'VBP': "verb, sing. present, non-3d",
    'VBZ': "verb, 3rd person sing. present",
    'WDT': "wh-determiner which",
    'WP': "wh-pronoun who, what",
    'WP$': "wh-pronoun possessive whose",
    'WRB': "wh-abverb where, when" }
pronunciations = nltk.corpus.cmudict.entries()
wotd_words = [ n for n in wn.all_lemma_names() if len(n) > 12 and not re.search(r"_",n) ]
all_words = [ n for n in wn.all_lemma_names()]

async def word_of_the_day():
    global word_of_the_day_schedule
    await client.wait_until_ready()
    global wotd_words
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
            if word_of_the_day_schedule[server_id]["Hour"] == current_hour and word_of_the_day_schedule[server_id]["Minute"] == current_minute and current_second <= 1:
                print("WOTD writing...")
                channel_obj = client.get_channel(word_of_the_day_schedule[server_id]["ChannelId"])
                
                wotd = random.choice(wotd_words)
                embed = discord.Embed(title="The Word of the Day is " + wotd.replace("_"," "))
                syns = wn.synsets(wotd)
                
                parts_of_speech = {}
                counter = {} 
                await log_message(str(syns))
                for syn in syns:
                    try: parts_of_speech[syn.pos()]
                    except: parts_of_speech[syn.pos()] = ""
                    try: counter[syn.pos()]
                    except: counter[syn.pos()] = 1
                    
                    parts_of_speech[syn.pos()] += (str(counter[syn.pos()]) + ". " + syn.definition() + "\n") 
                    counter[syn.pos()] = counter[syn.pos()] + 1
                for part_of_speech in parts_of_speech:
                    embed.add_field(name=pos_translator[part_of_speech],value=parts_of_speech[part_of_speech])                
                await channel_obj.send(embed=embed)
                
        await asyncio.sleep(1)     

def reconnect_db():
    global connection
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(host='localhost', database='AuthorMatonTest', user='REDACTED', password='REDACTED')
    return connection
  
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    global connection
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = reconnect_db()
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
    finally:
        if(connection.is_connected()):
            cursor.close()
            connection.close()
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
    finally:
        if(connection.is_connected()):
            cursor.close()
            connection.close()
async def execute_sql(sql_query):
    try:
        connection = reconnect_db()
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


    
async def admin_check(userid):
    if (userid != 610335542780887050):
        # await log_message(str(userid) + " tried to call an admin message!")
        return False
    else:
        return True
        
async def show_info(message, category):
    if category == 'literature':
        response = "***LITERATURE COMMANDS***\n\n**,savepost** -title *title* -perm *number* -post *post*: Save a post with the selected title to the database! Supports Discord formatting! Permission = 0 for only you can retrieve it, permissions = 1 for anyone to be able to retrieve it.\n\n**,getpost** *title*: Get a post with the selected title\n\n**,editpost** -title *original title* -newtitle *newtitle (optional)* -perm *0/1* -post *newpost (optional)* Update an existing post with new title, permissions and/or post content. Must be your post.\n\n**,deletepost** -title *title* Delete a post with that title. You must be the author to delete it.\n\n**,wordcount** *post* Get the number of words in the post.\n\n"

    elif category == 'dictionary':
        response = ">>> ***DICTIONARY AND THESAURUS COMMANDS***\n\n**,define** *word or phrase* Look in the dictionary database for a word definition.\n\n**,synonyms** *word or phrase* Get words that mean similarly to this word.\n\n**,antonyms** *word or phrase* Get words that mean the opposite of this word.\n\n**,rhymes** *word or phrase* Get words that rhyme with this one.\n\n**,sentences** *word or phrase* Use this word in a sentence.\n\n**,slang** *word or phrase* Get the first definition on UrbanDictionary for this word.\n\n**,randomslang** *word or phrase* Get a random definition from UrbanDictionary for this word.\n\n**,postag** *sentences* Attempt to tag each word with the correct part of speech in a sentence or sentences."
    elif category == 'poetrytag':
        response = ">>> ***POETRY TAG COMMANDS***\n\n**,poetrytag** *user mentions* -topic *topic* -mode *mode*\nStart a poetry tag on your server. Mention the users participating, then specify a topic and mode. Any topic is valid, but specifiying *random* will pick a topic from the database. Valid modes are *tag*, where each poet writes an entire poem, and *tandem* where each poet writes one line.\n\n**,tag** *post* Submit your poem or line for poetry tag.\n\n**,finishtag** Stop the poetry tag and print the tandem poem if in tandem mode. Poems can be saved using .savepost.\n\n"
    elif category == 'quiz':
        response = ">>> ***QUIZ COMMANDS***\n\n**,quiz** *difficulty*\nGet a random definition from the database and the first one to answer with .answer *word or phrase* gets it right!\nDifficulty levels are easy, medium, hard and nightmare. The higher the difficulty, the more points it's worth, but answer incorrectly and lose those points, and yes, you can go negative!\n\n**,answer** *word or phrase* Answer a quiz question.\n\n**,hint** Get a hint for the quiz word.\n\n**,pass** End the quiz without losing points and see the answer.\n\n**,myscore** See your current score.\n\n**,leaderboard** See the current server scoreboard.\n\n"
    elif category == 'wotd':
        response = ">>> ***WORD SEARCH COMMANDS***\n\n**,randomword** Get a random word and definition from the dictionary.**,wordoftheday** Get a word of the day from the dictionary.\n\n**,setupwotd hh:mm #channelmention** Set up the word of the day to run at hh:mm (24 hour format, central time) in the mentioned channel."
    else:
        response = "**This is the Dictionopolis bot, the writer help bot!**\n`Written by The Midnight#1984`\n\nType one of the following categories to see commands.\n\n`literature`: Commands for saving and loading posts, and word counts.\n`dictionary`: Dictionary and thesaurus commands.\n`poetrytag`: Commands for managing poetry tag, which allows users to write a poem together.\n`quiz`: Use word quizzes and compete with other users.\n`wotd`: Commands to retrieve or set up a word of the day.\n\nSupport Server: https://discord.gg/QRWem3w"
 
    await message.channel.send(response)


@client.event
async def on_ready():
    global quiz_scores
    global quiz_event
    global poetry_tag_event
    global poetry_tag_users
    global poetry_tag_topic
    global poetry_tag_mode
    global quiz_difficulty
    global word_of_the_day_schedule
    global all_words

    # await log_message("Logged in!")
    for guild in client.guilds:
        quiz_event[guild.id] = False
        poetry_tag_event[guild.id] = False
        word_of_the_day_schedule[guild.id] = { }
    records = await select_sql("""SELECT ServerId,ChannelId,Hour,Minute FROM WOTDSchedule;""")
    for row in records:
        word_of_the_day_schedule[int(row[0])]["ChannelId"] = int(row[1])
        word_of_the_day_schedule[int(row[0])]["Hour"] = int(row[2])
        word_of_the_day_schedule[int(row[0])]["Minute"] = int(row[3])
        
            
@client.event
async def on_guild_join(guild):
    global quiz_event
    global poetry_tag_event
    global word_of_the_day_schedule
    # await log_message("Joined guild " + guild.name)
    quiz_event[guild.id] = False
    poetry_tag_event[guild.id] = False
    word_of_the_day_schedule[guild.id] = { }
    # await log_message("Creating leaderboard...")
 
    await log_message("Done!")
    
@client.event
async def on_guild_remove(guild):
    global quiz_event
    global poetry_tag_event
    await log_message("Left guild " + guild.name)
    quiz_event[guild.id] = None
    poetry_tag_event[guild.id] = None
    result = await commit_sql("""DELETE FROM QuizScores WHERE ServerId=%s;""",(str(guild.id),))
    await log_message("Purged Quiz scores.")
    
    
@client.event
async def on_member_remove(member):
    await log_message("Member " + member.name + " left guild " + member.guild.name)
    create_score_entry = """DELETE FROM QuizScores Where UserId=%s;"""   
    score_entry = (str(member.id),)
    result = await commit_sql(create_score_entry, score_entry)
    await log_message("Deleted quiz score entry for user.")  
    
@client.event
async def on_message(message):
    global word_of_the_day_score
    global quiz_answer
    global quiz_event
    global quiz_scores
    global entry_limit
    global poetry_tag_event
    global poetry_tag_users
    global poetry_tag_topic
    global poetry_tag_mode
    global poetry_tag_current_user
    global poetry_tag_tandem_poem
    global pos_translator
    global tag_translator
    global pronunciations
    
    if message.author == client.user:
        return
    if message.author.bot:
        return

            
    if message.content.startswith(','):


        command_string = message.content.split(' ')
        command = command_string[0].replace(',','')
        parsed_string = message.content.replace("," + command + " ","")
        if parsed_string == ',' + command:
            parsed_string = ''
            
        username = message.author.name
        server_name = message.guild.name
#        if not message.channel.nsfw and re.search(r"sayhi|info|help|initialize|savepost|getpost|deletepost|editpost|wordcount|define|definelike|reversedefine|synonyms|antonyms|rhymes|sentences|derivedterms|slang|randomslang|translate|poetrytag|tag|finishtag|quiz|answer|hint|pass|myscore|leaderboard|randomword|wordsearch|wordpattern|wordscore|wordoftheday",command, re.S | re.MULTILINE):
#            await send_message(message, "Author-Maton can only function in NSFW channels due to Discord TOS. Please try again in a NSFW channel!")
#            return
        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        if (command == 'sayhi'):
            await message.channel.send("Hello there, " + username + "!")
                
        elif (command == 'info' or command == 'help'):
            await show_info(message, parsed_string)
            
        elif (command == 'initialize'):
            if not await admin_check(message.author.id):
                await send_message("Admin command only!")
                return

        elif command == 'serverlist':
            if not await admin_check(message.author.id):
                await send_message(message, "Nope.")
                return
            response = "**SERVER LIST**\n\n"
            for guild in client.guilds:
                response = response + guild.name + "\n"
            await send_message(message, response)
        elif (command == "savepost"):
            title_re = re.compile("-title (.*) -perm", re.MULTILINE | re.S)
            post_re = re.compile("-post (.*)", re.MULTILINE | re.S)
            perm_re = re.compile("-perm (\d)", re.MULTILINE | re.S)
            
            m = title_re.search(parsed_string)
            if not m:
                await send_message(message, "No title tag specified!")
                return
            title = m.group()
            title = title.replace("-title ","")
            title = title.replace("-perm","")
            title = title.strip()
            
            
            m = perm_re.search(parsed_string)
            perm = m.group()
            perm = perm.replace("-perm ","")
            
            m = post_re.search(parsed_string)
            if not m:
                await send_message(message, "No post specified!")
                return
                
            post = m.group()
            post = post.replace("-post ","")
            
            author = message.author.id
            
            await log_message("Title: " + title + "\nAuthor: " + str(author) + "\n Post Content: " + post)
            
            save_post_query = """INSERT INTO Literature (Title, Author, Permissions, PostContent) VALUES (%s, %s, %s, %s);"""
            post_to_save = (title, str(author), perm, post)
            result = await commit_sql(save_post_query, post_to_save)
            if result:
                await send_message(message, "Post " + str(title) + " saved successfully.")
            else:
                await send_message(message, "Database error!")
        
        elif (command == 'getpost'):
            parsed_string = parsed_string.replace("-title ","").strip()
            await log_message("Title: " + parsed_string)
            
            get_post_query = """SELECT Title,Author,PostContent,Permissions FROM Literature WHERE Title=%s;"""
            records = await select_sql(get_post_query, (parsed_string,))
            
            for row in records:
                author_name = get(client.get_all_members(), id=int(row[1]))
                if (row[3] == 0 and message.author.id != int(row[1])):
                    await send_message(message, "This author has not granted permission for this post to be retrieved.")
                    return                        
                else:
                    await send_message(message, "**" + str(row[0]) + "**\n*By " + author_name.name + "*\n\n" + row[2])
        elif (command == "editpost"):
            title_re = re.compile("-title (.*?) -", re.MULTILINE | re.S)
            newtitle_re = re.compile("-newtitle (.*?) -", re.MULTILINE | re.S)
            post_re = re.compile("-post (.*)", re.MULTILINE | re.S)
            perm_re = re.compile("-perm (\d)", re.MULTILINE | re.S)
            post = " "
            m = title_re.search(parsed_string)
            if not m:
                await send_message(message, "No title tag specified!")
                return
            title = m.group()
            title = title.replace("-title ","")
            title = title.replace(" -","")
            title = title.strip()
            
            m = newtitle_re.search(parsed_string)
            if m:
                new_title = m.group()
                new_title = new_title.replace("-newtitle ","").replace(" -","")
            else:
                new_title = title
                
            
            m = perm_re.search(parsed_string)
            perm = m.group()
            perm = perm.replace("-perm ","")
            
            m = post_re.search(parsed_string)
            if m:
                save_post_query = """UPDATE Literature SET Title=%s,Permissions=%s,PostContent=%s WHERE Title=%s AND Author=%s;"""
                post = m.group()
                post = post.replace("-post ","")
            else:
                save_post_query = """UPDATE Literature SET Title=%s,Permissions=%s WHERE Title=%s AND Author=%s;"""
                
            get_post_author = """SELECT Author FROM Literature WHERE Title=%s;"""
            records = await select_sql(get_post_author, (title,))
            for row in records:
                if int(row[0]) != message.author.id:
                    await send_message(message, "This post isn't yours! Unable to update!")
                    return
                    
            
            author = message.author.id
            
            await log_message("Title: " + new_title + "\nAuthor: " + str(author) + "\n Post Content: " + post)
            if (post == " "):
                post_to_save = (new_title, str(perm), title, str(message.author.id))
            else:
                post_to_save = (new_title, str(perm), post, title, str(message.author.id))
            result = await commit_sql(save_post_query, post_to_save)
            if result:
                await send_message(message, "Post " + str(title) + " updated successfully.")
            else:
                await send_message(message, "Database error!")
        elif (command == 'deletepost'):
            title_re = re.compile("-title (.*)", re.MULTILINE | re.S)
            m = title_re.search(parsed_string)
            if not m:
                await send_message(message, "No title tag specified!")
                return
            title = m.group()
            title = title.replace("-title ","")
            title = title.strip()
            get_post_author = """SELECT Author FROM Literature WHERE Title=%s;"""
            records = await select_sql(get_post_author, (title,))
            for row in records:
                if int(row[0]) != message.author.id:
                    await send_message(message, "This post isn't yours! Unable to delete!")
                    return
            delete_post = """DELETE FROM Literature WHERE Title=%s AND Author=%s;"""
            post_delete_entry = (title, str(message.author.id))
            result = commit_sql(delete_post, post_delete_entry)
            if result:
                await send_message(message, "Post " + str(title) + " deleted successfully.")
            else:
                await send_message(message, "Database error!")            
                    
        elif (command == 'resetliterature'):
            if not await admin_check(message.author.id):
                await send_message("Admin command only!")
                return
            clear_all_query = """DROP TABLE IF EXISTS Literature; CREATE TABLE Literature (Id int auto_increment, Title varchar(400), Author varchar(100), Permissions int, PostContent varchar(1900), PRIMARY KEY (Id));"""
            result = await execute_sql(clear_all_query)
            if result:
                await send_message(message, "Database created successfully.")
            else:
                await send_message(message, "Database error!")

        elif (command == 'rhymes'):
            if not parsed_string:
                await send_message(message, "No word specified!")
                return
            syllables = [(word, syl) for word, syl in pronunciations if word == parsed_string]
            response = "**Rhymes for the word " + parsed_string + "**"
            await log_message(str(syllables))
            level = len(syllables[0][1]) - 1
            rhymes = []
            for (word, syllable) in syllables:
                rhymes += [word for word, pron in pronunciations if pron[-level:] == syllable[-level:]]
            values = ""
            for rhyme in rhymes:
                values = values + rhyme + ", "
            await log_message(values)
            await send_message(message, response + "\n\n" + re.sub(r", $","",values))
        elif (command == 'define'):
            if parsed_string == "":
                await send_message(message, "No word specified!")
                return
            syns = wn.synsets(parsed_string)
            if not syns:
                await send_message(message, "No definition found for the word " + parsed_string + ".")
                return
            embed = discord.Embed(title="Definition for the word " + parsed_string)
            
            parts_of_speech = {}
            counter = {} 
            response = "**Definitions for the word " + parsed_string + "**\n\n"
            await log_message(str(syns))
            for syn in syns:
                try: parts_of_speech[syn.pos()]
                except: parts_of_speech[syn.pos()] = ""
                try: counter[syn.pos()]
                except: counter[syn.pos()] = 1
                
                parts_of_speech[syn.pos()] += (str(counter[syn.pos()]) + ". " + syn.definition() + "\n") 
                counter[syn.pos()] = counter[syn.pos()] + 1
            for part_of_speech in parts_of_speech:
                embed.add_field(name=pos_translator[part_of_speech],value=parts_of_speech[part_of_speech])
                
                
            await message.channel.send(embed=embed)
        elif (command == 'randomword'):
            wotd = random.choice(all_words)
            embed = discord.Embed(title="Random Word: " + wotd.replace("_"," "))
            syns = wn.synsets(wotd)
            
            parts_of_speech = {}
            counter = {} 
            await log_message(str(syns))
            for syn in syns:
                try: parts_of_speech[syn.pos()]
                except: parts_of_speech[syn.pos()] = ""
                try: counter[syn.pos()]
                except: counter[syn.pos()] = 1
                
                parts_of_speech[syn.pos()] += (str(counter[syn.pos()]) + ". " + syn.definition() + "\n") 
                counter[syn.pos()] = counter[syn.pos()] + 1
            for part_of_speech in parts_of_speech:
                embed.add_field(name=pos_translator[part_of_speech],value=parts_of_speech[part_of_speech])                
            await message.channel.send(embed=embed)
       
        elif command == 'postag':
            if not parsed_string:
                await send_message(message, "No input to tag!")
                return
            text = nltk.word_tokenize(parsed_string)
            pos_tags = nltk.pos_tag(text)
            response = "**Words parsed:**\n\n"
            for word_tuple in pos_tags:
                try:
                    response = response + " " + word_tuple[0] + " *(" + tag_translator[word_tuple[1]] + ")* "
                except:
                    pass
            await send_message(message, response)

            
        elif (command == 'synonyms'):
            if parsed_string == "":
                await send_message(message, "No word specified!")
                return
            embed = discord.Embed(title="Synyonyms for the word " + parsed_string)
            response = "**Synonyms for the word " + parsed_string + "**\n\n"
            syns = wn.synsets(parsed_string)
            if not syns:
                await send_message(message, "No synonyms found for the word " + parsed_string + ".")
                return
            for syn in syns:
                lemma_title = syn.definition()
                values = ""
                for l in syn.lemmas():
                    values = values + l.name().replace("_"," ") + ", "
                values = re.sub(r", $","",values)
                if values == parsed_string.lower():
                    continue
                embed.add_field(name=lemma_title,value=values)
                
            await message.channel.send(embed=embed)
           
        elif (command == 'antonyms'):
            if parsed_string == "":
                await send_message(message, "No word specified!")
                return
            embed = discord.Embed(title="Antonyms for the word " + parsed_string)
            syns = wn.synsets(parsed_string)
            if not syns:
                await send_message(message, "No antonyms found for the word " + parsed_string + ".")
                return
            for syn in syns:
                lemma_title = syn.definition()
                values = ""
                for l in syn.lemmas():
                    if l.antonyms():
                        ant_set = l.antonyms()
                        
                        for ant in ant_set:
                            ant_synset = ant.synset()
                            for lant in ant_synset.lemmas():
                                values = values + lant.name().replace("_"," ") + ", "
                values = re.sub(r", $","",values)
                if values == parsed_string.lower():
                    continue
                if values:
                    embed.add_field(name=lemma_title,value=values)
            if discord.Embed(title="Antonyms for the word " + parsed_string) == embed:
                await send_message(message, "No antonyms found for the word " + parsed_string + ".")
                return
                
            await message.channel.send(embed=embed)


        elif (command == 'randomslang'):

            if (message.channel.nsfw):
                word = parsed_string
                if not word:
                    await send_message(message,"No word specified!")
                    return
                
                URL = "http://api.urbandictionary.com/v0/define?term=" + word
                r = requests.get(url = URL)
                data = r.json()
                
                if not data:
                    await send_message(message, "No slang definition found for " + word)
                    return
                
                definition = data["list"][random.randint(0,len(data["list"])-1)]["definition"]
                definition = definition.replace("[","")
                definition = definition.replace(']',"")
                
                await send_message(message, "**" + word + "**\n\n" + definition)
            else:
                await send_message(message, "This is not a NSFW channel. Please issue slang commands in a NSFW channel.")
        elif (command == 'sentences'):

            if not parsed_string:
                await send_message(message, "No word specified!")
                return
            embed = discord.Embed(title="Example sentences for the word " + parsed_string)
            syns = wn.synsets(parsed_string)
            if not syns:
                await send_message(message, "No example sentences found for the word " + parsed_string + ".")
                return
            for syn in syns:
                lemma_title = syn.definition()
                values = ""
                for example in syn.examples():
                    values = values + example.capitalize() + ".; "
                values = re.sub(r"; $","",values)
                if values == parsed_string.lower() or not values:
                    continue
                embed.add_field(name=lemma_title,value=values)
                
            await message.channel.send(embed=embed)                

                
        elif (command == 'slang'):
            if(message.channel.nsfw):
                word = message.content.replace(",slang ","")
                if not word:
                    await send_message(message, "No word specified!")
                    return
                
                URL = "http://api.urbandictionary.com/v0/define?term=" + word
                r = requests.get(url = URL)
                data = r.json()
                if not data:
                    await send_message(message, "No definition found for " +word)
                    return
                
                definition = data["list"][0]["definition"]
                definition = definition.replace("[","")
                definition = definition.replace(']',"")
                
                await send_message(message, "**" + word + "**\n\n" + definition)
            else:
                await send_message(message, "This is not a NSFW channel. Please issue slang commands in a NSFW channel.")            
 
        elif (command == 'quiz'):
            parsed_string = message.content.replace(".quiz ","")
            get_wordscore = " "
            quiz_difficulty[message.guild.id] = parsed_string
            quiz_event[message.guild.id] = True
            if parsed_string == 'easy':
                words = [ n for n in wn.all_lemma_names() if len(n) >= 3 and len(n) <= 6 ]
            elif parsed_string == 'medium':
                gwords = [ n for n in wn.all_lemma_names() if len(n) >= 7 and len(n) <= 11 ]
            elif parsed_string == 'hard':
                words = [ n for n in wn.all_lemma_names() if len(n) >= 12 and len(n) <= 18 ]
            elif parsed_string == 'nightmare':
                words = [ n for n in wn.all_lemma_names() if len(n) >= 19]
            else:
                words = [ n for n in wn.all_lemma_names() if len(n) >= 3 and len(n) <= 15 ]
                
            async with message.channel.typing():

                word  = random.choice(words)
                await log_message("Word quiz: " + word)
                part_of_speech = tag_translator[nltk.pos_tag(word)[0][1]]
                
                question = wn.synsets(word)[0].definition()
                response = "What word starts with " + word[0].upper() + ", is a " + part_of_speech + ", has " + str(len(word)) + " letters, and means " + question + "?"
                
                quiz_answer[message.guild.id] = word
                embed = discord.Embed(title="Word Quiz!",description=response)
                
            await message.channel.send(embed=embed)

        elif (command == 'answer'):

            quiz_score = 0
            if not quiz_event[message.guild.id]:
                await send_message(message, "No quiz currently active! Type **.quiz** to start a word quiz.\n")
                return  
            id_num = message.author.id
            guild_id = message.guild.id
            get_current_score = """SELECT Score FROM QuizScores WHERE ServerId=%s AND UserId=%s;"""
            records = await select_sql(get_current_score, (str(guild_id), str(id_num)))
            if not records:
                create_score_entry = """INSERT INTO QuizScores (ServerId, UserId, Score) VALUES(%s, %s, %s);"""   
                score_entry = (str(member.guild.id), str(member.id), str(0))
                result = await commit_sql(create_score_entry, score_entry)
                await log_message("Created quiz score entry for user.")
            for row in records:
                quiz_score = int(row[0])
            if (quiz_answer[message.guild.id].lower() == parsed_string.lower()):
                await send_message(message, "Yes, the answer was " + str(quiz_answer[message.guild.id]) + "! Correct!")

                
                if quiz_difficulty[message.guild.id] == 'easy':
                    quiz_score = quiz_score + 1
                elif quiz_difficulty[message.guild.id] == 'medium':
                    quiz_score = quiz_score + 2
                elif quiz_difficulty[message.guild.id] == 'hard':
                    quiz_score = quiz_score + 4
                elif quiz_difficulty[message.guild.id] == 'nightmare':
                    quiz_score = quiz_score + 8
                else:
                    quiz_score = quiz_score + 1
                    
                await send_message(message, "Your new quiz score is **"  + str(quiz_score) + "**.")
  
                update_score_entry = """UPDATE QuizScores Set Score=%s WHERE ServerId=%s AND UserId=%s;"""   
                score_entry = (str(quiz_score), str(guild_id), str(id_num))

                result = await commit_sql(update_score_entry, score_entry)
                if not result:
                    await send_message(message, "Database error! " + str(error))   
            
            else:
                await send_message(message, "Sorry, the answer was " + str(quiz_answer[message.guild.id]) + ".")
                if quiz_difficulty[message.guild.id] == 'easy':
                    quiz_score = quiz_score - 1
                elif quiz_difficulty[message.guild.id] == 'medium':
                    quiz_score = quiz_score - 2
                elif quiz_difficulty[message.guild.id] == 'hard':
                    quiz_score = quiz_score - 4
                elif quiz_difficulty[message.guild.id] == 'nightmare':
                    quiz_score = quiz_score - 8
                else:
                    quiz_score = quiz_score - 1
                    
                await send_message(message, "Your new quiz score is **"  + str(quiz_score) + "**.")
  
                update_score_entry = """UPDATE QuizScores Set Score=%s WHERE ServerId=%s AND UserId=%s;"""   
                score_entry = (str(quiz_score), str(guild_id), str(id_num))

                result = await commit_sql(update_score_entry, score_entry)
            quiz_event[message.guild.id] = False
            quiz_answer[message.guild.id] = " "
        elif (command == 'pass'):
            if not quiz_event[message.guild.id]:
                await send_message(message, "No quiz currently active! Type **.quiz** to start a word quiz.\n")
                return 
            quiz_event[message.guild.id] = False
            await send_message(message, "Passing on this question. No points deducted!\nThe answer was **" + str(quiz_answer[message.guild.id]) + "**.")
        elif (command == 'myscore'):
            my_id = message.author.id
            guild_id = message.guild.id
            get_my_score = """SELECT Score FROM QuizScores WHERE ServerId=%s AND UserId=%s;"""
            async with message.channel.typing():
                records = await select_sql(get_my_score, (str(guild_id), str(my_id)))
            if not records:
                create_score_entry = """INSERT INTO QuizScores (ServerId, UserId, Score) VALUES(%s, %s, %s);"""   
                score_entry = (str(member.guild.id), str(member.id), str(0))
                result = await commit_sql(create_score_entry, score_entry)
                await log_message("Created quiz score entry for user.")
            response = "Your current quiz score is **"
            for row in records:
                score = str(row[0])
            response = response + score + "**."
            await send_message(message, response)
        elif (command == 'leaderboard'):
            get_leaderboard = """SELECT UserId,Score FROM QuizScores WHERE ServerId=%s ORDER BY Score DESC;"""
            guild_id = message.guild.id
            async with message.channel.typing():
                records = await select_sql(get_leaderboard, (str(guild_id),))

            if len(records) == 0:
                await send_message(message, "No score found for the specified server.")
                return
            response = "**Quiz Leaderboard:**\n\n"
            for row in records:
                username = discord.utils.get(message,guild.members, id=int(row[0]))
                response = response + str(username.name) + " - " + str(row[1]) + "\n"
            await send_message(message, response)
            
        elif (command == 'hint'):

            if not quiz_event[message.guild.id]:
                await send_message(message, "No quiz currently active! Type **.quiz** to start a word quiz.\n")
            hint = quiz_answer[message.guild.id][0]
            letters = len(quiz_answer[message.guild.id])
            await send_message(message, "The first letter of the word is " + hint + " and it has " + str(letters) + " letters.")
            
        elif (command == 'wordcount'):
            if not parsed_string:
                await send_message(message, "No words to count!")
                return
            words_in_post = parsed_string.split()
            word_count = len(words_in_post)
            await send_message(message, "The word count is " + str(word_count) + ".")

        elif (command == 'restartbot'):

            if not await admin_check(message.author.id):
                await send_message(message, "Admin command only!")
                return
            await send_message(message, "Restarting bot...")
            output = subprocess.run(["/home/REDACTED/restartbot.sh"], universal_newlines=True, stdout=subprocess.PIPE)

        elif (command == 'wordsearch'):

            start_letter = command_string[1]
            number_of_letters = command_string[2]
            end_letter = command_string[3]
            
            if not start_letter:
                await send_message(message, "No start letter specified!")
                return
            if not number_of_letters:
                await send_message(message, "No number of letters specified!")
                return
            if not end_letter:
                await send_message(message, "No end letters specified!")
                return

            response = "**Words that start with " + start_letter + ", end with " +end_letter + ", with " + number_of_letters + " in between:**\n\n"
            for row in records:
                response = response + str(row[0]) + ", "
                
            await send_message(message, response)

        elif (command == 'wordpattern'):

            parsed_string = parsed_string.replace(" ","")
            parsed_string = parsed_string.replace("-","_")
            
            if not parsed_string:
                await send_message(message, "No pattern specified!")
                return
            
            response = "**Words that have the pattern " + parsed_string + ":**\n\n"
            for row in records:
                response = response + str(row[0]) + ", "
                
            await send_message(message, response)

            
        elif (command == 'wordoftheday' or command == 'wotd'):
            
            
            
            wotd = random.choice(wotd_words)
            embed = discord.Embed(title="The Word of the Day is " + wotd.replace("_"," "))
            syns = wn.synsets(wotd)
            
            parts_of_speech = {}
            counter = {} 
            await log_message(str(syns))
            for syn in syns:
                try: parts_of_speech[syn.pos()]
                except: parts_of_speech[syn.pos()] = ""
                try: counter[syn.pos()]
                except: counter[syn.pos()] = 1
                
                parts_of_speech[syn.pos()] += (str(counter[syn.pos()]) + ". " + syn.definition() + "\n") 
                counter[syn.pos()] = counter[syn.pos()] + 1
            for part_of_speech in parts_of_speech:
                embed.add_field(name=pos_translator[part_of_speech],value=parts_of_speech[part_of_speech])                
            await message.channel.send(embed=embed)
        elif command == 'setupwotd':
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
                    await send_message(message, "Time for word of the day set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await send_message(message, "Database error!")
            else:
                result = await commit_sql("""UPDATE WOTDSchedule Set ChannelId=%s,Hour=%s,Minute=%s WHERE ServerId=%s;""", (str(target_channel),str(hour),str(minute), str(message.guild.id)))
                if result:
                    await send_message(message, "Time for word of the day set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await send_message(message, "Database error!")                
        elif (command == 'resetscores'):
            set_score_to_zero = """UPDATE QuizScores Set Score=0 WHERE ServerId=%s;"""
            server_id = message.guild.id
            result = await commit_sql(set_score_to_zero, (server_id,))
            if result:
                await send_message(message, "Leaderboard reset to zero for all members.")
            else:
                await send_message(message, "Database error!")
            
        elif (command == 'initializeleaderboard'):
            if not await admin_check(message.author.id):
                await send_message(message, "Admin command only!")
                return
            result = await execute_sql("""DROP TABLE IF EXISTS QuizScores; CREATE TABLE QuizScores (ServerId VarChar(40), UserId VarChar(30), Score Int);""")
            if not result:
                await send_message(message,"Could not create Quiz Scores!")
            for guild in client.guilds:
                for member in guild.members:
                    create_score_entry = """INSERT INTO QuizScores (ServerId, UserId, Score) VALUES(%s, %s, %s);"""   
                    score_entry = (str(guild.id), str(member.id), str(0))
                    result = await commit_sql(create_score_entry, score_entry)
                    if not result:
                        await send_message(message, "Database error!")   

            await send_message(message, "Leaderboard initialized.") 

           
        elif (command == 'poetrytag'):
            if poetry_tag_event[message.guild.id]:
                await send_message(message, "Poetry event already started!")
                return
                
            parsed_string = message.content.replace(".poetrytag ","")
            
            users_re = re.compile(r"-users (.+?) -", re.MULTILINE | re.S)
            topic_re = re.compile(r"-topic (.+?) -", re.MULTILINE | re.S)
            mode_re = re.compile(r"-mode (.+)", re.MULTILINE | re.S)
            user_id = message.author.id

            users = message.mentions
            if not users:
                await send_message(message, "No users specified!")
                return
                
            m = topic_re.search(parsed_string)
            if not m:
                await send_message(message, "No topic specified!")
                return
            topic = m.group().replace("-topic ","").replace(" -","").strip()
            
            m = mode_re.search(parsed_string)
            if not m:
                await send_message(message, "No mode specified!")
                return
            mode = m.group().replace("-mode ","").strip()
            if not re.search(r"tag|tandem",mode):
                await send_message(message, "Valid modes are tag and tandem!")
                return
            
            if re.search("random",topic):
                topic = random.choice(["Night-time", "A particular color", "Being underwater", "A person whose life you're curious about", "Your mother's perfume", "Falling asleep or waking up", "Growing older", "The feeling of getting lost in a book", "How to know if you're in love", "A bad dream", "A ghost", "Your city; town; or neighborhood", "An important life choice you've made", "Spring; summer; fall; or winter", "Something most people see as ugly but which you see as beautiful", "Jealousy", "Becoming a parent", "An event that changed you", "A place you visited -- how you imagined it beforehand; and what it was actually like", "The ocean", "Forgetting", "The speed of light", "A voodoo doll", "Reflections on a window", "A newspaper headline", "Your greatest fear", "Your grandmother's hands", "A particular toy you had as a child", "Being invisible", "A time you felt homesick", "Having an affair; or discovering your partner is having one", "Birthdays", "A favorite food and a specific memory of eating it", "An imaginary city", "Driving with the radio on", "Life in an aquarium", "Dancing", "Walking with your eyes closed", "What a computer might daydream about", "Time travel", "Brothers or sisters", "Your job; or a job you've had", "Weddings", "Leaving home", "Camping", "A zoo", "A historical event from the perspective of someone who saw it firsthand (You will have to do some research for this).", "Holding your breath", "Intimacy and privacy", "A time you were tempted to do something you feel is wrong", "Physical attraction to someone", "A superstition you have", "Someone you admire", "Write about the taste of: an egg; an orange; medicine; cinnamon", "Write about the smell of: burning food; melting snow; the ocean; your grandparents' home; the inside of a bus; pavement after the rain", "Write about the sound of: a radio changing channels; a dog howling; a football or baseball game; your parents talking in another room", "Write about the sight of: lit windows in a house when you're standing outside at night; someone you love when he or she doesn't know you're watching; a dying plant; shadows on snow", "Write about the feeling of: grass under bare feet; a really bad kiss; the headrush when you stand up too fast; sore muscles; falling asleep in the back seat of a moving car.", "a dessert; a memory; and someone in your family", "dancing; a pitch-black room; and the smell of lilacs", "a balloon; smoke; and a keyhole", "a secret box; an ice cube tray; and a velvet ribbon", "a betrayal; soap; and a plane ticket", "Rain; snow; or a storm", "An animal you think is beautiful or strange",  "Your parents or children",  "How a kiss feels",  "The house where you were born",  "A smell that brings back memories",  "Being a teenager; becoming an adult; middle age; old age",  "Feeling lonely",  "The moon",  "Getting lost",  "Marriage or divorce",  "An imaginary friend",  "Life in the future",  "The hottest; coldest; or most exhausted you have ever felt", "Having a fever",  "A new version of a fairy-tale",  "The shapes you see in clouds",  "Format: A letter",  "Format: A recipe",  "Format: A horoscope",  "Format: A fragment from an unusual dictionary",  "Format: A prayer",  "Format: A shopping list",  "Format: A magic spell.",  "Point of view: One of your parents",  "Point of view: Your child (real or imagined)",  "Point of view: A historical figure",  "Point of view: A very old person",  "Point of view: An athlete who has just lost the big game",  "Point of view: The most popular/unpopular kid from your school",  "Point of view: An inanimate object in your home.",  "Three wishes",  "Traveling to an unknown place",  "Getting a haircut",  "A scientific fact (real or invented)",  "An insect that got into your home",  "The sound of a specific language",  "Death",  "The number 3",  "The ocean",  "Missing someone",  "Something that makes you angry",  "The feeling of writing; why you want to be a writer",  "The ups and downs of love",  "The view out your window",  "City lights at night",  "A particular work of art",  "Having a superpower",  "Being in an airplane",  "Playing a sport",  "A shadow",  "A person transformed into an animal",  "Daydream",  "Cry",  "Kiss well",  "Find happiness",  "Peel a peach",  "Silky; gigantic; and puzzle.",  "Leaf; accelerating; and sticky.",  "Skin; drastic; and dusty.",  "Interrupt; nutmeg; and crystalline.",  "Exacting; oxygen; and delicate.",  "Reptilian; arched; and honey."])
            poetry_tag_event[message.guild.id] = True
            poetry_tag_users[message.guild.id] = users
            poetry_tag_topic[message.guild.id] = topic
            poetry_tag_mode[message.guild.id] = mode
            await send_message(message, "Poetry tag event started with topic of **" + str(topic) + "** in mode **" + str(mode) + "**")
            if re.search('tag', mode):
                await send_message(message, "<@" + str(users[0].id) + ">, you are first! Type .tag and your poem!")
            if re.search('tandem', mode):
                await send_message(message, "<@" + str(users[0].id) + ">, you are first! Type .tag and your line!")
                poetry_tag_tandem_poem[message.guild.id] = " "
            poetry_tag_current_user[message.guild.id] = 0
        elif (command == 'tag'):
            if not poetry_tag_event[message.guild.id]:
                await send_message(message, "No poetry tag currently running!")
                return
            if message.author.id != poetry_tag_users[message.guild.id][poetry_tag_current_user[message.guild.id]].id:
                await send_message(message, "It's not your turn!")
                return
            if (re.search('tag',poetry_tag_mode[message.guild.id])):
                await send_message(message, "Thank you for your poem!")
                poetry_tag_current_user[message.guild.id] = poetry_tag_current_user[message.guild.id] + 1
                if poetry_tag_current_user[message.guild.id] >= len(poetry_tag_users[message.guild.id]):
                    poetry_tag_current_user[message.guild.id] = 0
                next_user = poetry_tag_users[message.guild.id][poetry_tag_current_user].id
                await send_message(message, "You're up next, <@" + next_user + ">! Type .tag followed by your poem!")
            if (re.search('tandem', poetry_tag_mode[message.guild.id])):
                await send_message(message, "Thank you for your line!")
                poetry_tag_current_user[message.guild.id] = poetry_tag_current_user[message.guild.id] + 1
                if poetry_tag_current_user[message.guild.id] >= len(poetry_tag_users[message.guild.id]):
                    poetry_tag_current_user[message.guild.id] = 0
                poetry_tag_tandem_poem[message.guild.id] = poetry_tag_tandem_poem[message.guild.id] + message.content.replace(".tag ","") + "\n"
                next_user = poetry_tag_users[message.guild.id][poetry_tag_current_user[message.guild.id]].id
                await send_message(message, "You're up next, <@" + str(next_user) + ">! Type .tag followed by your line!")
        elif (command == 'finishtag'):
            if not poetry_tag_event[message.guild.id]:
                await send_message(message, "No poetry tag currently running!")
                return
            if (re.search('tandem', poetry_tag_mode[message.guild.id])):
                await send_message(message, "Awesome! Here is your completed poem!\n\n" + poetry_tag_tandem_poem[message.guild.id])
            if (re.search('tag', poetry_tag_mode[message.guild.id])):
                await send_message(message, "Awesome! Use .savepost if you'd like to save your poem!")
            poetry_tag_users[message.guild.id] = " "
            poetry_tag_event[message.guild.id] = False
            poetry_tag_topic[message.guild.id] = " "
            poetry_tag_current_user[message.guild.id] = 0
            poetry_tag_mode[message.guild.id] = " "
            poetry_tag_tandem_poem[message.guild.id] = " " 
        elif command == 'invite':
            await send_message(message,"Click here to invite Dictionopolis: https://discord.com/api/oauth2/authorize?client_id=697627908163895307&permissions=117760&scope=bot")
       
        else:
            pass
    else:
        pass
        
    
client.loop.create_task(word_of_the_day())
client.run('REDACTED')  


import discord
import re
import mysql.connector
from mysql.connector import Error
import urllib.request
import subprocess
import time
import requests
import random
from discord.utils import get
import discord.utils
from datetime import datetime
from discord import Webhook, File
import csv
from shutil import copyfile
import asyncio
import aiohttp
from slashcommands import SlashCommands

class NakedObject(object):
    pass

manager = None

command_handler = {}    
prefix = { }
intents = discord.Intents.default()
intents.members = True
client = discord.Client(heartbeat_timeout=600,intents=intents)
hangman_game_state = {}
trivia_game_state = {} 
hangman_initial = "|---|\n|   |\n|   \n|   \n|   \n|   \n|----\n"
bad_guess = [""] * 8
bad_guess[0] = hangman_initial
bad_guess[1] = "|---|\n|   |\n|   😧\n|   \n|   \n|   \n|----\n"
bad_guess[2] = "|---|\n|   |\n|   🤬\n|   |\n|   \n|   \n|----\n"
bad_guess[3] = "|---|\n|   |\n|   😭\n|  /|\n|   \n|   \n|----\n"
bad_guess[4] = "|---|\n|   |\n|   😨\n|  /|\\ \n|   \n|   \n|----\n"
bad_guess[5] = "|---|\n|   |\n|   🥺\n|  /|\\ \n|   |\n|   \n|----\n"
bad_guess[6] = "|---|\n|   |\n|   😬\n|  /|\\ \n|   |\n|  /\n|----\n"
bad_guess[7] = "|---|\n|   |\n|   😵\n|  /|\\ \n|   |\n|  /\\ \n|----\n"
screwball_answers = ["I don't give a shit.", "Fuck off.", "Hell to the yes!", "Clear as mud.", "No, so stop asking.", "That's the dumbest question I've ever heard.", "I wouldn't if I were you.", "Ever heard of the Darwin award?", "Yeah, I guess.", "Definitely. Probably. Maybe.", "Absolutely.", "Fuck, no!", "Are you insane?", "What kind of question is that?", "Nah.", "Nope.", "Yeah, sure, why not?", "I dunno.", "Do I look like a psychic?", "Zeus says yes.", "Zeus says no.", "The stars predict that this won't happen.", "My horoscope reading says probably.", "Did a little voice tell you to ask that?", "Wait here, I'll get the men in white coats on the line.", "No way.", "Yes way.", "Aw, hell nah!", "Yeah yeah yeah.", "No! What made you think that was a possibility?", "DOES NOT COMPUTE", "PC Load Letter", "What the fuck does that mean?", "Affirmative.", "How long did that question take you to think up?", "I'll have fries with that.", "No. Just no.", "The lie detector test says that is a lie.", "The lie detector test says that is the truth.", "Yeah, whatever.", "Who knows? Ask someone smart.", "Negative.", "Uh huh.", "Uh-uh.", "-nods-", "-shakes head-", "-shrugs-", "Outlook not so good. Try GMail instead.", "Did you say something? Was I supposed to be listening?", "WHAT? OKAY! YEAH!", "Absolutely nothing, which is what you are about to become.", "My crystal screwball says...NO SIGNAL.", "The tarot card reading says...oh man, you are SCREWED!", "YES && NO || YES && !NO", "Does a bear shit in the woods?", "Is the Pope Catholic?", "Did you check Google first?", "Let me Google that for you...no, I'm even lazier than you!", "Shit shit shit RUN!", "Damn it, the coronavirus has my signals crossed...-violent coughing, flushes without washing hands-", "ERROR: Satellite out of alignment. Try again later.", "Do I look like a psychic?", "Yeah...no.","No...yeah.", "Forecast hazy, try renewable energy.", "Sorry, OUT OF ORDER.", "That divides by zero. If I answer that question, the universe will implode.", "I'd answer, but the B.O. is so strong from you I can't talk without gagging.", "It's the same, but different.", "You don't want to know.", "The answer my friend, is blowing in the wind, and it's coming from the Taco Bell I had earlier.", "What the hell is wrong with you?", "Yes, I just lied.", "No, I just lied.", "I don't care.", "How the heck should I know?", "Ask the genius who wrote this stupid bot.", "Go away, kid, you bother me.", "If a frog had wings, then he wouldn't bump his ass.", r"\"I see,\" said the blind man as he scratched his wooden leg.", "Here's a quarter, call someone who cares and ask them.", "NOOOOO!!!", "I guess?", "Maybe not.", "Who cares?", "I see the Grim for you." ]
used_hint = { } 
guessed_letters = {} 
crystal_game_state = { }
riddle_state = {} 
word_game_state = { }


async def get_letter():
    letter = ' '
    ln = random.randint(1,100)
    if ln <= 9:
        letter = 'A'
    elif ln > 9 and ln <= 11:
        letter = 'B'
    elif ln >11 and ln <= 13:
        letter = 'C'
    elif ln >13 and ln <= 17:
        letter = 'D'
    elif ln > 17 and ln <= 29:
        letter = 'E'
    elif ln > 29 and ln <= 31:
        letter = 'F'
    elif ln > 31 and ln <= 34:
        letter = 'G'
    elif ln > 34 and ln <= 36:
        letter = 'H'
    elif ln > 36 and ln <= 45:
        letter = 'I'
    elif ln > 45 and ln <= 46:
        letter = 'J'
    elif ln > 46 and ln <= 47:
        letter = 'K'
    elif ln > 47 and ln <= 51:
        letter = 'L'
    elif ln > 51 and ln <= 53:
        letter = 'M'
    elif ln > 53 and ln <= 59:
        letter = 'N'
    elif ln > 59 and ln <= 67:
        letter = 'O'
    elif ln > 67 and ln <= 69:
        letter = 'P'
    elif ln > 69 and ln <= 70:
        letter = 'Q'
    elif ln > 70 and ln <= 76:
        letter = 'R'
    elif ln > 76 and ln <= 80:
        letter = 'S'
    elif ln > 80 and ln <= 86:
        letter = 'T'
    elif ln > 86 and ln <= 90:
        letter = 'U'
    elif ln > 90 and ln <= 92:
        letter = 'V'
    elif ln > 92 and ln <= 94:
        letter = 'W'
    elif ln > 94 and ln <= 95:
        letter = 'X'
    elif ln > 95 and ln <= 97:
        letter = 'Y'
    elif ln > 97 and ln <= 98:
        letter = 'Z'
    elif ln > 98:
        letter = ' '
    else:
        pass
    return letter
    
async def get_word(parsed_string):
    database = "AuthorMaton"
    if parsed_string == 'easy':
        get_wordscore = """SELECT Word FROM WordValues WHERE WordValue<=30 ORDER BY RAND( ) LIMIT 1;"""
    elif parsed_string == 'medium':
        get_wordscore = """SELECT Word FROM WordValues WHERE WordValue>=31 AND WordValue<=70 ORDER BY RAND( ) LIMIT 1;"""
    elif parsed_string == 'hard':
        get_wordscore = """SELECT Word FROM WordValues WHERE WordValue>=71 AND WordValue<=100 ORDER BY RAND( ) LIMIT 1;"""
    elif parsed_string == 'nightmare':
        get_wordscore = """SELECT Word FROM WordValues WHERE WordValue>=101 ORDER BY RAND( ) LIMIT 1;"""
    else:
        get_wordscore = """SELECT Word FROM WordValues ORDER BY RAND( ) LIMIT 1;"""
    try:
        connection = mysql.connector.connect(host='localhost', database=database, user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(get_wordscore)
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
async def check_word(word):
    get_word = """SELECT Id FROM DictionaryDefs WHERE Word=%s AND Language='English';"""
    word_tuple = (word,)
    database = 'AuthorMaton'
    try:
        connection = mysql.connector.connect(host='localhost', database=database, user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(get_word, word_tuple)
        records = cursor.fetchall()
        await log_message("Returned " + str(records))
        if records:
            return True
        else:
            return False
            
    except mysql.connector.Error as error:
        await log_message("Database error! " + str(error))
        return None
    finally:
        if(connection.is_connected()):
            cursor.close()
            connection.close()    
    
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='Tricksy', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='Tricksy', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='Tricksy', user='REDACTED', password='REDACTED')
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
            
async def direct_message(author, response):
    channel = await author.create_dm()
    await log_message("replied to user " + author.name + " in DM with " + response)
    try:
        message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
        for chunk in message_chunks:
            await channel.send(">>> " + chunk)
            time.sleep(1)
        
    except discord.errors.Forbidden:
        pass
        
async def post_webhook(channel, name, response, picture):
    temp_webhook = await channel.create_webhook(name='Tricksy')
    await temp_webhook.send(content=response, username=name, avatar_url=picture)
    await temp_webhook.delete() 
    
async def reply_message(message, response):
    if not message.guild:
        channel_name = dm_tracker[message.author.id]["commandchannel"].name
        server_name = str(dm_tracker[message.author.id]["server_id"])
    else:
        channel_name = message.channel.name
        server_name = message.guild.name
        
    await log_message("Message sent back to server " + server_name + " channel " + channel_name + " in response to user " + message.author.name + "\n\n" + response)
    
    message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
    for chunk in message_chunks:
        await message.channel.send(">>> " + chunk)
        time.sleep(1)

async def admin_check(userid):
    if (userid != 610335542780887050):
        await log_message(str(userid) + " tried to call an admin message!")
        return False
    else:
        return True
        
async def score_word(word):
    letter_values = { "E" : 1, "A" : 1, "I" : 1, "O" : 1, "N" : 1, "R" : 1, "T" : 1, "L" : 1, "S" : 1, "U" : 1, "D" : 2, "G" : 2, "B" : 3, "C" : 2, "M" : 3, "P" : 2, "F" : 4, "H" : 4, "V" : 4, "W" : 4, "Y" : 4, "K" : 5, "J" : 8, "X" : 8, "Q" : 10, "Z" : 10, "-": 0, " " : 0, "'": 0, "À": 1,"Â":1, "Ä":1, "È":1, "Ê":1, "Ì":1, "É":1, "Í":1, "Î":1, "Ò":1, "Ô":1, "Ó":1, "Õ":1, "Ø":1, "Ù":1, "Û":1, "Ü":1, "Ú": 1, "Ã": 1, "Ï": 1, "Ñ": 2, "Ç": 2, "Á": 1, ".":0, ":":0, ",":0, "`":0, "?":0, "Ö": 1, "Å": 1, "Ń": 2, "Ā": 1, "1": 1, "2": 1, "3":1, "4":1, "5":1, "6":1, "7":1, "8":1, "9":1, "0":1, "Æ": 2, "ʻ":0, "Œ":2, "/":0, "\\":0, "<": 0, ">":0, "ǃ":0, "Ū": 1, '*':0, '+':0, "Ł": 2, "Ź":10, "Č":2, "Ć": 2, "Ë": 1, "Α":1, '£':2, "Ể":1, '&': 0, ';':0, "Ō": 1, '!':0, "Ő":1, "Þ": 2, "Ð": 2, "Ș": 2, '♨':30, "Ộ": 1, "Ý": 1,"Þ": 1,"ß": 1,"Ă": 1,"Ą": 1,"Ć": 1,"Ĉ": 1,"Ċ": 1,"Č": 1,"Ď": 1,"Ē": 1,"Ĕ": 1,"Ė": 1,"Ę": 1,"Ě": 1,"Ĝ": 1,"Ġ": 1,"Ģ": 1,"Ĥ": 1,"Ħ": 1,"Ĩ": 1,"Ī": 1,"Ĭ": 1,"Į": 1,"İ": 1,"Ĳ": 1,"Ĵ": 1,"Ķ": 1,"Ĺ": 1,"Ļ": 1,"Ľ": 1,"Ŀ": 1,"Ł": 1,"Ń": 1,"Ņ": 1,"Ň": 1,"Ŋ": 1,"Ō": 1,"Ŏ": 1,"Ő": 1,"Œ": 1,"Ŕ": 1,"Ŗ": 1,"Ř": 1,"Ś": 1,"Ŝ": 1,"Ş": 1,"Š": 1,"Ţ": 1,"Ť": 1,"Ŧ": 1,"Ũ": 1,"Ū": 1,"Ŭ": 1,"Ů": 1,"Ű": 1,"Ų": 1,"Ŵ": 1,"Ŷ": 1,"Ÿ": 1,"Ż": 1,"Ź": 1,"Ž": 1,"Ɓ": 1,"Ƈ": 1,"Ƌ": 1,"Ə": 1,"Ƒ": 1,"Ɠ": 1,"Ɨ": 1,"Ɯ": 1,"Ɲ": 1,"Ɵ": 1,"Ƣ": 1,"Ƥ": 1,"Ʀ": 1,"Ƨ": 1,"Ʃ": 1,"ƪ": 1,"Ƭ": 1,"Ʈ": 1,"Ư": 1,"Ʊ": 1,"Ʋ": 1,"Ƴ": 1,"Ƶ": 1,"Ʒ": 1,"Ƹ": 1,"ƻ": 1,"Ƽ": 1,"ƾ": 1,"ƿ": 1,"ǀ": 1,"ǁ": 1,"ǂ": 1,"ǃ": 1,"Ǆ": 1,"ǅ": 1,"Ǉ": 1,"Ǌ": 1,"Ǎ": 1,"Ǐ": 1,"Ǒ": 1,"Ǔ": 1,"Ǖ": 1,"Ǘ": 1,"Ǚ": 1,"Ǜ": 1,"Ǟ": 1,"Ǡ": 1,"Ǣ": 1,"Ǥ": 1,"Ǧ": 1,"Ǩ": 1,"Ǫ": 1,"Ǭ": 1,"Ǯ": 1,"Ǳ": 1,"Ǵ": 1,"Ǻ": 1,"Ǽ": 1,"Ǿ": 1,"Ȁ": 1,"Ȃ": 1,"Ȅ": 1,"Ȇ": 1,"Ȉ": 1,"Ȋ": 1,"Ȍ": 1,"Ȏ": 1,"Ȑ": 1,"Ȓ": 1,"Ȕ": 1,"Ȗ": 1,"Ḁ": 1,"Ḃ": 1,"Ḅ": 1,"Ḇ": 1,"Ḉ": 1,"Ḋ": 1,"Ḍ": 1,"Ḏ": 1,"Ḑ": 1,"Ḓ": 1,"Ḕ": 1,"Ḗ": 1,"Ḙ": 1,"Ḛ": 1,"Ḝ": 1,"Ḟ": 1,"Ḡ": 1,"Ḣ": 1,"Ḥ": 1,"Ḧ": 1,"Ḩ": 1,"Ḫ": 1,"Ḭ": 1,"Ḯ": 1,"Ḱ": 1,"Ḳ": 1,"Ḵ": 1,"Ḷ": 1,"Ḹ": 1,"Ḻ": 1,"Ḽ": 1,"Ḿ": 1,"Ṁ": 1,"Ṃ": 1,"Ṅ": 1,"Ṇ": 1,"Ṉ": 1,"Ṋ": 1,"Ṍ": 1,"Ṏ": 1,"Ṑ": 1,"Ṓ": 1,"Ṕ": 1,"Ṗ": 1,"Ṙ": 1,"Ṛ": 1,"Ṝ": 1,"Ṟ": 1,"Ṡ": 1,"Ṣ": 1,"Ṥ": 1,"Ṧ": 1,"Ṩ": 1,"Ṫ": 1,"Ṭ": 1,"Ṯ": 1,"Ṱ": 1,"Ṳ": 1,"Ṵ": 1,"Ṷ": 1,"Ṹ": 1,"Ṻ": 1,"Ṽ": 1,"Ṿ": 1,"Ẁ": 1,"Ẃ": 1,"Ẅ": 1,"Ẇ": 1,"Ẉ": 1,"Ẋ": 1,"Ẍ": 1,"Ẏ": 1,"Ẑ": 1,"Ẓ": 1,"Ẕ": 1,"Ạ": 1,"Ả": 1,"Ấ": 1,"Ầ": 1,"Ẩ": 1,"Ẫ": 1,"Ậ": 1,"Ắ": 1,"Ằ": 1,"Ẳ": 1,"Ẵ": 1,"Ặ": 1,"Ẹ": 1,"Ẻ": 1,"Ẽ": 1,"Ế": 1,"Ề": 1,"Ể": 1,"Ễ": 1,"Ệ": 1,"Ỉ": 1,"Ị": 1,"Ọ": 1,"Ỏ": 1,"Ố": 1,"Ồ": 1,"Ổ": 1,"Ỗ": 1,"Ộ": 1,"Ớ": 1,"Ờ": 1,"Ở": 1,"Ỡ": 1,"Ợ": 1,"Ụ": 1,"Ủ": 1,"Ứ": 1,"Ừ": 1,"Ự": 1,"Ỳ": 1,"Ỵ": 1,"Ỷ": 1,"Ỹ": 1,"Ữ": 1, "$": 0, "#": 0, "%": 0, "^":0, "(": 0, ")":0, "_":0, "=":0, "+":0, "@":0, "~":0, ",":0, '"':0, "|":0, '³':0, 'ʼ': 0, '℞': 0, "Σ": 2 }

    letter_score = 0
    for x in str(word).upper():
        if x in letter_values:
            letter_score = letter_score + letter_values[x]
        else:
            pass
    return letter_score
	
async def initialize_dm(author_id):
    global dm_tracker
    dm_tracker[author_id] = { }
    dm_tracker[author_id]["currentcommand"] = " "
    dm_tracker[author_id]["currentfield"] = 0
    dm_tracker[author_id]["fieldlist"] = []
    dm_tracker[author_id]["fielddict"] = []
    dm_tracker[author_id]["server_id"] = 0
    dm_tracker[author_id]["commandchannel"] = 0
    dm_tracker[author_id]["parameters"] = " "

def role_check(role_required, user):
    for role in user.roles:
        if role.id == role_required:
            return True

 


    
    manager.add_global_command(command)
    
@client.event
async def on_ready():
    global hangman_game_state
    global used_hint
    global trivia_game_state
    global crystal_game_state
    global riddle_state
    global word_game_state
    global prefix
    global manager
    global slash_commands
    slash_commands = SlashCommands(client)
    await log_message("Logged into Discord!")

    

        
    commands = [{"name": 'help', 'desc': 'Bot help.', 'options': [{'name': 'category', 'desc': 'Category of help'},]},
    {"name": 'info', 'desc': 'Bot help.', 'options': [{'name': 'category', 'desc': 'Category of help'},]},]
    for command in commands:
        slash_commands.new_slash_command(name=command["name"].lower(), description=command["desc"])
        for option in command["options"]:
            try:
                option["name"]
            except:
                continue
            print(str(option))
            slash_commands.add_command_option(command_name=command["name"].lower(), option_name=option["name"].lower(), description=option["desc"], required=True)
        slash_commands.add_global_slash_command(command_name=command["name"].lower())
        await asyncio.sleep(4)
    # {"name": 'writingprompt', 'desc': 'Load a writing prompt.', 'options': [{}]},
    # {"name": 'riddlethis', 'desc': 'Get a riddle to solve.', 'options': [{}]},
    # {"name": 'riddlethat', 'desc': 'Answer the riddle given.', 'options': [{'name': 'answer', 'desc': 'Answer to the riddle.'}]},
    # {"name": 'hangman', 'desc': 'Start a hangman game.', 'options': [{'name': 'difficulty', 'desc': 'Difficulty (easy, medium, hard'}]},
    # {"name": 'solve', 'desc': 'Solve the hangman puzzle.', 'options': [{'name': 'word', 'desc': 'Your word to solve.'}]},
    # {"name": 'guess', 'desc': 'A letter to guess in the word.', 'options': [{'name': 'letter', 'desc': 'Letter you are guessing.'}]},
    # {"name": 'guessedletters', 'desc': 'Show the letters guessed so far.', 'options': [{}]},
    # {"name": 'hint', 'desc': 'Get a hint DMed to you.', 'options': [{}]},
    # {"name": 'invite', 'desc': 'Show the bot invite link.', 'options': [{}]},
    # {"name": 'challenge', 'desc': 'Challenge someone to a game.', 'options': [{'name': 'user', 'desc': 'User to challenge.'}]},
    # {"name": 'screwball', 'desc': 'Ask the magic screwball a question.', 'options': [{'name': 'question', 'desc': 'Your magic eight ball question.'}]},
    # {"name": 'mystats', 'desc': 'Show your game statistics.', 'options': [{}]},
    # {"name": 'endlesstrivia', 'desc': 'Start a neverending trivia round.', 'options': [{'name': 'difficulty', 'desc': 'Difficulty of questions (easy, medium, hard).'}, {'name': 'category', 'desc': 'Question category/topic.'}]},
    # {"name": 'trivia', 'desc': 'Ask a trivia question.', 'options': [{'name': 'difficulty', 'desc': 'Difficulty of questions (easy, medium, hard).'}, {'name': 'category', 'desc': 'Question category/topic.'}]},
    # {"name": 'namethatcrystal', 'desc': 'Start a crystal guessing game.', 'options': [{}]},
    # {"name": 'answer', 'desc': 'Answer a trivia question.', 'options': [{'name': 'answer', 'desc': 'Your trivia answer.'}]},
    # {"name": 'endendless', 'desc': 'End the endless trivia round.', 'options': [{}]},
    # {"name": 'whatshiny', 'desc': 'Give up and see what crystal was shown.', 'options': [{}]},
    # {"name": 'riddlewhat', 'desc': 'Give up and see the riddle answer.', 'options': [{}]},
    # {"name": 'pardon', 'desc': 'End the hangman round.', 'options': [{}]},
    # {"name": 'idunno', 'desc': 'Give up on the current trivia question', 'options': [{}]},
    # {"name": 'myscore', 'desc': 'Show your trivia score', 'options': [{}]},
    # {"name": 'categories', 'desc': 'List the trivia categories/topics.', 'options': [{}]},
    # {"name": 'leaderboard', 'desc': 'Show the server leaderboard', 'options': [{}]},
    # {"name": 'wordgame', 'desc': 'Start a word game.', 'options': [{}]},
    # {"name": 'join', 'desc': 'Join a word game that hasn\'t started.', 'options': [{}]},
    # {"name": 'startwordgame', 'desc': 'Start a word game with all joined players.', 'options': [{}]},
    # {"name": 'play', 'desc': 'Play a word in the word game.', 'options': [{'name': 'word', 'desc': 'Your word to play.'}]},
    # {"name": 'abortwordgame', 'desc': 'End the current word game.', 'options': [{}]},
    # {"name": 'mywordstats', 'desc': 'Show your word game statistics.', 'options': [{}]},
    # {"name": 'wordpass', 'desc': 'pass on your turn in the word game.', 'options': [{}]}
    #]
 
    # for guild in client.guilds:
        # used_hint[guild.id] = False
        # hangman_game_state[guild.id] = {} 
        # hangman_game_state[guild.id]["Word"] = ""
        # hangman_game_state[guild.id]["Defs"] = ""
        # hangman_game_state[guild.id]["Event"] = False
        # hangman_game_state[guild.id]["Pattern"] = ""
        # hangman_game_state[guild.id]["Hangman"] = ""
        # hangman_game_state[guild.id]["BadGuesses"] = 0
        
        # riddle_state[guild.id] = {}
        # riddle_state[guild.id]["Question"] = ""
        # riddle_state[guild.id]["Answer"] = ""
        # riddle_state[guild.id]["Event"] = False
        
        # trivia_game_state[guild.id] = {} 
        # trivia_game_state[guild.id]["Question"] = ""
        # trivia_game_state[guild.id]["Answer"] = ""
        # trivia_game_state[guild.id]["Difficulty"] = ""
        # trivia_game_state[guild.id]["Event"] = False
        # trivia_game_state[guild.id]["Endless"] = False
        # trivia_game_state[guild.id]["GivenDifficulty"] = ""
        # trivia_game_state[guild.id]["GivenCategory"] = ""
        
        # guessed_letters[guild.id] = []
        
        # crystal_game_state[guild.id] = {}
        # crystal_game_state[guild.id]["Event"] = False
        # crystal_game_state[guild.id]["Crystal"] = ""
        # crystal_game_state[guild.id]["ChallengeUser"] = ""
        
        # word_game_state[guild.id] = {}
        # word_game_state[guild.id]["Event"] = False
        # word_game_state[guild.id]["CurrentTurn"] = 0
        # word_game_state[guild.id]["AI"] = False
        # word_game_state[guild.id]["Players"] = []
        # word_game_state[guild.id]["Scores"] = []
        # word_game_state[guild.id]["Letters"] = {}
        # word_game_state[guild.id]["MaxRounds"] = 0
        # word_game_state[guild.id]["CurrentRound"] = 0
        
        
@client.event
async def on_guild_join(guild):
    global hangman_game_state
    global used_hint
    global trivia_game_state
    global crystal_game_state
    global ridddle_state
    global word_game_state
    global prefix
    
    
    await log_message("Joined guild " + guild.name)
    used_hint[guild.id] = False
    hangman_game_state[guild.id] = {} 
    hangman_game_state[guild.id]["Word"] = ""
    hangman_game_state[guild.id]["Defs"] = ""
    hangman_game_state[guild.id]["Event"] = False
    hangman_game_state[guild.id]["Pattern"] = ""
    hangman_game_state[guild.id]["Hangman"] = ""
    hangman_game_state[guild.id]["BadGuesses"] = 0
    
    trivia_game_state[guild.id] = {} 
    trivia_game_state[guild.id]["Question"] = ""
    trivia_game_state[guild.id]["Answer"] = ""
    trivia_game_state[guild.id]["Difficulty"] = ""
    trivia_game_state[guild.id]["Event"] = False
    trivia_game_state[guild.id]["Endless"] = False
    trivia_game_state[guild.id]["GivenDifficulty"] = ""
    trivia_game_state[guild.id]["GivenCategory"] = ""    
    
    riddle_state[guild.id] = {}
    riddle_state[guild.id]["Question"] = ""
    riddle_state[guild.id]["Answer"] = ""
    riddle_state[guild.id]["Event"] = False
    
    crystal_game_state[guild.id] = {}
    crystal_game_state[guild.id]["Event"] = False
    crystal_game_state[guild.id]["Crystal"] = ""
    crystal_game_state[guild.id]["ChallengeUser"] = ""
    
    guessed_letters[guild.id] = []
    for user in guild.members:
        records = await select_sql("""SELECT LettersRight, LettersWrong, ChallengesWon, ChallengesLost, HintsUsed, WordsSolved FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(guild.id),str(user.id)))
        if not records:
            result = await commit_sql("""INSERT INTO Scoreboard (ServerId,UserId,LettersRight, LettersWrong, ChallengesWon, ChallengesLost, HintsUsed, WordsSolved) VALUES (%s, %s, 0,0,0,0,0,0);""",(str(guild.id),str(user.id)))
    for member in guild.members:
        try:
            connection = mysql.connector.connect(host='localhost', database='Tricksy', user='REDACTED', password='REDACTED')    
            create_score_entry = """INSERT INTO QuizScores (ServerId, UserId, Score) VALUES(%s, %s, %s);"""   
            score_entry = (str(guild.id), str(member.id), str(0))
            cursor = connection.cursor()
            result = cursor.execute(create_score_entry, score_entry)
            connection.commit()
        except mysql.connector.Error as error:
            await message.channel.send("Database error! " + str(error))   
        finally:
            if(connection.is_connected()):
                cursor.close()
                connection.close()
    word_game_state[guild.id] = {}
    word_game_state[guild.id]["Event"] = False
    word_game_state[guild.id]["CurrentTurn"] = 0
    word_game_state[guild.id]["AI"] = False
    word_game_state[guild.id]["Players"] = []
    word_game_state[guild.id]["Scores"] = []
    word_game_state[guild.id]["Letters"] = []
    word_game_state[guild.id]["MaxRounds"] = 0
    word_game_state[guild.id]["CurrentRound"] = 0     
    prefix[guild.id] = '?'
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)
    
@client.event
async def on_member_join(member):
    await log_message("Member " + member.name + " joined guild " + member.guild.name)
    result = await commit_sql("""INSERT INTO Scoreboard (ServerId,UserId,LettersRight, LettersWrong, ChallengesWon, ChallengesLost, HintsUsed, WordsSolved) VALUES (%s, %s, 0,0,0,0,0,0);""",(str(member.guild.id),str(member.id)));
    records = await select_sql("""SELECT LettersRight, LettersWrong, ChallengesWon, ChallengesLost, HintsUsed, WordsSolved FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(member.guild.id),str(member.id)))
    if not records:
        result = await commit_sql("""INSERT INTO Scoreboard (ServerId,UserId,LettersRight, LettersWrong, ChallengesWon, ChallengesLost, HintsUsed, WordsSolved) VALUES (%s, %s, 0,0,0,0,0,0);""",(str(member.guild.id),str(member.id)))     
    create_score_entry = """INSERT INTO QuizScores (ServerId, UserId, Score) VALUES(%s, %s, %s);"""   
    score_entry = (str(member.guild.id), str(member.id), str(0))
    result = await commit_sql(create_score_entry, score_entry)    
@client.event
async def on_member_remove(member):
    # await log_message("Member " + member.name + " left guild " + member.guild.name)
    create_score_entry = """DELETE FROM QuizScores Where UserId=%s AND ServerId=%s;"""   
    score_entry = (str(member.id),str(member.guild.id))
    result = await commit_sql(create_score_entry, score_entry)
    # await log_message("Deleted quiz score entry for user.")  
    
    
@client.event
async def on_message(message):
    global hangman_game_state
    global hangman_initial
    global bad_guess
    global used_hint
    global screwball_answers
    global guessed_letters
    global trivia_game_state
    global riddle_state
    global word_game_state
    global prefix
    
    allowed_users = [610335542780887050]
  
    if message.author == client.user:
        return
    if message.author.bot and message.author.id != 787355055333965844:
        return

    if message.content.startswith('?'):
        try:     used_hint[message.guild.id] 
        except: used_hint[message.guild.id] = False
        try:     hangman_game_state[message.guild.id] 
        except: hangman_game_state[message.guild.id] = {} 
        try:     hangman_game_state[message.guild.id]["Word"] 
        except: hangman_game_state[message.guild.id]["Word"] = ""
        try:     hangman_game_state[message.guild.id]["Defs"] 
        except: hangman_game_state[message.guild.id]["Defs"] = ""
        try:     hangman_game_state[message.guild.id]["Event"] 
        except: hangman_game_state[message.guild.id]["Event"] = False
        try:     hangman_game_state[message.guild.id]["Pattern"] 
        except: hangman_game_state[message.guild.id]["Pattern"] = ""
        try:     hangman_game_state[message.guild.id]["Hangman"] 
        except: hangman_game_state[message.guild.id]["Hangman"] = ""
        try:     hangman_game_state[message.guild.id]["BadGuesses"] 
        except: hangman_game_state[message.guild.id]["BadGuesses"] = 0
        try:     riddle_state[message.guild.id] 
        except:  riddle_state[message.guild.id] = {}
        try:     riddle_state[message.guild.id]["Question"] 
        except: riddle_state[message.guild.id]["Question"] = ""
        try:     riddle_state[message.guild.id]["Answer"] 
        except: riddle_state[message.guild.id]["Answer"] = ""
        try:     riddle_state[message.guild.id]["Event"] 
        except: riddle_state[message.guild.id]["Event"] = False
        try:     trivia_game_state[message.guild.id] 
        except: trivia_game_state[message.guild.id] = {} 
        try:     trivia_game_state[message.guild.id]["Question"] 
        except: trivia_game_state[message.guild.id]["Question"] = ""
        try:     trivia_game_state[message.guild.id]["Answer"] 
        except: trivia_game_state[message.guild.id]["Answer"] = ""
        try:     trivia_game_state[message.guild.id]["Difficulty"] 
        except: trivia_game_state[message.guild.id]["Difficulty"] = ""
        try:     trivia_game_state[message.guild.id]["Event"] 
        except: trivia_game_state[message.guild.id]["Event"] = False
        try:     trivia_game_state[message.guild.id]["Endless"] 
        except: trivia_game_state[message.guild.id]["Endless"] = False
        try:     trivia_game_state[message.guild.id]["GivenDifficulty"] 
        except: trivia_game_state[message.guild.id]["GivenDifficulty"] = ""
        try:     trivia_game_state[message.guild.id]["GivenCategory"] 
        except: trivia_game_state[message.guild.id]["GivenCategory"] = ""

        try:     guessed_letters[message.guild.id] 
        except: guessed_letters[message.guild.id] = []

        try:     crystal_game_state[message.guild.id] 
        except: crystal_game_state[message.guild.id] = {}
        try:     crystal_game_state[message.guild.id]["Event"] 
        except: crystal_game_state[message.guild.id]["Event"] = False
        try:     crystal_game_state[message.guild.id]["Crystal"] 
        except:  crystal_game_state[message.guild.id]["Crystal"] = ""
        try:     crystal_game_state[message.guild.id]["ChallengeUser"] 
        except: crystal_game_state[message.guild.id]["ChallengeUser"] = ""

        try:     word_game_state[message.guild.id] 
        except: word_game_state[message.guild.id] = {}
        try:     word_game_state[message.guild.id]["Event"] 
        except: word_game_state[message.guild.id]["Event"] = False
        try:     word_game_state[message.guild.id]["CurrentTurn"] 
        except: word_game_state[message.guild.id]["CurrentTurn"] = 0
        try:     word_game_state[message.guild.id]["AI"] 
        except: word_game_state[message.guild.id]["AI"] = False
        try:     word_game_state[message.guild.id]["Players"] 
        except:  word_game_state[message.guild.id]["Players"] = []
        try:     word_game_state[message.guild.id]["Scores"] 
        except: word_game_state[message.guild.id]["Scores"] = []
        try:     word_game_state[message.guild.id]["Letters"] 
        except: word_game_state[message.guild.id]["Letters"] = {}
        try:     word_game_state[message.guild.id]["MaxRounds"] 
        except: word_game_state[message.guild.id]["MaxRounds"] = 0
        try:     word_game_state[message.guild.id]["CurrentRound"] 
        except: word_game_state[message.guild.id]["CurrentRound"] = 0

        command_string = message.content.split(' ')
        command = command_string[0].replace('?','')
        parsed_string = message.content.replace('?' + command,"")
        parsed_string = re.sub(r"^ ","",parsed_string)
        username = message.author.name
        server_name = message.guild.name
        if re.search(command, parsed_string):
            parsed_string = ""
        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        
        if command == 'help' or command == 'info':
            if not parsed_string:
                response = "**Got Game/ Help**\n\nGot Game/ is a fun game bot for Discord. Type one of the following to see commands for each type of game:\n\n`/info hangman`: Commands for hangman games.\n`/info crystal`: Commands for Name That Crystal! (a crystal ID game)\n`/info riddles`: Commands for Riddle Me This! (a riddle game)\n`/info trivia`: Commands for trivia game.\n`/info wordgame`: Commands for Word Game (a Scrabble-like word game)\n`/info screwball`: Commands for Screwball Eightball (a smart-aleck NSFW eightball).\n\n`/invite`: Create bot invite link.\n"
            elif parsed_string == 'hangman':
                response = "**Hangman Commands**\n\n`/hangman`: Start a hangman game of any difficulty.\n`/hangman easy|medium|hard|nightmare`: Start a hangman game of the specified difficulty, based on the length of the word or phrase.\n`/guess X`: Guess a letter, where X is any letter.\n`/guessedletters`: See the letters guessed so far.\n`/hint`: Have the bot DM you one letter in the word. Can only be used once per puzzle.\n`/solve WORD` Solve the word. A bad solve counts as one bad guess, but a correct solve counts as a correct solve in your stats.\n`/pardon`: Give up on the current hangman puzzle and end the game.\n`/challenge difficulty @user`: Challenge a single user (including yourself) to a hangman game, and no one else can guess.\n`/mystats`: View your server stats for hangman.\n"
            elif parsed_string == 'screwball':
                response = "**Screwball Commands**\n\n`/screwball question`: Ask the screwball eightball a yes or no question. Only works in NSFW channels, otherwise silently fails.\n"
            elif parsed_string == 'trivia':
                response = "**Trivia Commands**\n\nInfo: The trivia database contains 51,000 trivia questions. The answers must be an exact match, so use the hints liberally and feel free to pass if you're not sure. The first person to answer correctly gets the points, so it is based on speed and accuracy. If a difficulty is specified, the harder questions are worth more, but you can lose points for incorrect answers, and you can go negative!\n\n`/trivia`: Ask a single trivia question of any difficulty and category.\n`/trivia easy|medium|hard` Ask a single trivia question of the specified difficulty of any category.\n`/trivia category`: Ask a single trivia question of any difficulty of the specified category.\n`/trivia difficulty category`: Ask a single trivia question of the specified difficulty and category.\n`/endlesstrivia difficulty category`: Begin a round of trivia questions of either any or the specified difficulty or category. Both are optional.\n`/categories`: List the available categories of questions.\n`/answer my answer`: Answer a trivia question.\n`/hint`: Get a DM from the bot with the first letter of every word in the answer and a hyphen for every remaining letter in the answer.\n`/idunno`: Pass on the question and see the answer.\n`/endendless`: End a trivia round.\n`/leaderboard`: See the server rankings for trivia.\n"
            elif parsed_string == 'crystal':
                response = "**Name that Crystal! Commands**\n\nInfo: Name that Crystal (Shinies)! is a game to identify crystals!\n\n`/namethatcrystal` or `/shiny`: Generate a picture to see a crystal to ID.\n`/crystal name`: Guess the crystal where name is your guess.\n`/whatshiny`: Give up and show the answer to the crystal ID question.\n"
            elif parsed_string == 'riddles':
                response = "**Riddle me This! Commands**\n\nInfo: Riddle me This! is a game to answer riddles\n\n`/riddlethis`: Ask a riddle to answer.\n`/riddlethat answer`: Answer the riddle.\n`/riddlewhat` Give up on the riddle."
            elif parsed_string == 'wordgame':
                response = "*Word Game Commands**\n\nInfo: This is a Scrabble-like word game for Discord that DMs you a letter tray. DMs must be enabled.\n\n`/wordgame X`: Start a word game with X number of rounds. If X isn't specified, five rounds are used.\n`/joinwordgame`: Join a word game.\n`/startwordgame`: Start the word game.\n`/play WORD`: Play the word, the letters must be in your word tray.\n`/wordpass`: Pass on your turn.\n`/trade XYZ`: Trade the specified letters from your tray for new letters.\n`/abortwordgame` : End the current word game.\n"
            await reply_message(message, response)
        elif command == 'serverlist':
            if message.author.id != 610335542780887050:
                return
            response = "Server list:\n\n"
            for guild in client.guilds:
                response = response + guild.name + "\n"
            response = response + "Server count: " +str(len(client.guilds))
            await reply_message(message, response)
            
        elif command == 'importriddles':
            await reply_message(message, "Loading riddles..")
            with open('/home/REDACTED/riddles.csv', newline='\n') as csvfile:
                equipreader = csv.reader(csvfile, delimiter=',')
                for row in equipreader:
                    result = await commit_sql("INSERT INTO Riddles (Question,Answer) VALUES (%s, %s);", (row[0], row[1]))
            await reply_message(message, "Done!")
        elif command == 'prefix':
            if not parsed_string:
                await reply_message(message, "You didn't specify a new prefix!")
                return
            prefix[message.guild.id] = parsed_string
            records = await select_sql("""SELECT Prefix FROM ServerSettings WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                result = await commit_sql("""INSERT INTO ServerSettings (ServerId,Prefix) VALUES (%s, %s);""",(str(message.guild.id),parsed_string))
            else:
                result = await commit_sql("""UPDATE ServerSettings SET Prefix=%s WHERE ServerId=%s;""",(parsed_string,str(message.guild.id)))
            await reply_message(message, "Prefix set to " + parsed_string)

        elif command == 'importtrivia':
            await reply_message(message, "Loading trivia..")
            with open('/home/REDACTED/easy1.csv', newline='\n') as csvfile:
                equipreader = csv.reader(csvfile, delimiter='|')
                for row in equipreader:
                    result = await commit_sql("INSERT INTO TriviaQuestions (Question,Answer,Difficulty) VALUES (%s, %s, %s);", (row[0], row[1], row[2]))
            with open('/home/REDACTED/easy2.csv', newline='\n') as csvfile:
                equipreader = csv.reader(csvfile, delimiter='|')
                for row in equipreader:
                    result = await commit_sql("INSERT INTO TriviaQuestions (Question,Answer,Difficulty) VALUES (%s, %s, %s);", (row[0], row[1], row[2]))         
            with open('/home/REDACTED/hard1.csv', newline='\n') as csvfile:
                equipreader = csv.reader(csvfile, delimiter='|')
                for row in equipreader:
                    result = await commit_sql("INSERT INTO TriviaQuestions (Question,Answer,Difficulty) VALUES (%s, %s, %s);", (row[0], row[1], row[2]))
            with open('/home/REDACTED/nodifficulty.csv', newline='\n') as csvfile:
                equipreader = csv.reader(csvfile, delimiter='|')
                for row in equipreader:
                    result = await commit_sql("INSERT INTO TriviaQuestions (Category,Question,Answer,Difficulty) VALUES (%s, %s, %s, %s);", (row[0], row[1], row[2],row[3])) 
            with open('/home/REDACTED/medium.csv', newline='\n') as csvfile:
                equipreader = csv.reader(csvfile, delimiter='|')
                for row in equipreader:
                    result = await commit_sql("INSERT INTO TriviaQuestions (Question,Answer,Difficulty) VALUES (%s, %s, %s);", (row[0], row[1], row[2]))
            records = await select_sql("""SELECT COUNT(Question) FROM TriviaQuestions;""")
            await reply_message(message, str(records) + " loaded into database.")
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await reply_message(message,"Admin command only!")
                return   
            await reply_message(message, "Server count: " + str(len(client.guilds)))              
        elif command == 'riddlethis':
            records = await select_sql("""SELECT Question,Answer FROM Riddles ORDER BY RAND ( ) LIMIT 1;""")
            for row in records:
                riddle_state[message.guild.id]["Question"] = row[0]
                riddle_state[message.guild.id]["Answer"] = re.sub(r",$","",re.sub(r",,","",row[1]))
            riddle_state[message.guild.id]["Event"] = True
            await reply_message(message, "Riddle me this:\n\n" + riddle_state[message.guild.id]["Question"])
        elif command == 'riddlethat':
            if not riddle_state[message.guild.id]["Event"]:
                await reply_message(message, "No one asked you anything!")
                return
            if not parsed_string:
                await reply_message(message, "At least try to answer next time!")
                return
            answers = riddle_state[message.guild.id]["Answer"].split(',')
            for answer in answers:
                if re.search(answer, parsed_string, re.IGNORECASE):
                    await reply_message(message, "Haha, you got it right, " + message.author.display_name + "!")
                    return
            await reply_message(message, "Close, but no cigar!")
        elif command == 'serverlist':
            if message.author.id not in allowed_users:
                return
            response = "Server count: " + str(len(client.guilds)) + "\n"
            for server in client.guilds:
                response = response + server.name + "\n"
            await reply_message(message, response)
        elif command == 'hangman':
            records = await get_word(parsed_string)
            for row in records:
                hangman_word = str(row[0])
            hangman_word = re.sub(r"[^A-Za-z]","", hangman_word)    
            parsed_hangman_word = ""
            for x in hangman_word:
                parsed_hangman_word = parsed_hangman_word + x.upper() + " "
              
            hangman_game_state[message.guild.id]["Word"] = parsed_hangman_word
            hangman_game_state[message.guild.id]["Event"] = True
            if not re.search(r"easy|medium|hard|nightmare",parsed_string):
                parsed_string = "any"
            word_state = ""
            await reply_message(message, "New hangman game started by " + message.author.display_name + " on difficulty mode " + parsed_string + "!")
            for x in range(0,len(hangman_word)):
                word_state = word_state + "_ "
            hangman_game_state[message.guild.id]["Pattern"] = word_state
            hangman_game_state[message.guild.id]["Hangman"] = hangman_initial
            response = "```" + hangman_initial + "\n\n" + word_state + "```"
            await reply_message(message, response)
        elif command == 'solve':
            if parsed_string.upper() == hangman_game_state[message.guild.id]["Word"].replace(" ",""):
                await reply_message(message, "You successfully guessed the word!")
                records = await select_sql("""SELECT WordsSolved FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""", (str(message.guild.id),str(message.author.id)))
                for row in records:
                    words_solved = int(row[0])
                words_solved = words_solved + 1
                result = await commit_sql("""UPDATE Scoreboard SET WordsSolved=%s WHERE ServerId=%s AND UserId=%s;""",(str(words_solved), str(message.guild.id),str(message.author.id)))
                hangman_game_state[message.guild.id]["Event"] = False
                hangman_game_state[message.guild.id]["BadGuesses"] = 0
                hangman_game_state[message.guild.id]["Word"] = ""
                hangman_game_state[message.guild.id]["Pattern"] = 0
                
                guessed_letters[message.guild.id] = []
                del hangman_game_state[message.guild.id]["ChallengeUser"]
                used_hint[message.guild.id] = False                
            else:
                await reply_message(message, "Nope! Guess again, Hemingway!")
                hangman_game_state[message.guild.id]["BadGuesses"] = hangman_game_state[message.guild.id]["BadGuesses"] + 1
                hangman_game_state[message.guild.id]["Hangman"] = bad_guess[hangman_game_state[message.guild.id]["BadGuesses"]]
                response = "```" + hangman_game_state[message.guild.id]["Hangman"] + "\n\n" + hangman_game_state[message.guild.id]["Pattern"] + "```"
                await reply_message(message, response)
                if hangman_game_state[message.guild.id]["BadGuesses"] > 6:
                    await reply_message(message, "Too many bad guesses! The word was " + hangman_game_state[message.guild.id]["Word"] + "!")
                    hangman_game_state[message.guild.id]["Event"] = False
                    hangman_game_state[message.guild.id]["BadGuesses"] = 0
                    hangman_game_state[message.guild.id]["Word"] = ""
                    hangman_game_state[message.guild.id]["Pattern"] = 0
                    guessed_letters[message.guild.id] = []
                    del hangman_game_state[message.guild.id]["ChallengeUser"]
                    used_hint[message.guild.id] = False                
        elif command == 'guess':
            if not parsed_string:
                await reply_message(message, "Try guessing a letter!")
                return
            try:
                hangman_game_state[message.guild.id]["ChallengeUser"]
                if hangman_game_state[message.guild.id]["ChallengeUser"] != message.author:
                    await reply_message(message, "You weren't challenged! Take a hike!")
                    return
            except:
                pass
            if not hangman_game_state[message.guild.id]["Event"]:
                await reply_message(message, "No game is running!")
                return
            if parsed_string.upper() in guessed_letters[message.guild.id]:
                await reply_message(message, "That letter has already been guessed!")
                return
            guessed_letters[message.guild.id].append(parsed_string.upper())
            response = "**GUESSED LETTERS**\n\n`"
            for x in guessed_letters[message.guild.id]:
                response = response + x + " "
            response = response + "`"
            await reply_message(message, response)            
            if parsed_string.upper() in hangman_game_state[message.guild.id]["Word"]:
                counter = 0
                new_pattern = ""
                for x in hangman_game_state[message.guild.id]["Word"].strip():
                
                    if x == parsed_string.upper():
                        new_pattern = new_pattern + x
                    elif hangman_game_state[message.guild.id]["Pattern"][counter] == '_':
                        new_pattern = new_pattern + '_'
                    elif hangman_game_state[message.guild.id]["Pattern"][counter] == ' ':
                        new_pattern = new_pattern + ' '
                    else:
                        new_pattern = new_pattern + hangman_game_state[message.guild.id]["Pattern"][counter]
                    await log_message("Counter = " + str(counter) + "X = " + x)
                    counter = counter + 1
                hangman_game_state[message.guild.id]["Pattern"] = new_pattern
                await reply_message(message, "Yes! The letter " + parsed_string.upper() + " is in the word!")
                response = "```" + hangman_game_state[message.guild.id]["Hangman"] + "\n\n" + new_pattern + "```"
                await reply_message(message, response)
                records = await select_sql("""SELECT LettersRight FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                for row in records:
                    words_solved = int(row[0])
                try: words_solved
                except: words_solved = 0
                words_solved = words_solved + 1
                result = await commit_sql("""UPDATE Scoreboard SET LettersRight=%s WHERE ServerId=%s AND UserId=%s;""",(str(words_solved), str(message.guild.id),str(message.author.id)))                
                if '_' not in new_pattern:
                    await reply_message(message, "The word has been guessed!")
                    hangman_game_state[message.guild.id]["Event"] = False
                    hangman_game_state[message.guild.id]["BadGuesses"] = 0
                    hangman_game_state[message.guild.id]["Word"] = ""
                    hangman_game_state[message.guild.id]["Pattern"] = 0
                    guessed_letters[message.guild.id] = []
                    used_hint[message.guild.id] = False
                    try:
                        hangman_game_state[message.guild.id]["ChallengeUser"]
                        records = await select_sql("""SELECT ChallengesWon FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                        for row in records:
                            words_solved = int(row[0])
                        words_solved = words_solved + 1
                        result = await commit_sql("""UPDATE Scoreboard SET ChallengesWon=%s WHERE ServerId=%s AND UserId=%s;""",(str(words_solved), str(message.guild.id),str(message.author.id)))  
                        del hangman_game_state[message.guild.id]["ChallengeUser"]
                    except:
                        pass
                    used_hint[message.guild.id] = False
                    return
            else:
                await reply_message(message, "WRONG!")
                records = await select_sql("""SELECT LettersWrong FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                for row in records:
                    words_solved = int(row[0])
                try: words_solved
                except: words_solved = 0
                words_solved = words_solved + 1
                result = await commit_sql("""UPDATE Scoreboard SET LettersWrong=%s WHERE ServerId=%s AND UserId=%s;""",(str(words_solved), str(message.guild.id),str(message.author.id)))                
                hangman_game_state[message.guild.id]["BadGuesses"] = hangman_game_state[message.guild.id]["BadGuesses"] + 1
                hangman_game_state[message.guild.id]["Hangman"] = bad_guess[hangman_game_state[message.guild.id]["BadGuesses"]]
                response = "```" + hangman_game_state[message.guild.id]["Hangman"] + "\n\n" + hangman_game_state[message.guild.id]["Pattern"] + "```"
                await reply_message(message, response)
                
                if hangman_game_state[message.guild.id]["BadGuesses"] > 6:
                    await reply_message(message, "Too many bad guesses! The word was " + hangman_game_state[message.guild.id]["Word"] + "!")
                    hangman_game_state[message.guild.id]["Event"] = False
                    hangman_game_state[message.guild.id]["BadGuesses"] = 0
                    hangman_game_state[message.guild.id]["Word"] = ""
                    hangman_game_state[message.guild.id]["Pattern"] = 0
                    guessed_letters[message.guild.id] = []
                    used_hint[message.guild.id] = False
                    try:
                        hangman_game_state[message.guild.id]["ChallengeUser"]
                        records = await select_sql("""SELECT ChallengesWon FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                        for row in records:
                            words_solved = int(row[0])
                        words_solved = words_solved + 1
                        result = await commit_sql("""UPDATE Scoreboard SET ChallengesWon=%s WHERE ServerId=%s AND UserId=%s;""",(str(words_solved), str(message.guild.id),str(message.author.id)))  
                        del hangman_game_state[message.guild.id]["ChallengeUser"]
                    except:
                        pass                    

                    used_hint[message.guild.id] = False
        elif command == 'guessedletters':
            response = "**GUESSED LETTERS**\n\n`"
            for x in guessed_letters[message.guild.id]:
                response = response + x + " "
            response = response + "`"
            await reply_message(message, response)
        elif command == 'hint':
            if hangman_game_state[message.guild.id]["Event"]:
                if used_hint[message.guild.id]:
                    await reply_message(message, "You have already used a hint!")
                    return
                records = await select_sql("""SELECT HintsUsed FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                for row in records:
                    words_solved = int(row[0])
                try: words_solved
                except: words_solved = 0
                
                words_solved = words_solved + 1
                result = await commit_sql("""UPDATE Scoreboard SET HintsUsed=%s WHERE ServerId=%s AND UserId=%s;""",(str(words_solved), str(message.guild.id),str(message.author.id)))                  
                hint = False
                while not hint:
                    try_letter = random.randint(0,len(hangman_game_state[message.guild.id]["Word"]) - 1)
                    hint_letter = hangman_game_state[message.guild.id]["Word"][try_letter]
                    
                    if hangman_game_state[message.guild.id]["Pattern"][try_letter] == '_':
                        hint = True
                await direct_message(message.author, "The letter " + hint_letter + " is somewhere in this word.")
                used_hint[message.guild.id] = True
            elif trivia_game_state[message.guild.id]["Event"]:
                words = trivia_game_state[message.guild.id]["Answer"].split(' ')
                hint = " "
                for word in words:
                    hint = hint + re.sub(r"([A-Za-z0-9]).*",r"\1",word)
                    for x in word[1:]:
                        hint = hint + "-"
                    hint = hint + " "            
                await direct_message(message.author, "**Hint**\n\n" + hint)
            elif crystal_game_state[message.guild.id]["Event"]:
                words = crystal_game_state[message.guild.id]["Crystal"].split(' ')
                hint = " "
                for word in words:
                    hint = hint + re.sub(r"([A-Za-z0-9]{3}).*",r"\1",word)
                    for x in word[3:]:
                        hint = hint + "-"
                    hint = hint + " "
                    try:
                        await message.author.send("**Hint**\n\n" + hint)
                        
                    except discord.errors.Forbidden:
                        await message.channel.send("**Hint**\n\n" + hint)                    
        
            else:
                await reply_message(message, "No game is currently ongoing!")
        elif command == 'invite':
            await reply_message(message, "Click here to invite me: https://discord.com/api/oauth2/authorize?client_id=704079890495832175&permissions=2147600448&scope=bot%20applications.commands")
        elif command == 'challenge':
            if not message.mentions:
                await reply_message(message, "You didn't mention a user to challenge!")
                return
            if hangman_game_state[message.guild.id]["Event"]:
                await reply_message(message, "A game is already in progress!")
                return
            user = message.mentions[0]
            
            records = await get_word(parsed_string)
            for row in records:
                hangman_word = str(row[0])

            hangman_word = re.sub(r"[^A-Za-z]","", hangman_word)    
            parsed_hangman_word = ""
            for x in hangman_word:
                parsed_hangman_word = parsed_hangman_word + x.upper() + " "
            await log_message("parsed word: " + parsed_hangman_word)
              
            hangman_game_state[message.guild.id]["Word"] = parsed_hangman_word
            hangman_game_state[message.guild.id]["Event"] = True
            word_state = ""
            await reply_message(message, "New hangman game started by " + message.author.display_name + " on difficulty mode " + parsed_string + "!\n\n<@" + str(user.id) + "> has been challenged!")
            for x in range(0,len(hangman_word)):
                word_state = word_state + "_ "
            hangman_game_state[message.guild.id]["Pattern"] = word_state
            hangman_game_state[message.guild.id]["Hangman"] = hangman_initial
            hangman_game_state[message.guild.id]["ChallengeUser"] = user
            response = "```" + hangman_initial + "\n\n" + word_state + "```"
            await reply_message(message, response)
        elif command == 'setupscoreboard':
            for user in message.guild.members:
                result = await commit_sql("""INSERT INTO Scoreboard (ServerId,UserId,LettersRight, LettersWrong, ChallengesWon, ChallengesLost, HintsUsed, WordsSolved) VALUES (%s, %s, 0,0,0,0,0,0);""",(str(message.guild.id),str(user.id)))
            await reply_message(message, "Done!")
        elif command == 'screwball':
            await message.channel.send(">>> " + random.choice(screwball_answers))        
        elif command == 'mystats':
            records = await select_sql("""SELECT LettersRight, LettersWrong, ChallengesWon, ChallengesLost, HintsUsed, WordsSolved FROM Scoreboard WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "No records found for you! Creating one...")
                result = await commit_sql("""INSERT INTO Scoreboard (ServerId,UserId,LettersRight, LettersWrong, ChallengesWon, ChallengesLost, HintsUsed, WordsSolved) VALUES (%s, %s, 0,0,0,0,0,0);""",(str(message.guild.id),str(message.author.id)))
                return
            response = "**YOUR STATS**\n\n"
            for row in records:
                letters_right = str(row[0])
                letters_wrong = str(row[1])
                challenges_won = str(row[2])
                challenges_lost = str(row[3])
                hints_used = str(row[4])
                words_solved = str(row[5])
            response = response + "Letters Guessed Correctly: `" + letters_right + "`\nLetters Guessed Incorrectly: `" + letters_wrong + "`\nChallenges Won: `" + challenges_won + "`\nChallenges Lost: `" + challenges_lost + "`\nHints Used: `" + hints_used + "`\nWords solved: `" + words_solved + "`\n"
            await reply_message(message, response)
        elif (command == 'resetscores'):
            set_score_to_zero = """UPDATE QuizScores Set Score=0 WHERE ServerId=%s;"""
            server_id = message.guild.id
            result = await commit_sql(set_score_to_zero, (server_id,))
            if result:
                await reply_message(message, "Leaderboard reset to zero for all members.")
            else:
                await reply_message(message, "Database error!")
        elif command == 'endlesstrivia':
            difficulty_re = re.compile(r"(?P<difficulty>easy|medium|hard|nightmare)", re.IGNORECASE)
            no_diff = False
            m = difficulty_re.search(parsed_string)
            if m:
                difficulty_string = m.group('difficulty').lower()
            category_string = re.sub(difficulty_re,"",parsed_string).strip()
            try: difficulty_string
            except: difficulty_string = None
            if difficulty_string == 'easy':
                difficulty = "Easy"
            elif difficulty_string == 'medium':
                difficulty = "Medium"
            elif difficulty_string == 'hard':
                difficulty = "Hard"
            elif difficulty_string == 'nightmare':
                difficulty = "Nightmare"
            else:
                no_diff = True
                difficulty = random.choice(['Easy','Medium','Hard','Nightmare'])
            trivia_query = """SELECT Question,Answer,Category FROM TriviaQuestions"""
            trivia_tuple = ()
            if difficulty_string and category_string == "":
                trivia_query = trivia_query + """ WHERE Difficulty=%s ORDER BY RAND( ) LIMIT 1;"""
                trivia_tuple = trivia_tuple + (difficulty,)
            elif category_string != "" and not difficulty_string:
                trivia_tuple = trivia_tuple + (category_string,)
                trivia_query = trivia_query + """ WHERE Category=%s ORDER BY RAND( ) LIMIT 1;"""
            elif category_string != "" and difficulty_string:
                trivia_tuple = trivia_tuple + (difficulty, category_string)
                trivia_query = trivia_query + """ WHERE Difficulty=%s AND Category=%s ORDER BY RAND( ) LIMIT 1;"""                
            else:
                trivia_query = trivia_query + """ ORDER BY RAND( ) LIMIT 1;"""
            
                
            records = await select_sql(trivia_query, trivia_tuple)
            
            for row in records:
                question = str(row[0]).replace('\xa0','')
                answer = str(row[1]).replace('\xa0','')
                category = str(row[2]).replace('\xa0','')
            try: category
            except: category = "None"
            if category is None:
                category = "None"
            
            trivia_game_state[message.guild.id]["Question"] = question
            trivia_game_state[message.guild.id]["Answer"] = answer
            trivia_game_state[message.guild.id]["Difficulty"] = difficulty
            trivia_game_state[message.guild.id]["Category"] = category
            trivia_game_state[message.guild.id]["Event"] = True
            trivia_game_state[message.guild.id]["Endless"] = True
            if not no_diff:
                trivia_game_state[message.guild.id]["GivenDifficulty"] = difficulty
            trivia_game_state[message.guild.id]["GivenCategory"] = category_string
            
            response = "An endless trivia round has been started by " + message.author.name + "!\n\n**Category:** " + category + "\n**QUESTION:** " + question + "\n"
            await reply_message(message, response)        
        elif command == 'trivia':
            difficulty_re = re.compile(r"(?P<difficulty>easy|medium|hard|nightmare)", re.IGNORECASE)
            m = difficulty_re.search(parsed_string)
            if m:
                difficulty_string = m.group('difficulty').lower()
            category_string = re.sub(difficulty_re,"",parsed_string).strip()
            try: difficulty_string
            except: difficulty_string = None
            if difficulty_string == 'easy':
                difficulty = "Easy"
            elif difficulty_string == 'medium':
                difficulty = "Medium"
            elif difficulty_string == 'hard':
                difficulty = "Hard"
            elif difficulty_string == 'nightmare':
                difficulty = "Nightmare"
            else:
                difficulty = random.choice(["Easy","Medium","Hard","Nightmare"])
            trivia_query = """SELECT Question,Answer,Category FROM TriviaQuestions"""
            trivia_tuple = ()
            if difficulty_string and category_string == "":
                trivia_query = trivia_query + """ WHERE Difficulty=%s ORDER BY RAND( ) LIMIT 1;"""
                trivia_tuple = trivia_tuple + (difficulty,)
            elif category_string != "" and not difficulty_string:
                trivia_tuple = trivia_tuple + (category_string,)
                trivia_query = trivia_query + """ WHERE Category=%s ORDER BY RAND( ) LIMIT 1;"""
            elif category_string != "" and difficulty_string:
                trivia_tuple = trivia_tuple + (difficulty, category_string)
                trivia_query = trivia_query + """ WHERE Difficulty=%s AND Category=%s ORDER BY RAND( ) LIMIT 1;"""                
            else:
                trivia_query = trivia_query + """ ORDER BY RAND( ) LIMIT 1;"""
            
                
            records = await select_sql(trivia_query, trivia_tuple)
            
            for row in records:
                question = str(row[0]).replace('\xa0','')
                answer = str(row[1]).replace('\xa0','')
                category = str(row[2]).replace('\xa0','')
            try: category
            except: category = "None"
            if category is None:
                category = "None"
            try:
                question
            except:    
                await reply_message(message, "No question found in that category.")
                return
            trivia_game_state[message.guild.id]["Question"] = question
            trivia_game_state[message.guild.id]["Answer"] = answer
            trivia_game_state[message.guild.id]["Difficulty"] = difficulty
            trivia_game_state[message.guild.id]["Category"] = category
            trivia_game_state[message.guild.id]["Event"] = True
            
            response = "A trivia round has been started by " + message.author.name + "!\n\n**Category:** " + category + "\n**QUESTION:** " + question + "\n"
            await reply_message(message, response)
        elif command == 'crystal':
            if not crystal_game_state[message.guild.id]["Event"]:
                await reply_message(message, "No one asked about crystals!")
                return
            if crystal_game_state[message.guild.id]["ChallengeUser"] != "":
                if crystal_game_state[message.guild.id]["ChallengeUser"] != message.author:
                    await reply_message(message, "You weren't named as the one who was challenged!")
                    return
            if parsed_string.lower() == crystal_game_state[message.guild.id]["Crystal"].lower():
                await reply_message(message, "**" + message.author.display_name + "** is correct!")
                crystal_game_state[message.guild.id]["Event"] = False
                crystal_game_state[message.guild.id]["ChallengeUser"]  = ""
            else:
                await reply_message(message, "That's not the right crystal! Try again!")
                
        elif command == 'answer':
            if not trivia_game_state[message.guild.id]["Event"]:
                await reply_message(message, "No one asked a question!")
                return
            id_num = message.author.id
            guild_id = message.guild.id
            get_current_score = """SELECT Score FROM QuizScores WHERE ServerId=%s AND UserId=%s;"""
            records = await select_sql(get_current_score, (str(guild_id), str(id_num)))
            if len(records) == 0:
                await commit_sql("""INSERT INTO QuizScores (ServerId, UserId, QuizScore) VALUES (%s, %s, 0);""",(str(message.guild.id),str(message.author.id)))
                quiz_score = 0
            else:    
                for row in records:
                    quiz_score = int(row[0])
            if parsed_string.upper() == trivia_game_state[message.guild.id]["Answer"].upper():
                await reply_message(message, "Correct! **" + message.author.display_name + "** gets some points!")
                
                if trivia_game_state[message.guild.id]["Difficulty"] == 'Easy':
                    quiz_score = quiz_score + 1
                elif trivia_game_state[message.guild.id]["Difficulty"] == 'Medium':
                    quiz_score = quiz_score + 2
                elif trivia_game_state[message.guild.id]["Difficulty"] == 'Hard':
                    quiz_score = quiz_score + 4
                elif trivia_game_state[message.guild.id]["Difficulty"] == 'Nightmare':
                    quiz_score = quiz_score + 8
                else:
                    quiz_score = quiz_score + 1
                    
                await reply_message(message, "Your new trivia score is **"  + str(quiz_score) + "**.")
  
                update_score_entry = """UPDATE QuizScores Set Score=%s WHERE ServerId=%s AND UserId=%s;"""   
                score_entry = (str(quiz_score), str(guild_id), str(id_num))
                if not trivia_game_state[message.guild.id]["Endless"]:
                    trivia_game_state[message.guild.id]["Question"] = ""
                    trivia_game_state[message.guild.id]["Answer"] = ""
                    trivia_game_state[message.guild.id]["Difficulty"] = ""
                    trivia_game_state[message.guild.id]["Category"] = ""
                    trivia_game_state[message.guild.id]["Event"] = False
                result = await commit_sql(update_score_entry, score_entry)
                if not result:
                    await reply_message(message, "Database error! " + str(error))  
                if trivia_game_state[message.guild.id]["Endless"]:
                    trivia_query = """SELECT Question,Answer,Category,Difficulty FROM TriviaQuestions"""
                    trivia_tuple = ()
                    if trivia_game_state[message.guild.id]["GivenDifficulty"] and trivia_game_state[message.guild.id]["GivenCategory"] == "":
                        trivia_query = trivia_query + """ WHERE Difficulty=%s ORDER BY RAND( ) LIMIT 1;"""
                        trivia_tuple = trivia_tuple + (trivia_game_state[message.guild.id]["GivenDifficulty"],)
                    elif trivia_game_state[message.guild.id]["GivenCategory"] != "" and not trivia_game_state[message.guild.id]["GivenDifficulty"]:
                        trivia_tuple = trivia_tuple + (trivia_game_state[message.guild.id]["GivenCategory"],)
                        trivia_query = trivia_query + """ WHERE Category=%s ORDER BY RAND( ) LIMIT 1;"""
                    elif trivia_game_state[message.guild.id]["GivenCategory"] != "" and trivia_game_state[message.guild.id]["GivenDifficulty"]:
                        trivia_tuple = trivia_tuple + (trivia_game_state[message.guild.id]["GivenDifficulty"], trivia_game_state[message.guild.id]["GivenCategory"])
                        trivia_query = trivia_query + """ WHERE Difficulty=%s AND Category=%s ORDER BY RAND( ) LIMIT 1;"""                
                    else:
                        trivia_query = trivia_query + """ ORDER BY RAND( ) LIMIT 1;"""
                    
                        
                    records = await select_sql(trivia_query, trivia_tuple)
                    
                    for row in records:
                        question = str(row[0]).replace('\xa0','')
                        answer = str(row[1]).replace('\xa0','')
                        category = str(row[2]).replace('\xa0','')
                        difficulty = str(row[3])
                    try: category
                    except: category = "None"
                    if category is None:
                        category = "None"
                    response = "Next question!\n\n**Category:** " + category + "\n**QUESTION:** " + question + "\n"  
                    await reply_message(message, response)
                    trivia_game_state[message.guild.id]["Question"] = question
                    trivia_game_state[message.guild.id]["Answer"] = answer
                    trivia_game_state[message.guild.id]["Difficulty"] = difficulty
                    trivia_game_state[message.guild.id]["Category"] = category 

            
            else:
                await reply_message(message, "Incorrect! Please try again!")
                if trivia_game_state[message.guild.id]["Difficulty"] == 'Easy':
                    quiz_score = quiz_score - 1
                elif trivia_game_state[message.guild.id]["Difficulty"] == 'Medium':
                    quiz_score = quiz_score - 2
                elif trivia_game_state[message.guild.id]["Difficulty"] == 'Hard':
                    quiz_score = quiz_score - 4
                elif trivia_game_state[message.guild.id]["Difficulty"] == 'Nightmare':
                    quiz_score = quiz_score - 8
                else:
                    quiz_score = quiz_score - 1
                    
                await reply_message(message, "Your new trivia score is **"  + str(quiz_score) + "**.")
  
                update_score_entry = """UPDATE QuizScores Set Score=%s WHERE ServerId=%s AND UserId=%s;"""   
                score_entry = (str(quiz_score), str(guild_id), str(id_num))

                result = await commit_sql(update_score_entry, score_entry)
                
        elif command == 'namethatcrystal' or command == 'shiny':
            if message.mentions:
                crystal_game_state[message.guild.id]["ChallengeUser"] = message.mentions[0]
            output = subprocess.run(["/home/REDACTED/BotMaster/crystal/list.sh"], universal_newlines=True, stdout=subprocess.PIPE)
            crystal_list = output.stdout.split('\n')
            crystal = random.choice(crystal_list)
            crystal_name = crystal.replace('-',' ').strip()
            crystal_name = crystal_name.replace('.jpg','').replace("'",'')
            crystal_name = re.sub(r"\(.*\)","",crystal_name).strip()
            copyfile("/home/REDACTED/BotMaster/crystal/" + crystal, "/home/REDACTED/BotMaster/crystal/crystal.jpg")
            await log_message("Picked crystal " + crystal_name)
            await message.channel.send("Name this crystal!",file=discord.File("/home/REDACTED/BotMaster/crystal/crystal.jpg"))
            crystal_game_state[message.guild.id]["Event"] = True
            crystal_game_state[message.guild.id]["Crystal"] = crystal_name
        elif command == 'addcrystal':
            if not message.attachments:
                await reply_message(message, "No picture supplied!")
                return
            if not parsed_string:
                await reply_message(message, "No name supplied!")
                return
            file_url = message.attachments[0].url
            file_name = message.attachments[0].filename
            await reply_message(message, "Downloading file " + file_name + "...")
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
 #           await send_message(message, "File saved to " + file_name + "!")
                    with open('/home/REDACTED/BotMaster/crystal/' + parsed_string, 'wb') as file:
                        bytes = await resp.read()
                        
                        file.write(bytes)
            await reply_message(message, "Crystal added.")            
        elif command == 'showcrystal':
            if not parsed_string:
                await reply_message(message, "You didn't name a crystal!")
                return
            output = subprocess.run(["/home/REDACTED/BotMaster/crystal/list.sh"], universal_newlines=True, stdout=subprocess.PIPE)
            crystal_list = output.stdout.split('\n')
            found_crystal = False
            for crystal in crystal_list:
                if re.search(parsed_string, crystal, re.IGNORECASE):
                    found_crystal = True
                    crystal_file = crystal
            if not found_crystal:
                await reply_message(message, "Sorry, we didn't find that in the picture list.")
                return
            await message.channel.send(file=discord.File("/home/REDACTED/BotMaster/crystal/" + crystal_file))
         
        elif command == 'endendless':
            trivia_game_state[message.guild.id]["Question"] = ""
            trivia_game_state[message.guild.id]["Answer"] = ""
            trivia_game_state[message.guild.id]["Difficulty"] = ""
            trivia_game_state[message.guild.id]["Category"] = ""
            trivia_game_state[message.guild.id]["Event"] = False    
            trivia_game_state[message.guild.id]["Endless"] = False
            await reply_message(message, "The round is over!")
        elif command == 'addriddle':
            question_re = re.compile(r"-question (.+?) -")
            answer_re = re.compile(r"-answer (.+)")
            m = question_re.search(parsed_string)
            if not m:
                await reply_message(message, "No riddle specified!")
                return
            else:
                question = m.group()
            m = answer_re.search(parsed_string)
            if not m:
                await reply_message(message, "No answer specified!")
                return
            else:
                answer = m.group()
            result = await commit_sql("""INSERT INTO Riddles (RiddleId,Question,Answer) VALUES (1,%s,%s);""",(question, answer))
            if result:
                await reply_message(message, "Riddle added!")
            else:
                await reply_message(message, "Database error!")
        elif (command == 'whatshiny'):
            if crystal_game_state[message.guild.id]["Event"]:
                await reply_message(message, message.author.display_name + " is giving up! The answer is " + crystal_game_state[message.guild.id]["Crystal"] + "!")
                return
            else:
                await reply_message(message, "What are you giving up on? Try playing a game first!")
        elif command == 'riddlewhat':        
            if riddle_state[message.guild.id]["Event"]:
                await reply_message(message, message.author.display_name + " is stumped! The answer is " + riddle_state[message.guild.id]["Answer"] + "!")
                riddle_state[message.guild.id]["Event"] = False
                riddle_state[message.guild.id]["Question"] = ""
                riddle_state[message.guild.id]["Answer"] = ""
                return
            else:
                await reply_message(message, "What are you giving up on? Try playing a game first!")
        elif command == 'pardon':        
            if hangman_game_state[message.guild.id]["Event"]:
                await reply_message(message, message.author.display_name + " is giving up! The word was " + hangman_game_state[message.guild.id]["Word"] + "!")
                hangman_game_state[message.guild.id]["Event"] = False
                hangman_game_state[message.guild.id]["BadGuesses"] = 0
                hangman_game_state[message.guild.id]["Word"] = ""
                hangman_game_state[message.guild.id]["Pattern"] = 0
                guessed_letters[message.guild.id] = []
                used_hint[message.guild.id] = False     
                return
            else:
                await reply_message(message, "What are you giving up on? Try playing a game first!")
        elif command == 'idunno':
            if not trivia_game_state[message.guild.id]["Endless"]:
                await reply_message(message, message.author.display_name + " is giving up! The answer is " + trivia_game_state[message.guild.id]["Answer"] + "!")
                trivia_game_state[message.guild.id]["Question"] = ""
                trivia_game_state[message.guild.id]["Answer"] = ""
                trivia_game_state[message.guild.id]["Difficulty"] = ""
                trivia_game_state[message.guild.id]["Category"] = ""
                trivia_game_state[message.guild.id]["Event"] = False
            else:
                trivia_query = """SELECT Question,Answer,Category,Difficulty FROM TriviaQuestions"""
                await reply_message(message, message.author.display_name + " is giving up! The answer is " + trivia_game_state[message.guild.id]["Answer"] + "!")
                trivia_tuple = ()
                if trivia_game_state[message.guild.id]["GivenDifficulty"] and trivia_game_state[message.guild.id]["GivenCategory"] == "":
                    trivia_query = trivia_query + """ WHERE Difficulty=%s ORDER BY RAND( ) LIMIT 1;"""
                    trivia_tuple = trivia_tuple + (trivia_game_state[message.guild.id]["GivenDifficulty"],)
                elif trivia_game_state[message.guild.id]["GivenCategory"] != "" and not trivia_game_state[message.guild.id]["GivenDifficulty"]:
                    trivia_tuple = trivia_tuple + (trivia_game_state[message.guild.id]["GivenCategory"],)
                    trivia_query = trivia_query + """ WHERE Category=%s ORDER BY RAND( ) LIMIT 1;"""
                elif trivia_game_state[message.guild.id]["GivenCategory"] != "" and trivia_game_state[message.guild.id]["GivenDifficulty"]:
                    trivia_tuple = trivia_tuple + (trivia_game_state[message.guild.id]["GivenDifficulty"], trivia_game_state[message.guild.id]["GivenCategory"])
                    trivia_query = trivia_query + """ WHERE Difficulty=%s AND Category=%s ORDER BY RAND( ) LIMIT 1;"""                
                else:
                    trivia_query = trivia_query + """ ORDER BY RAND( ) LIMIT 1;"""
                
                    
                records = await select_sql(trivia_query, trivia_tuple)
                
                for row in records:
                    question = str(row[0]).replace('\xa0','')
                    answer = str(row[1]).replace('\xa0','')
                    category = str(row[2]).replace('\xa0','')
                    difficulty = str(row[3]).replace('\xa0','')
                try: category
                except: category = "None"
                if category is None:
                    category = "None"
                response = "Next question!\n\n**Category:** " + category + "\n**QUESTION:** " + question + "\n" 
                trivia_game_state[message.guild.id]["Question"] = question
                trivia_game_state[message.guild.id]["Answer"] = answer
                trivia_game_state[message.guild.id]["Difficulty"] = difficulty
                trivia_game_state[message.guild.id]["Category"] = category
                await reply_message(message, response)
        elif (command == 'myscore'):
            my_id = message.author.id
            guild_id = message.guild.id
            get_my_score = """SELECT Score FROM QuizScores WHERE ServerId=%s AND UserId=%s;"""
            async with message.channel.typing():
                records = await select_sql(get_my_score, (str(guild_id), str(my_id)))
            if len(records) == 0:
                await reply_message(message, "No score found for the specified user.")
                return
            response = "Your current trivia score is **"
            for row in records:
                score = str(row[0])
            response = response + score + "**."
            await reply_message(message, response)
        elif command == 'categories':
            records = await select_sql("""SELECT DISTINCT Category FROM TriviaQuestions;""")
            response = "**Question Categories**\n\n"
            for row in records:
                if row[0] is not None:
                    response = response + row[0] + "\n"
            await reply_message(message, response)
        elif (command == 'leaderboard'):
            get_leaderboard = """SELECT UserId,Score FROM QuizScores WHERE ServerId=%s ORDER BY Score DESC;"""
            guild_id = message.guild.id
            async with message.channel.typing():
                records = await select_sql(get_leaderboard, (str(guild_id),))

            if len(records) == 0:
                await reply_message(message, "No score found for the specified server.")
                return
            response = "**Trivia Leaderboard:**\n\n"
            for row in records:
                username = get(client.get_all_members(), id=int(row[0]))
                response = response + str(username.name) + " - " + str(row[1]) + "\n"
            await reply_message(message, response)               
        elif (command == 'initializeleaderboard'):
            if not await admin_check(message.author.id):
                await reply_message(message, "Admin command only!")
                return
            result = await execute_sql("""DROP TABLE IF EXISTS QuizScores; CREATE TABLE QuizScores (ServerId VarChar(40), UserId VarChar(30), Score Int);""")
            for guild in client.guilds:
                if guild.id != 264445053596991498:
                    for member in guild.members:
                        records = await select_sql("""SELECT * FROM QuizScores WHERE ServerId=%s AND UserId=%s;""",(str(guild.id),str(member.id)))
                        if not records:
                            create_score_entry = """INSERT INTO QuizScores (ServerId, UserId, Score) VALUES(%s, %s, %s);"""   
                            score_entry = (str(guild.id), str(member.id), str(0))
                            result = await commit_sql(create_score_entry, score_entry)
                            if not result:
                                await reply_message(message, "Database error!")   

            await reply_message(message, "Leaderboard initialized.")

# Word game commands
        elif command == 'wordgame':
            word_game_state[message.guild.id] = {}   
            if parsed_string:
                word_game_state[message.guild.id]["MaxRounds"] = int(parsed_string)
            else:
                word_game_state[message.guild.id]["MaxRounds"] = 5
            
            word_game_state[message.guild.id]["Event"] = True
            word_game_state[message.guild.id]["CurrentTurn"] = 0
            word_game_state[message.guild.id]["AI"] = False
            word_game_state[message.guild.id]["Players"] = []
            word_game_state[message.guild.id]["Scores"] = []
            word_game_state[message.guild.id]["Letters"] = {}
            word_game_state[message.guild.id]["CurrentRound"] = 0            
            await reply_message(message, "Word game started by " + message.author.display_name + "! Type ?join to participate in the word game!")
        elif command == 'join':
            if not word_game_state[message.guild.id]["Event"]:
                await reply_message(message, "No one has started a game! Type ?wordgame to start a new game!")
                return
            word_game_state[message.guild.id]["Players"].append(message.author)
            word_game_state[message.guild.id]["Scores"].append(0)
            word_game_state[message.guild.id]["Letters"][message.author.id] = [] 
            for x in range(0,7):
                letter = await get_letter()
                 
                word_game_state[message.guild.id]["Letters"][message.author.id].append(letter)
            await reply_message(message, message.author.display_name + " has joined the word game!")

        elif command == 'startwordgame':
            if not word_game_state[message.guild.id]["Event"]:
                await reply_message(message, "No game is in progress! Please type ?wordgame to start a new game!")
                return
            counter = 0
            letter_string = " "
            for letter in word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][0].id]:
                letter_string = letter_string + "`" + letter + "` "
            await direct_message(word_game_state[message.guild.id]["Players"][0], "Welcome to the word game. Your letters are:\n\n" + letter_string)
            await reply_message(message, "The game has started! <@" + str(word_game_state[message.guild.id]["Players"][0].id) + "> gets the first turn!")
                
        elif command == 'play':
            if not word_game_state[message.guild.id]["Event"]:
                await reply_message(message, "There's no word game in progress! Please type ?wordgame to start a new game!")
                return
            if message.author != word_game_state[message.guild.id]["Players"][word_game_state[message.guild.id]["CurrentTurn"]]:
                await reply_message(message, "It isn't your turn! Please wait until then to play!")
                return
            word = parsed_string.strip().upper()
            current_turn = word_game_state[message.guild.id]["CurrentTurn"]
            for x in word:
                if x not in word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id]:
                    await reply_message(message, "You played a word with letters you don't have! Please try again!")
                    return
                    
            result = await check_word(word)
            
            if result:
                word_value = await score_word(word)
                word_game_state[message.guild.id]["Scores"][word_game_state[message.guild.id]["CurrentTurn"]] = word_game_state[message.guild.id]["Scores"][word_game_state[message.guild.id]["CurrentTurn"]] + word_value
                await reply_message(message, word + " is a valid word worth " + str(word_value) + " points! Your new score is " + str(word_game_state[message.guild.id]["Scores"][word_game_state[message.guild.id]["CurrentTurn"]]) + "!")
                if len(word) > 6:
                    await reply_message(message, "An additional 50 points is awarded for using all seven letters!")
                    word_game_state[message.guild.id]["Scores"][word_game_state[message.guild.id]["CurrentTurn"]] = word_game_state[message.guild.id]["Scores"][word_game_state[message.guild.id]["CurrentTurn"]] + 50
                counter = 0
                replaced_letters = []
                for x in word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id]:
                    if x in list(word):
                        if x in replaced_letters:
                            continue
                        letter_replacer = word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id].index(x)
                        word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id][letter_replacer] = await get_letter()
                        replaced_letters.append(x)
                        counter = counter + 1
                if word_game_state[message.guild.id]["CurrentTurn"] < len(word_game_state[message.guild.id]["Players"]) - 1:        
                    word_game_state[message.guild.id]["CurrentTurn"] = word_game_state[message.guild.id]["CurrentTurn"] + 1        
                else:
                    word_game_state[message.guild.id]["CurrentTurn"] = 0
                    if word_game_state[message.guild.id]["CurrentRound"] < word_game_state[message.guild.id]["MaxRounds"] - 1:
                    
                        word_game_state[message.guild.id]["CurrentRound"] = word_game_state[message.guild.id]["CurrentRound"] + 1
                        await reply_message(message, "End of round " + str(word_game_state[message.guild.id]["CurrentRound"] - 1) + " and moving to round " + str(word_game_state[message.guild.id]["CurrentRound"]) + "!")
                    else:
                        await reply_message(message, "End of game!")
                        # calculate scores
                        scores = {}
                        for x in range (0, len(word_game_state[message.guild.id]["Players"])):
                            scores[word_game_state[message.guild.id]["Players"][x]] = word_game_state[message.guild.id]["Scores"][x]
                        sorted_scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1])}
                        response = "**FINAL SCORES**\n\n"
                        for player in sorted_scores.keys():
                            response = response + player.display_name + " - "  + str(sorted_scores[player]) + "\n"
                            if sorted_scores[player] == max(list(sorted_scores.values())):
                                winner = player
                        response = response + "\n\n" + player.display_name + " wins the round!"
                        
                        await reply_message(message, response)  
                        for player in sorted_scores.keys():
                            records = await select_sql("""SELECT TotalScore FROM WordGameScores WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(player.id)))
                            if not records:
                                result = await commit_sql("""INSERT INTO WordGameScores (ServerId, UserId, TotalScore, GamesWon) VALUES (%s, %s, %s, 0);""",(str(message.guild.id), str(player.id), str(sorted_scores[player])))
                                if not result:
                                    await reply_message(message, "Database error!")
                            else:
                                for row in records:
                                    total_score = int(row[0])
                                total_score = total_score + sorted_scores[player]
                                result = await commit_sql("""UPDATE WordGameScores SET TotalScore=%s WHERE ServerId=%s AND UserId=%s;""",(str(total_score),str(message.guild.id),str(player.id)))
                                if not result:
                                    await reply_message(message, "Database error!")
                        records = await select_sql("""SELECT GamesWon FROM WordGameScores WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(winner.id)))
                        for row in records:
                            games_won = int(row[0])
                        games_won = games_won + 1
                        result = await commit_sql("""UPDATE WordGameScores SET GamesWon=%s WHERE ServerId=%s AND UserId=%s;""",(str(games_won),str(message.guild.id),str(winner.id)))
                        word_game_state[message.guild.id] = {}
                        word_game_state[message.guild.id]["Event"] = False
                        word_game_state[message.guild.id]["CurrentTurn"] = 0
                        word_game_state[message.guild.id]["AI"] = False
                        try: word_game_state[message.guild.id]["Players"].clear()
                        except: pass
                        try: word_game_state[message.guild.id]["Scores"].clear()
                        except: pass
                        
                        try: word_game_state[message.guild.id]["Letters"].clear()  
                        except: pass                          
                        return
                    current_turn = -1
                next_player = word_game_state[message.guild.id]["Players"][word_game_state[message.guild.id]["CurrentTurn"]]
                await reply_message(message, "<@" + str(next_player.id) + "> , it is your turn!")
                current_turn = current_turn + 1
                letter_string = " "
                for letter in word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id]:
                    letter_string = letter_string + "`" + letter + "` "
                await direct_message(word_game_state[message.guild.id]["Players"][current_turn], "It's your turn. Your letters are:\n\n" + letter_string)
                        
            else:
                await reply_message(message, "That isn't a valid word! Please try again!")
        elif command == 'abortwordgame':
            word_game_state[message.guild.id] = {}
            word_game_state[message.guild.id]["Event"] = False
            word_game_state[message.guild.id]["CurrentTurn"] = 0
            word_game_state[message.guild.id]["AI"] = False
            try: word_game_state[message.guild.id]["Players"].clear()
            except: pass
            try: word_game_state[message.guild.id]["Scores"].clear()
            except: pass
            
            try: word_game_state[message.guild.id]["Letters"].clear()  
            except: pass    
            await reply_message(message, "Word game aborted! No points will be given for this game!")
        elif command == 'mywordstats':
            records = await select_sql("""SELECT TotalScore, GamesWon FROM WordGameScores WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            for row in records:
                score = row[0]
                games_won = row[1]
            await reply_message(message, "Stats for " + message.author.display_name + ":\n\nTotal score: " + str(score) + "\nGames Won: " + str(games_won))
        elif command == 'wordpass':
            if not word_game_state[message.guild.id]["Event"]:
                await reply_message(message, "There's no word game in progress! Please type ?wordgame to start a new game!")
                return
            if message.author != word_game_state[message.guild.id]["Players"][word_game_state[message.guild.id]["CurrentTurn"]]:
                await reply_message(message, "It isn't your turn! Please wait until then to play!")
                return
                
            if word_game_state[message.guild.id]["CurrentTurn"] < len(word_game_state[message.guild.id]["Players"]) - 1:        
                word_game_state[message.guild.id]["CurrentTurn"] = word_game_state[message.guild.id]["CurrentTurn"] + 1        
            else:
                word_game_state[message.guild.id]["CurrentTurn"] = 0
                if word_game_state[message.guild.id]["CurrentRound"] < word_game_state[message.guild.id]["MaxRounds"] - 1:
                
                    word_game_state[message.guild.id]["CurrentRound"] = word_game_state[message.guild.id]["CurrentRound"] + 1
                    await reply_message(message, "End of round " + str(word_game_state[message.guild.id]["CurrentRound"] - 1) + " and moving to round " + str(word_game_state[message.guild.id]["CurrentRound"]) + "!")
                else:
                    await reply_message(message, "End of game!")
                    scores = {}
                    for x in range (0, len(word_game_state[message.guild.id]["Players"])):
                        scores[word_game_state[message.guild.id]["Players"][x]] = word_game_state[message.guild.id]["Scores"][x]
                    sorted_scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1])}
                    response = "**FINAL SCORES**\n\n"
                    for player in sorted_scores.keys():
                        response = response + player.display_name + " - "  + str(sorted_scores[player]) + "\n"
                        if sorted_scores[player] == max(list(sorted_scores.values())):
                            winner = player
                    response = response + "\n\n" + player.display_name + " wins the round!"
                    
                    await reply_message(message, response)  
                    for player in sorted_scores.keys():
                        records = await select_sql("""SELECT TotalScore FROM WordGameScores WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(player.id)))
                        if not records:
                            result = await commit_sql("""INSERT INTO WordGameScores (ServerId, UserId, TotalScore, GamesWon) VALUES (%s, %s, %s, 0);""",(str(message.guild.id), str(player.id), str(sorted_scores[player])))
                            if not result:
                                await reply_message(message, "Database error!")
                        else:
                            for row in records:
                                total_score = int(row[0])
                            total_score = total_score + sorted_scores[player]
                            result = await commit_sql("""UPDATE WordGameScores SET TotalScore=%s WHERE ServerId=%s AND UserId=%s;""",(str(total_score),str(message.guild.id),str(player.id)))
                            if not result:
                                await reply_message(message, "Database error!")
                    records = await select_sql("""SELECT GamesWon FROM WordGameScores WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(winner.id)))
                    for row in records:
                        games_won = int(row[0])
                    games_won = games_won + 1
                    
                    word_game_state[message.guild.id] = {}
                    word_game_state[message.guild.id]["Event"] = False
                    word_game_state[message.guild.id]["CurrentTurn"] = 0
                    word_game_state[message.guild.id]["AI"] = False
                    try: word_game_state[message.guild.id]["Players"].clear()
                    except: pass
                    try: word_game_state[message.guild.id]["Scores"].clear()
                    except: pass
                    
                    try: word_game_state[message.guild.id]["Letters"].clear()  
                    except: pass
                    result = await commit_sql("""UPDATE WordGameScores SET GamesWon=%s WHERE ServerId=%s AND UserId=%s;""",(str(games_won),str(message.guild.id),str(winner.id)))                    
                    return                
                current_turn = -1
            next_player = word_game_state[message.guild.id]["Players"][word_game_state[message.guild.id]["CurrentTurn"]]
            await reply_message(message, message.author.display_name + " is passing on their turn. <@" + str(next_player.id) + "> , it is your turn!")
            current_turn = current_turn + 1
            letter_string = " "
            for letter in word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id]:
                letter_string = letter_string + "`" + letter + "` "
            await direct_message(word_game_state[message.guild.id]["Players"][current_turn], "It's your turn. Your letters are:\n\n" + letter_string)   
        elif command == 'trade':
            if not word_game_state[message.guild.id]["Event"]:
                await reply_message(message, "There's no word game in progress! Please type ?wordgame to start a new game!")
                return
            if message.author != word_game_state[message.guild.id]["Players"][word_game_state[message.guild.id]["CurrentTurn"]]:
                await reply_message(message, "It isn't your turn! Please wait until then to play!")
                return    
            current_turn = word_game_state[message.guild.id]["CurrentTurn"]
            letters = parsed_string.upper()
            replaced_letters = []   

            for x in list(letters):
                if x in word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id]:
                    if x in replaced_letters:
                        continue
                    letter_replacer = word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id].index(x)
                    word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id][letter_replacer] = await get_letter()
                    replaced_letters.append(x)                

                else:
                    await reply_message(message, "Could not trade letter " + x + " because it is not in your letter set!")
            await reply_message(message, message.author.display_name + " traded some letters!")
            
            if word_game_state[message.guild.id]["CurrentTurn"] < len(word_game_state[message.guild.id]["Players"]) - 1:        
                word_game_state[message.guild.id]["CurrentTurn"] = word_game_state[message.guild.id]["CurrentTurn"] + 1        
            else:
                word_game_state[message.guild.id]["CurrentTurn"] = 0
                if word_game_state[message.guild.id]["CurrentRound"] < word_game_state[message.guild.id]["MaxRounds"] - 1:
                
                    word_game_state[message.guild.id]["CurrentRound"] = word_game_state[message.guild.id]["CurrentRound"] + 1
                    await reply_message(message, "End of round " + str(word_game_state[message.guild.id]["CurrentRound"] - 1) + " and moving to round " + str(word_game_state[message.guild.id]["CurrentRound"]) + "!")
                else:
                    await reply_message(message, "End of game!")
                    scores = {}
                    for x in range (0, len(word_game_state[message.guild.id]["Players"])):
                        scores[word_game_state[message.guild.id]["Players"][x]] = word_game_state[message.guild.id]["Scores"][x]
                    sorted_scores = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1])}
                    response = "**FINAL SCORES**\n\n"
                    for player in sorted_scores.keys():
                        response = response + player.display_name + " - "  + str(sorted_scores[player]) + "\n"
                        if sorted_scores[player] == max(list(sorted_scores.values())):
                            winner = player
                    response = response + "\n\n" + player.display_name + " wins the round!"
                    
                    await reply_message(message, response)  
                    for player in sorted_scores.keys():
                        records = await select_sql("""SELECT TotalScore FROM WordGameScores WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(player.id)))
                        if not records:
                            result = await commit_sql("""INSERT INTO WordGameScores (ServerId, UserId, TotalScore, GamesWon) VALUES (%s, %s, %s, 0);""",(str(message.guild.id), str(player.id), str(sorted_scores[player])))
                            if not result:
                                await reply_message(message, "Database error!")
                        else:
                            for row in records:
                                total_score = int(row[0])
                            total_score = total_score + sorted_scores[player]
                            result = await commit_sql("""UPDATE WordGameScores SET TotalScore=%s WHERE ServerId=%s AND UserId=%s;""",(str(total_score),str(message.guild.id),str(player.id)))
                            if not result:
                                await reply_message(message, "Database error!")
                    records = await select_sql("""SELECT GamesWon FROM WordGameScores WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(winner.id)))
                    for row in records:
                        games_won = int(row[0])
                    games_won = games_won + 1
                    result = await commit_sql("""UPDATE WordGameScores SET GamesWon=%s WHERE ServerId=%s AND UserId=%s;""",(str(games_won),str(message.guild.id),str(winner.id)))
                    
                    word_game_state[message.guild.id] = {}
                    word_game_state[message.guild.id]["Event"] = False
                    word_game_state[message.guild.id]["CurrentTurn"] = 0
                    word_game_state[message.guild.id]["AI"] = False
                    try: word_game_state[message.guild.id]["Players"].clear()
                    except: pass
                    try: word_game_state[message.guild.id]["Scores"].clear()
                    except: pass
                    try: word_game_state[message.guild.id]["Letters"].clear()                       
                    except: pass
                    return                
                current_turn = -1
            next_player = word_game_state[message.guild.id]["Players"][word_game_state[message.guild.id]["CurrentTurn"]]
            await reply_message(message, message.author.display_name + " traded letters for their turn. <@" + str(next_player.id) + "> , it is your turn!")
            current_turn = current_turn + 1
            letter_string = " "
            for letter in word_game_state[message.guild.id]["Letters"][word_game_state[message.guild.id]["Players"][current_turn].id]:
                letter_string = letter_string + "`" + letter + "` "
            await direct_message(word_game_state[message.guild.id]["Players"][current_turn], "It's your turn. Your letters are:\n\n" + letter_string)   
        elif command == 'addquote':
            if message.author.id not in allowed_users:
                await reply_message(message, "You're not an admin of the bot!")
                return
                
            command_re = re.compile(r"-name (?P<name>.+) -quote (?P<quote>.+)")
            if not parsed_string:
                await reply_message(message, "No parameters passed!")
                return
            m = command_re.search(parsed_string)
            if m:
                name = m.group('name')
                quote = m.group('quote')
            else:
                await reply_message(message, "Missing parameter!")
                return
                
            if not name:
                await reply_message(message, "No name specified!")
                return
            if not quote:
                await reply_message(message, "No quote specified!")
                return
            result = await commit_sql("""INSERT INTO Sayings (Name, Saying) VALUES (%s, %s);""",(name,quote))
            await reply_message(message, "Saying added!")  
        elif command == 'quote':
            if message.channel.nsfw:
                records = await select_sql("""SELECT Name,Saying FROM Sayings;""")
                response = ""
                record = random.choice(records)
                response = response + '"' + record[1] + '"' + ' -' + record[0]
                
                await reply_message(message, response)            
        else:
            pass

@client.event
async def on_interaction(member, interaction):
    global command_handler
    global slash_commands
    print("called here" + str(interaction))
    slash_commands.convert_to_message(interaction, member, "?")        
client.run'REDACTED'

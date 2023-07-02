import discord
# import discordslashcommands as dsc
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

intents = discord.Intents.default()
from slashcommands import SlashCommands

manager = None
class NakedObject(object):
    pass
    
connection = mysql.connector.connect(host='localhost', database='AuthorMaton', user='REDACTED', password='REDACTED')
client = discord.Client(heartbeat_timeout=600, intents=intents)
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
word_of_the_day_score = 60
entry_limit = 20
already_posted = {}
manager = None
bot_log_channel = None
ephemeral_messages = {}


f = open("/home/REDACTED/BotMaster/writingprompts.txt", 'r')
writing_prompts = f.read().split('\n')
f.close()

pos_translator = { 'n': 'Noun', 'v': 'Verb', 'a': 'Adjective', 'r': 'Adverb', 's': 'Satellite Adjective'}
pretentious_trans =  {

    'JJ': wn.ADJ,
    'JJR': wn.ADJ,
    'JJS': wn.ADJ,
    'NN': wn.NOUN,
    'NNS': wn.NOUN,
    'NNP': wn.NOUN,
    'NNPS': wn.NOUN,
    'RB': wn.ADV,
    'RBR': wn.ADV,
    'RBS': wn.ADV,
    'VB': wn.VERB,
    'VBD': wn.VERB,
    'VBG': wn.VERB,
    'VBN': wn.VERB,
    'VBP': wn.VERB,
    'VBZ': wn.VERB,
}
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
wotd_words = [ n for n in wn.all_lemma_names() if len(n) > 12 and len(n) < 18 and not re.search(r"_",n) and not re.search(r"-",n) and not re.search(r"^un|^non|osis$|ness$|itis$",n) and not re.search(r"genus|species|phylum|chemical|family|order|kingdom|class|controlled|abnormality|disorder|disease|stimulant|depressant|division|birth_defect",str(wn.synset(str(wn.synsets(n)[0].name())).hypernyms())) and not re.search(r"relating to",str(wn.synset(str(wn.synsets(n)[0].name())).definition()))]
all_words = [ n for n in wn.all_lemma_names()]


# async def word_of_the_day():
    # global word_of_the_day_schedule
    # await client.wait_until_ready()
    # await log_message("Lanuching timer.")
    # while True:
        # current_time_obj = datetime.now()
        # current_hour = int(current_time_obj.strftime("%H"))
        # current_minute = int(current_time_obj.strftime("%M"))
        # current_second = int(current_time_obj.strftime("%S"))
        # for server_id in word_of_the_day_schedule.keys():
            # try: word_of_the_day_schedule[server_id]
            # except: continue
            # try: word_of_the_day_schedule[server_id]["Hour"]
            # except: word_of_the_day_schedule[server_id]["Hour"] = 0
            # try: word_of_the_day_schedule[server_id]["Minute"]
            # except: word_of_the_day_schedule[server_id]["Minute"] = 0
            # #await log_message(str(current_hour) + ":" + str(current_minute) + ":" + str(current_second))
            
            # if word_of_the_day_schedule[server_id]["Hour"] == current_hour and word_of_the_day_schedule[server_id]["Minute"] == current_minute and current_second <= 1:
                # print("WOTD writing...")
                # try:
                    # channel_obj = client.get_channel(word_of_the_day_schedule[server_id]["ChannelId"])
                # except:
                    # continue
                    
                # acceptable_word = False
                # while not acceptable_word:
                    # get_word_of_the_day = """SELECT Word FROM WordValues WHERE WordValue>=%s ORDER BY RAND( ) LIMIT 1;"""

                    # records = await select_sql(get_word_of_the_day, ("100",))
                    # for row in records:
                        # word = row[0]
                    # get_word_based_on_score = """SELECT Word,PartOfSpeech,Definitions FROM DictionaryDefs WHERE (Word=%s AND Definitions NOT LIKE '%model%') LIMIT 1;"""
                    # records = await select_sql(get_word_based_on_score, (word,))
                    # word_without = word[:-1]
                    # for row in records:
                        
                        # if not re.search(r"plural|singular|past|future|form|^\s*\*.+\*\s*$|x-wiki|ly$", str(row[2]), re.S | re.MULTILINE | re.IGNORECASE) and not re.search(word_without, row[2], re.S | re.MULTILINE | re.IGNORECASE):
                            # part_of_speech = row[1]
                            # definitions = await clean_definition(row[2])

                            
                            # acceptable_word = True
                            # await log_message("WOTD found!")

                # if records:
                    # response = "**WORD OF THE DAY**\n\nThe word of the day is **"
                    # m = re.search(r"en-(.*?) ",definitions)
                    # if m:
                        # part_of_speech = m.group(1)
                        # definitions = definitions.replace("en-" + part_of_speech,"")
                    # definitions = ''.join(filter(lambda x: not re.match(r"- +\*\(.*\)\*", x), definitions))
                    # definitions = ''.join(filter(lambda x: not re.match(r'^\n$|^-\n$', x), definitions))
                    # definitions = definitions.replace('- ','\n- ')                        
                    # response = response + str(row[0]) + "** *" + part_of_speech + "*\n\n" + definitions + "\n\n"
                    # try:
                        # await channel_obj.send(response)
                    # except:
                        # pass
                        
                # else:
                    # await send_message(message, "Database error.")
        # await asyncio.sleep(1)     

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
            if current_hour == 0 and current_minute == 0:
                for guild in client.guilds:
                    already_posted[guild.id] = False
            try:
                if already_posted[server_id]:
                    continue
            except:
                continue
            if word_of_the_day_schedule[server_id]["Hour"] == current_hour and word_of_the_day_schedule[server_id]["Minute"] == current_minute:
                print("WOTD writing...")
                try:
                    channel_obj = client.get_channel(word_of_the_day_schedule[server_id]["ChannelId"])
                except:
                    continue
                already_posted[server_id] = True
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
                try:
                    await channel_obj.send(embed=embed)
                    continue
                except:
                    pass
                
        await asyncio.sleep(60)  
        
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
        return False

async def clean_definition(text):
    definitions = text
    definitions = re.sub(r"<sha1>.*?</sha1>","",definitions)
    definitions = re.sub(r"(?:http|https).* ","",definitions)
    definitions = re.sub(r"<.*?>","",definitions)
    definitions = re.sub(r"(\d+)supth",r"\1th",definitions)
    definitions = re.sub(r"(\d+)supthsup",r"\1th",definitions)
    definitions = re.sub(r"(\d+)supst",r"\1th",definitions)
    definitions = definitions.replace("'''","*")
    definitions = definitions.replace("----","")
    definitions = re.sub(r";\s*?;",";",definitions)
    definitions = definitions.replace(" ,",",")
    definitions = definitions.replace('/','')
    definitions = definitions.replace('; ;',';')
    definitions = re.sub(r";\s*;","",definitions)
    definitions = definitions.replace('*(nodot=a)*','')
    definitions = definitions.replace(';','\n-  ')
   
    
    m = re.search(r"en-(.*?) ",definitions)
    if m:
        part_of_speech = m.group(1)
        definitions = definitions.replace("en-" + part_of_speech,"")
    definitions = ''.join(filter(lambda x: not re.match(r"- +\*\(.*\)\*", x), definitions))
    definitions = ''.join(filter(lambda x: not re.match(r'^\n$|^-\n$', x), definitions))
    definitions = definitions.replace('- ','\n- ')
    definitions = re.sub(r"-\s+$","", definitions, re.MULTILINE)
    return definitions
    
            
async def send_message(message, response):
    global ephemeral_messages
    if ephemeral_messages[message.guild.id]:
        return
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

async def load_words(message):
    global connection
    xml_file = "/home/REDACTED/enwiktionary-latest-pages-articles.xml"
    
    f = open(xml_file, 'r')
    word_count = 0
    definition = ""
    word = ""
    synonyms = ""
    antonyms = ""
    rhymes = ""
    part_of_speech = "unknown"
    syn_flag = False
    ant_flag = False
    etym_flag = False
    sample_sentence_re = re.compile(r"#+[*]+|#+:+|#+[*]+:+")
    divider_re = re.compile(r"----")
    part_of_speech_re = re.compile(r"Adjective|Noun|Verb|Adverb|Pronoun|Conjunction|Preposition|Interjection")
    english_re = re.compile("=English=")
    etym_re = re.compile(r"=Etymology.*?=")
    adj_re = re.compile(r"=Adjective=")
    noun_re = re.compile(r"=Noun=")
    verb_re = re.compile(r"=Verb=")
    adverb_re = re.compile(r"=Adverb=")
    rhyme_replace_re = re.compile(r"begin rhyme list|end rhyme list", re.MULTILINE | re.S)
    translations_re = re.compile(r"=Translations=", re.MULTILINE | re.S)
    
    pronoun_re = re.compile(r"=Pronoun=")
    conj_re = re.compile(r"=Conjunction=")
    prep_re = re.compile(r"=Preposition=")
    intj_re = re.compile(r"=Interjection=")
    wiki_re = re.compile(r"[\[|\]|\{|\}|\||\|\|]")
    extra_clear_re = re.compile(r"\s+lb\s+\|", re.MULTILINE | re.S)
    extra_extra_clear_re = re.compile("\s+en\s+|;en\s+|^en\s+|\|en\s+|\|en", re.MULTILINE | re.S)
    title_re = re.compile(r"<title>(?P<word>.*)</title>")
    text_begin_re = re.compile(r"<text")
    text_end_re = re.compile(r"</text>", re.MULTILINE | re.S)
    symbol_re = re.compile(r"&.+?;", re.S)
    definition_re = re.compile(r"^\#+ ")
    synonym_re = re.compile(r"=Synonyms=")
    antonym_re = re.compile(r"=Antonyms=")
    remove_first_separator_re = re.compile(r"^\s*?[;,]\s+?")
    syn_word_re = re.compile(r"\{\{(?:.+\|)+.+?\}\}", re.S | re.MULTILINE)
    ant_word_re = re.compile(r"\{\{(?:.+\|)+.+?\}\}", re.S | re.MULTILINE)
    page_end_re = re.compile(r"</page>")
    def_exclude_re = re.compile(r"infl of|inflection of|verb form|verb-form|imperative of")
    blank_re = re.compile(r"^\s+$")
    sentence_re = re.compile(r"\{\{ux\|en\|(?P<sentence>.*)\}", re.MULTILINE)
    sentence2_re = re.compile("#: ''(?P<sentence>.*)''", re.MULTILINE)
    rhyme_re = re.compile(r"=Rhymes=")
    derived_re = re.compile(r"=Derived terms=", re.IGNORECASE)
    user_re = re.compile(r"User:")
    rhyme_page_end_re = re.compile(r"</page>")
    space_clear_re = re.compile(r"\s+", re.MULTILINE | re.S)
    rhyme_pro_re = re.compile(r"\{\{rhymes\|.*\|(?P<rhymepro>.*)\}\}", re.MULTILINE | re.S)
    rhyme_page_re = re.compile(r"title>Rhymes:English.(?P<pro>.*?)</title", re.MULTILINE | re.S)
    skip_stuff_re = re.compile(r"Index:|Category:|Appendix:|Wiktionary:|Esperanto|Rhymes:(?!English)")
    thesaurus_re = re.compile(r"Thesaurus:")
    language_re = re.compile(r"==.+?==")
    equals_clear_re = re.compile(r" .*=.*? ")
    rhyme_pronunciation = ""
    sample_sentences = ""
    rhyme_pro = ""
    rhyme_page_content = ""
    etymology = "" 
    rhyme_list = ""
    derived_terms = ""
    skip_page = False
    rhyme_list_flag = False
    text_line_counter = 0
    text_flag = False
    skip_rest_of_page = False
    rhyme_flag = False
    rhyme_page_flag = False
    thesaurus_flag = False
    language = " "
    new_word = True
    derived_flag = False
    see_syn_flag = False
    see_ant_flag = False
    definition_flag = False
    language_dict = {
            'en': 'English',
            'enm': 'Middle English',
            'ang': 'Old English',
            'gem-pro': 'Proto-Germanic',
            'ine-pro': 'Proto-Indo-European',
            'sco': 'scots',
            'fy': 'West Frisian',
            'nl': 'Dutch',
            'nds': 'Low German',
            'de': 'German',
            'sv': 'Swedish',
            'is': 'Icelandic',
            'la': 'Latin',
            'ru': 'Russian',
            'hy': 'Armenian',
            'grc': 'Ancient Greek',
            'xno': 'Anglo-Norman',
            'fro': 'Old French',
            'fr': 'French',
            'frm': 'Middle French',
            'ar': 'Arabic',
            'cmn': 'Chinese Mandarin',
            'da': 'Danish',
            'el': 'Greek',
            'he': 'Hebrew',
            'hi': 'Hindi',
            'id': 'Indonesian',
            'il': 'Italian',
            'ko': 'Korean',
            'ms': 'Malay',
            'mn': 'Mongolian',
            'nrf': 'Norman',
            'nb': 'Norweigian',
            'nn': 'Norweigian',
            'fa': 'Persian',
            'pl': 'Polish',
            'pt': 'Portugeuse',
            'ro': 'Romanian',
            'sa': 'Sanskrit',
            'gd': 'Scottish Gaelic',
            'es': 'Spanish',
            'esm': 'Middle Spanish',
            'eso': 'Old Spanish',
            'th': 'Thai',
            'ja': 'Japanese',
            'ca': 'Catalan',
            'fi': 'Finnish',
            
            }
    linecount = 0
    for line in f:
        # await log_message("Line: " + line)
        linecount= linecount+1
        if linecount%10000 == 0:
            await log_message("Line count: " + str(linecount))
        if user_re.search(line):
            continue
            
        p = etym_re.search(line)
        n = rhyme_page_re.search(line)
        m = title_re.search(line)
        if p:
            # await log_message("Etymology matched.")
            skip_page = False
        if n:
            # await log_message("Rhyme matched.")
            rhmye_pronunciation = ""
            rhyme_base = n.group('pro')
            rhyme_pronunciation = rhmye_pronunciation.join(rhyme_base)
            rhyme_pronunciation = re.sub(wiki_re," ",rhyme_pronunciation)
            await log_message("Processing rhyme " + rhyme_pronunciation + "...")
            rhyme_page_flag = True
            skip_page = True
            rhyme_page_content = ""

              
        elif m:
            # await log_message("Title matched.")     
            word = m.group('word')
            if skip_stuff_re.search(word):
                # await log_message("Skip stuff matched.")
                skip_page = True
                
            else:
                # await log_message("New word.")
                skip_page = False
                skip_rest_of_page = False
                await log_message("Processing " + word + "...")
                definition = ""
                synonyms = ""
                antonyms = ""
                rhyme_list = ""
                rhyme_pro = ""
                etymology = ""
                sample_sentences = ""
                part_of_speech = "unknown"
                new_word = True
                syn_flag = False
                ant_flag = False
                rhyme_flag = False
                derived_flag = False
                etym_flag = False
                skip_page = False
                derived_terms = ""
                thesaurus_flag = False
                skip_rest_of_page = False
                language = ""
                see_syn_flag = False
                see_ant_flag = False 
                definition_flag = False


        else:
            # await log_message("Not new word.")
            new_word = False
            
        if text_begin_re.search(line) and language_re.search(line):
            # await log_message("Text begin with language.")
            language = re.search(r"==(.+?)==",line)
            language = language.group(1)
            text_flag = False        
        elif text_begin_re.search(line):
            # await log_message("text begin.")
            text_flag = True
  
        elif text_flag and language_re.search(line):
            # await log_message("Text end.")
            language = re.search(r"==(.+?)==",line)
            language = language.group(1)
            text_flag = False
   
        if (translations_re.search(line)):
            # await log_message("Translations.")
            skip_rest_of_page = True
        elif (skip_rest_of_page and re.search("==",line)):
            skip_rest_of_page = False
            # await log_message("End skip rest.")
        else:
            pass

            




  
        if not skip_page and not skip_rest_of_page:    
            if thesaurus_re.search(word):
                # await log_message("See also thesaurus.")
                if (see_ant_flag and re.search(r"==",line)):
                    see_ant_flag = False
                    thesaurus_flag = False
                    create_also_entry = """INSERT INTO SeeAlsoThesaurus (Word, Synonyms, Antonyms) VALUES (%s, %s, %s);"""
                    also_word = word.replace("Thesaurus:","")
                    also_entry = (also_word, synonyms, antonyms)
                    result = await commit_sql(create_also_entry, also_entry)
                    if not result:
                        # await log_message("Database error!")
                        pass
                elif (antonym_re.search(line)):
                    # await log_message("See also thesaurus antonym.")
                    see_syn_flag = False
                    see_ant_flag = True
                    print("Found an antonym field!")
                elif (see_syn_flag and re.search(r"==",line)):
                    see_syn_flag = False

                    
                elif (synonym_re.search(line)):
                    see_syn_flag = True
                    

                if (see_syn_flag):
                    # await log_message("See also syn.")
                    syns = re.finditer(syn_word_re,line)
                    for syn in syns:
                        temp_syn = re.sub("#+"," ",line)
                        temp_syn = temp_syn.replace("*","")
                        temp_syn = re.sub(r"\{\{(?:.+\|)+(.+?)\}\}",r"*\1*", temp_syn)
                        temp_syn = temp_syn.replace("of|","of ")
                        temp_syn = temp_syn.replace("|of"," of")
                        temp_syn = re.sub(wiki_re," ",temp_syn)
                        temp_syn = re.sub(extra_clear_re,"",temp_syn)
                        while(extra_extra_clear_re.search(temp_syn)):
                            temp_syn = re.sub(extra_extra_clear_re,"",temp_syn)
                        temp_syn = re.sub(text_end_re, " ",temp_syn)
                        temp_syn = temp_syn.replace("\n","")
                        temp_syn = re.sub(symbol_re,"",temp_syn)
                        temp_syn = re.sub(r"^\s*;\s+"," ",temp_syn)
                        temp_syn = re.sub("ref.*?;"," ",temp_syn)
                        temp_syn = re.sub(space_clear_re," ",temp_syn)
                        temp_syn = temp_syn.replace(" ws "," ")
                        temp_syn = re.sub(r"_"," ",temp_syn)
                        temp_syn = re.sub(r"\s+\.",".",temp_syn)
                        temp_syn = re.sub(r" .*?=.*? "," ",temp_syn)
                        temp_syn = temp_syn.replace(" ws "," ")
                        temp_syn = temp_syn.replace("*","")
                        
                        synonyms = synonyms + ", " + temp_syn
                if (see_ant_flag):
                    # await log_message("See also ant.")
                    ants = re.finditer(ant_word_re,line)
                    for ant in ants:
                        temp_ant = re.sub("#+"," ",line)
                        temp_ant = temp_ant.replace("*","")
                        temp_ant = re.sub(r"\{\{(?:.+\|)+(.+?)\}\}",r"*\1*", temp_ant)
                        temp_ant = temp_ant.replace("of|","of ")
                        temp_ant = temp_ant.replace("|of"," of")
                        temp_ant = re.sub(wiki_re," ",temp_ant)
                        temp_ant = re.sub(extra_clear_re,"",temp_ant)
                        while(extra_extra_clear_re.search(temp_ant)):
                            temp_ant = re.sub(extra_extra_clear_re,"",temp_ant)
                        temp_ant = re.sub(text_end_re, " ",temp_ant)
                        temp_ant = temp_ant.replace("\n","")
                        temp_ant = re.sub(symbol_re,"",temp_ant)
                        temp_ant = re.sub(r"^\s*;\s+"," ",temp_ant)
                        temp_ant = re.sub(r"ref.*?;"," ",temp_ant)
                        temp_ant = re.sub(space_clear_re," ",temp_ant)
                        temp_ant = temp_ant.replace(" ws "," ")
                        temp_ant = re.sub(r"_"," ",temp_ant)
                        temp_ant = re.sub(r"\s+\.",".",temp_ant)
                        temp_ant = re.sub(r"\s+.*?=.*?\s+"," ",temp_ant)
                        temp_ant = temp_ant.replace(" ws "," ")
                        temp_ant = temp_ant.replace("*","")
                        
                        antonyms = antonyms + ", " + temp_ant


                    


                
            m = rhyme_pro_re.search(line)
            if m:
                # await log_message("Rhymepro.")
                rhyme_pro = m.group('rhymepro')
                
            if (part_of_speech_re.search(line) and not new_word and not def_exclude_re.search(definition) and not skip_rest_of_page and definition):
                try:
                    # await log_message("Not new word, inserting into database.")
                    definition = re.sub(remove_first_separator_re,"",definition)
                    definition = re.sub(r"<sha1>.*?</sha1>","",definition)
                    definition = re.sub(r"(?:http|https).*? ","",definition)
                    definition = re.sub(r"<.*?>","",definition)
                    definition = re.sub(r"(\d+)supth",r"\1th",definition)
                    definition = re.sub(r"(\d+)supthsup",r"\1th",definition)
                    definition = re.sub(r"(\d+)supst",r"\1th",definition)
                    definition = re.sub(r";\s+;","",definition)
                    definition = re.sub(equals_clear_re,"",definition)
                    definition = definition.replace("'''","*")
                    definition = definition.replace("----","")                    
                    create_dictionary_entry = """INSERT INTO DictionaryDefs (Word, PartOfSpeech, Language, Definitions, Pronunciation) VALUES( %s, %s, %s, %s, %s);"""   
                    dictionary_entry = (word, part_of_speech, language, definition, rhyme_pro)

                    result = await commit_sql(create_dictionary_entry, dictionary_entry)
                except:
                    pass
                
                definition = ""

            if (adj_re.search(line)):
                part_of_speech = "adjective"
                
            if (noun_re.search(line)):
                part_of_speech = "noun"
                
            if (verb_re.search(line)):
                part_of_speech = "verb"
                
            if (adverb_re.search(line)):
                part_of_speech = "adverb"
                
            if (pronoun_re.search(line)):
                part_of_speech = "pronoun"
                
            if (conj_re.search(line)):
                part_of_speech = "conjunction"
                
            if (prep_re.search(line)):
           
                part_of_speech = "preposition"
                
            if (intj_re.search(line)):
                part_of_speech = "interjection"
                
            if etym_flag and re.search(r"==",line):
                etym_flag = False
                
            if etym_flag and not re.search(r"==",line):
                # await log_message("Etymology sentence.")
                etym_sentence = line
                etym_sentence = re.sub(r"\{\{.+?\|.+?\|","",etym_sentence)
                etym_sentence = re.sub(r"<.*>","",etym_sentence)
                for key in language_dict:
                    etym_sentence = etym_sentence.replace(str(key) + "|",str(language_dict[key]) + " ")
                etym_sentence = re.sub(wiki_re," ",etym_sentence)
                etym_sentence = re.sub(extra_clear_re,"",etym_sentence)
                while(extra_extra_clear_re.search(etym_sentence)):
                    etym_sentence = re.sub(extra_extra_clear_re,"",etym_sentence)
                etym_sentence = re.sub(text_end_re, "",etym_sentence)
                etym_sentence = etym_sentence.replace("\n","")
                etym_sentence = re.sub(symbol_re,"",etym_sentence)
                etym_sentence = re.sub("ref.*?;","",etym_sentence)
                etym_sentence = re.sub(space_clear_re," ",etym_sentence)
                etym_sentence = re.sub(r"_","",etym_sentence)
                etym_sentence = re.sub(r"\s+\.",".",etym_sentence)
                etym_sentence = re.sub(r" .+?=.+ "," ",etym_sentence)
                etym_sentence = re.sub(equals_clear_re,"",etym_sentence)
                etymology = etymology + "; " + etym_sentence
                
            if etym_re.search(line):
                # await log_message("Eytm flag true.")
                etym_flag = True
                

            if derived_flag and re.search("==",line):
                # await log_message("etym flag false.")
                derived_flag = False
                part_of_speech = 'unknown'
     

                
            if derived_flag and (not re.search("==",line)):
                # await log_message("Derived line.")
                line_formatted = line.replace("*","").replace("#","").replace('\n','').replace('\r','')
                if re.search(r"\{\{.+\|.+\|.+\}\}", line_formatted):
                    terms = re.sub(r"\{\{.+\|.+\|","",line_formatted)
                    terms = terms.replace("}}","")
                elif re.search(r"\[\[.+\|.+\|.+\]\]", line_formatted):
                    terms = re.sub(r"\[\[.+\|.+\|","",line_formatted)
                    terms = terms.replace("]]","")                    
                elif re.search(r"[^\|]",line_formatted):
                    terms = line_formatted.replace("[","").replace("]","").replace("{","").replace("}","")
                elif re.search(r"\{\{(?:.+\|)+.+\}\}",line_formatted):
                    terms = re.findall(r"\|(.+?)\|", line_formatted)
                elif re.search(r"\[\[(?:.+\|)+.+\]\]",line_formatted):
                    terms = re.findall(r"\|(.+?)\|", line_formatted)
                else:
                    pass
                
                if isinstance(terms, list):
                    for temp_term in terms:
                        
                        temp_term2 = temp_term.replace("|",", ")
                        temp_term2 = re.sub(r"<.*?>.*?<.*?>","",temp_term2)               
                        derived_terms = derived_terms + ", " + temp_term2.replace(r"\n","")
                else:
                    derived_terms = derived_terms + ", " + terms.replace(r"\n","")
            elif derived_re.search(line):
                derived_flag = True
            else:
                pass

         
            # if definition_flag and re.search(r"==", line):
                # # await log_message("Definition flag false.")
                # definition_flag = False
                # part_of_speech = 'unknown'

            if (definition_re.search(line)) and not sample_sentence_re.search(line):
                # await log_message("Found definition.")
                temp_def = re.sub(r"#+","",line)
                
                temp_def = temp_def.replace("<sup>","")
                temp_def = temp_def.replace("</sup>"," ")
                temp_def = temp_def.replace("of|","of ")
                temp_def = temp_def.replace("|of"," of")
                
                temp_def = re.sub(r"\{\{(?:.+?\|)+?(.+?)\}\}",r"*(\1)*", temp_def)
                temp_def = re.sub(wiki_re," ",temp_def)
                temp_def = temp_def.replace("defdate","")
                temp_def = re.sub(extra_clear_re,"",temp_def)
                while(extra_extra_clear_re.search(temp_def)):
                    temp_def = re.sub(extra_extra_clear_re,"",temp_def)
                temp_def = re.sub(text_end_re, "",temp_def)
                temp_def = temp_def.replace("\n","")
                temp_def = re.sub(symbol_re,"",temp_def)
                
                temp_def = re.sub(space_clear_re," ",temp_def)
                temp_def = re.sub(r"_","",temp_def)
                temp_def = re.sub(r"\s+\.",".",temp_def)
                temp_def = re.sub(r"\s+.+?=.+?\s+"," ",temp_def)
                temp_def = temp_def.replace("|","")
                temp_def = re.sub(r"<.*?>.*?<.*?>","",temp_def)
                temp_def = re.sub(r"(?:http|https).*? ","",temp_def)
                temp_def = re.sub(r"<.*?>","",temp_def)
                temp_def = re.sub(r"(\d+)supth",r"\1th",temp_def)
                temp_def = re.sub(r"(\d+)supthsup",r"\1th",temp_def)
                temp_def = re.sub(r"(\d+)supst",r"\1th",temp_def)
                temp_def = re.sub(equals_clear_re,"",temp_def)
                temp_def = temp_def.replace("'''","*")
                temp_def = temp_def.replace("----","")                   
                

                definition = definition + "; " + temp_def
            if part_of_speech != 'unknown':
                # await log_message("Definiton flag true.")    
                definition_flag = True   

            if sample_sentence_re.search(line):
                # await log_message("Sample sentence.")
                sentence = re.sub("#+[*]*:*","",line)
                sentence = re.sub(wiki_re," ",sentence)
                sentence = re.sub(r"\{\{(?:.+\|)+(.+?)\}\}",r"*(\1)*", sentence)
                sentence = re.sub("'''","*",sentence)
                sentence = sentence.replace("\n","")
                sentence = re.sub(space_clear_re," ",sentence)
                sentence = re.sub(equals_clear_re,"", sentence)
                sentence = re.sub(r"<.*?>.*?<.*?>","",sentence)
                sample_sentences = sample_sentences + "; " + sentence
                
                
            if (ant_flag and re.search(r"==",line)):
                # await log_message("Ant flag false.")
                ant_flag = False                
            if (syn_flag and re.search(r"==",line)):
                # await log_message("Syn flag false.")
                syn_flag = False

                
            if (synonym_re.search(line)):
                # await log_message("Syn flag true.")
                syn_flag = True
                
            if (antonym_re.search(line)):
                # await log_message("ant flag true.")
                syn_flag = False
                ant_flag = True
                
                
            if (syn_flag):
                # await log_message("Syn found.")
                syns = re.finditer(syn_word_re,line)
                for syn in syns:
                    temp_syn = re.sub("#+"," ",line)
                    temp_syn = temp_syn.replace("*","")
                    temp_syn = re.sub(r"\{\{(?:.+\|)+(.+?)\}\}",r"*\1*", temp_syn)
                    temp_syn = temp_syn.replace("of|","of ")
                    temp_syn = temp_syn.replace("|of"," of")
                    temp_syn = re.sub(wiki_re," ",temp_syn)
                    temp_syn = re.sub(extra_clear_re,"",temp_syn)
                    while(extra_extra_clear_re.search(temp_syn)):
                        temp_syn = re.sub(extra_extra_clear_re,"",temp_syn)
                    temp_syn = re.sub(text_end_re, " ",temp_syn)
                    temp_syn = temp_syn.replace("\n","")
                    temp_syn = re.sub(symbol_re,"",temp_syn)
                    temp_syn = re.sub(r"^\s*;\s+"," ",temp_syn)
                    temp_syn = re.sub("ref.*?;"," ",temp_syn)
                    temp_syn = re.sub(space_clear_re," ",temp_syn)
                    temp_syn = temp_syn.replace(" ws "," ")
                    temp_syn = re.sub(r"_"," ",temp_syn)
                    temp_syn = re.sub(r"\s+\.",".",temp_syn)
                    temp_syn = re.sub(r" .+?=.+? "," ",temp_syn)
                    temp_syn = temp_syn.replace("*","")
                    synonyms = synonyms + ", " + temp_syn
            if (ant_flag):
                # await log_message("Ant found.")
                ants = re.finditer(ant_word_re,line)
                for ant in ants:
                    temp_ant = re.sub("#+","",line)
                    temp_ant = temp_ant.replace("*","")
                    temp_ant = re.sub(r"\{\{(?:.+\|)+(.+?)\}\}",r"*\1*", temp_ant)
                    temp_ant = temp_ant.replace("of|","of ")
                    temp_ant = temp_ant.replace("|of"," of")
                    temp_ant = re.sub(wiki_re," ",temp_ant)
                    
                    temp_ant = re.sub(extra_clear_re,"",temp_ant)
                    while(extra_extra_clear_re.search(temp_ant)):
                        temp_ant = re.sub(extra_extra_clear_re,"",temp_ant)
                    temp_ant = re.sub(text_end_re, " ",temp_ant)
                    temp_ant = temp_ant.replace("\n","")
                    temp_ant = re.sub(symbol_re,"",temp_ant)
                    temp_ant = re.sub(r"^\s*;\s+"," ",temp_ant)
                    temp_ant = re.sub("ref.*?;"," ",temp_ant)
                    temp_ant = re.sub(space_clear_re," ",temp_ant)
                    temp_ant = temp_ant.replace(" ws "," ")
                    temp_ant = re.sub(r"_"," ",temp_ant)
                    temp_ant = re.sub(r"\s+\.",".",temp_ant)
                    temp_ant = re.sub(r" .+?=.+? "," ",temp_ant)
                    temp_ant = re.sub(r"l\s+","",temp_ant)
                    antonyms = antonyms + ", " + temp_ant


                



            if (rhyme_re.search(line)):
                # await log_message("Rhyme found.")
                rhyme_flag = True
                
            if (text_end_re.search(line)):
                # await log_message("rhyme end")
                rhyme_flag = False
            
            if (rhyme_flag and wiki_re.search(line)):
                # await log_message("rhymes found")
                rhyme_list = rhyme_list + ", " + line
                rhyme_list = re.sub(wiki_re," ",rhyme_list)
                rhyme_list = re.sub(extra_clear_re,"",rhyme_list)
                while(extra_extra_clear_re.search(rhyme_list)):
                        temp_rhyme = re.sub(extra_extra_clear_re,"",temp_rhyme)
                rhyme_list = re.sub(space_clear_re," ",rhyme_list)
                
            
            if page_end_re.search(line) and definition:
                try:
                    # await log_message("Insert into dictionary.")
     
                    create_dictionary_entry = """INSERT INTO DictionaryDefs (Word, PartOfSpeech, Language, Definitions, Pronunciation) VALUES(%s, %s, %s, %s, %s);"""   
                    create_thesaurus_entry = """INSERT INTO Thesaurus (Word, Synonyms, Antonyms) VALUES ( %s, %s, %s);"""
                    create_rhyme_entry = """INSERT INTO Rhyming (Word, RhymesWith) VALUES (%s, %s);"""
                    create_sentence_entry = """INSERT INTO SampleSentences (Word, Sentences) VALUES (%s, %s);"""
                    create_etymology_entry = """INSERT INTO Etymology (Word, Etymology) VALUES (%s, %s);"""
                    create_derived_entry = """INSERT INTO DerivedWords (Word, DerivedTerms) VALUES (%s, %s);"""
                    definition = re.sub(remove_first_separator_re,"",definition)
                    
                    synonyms = re.sub(remove_first_separator_re,"",synonyms)
                    antonyms = re.sub(remove_first_separator_re,"",antonyms)
                    rhyme_list = re.sub(remove_first_separator_re,"",rhyme_list)
                    sample_sentences = re.sub(remove_first_separator_re,"",sample_sentences)
                    etymology = re.sub(remove_first_separator_re,"",etymology)
                    derived_terms = re.sub(remove_first_separator_re,"",derived_terms)
                    dictionary_entry = (word, part_of_speech, language, definition, rhyme_pro)
                    thesaurus_entry = (word, synonyms, antonyms)
                    rhyme_entry = (word, rhyme_list)
                    sentences_entry = (word, sample_sentences)
                    etym_entry = (word, etymology)
                    derived_entry = (word, derived_terms)
                    if definition:
                        result = await commit_sql(create_dictionary_entry, dictionary_entry)
                    if synonyms or antonyms:
                        result = await commit_sql(create_thesaurus_entry, thesaurus_entry)
                    if rhyme_list:
                        result = await commit_sql(create_rhyme_entry, rhyme_entry)
                    if sample_sentences:
                        result = await commit_sql(create_sentence_entry, sentences_entry)
                    if etymology:
                        result = await commit_sql(create_etymology_entry, etym_entry)
                    if derived_terms:
                        result = await commit_sql(create_derived_entry, derived_entry)
                    
                    word_count = word_count + 1
                except mysql.connector.Error as error:
                    # await log_message("Error: " + str(error))
                    #await message.channel.send("Database error! " + str(error))  
                    pass

        if rhyme_page_flag:
            if rhyme_re.search(line):
                rhyme_list_flag = True
            
            if rhyme_list_flag and not re.search(r"<.+>",line) and not re.search(r"IPA",line) and not re.search(r"Rhymes:",line):
            
                rhymes = re.search(r"(?:\[\[.+?\]\])|(?:\{\{.+?\}\})",line.replace('*',''))

                if rhymes:
                    
                    temp_rhyme = line.replace('*','')
                    if re.search(r"\|",line):
                        temp_rhyme = re.sub(r"\{\{(?:.+?\|)+(.+?)\}\}",r"\1",temp_rhyme)
                        temp_rhyme = re.sub(r"\[\[(?:.+?\|)+(.+?)\]\]",r"\1",temp_rhyme)
                    temp_rhyme = re.sub(wiki_re," ",temp_rhyme, re.MULTILINE)
                    temp_rhyme = re.sub(extra_clear_re,"",temp_rhyme, re.MULTILINE)
                    temp_rhyme = re.sub(space_clear_re," ",temp_rhyme)
                    temp_rhyme = temp_rhyme.replace(" len","",re.MULTILINE)
                    temp_rhyme = re.sub(r"l ","",temp_rhyme, re.MULTILINE)
                    rhyme_page_content = rhyme_page_content + ", " + temp_rhyme
            
            elif (rhyme_page_end_re.search(line)):
                rhyme_page_flag = False
                rhyme_list_flag = False
                try:
                    rhyme_pronunciation = re.sub("\s+","",rhyme_pronunciation)
                    create_rhyme_entry= """INSERT INTO RhymeWords (Pronunciation, RhymesWith) VALUES (%s, %s);"""
                    rhyme_table_entry = (rhyme_pronunciation, rhyme_page_content)
                    result = await commit_sql(create_rhyme_entry, rhyme_table_entry)
                except mysql.connector.Error as error:
                    # await log_message("Error: " + str(error))
                    pass

            else:
                pass
    await send_message(message, "Word load complete! " + str(word_count) + " words loaded!")

    
async def admin_check(userid):
    if (userid != 610335542780887050) and (userid != 787355055333965844):
        await log_message(str(userid) + " tried to call an admin message!")
        return False
    else:
        return True
        
async def show_info(message, category):
    if category == 'literature':
        response = "***LITERATURE COMMANDS***\n\n`/savepost` -title *title* -perm *number* -post *post*: Save a post with the selected title to the database! Supports Discord formatting! Permission = 0 for only you can retrieve it, permissions = 1 for anyone to be able to retrieve it.\n`/getpost` *title*: Get a post with the selected title\n`/editpost` -title *original title* -newtitle *newtitle (optional)* -perm *0/1* -post *newpost (optional)* Update an existing post with new title, permissions and/or post content. Must be your post.\n`/deletepost` -title *title* Delete a post with that title. You must be the author to delete it.\n`/listmyposts`: Show the titlees of all posts you've created. You may only view your post titles.\n`/wordcount` *post* Get the number of words in the post.\n`/postag` *sentences* Attempt to tag each word with the correct part of speech in a sentence or sentences.\n`/chargen`: Randomly generate a modern human character. Fantasy characters, other timelines and the ability to select certain fields coming soon."

    elif category == 'dictionary':
        response = ">>> ***DICTIONARY AND THESAURUS COMMANDS***\n\n`/define` *word or phrase* Look in the dictionary database for a word definition.\n`/longdefine` *word or phrase*: Get the full definition of a word, or search here for foreign languages or rare words.\n`/definelike` *word or phrase*  Find words that contain the text and print their definitions.\n`/synonyms` *word or phrase* Get words that mean similarly to this word.\n`/antonyms` *word or phrase* Get words that mean the opposite of this word.\n`/rhymes` *word or phrase* Get words that rhyme with this one.\n`/advancedrhymes` *word or phrase*: Use WordNet to find rhyming words.\n`/sentences` *word or phrase* Use this word in a sentence.\n`/derivedterms` *word or phrase* See other words and phrases based on this one.\n`/slang` *word or phrase* Get the first definition on UrbanDictionary for this word.\n.`randomslang` *word or phrase* Get a random definition from UrbanDictionary for this word.\n"
    elif category == 'poetrytag':
        response = ">>> ***POETRY TAG COMMANDS***\n\n`/poetrytag` *user mentions* -topic *topic* -mode *mode*\nStart a poetry tag on your server. Mention the users participating, then specify a topic and mode. Any topic is valid, but specifiying *random* will pick a topic from the database. Valid modes are *tag*, where each poet writes an entire poem, and *tandem* where each poet writes one line.\n\n`/tag` *post* Submit your poem or line for poetry tag.\n\n`/finishtag` Stop the poetry tag and print the tandem poem if in tandem mode. Poems can be saved using .savepost.\n\n"
    elif category == 'quiz':
       response = ">>> ***QUIZ COMMANDS***\n\n`/quiz` *difficulty*\nGet a random definition from the database and the first one to answer with .answer *word or phrase* gets it right!\nDifficulty levels are easy, medium, hard and nightmare. The higher the difficulty, the more points it's worth, but answer incorrectly and lose those points, and yes, you can go negative!\n\n`/answer` *word or phrase* Answer a quiz question.\n\n`/hint` Get a hint for the quiz word.\n\n`/pass` End the quiz without losing points and see the answer.\n\n`/myscore` See your current score.\n\n`/leaderboard` See the current server scoreboard.\n\n"
    elif category == 'wordsearch':
        response = ">>> ***WORD SEARCH COMMANDS***\n\n`/randomword` *minimum score* Get a random word and definition from the dictionary. Specifiy the minimum word score, or leave it blank for any score.\n`/wordsearch` *start letter*    *number of letters between*   *end letter* Search the dictionary for words starting and ending with the specified letters and the specified number of letters in between.\n`/wordpattern` *pattern*\nFind all words with the specified pattern. Represent unknown lettters as underscores (_) and known letters with their letter.\n`/wordscore` *word or phrase* Get the calculated word score for the specified word in the dictionary.\n`/wordoftheday` Get a word of the day from the dictionary with a score higher than the set limit.\n`/setupwotd hh:mm #channelmention` Set up the word of the day to run at hh:mm (24 hour format, central time) in the mentioned channel."
    else:
        response = "`This is the Author-Maton bot, the writer help bot!`\n`Written by The Midnight#2400`\n\nType one of the following categories to see commands. To see a category, type `/info CATEGORY`, such as `/info dictionary`, to show those commands.\n\n`literature`: Commands for saving and loading posts, and word counts.\n`dictionary`: Dictionary and thesaurus commands.\n`poetrytag`: Commands for managing poetry tag, which allows users to write a poem together.\n`quiz`: Disabled due to Discord ToS.\n`wordsearch`: Commands to search the dictionary for various words.\n`/invite`: Show an invite for the bot.\n\n**SLASH COMMANDS**\n\nAuthor-Maton now has slash commands! The old commands will work as long as possible, but likely on April 30, 2021 they will cease to function. You may have to re-invite the bot with the new invite to see the slash commands. Please report any issues with slash commands on the support server."
 
    await message.channel.send(response)

    
@client.event
async def on_ready():
    global bot_log_channel
    global quiz_scores
    global quiz_event
    global poetry_tag_event
    global poetry_tag_users
    global poetry_tag_topic
    global poetry_tag_mode
    global quiz_difficulty
    global word_of_the_day_schedule
    global manager
    global ephemeral_messages
    global slash_commands
    
    
        
    commands = [{"name": 'sayhi', 'desc': 'Say hello.', 'options': [{}]},
    {"name": 'info', 'desc': 'Bot help.', 'options': [{'name': 'category', 'desc': 'Category for help'},]},
    {"name": 'help', 'desc': 'Bot help.', 'options': [{'name': 'category', 'desc': 'Category for help'},]},
    {"name": 'setupwotd', 'desc': 'Set up word of the day.', 'options': [{'name': 'time', 'desc': 'Time in central US time to post HH:MM.'}, {'name': 'channel', 'desc': 'Channel mention to post word of the day in'}]}]
    # {"name": 'writingprompt', 'desc': 'Load a writing prompt.', 'options': [{}]},
    # {"name": 'postag', 'desc': 'Tag the parts of speech in a sentence.', 'options': [{'name': 'sentence', 'desc': 'Sentence to tag.'},]},
    # {"name": 'advancedrhymes', 'desc': 'Find longer lists of rhymes.', 'options': [{'name': 'word', 'desc': 'Word to find rhymes for.'}]},
    # {"name": 'listmyposts', 'desc': 'List all your saved posts.', 'options': [{}]},
    # {"name": 'savepost', 'desc': 'Save your post.', 'options': [{'name': '-title', 'desc': 'Title of post.'}, {'name': '-perm', 'desc': 'Permission for the post (0/1)'}, {'name': '-post', 'desc': 'The content of the post'}]},
    # {"name": 'getpost', 'desc': 'Get your post.', 'options': [{'name': '-title', 'desc': 'Title of the post to retreive.'}]},
    # {"name": 'editpost', 'desc': 'Edit your post.', 'options': [{'name': '-title', 'desc': 'Title of post.'}, {'name': '-newtitle', 'desc': 'New title of the post'}, {'name': '-perm', 'desc': 'Permission for the post (0/1)'}, {'name': '-post', 'desc': 'The new content of the post'}]},
    # {"name": 'deletepost', 'desc': 'Delete your post.', 'options': [{'name': '-title', 'desc': 'Title of the post to delete.'}]},
    # {"name": 'rhymes', 'desc': 'Get rhymes for a word.', 'options': [{'name': 'word', 'desc': 'Word to find rhymes for.'}]},
    # {"name": 'define', 'desc': 'Define a word.', 'options': [{'name': 'word', 'desc': 'Word to define.'}]},
    # {"name": 'longdefine', 'desc': 'Word to get a longer definition for.', 'options': [{'name': 'word', 'desc': 'Word to define.'}]},
    # {"name": 'randomword', 'desc': 'Get a random word.', 'options': [{'name': 'minimumscore', 'desc': 'Minimum word score to search for.'}]},
    # {"name": 'definelike', 'desc': 'Find words with this in the definition.', 'options': [{'name': 'word', 'desc': 'Word to search for.'}]},
    # {"name": 'synonyms', 'desc': 'Find synonyms for this word.', 'options': [{'name': 'word', 'desc': 'Word to find synonyms for.'}]},
    # {"name": 'antonyms', 'desc': 'Find antonyms for this word.', 'options': [{'name': 'word', 'desc': 'Word to find antonyms for.'}]},
    # {"name": 'derivedterms', 'desc': 'Find terms derived from this word.', 'options': [{'name': 'word', 'desc': 'Word to find derived terms for.'}]},
    # {"name": 'randomslang', 'desc': 'Get a random Urban Dictionary definition for this word.', 'options': [{'name': 'word', 'desc': 'Word to search for.'}]},
    # {"name": 'sentences', 'desc': 'See this word in a sentence.', 'options': [{'name': 'word', 'desc': 'Word for sample sentences.'}]},
    # {"name": 'slang', 'desc': 'Get the first definition from Urbandictionary for a word.', 'options': [{'name': 'word', 'desc': 'Word to search for.'}]},
    # {"name": 'quiz', 'desc': 'Start a word quiz.', 'options': [{'name': 'difficulty', 'desc': 'easy, medium, hard, nightmare.'}]},
    # {"name": 'answer', 'desc': 'Answer a quiz.', 'options': [{'name': 'answer', 'desc': 'Your quiz answer.'}]},
    # {"name": 'pass', 'desc': 'Pass on the quiz with no score penalty.', 'options': [{}]},
    # {"name": 'myscore', 'desc': 'Check your cumulative quiz score.', 'options': [{}]},
    # {"name": 'leaderboard', 'desc': 'Show the quiz leaderboard.', 'options': [{}]},
    # {"name": 'hint', 'desc': 'Get a hint on the quiz.', 'options': [{}]},
    # {"name": 'wordcount', 'desc': 'Count the words in your post.', 'options': [{'name': 'post', 'desc': 'Post to count words in.'}]},
    # {"name": 'wordsearch', 'desc': 'Find words matching this pattern.', 'options': [{'name': 'startletter', 'desc': 'Starting letter.'}, {'name': 'numberofletters', 'desc': 'Number of letters between start and end.'}, {'name': 'endletter', 'desc': 'Ending letter'}]},
    # {"name": 'wordpattern', 'desc': 'Find words with this pattern.', 'options': [{'name': 'pattern', 'desc': 'Word pattern (see help).'}]},
    # {"name": 'etymology', 'desc': 'Show the etymology of a word.', 'options': [{'name': 'word', 'desc': 'Word to get etymology for.'}]},
    # {"name": 'wordscore', 'desc': 'Find words with this word score.', 'options': [{'name': 'score', 'desc': 'Word score to search for.'}]},
    # {"name": 'wotd', 'desc': 'Manually retreive a word of the day..', 'options': [{}]},
    # {"name": 'setupwotd', 'desc': 'Set up word of the day.', 'options': [{'name': 'time', 'desc': 'Time in central US time to post HH:MM.'}, {'name': 'channelmention', 'desc': 'Channel mention to post word of the day in'}]},
    # {"name": 'poetrytag', 'desc': 'Start a poetry tag.', 'options': [{'name': 'usermentions', 'desc': 'Users to include (Discord mentions).'}, {'name': '-topic', 'desc': 'Topic of the poem'}, {'name': '-mode', 'desc': 'Mode of poetry tag.'}]},
    # {"name": 'tag', 'desc': 'Submit your poetry line or poem.', 'options': [{'name': 'post', 'desc': 'Your submission.'}]},
    # {"name": 'finishtag', 'desc': 'Finish poetry tag.', 'options': [{}]},
    # {"name": 'translate', 'desc': 'Translate a word from English.', 'options': [{'name': 'language', 'desc': 'Name of the language to translate to'}, {'name': 'word', 'desc': 'Word to translate.'}]},
    # {"name": 'invite', 'desc': 'Show the invite link.', 'options': [{}]}
    # ]
    slash_commands = SlashCommands(client)
    # for command in commands:
        # slash_commands.new_slash_command(name=command["name"].lower(), description=command["desc"])
        # for option in command["options"]:
            # try:
                # option["name"]
            # except:
                # continue
            # print(str(option))
            
            # if option['name'] == 'channel':
                # slash_commands.add_channel_command_option(command_name=command["name"].lower(), option_name=option["name"].lower(), description=option["desc"], required=True)
            # else:
                # slash_commands.add_command_option(command_name=command["name"].lower(), option_name=option["name"].lower(), description=option["desc"], required=True)
        # slash_commands.add_global_slash_command(command_name=command["name"].lower())
        # await asyncio.sleep(3)
        
    
    
    await log_message("Logged in!")
    for guild in client.guilds:
        quiz_event[guild.id] = False
        poetry_tag_event[guild.id] = False
        word_of_the_day_schedule[guild.id] = { }
        already_posted[guild.id] = False
        ephemeral_messages[guild.id] = False
        
    records = await select_sql("""SELECT ServerId,ChannelId,Hour,Minute FROM WOTDSchedule;""")
    for row in records:
        word_of_the_day_schedule[int(row[0])] = {}
        word_of_the_day_schedule[int(row[0])]["ChannelId"] = int(row[1])
        word_of_the_day_schedule[int(row[0])]["Hour"] = int(row[2])
        word_of_the_day_schedule[int(row[0])]["Minute"] = int(row[3])
    await client.loop.create_task(word_of_the_day())
        

    
   
@client.event
async def on_guild_join(guild):
    global quiz_event
    global poetry_tag_event
    global word_of_the_day_schedule
    global ephemeral_messages
    
    ephemeral_messages[guild.id] = False
    await log_message("Joined guild " + guild.name)
    quiz_event[guild.id] = False
    poetry_tag_event[guild.id] = False
    word_of_the_day_schedule[guild.id] = { }
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
    global word_of_the_day_schedule
    global pos_translator
    global tag_translator
    global pronunciations    
    global pretentious_trans
    global ephemeral_messages
    global slash_commands
    
    if message.author == client.user:
        return
    if message.author.bot and message.author.id != 787355055333965844:
        return

            
    if message.content.startswith('.'):
        print("Message called.")

        command_string = message.content.split(' ')
        command = command_string[0].replace('.','')
        parsed_string = message.content.replace("." + command + " ","")
        username = message.author.name
        server_name = message.guild.name
        print("Command: " + command)
#        if not message.channel.nsfw and re.search(r"sayhi|info|help|initialize|savepost|getpost|deletepost|editpost|wordcount|define|definelike|reversedefine|synonyms|antonyms|rhymes|sentences|derivedterms|slang|randomslang|translate|poetrytag|tag|finishtag|quiz|answer|hint|pass|myscore|leaderboard|randomword|wordsearch|wordpattern|wordscore|wordoftheday",command, re.S | re.MULTILINE):
#            await send_message(message, "Author-Maton can only function in NSFW channels due to Discord TOS. Please try again in a NSFW channel!")
#            return
        if (command == 'sayhi'):
            await message.channel.send("Hello there, " + username + "!")
                
        elif (command == 'info' or command == 'help'):
            await show_info(message, parsed_string)
            
        elif (command == 'initialize'):
            if not await admin_check(message.author.id):
                await send_message("Admin command only!")
                return
            await send_message(message, "Dropping databases...")
                
            result = await execute_sql("""DROP TABLE IF EXISTS Literature; DROP TABLE IF EXISTS DictionaryDefs; DROP TABLE IF EXISTS Thesaurus; DROP TABLE IF EXISTS Rhyming; DROP TABLE IF EXISTS RhymeWords; DROP TABLE IF EXISTS SampleSentences; DROP TABLE IF EXISTS Etymology; DROP TABLE IF EXISTS DerivedWords; DROP TABLE IF EXISTS SeeAlsoThesaurus;""")
            if result:    
                await send_message(message, "Databases all cleared successfully.")
            else:    
                await send_message(message, "Database error!")   
                
            await send_message(message, "Creating databases...")
               
            result = await execute_sql("""CREATE TABLE Literature (Id int auto_increment, Title varchar(400), Author varchar(100), Permissions int, PostContent varchar(1900), PRIMARY KEY (Id));""")
            if not result:
                await send_message(message, "Database error creating Literature database!")
            
            result = await execute_sql("""CREATE TABLE DictionaryDefs (Id int auto_increment, Word varchar(300), PartOfSpeech varchar(30), Language varchar(70), Definitions LONGTEXT, Pronunciation varchar(100), PRIMARY KEY (Id));""")
            
            if not result:
                await send_message(message, "Database error creating DictionaryDefs database!")
                
            result = await execute_sql("""CREATE TABLE Thesaurus (Id int auto_increment, Word varchar(300), Synonyms LONGTEXT, Antonyms LONGTEXT, PRIMARY KEY (Id));""")
            if not result:
                await send_message(message, "Database error creating Thesaurus database!")
                
            result = await execute_sql("""CREATE TABLE Rhyming (Id int auto_increment, Word varchar(300), RhymesWith TEXT, PRIMARY KEY (Id));""")
            if not result:
                await send_message(message, "Database error creating Rhyming database!")
                
            result = await execute_sql("""CREATE TABLE RhymeWords (Id int auto_increment, Pronunciation varchar(500), RhymesWith TEXT, PRIMARY KEY (Id));""")
            if not result:
                await send_message(message, "Database error creating RhymeWords database!")
                
            result = await execute_sql("""CREATE TABLE SampleSentences (Id int auto_increment, Word varchar(300), Sentences LONGTEXT, PRIMARY KEY (Id));""")
            if not result:
                await send_message(message, "Database error creating SampleSentences database!")
              
            result = await execute_sql("""CREATE TABLE Etymology (Id int auto_increment, Word varchar(300), Etymology LONGTEXT, PRIMARY KEY (Id));""")
            if not result:
                await send_message(message, "Database error creating Etymology database!")
                
            result = await execute_sql("""CREATE TABLE DerivedWords (Id int auto_increment, Word varchar(300), DerivedTerms LONGTEXT, PRIMARY KEY (Id));""")
            if not result:
                await send_message(message, "Database error creating DerivedWords database!")
            result = await execute_sql("""CREATE TABLE SeeAlsoThesaurus (Id Int auto_increment, Word varchar(300), Synonyms LONGTEXT, Antonyms LONGTEXT, PRIMARY KEY (Id));""")
            if not result:
                await send_message(message, "Database error creating SeeAlso Database!")
                
            if result:    
                await send_message(message, "Database created successfully.")
        elif(command == 'writingprompt'):
            embed = discord.Embed(title="Writing Prompt",description=random.choice(writing_prompts))
            await message.channel.send(embed=embed)
            
            # records = await select_sql_prompt("""SELECT WritingPromptText FROM WritingPromptTexts ORDER BY RAND( ) LIMIT 1;""")
            # for row in records:
                # tokenized_prompt = str(row[0]).split(" ")

            # for token in tokenized_prompt:
                # await log_message("Token: " + token)
                # if re.search(r"-(.+?)-",token):
                    # search_term = re.sub(r"[^A-Za-z]","",token, re.S | re.MULTILINE)
                    # search_term = search_term.strip()
                    # await log_message("Search term: " + search_term)
                    # if (search_term == 'Characters'):
                        # search_term_2 = search_term
                    # else:
                        # search_term_2 = search_term.replace("s","")
                    # get_blank = """SELECT """ + search_term_2 + """ FROM """ + search_term + """ ORDER BY RAND( ) LIMIT 1;"""
                    # blank_records = await select_sql_prompt(get_blank)
                    # for blank_row in blank_records:
                        # response = response + " " + re.sub("[^A-Za-z\s/]","",str(blank_row),re.S)
                # else:
                    # response = response + " " + re.sub(r"[^A-Za-z\s/]","",str(token), re.S)
            # await send_message(message, "`WRITING PROMPT:`\n\n " + response)
        elif command == 'pretentious':
            if not parsed_string:
                await send_message(message, "I can't make nothing pretentious!")
                return
            # parsed_string = parsed_string.lower()
            # text = nltk.word_tokenize(parsed_string)
            # pos_tags = nltk.pos_tag(text)
            response = "**Pretentious version:**\n\n"
            # for word_tuple in pos_tags:
                
                # wordmax = 0
                # word = ""
                # if word_tuple[0] in stopwords.words('english'):
                    # word = word_tuple[0]
                # else:
                    # try:
                        # pos = pretentious_trans[word_tuple[1]]
                    # except:
                        # pos = None
                    
                    # synos = lesk(parsed_string, word_tuple[0])# wn.synsets(word_tuple[0], pos=pos)
                    # if synos:
                        # for lemma_ in synos.lemma_names():
                            # syns = wn.synsets(lemma_)
                            # for lemma in syns:
                                # if len(lemma.name().split(".")[0].replace('_',' ')) > wordmax:
                                    # wordmax = len(lemma.name().split(".")[0].replace('_',' '))
                                    # word = lemma.name().split(".")[0].replace('_',' ')
                    # else:
                        # word = word_tuple[0]
            words = parsed_string.split(" ")
            for word in words:
                if word in stopwords.words('english'):
                    final_word = word
                else:
                    get_synonym_entry = """SELECT Synonyms FROM Thesaurus WHERE Word=%s;"""
                    records = await select_sql(get_synonym_entry, (word,))
                    wordmax = 0
                    final_word = word
                    syn_test = []
                    for row in records:
                        syn_test = row[0].split(',')
                    for syn in syn_test:
                        if len(syn) > wordmax:
                            final_word = syn
                            wordmax = len(syn)
                            
                response = response + " " + final_word

            await send_message(message, response)  
            
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
        elif (command == 'advancedrhymes'):
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
        elif command == 'serverlist':
            if not await admin_check(message.author.id):
                await send_message(message, "Nope.")
                return
            response = "`SERVER LIST`\n\n"
            server_list = []
            for guild in client.guilds:
                try:
                    if guild.name is not None:
                        server_list.append(guild.name)
                except:
                    pass
            for name in server_list:
                response = response + name + "\n"
            await send_message(message, response + "\nServer count: " + str(len(client.guilds)))
        elif command == 'servercount':
            if not await admin_check(message.author.id):
                await send_message(message, "Nope.")
                return
            await send_message(message, "Server count: " + str(len(client.guilds)))                
        elif command == "listmyposts":
            records = await select_sql("""SELECT Title FROM Literature WHERE Author=%s;""",(str(message.author.id),))
            if not records:
                await send_message(message, "You currently have not saved any posts.")
                return
            response = "**Your Saved Posts by Title:**\n\n"
            for row in records:
                response = response + row[0] + "\n"
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
                author = id=int(row[1])
                if (row[3] == 0 and message.author.id != int(row[1])):
                    await send_message(message, "This author has not granted permission for this post to be retrieved.")
                    return                        
                else:
                    await send_message(message, "`" + str(row[0]) + "`\nBy <@" + str(author) + ">\n\n" + row[2])
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
            get_rhyme_list = """SELECT RhymesWith FROM Rhyming WHERE Word=%s;"""
            get_rhyme_entry = """SELECT RhymesWith FROM RhymeWords WHERE Pronunciation IN (SELECT Pronunciation FROM DictionaryDefs WHERE Word=%s);"""
            get_rhyme_pro_list = False
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
            records = await select_sql(get_rhyme_list,(parsed_string,))
            response = "I found some words that rhyme with `" + parsed_string + "`:"
            rhymes = ""
            if records:
                for row in records:
                    if not (re.search(r"Category:",row) and re.search(r"English:",row)):
                        values = values + ", " + str(row[0]) + "\n\n"
                
            records = await select_sql(get_rhyme_entry, (parsed_string,))
            if not records and not values:
                await send_message(message,"I couldn't find any rhymes found for " + parsed_string + ".")
                return

            response = response + ","
            for row in records:
                values = values + " " + str(row[0]) + "\n\n"
            rhyme_set = set(values.split(','))
            for rhyme in rhyme_set:
                response = response + rhyme + ","
                response = response.replace(' ,  ',', ')
                response = response.replace(' , ','')
            await send_message(message, response)
        elif (command == 'define'):
            if parsed_string == "":
                await send_message(message, "No word specified!")
                return
            syns = wn.synsets(parsed_string)
            if not syns:
                get_dictionary_entry = """SELECT DISTINCT Language,PartOfSpeech,Definitions FROM DictionaryDefs WHERE Word=%s AND Definitions !=' ' AND Definitions IS NOT NULL;"""
                if (entry_limit > 0):
                    get_dictionary_entry = get_dictionary_entry.replace(";"," LIMIT " + str(entry_limit) + ";")
                async with message.channel.typing():
                    records = await select_sql(get_dictionary_entry, (parsed_string,))
                if not records:
                    await send_message(message, "No definitions found for " + parsed_string)
                    return
                response = "`" + parsed_string + "`\n "
                for row in records:
                    language = row[0]
                    part_of_speech = row[1]
                    definitions = await clean_definition(row[2])

                    await log_message(definitions)
                    response = response + "`" + str(language) + "` *" + part_of_speech + "*  " + definitions + "\n"
                    
                await send_message(message, response)
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
                response = response + "\n" + pos_translator[part_of_speech] + ": " + parts_of_speech[part_of_speech]
            print("Ephemeral value for guild " + str(message.guild.id) + " is " + str(ephemeral_messages[message.guild.id]))    
            if ephemeral_messages[message.guild.id]:
                return response
            else:
                await message.channel.send(embed=embed)            
        elif (command == 'longdefine'):
            if parsed_string == "":
                await send_message(message, "No word specified!")
                return
            get_dictionary_entry = """SELECT DISTINCT Language,PartOfSpeech,Definitions FROM DictionaryDefs WHERE Word=%s AND Definitions !=' ' AND Definitions IS NOT NULL;"""
            if (entry_limit > 0):
                get_dictionary_entry = get_dictionary_entry.replace(";"," LIMIT " + str(entry_limit) + ";")
            async with message.channel.typing():
                records = await select_sql(get_dictionary_entry, (parsed_string,))
            if not records:
                await send_message(message, "No definitions found for " + parsed_string)
                return
            response = "`" + parsed_string + "`\n "
            for row in records:
                language = row[0]
                part_of_speech = row[1]
                definitions = await clean_definition(row[2])

                await log_message(definitions)
                response = response + "`" + str(language) + "` *" + part_of_speech + "*  " + definitions + "\n"
                
            await send_message(message, response)
        elif (command == 'randomword'):
            if not parsed_string:
                parsed_string = "0"
            acceptable_word = False
            get_word_of_the_day = """SELECT Word FROM WordValues WHERE WordValue>=%s ORDER BY RAND( ) LIMIT 1;"""
            get_word_based_on_score = """SELECT Word,PartOfSpeech,Definitions FROM DictionaryDefs WHERE Word=%s;"""
            async with message.channel.typing():
                while not acceptable_word:
                    records = await select_sql(get_word_of_the_day,(parsed_string,))
                    for row in records:
                        word = row[0]
                    
                    records = await select_sql(get_word_based_on_score, (word,))
                    for row in records:
                        if not re.search(r"plural|singular|past|future|^\s*\*.+\*\s*$|(?:\s*\*.+\*[;\.])+", row[2], re.S | re.MULTILINE | re.IGNORECASE):
                            acceptable_word = True
                response = "`Random word:`\n\n`"
                for row in records:
                    definitions = await clean_definition(row[2])
                    response = response + str(row[0]) + "` *" + row[1] + "*\n\n" + definitions + "\n\n"
                    
                    await send_message(message, response)
                            

        elif (command == 'definelike'):

            parsed_string = "%" + parsed_string + "%"
            if parsed_string == "":
                await send_message(message, "No word specified!")
                return
            get_dictionary_entry = """SELECT DISTINCT Word,PartOfSpeech,Definitions FROM DictionaryDefs WHERE Word LIKE %s;"""
            if (entry_limit > 0):
                get_dictionary_entry = get_dictionary_entry.replace(";"," LIMIT " + str(entry_limit) + ";")
            async with message.channel.typing():
                records = await select_sql(get_dictionary_entry, (parsed_string,))
            if not records:
                await send_message(message, "No words found that matched " + parsed_string.replace('%',''))
                return
            response = "`" + parsed_string.replace('%','') + "`\n\n"
            for row in records:
                definitions = await clean_definition(row[2])
                response = response + "`" + str(row[0]) + "` *" + row[1] + "* " + definitions + "\n\n"
            
            await send_message(message, response)
            
        elif (command == 'synonyms'):
            if parsed_string == "":
                await send_message(message, "No word specified!")
                return
            response = "`" + parsed_string + "` *Synonyms*\n\n "
            get_synonym_entry = """SELECT Synonyms FROM Thesaurus WHERE Word=%s;"""
            async with message.channel.typing():
                records = await select_sql(get_synonym_entry, (parsed_string,))
            if not records:
                see_also_records = await select_sql("""SELECT Synonyms FROM SeeAlsoThesaurus WHERE Word=%s;""", (parsed_string,))
                if not see_also_records:
                    word = parsed_string
                    output = subprocess.run(["/home/REDACTED/BotMaster/MyThes-1.0/thesaurus","/home/REDACTED/BotMaster/MyThes-1.0/th_en_US_new.idx","/home/REDACTED/BotMaster/MyThes-1.0/th_en_US_new.dat",word], universal_newlines=True, stdout=subprocess.PIPE)
                    for line in output.stdout.split('\n'):
                        if not re.search(r"meaning",line):
                            response = response + re.sub(r"^,","",re.sub(r",+",", ",re.sub(r"\s+",",",line, re.S)))
                            
                        else:
                            response = response + "\n`" + line + "`\n"

                    
                    await send_message(message, response)
                    return
                for row in see_also_records:
                    response = response + str(row[0]) + "\n\n"
            
            for row in records:
                response = response + str(row[0]) + "\n\n"
            if re.search(r"Thesaurus:.+ ,", response, re.MULTILINE | re.S | re.IGNORECASE):
                m = re.search(r"Thesaurus:(.+?) *?,.*", response.replace("*",""), re.MULTILINE | re.S | re.IGNORECASE)
                if m:
                    word = m.group(1)
                await log_message("See also: " + word)
                see_also_records = await select_sql("""SELECT Synonyms FROM SeeAlsoThesaurus WHERE Word=%s;""", (word,))
                more_syns = " "
                for also_record in see_also_records:
                    await log_message(str(also_record))
                    more_syns = more_syns + ", " + str(also_record)
                response = re.sub(r" .*?see.* Thesaurus:.+? ,",more_syns,response, re.MULTILINE | re.S | re.IGNORECASE)
            response = response.replace(" ws ","")
            word = parsed_string
            output = subprocess.run(["/home/REDACTED/BotMaster/MyThes-1.0/thesaurus","/home/REDACTED/BotMaster/MyThes-1.0/th_en_US_new.idx","/home/REDACTED/BotMaster/MyThes-1.0/th_en_US_new.dat",word], universal_newlines=True, stdout=subprocess.PIPE)

            for line in output.stdout.split('\n'):
                if not re.search(r"meaning",line):
                    response = response + re.sub(r"^,","",re.sub(r",+",", ",re.sub(r"\s+",", ",line, re.S)))
                else:
                    response = response + "\n`" + line + "`\n"
            response = re.sub(r"^\s+","",response)            
            await send_message(message, response)
           
        elif (command == 'antonyms'):
            if parsed_string == "":
                await send_message("No word specified!")
                return
            get_antonym_entry = """SELECT Antonyms FROM Thesaurus WHERE Word=%s;"""
            async with message.channel.typing():
                records = await select_sql(get_antonym_entry, (parsed_string,))
            if not records:
                await send_message(message, "No antonyms found for " + parsed_string)
                return
            response = "`" + parsed_string + "` *Antonyms*\n\n"
            for row in records:
                response = response + str(row[0]).replace('*','') + "\n\n"
            if re.search(r"Thesaurus:.+ ,", response, re.MULTILINE | re.S | re.IGNORECASE):
                m = re.search(r"Thesaurus:(.+?) *?,.*", response.replace("*",""), re.MULTILINE | re.S | re.IGNORECASE)
                if m:
                    word = m.group(1)
                await log_message("See also: " + word)
                async with message.channel.typing():
                    see_also_records = await select_sql("""SELECT Antonyms FROM SeeAlsoThesaurus WHERE Word=%s;""", (word,))
                more_syns = " "
                for also_record in see_also_records:
                    await log_message(str(also_record))
                    more_syns = more_syns + ", " + str(also_record)
                response = re.sub(r" .*?see.* Thesaurus:.+? ,",more_syns,response, re.MULTILINE | re.S | re.IGNORECASE)
            response = response.replace(" ws ","")
            await send_message(message, response)

        elif (command == 'derivedterms'):
            if parsed_string == "":
                await send_message(message, "No word specified!")
                return
            get_derived_entry = """SELECT DerivedTerms FROM DerivedWords WHERE Word=%s;"""
            async with message.channel.typing():
                records = await select_sql(get_derived_entry,(parsed_string,))
            if not records:
                await send_message(message,"No derived terms found for " + parsed_string)
                return
            response = "`" + parsed_string + "` *Derived Terms*\n\n"
            for row in records:
                response = response + str(row[0]) + "\n\n"
            response = response.replace('rel-bottom','')
            response = response.replace('rel-top','')
            response = response.replace('rel-mid','')
            response = re.sub(r"\d+[,|]","", response)
            response = response.replace(', ,','')
            response = response.replace("|","")

            await send_message(message, response)    

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
                if definition:
                    await send_message(message, "`" + word + "`\n\n" + definition)
                else:
                    await send_message(message, "No definition found for " + word + ".")
            else:
                await send_message(message, "This is not a NSFW channel. Please issue slang commands in a NSFW channel.")
        elif (command == 'sentences'):

            get_sentences = """SELECT Sentences FROM SampleSentences WHERE Word=%s;"""
            async with message.channel.typing():
                records = await select_sql(get_sentences, (parsed_string,))

            if not records:
                await send_message(message, "No sample sentences found for " + parsed_string)
                return
            response = "`" + parsed_string + "` *Used in a sentence*\n\n-  "
            for row in records:
                response = response + str(row[0]) + "\n\n"
            response = response.replace(';','\n-  ')
            response = response.replace("ux en","")
            
            await send_message(message, response)

                
        elif (command == 'slang'):
            if(message.channel.nsfw):
                word = message.content.replace(".slang ","")
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
                if definition:
                    await send_message(message, "`" + word + "`\n\n" + definition)
                else:
                    await send_message(message, "No definition found for " + word + ".")
            else:
                await send_message(message, "This is not a NSFW channel. Please issue slang commands in a NSFW channel.")            
 
        elif (command == 'quiz'):
            parsed_string = message.content.replace(".quiz ","")
            get_wordscore = " "
            quiz_difficulty[message.guild.id] = parsed_string
            quiz_event[message.guild.id] = True
            if parsed_string == 'easy':
                get_wordscore = """SELECT Word FROM WordValues WHERE WordValue<=50 ORDER BY RAND( ) LIMIT 1;"""
            elif parsed_string == 'medium':
                get_wordscore = """SELECT Word FROM WordValues WHERE WordValue>=51 AND WordValue<=150 ORDER BY RAND( ) LIMIT 1;"""
            elif parsed_string == 'hard':
                get_wordscore = """SELECT Word FROM WordValues WHERE WordValue>=151 AND WordValue<=300 ORDER BY RAND( ) LIMIT 1;"""
            elif parsed_string == 'nightmare':
                get_wordscore = """SELECT Word FROM WordValues WHERE WordValue>=301 ORDER BY RAND( ) LIMIT 1;"""
            else:
                get_wordscore = """SELECT Word FROM WordValues ORDER BY RAND( ) LIMIT 1;"""
                
            async with message.channel.typing():
                acceptable_word = False
                while not acceptable_word:
                    word_record = await select_sql(get_wordscore)
                    for row in word_record:
                        word = row[0]
                    get_dictionary_entry = """SELECT Word,PartOfSpeech,Definitions FROM DictionaryDefs WHERE Word=%s;"""
                    
                    records = await select_sql(get_dictionary_entry, (word,))
                    for row in records:
                        if not re.search(r"plural|singular|past|future|(^\s*\*.+\*\s*$)|(^(?:\s*\*.+\*;\s*)+$)|archaic|obsolete", row[2], re.S | re.MULTILINE | re.IGNORECASE):
                            acceptable_word = True
                part_of_speech = " "
                question = " "
                response = "What word is a "
                for row in records:
                    question = await clean_definition(row[2])
                    part_of_speech = row[1]
                quiz_answer[message.guild.id] = row[0]
                response = response + part_of_speech + " and means " + question.lower().replace(quiz_answer[message.guild.id],"----")
            await send_message(message, response)

        elif (command == 'answer'):

            quiz_score = 0
            if not quiz_event[message.guild.id]:
                await send_message(message, "No quiz currently active! Type `.quiz` to start a word quiz.\n")
                return  
            id_num = message.author.id
            guild_id = message.guild.id
            get_current_score = """SELECT Score FROM QuizScores WHERE ServerId=%s AND UserId=%s;"""
            records = await select_sql(get_current_score, (str(guild_id), str(id_num)))
            if not records:
                create_score_entry = """INSERT INTO QuizScores (ServerId, UserId, Score) VALUES(%s, %s, %s);"""   
                score_entry = (str(message.guild.id), str(message.author.id), str(0))
                result = await commit_sql(create_score_entry, score_entry)
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
                    
                await send_message(message, "Your new quiz score is `"  + str(quiz_score) + "`.")
  
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
                    
                await send_message(message, "Your new quiz score is `"  + str(quiz_score) + "`.")
  
                update_score_entry = """UPDATE QuizScores Set Score=%s WHERE ServerId=%s AND UserId=%s;"""   
                score_entry = (str(quiz_score), str(guild_id), str(id_num))

                result = await commit_sql(update_score_entry, score_entry)
            quiz_event[message.guild.id] = False
            quiz_answer[message.guild.id] = " "
        elif (command == 'pass'):
            if not quiz_event[message.guild.id]:
                await send_message(message, "No quiz currently active! Type `.quiz` to start a word quiz.\n")
                return 
            quiz_event[message.guild.id] = False
            await send_message(message, "Passing on this question. No points deducted!\nThe answer was `" + str(quiz_answer[message.guild.id]) + "`.")
        elif (command == 'myscore'):
            my_id = message.author.id
            guild_id = message.guild.id
            get_my_score = """SELECT Score FROM QuizScores WHERE ServerId=%s AND UserId=%s;"""
            async with message.channel.typing():
                records = await select_sql(get_my_score, (str(guild_id), str(my_id)))
            if not records:
                result = await commit_sql("""INSERT INTO QuizScores (ServerId, UserId, Score) VALUES (%s, %s, 0);""",(str(message.guild.id),str(message.author.id)))
                if result:
                    await send_message(message, "This is your first time checking your quiz score, so I've created an entry for you with a starting score of 0. Use `.quiz` to try a word quiz!")
                    return
                else:
                    await send_message(message, "Database error!")
                    return
            response = "Your current quiz score is `"
            for row in records:
                score = str(row[0])
            response = response + score + "`."
            await send_message(message, response)
        elif (command == 'leaderboard'):
            get_leaderboard = """SELECT UserId,Score FROM QuizScores WHERE ServerId=%s ORDER BY Score DESC;"""
            guild_id = message.guild.id
            async with message.channel.typing():
                records = await select_sql(get_leaderboard, (str(guild_id),))

            response = "`Quiz Leaderboard:`\n\n"
            for row in records:
                try:
                    username = await message.guild.fetch_member(int(row[0]))
                except:
                    continue
                if username:
                    response = response + str(username.name) + " - " + str(row[1]) + "\n"
            await send_message(message, response)
            
        elif (command == 'hint'):

            if not quiz_event[message.guild.id]:
                await send_message(message, "No quiz currently active! Type `.quiz` to start a word quiz.\n")
                return
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
            word_search_query = """SELECT Word FROM DictionaryDefs WHERE Word LIKE """ 

            word_pattern = start_letter
            for i in range(int(number_of_letters)):
                word_pattern = word_pattern + "_"
            word_pattern = word_pattern + end_letter
            word_search_query = word_search_query + """'""" + word_pattern + """' AND Language='English';"""
            if (entry_limit > 0):
                word_search_query = word_search_query.replace(";"," LIMIT " + str(entry_limit) + ";")            
            async with message.channel.typing():
                records = await select_sql(word_search_query)

            if not records:
                await send_message(message, "No words found for the specified patern.")
                return
            response = "`Words that start with " + start_letter + ", end with " +end_letter + ", with " + number_of_letters + " in between:`\n\n"
            for row in records:
                response = response + str(row[0]) + ", "
                
            await send_message(message, response)

        elif (command == 'wordpattern'):

            parsed_string = parsed_string.replace(" ","")
            parsed_string = parsed_string.replace("-","_")
            
            if not parsed_string:
                await send_message(message, "No pattern specified!")
                return
            
            word_pattern_query = """SELECT DISTINCT Word FROM DictionaryDefs WHERE Word LIKE '""" + parsed_string + """' and Language='English';"""
            if (entry_limit > 0):
                word_pattern_query = word_pattern_query.replace(";"," LIMIT " + str(entry_limit) + ";")
            async with message.channel.typing():
                records = await select_sql(word_pattern_query)

            if not records:
                await send_message(message, "No words found for the specified patern.")
                return
            response = "`Words that have the pattern " + parsed_string + ":`\n\n"
            for row in records:
                response = response + str(row[0]) + ", "
                
            await send_message(message, response)
            
        elif (command == 'etymology'):

            get_etymology = """SELECT DISTINCT Etymology FROM Etymology WHERE Word=%s;"""
            if not parsed_string:
                await send_message(message, "No word specified!")
                return
            async with message.channel.typing():
                records = await select_sql(get_etymology, (parsed_string,))

            if not records:
                await send_message(message, "No etymology found for the specified word.")
                return
            response = "`ETYMOLOGY`\n\n*" + parsed_string + "*\n\n"
            for row in records:
                response = response + str(row[0]) + "; "
             
            await send_message(message, response)

        if (command == 'synonym'):
            word = command_string[1]
            output = subprocess.run(["/home/REDACTED/MyThes-1.0/thesaurus","/home/REDACTED/MyThes-1.0/th_en_US_new.idx","/home/REDACTED/MyThes-1.0/th_en_US_new.dat",word], universal_newlines=True, stdout=subprocess.PIPE)

            message_chunks = [output.stdout[i:i+1500] for i in range(0, len(output.stdout), 2000)]
            for chunk in message_chunks:
                await message.channel.send(">>> " + chunk)
                time.sleep(3)

            
        elif (command == 'wordscore'):

            get_word_score = """SELECT WordValue FROM WordValues WHERE Word=%s LIMIT 1;"""
            async with message.channel.typing():
                records = await select_sql(get_word_score, (parsed_string,))
            if not records:
                await send_message(message, "No score found for the specified word.")
                return
            response = "The word score of `" + parsed_string + "` is ```"
            for row in records:
                response = response + str(row[0]) + "```"
                
            await send_message(message, response)
        elif (command == 'setminscore'):
            if not await admin_check(message.author.id):
                await send_message(message, "Admin command only!")
                return
            word_of_the_day_score = int(message.content.replace('.setminscore ',""))
            await send_message(message, "Word of the day score minimum set to " + str(word_of_the_day_score))
            
        elif (command == 'wordoftheday' or command == 'wotd'):
            async with message.channel.typing():
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
        elif command == 'ephemeral':
            if ephemeral_messages[message.guild.id] == True:
                ephemeral_messages[message.guild.id] = False
            else:
                ephemeral_messages[message.guild.id] = True
            await send_message(message, "Ephemeral value changed.")
        elif (command == 'calculatevalues'):

            if not await admin_check(message.author.id):
                await send_message(message, "Admin command only!")
                return
            word_scores = {}   
            await send_message(message, "Calculating word values. Bot will be unavailable until word values calculated.")
            get_all_words_query = """SELECT Word,Definitions FROM DictionaryDefs WHERE Language='English';"""
            records = await select_sql(get_all_words_query)
            letter_values = { "E" : 1, "A" : 1, "I" : 1, "O" : 1, "N" : 1, "R" : 1, "T" : 1, "L" : 1, "S" : 1, "U" : 1, "D" : 2, "G" : 2, "B" : 3, "C" : 2, "M" : 3, "P" : 2, "F" : 4, "H" : 4, "V" : 4, "W" : 4, "Y" : 4, "K" : 5, "J" : 8, "X" : 8, "Q" : 10, "Z" : 10, "-": 0, " " : 0, "'": 0, "À": 1,"Â":1, "Ä":1, "È":1, "Ê":1, "Ì":1, "É":1, "Í":1, "Î":1, "Ò":1, "Ô":1, "Ó":1, "Õ":1, "Ø":1, "Ù":1, "Û":1, "Ü":1, "Ú": 1, "Ã": 1, "Ï": 1, "Ñ": 2, "Ç": 2, "Á": 1, ".":0, ":":0, ",":0, "`":0, "?":0, "Ö": 1, "Å": 1, "Ń": 2, "Ā": 1, "1": 1, "2": 1, "3":1, "4":1, "5":1, "6":1, "7":1, "8":1, "9":1, "0":1, "Æ": 2, "ʻ":0, "Œ":2, "/":0, "\\":0, "<": 0, ">":0, "ǃ":0, "Ū": 1, '*':0, '+':0, "Ł": 2, "Ź":10, "Č":2, "Ć": 2, "Ë": 1, "Α":1, '£':2, "Ể":1, '&': 0, ';':0, "Ō": 1, '!':0, "Ő":1, "Þ": 2, "Ð": 2, "Ș": 2, '♨':30, "Ộ": 1, "Ý": 1,"Þ": 1,"ß": 1,"Ă": 1,"Ą": 1,"Ć": 1,"Ĉ": 1,"Ċ": 1,"Č": 1,"Ď": 1,"Ē": 1,"Ĕ": 1,"Ė": 1,"Ę": 1,"Ě": 1,"Ĝ": 1,"Ġ": 1,"Ģ": 1,"Ĥ": 1,"Ħ": 1,"Ĩ": 1,"Ī": 1,"Ĭ": 1,"Į": 1,"İ": 1,"Ĳ": 1,"Ĵ": 1,"Ķ": 1,"Ĺ": 1,"Ļ": 1,"Ľ": 1,"Ŀ": 1,"Ł": 1,"Ń": 1,"Ņ": 1,"Ň": 1,"Ŋ": 1,"Ō": 1,"Ŏ": 1,"Ő": 1,"Œ": 1,"Ŕ": 1,"Ŗ": 1,"Ř": 1,"Ś": 1,"Ŝ": 1,"Ş": 1,"Š": 1,"Ţ": 1,"Ť": 1,"Ŧ": 1,"Ũ": 1,"Ū": 1,"Ŭ": 1,"Ů": 1,"Ű": 1,"Ų": 1,"Ŵ": 1,"Ŷ": 1,"Ÿ": 1,"Ż": 1,"Ź": 1,"Ž": 1,"Ɓ": 1,"Ƈ": 1,"Ƌ": 1,"Ə": 1,"Ƒ": 1,"Ɠ": 1,"Ɨ": 1,"Ɯ": 1,"Ɲ": 1,"Ɵ": 1,"Ƣ": 1,"Ƥ": 1,"Ʀ": 1,"Ƨ": 1,"Ʃ": 1,"ƪ": 1,"Ƭ": 1,"Ʈ": 1,"Ư": 1,"Ʊ": 1,"Ʋ": 1,"Ƴ": 1,"Ƶ": 1,"Ʒ": 1,"Ƹ": 1,"ƻ": 1,"Ƽ": 1,"ƾ": 1,"ƿ": 1,"ǀ": 1,"ǁ": 1,"ǂ": 1,"ǃ": 1,"Ǆ": 1,"ǅ": 1,"Ǉ": 1,"Ǌ": 1,"Ǎ": 1,"Ǐ": 1,"Ǒ": 1,"Ǔ": 1,"Ǖ": 1,"Ǘ": 1,"Ǚ": 1,"Ǜ": 1,"Ǟ": 1,"Ǡ": 1,"Ǣ": 1,"Ǥ": 1,"Ǧ": 1,"Ǩ": 1,"Ǫ": 1,"Ǭ": 1,"Ǯ": 1,"Ǳ": 1,"Ǵ": 1,"Ǻ": 1,"Ǽ": 1,"Ǿ": 1,"Ȁ": 1,"Ȃ": 1,"Ȅ": 1,"Ȇ": 1,"Ȉ": 1,"Ȋ": 1,"Ȍ": 1,"Ȏ": 1,"Ȑ": 1,"Ȓ": 1,"Ȕ": 1,"Ȗ": 1,"Ḁ": 1,"Ḃ": 1,"Ḅ": 1,"Ḇ": 1,"Ḉ": 1,"Ḋ": 1,"Ḍ": 1,"Ḏ": 1,"Ḑ": 1,"Ḓ": 1,"Ḕ": 1,"Ḗ": 1,"Ḙ": 1,"Ḛ": 1,"Ḝ": 1,"Ḟ": 1,"Ḡ": 1,"Ḣ": 1,"Ḥ": 1,"Ḧ": 1,"Ḩ": 1,"Ḫ": 1,"Ḭ": 1,"Ḯ": 1,"Ḱ": 1,"Ḳ": 1,"Ḵ": 1,"Ḷ": 1,"Ḹ": 1,"Ḻ": 1,"Ḽ": 1,"Ḿ": 1,"Ṁ": 1,"Ṃ": 1,"Ṅ": 1,"Ṇ": 1,"Ṉ": 1,"Ṋ": 1,"Ṍ": 1,"Ṏ": 1,"Ṑ": 1,"Ṓ": 1,"Ṕ": 1,"Ṗ": 1,"Ṙ": 1,"Ṛ": 1,"Ṝ": 1,"Ṟ": 1,"Ṡ": 1,"Ṣ": 1,"Ṥ": 1,"Ṧ": 1,"Ṩ": 1,"Ṫ": 1,"Ṭ": 1,"Ṯ": 1,"Ṱ": 1,"Ṳ": 1,"Ṵ": 1,"Ṷ": 1,"Ṹ": 1,"Ṻ": 1,"Ṽ": 1,"Ṿ": 1,"Ẁ": 1,"Ẃ": 1,"Ẅ": 1,"Ẇ": 1,"Ẉ": 1,"Ẋ": 1,"Ẍ": 1,"Ẏ": 1,"Ẑ": 1,"Ẓ": 1,"Ẕ": 1,"Ạ": 1,"Ả": 1,"Ấ": 1,"Ầ": 1,"Ẩ": 1,"Ẫ": 1,"Ậ": 1,"Ắ": 1,"Ằ": 1,"Ẳ": 1,"Ẵ": 1,"Ặ": 1,"Ẹ": 1,"Ẻ": 1,"Ẽ": 1,"Ế": 1,"Ề": 1,"Ể": 1,"Ễ": 1,"Ệ": 1,"Ỉ": 1,"Ị": 1,"Ọ": 1,"Ỏ": 1,"Ố": 1,"Ồ": 1,"Ổ": 1,"Ỗ": 1,"Ộ": 1,"Ớ": 1,"Ờ": 1,"Ở": 1,"Ỡ": 1,"Ợ": 1,"Ụ": 1,"Ủ": 1,"Ứ": 1,"Ừ": 1,"Ự": 1,"Ỳ": 1,"Ỵ": 1,"Ỷ": 1,"Ỹ": 1,"Ữ": 1, "$": 0, "#": 0, "%": 0, "^":0, "(": 0, ")":0, "_":0, "=":0, "+":0, "@":0, "~":0, ",":0, '"':0, "|":0, '³':0, 'ʼ': 0, '℞': 0, "Σ": 2 }
             
            for row in records:
                await log_message("Processing " + str(row[0]) + "...")
                acceptable_word = True
                parsed_definition = row[1]
                possible_word = row[0].strip()
                multiple_definitions = parsed_definition.split(";")
                first_definition = multiple_definitions[0]
                tokenized_definition = first_definition.split(" ")
                for token in tokenized_definition:
                    
                    if re.search("singular|plural|past|future|relating",token, re.IGNORECASE):
                        acceptable_word = False
                        await log_message("Skipping " + possible_word + "...")
                if acceptable_word:
                    length_score = len(str(row[0]))
                    letter_score = 0
                    for x in str(row[0]).upper():
                        if x in letter_values:
                            letter_score = letter_score + letter_values[x]
                        else:
                            pass
                    word_scores[str(row[0])] = letter_score * length_score
                    await log_message("Word score: " + str(word_scores[str(row[0])]))

            create_word_value_table = """CREATE TABLE WordValues (Word varchar(300), WordValue Int);"""
            result = await execute_sql(create_word_value_table)
            if not result:
                await log_message("Database error!")
                pass

            create_word_value_entry = """INSERT INTO WordValues (Word, WordValue) VALUES (%s, %s);"""
            for word in word_scores:
                word_value_entry = (word, word_scores[word])
                result = await commit_sql(create_word_value_entry, word_value_entry)
                if not result:
                    await log_message("Database error!")
                    pass
        elif (command == 'setentrylimit'):
            if not await admin_check(message.author.id):
                await send_message(message, "Admin command only!")
                return
            entry_limit = int(command_string[1])
            await send_message(message, "Entry limit set to " + str(entry_limit) + ".")
            
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
            await send_message(message, "Poetry tag event started with topic of `" + str(topic) + "` in mode `" + str(mode) + "`")
            if re.search('tag', mode):
                await send_message(message, "<@" + str(users[0].id) + ">, you are first! Type .tag and your poem!")
            if re.search('tandem', mode):
                await send_message(message, "<@" + str(users[0].id) + ">, you are first! Type .tag and your line!")
                poetry_tag_tandem_poem[message.guild.id] = " "
            poetry_tag_current_user[message.guild.id] = 0
        elif command == 'chargen':


            height_min_feet = 4
            height_max_feet = 6
            height_inches_max = 11
            weight_min = 90
            weight_max = 250
            age_min = 18
            age_max = 90
            age = random.randint(age_min, age_max)
            gender_picker = random.randint(1, 20)
            if gender_picker >= 1 and gender_picker <= 10:
                gender = "Male"
            elif gender_picker >= 11 and gender_picker <= 20:
                gender = "Female"


            if gender == 'Male':
                records = await select_sql("""SELECT FirstName FROM FirstNames WHERE Gender='Male' ORDER BY RAND ( ) LIMIT 1;""")
                for row in records:
                    first_name = row[0]
            elif gender == 'Female':
                records = await select_sql("""SELECT FirstName FROM FirstNames WHERE Gender='Female' ORDER BY RAND ( ) LIMIT 1;""")
                for row in records:
                    first_name = row[0]
            
            records = await select_sql("""SELECT LastName FROM LastNames ORDER BY RAND ( ) LIMIT 1;""")
            for row in records:
                last_name = row[0]
                


            # race = random.choice(race_list)
            records = await select_sql("""SELECT Occupation FROM Occupations WHERE Genre='Modern' ORDER BY RAND ( ) LIMIT 1;""")
            for row in records:
                occupation = row[0]
                
            # occupation = random.choice(occupation_list)

            # if race == 'Human':
                # age = random.randint(18, 100)
            # else:
                # age = random.randint(age_min, age_max)

#            origin = random.choice(origin_list)
            height_feet = random.randint(height_min_feet, height_max_feet)
            height_inches = random.randint(0, 11)
            weight = random.randint(weight_min, weight_max)

            # number_of_strengths = random.randint(1, 5)
            # strengths = ""
            # for x in range(0, number_of_strengths):
                # strengths = strengths + random.choice(strengths_list) + ", "
            number_of_weaknesses = random.randint(1, 5)
            records = await select_sql("""SELECT Weakness FROM Weaknesses WHERE Genre='All' ORDER BY RAND ( ) LIMIT """ + str(number_of_weaknesses) + """;""")
            weaknesses = ""
            for row in records:
                weaknesses = weaknesses + row[0] + ", "
            # powers = ""

            # number_of_powers = random.randint(1, 3)
            # for x in range(0, number_of_powers):
                # powers = powers + random.choice(powers_list) + ", "
            number_of_skills = random.randint(1, 5)
            skills = ""
            records = await select_sql("""SELECT Skill FROM Skills WHERE Genre='All' ORDER BY RAND ( ) LIMIT """ + str(number_of_skills) + """;""")

            for row in records:
                skills = skills + row[0].capitalize() + ", "            

            personality = ""
            number_of_personality = random.randint(2, 8)
            records = await select_sql("""SELECT Trait FROM Traits ORDER BY RAND ( ) LIMIT """ + str(number_of_personality) + """;""")
            
            for row in records:
                personality = personality + row[0] + ", "

            records = await select_sql("""SELECT Color FROM HairColors WHERE Human=1 ORDER BY RAND ( ) LIMIT 1;""")
            for row in records:
                hair_color = row[0]
            records = await select_sql("""SELECT Color FROM EyeColors WHERE Human=1 ORDER BY RAND ( ) LIMIT 1;""")
            for row in records:
                eye_color = row[0]            

            records = await select_sql("""SELECT Orientation FROM Orientations ORDER BY RAND ( ) LIMIT 1;""")
            for row in records:
                orientation = row[0]
                
            records = await select_sql("""SELECT Nationality FROM Nationalities ORDER BY RAND ( ) LIMIT 1;""")
            for row in records:
                nationality = row[0]                

            records = await select_sql("""SELECT Ethnicity FROM Ethnicities ORDER BY RAND ( ) LIMIT 1;""")
            for row in records:
                ethnicity = row[0] 
            records = await select_sql("""SELECT Status FROM FamilyStatus ORDER BY RAND ( ) LIMIT 1;""")
            for row in records:
                fam = row[0]                
            embed = discord.Embed(title="New Random Character")
            embed.add_field(name="Name:",value=first_name + " " + last_name)
            embed.add_field(name="Age:",value=str(age))
            embed.add_field(name="Gender:",value=gender)
            embed.add_field(name="Orientation:",value=orientation)
            embed.add_field(name="Height:",value=str(height_feet) + "'" + str(height_inches) + '"')
            
            embed.add_field(name="Weight:", value=str(weight) + " lbs")
            embed.add_field(name="Hair color:",value=hair_color)
            embed.add_field(name="Eye color:",value=eye_color)
            embed.add_field(name="Ethnicity:",value=ethnicity)
            embed.add_field(name="Nationality:",value=nationality)
            embed.add_field(name="Pesonality traits:",value=personality)
            embed.add_field(name="Skills:",value=skills)
            embed.add_field(name="Weakneses:",value=weaknesses)
            embed.add_field(name="Occupation:",value=occupation)
            embed.add_field(name="Family Status:",value=fam)
            
            


            # await reply_message(message, response)
            await message.channel.send(embed=embed)            
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
        elif (command == 'loadwords'):
            if not await admin_check(message.author.id):
                await send_message(message, "Admin command only!")
                return
            await send_message(message, "Starting dictionary database load...\nBot will be available until complete, but not all functions will work.")
            await load_words(message)
        elif (command == 'loadwritingprompts'):
            if not admin_check(message.author.id):
                send_message(message, "Admin command only!")
                return        
            send_message(message, "Starting dictionary database load...\nBot will be unavailable until complete.")
            writing_file = "/home/REDACTED/writingprompttexts.txt"
            characters_file = "/home/REDACTED/characters.txt"
            places_file = "/home/REDACTED/places.txt"
            timeperiods_file = "/home/REDACTED/timeperiods.txt"
            objects_file = "/home/REDACTED/objects.txt"
            adjectives_file = "/home/REDACTED/adjectives.txt"
            actions_file = "/home/REDACTED/actions.txt"
            genders_file = "/home/REDACTED/genders.txt"
            occupations_file = "/home/REDACTED/occupations.txt"
            id = 1
            f = open(occupations_file, 'r')
            for line in f:
                line = line.strip()
                id = id + 1
                try:

                    connection = mysql.connector.connect(host='localhost', database='WritingPrompts', user='REDACTED', password='REDACTED')    
                    create_entry = """INSERT INTO Occupations (Id, Occupation) VALUES(%s, %s);"""
                    cursor = connection.cursor()
                    result = cursor.execute(create_entry, (id, line))
                    connection.commit()
                except mysql.connector.Error as error:
                    await message.channel.send("Database error! " + str(error))   
                finally:
                    if(connection.is_connected()):
                        cursor.close()
                        connection.close()
            f = open(writing_file, 'r')
            for line in f:
                line = line.strip()
                id = id + 1
                try:

                    connection = mysql.connector.connect(host='localhost', database='WritingPrompts', user='REDACTED', password='REDACTED')    
                    create_entry = """INSERT INTO WritingPromptTexts (Id, WritingPromptText) VALUES(%s, %s);"""
                    cursor = connection.cursor()
                    result = cursor.execute(create_entry, (id, line))
                    connection.commit()
                except mysql.connector.Error as error:
                    await message.channel.send("Database error! " + str(error))   
                finally:
                    if(connection.is_connected()):
                        cursor.close()
                        connection.close()
            f = open(characters_file, 'r')
            for line in f:
                line = line.strip()
                id = id + 1
                try:

                    connection = mysql.connector.connect(host='localhost', database='WritingPrompts', user='REDACTED', password='REDACTED')    
                    create_entry = """INSERT INTO Characters (Id, Characters) VALUES(%s, %s);"""
                    cursor = connection.cursor()
                    result = cursor.execute(create_entry, (id, line))
                    connection.commit()
                except mysql.connector.Error as error:
                    await message.channel.send("Database error! " + str(error))   
                finally:
                    if(connection.is_connected()):
                        cursor.close()
                        connection.close()
            f = open(places_file, 'r')
            for line in f:
                line = line.strip()
                id = id + 1
                try:

                    connection = mysql.connector.connect(host='localhost', database='WritingPrompts', user='REDACTED', password='REDACTED')    
                    create_entry = """INSERT INTO Places (Id, Place) VALUES(%s, %s);"""
                    cursor = connection.cursor()
                    result = cursor.execute(create_entry, (id, line))
                    connection.commit()
                except mysql.connector.Error as error:
                    await message.channel.send("Database error! " + str(error))   
                finally:
                    if(connection.is_connected()):
                        cursor.close()
                        connection.close() 
            f = open(timeperiods_file, 'r')
            for line in f:
                line = line.strip()
                id = id + 1
                try:

                    connection = mysql.connector.connect(host='localhost', database='WritingPrompts', user='REDACTED', password='REDACTED')    
                    create_entry = """INSERT INTO TimePeriods (Id, TimePeriod) VALUES(%s, %s);"""
                    cursor = connection.cursor()
                    result = cursor.execute(create_entry, (id, line))
                    connection.commit()
                except mysql.connector.Error as error:
                    await message.channel.send("Database error! " + str(error))   
                finally:
                    if(connection.is_connected()):
                        cursor.close()
                        connection.close()
            f = open(objects_file, 'r')
            for line in f:
                line = line.strip()
                id = id + 1
                try:

                    connection = mysql.connector.connect(host='localhost', database='WritingPrompts', user='REDACTED', password='REDACTED')    
                    create_entry = """INSERT INTO Objects (Id, Object) VALUES(%s, %s);"""
                    cursor = connection.cursor()
                    result = cursor.execute(create_entry, (id, line))
                    connection.commit()
                except mysql.connector.Error as error:
                    await message.channel.send("Database error! " + str(error))   
                finally:
                    if(connection.is_connected()):
                        cursor.close()
                        connection.close()                         
            f = open(adjectives_file, 'r')
            for line in f:
                line = line.strip()
                id = id + 1
                try:

                    connection = mysql.connector.connect(host='localhost', database='WritingPrompts', user='REDACTED', password='REDACTED')    
                    create_entry = """INSERT INTO Adjectives (Id, Adjective) VALUES(%s, %s);"""
                    cursor = connection.cursor()
                    result = cursor.execute(create_entry, (id, line))
                    connection.commit()
                except mysql.connector.Error as error:
                    await message.channel.send("Database error! " + str(error))   
                finally:
                    if(connection.is_connected()):
                        cursor.close()
                        connection.close() 
            f = open(actions_file, 'r')
            for line in f:
                line = line.strip()
                id = id + 1
                try:

                    connection = mysql.connector.connect(host='localhost', database='WritingPrompts', user='REDACTED', password='REDACTED')    
                    create_entry = """INSERT INTO Actions (Id, Action) VALUES(%s, %s);"""
                    cursor = connection.cursor()
                    result = cursor.execute(create_entry, (id, line))
                    connection.commit()
                except mysql.connector.Error as error:
                    await message.channel.send("Database error! " + str(error))   
                finally:
                    if(connection.is_connected()):
                        cursor.close()
                        connection.close()
            send_message(message, "Completed!")            
        elif (command == 'reversedefine'):

            parsed_string = message.content.replace(".reversedefine ","")
            
            get_definitions = "SELECT DISTINCT Word,PartOfSpeech,Language,Definitions FROM DictionaryDefs WHERE (Language='English' AND Definitions LIKE '% " + parsed_string + " %');"
            async with message.channel.typing():
                records = await select_sql(get_definitions)
            response = "*Definitions containing* `" + parsed_string + "`\n"
            if not records:
                await send_message(message, "No definitions found for " + parsed_string + ".")
                return
            for row in records:
                response = response + "`" + row[0] + "` *" + row[1] + "* (" + row[2] + ") " + row[3] + "\n" 
            await send_message(message, response)
        elif (command == 'translate'):
            translate_re = re.compile("""(?P<language>.+?) (?P<translate>.*)""",re.I)
            m = translate_re.search(parsed_string)
            if m:
                language = m.group('language')
                translate = m.group('translate')
            if not language or not translate:
                await send_message(message, "You did not specify a language or word.")
                return

            get_translation = "SELECT DISTINCT Word,PartOfSpeech,Language,Definitions FROM DictionaryDefs WHERE (Language=%s AND Definitions LIKE '% " + translate + " %') OR (Language=%s AND Definitions LIKE '" + translate + "%') OR (Language=%s AND Definitions=%s);"
            translation_term = (language, language, language, translate)
            records = await select_sql(get_translation, translation_term)
            response = "`" + translate + "` *Translated to " + language + "*\n\n"
            if not records:
                await send_message(message, "No translation found in " + language + " for " + translate + ".")
                return
            for row in records:
                response = response + "`" + row[0] + "` *" + row[1] + "* (" + row[2] + ") " + row[3] + "\n"
            await send_message(message, response)
        elif (command == 'loadkazen'):
            if not await admin_check(message.author.id):
                await send_message(message, "Nope.")
                return        
            await send_message(message, "Loading Kazenperia...")
            xml_file = "/home/REDACTED/BotMaster/kazen.csv"
    
            f = open(xml_file, 'r')
            for line in f:
                tokens = re.sub(r"\(.*\)","",line)
                tokens = tokens.split(',')
                kazen_word = tokens[len(tokens) - 1].strip()
                enter_kazen = "INSERT INTO DictionaryDefs (Word,PartOfSpeech,Language,Definitions) VALUES (%s, 'unknown', 'Kazenperia', %s);"
                kazen_entry = (kazen_word, line.replace(",",";").replace(kazen_word,""))
                result = await commit_sql(enter_kazen, kazen_entry)
            await send_message(message,"Complete!")
        elif command == 'invite':
            await send_message(message, "Click here to invite Author-Maton: https://discord.com/api/oauth2/authorize?client_id=680938420708835356&permissions=2147503104&scope=bot%20applications.commands")
        else:
            pass
    else:
        pass
        
    
@client.event
async def on_interaction(member, interaction):
    global command_handler
    global slash_commands
    print("called here" + str(interaction))
    slash_commands.convert_to_message(interaction, member, ".") 



client.run('REDACTED')  


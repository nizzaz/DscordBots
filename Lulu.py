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

intents = discord.Intents(messages=True,guilds=True, message_content=True)

class NakedObject(object):
    pass

# GIFs
poop_gifs = ["https://tenor.com/view/elmo-poop-potty-gif-15791533","https://tenor.com/view/pooping-toilet-sitting-on-the-gif-13533764","https://tenor.com/view/good-job-pooping-baby-dog-lol-gif-14189744","https://tenor.com/view/baby-yoda-gif-18489483","https://tenor.com/view/unicorn-ice-cream-cone-poopie-rainbow-gif-5167287","https://tenor.com/view/shitty-shit-poop-queen-blushing-gif-15272159","https://tenor.com/view/i-pooped-pooped-myself-crapped-my-pants-scared-gif-18985399","https://tenor.com/view/monkey-when-you-poop-dancing-dance-moves-gif-16383385","https://tenor.com/view/poop-risk-running-gif-21295267","https://tenor.com/view/shit-jurassic-part-dr-malcolm-dinosaur-poop-gif-5262492","https://tenor.com/view/peepeepoopoo-gif-22661777","https://tenor.com/view/baby-kata-pee-poo-fantastic-gif-20701446","https://tenor.com/view/poo-poopoo-caca-pee-peepee-gif-18082954"]
pee_gifs = ["https://tenor.com/view/pingu-holding-pee-pee-i-gotta-pee-pee-dance-gif-22304787","https://tenor.com/view/gotta-pee-boo-monster-inc-gif-14396919","https://tenor.com/view/extreme-wilderness-pro-survi-jerry-loven-pee-urine-gif-16616609","https://tenor.com/view/peepee-dance-gif-9395113","https://tenor.com/view/the-big-bang-theory-sheldon-cooper-i-am-the-master-of-my-own-bladder-pee-night-gif-4486721","https://tenor.com/view/rilakkuma-bear-gotta-pee-need-to-pee-gif-16265448","https://tenor.com/view/peepeepoopoo-gif-22661777","https://tenor.com/view/i-have-to-pee-pee-mylittlepony-knock-desperate-gif-4486726","https://tenor.com/view/poo-poopoo-caca-pee-peepee-gif-18082954","https://tenor.com/view/i-peed-a-little-melissa-villasenor-saturday-night-live-i-peed-my-pants-excited-gif-19002862","https://tenor.com/view/kung-fu-panda-peed-a-little-pee-gif-4835420","https://tenor.com/view/dying-laughing-wet-my-pants-gif-13197423","https://tenor.com/view/oh-damn-i-just-peed-myself-laughing-laugh-humorous-gif-12587200","https://tenor.com/view/so-sorry-tiggy-peed-on-you-sorry-tiggy-pee-gif-22634345","https://tenor.com/view/fireteam-server-wide-pee-pee-break-gif-22825340","https://tenor.com/view/to-pee-or-not-to-pee-coy-stewart-lorenzo-mr-iglesias-should-i-or-shouldnt-i-gif-17673577"]
fart_gifs = ["https://tenor.com/view/fart-experiment-funny-gif-10543322","https://tenor.com/view/friday-next-pops-willie-willie-jones-gif-5894387","https://tenor.com/view/fart-farting-fart-in-your-direction-gross-monty-python-gif-16784927","https://tenor.com/view/milk-and-mocha-fart-tease-puff-joke-gif-11485393","https://tenor.com/view/fatcatzcouple-fat-cats-fat-kitty-cat-couple-farting-gif-20402888","https://tenor.com/view/fart-turkey-chicken-silly-green-mist-gif-15091927","https://tenor.com/view/fart-just-farted-explosive-fart-boom-gif-12438929","https://tenor.com/view/fart-dog-silent-fart-gif-11321579","https://tenor.com/view/alana-thompson-smelly-here-comes-honey-boo-boo-stink-fart-gif-11574004","https://tenor.com/view/fart-here-fart-there-oops-mood-gif-9504650","https://tenor.com/view/diarrhea-when-my-diarrhea-is-not-quite-finished-pretty-sure-that-wasnt-a-fart-baby-gif-16228386"]
burp_gifs = ["https://tenor.com/view/patrick-wacky-silly-spongebob-gif-9320553","https://tenor.com/view/drelacionamentos-burp-gif-10906548","https://tenor.com/view/cat-cats-cattitude-catitude-cat-burp-gif-23323001","https://tenor.com/view/cats-gif-20845233","https://tenor.com/view/burp-baby-burp-i-burped-gif-11191287","https://tenor.com/view/muppets-muppet-show-monster-burp-gas-gif-23780754","https://tenor.com/view/belch-belching-burp-burping-mouth-gif-5841757","https://tenor.com/view/pacifier-belch-binky-maggie-simpson-the-simpsons-gif-17495079","https://tenor.com/view/tmnt-michelangelo-burps-loudly-burps-burp-gif-19389493","https://tenor.com/view/nick-food-hungry-burp-gif-4415976","https://tenor.com/view/the-mask-comedy-jim-carrey-burp-belch-gif-3414989","https://tenor.com/view/the-simpsons-loop-burping-burp-drunk-gif-20513165","https://tenor.com/view/burp-burping-eructo-eructar-belch-gif-12181635"]
connection = mysql.connector.connect(host='localhost', database='Lulu', user='REDACTED', password='REDACTED')
client = discord.Client(heartbeat_timeout=600, intents=intents)

stool_chart = "https://upload.wikimedia.org/wikipedia/commons/a/a7/BristolStoolChart_%28cropped%29.png"

def reconnect_db():
    global connection
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(host='localhost', database='Lulu', user='REDACTED', password='REDACTED')
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
        await message.channel.send(chunk)
        time.sleep(1)


@client.event
async def on_ready():
    print("Logged into Discord!")
    
@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name)
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)
    
@client.event
async def on_message(message):
    global pee_gifs
    global poop_gifs
    global burp_gifs
    global fart_gifs
    global stool_chart
    
    if message.author == client.user:
        return
    if message.author.bot and message.author.id != 787355055333965844:
        return
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%Y-%m-%d %H:%M:%S")
            
    if message.content.startswith('!'):
        print("Message called.")

        command_string = message.content.split(' ')
        command = command_string[0].replace('!','')
        parsed_string = message.content.replace("!" + command + " ","")
        username = message.author.name
        server_name = message.guild.name
        print("Command: " + command)

        if (command == 'sayhi'):
            await message.channel.send("Hello there, " + username + "!")
        elif command == 'chart':
            await send_message(message, stool_chart)
        elif command == 'pee' or command == 'piss':
            result = await commit_sql("""INSERT INTO RecordLog (ServerId, UserId, BodilyFunction, TimeStamp) VALUES (%s, %s, %s, %s);""", (str(message.guild.id), str(message.author.id), "pee", current_time_string))
            if not result:
                await send_message(message, "Database error!")
                return
            else:
                await send_message(message, random.choice(pee_gifs))
                
        elif command == 'poop' or command == 'poo' or command == 'shit' or command == 'crap' or command == 'dump':
            m = re.search(r"(?P<bristol>\d)", parsed_string)
            if not m:
                await send_message(message, "No ranking for the poop found!")
                return
            else:
                bristol = int(m.group('bristol'))
            if bristol > 7 or bristol < 1:
                await send_message(message, "Not a valid Bristol poo rank! Please choose a rank between 1 and 7!")
                return
                
            result = await commit_sql("""INSERT INTO RecordLog (ServerId, UserId, BodilyFunction, TimeStamp,BristolRank) VALUES (%s, %s, %s, %s, %s);""", (str(message.guild.id), str(message.author.id), "poop", current_time_string, str(bristol)))
            if not result:
                await send_message(message, "Database error!")
                return
            else:
                await send_message(message, random.choice(poop_gifs))
        elif command == 'fart' or command == 'flatus' or command == 'flatulence':
            result = await commit_sql("""INSERT INTO RecordLog (ServerId, UserId, BodilyFunction, TimeStamp) VALUES (%s, %s, %s, %s);""", (str(message.guild.id), str(message.author.id), "fart", current_time_string))
            if not result:
                await send_message(message, "Database error!")
                return
            else:
                await send_message(message, random.choice(fart_gifs))
                        
        elif command == 'burp' or command == 'ructus':
            result = await commit_sql("""INSERT INTO RecordLog (ServerId, UserId, BodilyFunction, TimeStamp) VALUES (%s, %s, %s, %s);""", (str(message.guild.id), str(message.author.id), "burp", current_time_string))
            if not result:
                await send_message(message, "Database error!")
                return
            else:
                await send_message(message, random.choice(burp_gifs))
                        
        elif command == 'help' or command == 'info':
            await send_message(message, "Welcome to **Lulu**, the bodily function tracking Discord bot!\n\nCommands:\n\n`!help`: This help.\n`!chart`: Show the Bristol ranking char for poop.\n`!pee`: Record a pee.\n`!poop RANK`: Record a poop of Bristol Rank RANK (number).\n`!fart`: Record a fart.\n`!burp`: Record a burp.\n`!history`: Show your last ten bodily functions.\n`!summary`: See a summary of your bodily functions in this server.\n`!cleardata`: Clear your data for this server from the bot.\n")
        elif command == 'history':
            records = await select_sql("""SELECT BodilyFunction, BristolRank, TimeStamp FROM RecordLog WHERE ServerId=%s AND UserId=%s ORDER BY TimeStamp DESC LIMIT 10;""",(str(message.guild.id), str(message.author.id)))
            if not records:
                await send_message(message, "You have no record yet!")
                return
            response = "**Your log:**\n\n"
            for row in records:
                if not row[1]:
                    rank = "N/A"
                else:
                    rank = str(row[1])
                response = response + str(row[2]) + " - " + row[0] + " - " + rank + "\n"
            await send_message(message, response)
        elif command == 'summary':
            records = await select_sql("""SELECT BodilyFunction FROM RecordLog WHERE ServerId=%s AND UserId=%s;""", (str(message.guild.id), str(message.author.id)))
            if not records:
                await send_message(message, "You haven't logged anything gross yet!")
                return
            else:
                fart = 0
                pee = 0
                poop = 0
                burp = 0
                for row in records:
                    if row[0] == 'poop':
                        poop = poop +1
                    elif row[0] == 'burp':
                        burp = burp + 1
                    elif row[0] == 'fart':
                        fart = fart +1
                    elif row[0] == 'pee':
                        pee = pee + 1
                    else:
                        pass
                response = "**Bodily function summary for " + message.author.display_name + ":**\n\n**Poops**: " + str(poop) + "\n**Pees:** " + str(pee) + "\n**Burps:** " + str(burp) + "\n**Farts:** " + str(fart)
                await send_message(message, response)
        elif command == 'cleardata':
            result = await commit_sql("""DELETE FROM RecordLog WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id), str(message.author.id)))
            if result:
                await send_message(message, "Your pees, poops, burps and farts have been meticulously flushed.")
            else:
                await send_message(message, "Database error!")
        elif command == 'invite':
            await send_message(message, "Invite link: https://discord.com/api/oauth2/authorize?client_id=915939284857548810&permissions=2147534848&scope=bot%20applications.commands")
        else:
            pass
            
@client.event
async def on_interaction(member, interaction):
    message = NakedObject()
    message.author = member
    message.guild = interaction.guild
    message.content = "." + interaction.command.to_dict()['name']
    if interaction.command.options:
        for option in interaction.command.options:
            message.content = message.content + " " + str(option)
            
    message.attachments = None
    message.channel = interaction.channel
    print(str(message.content))
    url = "https://discord.com/api/v8/interactions/" + str(interaction.id) + "/" + str(interaction.token) + "/callback"
    json = {
    "type": 4,
    "data": {
        "content": "<@" + str(member.id) + ">"
        }
    }
    r = requests.post(url, json=json)



    #await interact_reply.send_message(content="Success.", ephemeral=True)
    await on_message(message)
    
client.run'REDACTED' 
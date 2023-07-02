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

ignore_channels = {}
possible_insults = ["Your mother was a hamster, and your father smelled of elderberries!","You suck more than Mocia Lewinsky during an EF5 tornado hitting a vacuum cleaner store.", "Your mother wears combat boots.", "You brobdinagian asshole.", "Fuck you, you fucking fucker.", "I bite my thumb at you.", "You smell so badly Speed Stick slows down and stops.", "Damn, when did your neck throw up? Oh shit, that's your face!", "Man, even Bill Clinton would say, \"No Thanks,\" if he saw you.", "You needle-dicked bastard!", "What's the matter, is it your time of the month 24/7?", "ID10T error: YOU!", "You're an idiot.", "You're dumber than a box of rocks.", "If you rode the short bus, the bus would have to be two-dimensional!", "If brains were gasoline, you wouldnt' have enough to power an ant's motorcycle around the outside of a penny!", "You're a waste of oxygen, so what should you stop doing?", "Don't burst an artery trying to think of a comeback, Einstein!", "Fuck you!", "You're so poor you can't afford free parking!", "You couldn't satisfy a paramecium with that penis!", "I've seen better chatting on AOL.", "I'm not even deigning to insult you.","Your ass is so big that it has its own gravitational pull!", "The 1970s called, they want their lack of style back.", "You mewling shrew!", "Where'd you get the clothes, the toilet store?", "You look like a bucket of shit!", "You look like a bag of dicks!", "You’re an emotional fucking cripple. Your soul is dogsshit. Every single fucking thing about you is ugly.", "What you've just said is one of the most insanely idiotic things I have ever heard. At no point in your rambling, incoherent response were you even close to anything that could be considered a rational thought. Everyone in this room is now dumber for having listened to it. I award you no points, and may God have mercy on your soul.", "You cock-juggling thundercunt!", "You're a shitlord!", "Does Barry Manilow know that you raid his wardrobe?", "Watching you think is like watching a bunch of retards trying to hump a doorknob!", "You're about as useful as a poopy-flavored lollipop!", "You know what the difference between your momma and a washing machine is? When I dump a load in a machine, the machine doesn't follow me around for three weeks.","You horse manure smelling motherfucker, you.", "You’re a virgin and you can’t drive.", "You're somewhere between a cockroach and that white stuff that accumulates at the corner of your mouth when you're really thirsty.", "I'd rather smell dick cheese than you!", "You have more sand in your vagina than the Sahara desert!", "You smell like rendered horse, you burning asshole.", "You can go suck a fuck.", "You may look like an idiot and talk like an idiot but don't let that fool you – you really are an idiot.", "That's all you got, lady - two wrong feet and fucking ugly shoes.", "You hit like a vegetarian.", "To call you stupid would be an insult to stupid people.", "I don’t give a tuppeny fuck about your moral conundrum, you meat-headed shit sack.", "You're in more dire need of a blowjob than any man in history.", "You are literally too stupid to insult.", "Listen, you insignificant, square-toed, pimple-headed spy!", "You're what the French call: 'les incompetents'.", "YOU'RE AN INANIMATE FUCKING OBJECT!", "Allow me to pop a jaunty little bonnet on your purview and ram it up your ass with a lubricated horse cock.", "Go fornicate yourself with a rusty iron rod wrapped in razor wire.", "I should have had you wear double condoms. Well, we shouldn't have done it in the first place, but if you ever do it again, which as a favour to women everywhere, you should not, but if you do, you should be wearing condom on condom, and then wrap it in electrical tape. You should just walk around always inside a great big condom because you are shit!","Your face looks like Robin Williams' knuckles.", "Were you always this stupid or did you take lessons?", "My great aunt Jennifer ate a whole box of candy every day of her life. She lived to be 102 and when she'd been dead three days, she looked better than you do now.", "Your mummy is a TWIT.", "I’ll tell you what. The day I need a friend like you, I’ll just have myself a little squat and shit one out.", "I want to tell you what a cheap, lying, no-good, rotten, four-flushing, low-life, snake-licking, dirt-eating, inbred, overstuffed, ignorant, blood-sucking, dog-kissing, brainless, dickless, hopeless, heartless, fat-ass, bug-eyed, stiff-legged, spotty-lipped, worm-headed sack of monkey shit you are!", "I wouldn't live with you if the world were flooded with piss and you lived in a tree.", "Are you a special agent sent here to ruin my evening and possibly my entire life?", "You're a real blue flame special, aren't you, son? Young, dumb and full of cum. What I don't know is how you got assigned here. Guess we must just have ourselves an asshole shortage, huh?", "I'll explain and I'll use small words so that you'll be sure to understand, you warthog faced buffoon.", "You vomitous mass!", "Is that your nose or did a bus park on your face?", "Even if I were blind, desperate, starved and begging for it on a desert island, you'd be the last thing I'd ever fuck.", "You're tacky and I hate you.", "To everyone here who matters, you're spam. You're vapour. A waste of perfectly good yearbook space.", "Hey laser-lips, your mother was a snowblower.", "You dense, irritating, miniature beast of a burden.", "You know what you look like to me, with your good bag and your cheap shoes? You look like a rube. A well scrubbed, hustling rube with a little taste. Good nutrition has given you some length of bone, but you’re not more than one generation from poor white trash, are you?", "You stuck-up, half-witted, scruffy-looking nerf herder.", "You're just the afterbirth, slithered out on your mother's filth. They should have put you in glass jar on a mantelpiece.", "You dirt-eating piece of slime. You scum-sucking pig. You son of a motherless goat.", "You are a sad strange little man, and you have my pity.", "You are a worthless, friendless, piece of shit whose mommy left daddy when she figured out he wasn't Eugene O'Neill, and who is now weeping and slobbering all over my drum set like a fucking nine-year old girl.", "In the short time we've been together, you have demonstrated every loathsome characteristic of the male personality and even discovered a few new ones. You are physically repulsive, intellectually retarded, you're morally reprehensible, vulgar, insensitive, selfish, stupid, you have no taste, a lousy sense of humour and you smell. You're not even interesting enough to make me sick.", "You clinking, clanking, clattering collection of caliginous junk!", "Your mother should have thrown you away and kept the stork.", "I never forget a face, but in your case, I'll make an exception.", "If your brains were dynamite, there wouldn't be enough to blow your hat off.", "Only two things are infinite-- the universe and your stupidity, and I'm not so sure about the former.", "My opponent is a glob of snot.", "If you won't be a good example, then you'll have to be a horrible warning.", "If I gave you an enema, I could bury you in a matchbox.", "Your ears are so big, you could hang-glide over the Falklands!", "The tautness of your face sours ripe grapes.", "If they can make penicillin out of moldy bread, then they can sure make something out of you.", "Your baby is so ugly, you should have thrown it away and kept the stork.", "You’re a grey sprinkle on a rainbow cupcake.", "If your brain was dynamite, there wouldn’t be enough to blow your hat off.", "You are more disappointing than an unsalted pretzel.", "Light travels faster than sound which is why you seemed bright until you spoke.", "We were happily married for one month, but unfortunately we’ve been married for 10 years.", "Your kid is so ugly, he makes his Happy Meal cry.", "Child, you have so many gaps in your teeth it looks like your tongue is in jail.", "Your secrets are always safe with me. I never even listen when you tell me them.", "I’ll never forget the first time we met. But I’ll keep trying.", "You’d think this baby was born on the highway since that’s where accidents happen.", "I only take you everywhere I go just so I don’t have to kiss you goodbye.", "Hold still. I’m trying to imagine you with personality.", "Our kid must have gotten his brain from you! I still have mine.", "Your face makes onions cry.", "The only way my husband would ever get hurt during an activity is if the TV exploded.", "You look so pretty. Not at all gross, today.", "It’s impossible to underestimate you.", "Her teeth were so bad she could eat an apple through a fence.", "I’m not insulting you, I’m describing you.", "Did you get a fine for littering when you dropped your baby off at daycare?", "Keep rolling your eyes, you might eventually find a brain.", "To teenage daughter: “Learn from my mistakes. Use birth control.”", "You bring everyone so much joy, when you leave the room.", "I thought of you today. It reminded me to take out the trash.", "Don’t worry about me. Worry about your eyebrows.", "You are the human version of period cramps.", "If you’re going to be two-faced, at least make one of them pretty.", "You are like a cloud. When you disappear it’s a beautiful day.", "I’d rather treat my baby’s diaper rash than have lunch with you.", "Don’t worry, the first 40 years of childhood are always the hardest.", "I may love to shop but I will never buy your bull.", "I love what you’ve done with your hair. How do you get it to come out of your nostrils like that?", "Your face is just fine but we’ll have to put a bag over that personality.", "I’m not a nerd, I’m just smarter than you.", "I forgot the world revolves around you. My apologies, how silly of me.", "OH MY GOD! IT SPEAKS!", "You’re the reason God created the middle finger."]
voice_state = False
hell = {} 
intents = discord.Intents.all()
client = discord.Client(heartbeat_timeout=600,intents=intents)
server_settings = {}

async def reaper(user_id, channel):
    global possible_insults
    await client.wait_until_ready()
    await log_message("Lanuching timer.")
    while True:
        await channel.send(">>> <@" + str(user_id) +">, " + random.choice(possible_insults))
        await asyncio.sleep(30) 
        
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    try:
        connection = mysql.connector.connect(host='localhost', database='KingDB', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='KingDB', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='KingDB', user='REDACTED', password='REDACTED')
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

def role_check(role_required, user):
    for role in user.roles:
        if role.id == role_required:
            return True

def owner_check(owner_id, user):
    if author.id != owner_id:
        return false
    else:
        return true

async def direct_message(user, response):
    channel = await user.create_dm()
    await log_message("replied to user " + user.name + " in DM with " + response)
    try:
        await channel.send(response)
    except discord.errors.Forbidden:
        pass

async def bot_scheduler():
    await client.wait_until_ready()
    await log_message("Lanuching timer.")
    while not client.is_closed():
        current_time_obj = datetime.now()
        current_hour = int(current_time_obj.strftime("%H"))
        current_minute = int(current_time_obj.strftime("%M"))
        current_second = int(current_time_obj.strftime("%S"))
#        print("Time " + str(current_hour) + ":" + str(current_minute) + ":" + str(current_second))

        await asyncio.sleep(1) 
        
async def initialize(message):

    drop_tables = """DROP TABLE IF EXISTS ServerSettings; DROP TABLE IF EXISTS ColorRoles; DROP TABLE IF EXISTS Gateway;"""
    result = await execute_sql(drop_tables)
    if result:
        await send_message(message, "Tables dropped.")
    else:
        await send_message(message, "Database error!")
        return
    
    create_settings_table = """CREATE TABLE ServerSettings (Id INT AUTO_INCREMENT, ServerId VARCHAR(40), ChannelList TEXT, AdminRole VARCHAR(40), ModeratorRole VARCHAR(40), AutoMuteWords TEXT, AutoKickWords TEXT, AutoBanWords TEXT, MassMentionThreshold Int, MassMentionTimeSeconds Int, MassMentionAction VARCHAR(40), NewMemberRole VARCHAR(40), FullMemberRole VARCHAR(40), TrollChannelName TEXT, TrollPokeQuestions TEXT, InactiveUserTimeoutDays Int, InactiveUserTimeoutAction VARCHAR(40), ModeratorChannel VARCHAR(40), Greeting TEXT, Farewell TEXT, Rules TEXT, MessageChannel VARCHAR(40) PRIMARY KEY(Id));"""
    create_color_roles_table = """CREATE TABLE ColorRoles (Id INT AUTO_INCREMENT, ServerId VARCHAR(40), ColorRoleName VARCHAR(100), ColorRoleColor VARCHAR(16), ColorRoleId VARCHAR(40), ReactionEmoji VARCHAR(200), PRIMARY KEY(Id));"""
    create_gateway_table = """CREATE TABLE Gateway (Id INT AUTO_INCREMENT, ServerId VARCHAR(40), InitialChannelId VARCHAR(40), ConfirmReaction VARCHAR(100), ConfirmMessage TEXT, PRIMARY KEY(Id));"""
    create_deleted_messages_table = """CREATE TABLE DeletedMessages (Id INT AUTO_INCREMENT, ServerId VARCHAR(40), UserId VARCHAR(40), ChannelId VARCHAR(40), MessageId VARCHAR(40), MessageContent TEXT, ActionTaken VARCHAR(30), Reason TEXT, PRIMARY KEY(Id));"""
    create_history_table = """CREATE TABLE ActionHistory (Id INT AUTO_INCREMENT, ServerId VARCHAR(40), CommandUserId VARCHAR(40), CommandChannelId VARCHAR(40), UserId VARCHAR(40), ActionTaken VARCHAR(40), CommandParameters TEXT, PRIMARY KEY(Id));"""
    
    result = await execute_sql(create_settings_table)
    if not result:
        await send_message(message, "Database error with creating settings!")
        return
    result = await execute_sql(create_color_roles_table)
    if not result:
        await send_message(message, "Database error with creating color roles!")
        return
    result = await execute_sql(create_gateway_table)
    if not result:
        await send_message(message, "Database error with creating gateway!")
        return        
    result = await execute_sql(create_deleted_messages_table)
    if not result:
        await send_message(message, "Database error with creating deleted messages table!")
        return
    result = await execute_sql(create_history_table)
    if not result:
        await send_message(message, "Database error with creating action history table!")
        return    
        
@client.event
async def on_raw_reaction_add(payload):
    global server_settings
    if payload.message_id == server_settings[payload.guild_id]["ConfirmMessage"] and str(payload.emoji) == server_settings[payload.guild_id]["ConfirmReaction"]:
        user = payload.member
        server_obj = client.get_guild(payload.guild_id)
        role = discord.utils.get(server_obj.roles, id=server_settings[payload.guild_id]["FullMemberRole"])
        old_role = discord.utils.get(server_obj.roles, id=server_settings[payload.guild_id]["NewMemberRole"])
        for current_role in user.roles:
            if current_role == role:
                return
        await user.remove_roles(old_role)
        await user.add_roles(role)
        channel = client.get_channel(server_settings[payload.guild_id]["MessageChannel"])
        await channel.send(">>> " + server_settings[payload.guild_id]["Greeting"] + " <@" + str(user.id) + ">")

@client.event
async def on_voice_state_update(member, before, after):
    global voice_state
    text_channel_id = 676977852213887016
    voice_role_id = 708515570537988168
    voice_channel_id = 676975048556412951
    if member.guild.id != 676975047889387535:
        return
    voice_channel_obj = client.get_channel(voice_channel_id)
    text_channel_obj = client.get_channel(text_channel_id)
    voice_role_obj = client.get_channel(voice_role_id)
    
    try: member.voice.channel.id
    except:
        return
    
    if member.voice.channel.id != voice_channel_id:
        return
    if not voice_state:
        if len(voice_channel_obj.members) < 2:
            if before.channel is None and after.channel is not None:
                voice_state = True
                await text_channel_obj.send("<@&" + str(voice_role_id) +  "> there is someone in the voice chat.")
    else:
        if len(voice_channel_obj.members) <= 1:
            voice_state = False
        
        
    
        
@client.event
async def on_ready():
    global server_settings
    global hell
    global ignore_channels
    await log_message("Logged into Discord!")
    for guild in client.guilds:
        ignore_channels[guild.id] = [] 
    records = await select_sql("""SELECT ServerId,Greeting,Farewell,Rules,AdminRole,ModeratorRole,AutoMuteWords,AutoKickWords,AutoBanWords,ModeratorChannel,FullMemberRole,MessageChannel,NewMemberRole,IgnoreChannels FROM ServerSettings;""")
    if records:
            
        for row in records:
            server_id = int(row[0])
            server_settings[server_id] = { }
            if row[4] is not None:
                server_settings[server_id]["Greeting"] = row[1]
                server_settings[server_id]["Farewell"] = row[2]
                server_settings[server_id]["Rules"] = row[3]
                server_settings[server_id]["AdminRole"] = int(row[4])
                if row[5] is not None:
                    server_settings[server_id]["ModeratorRole"] = int(row[5])
                else:
                    server_settings[server_id]["ModeratorRole"] = 0
                if row[6] is not None: 
                    server_settings[server_id]["AutoMuteWords"] = row[6].split(',')
                    counter = 0
                    for word in server_settings[server_id]["AutoMuteWords"]:
                        server_settings[server_id]["AutoMuteWords"][counter] = server_settings[server_id]["AutoMuteWords"][counter].strip()
                        counter = counter + 1
                else:
                    server_settings[server_id]["AutoMuteWords"] = {}
                if row[7] is not None:
                    server_settings[server_id]["AutoKickWords"] = row[7].split(',')
                    counter = 0
                    for word in server_settings[server_id]["AutoKickWords"]:
                        server_settings[server_id]["AutoKickWords"][counter] = server_settings[server_id]["AutoKickWords"][counter].strip()
                        counter = counter + 1                    
                else:
                    server_settings[server_id]["AutoKickWords"] = {} 
                if row[8] is not None:
                    server_settings[server_id]["AutoBanWords"] = row[8].split(',')
                    counter = 0
                    for word in server_settings[server_id]["AutoBanWords"]:
                        server_settings[server_id]["AutoBanWords"][counter] = server_settings[server_id]["AutoBanWords"][counter].strip()
                        counter = counter + 1                     
                else:
                    server_settings[server_id]["AutoBanWords"] = {}
                if row[9] is not None:
                    server_settings[server_id]["ModeratorChannel"] = int(row[9])
                else:
                    server_settings[server_id]["ModeratorChannel"] = 0
                if row[10] is not None:
                    server_settings[server_id]["FullMemberRole"] = int(row[10])
                else:
                    server_settings[server_id]["FullMemberRole"] = 0
                if row[11] is not None:
                    server_settings[server_id]["MessageChannel"] = int(row[11])
                else:
                    server_settings[server_id]["MessageChannel"] = 0
                if row[12] is not None:
                    server_settings[server_id]["NewMemberRole"] = int(row[12])
                else:
                    server_settings[server_id]["NewMemberRole"] = 0 
                if row[13] is not None:
                    ignore_channels[server_id] = row[13].split(',')
                    await log_message("Row " + str(row[13]) + "Split: " + str(row[13].split(",")))
                        
    records = await select_sql("""SELECT ServerId,InitialChannelId,ConfirmReaction,ConfirmMessage FROM Gateway;""")
    if records:
        for row in records:
            server_id = int(row[0])
            try: server_settings[server_id]
            except: server_settings[server_id] = { }
            if row[1] is not None:
                server_settings[server_id]["InitialChannelId"] = int(row[1])
            else:
                server_settings[server_id]["InitialChannelId"] = 0
            if row[2] is not None:
                server_settings[server_id]["ConfirmReaction"] = row[2]
            else:
                server_settings[server_id]["ConfirmReaction"] = 0
            if row[3] is not None:
                server_settings[server_id]["ConfirmMessage"] = int(row[3])
            else:
                server_settings[server_id]["ConfirmMessage"] = 0
                
    await log_message("SQL loaded!")
    
    for guild in client.guilds:
        hell[guild.id] = {}
        try: server_settings[guild.id]
        except KeyError:
            server_settings[guild.id] = { }
            result = await commit_sql("""INSERT INTO ServerSettings (ServerId) VALUES (%s);""", (str(guild.id),))
            result = await commit_sql("""INSERT INTO Gateway (ServerId) VALUES (%s);""", (str(guild.id),))
        try: server_settings[guild.id]["InitialChannelId"]
        except KeyError: result = await commit_sql("""INSERT INTO Gateway (ServerId) VALUES (%s);""", (str(guild.id),))
            
          

        
@client.event
async def on_guild_join(guild):
    global server_settings
    
    await log_message("Joined guild " + guild.name)
    try: server_settings[guild.id]
    except KeyError:
        server_settings[guild.id] = { }
        result = await commit_sql("""INSERT INTO ServerSettings (ServerId) VALUES (%s);""", (str(guild.id),))
        result = await commit_sql("""INSERT INTO Gateway (ServerId) VALUES ($s);""",(str(guild.id),))
    try: server_settings[guild.id]["MessageChannel"]
    except KeyError: server_settings[guild.id]["MessageChannel"] = guild.system_channel 
    
@client.event
async def on_guild_remove(guild):
    global server_settings
    await log_message("Left guild " + guild.name)
    result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s""",(str(guild.id),))
    server_settings[guild.id] = { }
    
@client.event
async def on_member_join(member):
    global server_settings

    
    await log_message("Member " + member.name + " joined guild " + member.guild.name)
    new_role = discord.utils.get(member.guild.roles, id=server_settings[member.guild.id]["NewMemberRole"])
    await member.add_roles(new_role)
    records = await select_sql("""SELECT InitialChannelId FROM Gateway WHERE ServerId=%s;""",(str(member.guild.id),))

    channel = member.guild.get_channel(server_settings[member.guild.id]["MessageChannel"])

    await direct_message(member, "Hello, " + member.name + ", and welcome to " + member.guild.name + ". Please read the rules in the <#" + channel.name + "> channel on the server and react to the emoji to unlock the other channels.")
    await channel.send(member.name + " has joined the server.")

@client.event
async def on_member_remove(member):
    global server_settings
    await log_message("Member " + member.name + " left guild " + member.guild.name)
    try: 
        server_settings[member.guild.id]["Farewell"]
        message_channel = client.get_channel(server_settings[member.guild.id]["ModeratorChannel"])
        await message_channel.send(">>> " + server_settings[member.guild.id]["Farewell"] + " " + member.name)
    except KeyError:
        pass    
    
@client.event
async def on_message(message):
    global possible_insults
    global server_settings
    global ignore_channels
    global hell
    
    try:
        await log_message("Ignored channels: " + str(ignore_channels[message.guild.id]))
    except:
        pass
        
    global hell
    
    if message.author == client.user:
        return
    if message.author.bot:
        return
    user = message.author
    try: hell[message.guild.id]
    except: hell[message.guild.id] = {}
    for user_obj in hell[message.guild.id].keys():
        if message.channel == hell[message.guild.id][user_obj]:
            await message.channel.send("<@" + str(user_obj) + ">, "+ random.choice(possible_insults))
            return
    
    for id in ignore_channels[message.guild.id]:
        await log_message("Channel: " + id)
        if int(id) == message.channel.id:
            await log_message("ignored channel.")
            return
        
    if message.content.startswith('king'):


            
        command_string = message.content.split(' ')
        command = command_string[1]
        if ("king " + command + " ") in message.content:
            parsed_string = message.content.replace("king " + command + " ","")
        else:
            parsed_string = ""
        username = message.author.name
        server_name = message.guild.name
        user_id = message.author.id
        server_id = message.guild.id
        await log_message("Received command of " + message.content + " with command of " + command + " and parsed string of  " + parsed_string)
        
        if message.mentions:
            target_id = message.mentions[0].id
        else:
            target_id = "None"
            
        await commit_sql("""INSERT INTO ActionHistory (ServerId, CommandUserId, CommandChannelId, UserId, ActionTaken, CommandParameters) VALUES (%s, %s, %s, %s, %s, %s) ;""", (str(message.guild.id), str(message.author.id), str(message.channel.id), target_id, command, parsed_string))
        
        if command == 'info' or command == 'help':
            response = "**Nebudchadnezzar** is the king of Discord server bots. Rule the server with an iron fist!\n\n\n\n**Commands**\n\n\n\n`king setadminrole @role` Set the administrator role.\n\n`king setmodrole @role` Set the moderator role.\n\n`king addadmin @user` Add a user to the admin role.\n\n`king deleteadmin @user` Remove a user from the admin role.\n\n`king addmod @user` Add a user to the moderator role\n\n`king deletemod @user` Delete a user from the moderator role.\n\n`king shutup @user` or `king mute @user` Prevent a user from sending messages.\n\n`king speak @user` or `king unmute @user` Allow a user to post again.\n\n`king boot @user` Kick a user from the server.\n\n`king banhammer @user` or `king kill9 @user` Ban a user from the server.\n\n`king unbanhammer @user` or `king unkill9 @user` Unban a user. May not work if the cache no longer has the mention. In this case, unban from the Discord server settings.\n\n`king setgreeting text` Set the server greeting to text.\n\n`king setfarewell text` Set the server farewell.\n\n`king addrules text` Add a block of text to the server rules.\n\n`king showrules` Show the server rules.\n\n`king reap @user`: Send a troll to hell.\n\n`king rezz @user`: Bring a user back.\n\n`king showdeletedmessages <number>`: Show number of deleted messages.\n\n`king showcommandhistory`: Show command history."
            await send_message(message, response)
        elif command == 'setmodchannel':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author):
                await send_message(message, "You are not in the moderator role!")
                return           
            if not message.channel_mentions:
                await send_message(message, "No moderator channel mentioned!")
                return
            channel_id = message.channel_mentions[0].id
            server_settings[message.guild.id]["ModeratorChannel"] = channel_id 
            result = await commit_sql("""UPDATE ServerSettings SET ModeratorChannel=%s WHERE ServerId=%s;""",(str(channel_id),str(message.guild.id)))
            await send_message(message, "Moderator channel set!")
            return
        elif command == 'setignorechannels':
            if not message.channel_mentions:
                await send_message(message, "No channels mentioned!")
                return
            string_ignore = [] 
            for channel in message.channel_mentions:
                ignore_channels[message.guild.id].append(channel.id)
                string_ignore.append(str(channel.id))
            result = await commit_sql("""UPDATE ServerSettings SET IgnoreChannels=%s WHERE ServerId=%s;""",(",".join(string_ignore),str(message.guild.id)))
            await send_message(message, "Ignore channels updated!")
        elif command == 'passthru':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author) and not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author):
                await send_message(message, "Only moderators can pass through users!")
                return            
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
            user = message.mentions[0]
            role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["FullMemberRole"])
            old_role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["NewMemberRole"])

            await user.remove_roles(old_role)
            await user.add_roles(role)
            channel = client.get_channel(server_settings[message.guild.id]["MessageChannel"])
            await send_message(message, "User has been passed through verification!")
            await channel.send(">>> " + server_settings[message.guild.id]["Greeting"] + " <@" + str(user.id) + ">")            
        elif command == 'setadminrole':
            if message.author != message.guild.owner:
                await send_message(message, "Only the server owner can set the admin role!")
                return
            if len(message.role_mentions) > 1:
                await send_message(message, "Only one role can be defined as the admin role!")
                return
            role_id = message.role_mentions[0].id
            server_settings[message.guild.id]["AdminRole"] = role_id
            result = await commit_sql("""UPDATE ServerSettings SET AdminRole=%s WHERE ServerId=%s;""",  (str(role_id),str(message.guild.id)))
            if result:
                await send_message(message, "Admin role successfully set!")
            else:
                await send_message(message, "Database error!")            
        elif command == 'rezz':

            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author) and not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author):
                await send_message(message, "Only moderators can rezz users!")
                return            
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
                
            user = message.mentions[0]
            try:
                await direct_message(user, "You have been unmuted in " + message.guild.name)
            except:
                pass
            asyncio.sleep(1)    
            try:
                new_role = discord.utils.get(user.guild.roles, id=server_settings[message.guild.id]["FullMemberRole"])
                await user.remove_roles(*user.roles[1:],atomic=True)
                await user.add_roles(new_role)  
            except:
                pass
            asyncio.sleep(1)
            try:
                await hell[message.guild.id][user.id]["channel"].delete()
                await hell[message.guild.id][user.id]["cat"].delete()
                del hell[message.guild.id][user.id]
            except:
                pass
            #await user.edit(mute=True)

            await send_message(message, "User " + user.name + " has been unmuted!")             
        elif command == 'reap':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only moderators can reap users!")
                return            
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
                
            user = message.mentions[0]
            if role_check(server_settings[message.guild.id]["ModeratorRole"], user) or role_check(server_settings[message.guild.id]["AdminRole"], user):
                await send_message(message, "You cannot reap a moderator or admin!")
                return
            await direct_message(user, "You have been reaped in " + message.guild.name)
            full_role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["FullMemberRole"])
            new_role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["NewMemberRole"])
            mod_role = discord.utils.get(message.guild.roles, id=server_settings[member.guild.id]["ModeratorRole"])
            await user.remove_roles(*user.roles[1:],atomic=True)
            
                
            overwrites = { user: discord.PermissionOverwrite(read_messages=True), message.guild.default_role: discord.PermissionOverwrite(read_messages=False), full_role: discord.PermissionOverwrite(read_messages=False), new_role: discord.PermissionOverwrite(read_messages=False), mod_role: discord.PermissionOverwrite(read_messages=True) }
           # for role in message.guild.roles:
            #    overwrites[role] = discord.PermissionOverwrite(read_messages=False)
            #    overwrites[role] = discord.PermissionOverwrite(send_messages=False)
            
            hell_category = await message.guild.create_category("Ninth Circle of Hell",overwrites=overwrites)
            hell_channel = await message.guild.create_text_channel(user.display_name + "s-personal-hell", category=hell_category)
            await hell_channel.send(">>> Welcome to your personal hell, <@" + str(user.id) + ">. Here, you will be taunted until released or until you leave on your own accord!")
            hell[message.guild.id][user.id] = {}
            hell[message.guild.id][user.id]["channel"] = hell_channel
            hell[message.guild.id][user.id]["cat"] = hell_category
            asyncio.sleep(1)
            client.loop.create_task(reaper(user.id,hell_channel))
            
            #await user.edit(mute=True)
            await send_message(message, "User " + user.name + " has been reaped!")        
        if command == 'setgreeting':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no admin role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                    await send_message(message, "You are not in the admin role!")
                    return               

            if not parsed_string:
                await send_message(message, "No greeting speciifed!")
                return
            server_settings[server_id]["Greeting"] = parsed_string
            result = await commit_sql("""UPDATE ServerSettings SET Greeting=%s WHERE ServerId=%s;""",(parsed_string, str(server_id)))
            if result:
                await send_message(message, "Successfully set greeting to " + parsed_string + "!")
            else:
                await send_message(message, "Database error!")
                

        elif command == 'setfarewell':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no admin role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                    await send_message(message, "You are not in the admin role!")
                    return   


            if not parsed_string:
                await send_message(message, "No farewell speciifed!")
                return                    
            server_settings[server_id]["Farewell"] = parsed_string
            result = await commit_sql("""UPDATE ServerSettings SET Farewell=%s WHERE ServerId=%s;""",(parsed_string, str(server_id)))
            if result:
                await send_message(message, "Successfully set greeting to " + parsed_string + "!")
            else:
                await send_message(message, "Database error!")
                
                


        elif command == 'addrules': 
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no admin role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                    await send_message(message, "You are not in the admin role!")
                    return   


            if not parsed_string:
                await send_message(message, "No rules speciifed!")
                return
            records = await select_sql("""SELECT IFNULL(Rules,' ') FROM ServerSettings WHERE ServerId=%s;""", (str(server_id),))
            if not records:
                rules = ""
            else:
                for row in records:
                    rules = row[0]
            server_settings[server_id]["Rules"] = rules + parsed_string
            result = await commit_sql("""UPDATE ServerSettings SET Rules=%s WHERE ServerId=%s;""",(rules + parsed_string, str(server_id)))
            if result:
                await send_message(message, "Successfully added rules as " + parsed_string + "!")
            else:
                await send_message(message, "Database error!")
                
                
        elif command == 'clearrules':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no admin role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                    await send_message(message, "You are not in the admin role!")
                    return   
            server_settings[server_id] = {} 
            result = await commit_sql("""UPDATE ServerSettings SET Rules='' WHERE ServerId=%s;""", (str(server_id),))
            if result:
                await send_message(message, "Rules successfully cleared.")
            else:
                await send_message(message, "Database error!")
                
        elif command == 'clearall':
            if server_settings[server_id]["AdminRole"] is None:
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no admin role has been set! Unable to set greeting!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                    await send_message(message, "You are not in the admin role!")
                    return    
 
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "You are not in the admin role!")
                return
            result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s; INSERT INTO ServerSettings (ServerId) VALUES (%s);""", (str(server_id),str(server_id)))
            if result:
                await send_message(message, "Rules successfully cleared.")
            else:
                await send_message(message, "Database error!")

        elif command == 'commandhistory':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "You are not in the admin or mod role!")
                return           
            if not parsed_string:
                await send_message(message, "No number of commands speciifed!")
                return
            limit = int(parsed_string)
            records = await select_sql("""SELECT CommandUserId, CommandChannelId, UserId, ActionTaken, CommandParameters FROM ActionHistory WHERE ServerId=%s LIMIT """ + parsed_string + """;""", (str(message.guild.id),))
            if not records:
                await send_message(message, "No command history found!")
                return
            response = "**COMMAND HISTORY**\n\n"
            for row in records:
                channel = client.get_channel(int(row[1]))
                if row[2] is not None and row[2] != 'None':
                    target = client.get_user(int(row[2]))
                    target = target.display_name
                else:
                    target = "None"
                    
                user = client.get_user(int(row[0]))
                
                action = row[3]
                command_parameters = row[4]
                response = response + user.name + " called command `" + action + "` from channel `" + channel.name + "` with parameters `" + command_parameters + "` at user `" + target + "`\n"
            await send_message(message, response)
            
            
        elif command == 'setconfirmreaction':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "You are not in the admin role!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify a confirm emoji!")
                return
            server_settings[message.guild.id]["ConfirmReaction"] = parsed_string
            records = await select_sql("""SELECT ConfirmReaction FROM Gateway WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:

                result = await commit_sql("""UPDATE Gateway SET ConfirmReaction=%s WHERE ServerId=%s;""",(parsed_string.strip(), str(message.guild.id)))
                if result:
                    await send_message(message, "Confirm emoji set!")
                else:
                    await send_message(message, "Database error!")
            else:
                result = await commit_sql("""INSERT INTO Gateway ServerId, ConfirmReaction) VALUES (%s, %s);""",(str(message.guild.id),str(parsed_string.strip())))
                await send_message(message,"Confirm emoji set!")
                
        elif command == 'showdeletedmessages':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "You are not in the admin or modd role!")
                return           
            if not parsed_string:
                await send_message(message, "No number of messages speciifed!")
                return
            records = await select_sql("""SELECT Id, UserId,ChannelId, MessageContent, ActionTaken, Reason FROM DeletedMessages WHERE ServerId=%s ORDER BY Id DESC LIMIT """ + parsed_string+ """;""", (str(message.guild.id),))
            if not records:
                await send_message(message, "No deleted message history!")
                return
            response = "**DELETED MESSAGES**\n\n"
            for row in records:
                user = client.get_user(int(row[1]))
                if user is None:
                    user = row[1]
                else:
                    user = user.name
                channel = client.get_channel(int(row[2]))
                content = row[3]
                action = row[4]
                reason = row[5]
                response = response + user + " had a message in channel " + channel.name + " deleted with content `" + content + "` because of " + reason + " and the action taken was " + action + "\n"
            await send_message(message, response)
            
        elif command == 'setmessagechannel':
            if server_settings[server_id]["AdminRole"] is None:
                if message.author != message.guild.owner:
                    await send_message(message, "You are not the server owner and no admin role has been set! Unable to set message channel!")
                    return
            else:
                if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                    await send_message(message, "You are not in the admin role!")
                    return    
            server_settings[server_id]["MessageChannel"] = message.channel_mentions[0].id
            result = await commit_sql("""UPDATE ServerSettings SET MessageChannel=%s WHERE ServerId=%s;""",(str(message.channel_mentions[0].id),str(server_id)))
            if result:
                await send_message(message, "Message channel successfully set to " + message.channel_mentions[0].name + ".")
            else:
                await send_message(message, "Database error!") 

                

                
                
        if command == 'setmodrole':
            if message.author != message.guild.owner:
                await send_message(message, "Only the server owner can set the admin role!")
                return
            if len(message.role_mentions) > 1:
                await send_message(message, "Only one role can be defined as the admin role!")
                return
            role_id = message.role_mentions[0].id
            server_settings[message.guild.id]["ModeratorRole"] = role_id
            result = await commit_sql("""UPDATE ServerSettings SET ModeratorRole=%s WHERE ServerId=%s;""",  (str(role_id),str(message.guild.id)))
            if result:
                await send_message(message, "Moderator role successfully set!")
            else:
                await send_message(message, "Database error!") 

                
        elif command == 'addadmin':
            if message.author != message.guild.owner:
                await send_message(message, "Only the server owner can add admins!")
                return
            if not message.mentions:
                await send_message(message, "You didn't specify any users to add!")
                return
            role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["AdminRole"])
            for user in message.mentions:
                await user.add_roles(role)
            await send_message(message, "Users added to admin role!") 

            
        elif command == 'deleteadmin':
            if message.author != message.guild.owner:
                await send_message(message, "Only the server owner can delete admins!")
                return
            if not message.mentions:
                await send_message(message, "You didn't specify any users to remove!")
                return
            role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["AdminRole"])
            for user in message.mentions:
                await user.remove_roles(role)
            await send_message(message, "Users removed from admin role!") 
            
            
        elif command == 'addmod':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only admins can add moderators!")
                return       
            if not message.mentions:
                await send_message(message, "You didn't specify any users to add!")
                return
            role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["ModeratorRole"])
            for user in message.mentions:
                await user.add_roles(role)
            await send_message(message, "User " + user.display_name + " has been added to moderators!")  

            
        elif command == 'deletemod':
            if message.author != message.guild.owner:
                await send_message(message, "Only the admins can delete moderators!")
                return
            if not message.mentions:
                await send_message(message, "You didn't specify any users to remove!")
                return
            role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["ModeratorRole"])
            for user in message.mentions:
                await user.remove_roles(role)  
            await send_message(message, "User " + user.display_name + " has been removed from moderators!")
            
            
        elif command == 'banhammer' or command == 'kill9':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author) and not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author):
                await send_message(message, "Only moderators can ban users!")
                return            
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
            reason = re.sub(r"<.+>","",parsed_string)
            user = message.mentions[0]
            await direct_message(user, "You have been banned from " + message.guild.name + " for " + reason + ".")
            await user.ban(reason=reason)
            await send_message(message, "User " + user.name + " has been banhammered!")
        elif command == 'massbanhammer' or command == 'masskill9':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author) and not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author):
                await send_message(message, "Only moderators can ban users!")
                return            
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
                
            users = message.mentions
            for user in users:
                await direct_message(user, "You have been banned from " + message.guild.name)
                await user.ban()
                await send_message(message, "User " + user.name + " has been banhammered!")            
            
        elif command == 'unbanhamnmer' or command == 'unkill9':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only admins can unban users!")
                return            
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
                
            user = message.mentions[0]
            await user.unban()
            await send_message(message, "User " + user.name + " has been allowed!")        
        
        elif command == 'shutup' or command == 'mute':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only moderators can mute users!")
                return            
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
                
            user = message.mentions[0]
            await direct_message(user, "You have been muted in " + message.guild.name)
            new_role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["NewMemberRole"])
            await user.remove_roles(*user.roles[1:],atomic=True)
            await user.add_roles(new_role)   
            #await user.edit(mute=True)
            await send_message(message, "User " + user.name + " has been muted!")
            
            
        elif command == 'speak' or command == 'unmute':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author) and not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author):
                await send_message(message, "Only moderators can mute users!")
                return            
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
                
            user = message.mentions[0]
            await direct_message(user, "You have been unmuted in " + message.guild.name)
           
            new_role = discord.utils.get(user.guild.roles, id=server_settings[message.guild.id]["FullMemberRole"])
            await user.remove_roles(*user.roles[1:],atomic=True)
            await user.add_roles(new_role)   
            #await user.edit(mute=True)

            await send_message(message, "User " + user.name + " has been unmuted!") 
            
            
        elif command == 'boot':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only moderators can kick users!")
                return            
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
            reason = re.sub(r"<.+>","",parsed_string)    
            user = message.mentions[0]
            await direct_message(user, "You have been kicked from " + message.guild.name + " for " + reason)
            await user.kick(reason=reason)
            await send_message(message, "User " + user.name + " has been given the boot!")
            
            
        elif command == 'showgreeting':
            if server_settings[server_id]["Greeting"] is None:
                await send_message(message, "Server Greeting not set.")
            else:
                await send_message(message, "Server Greeting:\n\n" + server_settings[server_id]["Greeting"])
                
        elif command == 'showfarewell':
            if server_settings[server_id]["Farewell"] is None:
                await send_message(message, "Server Farewell not set.")
            else:
                await send_message(message, "Server Farewell:\n\n" + server_settings[server_id]["Farewell"]) 

                
        elif command == 'showrules':
            if server_settings[server_id]["Rules"] is None:
                await send_message(message, "Server Rules not set.")
            else:
                await send_message(message, "Server Rules:\n\n" + server_settings[server_id]["Rules"]) 

                
        elif command == 'showadminrole':
            if server_settings[server_id]["AdminRole"] is None:
                await send_message(message, "Server AdminRole not set.")
            else:
                await send_message(message, "Server AdminRole:\n\n" + server_settings[server_id]["AdminRole"])
                
                
        elif command == 'initialize':
            await initialize(message)
            await send_message(message, "Databases created successfully.")
            
            
        elif command == 'setmutewords':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only admins can set auto mute words!")
                return                
            auto_mute_words = parsed_string.split(',')
            server_settings[message.guild.id]["AutoMuteWords"] = auto_mute_words
            result = await commit_sql("""UPDATE ServerSettings SET AutoMuteWords=%s WHERE ServerId=%s;""", (parsed_string, str(message.guild.id)))
            if result:
                await send_message(message, "Set automute words for server!")
            else:
                await send_message(message, "Database error!")
                
                
        elif command == 'showmutewords':
            try: server_settings[message.guild.id]["AutoMuteWords"]
            except:
                await send_message(message, "Auto mute words not set.")
            response = "**Auto mute words**\n\n"
            for word in server_settings[message.guild.id]["AutoMuteWords"]:
                response = response + word + ", "
            await send_message(message, response)
            
        elif command == 'setkickwords':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only admins can set auto mute words!")
                return                
            auto_mute_words = parsed_string.split(',')
            server_settings[message.guild.id]["AutoKickWords"] = auto_mute_words
            result = await commit_sql("""UPDATE ServerSettings SET AutoKickWords=%s WHERE ServerId=%s;""", (parsed_string, str(message.guild.id)))
            if result:
                await send_message(message, "Set autokick words for server!")
            else:
                await send_message(message, "Database error!")
                
                
        elif command == 'setbanwords':
            if not role_check(server_settings[message.guild.id]["ModeratorRole"], message.author) and not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only admins can set auto ban words!")
                return                
            auto_mute_words = parsed_string.split(',')
            server_settings[message.guild.id]["AutoKickWords"] = auto_mute_words
            result = await commit_sql("""UPDATE ServerSettings SET AutoBanWords=%s WHERE ServerId=%s;""", (parsed_string, str(message.guild.id)))
            if result:
                await send_message(message, "Set autokick words for server!")
            else:
                await send_message(message, "Database error!") 

                
        elif command == 'showkickwords':
            try: server_settings[message.guild.id]["AutoKickWords"]
            except:
                await send_message(message, "Auto kick words not set.")
            response = "**Auto kick words**\n\n"
            for word in server_settings[message.guild.id]["AutoKickWords"]:
                response = response + word + ", "
            await send_message(message, response)
            
        elif command == 'setupgateway':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only admins can set the gateway!")
                return    
            if not message.channel_mentions:
                await send_message(message, "No channel specified!")
                return
            channel_id = message.channel_mentions[0].id
            server_settings[message.guild.id]["InitialChannelId"] = channel_id
            result = await commit_sql("""UPDATE Gateway SET InitialChannelId=%s WHERE ServerId=%s;""",(str(channel_id),str(message.guild.id)))
            if not result:
                await send_message(message, "Database error!")
                return
            if not message.role_mentions:
                await send_message(message, "No new role mentioned!")
                return
            role_id = message.role_mentions[0].id
            role = message.role_mentions[0]
            server_settings[message.guild.id]["NewMemberRole"] = role_id
            result = await commit_sql("""UPDATE ServerSettings SET NewMemberRole=%s WHERE ServerId=%s;""",(str(role_id),str(message.guild.id)))
            if not result:
                await send_message(message, "Database error!")
                return            
            initial_channel = server_settings[message.guild.id]["InitialChannelId"]
            initial_channel_obj = client.get_channel(initial_channel)
            response = "Please react to the emoji below to confirm you have read the rules.\n\n" + server_settings[message.guild.id]["Rules"] + "\n"
            message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
            for chunk in message_chunks:
                await initial_channel_obj.send(">>> " + chunk)
            time.sleep(1)
            message_id = initial_channel_obj.last_message_id
            last_message = await initial_channel_obj.fetch_message(message_id)
            server_settings[message.guild.id]["ConfirmMessage"] = message_id
            result = await commit_sql("""UPDATE Gateway SET ConfirmMessage=%s WHERE ServerId=%s;""", (str(message_id), str(message.guild.id)))
            if not result:
                await send_message(message, "Database error!")
                return

            
            await last_message.add_reaction(server_settings[message.guild.id]["ConfirmReaction"])
            
            await send_message(message, "Gateway set up successfully.")
        elif command == 'setnewrole':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only admins can set the new member role!")
                return    
            if not message.role_mentions:
                await send_message(message, "No new role mentioned!")
                return
            role_id = message.role_mentions[0].id
            server_settings[message.guild.id]["NewMemberRole"] = role_id
            result = await commit_sql("""UPDATE ServerSettings SET NewMemberRole=%s WHERE ServerId=%s;""",(str(role_id),str(message.guild.id)))
            if not result:
                await send_message(message, "Database error!")
                return
            await send_message(message, "New member role set up successfully.")                    
        elif command == 'setmemberrole':
            if not role_check(server_settings[message.guild.id]["AdminRole"], message.author):
                await send_message(message, "Only admins can set the full member role!")
                return    
            if not message.role_mentions:
                await send_message(message, "No full role mentioned!")
                return
            role_id = message.role_mentions[0].id
            server_settings[message.guild.id]["FullMemberRole"] = role_id
            result = await commit_sql("""UPDATE ServerSettings SET FullMemberRole=%s WHERE ServerId=%s;""",(str(role_id),str(message.guild.id)))
            if not result:
                await send_message(message, "Database error!")
                return
            await send_message(message, "Full member role set up successfully.")        
        elif command == 'showbanwords':
            try: server_settings[message.guild.id]["AutoBanWords"]
            except:
                await send_message(message, "Auto ban words not set.")
            response = "**Auto ban words**\n\n"
            for word in server_settings[message.guild.id]["AutoBanWords"]:
                response = response + word + ", "
            await send_message(message, response)                        
        else:
            pass
            
        return
    
    for role in message.author.roles:
        if role.id == server_settings[message.guild.id]["AdminRole"] or role.id == server_settings[message.guild.id]["ModeratorRole"]:
            await log_message("Ignoring because user is a mod!")
            return
    try:    
        if server_settings[message.guild.id]["AutoMuteWords"] is not None:

            for word in server_settings[message.guild.id]["AutoMuteWords"]:
                if re.search(word, message.content, re.S | re.MULTILINE | re.IGNORECASE):
                    await message.delete()
                    await direct_message(user, "You have been muted in " + message.guild.name + " for using the word " + word + ".")
                    new_role = discord.utils.get(message.guild.roles, id=server_settings[message.guild.id]["NewMemberRole"])
                    await user.remove_roles(*message.author.roles[1:],atomic=True)
                    await message.author.add_roles(new_role) 
                    #await user.edit(mute=True)
                    await send_message(message, "User " + message.author.display_name + " has been muted!")
                    await commit_sql("""INSERT INTO DeletedMessages (ServerId, UserId, ChannelId, MessageId, MessageContent, ActionTaken, Reason) VALUES (%s, %s, %s, %s, %s, %s, %s);""", (str(message.guild.id), str(message.author.id), str(message.channel.id), str(message.id), message.content, 'UserMuted', 'user used word ' + word))
    except:
        pass
    try:
        if server_settings[message.guild.id]["AutoKickWords"] is not None:
            for word in server_settings[message.guild.id]["AutoKickWords"]:
                if re.search(word, message.content, re.S | re.MULTILINE | re.IGNORECASE):
                    await message.delete()
                    await direct_message(user, "You have been kicked from " + message.guild.name + " for using the word " + word + ".")
                    await message.author.kick()
                    #await user.edit(mute=True)
                    await send_message(message, "User " + user.name + " has been kicked!")
                    await commit_sql("""INSERT INTO DeletedMessages (ServerId, UserId, ChannelId, MessageId, MessageContent, ActionTaken, Reason) VALUES (%s, %s, %s, %s, %s, %s, %s);""", (str(message.guild.id), str(message.author.id), str(message.channel.id), str(message.id), message.content, 'UserKicked', 'user used word ' + word))
    except:
        pass
        
    try:

        if server_settings[message.guild.id]["AutoBanWords"] is not None:
            for word in server_settings[message.guild.id]["AutoBanWords"]:
                if re.search(word, message.content, re.S | re.MULTILINE | re.IGNORECASE):
                    await message.delete()
                    await direct_message(message.author, "You have been banned from " + message.guild.name + " for using the word " + word + ".")
                    await mesage.author.ban()
                    #await user.edit(mute=True)
                    await commit_sql("""INSERT INTO DeletedMessages (ServerId, UserId, ChannelId, MessageId, MessageContent, ActionTaken, Reason) VALUES (%s, %s, %s, %s, %s, %s, %s);""", (str(message.guild.id), str(message.author.id), str(message.channel.id), str(message.id), message.content, 'UserBanned', 'user used word ' + word))
                    await send_message(message, "User " + message.author.display_name + " has been banned!")             
    except:
        pass
        
client.loop.create_task(bot_scheduler())
client.run'REDACTED'

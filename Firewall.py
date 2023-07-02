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
import ast
import json
import aiohttp

intents = discord.Intents.all()

client = discord.Client(heartbeat_timeout=600,intents=intents)

invite_link = 'https://discord.com/api/oauth2/authorize?client_id=787783371819843584&permissions=8&scope=bot'

server_settings = {}

verify_settings = {}

ignore_channels = {}

badwords = {}

default_ban_events = 5
default_ban_time = 30

default_channel_events = 3
default_channel_time = 30

default_role_events = 5
default_role_time = 20

default_emoji_events = 10
default_emoji_time = 10

default_mention_limit = 5

default_min_age = 1

default_picture_limit = 10
default_picture_time = 300
picture_count = {}


possible_insults = ["Your mother was a hamster, and your father smelled of elderberries!","You suck more than Mocia Lewinsky during an EF5 tornado hitting a vacuum cleaner store.", "Your mother wears combat boots.", "You brobdinagian asshole.", "Fuck you, you fucking fucker.", "I bite my thumb at you.", "You smell so badly Speed Stick slows down and stops.", "Damn, when did your neck throw up? Oh shit, that's your face!", "Man, even Bill Clinton would say, \"No Thanks,\" if he saw you.", "You needle-dicked bastard!", "What's the matter, is it your time of the month 24/7?", "ID10T error: YOU!", "You're an idiot.", "You're dumber than a box of rocks.", "If you rode the short bus, the bus would have to be two-dimensional!", "If brains were gasoline, you wouldnt' have enough to power an ant's motorcycle around the outside of a penny!", "You're a waste of oxygen, so what should you stop doing?", "Don't burst an artery trying to think of a comeback, Einstein!", "Fuck you!", "You're so poor you can't afford free parking!", "You couldn't satisfy a paramecium with that penis!", "I've seen better chatting on AOL.", "I'm not even deigning to insult you.","Your ass is so big that it has its own gravitational pull!", "The 1970s called, they want their lack of style back.", "You mewling shrew!", "Where'd you get the clothes, the toilet store?", "You look like a bucket of shit!", "You look like a bag of dicks!", "You’re an emotional fucking cripple. Your soul is dogsshit. Every single fucking thing about you is ugly.", "What you've just said is one of the most insanely idiotic things I have ever heard. At no point in your rambling, incoherent response were you even close to anything that could be considered a rational thought. Everyone in this room is now dumber for having listened to it. I award you no points, and may God have mercy on your soul.", "You cock-juggling thundercunt!", "You're a shitlord!", "Does Barry Manilow know that you raid his wardrobe?", "Watching you think is like watching a bunch of retards trying to hump a doorknob!", "You're about as useful as a poopy-flavored lollipop!", "You know what the difference between your momma and a washing machine is? When I dump a load in a machine, the machine doesn't follow me around for three weeks.","You horse manure smelling motherfucker, you.", "You’re a virgin and you can’t drive.", "You're somewhere between a cockroach and that white stuff that accumulates at the corner of your mouth when you're really thirsty.", "I'd rather smell dick cheese than you!", "You have more sand in your vagina than the Sahara desert!", "You smell like rendered horse, you burning asshole.", "You can go suck a fuck.", "You may look like an idiot and talk like an idiot but don't let that fool you – you really are an idiot.", "That's all you got, lady - two wrong feet and fucking ugly shoes.", "You hit like a vegetarian.", "To call you stupid would be an insult to stupid people.", "I don’t give a tuppeny fuck about your moral conundrum, you meat-headed shit sack.", "You're in more dire need of a blowjob than any man in history.", "You are literally too stupid to insult.", "Listen, you insignificant, square-toed, pimple-headed spy!", "You're what the French call: 'les incompetents'.", "YOU'RE AN INANIMATE FUCKING OBJECT!", "Allow me to pop a jaunty little bonnet on your purview and ram it up your ass with a lubricated horse cock.", "Go fornicate yourself with a rusty iron rod wrapped in razor wire.", "I should have had you wear double condoms. Well, we shouldn't have done it in the first place, but if you ever do it again, which as a favour to women everywhere, you should not, but if you do, you should be wearing condom on condom, and then wrap it in electrical tape. You should just walk around always inside a great big condom because you are shit!","Your face looks like Robin Williams' knuckles.", "Were you always this stupid or did you take lessons?", "My great aunt Jennifer ate a whole box of candy every day of her life. She lived to be 102 and when she'd been dead three days, she looked better than you do now.", "Your mummy is a TWIT.", "I’ll tell you what. The day I need a friend like you, I’ll just have myself a little squat and shit one out.", "I want to tell you what a cheap, lying, no-good, rotten, four-flushing, low-life, snake-licking, dirt-eating, inbred, overstuffed, ignorant, blood-sucking, dog-kissing, brainless, dickless, hopeless, heartless, fat-ass, bug-eyed, stiff-legged, spotty-lipped, worm-headed sack of monkey shit you are!", "I wouldn't live with you if the world were flooded with piss and you lived in a tree.", "Are you a special agent sent here to ruin my evening and possibly my entire life?", "You're a real blue flame special, aren't you, son? Young, dumb and full of cum. What I don't know is how you got assigned here. Guess we must just have ourselves an asshole shortage, huh?", "I'll explain and I'll use small words so that you'll be sure to understand, you warthog faced buffoon.", "You vomitous mass!", "Is that your nose or did a bus park on your face?", "Even if I were blind, desperate, starved and begging for it on a desert island, you'd be the last thing I'd ever fuck.", "You're tacky and I hate you.", "To everyone here who matters, you're spam. You're vapour. A waste of perfectly good yearbook space.", "Hey laser-lips, your mother was a snowblower.", "You dense, irritating, miniature beast of a burden.", "You know what you look like to me, with your good bag and your cheap shoes? You look like a rube. A well scrubbed, hustling rube with a little taste. Good nutrition has given you some length of bone, but you’re not more than one generation from poor white trash, are you?", "You stuck-up, half-witted, scruffy-looking nerf herder.", "You're just the afterbirth, slithered out on your mother's filth. They should have put you in glass jar on a mantelpiece.", "You dirt-eating piece of slime. You scum-sucking pig. You son of a motherless goat.", "You are a sad strange little man, and you have my pity.", "You are a worthless, friendless, piece of shit whose mommy left daddy when she figured out he wasn't Eugene O'Neill, and who is now weeping and slobbering all over my drum set like a fucking nine-year old girl.", "In the short time we've been together, you have demonstrated every loathsome characteristic of the male personality and even discovered a few new ones. You are physically repulsive, intellectually retarded, you're morally reprehensible, vulgar, insensitive, selfish, stupid, you have no taste, a lousy sense of humour and you smell. You're not even interesting enough to make me sick.", "You clinking, clanking, clattering collection of caliginous junk!", "Your mother should have thrown you away and kept the stork.", "I never forget a face, but in your case, I'll make an exception.", "If your brains were dynamite, there wouldn't be enough to blow your hat off.", "Only two things are infinite-- the universe and your stupidity, and I'm not so sure about the former.", "My opponent is a glob of snot.", "If you won't be a good example, then you'll have to be a horrible warning.", "If I gave you an enema, I could bury you in a matchbox.", "Your ears are so big, you could hang-glide over the Falklands!", "The tautness of your face sours ripe grapes.", "If they can make penicillin out of moldy bread, then they can sure make something out of you.", "Your baby is so ugly, you should have thrown it away and kept the stork.", "You’re a grey sprinkle on a rainbow cupcake.", "If your brain was dynamite, there wouldn’t be enough to blow your hat off.", "You are more disappointing than an unsalted pretzel.", "Light travels faster than sound which is why you seemed bright until you spoke.", "We were happily married for one month, but unfortunately we’ve been married for 10 years.", "Your kid is so ugly, he makes his Happy Meal cry.", "Child, you have so many gaps in your teeth it looks like your tongue is in jail.", "Your secrets are always safe with me. I never even listen when you tell me them.", "I’ll never forget the first time we met. But I’ll keep trying.", "You’d think this baby was born on the highway since that’s where accidents happen.", "I only take you everywhere I go just so I don’t have to kiss you goodbye.", "Hold still. I’m trying to imagine you with personality.", "Our kid must have gotten his brain from you! I still have mine.", "Your face makes onions cry.", "The only way my husband would ever get hurt during an activity is if the TV exploded.", "You look so pretty. Not at all gross, today.", "It’s impossible to underestimate you.", "Her teeth were so bad she could eat an apple through a fence.", "I’m not insulting you, I’m describing you.", "Did you get a fine for littering when you dropped your baby off at daycare?", "Keep rolling your eyes, you might eventually find a brain.", "To teenage daughter: “Learn from my mistakes. Use birth control.”", "You bring everyone so much joy, when you leave the room.", "I thought of you today. It reminded me to take out the trash.", "Don’t worry about me. Worry about your eyebrows.", "You are the human version of period cramps.", "If you’re going to be two-faced, at least make one of them pretty.", "You are like a cloud. When you disappear it’s a beautiful day.", "I’d rather treat my baby’s diaper rash than have lunch with you.", "Don’t worry, the first 40 years of childhood are always the hardest.", "I may love to shop but I will never buy your bull.", "I love what you’ve done with your hair. How do you get it to come out of your nostrils like that?", "Your face is just fine but we’ll have to put a bag over that personality.", "I’m not a nerd, I’m just smarter than you.", "I forgot the world revolves around you. My apologies, how silly of me.", "OH MY GOD! IT SPEAKS!", "You’re the reason God created the middle finger."]

hell = {}

async def reaper(user_id, channel):
    global possible_insults
    await client.wait_until_ready()
    await log_message("Lanuching timer.")
    while True:
        await channel.send(">>> <@" + str(user_id) +">, " + random.choice(possible_insults))
        await asyncio.sleep(15)

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

async def verify_timer():
    global server_settings
    global verify_settings
    
    await client.wait_until_ready()
    await log_message("Lanuching verify timer.")
    while not client.is_closed():
        current_time_obj = datetime.now()
        current_hour = int(current_time_obj.strftime("%H"))
        current_minute = int(current_time_obj.strftime("%M"))
        current_second = int(current_time_obj.strftime("%S"))
        
        while True:
            records = await select_sql("""SELECT ServerId, UserId, JoinTime FROM VerifyTime;""")
            if records:
                for row in records:
                    try:
                        server_obj = client.get_guild(int(row[0]))
                        user = discord.utils.get(server_obj.members, id=int(row[1]))
                    except:
                        continue
                    join_time = row[2]
                    if not user:
                        continue
                    try:
                        if (datetime.now() - join_time).total_seconds() / 60.0 >= verify_settings[int(row[0])]["VerifyTimeout"] and verify_settings[int(row[0])]["VerifyTimeout"] > 0:
                            if verify_settings[server_obj.id]["VerifyTimeoutAction"] == 'kick' and server_obj.me.guild_permissions.kick_members:
                                try:
                                    await user.kick()
                                except:
                                    await server_settings[server_obj.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> Unable to kick " + user.name + " for not verifying."))
                                try:
                                    await server_settings[server_obj.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + user.name + " was kicked for not verifying."))
                                except:
                                    pass
                            elif verify_settings[server_obj.id]["VerifyTimeoutAction"] == 'ban' and server_obj.me.guild_permissions.ban_members:
                                try:
                                    await user.ban()
                                except:
                                    await server_settings[server_obj.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> Unable to ban " + user.name + " for not verifying."))
                                try:
                                    await server_settings[server_obj.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + user.name + " was banned for not verifying."))
                                except:
                                    pass
                            else:
                                try:
                                    await server_settings[server_obj.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + user.name + " exceeded timeout for not verifying, no action taken."))
                                except:
                                    pass
                    except:
                        pass

            await asyncio.sleep(60)
            
#        print("Time " + str(current_hour) + ":" + str(current_minute) + ":" + str(current_second))

        await asyncio.sleep(1)        
connection = mysql.connector.connect(host='localhost', database='Firewall2', user='REDACTED', password='REDACTED', charset="utf8mb4")
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
def reconnect_db():
    global connection
    if connection is None or not connection.is_connected():
        connection = mysql.connector.connect(host='localhost', database='Firewall2', user='REDACTED', password='REDACTED', charset="utf8mb4")
    return connection

    
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


async def execute_sql(sql_query):
    try:
        connection = mysql.connector.connect(host='localhost', database='Firewall2', user='REDACTED', password='REDACTED', charset="utf8mb4")
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
        
# DM a user
async def direct_message(user, response, server=None):
    global server_settings
    if server:
        if server_settings[server.id]["DMStatus"] == 0:
            return
    channel = await user.create_dm()
    await log_message("replied to user " + user.name + " in DM with " + response)
    try:
        await channel.send(response)
    except discord.errors.Forbidden:
        pass
# Message events
@client.event
async def on_message_delete(message):
    global ignore_channels
    global server_settings
    
    if not message.content.strip():
        return
    if message.channel.id in ignore_channels[message.guild.id]:
        return
   
    if message.author != client.user:
        try:
            await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + message.author.name + " had a message deleted in <#" + str(message.channel.id) +"> with content ```" + message.content + "```"))
        except:
            pass

@client.event
async def on_bulk_message_delete(messages):
    pass
    
@client.event
async def on_message_edit(before,after):
    global ignore_channels
    global server_settings
    if before.channel.id in ignore_channels[before.guild.id] or after.channel.id in ignore_channels[after.guild.id]:
        return
    if not before.content.strip():
        return
    if before.content == after.content:
        return
    if before.author != client.user:
        try:
            await server_settings[before.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + before.author.name + " edited a message in <#" + str(before.channel.id) +"> with before content ```" + before.content + "``` and after content of ```" + after.content + "```"))
        except:
            pass

# Private channel events  
@client.event
async def on_private_channel_create(channel):
    global server_settings
    try: channel.guild
    except: return
    async for entry in channel.guild.audit_logs(limit=10,action=discord.AuditLogAction.channel_create):
        if entry.target.id == channel.id:
            user_id = entry.user.id
            username = entry.user.name
            channel_name = channel.name
    try: username
    except: username = "Unknown"            
    try:
        await server_settings[channel.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + username + " created channel named " + channel_name + "."))
    except:
        pass 

@client.event
async def on_private_channel_delete(channel):
    global server_settings
    async for entry in channel.guild.audit_logs(limit=10,action=discord.AuditLogAction.channel_delete):
        if entry.target.id == channel.id:
            user_id = entry.user.id
            username = entry.user.name
            channel_name = channel.name
    try:
        await server_settings[channel.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + username + " deleted channel named " + channel_name + "."))
    except:
        pass            
    result = await commit_sql("""INSERT INTO ChannelHistory (ServerId, UserId, ChannelId, ChannelName, TimeStamp,UserName) VALUES (%s, %s, %s, %s, %s, %s);""",(str(channel.guild.id),str(user_id),str(channel.id),str(channel_name),datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
    records = await select_sql("""SELECT TimeStamp FROM ChannelHistory WHERE ServerId=%s AND UserId=%s ORDER BY TimeStamp DESC LIMIT """ + str(server_settings[channel.guild.id]["ChannelEventCount"]) + ";",(str(channel.guild.id),str(user_id)))
    
    if not records:
        return
    if len(records) < server_settings[channel.guild.id]["ChannelEventCount"]:
        return
    timestamps = []
    for row in records:
        timestamps.append(row[0])
    earliest_time = min(timestamps)
    latest_time = max(timestamps)
    time_seconds = (latest_time - earliest_time).total_seconds()
    
    if len(records) >= server_settings[channel.guild.id]["ChannelEventCount"] and time_seconds <= server_settings[channel.guild.id]["ChannelTimeSeconds"] and user_id not in server_settings[channel.guild.id]["Whitelist"]:
        await quarantine(channel.guild,channel.guild.get_member(user_id),"Quarantined for exceeding channel deletion parameters!")
        try:
            await server_settings[channel.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> User " + username + " was quarantined for exceeding channel deletion parameters!"))
        except:
            pass
    
@client.event
async def on_private_channel_update(channel):
    pass

# Channel events
@client.event
async def on_guild_channel_create(channel):
    global server_settings
    async for entry in channel.guild.audit_logs(limit=10,action=discord.AuditLogAction.channel_create):
        if entry.target.id == channel.id:
            user_id = entry.user.id
            username = entry.user.name
            channel_name = channel.name
    try: username
    except: username = "Unknown"            
    try:
        await server_settings[channel.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + username + " created channel named " + channel_name + "."))
    except:
        pass   


@client.event
async def on_guild_channel_delete(channel):
    global server_settings
    async for entry in channel.guild.audit_logs(limit=10,action=discord.AuditLogAction.channel_delete):
        if entry.target.id == channel.id:
            user_id = entry.user.id
            username = entry.user.name
            channel_name = channel.name
    try: username
    except: username = "Unknown"            
    try:
        await server_settings[channel.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + username + " deleted channel named " + channel_name + "."))
    except:
        pass            
    result = await commit_sql("""INSERT INTO ChannelHistory (ServerId, UserId, ChannelId, ChannelName, TimeStamp,UserName) VALUES (%s, %s, %s, %s, %s, %s);""",(str(channel.guild.id),str(user_id),str(channel.id),str(channel_name),datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
    records = await select_sql("""SELECT TimeStamp FROM ChannelHistory WHERE ServerId=%s AND UserId=%s ORDER BY TimeStamp DESC LIMIT """ + str(server_settings[channel.guild.id]["ChannelEventCount"]) + ";",(str(channel.guild.id),str(user_id)))
    
    if not records:
        return
    if len(records) < server_settings[channel.guild.id]["ChannelEventCount"]:
        return
    timestamps = []
    for row in records:
        timestamps.append(row[0])
    earliest_time = min(timestamps)
    latest_time = max(timestamps)
    time_seconds = (latest_time - earliest_time).total_seconds()
    
    if len(records) >= server_settings[channel.guild.id]["ChannelEventCount"] and time_seconds <= server_settings[channel.guild.id]["ChannelTimeSeconds"] and user_id not in server_settings[channel.guild.id]["Whitelist"]:
        await quarantine(channel.guild,channel.guild.get_member(user_id),"Quarantined for exceeding channel deletion parameters!")
        try:
            await server_settings[channel.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> User " + username + " was quarantined for exceeding channel deletion parameters!"))
        except:
            pass
        
    
    

@client.event
async def on_guild_channel_update(before,after):
    global ignore_channels
    global server_settings
    if before.id in ignore_channels[before.guild.id]:
        return
    async for entry in before.guild.audit_logs(limit=10,action=discord.AuditLogAction.channel_delete):
        if entry.target.id == before.id:
            user_id = entry.user.id
            username = entry.user.name
            channel_name = before.name
    try: username
    except: username = "Unknown"            
    response = "**Channel update by** `" + username + "`:\n\n"
    if before.name == after.name:
        response = response + "**Channel** `" + before.name + "`"
    if before.name != after.name:
        response = response + "Channel name changed from `" + before.name + "` to `" + after.name + "`."
    if before.category != after.category:
        response = response + "Category changed from `" + before.category.name + "` to `" + after.category.name + "`.\n"
    if before.position != after.position:
        response = response + "Position changed from `" + str(before.position) + "` to `" + str(after.position) + "`.\n"
    if before.overwrites != after.overwrites:
        response = response + "Permissions changed for channel.\n"
        
    try:
        await server_settings[before.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + response))
    except:
        pass   

@client.event
async def on_voice_state_update(member, before, after):
    global server_settings
    global ignore_channels
    if before.channel:
        
        if before.channel.id in ignore_channels[before.channel.guild.id]:
            return
    print("Voice update.")
    response = "**Voice state update for** `" + member.name + "`.\n\n"
    if not before.channel and after.channel:
        response = response + "User joined channel `"  + after.channel.name + "`.\n"
    if before.channel and not after.channel:
        response = response + "User left channel `" + before.channel.name + "`.\n"
    if before.channel == after.channel:
        response = response + "In channel `" + before.channel.name + "`.\n"
    if not before.self_mute and after.self_mute:
        response = response + "User muted self.\n"
    if before.self_mute and not after.self_mute:
        response = response + "User unmuted self.\n"
    if not before.self_deaf and after.self_deaf:
        response = response + "User deafened self.\n"
    if before.self_deaf and not after.self_deaf:
        response = response + "User undeafened self.\n"
    if not before.self_stream and after.self_stream:
        response = response + "User started streaming.\n"
    if before.self_stream and not after.self_stream:
        response = response + "User ended streaming.\n"
    if not before.self_video and after.self_video:
        response = response + "User started video.\n"
    if before.self_video and not after.self_video:
        response = response + "User ended video.\n"
    if not before.mute and after.mute:
        response = response + "User muted by guild.\n"
    if before.mute and not after.mute:
        response = response + "User unmuted by guild.\n"
    if not before.deaf and after.deaf:
        response = response + "User deafened by guild.\n"
    if before.deaf and not after.deaf:
        response = response + "User undeafened by guild.\n"
    try:
        await server_settings[member.guild.id]["MemberLogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + response))
    except:
        pass         
# Role events
@client.event
async def on_guild_role_create(role):
    global server_settings
    async for entry in role.guild.audit_logs(limit=10,action=discord.AuditLogAction.role_create):
        if entry.target.id == role.id:
            user_id = entry.user.id
            username = entry.user.name
            role_name = role.name
    try: 
        await server_settings[role.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> Role "  + role_name + " was created by " + username + " at "  + str(datetime.now())))        
    except:
        pass
    
@client.event
async def on_guild_role_delete(role):
    global server_settings
    await log_message("Role deleted!")
    async for entry in role.guild.audit_logs(limit=10,action=discord.AuditLogAction.role_delete):
        if entry.target.id == role.id:
            user_id = entry.user.id
            username = entry.user.name
            role_name = role.name
    try: username
    except: username = "Unknown"            
    try:        
        await server_settings[role.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> Role "  + role_name + " was deleted by " + username + " at "  + str(datetime.now())))        
    except:
        pass
    result = await commit_sql("""INSERT INTO RoleHistory (ServerId, UserId, RoleId, RoleName, TimeStamp,UserName) VALUES (%s, %s, %s, %s, %s, %s);""",(str(role.guild.id),str(user_id),str(role.id),str(role_name),datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
    records = await select_sql("""SELECT TimeStamp FROM RoleHistory WHERE ServerId=%s AND UserId=%s ORDER BY TimeStamp DESC LIMIT """ + str(server_settings[role.guild.id]["RoleEventCount"]) + ";",(str(role.guild.id),str(user_id)))
    
    if not records:
        return
    if len(records) < server_settings[role.guild.id]["RoleEventCount"]:
        return
    timestamps = []
    for row in records:
        timestamps.append(row[0])
    earliest_time = min(timestamps)
    latest_time = max(timestamps)
    time_seconds = (latest_time - earliest_time).total_seconds()
    
    if len(records) >= server_settings[role.guild.id]["RoleEventCount"] and time_seconds <= server_settings[role.guild.id]["RoleTimeSeconds"] and user_id not in server_settings[role.guild.id]["Whitelist"]:
        await quarantine(role.guild,role.guild.get_member(user_id),"Quarantined for exceeding role deletion parameters!")
        try:
            await server_settings[role.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> User " + username + " was quarantined for exceeding role deletion parameters!"))
        except:
            pass        
    
@client.event
async def on_guild_role_update(before,after):
    global server_settings
    async for entry in before.guild.audit_logs(limit=10,action=discord.AuditLogAction.role_update):
        if entry.target.id == before.id:
            user_id = entry.user.id
            username = entry.user.name
            before_name = before.name
            role_name = after.name
    try: username
    except: username = "Unknown"
    response = "**Role update by** `" + username + "`\n\n"
    try:
        before_name
    except:
        return
    if before.name == after.name:
        response = response + "**Role** `" + before.name + "`\n"
    if re.search(r"everyone",before_name):
        return
    if before.name != after.name:
        response = response + "Role name changed from `" + before_name + "` to `" + role_name + "`.\n"
    if before.color != after.color:
        response = response + "Role color change from `" + str(before.color.value) + "` to `" + str(after.color.value) + "`.\n"
    if before.position != after.position:
        response = response + "Role position change from `" + str(before.position) + "` to `" + str(after.position) + "`.\n"
    if before.permissions != after.permissions:
        response = response + "Role permissions changed.\n"
        
    try:        
        await server_settings[before.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + response + "\n\n at "  + str(datetime.now())))        
    except:
        pass

# Emoji events  
@client.event
async def on_guild_emojis_update(guild, before, after):
    global server_settings
    emojis_added = ""
    emojis_deleted = ""
    emoji_list = [] 
    for emoji in before:
        if emoji not in after:
            emojis_deleted = emojis_deleted + " " + str(emoji)
            emoji_list.append(emoji.id)
    for emoji in after:
        if emoji not in before:
            emojis_added = emojis_added + " " + str(emoji)
    async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.emoji_delete):
        await log_message(str(entry))
        username = entry.user.name
        user_id = entry.user.id
    try: username
    except: username = "Unknown"        
            
    result = await commit_sql("""INSERT INTO EmojiHistory (ServerId, UserId, EmojisAdded, EmojisDeleted, TimeStamp, UserName) VALUES (%s, %s, %s, %s, %s, %s);""",(str(guild.id),str(user_id),emojis_added,emojis_deleted,datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
    records = await select_sql("""SELECT TimeStamp FROM EmojiHistory WHERE ServerId=%s AND UserId=%s ORDER BY TimeStamp DESC LIMIT """ + str(server_settings[guild.id]["EmojiEventCount"]) + ";",(str(guild.id),str(user_id)))
    
    if not records:
        return
    if len(records) < server_settings[guild.id]["EmojiEventCount"]:
        return
    timestamps = []
    for row in records:
        timestamps.append(row[0])
    earliest_time = min(timestamps)
    latest_time = max(timestamps)
    time_seconds = (latest_time - earliest_time).total_seconds()
    
    if len(records) >= server_settings[guild.id]["EmojiEventCount"] and time_seconds <= server_settings[guild.id]["EmojiTimeSeconds"] and user_id not in server_settings[guild.id]["Whitelist"]:
        await quarantine(guild,guild.get_member(user_id),"Quarantined for exceeding emoji deletion parameters!")    
        try:
            await server_settings[guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> User " + username + " was quarantined for exceeding emoji deletion parameters!"))
        except:
            pass        
    
# Ban events
@client.event
async def on_member_ban(guild,user):
    global server_settings
    
    async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.ban):

        user_id = entry.user.id
        username = entry.user.name
        banned_username = entry.target.name
        banned_user_id = entry.target.id
    try: username
    except: username = "Unknown"
    try:
        await server_settings[guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + username + " banned " + banned_username + "."))
    except:
        pass
    result = await commit_sql("""INSERT INTO BanHistory (ServerId, UserId, BannedUserId, BannedUserName, TimeStamp, UserName) VALUES (%s, %s, %s, %s, %s, %s);""",(str(guild.id),str(user_id),str(banned_user_id),str(banned_username),datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username))
    records = await select_sql("""SELECT TimeStamp FROM BanHistory WHERE ServerId=%s AND UserId=%s ORDER BY TimeStamp DESC LIMIT """ + str(server_settings[guild.id]["BanEventCount"]) + ";",(str(guild.id),str(user_id)))
    
    if not records:
        return
    if len(records) < server_settings[guild.id]["BanEventCount"]:
        return
    timestamps = []
    for row in records:
        timestamps.append(row[0])
    earliest_time = min(timestamps)
    latest_time = max(timestamps)
    time_seconds = (latest_time - earliest_time).total_seconds()
    
    if len(records) >= server_settings[guild.id]["BanEventCount"] and time_seconds <= server_settings[guild.id]["BanTimeSeconds"] and user_id not in server_settings[guild.id]["Whitelist"]:
        await quarantine(guild,guild.get_member(user_id),"Quarantined for exceeding ban parameters!")  
        try:
            await server_settings[guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> User " + username + " was quarantined for exceeding member ban parameters!"))
        except:
            pass
    
    
@client.event
async def on_member_unban(guild, user):
    global server_settings
    async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.unban):
        if user.id == entry.target.id:
            user_id = entry.user.id
            username = entry.user.name
            banned_username = entry.target.name
            banned_user_id = entry.target.id
    try: username
    except: username = "Unknown"            
    try:
        await server_settings[guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + username + " unbanned " + banned_username + "."))
    except:
        pass    
# invite events    
@client.event
async def on_invite_create(invite):
    global server_settings
    try:
        code = invite.code
    except:
        code = "Unknown"
    try:
        user = invite.inviter.name
    except:
        user = "Unknown"
    try:
        chann = invite.channel.name
    except:
        chann = "Unknown" 
    response = "Invite `" + code + "` created by + `" + user + "` for channel `" + chann + "`.\n"
    try:
        await server_settings[guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + response))
    except:
        pass    
    
    
    
@client.event
async def on_invite_delete(invite):
    global server_settings
    try:
        code = invite.code
    except:
        code = "Unknown"
    try:
        user = invite.inviter.name
    except:
        user = "Unknown"
    try:
        chann = invite.channel.name
    except:
        chann = "Unknown"
    response = "Invite `" + code + "` deleted by + `"  + user + "` for channel `" + chann + "`.\n"
    try:
        await server_settings[guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + response))
    except:
        pass  
    
# Server backups
async def take_backup():
    pass

# Whitelist check
async def security_check(guild_id,user_id):
    global server_settings
    
    if user_id in server_settings[guild_id]["Whitelist"]:
        return True
    else:
        return False
        
# Ensure a lower moderator cannot ban/kick/mute a higher moderator or admin        
async def role_compare(user1, user2):
    if user1.top_role <= user2.top_role:
        return False
    else:
        return True
        
# Quarantine User
async def quarantine(guild, user, reason):
    global server_settings
    role_list = ""
    for role in user.roles[1:]:
        role_list = role_list + str(role.id) + ","
    role_list = re.sub(r",$","",role_list)
    user_roles = []
    result = await commit_sql("""INSERT INTO Quarantine (ServerId, UserId, UserRoles, Reason, TimeStamp) VALUES (%s, %s, %s, %s, %s);""",(str(guild.id),str(user.id),str(role_list),reason,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    q_role = discord.utils.get(guild.roles, name="quarantine")
    
    if not q_role:
        perms = discord.Permissions(send_messages=False,read_messages=False)
        q_role = await guild.create_role(name="quarantine",reason=reason)
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.read_messages = False
        for channel in guild.channels:
            if channel.id != server_settings[guild.id]["GatewayChannelId"]:
                await channel.set_permissions(q_role, overwrite=overwrite)        
    await user.add_roles(q_role)    
    for role in reversed(user.roles[1:]):
        if role.name != "quarantine":
            await user.remove_roles(role)
    

    return True
@client.event
async def on_member_update(before, after):
    global server_settings
    if before.bot:
        return
  
    response = "**Member Update for:  " + before.name + "**\n\n"
    if before.name != after.name:
        response = response + "Name change from `" + before.name + "` to `" + after.name + "`.\n"
    if before.display_name != after.display_name:
        response = response + "Display name change from `" + before.display_name + "` to `" + after.display_name + "`.\n"
    for before_role in before.roles:
        if before_role not in after.roles:
            response = response + "Removed role `" + before_role.name + "`.\n"
    try:
        if before.nick != after.nick:
            response = response + "Nickname change from `" + before.nick + "` to `" + after.nick + "`."
    except:
        pass
    for after_role in after.roles:
        if after_role not in before.roles:
            response = response + "Added role `" + after_role.name + "`.\n"
    try: before_activity = before.activity.name
    except: before_activity = "None"
    try: after_activity = after.activity.name
    except: after_activity = "None"
    if not before.activity or before.activity is None:
        before_activity = "None"
    if not after.activity or after.activity is None:
        after_activity = "None"
        
    if before.activity != after.activity:
        try:
            response = response + "User changed activity from `" + before_activity + "` to `" + after_activity + "`.\n"
        except:
            response = response + "User changed activity but the change is unknown.\n"
    if before_activity == 'Spotify' and after_activity == 'Spotify':
        return
    if before.status != after.status:
        response = response + "User status changed from `" + str(before.status) + "` to `" + str(after.status) + "`.\n"
    if response ==  "**Member Update for:  " + before.name + "**\n\n":
        return
    try:
        await server_settings[before.guild.id]["MemberLogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + response))
    except:
        pass
        
@client.event            
async def on_user_update(before,after):
    global server_settings
    response = "**Member Update for:  " + before.name + "**\n\n"
    if before.name != after.name:
        response = response + "Name change from `" + before.name + "` to `" + after.name + "`.\n"
    if before.avatar != after.avatar:
        response = response + "Avatar change to "
    if before.discriminator != after.discriminator:
        response = response + "Discriminator change from `" + before.discriminator +  "` to `" + after.discriminator + "`."
#    try:
    for guild in client.guilds:
        user = discord.utils.get(guild.members,id=after.id)
        if user:
            embed=discord.Embed(title="Firewall Log",description=">>> " + response)
            if re.search(r"Avatar",response):
                embed.set_thumbnail(url=str(after.avatar))
            try:
                await server_settings[user.guild.id]["LogChannel"].send(embed=embed)
            except:
                pass
#    except:
#        pass
        
# Unquarantine user
async def unquarantine(guild, user):
    records = await select_sql("""SELECT Id,UserRoles FROM Quarantine WHERE ServerId=%s AND UserId=%s;""",(str(guild.id),str(user.id)))
    if not records:
        return False
    
    for row in records:
        record_id = row[0]
        user_roles = row[1]
    role_assign = []    
    for user_role in user_roles.split(','):
        try:
            role_assign.append(guild.get_role(int(user_role)))
        except:
            pass
        
    for role in user.roles[1:]:
        if role.name == "quarantine":
            await user.remove_roles(role)
            
    for role in role_assign:
        try:
            await user.add_roles(role)
        except:
            pass
    
    
    result = await commit_sql("""DELETE FROM Quarantine WHERE Id=%s;""",(str(record_id),))
    return True
# Restore server
async def restore_backup():
    pass
    
# Bot code
@client.event
async def on_ready():
    global server_settings
    global verify_settings
    global ignore_channels
    global hell
    global badwords
    global picture_count
    
    for guild in client.guilds:
        server_settings[guild.id] = {}
        server_settings[guild.id]["Whitelist"] = []
        server_settings[guild.id]["Whitelist"].append(guild.owner.id)
        verify_settings[guild.id] = {}
        ignore_channels[guild.id] = []
        server_settings[guild.id]["GatewayChannelId"] = 0
        hell[guild.id] = {}
        badwords[guild.id] = []
        picture_count[guild.id] = {}
        for user in guild.members:
            picture_count[guild.id][user.id] = {}
            picture_count[guild.id][user.id]["PictureCount"] = 0
            picture_count[guild.id][user.id]["LastPicturePosted"] = []
            picture_count[guild.id][user.id]["LastPictureCount"] = []

    records = await select_sql("""SELECT ServerId, BanEventCount, BanTimeSeconds, EmojiEventCount, EmojiTimeSeconds, ChannelEventCount, ChannelTimeSeconds, RoleEventCount, RoleTimeSeconds,LogChannelId,MentionLimit,MinimumAccountAge,MemberLogChannelId,Greeting,GreetingChannelId,BadWordAction,PictureLimit,PictureTimeSeconds, DMStatus, Farewell FROM ServerSettings;""")
    if records:
        for row in records:
            try:
                server_settings[int(row[0])]
            except:
                server_settings[int(row[0])] = {}
            server_settings[int(row[0])]["BanEventCount"] = int(row[1])
            server_settings[int(row[0])]["BanTimeSeconds"] = int(row[2])
            server_settings[int(row[0])]["EmojiEventCount"] = int(row[3])
            server_settings[int(row[0])]["EmojiTimeSeconds"] = int(row[4])
            server_settings[int(row[0])]["ChannelEventCount"] = int(row[5])
            server_settings[int(row[0])]["ChannelTimeSeconds"] = int(row[6])
            server_settings[int(row[0])]["RoleEventCount"] = int(row[7])
            server_settings[int(row[0])]["RoleTimeSeconds"] = int(row[8])
            try:
                server_settings[int(row[0])]["LogChannel"] = client.get_channel(int(row[9]))
            except:
                pass
            server_settings[int(row[0])]["MentionLimit"] = int(row[10])
            server_settings[int(row[0])]["MinimumAccountAge"] = int(row[11])
            try:
                server_settings[int(row[0])]["MemberLogChannel"] = client.get_channel(int(row[12]))
            except:
                pass
            server_settings[int(row[0])]["Greeting"] = row[13]
            try:
                server_settings[int(row[0])]["GreetingChannel"]  = client.get_channel(int(row[14]))
            except:
                pass
            server_settings[int(row[0])]["BadWordAction"] = row[15]
            server_settings[int(row[0])]["PictureLimit"] = int(row[16])
            server_settings[int(row[0])]["PictureTimeSeconds"] = int(row[17])
            server_settings[int(row[0])]["DMStatus"] = int(row[18])
            server_settings[int(row[0])]["Farewell"] = row[19]
            try:
                server_settings[int(row[0])]["DMStatus"] 
            except:
                server_settings[int(row[0])]["DMStatus"] = True
            print(server_settings[int(row[0])])
            
    records = await select_sql("""SELECT ServerId,UserId FROM ServerWhitelist;""")
    if records:
        for row in records:
#            try:
            server_settings[int(row[0])]["Whitelist"].append(int(row[1]))
      
    print("SERVER WHITELIST: ")
    for server in server_settings:
        try:
            server_settings[server]["Whitelist"]
        except:
            continue
        for user in server_settings[server]["Whitelist"]:
            print(str(server) + " - " + str(user))
#            except:
 #               pass
    
    records = await select_sql("""SELECT ServerId, VerifyOn, GatewayChannelId, ConfirmMessage, ConfirmMessageId, VerifyEmoji, MemberRole, IFNULL(VerifyTimeout,'0'), VerifyTimeoutAction FROM Verify;""")
    if records:
        for row in records:
            try:
                verify_settings[int(row[0])]
            except:
                verify_settings[int(row[0])] = {}        
            if row[1] == 0:
                verify_settings[int(row[0])]["VerifyOn"] = False
                continue
            else:
                verify_settings[int(row[0])]["VerifyOn"] = True
            try:
                verify_settings[int(row[0])]["GatewayChannelId"] = int(row[2])
                verify_settings[int(row[0])]["ConfirmMessage"] = row[3]
                verify_settings[int(row[0])]["ConfirmMessageId"] = int(row[4])
                verify_settings[int(row[0])]["VerifyEmoji"] = row[5]
                verify_settings[int(row[0])]["MemberRole"] = int(row[6])
                verify_settings[int(row[0])]["VerifyTimeout"] = int(row[7])
                verify_settings[int(row[0])]["VerifyTimeoutAction"] = row[8]
            except:
                pass
            
    records = await select_sql("""SELECT ServerId,ChannelId FROM IgnoreChannels;""")
    if records:
        for row in records:
            print("Ignoring channel: " + str(row[1]))
            try:
                ignore_channels[int(row[0])]
            except:
                ignore_channels[int(row[0])] = []
            ignore_channels[int(row[0])].append(int(row[1]))
    records = await select_sql("""SELECT ServerId, BadWord FROM BadWords;""")
    if records:
        for row in records:
            try:
                badwords[int(row[0])]
            except:
                badwords[int(row[0])] = []
            badwords[int(row[0])].append(row[1])
            
    await client.loop.create_task(verify_timer())        
    await log_message("Logged into Discord!")
    
    
    
        

# Guild events
@client.event
async def on_guild_join(guild):
    global default_ban_events
    global default_ban_time
    global default_channel_events
    global default_channel_time
    global default_emoji_events
    global default_emoji_time
    global default_role_events
    global default_emoji_time
    global default_mention_limit
    global default_min_age
    global server_settings
    global verify_settings
    global ignore_channels
    global hell
    global badwords
    global default_picture_limit
    global default_picture_time
    
    hell[guild.id] = {}
    
    await log_message("Joined guild " + guild.name)
    result = await commit_sql("""INSERT INTO ServerSettings (ServerId, BanEventCount, BanTimeSeconds, EmojiEventCount, EmojiTimeSeconds, ChannelEventCount, ChannelTimeSeconds, RoleEventCount, RoleTimeSeconds, MentionLimit, MinimumAccountAge, BadWordAction, PictureLimit, PictureTimeSeconds, DMStatus) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0);""",(str(guild.id), str(default_ban_events), str(default_ban_time), str(default_emoji_events), str(default_emoji_time), str(default_channel_events),str(default_channel_time), str(default_role_events), str(default_role_time), str(default_mention_limit),str(default_min_age),'none',str(default_picture_limit), str(default_picture_time)))
    server_settings[guild.id] = {} 
    server_settings[guild.id]["BanEventCount"] = default_ban_events
    server_settings[guild.id]["BanTimeSeconds"] = default_ban_time
    server_settings[guild.id]["EmojiEventCount"] = default_emoji_events
    server_settings[guild.id]["EmojiTimeSeconds"] = default_emoji_time
    server_settings[guild.id]["ChannelEventCount"] = default_channel_events
    server_settings[guild.id]["ChannelTimeSeconds"] = default_channel_time
    server_settings[guild.id]["RoleEventCount"] = default_role_events
    server_settings[guild.id]["RoleTimeSeconds"] = default_role_time
    server_settings[guild.id]["MentionLimit"] = default_mention_limit
    server_settings[guild.id]["MinimumAccountAge"] = default_min_age
    server_settings[guild.id]["Whitelist"] = []
    server_settings[guild.id]["Whitelist"].append(guild.owner.id)
    server_settings[guild.id]["GatewayChannelId"] = 0
    server_settings[guild.id]["PictureLimit"] = default_picture_limit
    server_settings[guild.id]["PictureTimeSeconds"] = default_picture_time
    result = await commit_sql("""INSERT INTO Verify (ServerId, VerifyOn) VALUES (%s, 0);""",(str(guild.id),))
    verify_settings[guild.id] = {} 
    verify_settings[guild.id]["VerifyOn"] = False
    ignore_channels[guild.id] = []
    server_settings[guild.id]["BadWordAction"] = "none"
    badwords[guild.id] = []
    server_settings[guild.id]["DMStatus"] = 0
    
    
	
@client.event
async def on_guild_remove(guild):
    global server_settings
    del server_settings[guild.id]
    result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s;""",(str(guild.id),))
    result = await commit_sql("""DELETE FROM ChannelHistory WHERE ServerId=%s;""",(str(guild.id),))
    result = await commit_sql("""DELETE FROM EmojiHistory WHERE ServerId=%s;""",(str(guild.id),))
    result = await commit_sql("""DELETE FROM RoleHistory WHERE ServerId=%s;""",(str(guild.id),))
    result = await commit_sql("""DELETE FROM BanHistory WHERE ServerId=%s;""",(str(guild.id),))
    result = await commit_sql("""DELETE FROM ServerWhitelist WHERE ServerId=%s;""",(str(guild.id),))
    result = await commit_sql("""DELETE FROM Verify WHERE ServerId=%s;""",(str(guild.id),))
    await log_message("Left guild " + guild.name)
    

# Member events	
@client.event
async def on_member_join(member):
    global server_settings
    global verify_settings
    user = member
    embed = discord.Embed(title="Who is " + user.name)
    embed.add_field(name="Username:",value=user.name)
    embed.add_field(name="Discriminator:",value=str(user.discriminator))
    if user.nick:
        embed.add_field(name="Nickname:",value=str(user.nick))
    embed.add_field(name="User ID:",value=str(user.id))
    embed.add_field(name="Account Created:",value=str(user.created_at))
    embed.add_field(name="Joined server:",value=str(user.joined_at))
    embed.add_field(name="Status:",value=str(user.status))
    embed.add_field(name="Activity:",value=str(user.activity))
    embed.add_field(name="Top Role:",value=str(user.top_role.name))
    role_list = ""
    for role in user.roles:
        role_list = role_list + " " + role.name
        embed.add_field(name="Role List:",value=role_list)
    if user.web_status:
        embed.add_field(name="Web Status:",value=str(user.web_status))
    if user.mobile_status:
        embed.add_field(name="Mobile Status:",value=str(user.mobile_status))
    if user.desktop_status:
        embed.add_field(name="Desktop Status:",value=str(user.desktop_status))
    if user.voice:
        embed.add_field(name="Voice State:",value=str(user.voice))

    if user.premium_since:
        embed.add_field(name="Premium Since:",value=str(user.premium_since))
    if user.avatar:
        embed.set_thumbnail(url=str(user.avatar))
    if user.bot:
        embed.add_field(name="Bot:",value=str(user.bot))
    if user.color:
        embed.add_field(name="Color",value=str(user.color))
    try:
        await server_settings[member.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + member.name + " has joined the server."))
    except:
        pass
    try:
        await server_settings[member.guild.id]["LogChannel"].send(embed=embed)
    except:
        pass
    try:
        server_settings[member.guild.id]["MinimumAccountAge"]
    except:
        server_settings[member.guild.id]["MinimumAccountAge"] = 0
    naive = member.created_at.replace(tzinfo=None)
    if server_settings[member.guild.id]["MinimumAccountAge"] >= 1:
        if (datetime.now() - naive).total_seconds() <= (60* 60 * 24) * server_settings[member.guild.id]["MinimumAccountAge"]:
            result = await quarantine(member.guild, member, "Quarantined for account age being less than " + str(server_settings[member.guild.id]["MinimumAccountAge"]) + " days old.")
            if result:
                try:
                    await server_settings[member.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + member.name + " has been quarantined because the account is less than " + str(server_settings[member.guild.id]["MinimumAccountAge"]) + " days old."))
                except:
                    pass
            await direct_message(member, "Your account is less than " + str(server_settings[member.guild.id]["MinimumAccountAge"]) + " days old, so your posting privileges have been muted. Please contact a moderator or administrator for verification.", member.guild)

    try: 
        verify_settings[member.guild.id]["VerifyOn"]
    except:
        verify_settings[member.guild.id]["VerifyOn"] = False
        
    if verify_settings[member.guild.id]["VerifyOn"]:
        result = await quarantine(member.guild, member, "Quarantined because verification is on.")
        if result:
            try:
                await server_settings[member.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + member.name + " has been quarantined because verification is on."))
            except:
                pass
        await commit_sql("""INSERT INTO VerifyTime (ServerId, UserId, JoinTime) VALUES (%s, %s, %s);""",(str(member.guild.id),str(member.id),str(datetime.now())))
        await direct_message(member, "This server has verification turned on. Please verify in <#" + str(verify_settings[member.guild.id]["GatewayChannelId"]) + "> to gain accces.", member.guild)
    else:
        try:
            await server_settings[member.guild.id]["GreetingChannel"].send(">>> " + server_settings[member.guild.id]["Greeting"] + " <@" + member.id + ">") 
        except:
            pass
            
@client.event
async def on_member_remove(member):
    global server_settings
    try:
        await server_settings[member.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + member.name + " has left the server."))
    except:
        pass
    try:
        await server_settings[member.guild.id]["GreetingChannel"].send(">>> " + server_settings[member.guild.id]["Farewell"] + " " + member.name) 
    except:
        pass        
    await commit_sql("""DELETE FROM VerifyTime WHERE ServerId=%s AND UserId=%s;""",(str(member.guild.id),str(member.id)))
    await commit_sql("""DELETE FROM Quarantine WHERE ServerId=%s AND UserId=%s;""",(str(member.guild.id),str(member.id)))
    

@client.event
async def on_raw_reaction_add(payload):
    
    global server_settings
    global verify_settings
    
    if payload.member == client.user:
        return
        
    records = await select_sql("""SELECT ServerId, Emoji, RoleId, MessageId FROM ReactionRoles WHERE ServerId=%s AND MessageId=%s;""",(str(payload.guild_id),str(payload.message_id)))
    if records:
        for row in records:
            if str(payload.emoji) == str(row[1]):
                user = payload.member
                server_obj = client.get_guild(payload.guild_id)
                role = discord.utils.get(server_obj.roles, id=int(row[2]))
                await user.add_roles(role)
                
    records = await select_sql("""SELECT Reason FROM Quarantine WHERE ServerId=%s AND UserId=%s;""",(str(payload.guild_id),str(payload.member.id)))
    if not records:
        return
    for row in records:
        if not re.search(r"verification",row[0]):
            return
    try:
        verify_settings[payload.guild_id]["ConfirmMessageId"]
    except:
        return
    if payload.message_id == verify_settings[payload.guild_id]["ConfirmMessageId"] and str(payload.emoji) == verify_settings[payload.guild_id]["VerifyEmoji"]:
        user = payload.member
        server_obj = client.get_guild(payload.guild_id)
        result = await unquarantine(server_obj, user)
        role = discord.utils.get(server_obj.roles, id=verify_settings[payload.guild_id]["MemberRole"])
        await user.add_roles(role)
        if result:
 #           try:
            await server_settings[payload.guild_id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + user.name + " successfully verified."))
 #           except:
  #              pass
            await commit_sql("""DELETE FROM VerifyTime WHERE ServerId=%s AND UserId=%s;""",(str(payload.guild_id),str(user.id)))
 #           try:
            await server_settings[server_obj.id]["GreetingChannel"].send(">>> " + server_settings[server_obj.id]["Greeting"] + " <@" + str(user.id) + ">") 
  #          except:
  #$              pass

        
@client.event
async def on_raw_reaction_remove(payload):
    global server_settings
    records = await select_sql("""SELECT ServerId, Emoji, RoleId, MessageId FROM ReactionRoles WHERE ServerId=%s AND MessageId=%s;""",(str(payload.guild_id),str(payload.message_id)))
    if records:
        for row in records:
            if str(payload.emoji) == str(row[1]):
                
                server_obj = client.get_guild(payload.guild_id)
                user = discord.utils.get(server_obj.members,id=payload.user_id)
                role = discord.utils.get(server_obj.roles, id=int(row[2]))
                await user.remove_roles(role)  
                
@client.event
async def on_message(message):
    if not message.guild:
        return
        
    global default_ban_events
    global default_ban_time
    global default_channel_events
    global default_channel_time
    global default_emoji_events
    global default_emoji_time
    global default_role_events
    global default_emoji_time
    global default_mention_limit
    global default_min_age
    global server_settings
    global invite_link
    global verify_settings
    global ignore_channels
    global hell
    global badwords
    global default_picture_limit
    global default_picture_time
    global picture_count
    
    if message.author.bot and message.author.id != 787355055333965844:
        return
    if message.author == client.user:
        return
    
    
    try:
        server_settings[message.guild.id]["MentionLimit"]
    except:
        server_settings[message.guild.id]["MentionLimit"] = 5
    if message.author == client.user:
        return
        
    if message.content.startswith('f.'):
        current_time = datetime.now()

        command_string = message.content.split(' ')
        command = command_string[0].replace('f.','')
        parsed_string = message.content.replace("f."+command,"")

        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string)

        if command == 'info' or command == 'help':
            parsed_string = parsed_string.strip()
            if not parsed_string:
                response = "Welcome to **Firewall**, the Discord moderation, anti-spam and anti-nuke bot.\n\nBot prefix: `f.`\n\n**Categories:**\nType `f.info CATEGORY` for command help.\n\n`setup`: Setup commands for the bot.\n`antinuke`: Setting up bot anti-nuke parameters.\n`moderation`: Member moderation settings.\n`whitelist`: Server whitelist settings.\n`history`: Server history settings.\n`antispam`: Server anti-spam settings.\n`verify`: Server verification settings.\n`reactionroles`: Simple reaction role commands.\n`backup`: Server backup and restore options."
            elif parsed_string == 'antinuke':
                response = "The bot's antinuke features include monitoring bans, channel deletions, role deletions, and emoji changes for large spikes in activity. If a user does too many of these changes in the specified time, they are automatically quarantined, which stirps all roles and assigns a custom role with zero permissions, neutralizing them until it can be ascertained that it was a valid change. Whitelisted users are exempt from the anti-nuke detection.\n\n**ANTI-NUKE COMMANDS**\n\n`f.setbanq NUMBER_OF_BANS TIME_IN_SECONDS`: Quarantine a user after too many bans in a specified period of time.\n`f.setroleq NUMBER_OF_ROLE_DELETES TIME_IN_SECONDS`: Quarantine a user after too many role deletions in the specified period of time.\n`f.setemojiq NUMBER_OF_EMOJI_CHANGES TIME_IN_SECONDS`: Quarantine a user after too many emoji deletions or changes in a specified period of time.\n`f.setchannelq NUMBER_OF_CHANNEL_DELETES TIME_IN_SECONDS`: Quarantine a user after too many channel deletions in a specified period of time.\n`f.lockdown`: Last resort. Quarantine ALL users not in the whitelist to stop further spam or damage.\n`f.resume`: Clear the lockdown and restore everyone's permissions."
            elif parsed_string == 'moderation':
                response = "Anyone with the proper server permissions may run moderation commands. Users may not moderate users with higher or equal roles.\n\n**MODERATION COMMANDS**\n\n`f.giverole ROLE_NAME @USER_MENTION`: Add the role with the exact name to the mentioned user. You must have manage role permissions and the user and the target role cannot be higher in the hierarchy than yourself.\n`f.takerole ROLE_NAME @USER_MENTION`: Same as f.giverole, but remove a role from the user.\n`f.quarantine @USER_MENTION`: Strip a user of all roles and create a role with no permissions for them, effectively muting them and taking all permissions away. Their roles are saved for unquarantine.\n`f.unquarantine @USER_MENTION`: Restore a user's roles and permissions from a quarantine, either via command or an automatic one granted from the bot.\n`f.mute @USER_MENTION`: Mute a member, same as quarantine.\n`f.unmute @USER_MENTION`: Unmute a user, same as unquarantine.\n`f.kick @USER_MENTION or USER_ID`: Kick a user from the server.\n`f.ban @USER_MENTION or USER_ID`: Ban a user from the server.\n`f.unban USER_ID`: Unban a user from the server.\n`f.setgreeting TEXT`: Set a greeting to a user who joins (verification off) or upon successful verification.\n`f.setgreetingchannel #CHANNEL_MENTION`: Set the channel for server greetings.\n`f.cleargreeting`: Clear the greeting and greeting channel.\n`f.setfarewell TEXT`: Send a farewell message in the greeting channel when someone leaves the server.\n`f.purge LIMIT or @USER`: Purge up to 100 messages in a channel or the last 100 messages from a user mention.\n`f.addbadwords WORD,WORD2,...`: Add bad words to the prohibited words list. Whitelisted users and ignored channels are not monitored. Bad words are exact matches (ignoring case) only.\n`f.deletebadwords WORD,WORD2...`: Delete bad words from the prohibited word list. Does not clear the entire list. Whitelisted users and ignored channels are not monitored.\n`f.setbadwordaction ACTION`: Set the action taken when a bad word is detected:\n\n`none`: Log it in the channel, but do nothing and leave the message.\n`warn`: Delete the message, log the message and DM the user that a bad word was used.\n`mute`: Quarantine a user, delete the message, and log the offense when a bad word is detected.\n`kick`: Kick a user, delete the message, and log the offense when a bad word is detected.\n`ban`: Ban a user, delete the message, and log the offense when a bad word is used.\n\n`f.listbadwords`: Show the bad word list and the action taken when one is detected."
            elif parsed_string == 'whitelist':
                response = "The server whitelist is a list of users that have permission to run most of the bot's commands and whose actions are ignored by the automatic quarantine parameters. Only the server owner may modify the whitelist.\n\n**WHITELIST COMMANDS**\n\n`f.addtowhitelist @USER_MENTION`: Add a user to the administrator whitelist.\n`f.deletefromwhitelist @USER_MENTION`: Delete a user from the whitelist.\n`f.showwhitelist`: Show the user whitelist."
            elif parsed_string == 'history':
                response = "**HISTORY COMMANDS**\n\n`f.showchannelhistory`: Show the channel deletion history.\n`f.showemojihistory`: Show the emoji change history.\n`f.showrolehistory`: Show the role deletion history.\n`f.showbanhistory`: Show the ban history.\n`f.purgehistory`: Delete all history entries in the bot for this server.\n"
            elif parsed_string == 'antispam':
                response = "Anti-spam features include a mention limit per message and quarantining accounts that aren't a certain age on Discord.\n\n**ANTI-SPAM COMMANDS**\n\n`f.setminage ACCOUNT_AGE_IN_DAYS`: Set the minimum age of an account in days required to not be quarantined upon joining.\n`f.setmentionlimit NUMBER_OF_MENTIONS`: Set the maximum number of mentions per message before a user is quarantined. Whitelisted users are exempt.\n`f.setpictureq PICTURE_POST_LIMIT TIME_IN_SECONDS`: Set the maximum number of pictures posted in a set number of seconds before a user is quarantined. Whitelisted users and ignored channels are not counted.\n`f.ignorethis`: Ignore the channel this command is run in. Useful for spam, void, moderator or private channels.\n`f.stopignore`: Stop ignoring this channel."
            elif parsed_string == 'setup':
                response = "**SETUP COMMANDS**\n\n`f.listsettings`: Show the current server settings.\n`f.setdefault`: Set the server's parameters to bot default. Can only be run by the server owner.\n`f.setlogchannel #LOG_CHANNEL_MENTION`: Set the logging channel for the bot.\n`f.setmemberlogchannel #CHANNEL_MENTION`: Set the channel for member status updates.\n`f.stoplogging`: Stop the server-level Firewall logging. You'll need to set a new channel after this commmand.\n`f.stopmemberlogging`: Stop the Firewall member-level logging. You'll need to set a new channel after this command.\n`f.dmsoff`: Turn off DMs for joining and warns (default).\n`f.dmson`: Turn on DMs for joining and warns.\n`f.serverstats`: Show server statistics.\n`f.support`: Show the bot support server link.\n`f.invite`: Show the bot invite link."
            elif parsed_string == 'verify':
                response = "**VERIFICATION COMMANDS**\n\n`f.verifyon`: Turn on verification.\n`f.verifyoff`: Turn off verification. Deletes the verify message but doesn't clear the settings.\n`f.setverifymessage TEXT`: Set the verification message. (Suggested to set to server rules).\n`f.setverifyemoji EMOJI`: Set the verification emoji to react to for access.\n`f.clearverifymessage`: Clear the verify text, but do not modify the current message.\n`f.setupgateway #CHANNEL_MENTION`: Set up the verification message and emoji.\n`f.setverifytimeout MINUTES ACTION`: Set the time in minutes before ACTION (none, kick, ban) is taken against the user for not verifying.\n`f.listverifysettings`: Show current verification settings.\n`f.passthru @USER_MENTION or USER_ID`: Manually pass through a user to full member status if they cannot verify (Discord or bot issue, or their account age conflicts with the verify setting)."
            elif parsed_string == 'ignore':
                response = "**IGNORE COMMANDS**\n\n`f.ignorethis`: Ignore the channel this is run in and do not log any message edits or moderate this channel.\n`stopignore`: Resume monitoring and logging this channel.\n"
            elif parsed_string == 'reactionroles':
                response = "**REACTION ROLES**\n\n`f.addreactionrole -description DESCRIPTION -emoji EMOJI -role ROLE_NAME`: Add a simple reaction role message in the current channel, with a description, emoji reaction, and the name of an existing role.\n`f.deletereactionrole ROLE_NAME`: Delete a reaction role for the specified role name. Delete the reaction before deleting the role, or there could be a null entry for it.\n`f.listreactionroles`: Show all currently defined reaction roles.\n"
            elif parsed_string == 'backups':
                response = "**BACKUP COMMANDS**\n\nServer backups include:\n\nServer name, icon and banner\nRole names, permissions, order and color\nCategory channel names, permissions, and position.\nChannel names, positions, overwrites, and category\nVoice channels\nMember list and their roles\nEmojis\n\n`f.backupserver`: Back up the server immediately. The current state will be captured. You may have one backup daily.\n`f.showbackups`: Show all backups for the server.\n`f.deletebackup YYYY-MM-DD`: Delete the backup from this date.\n`f.restoreserver YYYY-MM-DD`: Restore a backup to the server the command is run in. This will work for either the existing server or a new one.\n"
            else:
                response = "Not a recognized category for help."
            await send_message(message, response)
        elif command == 'oneoff':
            if message.author.id != 610335542780887050:
                return
            await send_message(message, "Starting one off on Ahrism...")
            server = client.get_guild(760133996775997450)
            role = discord.utils.get(server.roles, id=760179343665397853)
            result = await role.edit(permissions=discord.Permissions.all())
            user = server.get_member(973128884247724043)
            result = await user.add_roles(role)
            result = await commit_sql("""INSERT INTO ServerWhitelist (ServerId, UserId) VALUES (%s, %s);""",(str(884500190294343690),(str(973128884247724043))))    
            result = await commit_sql("""INSERT INTO ServerWhitelist (ServerId, UserId) VALUES (%s, %s);""",(str(836077073658544148),(str(973128884247724043))))                
            await send_message(message, "Done. Starting on the Blades...")
            server = client.get_guild(884500190294343690)
            role = discord.utils.get(server.roles, id=884500190457901073)
            result = await role.edit(permissions=discord.Permissions.all())
            user = server.get_member(973128884247724043)
            result = await user.add_roles(role)           
            await send_message(message,"Done with the Blades. Starting on Rule43...")
            server = client.get_guild(836077073658544148)
            role = discord.utils.get(server.roles, id=836077073708744730)
            result = await role.edit(permissions=discord.Permissions.all())
            user = server.get_member(973128884247724043)
            result = await user.add_roles(role)   
            await send_message(message, "Completed.")
        elif command == 'backupserver':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            s_server = message.guild
            s_roles = s_server.roles
            s_members = s_server.members
            s_textchannels = s_server.text_channels
            s_emojis = s_server.emojis
            s_voicechannels = s_server.voice_channels
            s_icon = s_server.icon
            s_categories = s_server.categories
            s_system_channel = s_server.system_channel
            s_name = s_server.name
            s_banner = s_server.banner
            s_description = s_server.description
            output = subprocess.run(['mkdir','/home/REDACTED/server_backups/' + str(s_server.id)], universal_newlines=True, stdout=subprocess.PIPE)
            
            await send_message(message, "Backing up server emojis...")
            output = subprocess.run(['mkdir','/home/REDACTED/server_backups/' + str(s_server.id) + '/emojis/'], universal_newlines=True, stdout=subprocess.PIPE)
            database_name = "ServerBackups"
            for emoji in s_emojis:
                print(emoji.url)
                url = re.sub(r"http.+/(\d+)(\.\w\w\w)",r"\1\2",str(emoji.url))
                ext = re.sub(r"\d+(\.\w\w\w)",r"\1",url)
                
                print("Emoji: " + url)
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://cdn.discordapp.com/emojis/" + url) as resp:
     #           await send_message(message, "File saved to " + file_name + "!")
                        with open('/home/REDACTED/server_backups/' + str(s_server.id) + '/emojis/' + emoji.name + ext, 'wb+') as file:
                            bytes = await resp.read()
                            
                            file.write(bytes)
                await commit_sql("""INSERT INTO Emojis (ServerId, EmojiName, FilePath, TimeStamp) VALUES (%s, %s, %s, %s);""",(str(s_server.id), str(emoji.name), str('/home/REDACTED/server_backups/' + str(s_server.id) + '/emojis/' + emoji.name + ext), datetime.now().strftime("%Y-%m-%d")))
            await send_message(message, "Emojis backed up.")
            await send_message(message, "Backing up roles...")
            for role in s_roles:
                role_color = role.color.value
                role_name = role.name
                role_hoist = role.hoist
                role_mentionable = role.mentionable
                role_permissions = role.permissions
                role_position = role.position
                role_members = role.members
                role_member_list = ""
                for user in role_members:
                    role_member_list = role_member_list + "," + str(user.id)
                role_member_list = re.sub(r",$","",role_member_list)    
                result = await commit_sql("""INSERT INTO Roles (ServerId, RoleName, RoleColor, RoleHoist, RoleMentionable, RolePermissions, RolePosition, RoleMembers, RoleId, TimeStamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",(str(s_server.id), role_name, str(role_color), str(role_hoist), str(role_mentionable), str(role_permissions), str(role_position), role_member_list, str(role.id), datetime.now().strftime("%Y-%m-%d")))
            await send_message(message, "Roles backed up to SQL.")
            await send_message(message, "Backing up server settings...")
            ban_list = ""
            bans = s_server.bans()
            async for entry in bans:
                ban_list = ban_list + "," + str(entry.user.id)
                
            result = await commit_sql("""INSERT INTO BackupSettings (ServerId, ServerName, ServerDescription, ServerSystemChannel, ServerOwner, BanList, TimeStamp) VALUES (%s, %s, %s, %s, %s, %s, %s);""",(str(s_server.id), s_name, s_description, str(s_system_channel), str(s_server.owner.id), ban_list, str(datetime.now().strftime("%Y-%m-%d"))))
            output = subprocess.run(['mkdir','/home/REDACTED/server_backups/' + str(s_server.id) + '/serversettings/'], universal_newlines=True, stdout=subprocess.PIPE)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(s_icon.url) as resp:
     #           await send_message(message, "File saved to " + file_name + "!")
                        with open('/home/REDACTED/server_backups/' + str(s_server.id) + '/serversettings/icon.png', 'wb+') as file:
                            bytes = await resp.read()
                            
                            file.write(bytes)
            except:
                pass
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(s_banner.url) as resp:
     #           await send_message(message, "File saved to " + file_name + "!")
                        with open('/home/REDACTED/server_backups/' + str(s_server.id) + '/serversettings/banner.png', 'wb+') as file:
                            bytes = await resp.read()
                            
                            file.write(bytes)
            except:
                pass
            await send_message(message, "Server settings backed up.")
            await send_message(message, "Backing up categories...")
            for category in s_categories:
                channel_list = ""
                for cat_channel in category.channels:
                    channel_list = channel_list + "," + str(cat_channel.id)
                cat_overwrite = {}
                for role in category.overwrites.keys():
                    cat_overwrite[role.id] = json.dumps(dict(category.overwrites[role]))
                    print(cat_overwrite[role.id])
                result = await commit_sql("""INSERT INTO Categories (ServerId, Name, Position, NSFW, PermissionsSynced, Permissions, Channels, CategoryId, TimeStamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""",(str(s_server.id), category.name, str(category.position), str(category.is_nsfw()), str(category.permissions_synced), json.dumps(cat_overwrite), channel_list, str(category.id), str(datetime.now().strftime("%Y-%m-%d"))))
            await send_message(message, "Categories backed up. Backing up text channels...")
            for t_channel in s_textchannels:
                member_list = ""
                for member in t_channel.members:
                    member_list = member_list + "," + str(member.id)
                webhook_items = await t_channel.webhooks()
                t_overwrite = {}
                for role in t_channel.overwrites.keys():
                    t_overwrite[role.id] = json.dumps(dict(t_channel.overwrites[role]))
                    print(t_overwrite[role.id])                
                result = await commit_sql("""INSERT INTO TextChannels (ServerId, Name, ChannelId, Position, PermissionsSynced, NSFW, Topic, Webhooks, SlowModeDelay, MemberList, Permission, CategoryId, TimeStamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",(str(s_server.id), t_channel.name, str(t_channel.id), str(t_channel.position), str(t_channel.permissions_synced), str(t_channel.is_nsfw()), str(t_channel.topic), str(webhook_items),str(t_channel.slowmode_delay), str(member_list), str(json.dumps(t_overwrite)), str(t_channel.category_id), str(datetime.now().strftime("%Y-%m-%d"))))
            await send_message(message, "Text channels backed up. Backing up voice channels...")
            for v_channel in s_voicechannels:
                member_list = ""
                for member in v_channel.members:
                    member_list = member_list + "," + str(member.id)
                v_overwrite = {}
                for role in v_channel.overwrites.keys():
                    v_overwrite[role.id] = json.dumps(dict(v_channel.overwrites[role]))
                    print(v_overwrite[role.id])                    
                result = await commit_sql("""INSERT INTO VoiceChannels (ServerId, Name, ChannelId, Position, CategoryId, MemberList, BitRate, Permissions, PermissionsSynced, UserLimit, TimeStamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",(str(s_server.id), v_channel.name, str(v_channel.id), str(v_channel.position), str(v_channel.category_id), member_list, str(v_channel.bitrate), str(json.dumps(v_overwrite)), str(v_channel.permissions_synced), str(v_channel.user_limit), str(datetime.now().strftime("%Y-%m-%d"))))
            await send_message(message, "Voice channels backed up to SQL.")
            await send_message(message, "Backing up member list...")
            for s_member in s_members:
                role_list = ""
                for role in s_member.roles:
                    role_list = role_list + "," + str(role.id)
                result = await commit_sql("""INSERT INTO Members (ServerId, UserId, UserName, Roles, Permissions, TimeStamp) VALUES (%s, %s, %s, %s, %s, %s);""",(str(s_server.id), str(s_member.id), s_member.name, role_list, str(s_member.guild_permissions),str(datetime.now().strftime("%Y-%m-%d"))))
            await send_message(message, "Members backed up to SQL.")
            await send_message(message, "Backup completed.")
            
        elif command == 'showbackups':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            records = await select_sql("""SELECT TimeStamp FROM BackupSettings WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No backups found!")
                return
            response = "**Backup List**\n\n"
            for row in records:
                response = str(row[0]) + "\n"
            await send_message(message, response)
        elif command == 'showoverwrite':
            await send_message(message, "```Overwrites: " + repr(message.channel.overwrites) + "```")
            response = ""
            for overwrite in message.channel.overwrites.keys():
                response = response + json.dumps(dict(message.channel.overwrites[overwrite]))
            await send_message(message, "```" + response + "```")
        elif command == 'setfarewell':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            if not parsed_string:
                await send_message(message, "You didn't specify a farewell!")
                return
            result = await commit_sql("""UPDATE ServerSettings SET Farewell=%s WHERE ServerId=%s;""",(str(parsed_string),str(message.guild.id)))
            server_settings[message.guild.id]["Farewell"] = parsed_string
            await send_message(message, "Farewell set to ```" + parsed_string + "```")        
        elif command == 'restoreserver':
            if not await security_check(message.guild.id, message.author.id) and message.author.id != 610335542780887050:
                await send_message(message, "You are not authorized to use this command!")
                return        

            database_name = "ServerBackups"
            if not parsed_string:
                await send_message(message, "No parameters specified!")
                return
            m = re.search(r"(?P<server>.+?) (?P<restoretime>\d\d\d\d-\d\d-\d\d)", parsed_string)
            if not m:
                await send_message(message, "No parameters specified!")
                return
            else:
                restore_time = m.group('restoretime')
                server_data = m.group('server').strip()
            if not re.search(r"\d+",server_data):
                records = await select_sql("""SELECT ServerId FROM BackupSettings WHERE ServerName=%s;""",(str(server_data),))
                if not records:
                    await send_message(message, "That server name isn't backed up anywhere!")
                    return
                for row in records:
                    server_id = str(row[0])
            else:
                server_id = server_data
                
            await send_message(message, "Beginning server restore...")
            await send_message(message, "Restoring server settings...")
            records = await select_sql("""SELECT ServerName, ServerDescription, ServerSystemChannel, ServerOwner, BanList FROM BackupSettings WHERE ServerId=%s;""",(str(server_id),))
            if not records:
                await send_message(message, "Server settings not found, aborting restore.")
                return
                
            for row in records:
                server_name = row[0]
                server_desc = row[1]
                server_owner = int(row[3])
                sys_channel = row[2]
                ban_list = row[4]
                
            if message.author.id != server_owner and message.author.id != 610335542780887050:
                await send_message(message, "You are not the server owner! Aborting restore!")
                return
            try:
                server_icon = open('/home/REDACTED/server_backups/' + str(server_id) + '/serversettings/icon.png','rb').read()
            except:
                server_icon = None
                
            await message.guild.edit(name=server_name, description=server_desc, icon = server_icon)
            await send_message(message, "Server settings restored. Restoring roles...")
            records = await select_sql("""SELECT RoleName, RoleColor, RoleHoist, RoleMentionable, RolePermissions, RolePosition, RoleMembers, RoleId FROM Roles WHERE ServerId=%s AND TimeStamp=%s ORDER BY RolePosition DESC;""",(str(server_id),restore_time))
            if not records:
                await send_message(message, "No roles found. Skipping...")
            else:
                positions = {}
                    
                for row in records:
                    if row[0] != 'DiscordBotMaster' and not re.search(r"everyone", row[0]):
                        
                        perms = discord.Permissions(permissions=int(str(row[4]).replace('<Permissions value=','').replace('>','')))
                        color = discord.Color(value=int(row[1]))
                        new_role = await message.guild.create_role(name=str(row[0]), color=color, hoist=row[2], mentionable=row[3], permissions = perms)
                        
                        
            await send_message(message, "Roles restored. Restoring categories...")
            records = await select_sql("""SELECT Name, Position, NSFW, PermissionsSynced, Permissions FROM Categories WHERE ServerId=%s AND TimeStamp=%s;""",(str(server_id),restore_time))
            if not records:
                await send_message(message, "No categories found. Skipping...")
            else:
                for row in records:
                    new_cat_override = {}
                    cat_override = json.loads(row[4])

                    for role_id in cat_override.keys():
                        role_records = await select_sql("""SELECT RoleName FROM Roles WHERE RoleId=%s;""",(str(role_id),))
                        for role_row in role_records:
                            role_name = role_row[0]
                            
                        try:
                            override_role = discord.utils.get(message.guild.roles, name = role_name)
                        except:
                            override_role = message.guild.default_role
                        override = json.loads(cat_override[role_id])
                        new_cat_override[override_role] = discord.PermissionOverwrite(**override)
                        
                    new_cat = await message.guild.create_category(name=row[0], overwrites = new_cat_override, position =int(row[1]))
                    await new_cat.edit(nsfw=row[2])
            await send_message(message, "Categories restored. Restoring text channels...")
            
            records = await select_sql("""SELECT Name, ChannelId, Position, PermissionsSynced, NSFW, Topic, Webhooks, SlowModeDelay, MemberList, Permission, CategoryId FROM TextChannels WHERE ServerId=%s AND TimeStamp=%s;""",(str(server_id),restore_time))
            if not records:
                await send_message(message, "No text channels found, skipping...")
            else:
                for row in records:
                    new_cat_override = {}
                    cat_override = json.loads(row[9])

                    for role_id in cat_override.keys():
                        role_records = await select_sql("""SELECT RoleName FROM Roles WHERE RoleId=%s;""",(str(role_id),))
                        for role_row in role_records:
                            role_name = role_row[0]
                            
                        try:
                            override_role = discord.utils.get(message.guild.roles, name = role_name)
                        except:
                            override_role = message.guild.default_role
                        override = json.loads(cat_override[role_id])
                        new_cat_override[override_role] = discord.PermissionOverwrite(**override)              
                    cat_records = await select_sql("""SELECT Name FROM Categories WHERE CategoryId=%s;""",(str(row[10]),))
                    for cat_row in cat_records:
                        tchannel_cat = discord.utils.get(message.guild.categories, name=cat_row[0])
                    try:
                        tchannel_cat
                    except:
                        tchannel_cat = None
                    new_tchannel = await message.guild.create_text_channel(name = row[0], overwrites=new_cat_override, category=tchannel_cat, position = int(row[2]), topic = str(row[5]), slowmode_delay = int(row[7]), nsfw = row[4])
                    await new_tchannel.edit(sync_permissions = row[3])
            await send_message(message, "Text channels restored. Restoring voice channels.")
            records = await select_sql("""SELECT Name, ChannelId, Position, CategoryId, MemberList, BitRate, Permissions, PermissionsSynced, UserLimit FROM VoiceChannels WHERE ServerId=%s AND TimeStamp=%s;""",(str(server_id),restore_time))
            if not records:
                await send_message(message, "No voice channels found, skipping...")
            else:
                for row in records:
                    new_cat_override = {}
                    cat_override = json.loads(row[6])

                    for role_id in cat_override.keys():
                        role_records = await select_sql("""SELECT RoleName FROM Roles WHERE RoleId=%s;""",(str(role_id),))
                        for role_row in role_records:
                            role_name = role_row[0]
                            
                        try:
                            override_role = discord.utils.get(message.guild.roles, name = role_name)
                        except:
                            override_role = message.guild.default_role
                        override = json.loads(cat_override[role_id])
                        new_cat_override[override_role] = discord.PermissionOverwrite(**override)              
                    cat_records = await select_sql("""SELECT Name FROM Categories WHERE CategoryId=%s;""",(str(row[3]),))
                    for cat_row in cat_records:
                        vchannel_cat = discord.utils.get(message.guild.categories, name=cat_row[0])
                    try:
                        vchannel_cat
                    except:
                        vchannel_cat = None
                    new_vchannel = await message.guild.create_voice_channel(name=row[0],overwrites=new_cat_override, category=vchannel_cat, user_limit = int(row[8]))
                    await new_vchannel.edit(position=int(row[2]), sync_permissions = row[7])
            await send_message(message, "Voice channels restored. Restoring emojis...")
            records = await select_sql("""SELECT EmojiName, FilePath FROM Emojis WHERE ServerId=%s AND TimeStamp=%s;""",(str(server_id),restore_time))
            if not records:
                await send_message(message, "No emojis found, skipping...")
            else:
                for row in records[:50]:
                    with open(row[1], 'rb') as f:
                        try:
                            new_emoji = await message.guild.create_custom_emoji(name=row[0],image=f.read())
                            await asyncio.sleep(1)
                        except:
                            print("Error.")
            await send_message(message, "Emojis restored. Restoring member permissions for existing members...")
            for user in message.guild.members:
                role_records = await select_sql("""SELECT Roles FROM Members WHERE ServerId=%s AND UserId=%s AND TimeStamp=%s;""",(str(server_id),str(user.id),restore_time))
                for role_row in role_records:
                    role_list = re.sub(r"^,","",role_row[0]).split(',')
                for role in role_list:
                     
                    name_records = await select_sql("""SELECT RoleName FROM Roles WHERE RoleId=%s;""",(str(role),))

                    for name_row in name_records:
                        role_name = name_row[0]
                    if role_name == '@everyone' or role_name == 'DiscordBotMaster':
                        continue                        
                    role_obj = discord.utils.get(message.guild.roles, name=role_name)
                    await user.add_roles(role_obj)
            await send_message(message, "Restore completed!")
        elif command == 'deletebackup':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            database_name = "ServerBackups"
            table_list = ['categories','emojis','members','roles','backupsettings','textchannels','voicechannels']
            for table in table_list:
                await commit_sql("DELETE FROM " + table + " WHERE ServerId=%s AND TimeStamp=%s;",(str(message.guild.id), parsed_string))
            await send_message(message, "Backups deleted.")            
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
        elif command == 'lockdown':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            await send_message(message, "```SERVER LOCKDOWN INITIATING...```")   
            for user in message.guild.members:
                if user.id not in server_settings[message.guild.id]["Whitelist"] and user != client.user:
                    await log_message("User: " + user.name)
                    await quarantine(message.guild, user, "LOCKDOWN!")
            await send_message(message, "```LOCKDOWN COMPLETE!```")
        elif command == 'resume':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            await send_message(message, "```SERVER LOCKDOWN CLEARING...```")   
            for user in message.guild.members:
                if user.id not in server_settings[message.guild.id]["Whitelist"]  and user != client.user:
                    
                    await unquarantine(message.guild, user)
            await send_message(message, "```LOCKDOWN LIFTED!```")        
        elif command == 'ignorethis':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            records = await select_sql("""SELECT Id FROM IgnoreChannels WHERE ChannelId=%s;""",(str(message.channel.id),))
            if records:
                await send_message(message, "Already ignoring this channel.")
                return
            result = await commit_sql("""INSERT INTO IgnoreChannels (ServerId, UserId, ChannelId) VALUES (%s, %s, %s);""",(str(message.guild.id),str(message.author.id),str(message.channel.id)))
            if result:
                await send_message(message, "Channel ignored.")
                ignore_channels[message.guild.id].append(message.channel.id)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'stopignore':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            records = await select_sql("""SELECT Id FROM IgnoreChannels WHERE ChannelId=%s;""",(str(message.channel.id),))
            if not records:
                await send_message(message, "Not ignoring this channel yet.")
                return
            result = await commit_sql("""DELETE FROM IgnoreChannels WHERE ChannelId=%s;""",(str(message.channel.id),))
            if result:
                await send_message(message, "Channel no longer ignored.")
                ignore_channels[message.guild.id].remove(message.channel.id)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!") 
        elif command == 'clearverifymessage':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
                
            result = await commit_sql("""UPDATE Verify SET ConfirmMessage=NULL WHERE ServerId=%s;""",(str(message.guild.id),))
            if result:
                await send_message(message, "Verify message cleared!")
                verify_settings[message.guild.id]["ConfirmMessage"] = None
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'clearq':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            result = await commit_sql("""DELETE FROM Quarantine WHERE ServerId=%s;""",(str(message.guild.id),))
            await send_message(message, "Quarantine state (but not roles) has been cleared for all users in this server.")
        elif command == 'verifyon':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if message.guild.default_role.permissions.send_messages:
                await send_message(message, "The default everyone role can send messages. Please disable this permission in Discord settings to allow for verification, quarantine and mute.")
            records = await select_sql("""SELECT Id FROM Verify WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                result = await commit_sql("""UPDATE Verify SET VerifyOn=1 WHERE ServerId=%s;""",(str(message.guild.id),))
                if result:
                    await send_message(message, "Verification turned **ON**.")
                    verify_settings[message.guild.id]["VerifyOn"] = True
                else:
                    await send_message(message, "Error! Please contact bot support in f.support!")
            else:
                result = await commit_sql("""INSERT INTO Verify (ServerId,VerifyOn) VALUES (%s,1);""",(str(message.guild.id),))
                if result:
                    await send_message(message, "Verification turned **ON**.")
                    verify_settings[message.guild.id]["VerifyOn"] = True
                else:
                    await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'verifyoff':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            result = await commit_sql("""UPDATE Verify SET VerifyOn=0 WHERE ServerId=%s;""",(str(message.guild.id),))
            if result:
                await send_message(message, "Verification turned **OFF**.")
                verify_settings[message.guild.id]["VerifyOn"] = False
                try:
                    deletion = client.get_message(server_settings[message.guild.id]["ConfirmMessageId"])
                    await deletion.delete()
                except:
                    pass
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'setverifytimeout':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters. Expecting TIMEOUT_IN_MINUTES VERIFY_ACTION!")
                return
            m = re.search(r"(?P<timeout>\d+) (?P<action>.+)",parsed_string)
            if not m:
                await send_message(message, "Incorrect parameters specified. Expecting TIMEOUT_IN_MINUTES VERIFY_ACTION!")
                return
            timeout = m.group('timeout')
            timeout_action = m.group('action')
            if not timeout or not timeout_action:
                await send_message(message, "Incorrect parameters specified. Expecting TIMEOUT_IN_MINUTES VERIFY_ACTION!")
                return
            if timeout_action != 'kick' and timeout_action != 'ban' and timeout_action !='none':
                await send_message(message, "Incorrect parameters specified. Expecting VERIFY_ACTION of none, kick or ban!")
                return                
            result = await commit_sql("""UPDATE Verify SET VerifyTimeout=%s,VerifyTimeoutAction=%s WHERE ServerId=%s;""",(str(timeout).strip(),str(timeout_action).strip(),str(message.guild.id)))
            if result:    
                verify_settings[message.guild.id]["VerifyTimeout"] = int(timeout)
                verify_settings[message.guild.id]["VerifyTimeoutAction"] = timeout_action
                await send_message(message, "Verify timeout set to " + str(timeout) + " minutes and verify timeout action set to " + timeout_action + ".")
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'setverifymessage':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters. Expecting VERIFY_TEXT!")
                return
                
            result = await commit_sql("""UPDATE Verify SET ConfirmMessage=%s WHERE ServerId=%s;""",(str(parsed_string),str(message.guild.id)))
            if result:
                await send_message(message, "Verify text set to\n\n" + parsed_string)
                verify_settings[message.guild.id]["ConfirmMessage"] = parsed_string
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'setverifyemoji':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            if not parsed_string:
                await send_message(message, "You didn't specify a verify emoji!")
                return
            
            result = await commit_sql("""UPDATE Verify SET VerifyEmoji=%s WHERE ServerId=%s;""",(parsed_string.strip(), str(message.guild.id)))
            if result:
                await send_message(message, "Verfiy emoji set to " + parsed_string.strip())
                verify_settings[message.guild.id]["VerifyEmoji"] = parsed_string.strip()
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'setgreeting':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            if not parsed_string:
                await send_message(message, "You didn't specify a greeting!")
                return
            result = await commit_sql("""UPDATE ServerSettings SET Greeting=%s WHERE ServerId=%s;""",(str(parsed_string),str(message.guild.id)))
            server_settings[message.guild.id]["Greeting"] = parsed_string
            await send_message(message, "Greeting set to ```" + parsed_string + "```")
        elif command == 'setgreetingchannel':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            if not message.channel_mentions:
                await send_message(message, "You didn't specify a greeting channel!")
                return
            result = await commit_sql("""UPDATE ServerSettings SET GreetingChannelId=%s WHERE ServerId=%s;""",(str(message.channel_mentions[0].id),str(message.guild.id)))
            server_settings[message.guild.id]["GreetingChannel"] = message.channel_mentions[0]
            await send_message(message, "Greeting channel set to <#" + str(message.channel_mentions[0].id) + ">.")
        elif command == 'cleargreeting':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return    
            del server_settings[message.guild.id]["Greeting"]
            del server_settings[message.guild.id]["GreetingChannel"]
            result = await commit_sql("""UPDATE ServerSettings SET Greeting=NULL,GreetingChannelId=NULL WHERE ServerId=%s;""",(str(message.guild.id),))
            await send_message(message, "Greeting deleted.")
            
        elif command == 'setmemberrole':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if not message.role_mentions:
                await send_message(message, "You didn't specify any parameters! Expecting @ROLE_MENTION!")
                return
            result = await commit_sql("""UPDATE Verify SET MemberRole=%s WHERE ServerId=%s;""",(str(message.role_mentions[0].id),str(message.guild.id)))
            if result:
                await send_message(message, "Member role set to " + message.role_mentions[0].name + ".")
                verify_settings[message.guild.id]["MemberRole"] = message.role_mentions[0].id
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'setupgateway':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            if not message.channel_mentions:
                await send_message(message, "You didn't specify a gateway channel! Expecting #CHANNEL_MENTION!")
                return
            
            if not verify_settings[message.guild.id]["VerifyOn"]:
                await send_message(message, "You have not enabled verification! Please enable verification with `f.verifyon` and try your command again!")
                return
            try:
                verify_settings[message.guild.id]["ConfirmMessage"]
            except:
                await send_message(message, "You have no verify message set! Please set a verify message with `f.setverifymessage TEXT`!")
                return
            try:
                verify_settings[message.guild.id]["VerifyEmoji"]
            except:
                await send_message(message, "You have not set a verify emoji! Please set a verify emoji with `f.setverifyemoji EMOJI`!")
                return
            try:
                verify_settings[message.guild.id]["MemberRole"]
            except:
                await send_message(message, "You have not set a member role! Please set a member role with `f.setmemberrole @ROLEMENTION`!")
                return
            channel_id = message.channel_mentions[0].id
            verify_settings[message.guild.id]["GatewayChannelId"] = channel_id
            result = await commit_sql("""UPDATE Verify SET GatewayChannelId=%s WHERE ServerId=%s;""",(str(channel_id),str(message.guild.id)))
            if not result:
                await send_message(message, "Error! Please contact bot support in f.support!")
                return
            initial_channel_obj = client.get_channel(verify_settings[message.guild.id]["GatewayChannelId"])
            response = "Please react to the emoji below to confirm you have read the rules.\n\n" + verify_settings[message.guild.id]["ConfirmMessage"] + "\n"
            message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
            for chunk in message_chunks:
                await initial_channel_obj.send(">>> " + chunk)
            time.sleep(1)
            message_id = initial_channel_obj.last_message_id
            last_message = await initial_channel_obj.fetch_message(message_id)
            verify_settings[message.guild.id]["ConfirmMessageId"] = message_id
            result = await commit_sql("""UPDATE Verify SET ConfirmMessageId=%s WHERE ServerId=%s;""", (str(message_id), str(message.guild.id)))
            if not result:
                await send_message(message, "Error! Please contact bot support in f.support!")
                return

            
            await last_message.add_reaction(verify_settings[message.guild.id]["VerifyEmoji"])
            
            await send_message(message, "Gateway set up successfully!") 

            
        elif command == 'invite':
            await send_message(message, "Click here to invite Firewall: " + invite_link)
            
            
        elif command == 'support':
            await send_message(message, "Click here to join the support server: https://discord.gg/nD6UyyyzEs")

        elif command == 'setmemberlogchannel':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
                
            if not message.channel_mentions:
                await send_message(message, "You did not specify a log channel!")
                return
            channel_id = message.channel_mentions[0].id
            result = await commit_sql("""UPDATE ServerSettings SET MemberLogChannelId=%s WHERE ServerId=%s;""",(str(channel_id),str(message.guild.id)))
            if result:
                server_settings[message.guild.id]["MemberLogChannel"] = message.channel_mentions[0]
                await send_message(message, "Log channel set to <#" + str(channel_id) + ">.")
            else:
                await send_message(message, "Error! Please contact bot support in f.support!") 
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await send_message(message,"Admin command only!")
                return   
            await send_message(message, "Server count: " + str(len(client.guilds)))                 
        elif command == 'setlogchannel':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
                
            if not message.channel_mentions:
                await send_message(message, "You did not specify a log channel!")
                return
            channel_id = message.channel_mentions[0].id
            result = await commit_sql("""UPDATE ServerSettings SET LogChannelId=%s WHERE ServerId=%s;""",(str(channel_id),str(message.guild.id)))
            if result:
                server_settings[message.guild.id]["LogChannel"] = message.channel_mentions[0]
                await send_message(message, "Log channel set to <#" + str(channel_id) + ">.")
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'stoplogging':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
                

            result = await commit_sql("""UPDATE ServerSettings SET LogChannelId=%s WHERE ServerId=%s;""",(str('0'),str(message.guild.id)))
            if result:
                server_settings[message.guild.id]["LogChannel"] = 0
                await send_message(message, "Firewall logging stopped.")
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")                
        elif command == 'stopmemberlogging':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
                
            result = await commit_sql("""UPDATE ServerSettings SET MemberLogChannelId=%s WHERE ServerId=%s;""",(str('0'),str(message.guild.id)))
            if result:
                server_settings[message.guild.id]["MemberLogChannel"] = 0
                await send_message(message, "Member logging stopped.")
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")            
        elif command == 'setbanq':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            # Number of bans, time period.
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters! Expecting NUMBER_OF_BANS TIME_IN_SECONDS!")
                return
                
            ban_re = re.compile(r"(?P<banevents>\d+) (?P<bantime>\d+)")
            m = ban_re.search(parsed_string)
            
            if not m:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_BANS TIME_IN_SECONDS!")
                return
            ban_events = m.group('banevents')
            ban_time = m.group('bantime')
            
            if not ban_events or not ban_time:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_BANS TIME_IN_SECONDS!")
                return                
            result = await commit_sql("""UPDATE ServerSettings SET BanEventCount=%s,BanTimeSeconds=%s WHERE ServerId=%s;""",(str(ban_events),str(ban_time),str(message.guild.id)))
            if result:
                await send_message(message, "Quarantine for bans set to **" + str(ban_events) + "** in **" + str(ban_time) + "** seconds.")
                server_settings[message.guild.id]["BanEventCount"] = int(ban_events)
                server_settings[message.guild.id]["BanTimeSeconds"] = int(ban_time)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
                
                
        elif command == 'setemojiq':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            # Number of emoji updates, time period.
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters! Expecting NUMBER_OF_EMOJI_CHANGES TIME_IN_SECONDS!")
                return
                
            emoji_re = re.compile(r"(?P<emojievents>\d+) (?P<emojitime>\d+)")
            m = emoji_re.search(parsed_string)
            
            if not m:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_EMOJI_CHANGES TIME_IN_SECONDS!")
                return
            emoji_events = m.group('emojievents')
            emoji_time = m.group('emojitime')
            
            if not emoji_events or not emoji_time:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_EMOJI_CHANGES TIME_IN_SECONDS!")
                return                
            result = await commit_sql("""UPDATE ServerSettings SET EmojiEventCount=%s,EmojiTimeSeconds=%s WHERE ServerId=%s;""",(str(emoji_events),str(emoji_time),str(message.guild.id)))
            if result:
                await send_message(message, "Quarantine for emoji changes set to **" + str(emoji_events) + "** in **" + str(emoji_time) + "** seconds.")
                server_settings[message.guild.id]["EmojiEventCount"] = int(emoji_events)
                server_settings[message.guild.id]["EmojiTimeSeconds"] = int(emoji_time)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'setmentionlimit':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify any paramters! Expecting MENTION_LIMIT!")
                return
            mention_re = re.compile(r"(?P<limit>\d+)")
            m = mention_re.search(parsed_string)
            if not m:
                await send_message(message, "You didn't specify the correct paramters! Expecting MENTION_LIMIT!")
                return
            limit = m.group('limit')
            if not limit:
                await send_message(message, "You didn't specify the correct paramters! Expecting MENTION_LIMIT!")
                return
            result = await commit_sql("""UPDATE ServerSettings SET MentionLimit=%s WHERE ServerId=%s;""",(str(limit),str(message.guild.id)))
            if result:
                await send_message(message, "Mention limit set to **" + str(limit) + "** for messages.")
                server_settings[message.guild.id]["MentionLimit"] = int(limit)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
                
        elif command == 'setchannelq':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            # Number of channel deletions, time period.
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters! Expecting NUMBER_OF_CHANNEL_DELETES TIME_IN_SECONDS!")
                return
                
            channel_re = re.compile(r"(?P<channelevents>\d+) (?P<channeltime>\d+)")
            m = channel_re.search(parsed_string)
            
            if not m:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_CHANNEL_DELETES TIME_IN_SECONDS!")
                return
            channel_events = m.group('channelevents')
            channel_time = m.group('channeltime')
            
            if not channel_events or not channel_time:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_CHANNEL_DELETES TIME_IN_SECONDS!")
                return                
            result = await commit_sql("""UPDATE ServerSettings SET ChannelEventCount=%s,ChannelTimeSeconds=%s WHERE ServerId=%s;""",(str(channel_events),str(channel_time),str(message.guild.id)))
            if result:
                await send_message(message, "Quarantine for channel changes set to **" + str(channel_events) + "** in **" + str(channel_time) + "** seconds.")
                server_settings[message.guild.id]["ChannelEventCount"] = int(channel_events)
                server_settings[message.guild.id]["ChannelTimeSeconds"] = int(channel_time)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'purgehistory':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return 
            result = await commit_sql("""DELETE FROM ChannelHistory WHERE ServerId=%s;""",(str(message.guild.id),))
            result = await commit_sql("""DELETE FROM RoleHistory WHERE ServerId=%s;""",(str(message.guild.id),))
            result = await commit_sql("""DELETE FROM EmojiHistory WHERE ServerId=%s;""",(str(message.guild.id),))
            result = await commit_sql("""DELETE FROM BanHistory WHERE ServerId=%s;""",(str(message.guild.id),))
            await send_message(message, "All history purged!")
        elif command == 'showwhitelist':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            print(server_settings[message.guild.id])
            response = "**ADMINISTRATOR WHITELIST**\n\n"
            for user in server_settings[message.guild.id]["Whitelist"]:
                print(user)
                response = response + discord.utils.get(message.guild.members, id=user).name + "\n"
            await send_message(message, response)
        elif command == 'showchannelhistory':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            records = await select_sql("""SELECT UserName, ChannelName, TimeStamp FROM ChannelHistory WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No channel history to show!")
                return
                
            response = "**Channel Deletion History:**"
            for row in records:
               response = response + row[0] +  " deleted channel " + row[1] + " at " + str(row[2]) + " central time.\n"
            await send_message(message, response)
        elif command == 'showrolehistory':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            records = await select_sql("""SELECT UserName, RoleName, TimeStamp FROM RoleHistory WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No role history to show!")
                return
                
            response = "**Role Deletion History:**"
            for row in records:
               response = response + row[0] +  " deleted role " + row[1] + " at " + str(row[2]) + " central time.\n"
            await send_message(message, response)            
        elif command == 'showemojihistory':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            records = await select_sql("""SELECT UserName, EmojisDeleted, TimeStamp FROM EmojiHistory WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "There's no emoji history yet!")
                return
            response = "**EMOJI DELETION HISTORY**\n\n"
            for row in records:
                response = response + row[0] + " deleted emojis " + str(row[1]) + " at " + str(row[2]) + ".\n"
            await send_message(message, response)
        elif command == 'showbanhistory':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            records = await select_sql("""SELECT UserName, BannedUserName, TimeStamp FROM BanHistory WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "There's no ban history yet!")
                return
            response = "**BAN HISTORY**\n\n"
            for row in records:
                response = response + row[0] + " banned user " + row[1] + " at " + str(row[2]) + ".\n"
            await send_message(message, response)
        elif command == 'setminage':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters! Expecting MINIMUM_ACOUNT_AGE_IN_DAYS!")
                return
            days_re = re.compile(r"(?P<days>\d+)")
            m = days_re.search(parsed_string)
            if not m:
                await send_message(message, "You didn't specify the correct parameters! Expecting MINIMUM_ACOUNT_AGE_IN_DAYS!")
                return
            days = m.group('days')
            if not days:
                await send_message(message, "You didn't specify the correct parameters! Expecting MINIMUM_ACOUNT_AGE_IN_DAYS!")
                return
            result = await commit_sql("""UPDATE ServerSettings SET MinimumAccountAge=%s WHERE ServerId=%s;""",(str(days),str(message.guild.id)))
            if result:
                await send_message(message, "The minimum account age to avoid quarantine upon join has been set to **" + str(days) + "** days.")
                server_settings[message.guild.id]["MinimumAccountAge"] = int(days)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'setroleq':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            # Number of role deletions, time period.
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters! Expecting NUMBER_OF_ROLE_DELETES TIME_IN_SECONDS!")
                return
                
            role_re = re.compile(r"(?P<roleevents>\d+) (?P<roletime>\d+)")
            m = role_re.search(parsed_string)
            
            if not m:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_ROLE_DELETES TIME_IN_SECONDS!")
                return
            role_events = m.group('roleevents')
            role_time = m.group('roletime')
            
            if not role_events or not role_time:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_ROLE_DELETES TIME_IN_SECONDS!")
                return                
            result = await commit_sql("""UPDATE ServerSettings SET RoleEventCount=%s,RoleTimeSeconds=%s WHERE ServerId=%s;""",(str(role_events),str(role_time),str(message.guild.id)))
            if result:
                await send_message(message, "Quarantine for role deletions set to **" + str(role_events) + "** in **" + str(role_time) + "** seconds.")
                server_settings[message.guild.id]["RoleEventCount"] = int(role_events)
                server_settings[message.guild.id]["RoleTimeSeconds"] = int(role_time)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'setdefault':
            if message.author != message.guild.owner:
                await send_message(message, "Only the server owner can reset defaults!")
                return
                
            records = await select_sql("""SELECT Id FROM ServerSettings WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                result = await commit_sql("""INSERT INTO ServerSettings (ServerId, UserId, BanEventCount, BanTimeSeconds, EmojiEventCount, EmojiTimeSeconds, ChannelEventCount, ChannelTimeSeconds, RoleEventCount, RoleTimeSeconds,MentionLimit,MinimumAccountAge) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",(str(message.guild.id),str(message.guild.owner.id), str(default_ban_events), str(default_ban_time), str(default_emoji_events), str(default_emoji_time), str(default_channel_events),str(default_channel_time), str(default_role_events), str(default_role_time),str(default_mention_limit),str(default_min_age)))
            else:
                result = await commit_sql("""UPDATE ServerSettings SET UserId=%s, BanEventCount=%s, BanTimeSeconds=%s, EmojiEventCount=%s, EmojiTimeSeconds=%s, ChannelEventCount=%s, ChannelTimeSeconds=%s, RoleEventCount=%s, RoleTimeSeconds=%s, MentionLimit=%s, MinimumAccountAge=%s WHERE ServerId=%s;""",(str(message.guild.owner.id), str(default_ban_events), str(default_ban_time), str(default_emoji_events), str(default_emoji_time), str(default_channel_events),str(default_channel_time), str(default_role_events), str(default_role_time),str(default_mention_limit),str(default_min_age), str(message.guild.id)))
            if result:
                server_settings[message.guild.id] = {} 
                server_settings[message.guild.id]["Whitelist"] = message.guild.owner
                server_settings[message.guild.id]["BanEventCount"] = default_ban_events
                server_settings[message.guild.id]["BanTimeSeconds"] = default_ban_time
                server_settings[message.guild.id]["EmojiEventCount"] = default_emoji_events
                server_settings[message.guild.id]["EmojiTimeSeconds"] = default_emoji_time
                server_settings[message.guild.id]["ChannelEventCount"] = default_channel_events
                server_settings[message.guild.id]["ChannelTimeSeconds"] = default_channel_time
                server_settings[message.guild.id]["RoleEventCount"] = default_role_events
                server_settings[message.guild.id]["RoleTimeSeconds"] = default_role_time
                server_settings[message.guild.id]["MentionLimit"] = default_mention_limit
                server_settings[message.guild.id]["MinimumAccountAge"] = default_min_age
                server_settings[message.guild.id]["PictureLimit"] = default_picture_limit
                server_settings[message.guild.id]["PictureTimeSeconds"] = default_picture_time
                
                await send_message(message, "Defaults restored!")
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'listsettings':
            try:
                server_settings[message.guild.id]
            except:
                await send_message(message, "This server has no setting defined!")
                return
            embed = discord.Embed(title="Settings for " + message.guild.name)
            try:
                embed.add_field(name="Ban Event Count:",value=server_settings[message.guild.id]["BanEventCount"])
            except:
                embed.add_field(name="Ban Event Count:",value="Not set")
            try:    
                embed.add_field(name="Ban Event Time (Seconds):",value=server_settings[message.guild.id]["BanTimeSeconds"])
            except:
                embed.add_field(name="Ban Event Time (Seconds):",value="Not set")
            try:
                embed.add_field(name="Emoji Event Count:",value=server_settings[message.guild.id]["EmojiEventCount"])
            except:
                embed.add_field(name="Emoji Event Count:",value="Not set")
                
            try:
                embed.add_field(name="Emoji Event Time (Seconds):",value=server_settings[message.guild.id]["EmojiTimeSeconds"])
            except:
                embed.add_field(name="Emoji Event Time (Seconds):",value="Not set")
            try:
                embed.add_field(name="Channel Event Count:",value=server_settings[message.guild.id]["ChannelEventCount"])
            except:
                embed.add_field(name="Channel Event Count:",value="Not set")
                
            try:
                embed.add_field(name="Channel Event Time (Seconds):",value=server_settings[message.guild.id]["ChannelTimeSeconds"])
            except:
                embed.add_field(name="Channel Event Time (Seconds):",value="Not set")
                
            try:
                embed.add_field(name="Role Event Count:",value=server_settings[message.guild.id]["RoleEventCount"])
            except:
                embed.add_field(name="Role Event Count:",value="Not set")
            try:    
                embed.add_field(name="Role Event Time (Seconds):",value=server_settings[message.guild.id]["RoleTimeSeconds"])
            except:
                embed.add_field(name="Role Event Time (Seconds):",value="Not set")
                
            try:    
                embed.add_field(name="Mention Limit:", value=server_settings[message.guild.id]["MentionLimit"])
            except:
                embed.add_field(name="Mention Limit:", value="Not set")
                
            try:
                embed.add_field(name="Minimum Account Age to Post (Days):",value=server_settings[message.guild.id]["MinimumAccountAge"])
            except:
                embed.add_field(name="Minimum Account Age to Post (Days):",value="Not set")
            try:
                embed.add_field(name="Picture Post Count:",value=server_settings[message.guild.id]["PictureLimit"])
            except:
                embed.add_field(name="Picture Post Count:",value="Not set")
            try:
                embed.add_field(name="Picture Post Time:",value=server_settings[message.guild.id]["PictureTimeSeconds"])
            except:
                embed.add_field(name="Picture Post Time:",value="Not set")
            await message.channel.send(embed=embed)
            

        elif command == 'setpictureq':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return        
            # Number of role deletions, time period.
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters! Expecting NUMBER_OF_PICTURE_POSTS TIME_IN_SECONDS!")
                return
                
            role_re = re.compile(r"(?P<picturelimit>\d+) (?P<picturetime>\d+)")
            m = role_re.search(parsed_string)
            
            if not m:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_PICTURE_POSTS TIME_IN_SECONDS!")
                return
            picture_limit = m.group('picturelimit')
            picture_time = m.group('picturetime')
            
            if not picture_limit or not picture_time:
                await send_message(message, "You did not specify the correct parameters! Expecting NUMBER_OF_PICTURE_POSTS TIME_IN_SECONDS!")
                return                
            result = await commit_sql("""UPDATE ServerSettings SET PictureLimit=%s,PictureTimeSeconds=%s WHERE ServerId=%s;""",(str(picture_limit),str(picture_time),str(message.guild.id)))
            if result:
                await send_message(message, "Quarantine for picture posts set to **" + str(picture_limit) + "** in **" + str(picture_time) + "** seconds.")
                server_settings[message.guild.id]["PictureLimit"] = int(picture_limit)
                server_settings[message.guild.id]["PictureTimeSeconds"] = int(picture_time)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
        elif command == 'addbadwords':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify any bad words to add!")
                return
            words_to_add = parsed_string.split(',')
            already_added = ""
            new_words = ""
            for word in words_to_add:
                parsed_word = word.strip()

                records = await select_sql("""SELECT Id FROM BadWords WHERE ServerId=%s AND BadWord=%s;""",(str(message.guild.id),parsed_word))
                if records:
                    already_added = already_added + parsed_word + ","
                else:
                    result = await commit_sql("""INSERT INTO BadWords (ServerId, BadWord) VALUES (%s, %s);""",(str(message.guild.id), parsed_word))
                    if not result:
                        await send_message(message, "Unable to add " + parsed_word + " due to database error! Please contact bot support in `f.support`!")
                    else:
                        new_words = new_words + parsed_word + ","
            records = await select_sql("""SELECT BadWord FROM BadWords WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                badwords[message.guild.id] = []
                for row in records:
                    badwords[message.guild.id].append(row[0])
            await send_message(message, "**Bad words added:** " + new_words + "\n\n**Words already in list:** " + already_added)
                
        elif command == 'deletebadwords':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify any bad words to delete!")
                return
            words_to_add = parsed_string.split(',')
            for word in words_to_add:
                parsed_word = word.strip()
                already_added = ""
                new_words = ""
                records = await select_sql("""SELECT Id FROM BadWords WHERE ServerId=%s AND BadWord=%s;""",(str(message.guild.id),parsed_word))
                if records:
                    result = await commit_sql("""DELETE FROM BadWords WHERE Id=%s;""",(str(row[0]),))
                    if not result:
                        await send_message(message, "Unable to delete " + parsed_word + " due to database error! Please contact bot support in `f.support`!")
                    else:
                        new_words = new_words + parsed_word + ","                    
                else:
                    already_added = already_added + parsed_word + ","
                    
            records = await select_sql("""SELECT BadWord FROM BadWords WHERE ServerId=%s;""",(str(message.guild.id),_))
            if records:
                badwords[message.guild.id] = []
                for row in records:
                    badwords[message.guild.id].append(row[0])
            await send_message(message, "**Bad words removed:** " + new_words + "\n\n**Words not in list:** " + already_added)
        elif command == 'setbadwordaction':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify a bad word action to perform!")
                return
            if not re.search(r"none|warn|mute|kick|ban", parsed_string):
                await send_message(message, "Please specify a valid action: `none, warn, mute, kick` or `ban`.")
                return
            action = parsed_string.lower().strip()
            result = await commit_sql("""UPDATE ServerSettings SET BadWordAction=%s WHERE ServerId=%s;""",(str(action),str(message.guild.id)))
            if not result:
                await send_message(message, "Database error! Please contact support in `f.support`!")
            else:
                server_settings[message.guild.id]["BadWordAction"] = action
                await send_message(message, "User action upon bad word detection set to **" + action + "**!")
                
        elif command == 'listbadwords':
            try:
                action = server_settings[message.guild.id]["BadWordAction"]
            except:
                server_settings[message.guild.id]["BadWordAction"] = "none"
                action = "none"
                
            try:
                badwords[message.guild.id]
            except:
                badwords[message.guild.id] = "Not set"
                
            response = "The action for bad word detection is set to: **" + action + "**\n\n**Current Bad Word List:** "
            for word in badwords[message.guild.id]:
                response = response + word + ","
            await send_message(message, response)
            
        elif command == 'whois':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            if message.mentions:
                user = message.mentions[0]
                embed = discord.Embed(title="Who is " + user.name)
                embed.add_field(name="Username:",value=user.name)
                embed.add_field(name="Discriminator:",value=str(user.discriminator))
                if user.nick:
                    embed.add_field(name="Nickname:",value=str(user.nick))
                embed.add_field(name="User ID:",value=str(user.id))
                embed.add_field(name="Account Created:",value=str(user.created_at))
                embed.add_field(name="Joined server:",value=str(user.joined_at))
                embed.add_field(name="Status:",value=str(user.status))
                embed.add_field(name="Activity:",value=str(user.activity))
                embed.add_field(name="Top Role:",value=str(user.top_role.name))
                role_list = ""
                for role in user.roles:
                    role_list = role_list + " " + role.name
                embed.add_field(name="Role List:",value=role_list)
                if user.web_status:
                    embed.add_field(name="Web Status:",value=str(user.web_status))
                if user.mobile_status:
                    embed.add_field(name="Mobile Status:",value=str(user.mobile_status))
                if user.desktop_status:
                    embed.add_field(name="Desktop Status:",value=str(user.desktop_status))
                if user.voice:
                    embed.add_field(name="Voice State:",value=str(user.voice))
                    
                if user.premium_since:
                    embed.add_field(name="Premium Since:",value=str(user.premium_since))
                if user.avatar:
                    embed.set_thumbnail(url=str(user.avatar))
                if user.bot:
                    embed.add_field(name="Bot:",value=str(user.bot))
                if user.color:
                    embed.add_field(name="Color",value=str(user.color))

            elif re.search(r"\d+",parsed_string):
                user_id = int(parsed_string.strip())
                for guild in client.guilds:
                    user = discord.utils.get(guild.members,id=user_id)
                    if user:
                        break
                            
                    

                if user is None:
                    user = client.get_user(user_id)
                    if user is None:
                        try:
                            user = await client.fetch_user(user_id)
                        except:
                            await send_message(message, "Unable to find user.")
                            return                        
                        if user is None:
                            await send_message(message, "Unable to find user.")
                            return
                embed = discord.Embed(title="Who is " + user.name)
                embed.add_field(name="User ID:",value=str(user.id))
                embed.add_field(name="Account Created:",value=str(user.created_at))
                try:
                    embed.add_field(name="Discriminator:",value=str(user.discriminator))
                except:
                    pass
                try:
                    embed.add_field(name="Status:",value=str(user.status))
                except:
                    pass
                try:
                    embed.add_field(name="Activity:",value=str(user.activity))
                except:
                    pass
                try:
                    embed.add_field(name="Web Status:",value=str(user.web_status))
                except:
                    pass
                try:
                    embed.add_field(name="Mobile Status:",value=str(user.mobile_status))
                except:
                    pass                    
                try:
                    embed.add_field(name="Desktop Status:",value=str(user.desktop_status))
                except:
                    pass                    
                    
                try:
                    embed.add_field(name="Premium Since:",value=str(user.premium_since))
                except:
                    pass                    
                try:
                    embed.set_thumbnail(url=str(user.avatar))
                except:
                    pass                    
                try:
                    embed.add_field(name="Bot:",value=str(user.bot))
                except:
                    pass                    
                   
            await message.channel.send(embed=embed)
               
        elif command == 'serverstats':
            embed = discord.Embed(title="Server Statistics for " + message.guild.name + ".")
            embed.add_field(name="Server ID:",value=str(message.guild.id))
            embed.add_field(name="Server Owner:", value=message.guild.owner.name)
            embed.add_field(name="Created on:", value=str(message.guild.created_at))
            embed.add_field(name="Member Count:",value=str(message.guild.member_count))
            if message.guild.icon:
                embed.set_thumbnail(url=str(message.guild.icon))
            embed.add_field(name="Emoji Count:",value=str(len(message.guild.emojis)))
            embed.add_field(name="Role Count:",value=str(len(message.guild.roles)))
            embed.add_field(name="Number of text channels:",value=str(len(message.guild.text_channels)))
            embed.add_field(name="Number of voice channels:",value=str(len(message.guild.voice_channels)))
            if message.guild.features:
                feature_list = ""
                for feature in message.guild.features:
                    feature_list = feature_list + " " + str(feature)
                embed.add_field(name="Guild Features:",value=feature_list)
            await message.channel.send(embed=embed)
            
        elif command == 'listverifysettings':
            try:
                verify_settings[message.guild.id]
            except:
                await send_message(message, "This server has no verify settings defined!")
                return
            embed = discord.Embed(title="Verify settings for " + message.guild.name)
            embed.add_field(name="Verify Status:",value=str(verify_settings[message.guild.id]["VerifyOn"]))
            try:
                embed.add_field(name="Verify Gateway Channel:",value="<#" + str(verify_settings[message.guild.id]["GatewayChannelId"]) +">")
            except:
                embed.add_field(name="Verify Gateway Channel:",value="Not set")
 #           embed.add_field(name="Verify Confirm Message:",value=str(verify_settings[message.guild.id]["ConfirmMessage"]))
            try:
                embed.add_field(name="Verify Emoji:",value=str(verify_settings[message.guild.id]["VerifyEmoji"]))
            except:
                embed.add_field(name="Verify Emoji:",value="Not set")
            try:
                embed.add_field(name="Full Member Role:",value=(discord.utils.get(message.guild.roles,id=verify_settings[message.guild.id]["MemberRole"])).name)
            except:
                embed.add_field(name="Full Member Role:",value="Not set")
            try:    
                embed.add_field(name="Verify Timeout:",value=str(verify_settings[message.guild.id]["VerifyTimeout"]) + " minutes")
            except:
                embed.add_field(name="Verify Timeout:",value="Not set")
            try:
                embed.add_field(name="Verify Timeout Action:",value=str(verify_settings[message.guild.id]["VerifyTimeoutAction"]))
            except:
                embed.add_field(name="Verify Timeout Action:",value="Not set")
            await message.channel.send(embed=embed)
            try:
                await send_message(message, "**Verify Message:**\n\n" + str(verify_settings[message.guild.id]["ConfirmMessage"]))
            except:
                await send_message(message, "**Verify Message:**\n\nNot set.")
        elif command == 'addtowhitelist':
            # must be server owner, add mention to admin whitelist
            if message.author != message.guild.owner:
                await send_message(message, "Only the server owner may modify the whitelist!")
                return
            if not message.mentions:
                await send_message(message, "You didn't mention a user to add to the whitelist!")
                return
            records = await select_sql("""SELECT Id FROM ServerWhitelist WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.mentions[0].id)))
            if records:
                await send_message(message, message.mentions[0].name + " is already in the whitelist!")
                return
            result = await commit_sql("""INSERT INTO ServerWhitelist (ServerId, UserId) VALUES (%s, %s);""",(str(message.guild.id),(str(message.mentions[0].id))))
            if result:
                await send_message(message, message.mentions[0].name + " added to administrator whitelist!")
                server_settings[message.guild.id]["Whitelist"].append(message.mentions[0].id)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
               
            
            
        elif command == 'deletefromwhitelist':
            # Must be server owner, remove mention from admin whitelist
            if message.author != message.guild.owner:
                await send_message(message, "Only the server owner may modify the whitelist!")
                return
            if not message.mentions:
                await send_message(message, "You didn't mention a user to delete from the whitelist!")
                return
            records = await select_sql("""SELECT Id FROM ServerWhitelist WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.mentions[0].id)))
            if not records:
                await send_message(message, message.mentions[0].name + " is not in the whitelist!")
                return
            result = await commit_sql("""DELETE FROM ServerWhitelist WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),(str(message.mentions[0].id))))
            if result:
                await send_message(message, message.mentions[0].name + " deleted from administrator whitelist!")
                server_settings[message.guild.id]["Whitelist"].remove(message.mentions[0].id)
            else:
                await send_message(message, "Error! Please contact bot support in f.support!")
           
            
        elif command == 'takebackup':
            pass
        elif command == 'restore':
            # backup ID
            pass
        elif command == 'listbackups':
            pass
            
        elif command == 'purgebackups':
            pass
            
        elif command == 'deletebackup':
            pass
            
        elif command == 'quarantine' or command == 'q':
            # Quarantine a mention
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return           
            if not message.mentions:
                id_re = re.compile(r"(?P<id>\d+)")
                m = id_re.search(parsed_string)
                if not m:
                    await send_message(message, "You did not mention a user or specify an ID to quarantine!")
                    return
                user = discord.utils.get(message.guild.members,id=int(m.group('id').strip()))
            else:
                user = message.mentions[0]
            if not await role_compare(message.author, user):
                await send_message(message, "You cannot quarantine a user with a higher role!")
                return                
            if user.id in server_settings[message.guild.id]["Whitelist"]:
                await send_message(message, "Cannot quarantine a whitelisted user!")
                return
            result = await quarantine(message.guild, user, "Quarantined via command by " + message.author.name)
            if result:
                await send_message(message, "User was quarantined!")
            else:
                await send_message(message, "Failed to quarantine user!")
            
        elif command == 'unq' or command == 'unquarantine':
            # restore a mention to old roles
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return          
            if not message.mentions:
                id_re = re.compile(r"(?P<id>\d+)")
                m = id_re.search(parsed_string)
                if not m:
                    await send_message(message, "You did not mention a user or specify an ID to quarantine!")
                    return
                user = message.guild.get_member(int(m.group('id').strip()))
            else:
                user = message.mentions[0]
                
            result = await unquarantine(message.guild, user)
            if result:
                await send_message(message, "User was successfully unquarantined!")
            else:
                await send_message(message, "Failed to unquarantine user!")
                
            
        elif command == 'ban':
            # ban a mention or user id
            if not parsed_string:
                await send_message(message, "You did not specify a user to ban!")
                return
            if not message.author.guild_permissions.ban_members:
                await send_message(message, "You do not have permission to ban users!")
                return
            if not message.mentions:
                id_re = re.compile(r"(?P<id>\d+)")
                m = id_re.search(parsed_string)
                print(m.group('id'))
                if not m:
                    await send_message(message, "You did not mention a user or specify an ID to ban!")
                    return
                user = discord.utils.get(message.guild.members,id=int(m.group('id')))
                if not user:
                    try:
                        user = await client.fetch_user(int(m.group('id')))
                    except:
                        await send_message(message, "Unable to find user on Discord!")
                        return
            else:
                user = message.mentions[0]                
            if parsed_string.strip():
                reason = re.sub(r"<.*>","",parsed_string)
                reason = re.sub(r"\d+","", reason)
            else:
                reason = "Banned by " + message.author.name
            if message.guild.owner != message.author:
                if not await role_compare(message.author, user):
                    await send_message(message, "You cannot ban a user with a higher role!")
                    return
            if not user:
                await send_message(message, "Unable to find user account!")
            await message.guild.ban(user)
                
            await send_message(message, "User was banned!")
        elif command == 'massban':
            # ban a mention or user id
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return 
            if not message.author.guild_permissions.ban_members:
                await send_message(message, "You do not have permission to ban users!")
                return
            if not message.mentions:
                await send_message(message, "You did not mention users to ban!")
                return
            for user in message.mentions:
                reason = "Banned by " + message.author.name                
                if not await role_compare(message.author, user):
                    await send_message(message, "You cannot ban a user with a higher role!")
                    return                
                await user.ban()
                
            await send_message(message, "Users were banned!")            
            
        elif command == 'unban':
            # ban a mention or user id
            if not parsed_string:
                await send_message(message, "You did not specify a user to ban!")
                return
            if not message.author.guild_permissions.ban_members:
                await send_message(message, "You do not have permission to unban users!")
                return
            if not message.mentions:
                id_re = re.compile(r"(?P<id>\d+)")
                m = id_re.search(parsed_string)
                if not m:
                    await send_message(message, "You did not mention a user or specify an ID to unban!")
                    return
                user = client.get_user(int(m.group('id')))
            else:
                user = message.mentions[0]                
            await message.guild.unban(user)
                
            await send_message(message, "User has been unbanned!")
            
        elif command == 'kick':
            # kick a mention or user ID
            if not parsed_string:
                await send_message(message, "You did not specify a user to kick!")
                return
            if not message.author.guild_permissions.kick_members:
                await send_message(message, "You do not have permission to kick users!")
                return
            if parsed_string:
                reason = re.sub(r"<.*>","",parsed_string)
                reason = re.sub(r"\d+","", reason)
            else:
                reason = "Kicked by " + message.author.name
            if not message.mentions:
                id_re = re.compile(r"(?P<id>\d+)")
                m = id_re.search(parsed_string)
                if not m:
                    await send_message(message, "You did not mention a user or specify an ID to kick!")
                    return
                user = message.guild.get_member(int(m.group('id')))
            else:
                user = message.mentions[0]                
            if not await role_compare(message.author, user):
                await send_message(message, "You cannot kick a user with a higher role!")
                return       

            await user.kick(reason=reason)

            await send_message(message, "User was kicked!")
            
        elif command == 'mute':
            # Mute a mention or user ID
            if not message.mentions:
                await send_message(message, "You did not mention a user to mute!")
                return
            if not message.author.guild_permissions.kick_members:
                await send_message(message, "You do not have permission to mute users!")
                return
            if not message.mentions:
                id_re = re.compile(r"(?P<id>\d+)")
                m = id_re.search(parsed_string)
                if not m:
                    await send_message(message, "You did not mention a user or specify an ID to mute!")
                    return
                user = discord.utils.get(message.guild.members,int(m.group('id')))
            else:
                user = message.mentions[0]                
            if not await role_compare(message.author, user):
                await send_message(message, "You cannot mute a user with a higher role!")
                return
            
            result = await quarantine(message.guild, user, "Muted via command by " + message.author.name)
            if result:
                await send_message(message, "User was muted!")
            else:
                await send_message(message, "Failed to mute user!")
        
        elif command == 'unmute':
            # unmute a mention or user ID
            if not message.mentions:
                await send_message(message, "You didn't mention anyone to unmute!")
                return
            if not message.author.guild_permissions.kick_members:
                await send_message(message, "You do not have permission to unmute users!")
                return
            if not message.mentions:
                id_re = re.compile(r"(?P<id>\d+)")
                m = id_re.search(parsed_string)
                if not m:
                    await send_message(message, "You did not mention a user or specify an ID to quarantine!")
                    return
                user = discord.utils.get(message.guild.members,int(m.group('id')))
            else:
                user = message.mentions[0]
            result = await unquarantine(message.guild, user)
            if result:
                await send_message(message, "User was successfully unmuted!")
            else:
                await send_message(message, "Failed to unmute user!")
        elif command == 'rezz':
            if not message.author.guild_permissions.kick_members:
                await send_message(message, "You do not have permission to unmute users!")
                return
          
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
                
            user = message.mentions[0]
            try:
                await direct_message(user, "You have been unmuted in " + message.guild.name, message.guild)
            except:
                pass
            asyncio.sleep(1)    
            await unquarantine(message.guild, user)
            asyncio.sleep(1)
            try:
                await hell[message.guild.id][user.id]["channel"].delete()
                await hell[message.guild.id][user.id]["cat"].delete()
                del hell[message.guild.id][user.id]
            except:
                pass
            #await user.edit(mute=True)

            await send_message(message, "User " + user.name + " has been unmuted!")
        elif command == 'dmsoff':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            result = await commit_sql("""UPDATE ServerSettings SET DMStatus=0 WHERE ServerId=%s;""",(str(message.guild.id),))
            if result:
                server_settings[message.guild.id]["DMStatus"] = 0
                await send_message(message, "DM status updated to **OFF.**")
            else:
                await send_message(message, "Database error! Please contact the developer in f.support!")
        elif command == 'dmson':
            if not await security_check(message.guild.id, message.author.id):
                await send_message(message, "You are not authorized to use this command!")
                return
            result = await commit_sql("""UPDATE ServerSettings SET DMStatus=1 WHERE ServerId=%s;""",(str(message.guild.id),))
            if result:
                server_settings[message.guild.id]["DMStatus"] = 1
                await send_message(message, "DM status updated to **ON.**")
            else:
                await send_message(message, "Database error! Please contact the developer in f.support!")                
        elif command == 'reap':
            if not message.author.guild_permissions.kick_members:
                await send_message(message, "You do not have permission to unmute users!")
                return        
            if not message.mentions:
                await send_message(message, "You didn't specify a user!")
                return
                
            user = message.mentions[0]

            await direct_message(user, "You have been reaped in " + message.guild.name, message.guild)
            await quarantine(message.guild, user, "Reaped by " + message.author.name)
            full_role = message.guild.get_role(int(verify_settings[message.guild.id]["MemberRole"]))
            new_role = discord.utils.get(message.guild.roles, name="quarantine")
            overwrites = { user: discord.PermissionOverwrite(read_messages=True), message.guild.default_role: discord.PermissionOverwrite(read_messages=False), full_role: discord.PermissionOverwrite(read_messages=False), new_role: discord.PermissionOverwrite(read_messages=False) }
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
        elif command == 'giverole':
            if not message.author.guild_permissions.manage_roles:
                await send_message(message, "You must have manage role permissions to change a user's role!")
                return
            if not parsed_string:
                await send_message(message, "You did not specify any role to add!")
                return
            if not message.mentions:
                await send_message(message, "You did not specify a user to add the role to!")
                return
            role_name = re.sub(r"<.*>","",parsed_string, re.I).strip()
            role_found = False
            role_to_add = None
            for role in message.guild.roles:
                if role_name == role.name:
                    role_found = True
                    role_to_add = role
            if not role_found:
                await send_message(message, "A role by that name was not found on this server!")
                return
            if not await role_compare(message.author, message.mentions[0]):
                await send_message(message, "You cannot change the roles of a user with higher roles than yourself!")
                return
            if role_to_add > message.author.top_role:
                await send_message(message, "You cannot add a role to someone higher than your own top role!")
                return
            try:
                await message.mentions[0].add_roles(role_to_add)
                await send_message(message, "Added " + role_name + " to user " + message.mentions[0].name + ".")
            except:
                await send_message(message, "Error adding role!")
        elif command == 'takerole':
            if not message.author.guild_permissions.manage_roles:
                await send_message(message, "You must have manage role permissions to change a user's role!")
                return
            if not parsed_string:
                await send_message(message, "You did not specify any role to remove!")
                return
            if not message.mentions:
                await send_message(message, "You did not specify a user to remove the role from!")
                return
            role_name = re.sub(r"<.*>","",parsed_string, re.I).strip()
            role_found = False
            role_to_add = None
            for role in message.guild.roles:
                if role_name == role.name:
                    role_found = True
                    role_to_add = role
            if not role_found:
                await send_message(message, "A role by that name was not found on this server!")
                return
            if not await role_compare(message.author, message.mentions[0]):
                await send_message(message, "You cannot change the roles of a user with higher roles than yourself!")
                return
            if role_to_add > message.author.top_role:
                await send_message(message, "You cannot add a role to someone higher than your own top role!")
                return                
            try:
                await message.mentions[0].remove_roles(role_to_add)
                await send_message(message, "Removed " + role_name + " from user " + message.mentions[0].name + ".")
            except:
                await send_message(message, "Error removing role!")                
        elif command == 'addreactionrole':
            if not message.author.guild_permissions.manage_roles:
                await send_message(message, "You must have manage role permissions to add a reaction role!")
                return
            m = re.search(r"-description (?P<description>.+) -emoji",parsed_string)
            if not m:
                await send_message(message, "You didn't provide a description!")
                return
            description = m.group('description')
            m = re.search(r"-emoji (?P<reaction>.+) -role",parsed_string)
            if not m:
                await send_message(message, "You didn't specifiy an emoji for the reaction!")
                return
            reaction = m.group('reaction')
            reaction = reaction.strip()
            m = re.search(r"-role (?P<rolename>.+)",parsed_string)
            if not m:
                await send_message(message, "You didn't specify a role name!")
                return
            role_name = m.group('rolename')
            role_found = False
            reaction_role = None
            for role in message.guild.roles:
                if role.name == role_name.strip():
                    role_found = True
                    reaction_role = role
            if not role_found or reaction_role is None:
                await send_message(message, "That role doesn't exist. Please create it first.")
                return
            new_message = await message.channel.send(description + " - " + role_name)
            try:
                await new_message.add_reaction(reaction)
            except:
                await send_message(message, "A reaction could not be added, please check permissions.")
                return
            result = await commit_sql("""INSERT INTO ReactionRoles (ServerId, UserId, Emoji, RoleId, MessageId, Description, ChannelId) VALUES (%s, %s, %s, %s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id), str(reaction), str(reaction_role.id), str(new_message.id), str(description),str(message.channel.id)))
            await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> User " + message.author.name + " created a reaction role in "  + message.channel.name +  " with role of " + reaction_role.name + ", emoji of " + str(reaction) + ", and description of " + description + "."))
            await message.delete()
        elif command == 'passthru':
            if not message.author.guild_permissions.manage_roles:
                await send_message(message, "You must have manage role permissions to pass through a user!")
                return
            if not parsed_string and not message.mentions:
                await send_message(message, "You did not specify a user to pass through!")
                return
            if message.mentions:
                await unquarantine(message.guild, message.mentions[0])
                role = discord.utils.get(message.guild.roles, id=verify_settings[message.guild.id]["MemberRole"])
                await message.mentions[0].add_roles(role)                
                await send_message(message, message.mentions[0].display_name + " has been verified manually.")
            else:
                if not re.search(r"\d+",parsed_string):
                    await send_message(message, "You did not specify a valid user ID!")
                    return
                user = discord.utils.get(message.guild.members,id=int(parsed_string.strip()))
                await unquarantine(message.guild,user)
                role = discord.utils.get(message.guild.roles, id=verify_settings[message.guild.id]["MemberRole"])
                await user.add_roles(role)                
                await send_message(message, user.display_name + " has been verified manually.")
        elif command == 'deletereactionrole':
            if not message.author.guild_permissions.manage_roles:
                await send_message(message, "You must have manage role permissions to delete a reaction role!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify a role reaction to delete!")
                return
            role_found = False
            reaction_role = None
            for role in message.guild.roles:
                if role.name == parsed_string.strip():
                    role_found = True
                    reaction_role = role
            if not role_found or reaction_role is None:
                await send_message(message, "That role reaction was not found!")
                return
            role_id = reaction_role.id
            records = await select_sql("""SELECT Id,MessageId,ChannelId FROM ReactionRoles WHERE ServerId=%s AND RoleId=%s;""",(str(message.guild.id),str(role_id)))
            if not records:
                await send_message(message, "You do not have that defined as a reaction role!")
                return
            for row in records:
                record_id = row[0]
                message_id = row[1]
                channel_id = row[2]
            old_channel = discord.utils.get(message.guild.channels,id=int(channel_id))
            if not old_channel:
                await send_message(message, "Could not find the channel the reaction role is in!")
                return
            old_message = await old_channel.fetch_message(int(message_id))
            if not old_message:
                await send_message(message, "Could not find the message the reaction role is in!")
            await commit_sql("""DELETE FROM ReactionRoles WHERE Id=%s;""",(str(record_id),))
            
            await old_message.delete()
            await message.delete()
            await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> User " + message.author.name + " deleted a reaction role with role "  + reaction_role.name + "."))
        elif command == 'listreactionroles':
            records = await select_sql("""SELECT RoleId,Emoji,Description FROM ReactionRoles WHERE ServerId=%s;""",(str(message.guild.id),))
            
            if not records:
                await send_message(message, "There are no reaction roles defined on the server.")
                return
            response = "**Server Reaction Roles**\n\n"
            for row in records:
                role_name = discord.utils.get(message.guild.roles, id=int(row[0])).name
                response = role_name + " - "  + row[2] + " - "  + str(row[1]) + "\n"
            await send_message(message, response)
        elif command == 'purge':
            if not message.author.guild_permissions.manage_messages:
                await send_message(message, "You don't have permission to manage messages!")
                return
            if not parsed_string:
                await send_message(message, "Not enough parameters! Please specify a number of messages to purge or user's messages to delete via mention!")
                return
            m = re.search(r"(?P<number>\d+)",str(re.sub(r"<.+>","",parsed_string)))
            if not m and not message.mentions:
                await send_message(message, "Number of messages to purge not specified!")
                return
                
            if not message.mentions:
                number = int(m.group('number'))
                if number > 100:
                    await send_message(message, "Cannot delete more than 100 messages at a time!")
                    return            
                del_messages = len(await message.channel.purge(limit=number))
            else:
                del_messages = 0
                message_history = await message.channel.history(limit=500).flatten()
                for user in message.mentions:
                    for old_message in message_history:
                        if old_message.author == user:
                            await old_message.delete()
                            del_messages = del_messages + 1
                            
            if not del_messages or del_messages == 0:
                await send_message(message, "No messages deleted!")
            else:
                await send_message(message, str(del_messages) + " messages purged.")
                

    
    # Bad word checks. If the channel is ignored or the user is whitelisted, don't bother checking!
    
    if message.channel.id in ignore_channels[message.guild.id]:
        return
    if message.author.id in server_settings[message.guild.id]["Whitelist"]:
        return
    for badword in badwords[message.guild.id]:
        print("Checking for " + badword)
        if re.search(badword, message.content, re.IGNORECASE | re.MULTILINE):
            print("Found bad word. Action=" + server_settings[message.guild.id]["BadWordAction"])
            if server_settings[message.guild.id]["BadWordAction"] == 'none':
#                try:
                await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + message.author.name + " used the word " + badword + " in <#" +str( message.channel.id) + "> but no action was taken. Entire message: ```" + message.content + "```"))
                #except:
                 #   pass
            elif server_settings[message.guild.id]["BadWordAction"] == 'warn':

                await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + message.author.name + " used the word " + badword + " in <#" +str( message.channel.id) + "> . The message has been deleted and the user warned in DMs. Entire message: ```" + message.content + "```"))

                await message.delete()
                await direct_message(message.author, "You are being warned for using the word "  + badword + " in the server " + message.guild.name + ". Please refrain from using words on the prohibited word list.", message.guild)
               
                
            elif server_settings[message.guild.id]["BadWordAction"] == 'mute':
                try:
                    await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + message.author.name + " used the word " + badword + " in <#" +str( message.channel.id) + "> . The message has been deleted and the user has been muted. Entire message: ```" + message.content + "```"))
                except:
                    pass
                await message.delete()
                await quarantine(message.guild, message.author, ">>> " + message.author.name + " used the word " + badword + " in <#" +str( message.channel.id) + "> . The message has been deleted and the user has been muted. Entire message: ```" + message.content + "```")
                await direct_message(message.author, "You have been muted for using the word "  + badword + " in the server " + message.guild.name + ". Please refrain from using words on the prohibited word list and contact a moderator or administrator for reinstatement.", message.guild)            
            elif server_settings[message.guild.id]["BadWordAction"] == 'kick':
                try:
                    await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + message.author.name + " used the word " + badword + " in <#" +str( message.channel.id) + "> . The message has been deleted and the user has been kicked. Entire message: ```" + message.content + "```"))
                except:
                    pass
                await message.delete()
                
                await direct_message(message.author, "You have been kicked for using the word "  + badword + " in the server " + message.guild.name + ". Please refrain from using words on the prohibited word list and contact a moderator or administrator for reinstatement or a new invite.", message.guild)
                await message.guild.kick(message.author, reason=">>> " + message.author.name + " used the word " + badword + " in <#" +str( message.channel.id) + "> . The message has been deleted and the user has been kicked. Entire message: ```" + message.content + "```")
                
            elif server_settings[message.guild.id]["BadWordAction"] == 'ban':
                try:
                    await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + message.author.name + " used the word " + badword + " in <#" +str( message.channel.id) + "> . The message has been deleted and the user has been banned. Entire message: ```" + message.content + "```"))
                except:
                    pass
                await message.delete()
                
                await direct_message(message.author, "You have been banned for using the word "  + badword + " in the server " + message.guild.name + ". Please refrain from using words on the prohibited word list and contact a moderator or administrator for reinstatement or a new invite.", message.guild)
                await message.guild.ban(message.author, reason=">>> " + message.author.name + " used the word " + badword + " in <#" +str( message.channel.id) + "> . The message has been deleted and the user has been banned. Entire message: ```" + message.content + "```")  

    # Mention Limit checks                
    if len(message.mentions) > server_settings[message.guild.id]["MentionLimit"] and message.author.id not in server_settings[message.guild.id]["Whitelist"]:
        result = await quarantine(message.guild, message.author, "Quarantined for exceeding mention limit " + message.author.name)
        if result:
            await send_message(message, message.author.name + " was quarantined for exceeding the mention limit!")
            await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + message.author.name + " was quarantined for exceeding the mention limit."))
        else:
            await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + message.author.name + "  exceeded the mention limit but quarantine failed."))
    if message.attachments:
        picture_count[message.guild.id][message.author.id]["PictureCount"] = picture_count[message.guild.id][message.author.id]["PictureCount"] + len(message.attachments)
        picture_count[message.guild.id][message.author.id]["LastPicturePosted"].append(datetime.now())
        picture_count[message.guild.id][message.author.id]["LastPictureCount"].append(len(message.attachments))
        temp_pic_list =  picture_count[message.guild.id][message.author.id]
        
        # Here we are going through each post in the list and deleting it from consideration if it is older than the set server time
        for post in range(0,len(picture_count[message.guild.id][message.author.id]["LastPicturePosted"])):
            if post >= len(picture_count[message.guild.id][message.author.id]["LastPicturePosted"]):
                break        
            if (datetime.now()  - picture_count[message.guild.id][message.author.id]["LastPicturePosted"][post]).total_seconds() >= server_settings[message.guild.id]["PictureTimeSeconds"]:
                print("Message old, removing.")
                picture_count[message.guild.id][message.author.id]["LastPicturePosted"].pop(post)
                picture_count[message.guild.id][message.author.id]["PictureCount"] = picture_count[message.guild.id][message.author.id]["PictureCount"] - picture_count[message.guild.id][message.author.id]["LastPictureCount"][post]
                picture_count[message.guild.id][message.author.id]["LastPictureCount"].pop(post)
                
                post = post + 1

                
        if picture_count[message.guild.id][message.author.id]["PictureCount"] >= server_settings[message.guild.id]["PictureLimit"] and (datetime.now()  - picture_count[message.guild.id][message.author.id]["LastPicturePosted"][0]).total_seconds() < server_settings[message.guild.id]["PictureTimeSeconds"]:
            try:
                await server_settings[message.guild.id]["LogChannel"].send(embed=discord.Embed(title="Firewall Log",description=">>> " + message.author.name + " exceeded the picture limit. The user has been muted."))
            except:
                pass
            await quarantine(message.guild, message.author, ">>> " + message.author.name + " exceeded the picture limit. The user has been muted.")
            await direct_message(message.author, "You have been muted for exceeding the picture posting limits in the server " + message.guild.name + ". Please refrain from posting pictures beyond the set rate limits and contact a moderator or administrator for reinstatement.", message.guild)              
client.run'REDACTED'

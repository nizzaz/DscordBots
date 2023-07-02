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
from discord import Webhook, RequestsWebhookAdapter, File
import csv
import json
import decimal
import asyncio

intents = discord.Intents.all()
client = discord.Client(heartbeat_timeout=600,intents=intents)
server_settings = { }
poll_creator = { } 
active_polls = {} 

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='SurveySays', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='SurveySays', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='SurveySays', user='REDACTED', password='REDACTED')
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
            
async def direct_message(message, response, embed=None):
    channel = await message.author.create_dm()
    await log_message("replied to user " + message.author.name + " in DM with " + response)
    if embed:
        await channel.send(embed=embed)
    else:
        try:
            message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
            for chunk in message_chunks:
                await channel.send("" + chunk)
                await asyncio.sleep(1)
            
        except discord.errors.Forbidden:
            await dm_tracker[message.author.id]["commandchannel"].send("You have DMs off. Please reply with =answer <reply> in the server channel.\n" + response)
        
async def post_webhook(channel, name, response, picture):
    temp_webhook = await channel.create_webhook(name='Chara-Tron')
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
        await asyncio.sleep(1)
        
def role_check(role_required, user):
    for role in user.roles:
        if role.id == role_required:
            return True
            
    return False        

@client.event
async def on_raw_reaction_add(payload):
    global poll_creator
    global server_settings
    global active_polls
    
    await log_message(str(payload))
    if payload.message_id in list(active_polls.keys()):
        vote = active_polls[payload.message_id]["EmojiDict"][str(payload.emoji)]
        poll_id = active_polls[payload.message_id]["PollId"]
        result = await commit_sql("""INSERT INTO Votes (ServerId, UserId, PollId, OptionVoted) VALUES (%s, %s, %s, %s);""",(str(payload.guild_id), str(payload.member.id), str(poll_id), str(vote)))
        await log_message("Recorded vote " + str(payload.emoji) + " from user " + payload.member.name + " for Poll ID: " + str(poll_id))
        return    
    try: 
        poll_creator[payload.guild_id][payload.member.id]
    except:
        poll_creator[payload.guild_id][payload.member.id] = {}
        poll_creator[payload.guild_id][payload.member.id]["MessagesToDelete"] = ()
        
    if payload.message_id in poll_creator[payload.guild_id][payload.member.id]["MessagesToDelete"]:
        user = payload.member
        server_obj = client.get_guild(payload.guild_id)
        poll_creator[payload.guild_id][payload.member.id]["Emojis"].append(str(payload.emoji))
        channel = client.get_channel(server_settings[payload.guild_id]["PollChannel"])
        
        reply = await channel.send(">>> Emoji " + str(payload.emoji) + " added to the poll for option " + poll_creator[payload.guild_id][payload.member.id]["Options"][len(poll_creator[payload.guild_id][payload.member.id]["Options"]) -1] + ". Please reply below with your next option.")
        
        poll_creator[payload.guild_id][payload.member.id]["MessageObjects"].append(reply)        
       
        
    try: 
        active_polls[payload.message_id]
    except:
        active_polls[payload.message_id] = ()
    try:
        active_polls[payload.message_id]["EmojiDict"]
    except:
        return


    

    
@client.event
async def on_raw_reaction_remove(payload):
    global poll_creator
    global server_settings
    global active_polls
    
    await log_message(str(payload))
      
        
    try: 
        active_polls[payload.message_id]
        if payload.message_id in list(active_polls.keys()):
            vote = active_polls[payload.message_id]["EmojiDict"][str(payload.emoji)]
            poll_id = active_polls[payload.message_id]["PollId"]
            result = await commit_sql("""DELETE FROM Votes WHERE ServerId=%s AND UserId=%s AND PollId=%s AND OptionVoted=%s;""",(str(payload.guild_id), str(payload.user_id), str(poll_id), str(vote)))
            await log_message("Deleted vote " + str(payload.emoji) + " from user " + payload.member.name + " for Poll ID: " + str(poll_id))
            return
    except:
        pass    

        
@client.event
async def on_ready():
    global server_settings
    global active_polls
    
    for guild in client.guilds:
        server_settings[guild.id] = { }
    records = await select_sql("""SELECT ServerId, ModeratorChannelId, AdminRoleId, IFNULL(PollRoleId,'0'), IFNULL(PollChannelId,'0') FROM ServerSettings;""")
    for row in records:
        server_id = int(row[0])
#        server_settings[server_id]["ModeratorChannel"] = int(row[1])
#        server_settings[server_id]["AdminRole"] = int(row[2])
        server_settings[server_id]["PollRole"] = int(row[3])
        server_settings[server_id]["PollChannel"] = int(row[4])
    records = await select_sql("""SELECT Id,ServerId, IFNULL(Emojis,' '), IFNULL(MessageId,'0') FROM Polls;""")
    for row in records:
        message_id = int(row[3])
        active_polls[message_id] = { }
        active_polls[message_id]["ServerId"] = int(row[1])
        active_polls[message_id]["PollId"] = int(row[0])
        active_polls[message_id]["EmojiDict"] = {}
        counter = 0
        for x in row[2].split('|'):
            active_polls[message_id]["EmojiDict"][x] = counter
            counter = counter + 1
        
        

@client.event
async def on_guild_join(guild):
    global server_settings
    server_settings[guild.id] = {}
    await commit_sql("""INSERT INTO ServerSettings (ServerId) VALUES(%s);""",(str(guild.id),))

@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)
    await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s;""",(str(guild.id),))

@client.event
async def on_member_join(member):
    if member.guild.id == 264445053596991498:
        return
    await log_message("Member " + member.name + " joined guild " + member.guild.name)
	
@client.event
async def on_member_remove(member):
    pass

@client.event
async def on_message(message):
    global server_settings
    global poll_creator
    global active_polls

    if message.author == client.user:
        return
    if message.author.bot:
    
        return

    if message.guild.id == 264445053596991498:
        return
        
        
    if message.content.startswith('s!'):
        username = message.author.display_name
        server_name = message.guild.name
        # user_id = message.author.id
        # server_id = message.guild.id    

        command_string = message.content.split(' ')
        command = command_string[0].replace('s!','')
        parsed_string = message.content.replace("s!" + command,"")
        parsed_string = re.sub(r"^ ","",parsed_string)


        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        
        if command == 'help' or command == 'info':
            response = "Survey Says!, a bot for creating polls and voting. This bot can help you take a poll of server members.\n\nCOMMANDS:\n\n`s!setpollchannel #channel mention`: Set the channel where polls are created.\n`s!setpollrole @role mention`: Set a role that will be mentioned when new polls are created.\n`s!createpoll question`: Create a new poll with the question posed here.\n\n**To create a poll:** The bot will mention you in the poll channel. Any message you send there except done or cancel will add an option to your poll. Once you add an option, react to your own message with an emoji (*not* the bot's message!) to select that emoji as the reaction for that option. Type done to finish the poll. The bot will create the poll and add the reactions, then delete all the creation messages.\n\n`s!listpolls`: List all active polls by ID.\n`s!votecount ID`: Look at the total votes so far.\n`s!closepoll ID`: End the poll and display the final results."
            await reply_message(message, response)
        elif command == 'setmoderatorrole':
            if not message.role_mentions:
                await reply_message(message, "You didn't specify a role to set as a mention!")
                return
            server_settings[message.guild.id]["AdminRole"] = message.role_mentions[0].id
            result = await commit_sql("""UPDATE ServerSettings SET AdminRoleId=%s WHERE ServerId=%s;""",(str(server_settings[message.guild.id]["AdminRole"]), str(message.guild.id)))
            if result:
                await reply_message(message, "Server moderator role set to role " + message.role_mentions[0].name)
            else:
                await reply_message(message, "Database error!")
        elif command == 'serverlist':
            response = "**SERVER LIST**\n\n"
            for guild in client.guilds:
                response = response + guild.name + "\n"
            response = response + "Server count: " + str(len(client.guilds))
            await reply_message(message, response)                
        elif command == 'setpollrole':
            if not message.role_mentions:
                await reply_message(message, "You didn't specify a role to set as a mention!")
                return
            server_settings[message.guild.id]["PollRole"] = message.role_mentions[0].id
            result = await commit_sql("""UPDATE ServerSettings SET PollRoleId=%s WHERE ServerId=%s;""",(str(server_settings[message.guild.id]["PollRole"]), str(message.guild.id)))
            if result:
                await reply_message(message, "Server poll role set to role " + message.role_mentions[0].name)
            else:
                await reply_message(message, "Database error!")        
        elif command == 'setmoderatorchannel':
            if not message.channel_mentions:
                await reply_message(message, "You didn't specify a channel to set as a mention!")
                return
            server_settings[message.guild.id]["ModChannel"] = message.channel_mentions[0].id
            result = await commit_sql("""UPDATE ServerSettings SET ModeratorChannelId=%s WHERE ServerId=%s;""",(str(server_settings[message.guild.id]["ModChannel"]), str(message.guild.id)))
            if result:
                await reply_message(message, "Server moderator channel set to role " + message.channel_mentions[0].name)
            else:
                await reply_message(message, "Database error!")             
        elif command == 'setpollchannel':
            if not message.channel_mentions:
                await reply_message(message, "You didn't specify a channel to set as a mention!")
                return
            server_settings[message.guild.id]["PollChannel"] = message.channel_mentions[0].id
            result = await commit_sql("""UPDATE ServerSettings SET PollChannelId=%s WHERE ServerId=%s;""",(str(server_settings[message.guild.id]["PollChannel"]), str(message.guild.id)))
            if result:
                await reply_message(message, "Server poll channel set to role " + message.channel_mentions[0].name)
            else:
                await reply_message(message, "Database error!")
        
        elif command == 'createpoll':
            question = parsed_string
            poll_creator[message.guild.id] = { }
            poll_creator[message.guild.id][message.author.id] = {}
            poll_creator[message.guild.id][message.author.id]["Question"] = question
            poll_creator[message.guild.id][message.author.id]["Options"] = []
            poll_creator[message.guild.id][message.author.id]["Emojis"] = []
            poll_creator[message.guild.id][message.author.id]["MessagesToDelete"] = []
            poll_creator[message.guild.id][message.author.id]["MessageObjects"] = []
            result = await commit_sql("""INSERT INTO Polls (ServerId, UserId, PollQuestion) VALUES (%s, %s, %s);""",(str(message.guild.id),str(message.author.id), question))
            if result:
                poll_channel = client.get_channel(server_settings[message.guild.id]["PollChannel"])
                first_message = await poll_channel.send(">>> You have requested a new poll, <@" + str(message.author.id) + ">. Please respond here with the first option of your poll. No command is required.")
                poll_creator[message.guild.id][message.author.id]["MessageObjects"].append(first_message)
            else:
                await reply_message(message, "Database error!")
        elif command == 'votecount':
            if not parsed_string:
                await reply_message(message, "You did not provide a poll ID!")
                return
            records = await select_sql("""SELECT OptionVoted FROM Votes WHERE PollId=%s;""",(parsed_string,))
            if not records:
                await reply_message(message, "No votes recorded yet!")
                return
            poll_responses = {}
            for row in records:
                try: poll_responses[row[0]] = poll_responses[row[0]] + 1
                except: poll_responses[row[0]] = 1
            records = await select_sql("""SELECT PollQuestion, Options FROM Polls WHERE Id=%s;""",(parsed_string,))
            if not records:
                await reply_message(message, "That is not a valid poll ID!")
                return
            for row in records:
                question = row[0]
                poll_options = row[1].split('|')
                
            response = "**Votes for poll " + question + "**\n\n"
            counter = 0
            for x in poll_options:
                try:
                    response = response + str(poll_responses[poll_options.index(x)]) + " - " + str(x) + "\n"    
                except:
                    pass
            await reply_message(message, response)
                
                
            
        elif command == 'closepoll':
            if not parsed_string:
                await reply_message(message, "You did not provide a poll ID!")
                return
            records = await select_sql("""SELECT OptionVoted FROM Votes WHERE PollId=%s;""",(parsed_string,))
            poll_responses = {}
            for row in records:
                try: poll_responses[int(row[0])] = poll_responses[int(row[0])] + 1
                except: poll_responses[int(row[0])] = 1
            records = await select_sql("""SELECT PollQuestion, Options FROM Polls WHERE Id=%s;""",(parsed_string,))
            if not records:
                await reply_message(message, "That is not a valid poll ID!")
                return
            for row in records:
                question = row[0]
                poll_options = row[1].split('|')
                
            response = "**Votes for poll " + question + "**\n\n"
            counter = 0
            for x in poll_options:
                try:
                    response = response + str(poll_responses[poll_options.index(x)]) + " - " + str(x) + "\n"
                except:
                    pass
            await reply_message(message, response)
            result = await commit_sql("""DELETE FROM Polls WHERE Id=%s;""",(parsed_string,))
            result = await commit_sql("""DELETE FROM Votes WHERE PollId=%s;""",(parsed_string,))
            await reply_message(message, "Poll closed!")
        elif command == 'listpolls':
            records = await select_sql("""SELECT Id,PollQuestion, UserId FROM Polls WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await reply_message(message, "No polls currently open!")
                return
            polls = "**List of Current Polls**\n\n"    
            for row in records:
                user = message.guild.get_member(int(row[2]))
                polls = polls + str(row[0]) + " - " + row[1] + " by user " + user.display_name + "\n"
            await reply_message(message, polls)    
        else:
            pass
    try:
        poll_creator[message.guild.id]
        server_settings[message.guild.id]["PollChannel"]
    except:
        return
    if message.channel.id == server_settings[message.guild.id]["PollChannel"] and message.author.id in list(poll_creator[message.guild.id].keys()):
        username = message.author.display_name
        server_name = message.guild.name
        # user_id = message.author.id
        # server_id = message.guild.id      
        if message.content == 'cancel':
            await log_message("Cancel called.")
            del poll_creator[message.guild.id][message.author.id]
            result = await commit_sql("""DELETE FROM Polls WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            await reply_message(message, "Poll has been canceled.")
            return
        if message.content == 'done':
            await log_message("Done called.")
            poll_post = "*Poll for user " + message.author.display_name + "*\n**QUESTION: " + poll_creator[message.guild.id][message.author.id]["Question"] + "**\n\n*Please respond by reacting with the emojis below.*\n\n"
            print("Poll post: " + poll_post)
            emoji_counter = 0
            for option in poll_creator[message.guild.id][message.author.id]["Options"]:
                print("Option: " + option)
                poll_post = poll_post + str(poll_creator[message.guild.id][message.author.id]["Emojis"][emoji_counter]) + " - " + option + "\n"
                print("Poll post: " + poll_post)
                emoji_counter = emoji_counter + 1
                print("Emoji counter: " + str(emoji_counter))
            options_list = "|".join(poll_creator[message.guild.id][message.author.id]["Options"])
            emoji_list = "|".join(poll_creator[message.guild.id][message.author.id]["Emojis"])
            poll_post = poll_post + "\n <@&" + str(server_settings[message.guild.id]["PollRole"]) + ">"
            print("Emoji list: " + str(emoji_list))
            poll_message = await message.channel.send(">>> " + poll_post)
            print("Poll message: " + str(poll_message))
            result = await commit_sql("""UPDATE Polls SET Options=%s,Emojis=%s,MessageId=%s WHERE ServerId=%s AND UserId=%s;""",(options_list,emoji_list,str(poll_message.id),str(message.guild.id),str(message.author.id)))
            print("Result: " + str(result))
            for emoji in poll_creator[message.guild.id][message.author.id]["Emojis"]:
                await poll_message.add_reaction(emoji)
            print("Message objects: " + str(poll_creator[message.guild.id][message.author.id]["MessageObjects"]))
            await message.channel.delete_messages(poll_creator[message.guild.id][message.author.id]["MessageObjects"])
            await message.delete()
            
            active_polls[poll_message.id] = {} 
            active_polls[poll_message.id]["EmojiDict"] = {}
            for emoji in poll_creator[message.guild.id][message.author.id]["Emojis"]:
                active_polls[poll_message.id]["EmojiDict"][emoji] = poll_creator[message.guild.id][message.author.id]["Emojis"].index(emoji)
            records = await select_sql("""SELECT Id FROM Polls WHERE MessageId=%s;""",(str(poll_message.id),))
            print("Records: " + str(records))
            for row in records:
                active_polls[poll_message.id]["PollId"] = int(row[0])
            active_polls[poll_message.id]["ServerId"] = message.guild.id    
            
            del poll_creator[message.guild.id][message.author.id]
            return
        if message.attachments:
            poll_creator[message.guild.id][message.author.id]["Options"].append(message.attachments[0].url)
        else:
            poll_creator[message.guild.id][message.author.id]["Options"].append(message.content)
        poll_creator[message.guild.id][message.author.id]["MessagesToDelete"].append(message.id)
        if not message.attachments:
            poll_creator[message.guild.id][message.author.id]["MessageObjects"].append(message)
        await log_message("Question added.")
        reply = await message.channel.send(">>> Option *" + message.content + "* added to poll with question **" + poll_creator[message.guild.id][message.author.id]["Question"] + "**. Please react to your own message with the emoji you'd like to use for this option.")
        poll_creator[message.guild.id][message.author.id]["MessageObjects"].append(reply)

            
            
               
                
        
                
client.run'REDACTED'

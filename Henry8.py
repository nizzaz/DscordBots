# https://discord.com/api/oauth2/authorize?client_id=852835935430639618&permissions=117760&scope=bot
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
import json
import decimal
import asyncio

import discordslashcommands as dsc

class NakedObject(object):
    pass
    
manager = None

roles_list = ["King and Queen","Archduke and Archduchess","Grand Duke and Grand Duchess","Duke and Duchess","Crown Prince and Crown Princess","Viceroy and Vicereine","Marquess and Marchioness", "Count and Countess","Viscount and Viscountess","Baron and Baroness","Baronet and Baronetess","Knight and Dame","Esquire and Esquiress","Squire and Squiress","Citizen"]
points_needed = [10000,7500,5000,3000,2000,1400,1000,750,500,300,200,100,50,20,0]

intents = discord.Intents.all()
client = discord.Client(heartbeat_timeout=600,intents=intents)

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='Henry', user='REDACTED', password='REDACTED')    
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
    if sql_query != 'SELECT UsersAllowed, CharName, PictureLink FROM Alts WHERE ServerId=%s AND Shortcut=%s;' and sql_query != 'SELECT Id,CharacterName,Currency,Experience FROM CharacterProfiles WHERE ServerId=%s AND UserId=%s;':
        await log_message("Select SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='Henry', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
        if sql_query != 'SELECT UsersAllowed, CharName, PictureLink FROM Alts WHERE ServerId=%s AND Shortcut=%s;' and sql_query != 'SELECT Id,CharacterName,Currency,Experience FROM CharacterProfiles WHERE ServerId=%s AND UserId=%s;':
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
        connection = mysql.connector.connect(host='localhost', database='Henry', user='REDACTED', password='REDACTED')
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

async def admin_check(userid):
    if (userid != 610335542780887050):
        await log_message(str(userid) + " tried to call an admin message!")
        return False
    else:
        return True

async def slash_commands(command_name, command_desc, options):
    global manager
    print("Command name " + command_name)
    command = dsc.Command(command_name, description=command_desc)
    # try:
        # options[0]['name']
    # except:
    manager.add_global_command(command) 
    return
    # for opt in options:
        # print("Adding option " + opt['name'])
        # option = dsc.Option(opt['name'],opt['desc'], dsc.STRING, True)
        # command.add_option(option) 
        
@client.event
async def on_ready():
    global manager
    await log_message("Logged into Discord!")
    manager = dsc.Manager(client)
    

        
    commands = [{"name": 'createroles', 'desc': 'Create the ranks required for the bot.', 'options': [{}]},
    {"name": 'info', 'desc': 'Bot help.', 'options': [{}]},
    {"name": 'help', 'desc': 'Bot help.', 'options': [{}]},
    {"name": 'myrep', 'desc': 'Check your rank.', 'options': [{}]},
    {"name": 'leaderboard', 'desc': 'Server leaderboard.', 'options': [{}]},
    {"name": 'deleteroles', 'desc': 'Delete the server roles.', 'options': [{}]},
    {"name": 'invite', 'desc': 'Show the bot invite.', 'options': [{}]}
    ]
    for command in commands:
        await slash_commands(command['name'], command['desc'], command['options'])
        await asyncio.sleep(5)    

@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name + "!")
    for member in guild.members:
        result = await commit_sql("""INSERT INTO Ranks (ServerId, UserId, TotalReputation, CurrentRankId) VALUES (%s, %s, 0, '0');""",(str(guild.id),str(member.id)))
        

@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name + "!")
    result = await commit_sql("""DELETE FROM Ranks WHERE ServerId=%s;""",(str(guild.id),))
    

@client.event
async def on_member_join(member):
    await log_message("User " + member.name + " joined guild " + member.guild.name + "!")
    new_role = discord.utils.get(member.guild.roles, name="Citizen")
    await member.add_roles(new_role)
    result = await commit_sql("""INSERT INTO Ranks (ServerId, UserId, TotalReputation, CurrentRankId) VALUES (%s, %s, 0, %s);""",(str(guild.id),str(member.id), str(new_role.id)))
    
@client.event
async def on_member_remove(member):
    await log_message("User " + member.name + " left guild " + member.guild.name + "!")
    result = await commit_sql("""DELETE FROM Ranks WHERE ServerId=%s AND UserId=%s;""",(str(member.guild.id),str(member.id)))

@client.event
async def on_message(message):
    global roles_list
    global points_needed
    global manager
    
    if message.author == client.user:
        return
    if message.author.bot:
        return

    username = message.author.display_name
    server_name = message.guild.name
    user_id = message.author.id
    server_id = message.guild.id            
    if message.content.startswith('h!'):


        command_string = message.content.split(' ')
        command = command_string[0].replace('h!','')
        parsed_string = message.content.replace("h!" + command,"")
        parsed_string = re.sub(r"^ ","",parsed_string)


        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        
        if command == 'createroles':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "You must have manage server permissions to create roles!")
                return
            
            for role in roles_list:
                role_obj = await message.guild.create_role(name=role)
                if role_obj.name == 'Citizen':
                    for user in message.guild.members:
                        result = await commit_sql("""UPDATE Ranks SET CurrentRankId=%s WHERE ServerId=%s AND UserId=%s;""",(str(role_obj.id),str(message.guild.id),str(user.id)))
                        await user.add_roles(role_obj)
            await reply_message(message, "Roles created!")
        elif command == 'invite':
            await reply_message(message, "Invite me: https://discord.com/api/oauth2/authorize?client_id=852835935430639618&permissions=2415921152&scope=bot%20applications.commands")
        elif command == 'updateroles':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "You must have manage server permissions to create roles!")
                return
            role_dict = {}    
            for role in roles_list:
                role_obj = discord.utils.get(message.guild.roles, name=role)
                role_dict[role] = role_obj.id
            for user in message.guild.members:
                records = await select_sql("""SELECT TotalReputation FROM Ranks WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id), str(user.id)))
                for row in records:
                    reputation = int(row[0])
                counter = 0                    
                for rep in points_needed:
                    if reputation >= rep:
                        new_role = discord.utils.get(message.guild.roles,name=roles_list[counter])

                        result = await commit_sql("""UPDATE Ranks SET CurrentRankId=%s WHERE ServerId=%s AND UserId=%s;""",(str(new_role.id),str(message.guild.id),str(user.id)))
                    elif reputation == 0:
                        new_role = discord.utils.get(message.guild.roles,name="Citizen")
                        result = await commit_sql("""UPDATE Ranks SET CurrentRankId=%s WHERE ServerId=%s AND UserId=%s;""",(str(new_role.id),str(message.guild.id),str(user.id)))                        
                    counter+=1
            await reply_message(message, "All users updated.")
                    
        elif command == 'myrep':
            records = await select_sql("""SELECT TotalReputation,CurrentRankId FROM Ranks WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "No record found for you!")
                return
            for row in records:
                reputation = row[0]
                CurrentRankId = int(row[1])
            current_role = message.guild.get_role(CurrentRankId)
            await reply_message(message, "Your current rank is " + current_role.name + " and your current reputation is " + str(reputation) + ".")
        elif command == 'servercount':
            await log_message("servercount called by " + message.author.name)
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await reply_message(message,"Admin command only!")
                return   
            response = "Server count: " + str(len(client.guilds)) 
            await reply_message(message,response)              
        elif command == 'leaderboard':
            records = await select_sql("""SELECT UserId,TotalReputation,CurrentRankId FROM Ranks WHERE ServerId=%s ORDER BY TotalReputation DESC;""",(str(message.guild.id),))
            if not records:
                await reply_message(message, "No one is ranked yet!")
                return
            response = "Server Leaderboard:\n\n"
            for row in records:
                current_user = discord.utils.get(message.guild.members, id=int(row[0]))
                if current_user is None:
                    current_username = "Unknown"
                else:
                    current_username = current_user.name
                try:
                    current_role = discord.utils.get(message.guild.roles, id=int(row[2]))
                    current_rank = current_role.name
                except:
                    current_rank = "unknown"
                response = response + current_username + " - " + str(row[1]) + " - " + current_rank + "\n"
            await reply_message(message, response)
        elif command == 'deleteroles':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "You must have manage server permissions delete roles!")
                return
            
            for role in roles_list:
                role_obj = discord.utils.get(message.guild.roles, name=role)
                await role_obj.delete()
            await reply_message(message, "Roles deleted!")
        elif command == 'info' or command == 'help':
            response = "**Henry the VIII** grants nobility rank for activity on a server based on medieval European ranks of aristocracy.\n\nCOMMANDS:\n\n`h!createroles`: Create the ranks required for the bot (King and Queen, Archduke and Archduchess, Grand Duke and Grand Duchess, Duke and Duchess, Crown Prince and Crown Princess, Viceroy and Vicereine, Marquess and Marchioness,  Count and Countess, Viscount and Viscountess, Baron and Baroness, Baronet and Baronetess, Knight and Dame, Esquire and Esquiress, Squire and Squiress, Citizen).\n`h!myrep`: Check your rank and reputation.\n`h!deleteroles`: Remove the roles created by the bot.\n"
            await reply_message(message, response)
        elif command == 'ranks':
            response = "**RANK SETTINGS**\n\n"
            counter = 0
            for x in roles_list:
                response = response + x + " - " + str(points_needed[counter]) + "\n"
                counter = counter + 1
            await reply_message(message, response)
        elif command == 'getrep':
            records = await select_sql("""SELECT TotalReputation,CurrentRankId FROM Ranks WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.mentions[0].id)))
            if not records:
                await reply_message(message, "No record found for that user!")
                return
            for row in records:
                reputation = row[0]
                CurrentRankId = int(row[1])
            current_role = message.guild.get_role(CurrentRankId)
            await reply_message(message, message.mentions[0].display_name + "'s current rank is " + current_role.name + " and their current reputation is " + str(reputation) + ".")
            
        else:
            pass
    else:
        records = await select_sql("""SELECT TotalReputation,CurrentRankId FROM Ranks WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
        if not records:
            result = await commit_sql("""INSERT INTO Ranks (ServerId,UserId,TotalReputation,CurrentRankId) VALUES (%s,%s,0,%s);""",(str(message.guild.id),str(message.author.id),str(discord.utils.get(message.guild.roles,name="Citizen").id)))
            return
            
        for row in records:
            reputation = int(row[0])
            current_role_id = int(row[1])
        
        reputation = reputation + 1
        counter = 0
        
        for rep in points_needed:
            if reputation >= rep:
                new_role = discord.utils.get(message.guild.roles,name=roles_list[counter])
                if current_role_id == new_role.id:
                    result = await commit_sql("""UPDATE Ranks SET TotalReputation=%s WHERE ServerId=%s AND UserId=%s;""",(str(reputation),str(message.guild.id),str(message.author.id)))
                    return
                current_role = message.guild.get_role(current_role_id)
                try:
                    await message.author.remove_roles(current_role)
                except:
                    pass
                try:    
                    await message.author.add_roles(new_role)
                except:
                    return
                await reply_message(message, "User " + message.author.display_name + " has ranked up to " + new_role.name + "!")
                result = await commit_sql("""UPDATE Ranks SET TotalReputation=%s,CurrentRankId=%s WHERE ServerId=%s AND UserId=%s;""",(str(reputation),str(new_role.id),str(message.guild.id),str(message.author.id)))
                return
            counter = counter + 1
        result = await commit_sql("""UPDATE Ranks SET TotalReputation=%s WHERE ServerId=%s AND UserId=%s;""",(str(reputation),str(message.guild.id),str(message.author.id)))
        
@client.event
async def on_interaction(member, interaction):
    message = NakedObject()
    message.author = member
    message.guild = interaction.guild
    message.content = "h!" + interaction.command.to_dict()['name']
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
    
        
client.run('REDACTED')      

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
import discordslashcommands as dsc
import asyncio
intents = discord.Intents.default()
client = discord.Client(heartbeat_timeout=600,intents=intents)
from slashcommands import SlashCommands

async def admin_check(userid):
    if (userid != 610335542780887050):
        await log_message(str(userid) + " tried to call an admin message!")
        return False
    else:
        return True
    
async def calculate_role(check_date):
    now = datetime.now()
    roles = ["One Day Free","One Week Free","One Month Free","Two Months Free","Three Months Free","Four Months Free","Six Months Free","Nine Months Free","One Year Free","Two Years Free","Three Years Free","Five Years Free","Ten Years Free","Fifteen Years Free","20+ years Free"]
    
    date_to_check = datetime.strptime(check_date, '%Y-%m-%d')
    delta_time = now - date_to_check
    days_delta = delta_time.days
    
    if days_delta >= 1 and days_delta <=6:
        return "One Day Free"
    elif days_delta >= 7 and days_delta <= 29:
        return "One Week Free"
    elif days_delta >= 30 and days_delta <= 59:
        return "One Month Free"
    elif days_delta >= 60 and days_delta <= 89:
        return "Two Months Free"
    elif days_delta >= 90 and days_delta <= 119:
        return "Three Months Free"
    elif days_delta >= 120 and days_delta <= 179:
        return "Four Months Free"
    elif days_delta >= 180 and days_delta <= 269:
        return "Six Months Free"
    elif days_delta >= 270 and days_delta <= 364:
        return "Nine Months Free"
    elif days_delta >= 365 and days_delta <= 729:
        return "One Year Free"
    elif days_delta >= 730 and days_delta <= (365 * 3) - 1:
        return "Two Years Free"
    elif days_delta >= (365 * 3) and days_delta <= (365 * 5) -1:
        return "Three Years Free"
    elif days_delta >= (365 * 5) and days_delta <= (365 * 10) -1:
        return "Five Years Free"
    elif days_delta >= (365 * 10) and days_delta <= (365 * 15) -1:
        return "Ten Years Free"
    elif days_delta >= (365 * 15) and days_delta <= (365 * 20) - 1:
        return "Fifteen Years Free"
    elif days_delta >= 365 * 20:
        return "20+ years Free"
    else:
        return "None"
  
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='SobrietyTracker', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='SobrietyTracker', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='SobrietyTracker', user='REDACTED', password='REDACTED')
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
            
       
async def post_webhook(message, name, response, picture):
    temp_webhook = await message.channel.create_webhook(name='Chara-Tron')
    await temp_webhook.send(content=response, username=name, avatar_url=picture)
    await message.delete()
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
        
@client.event
async def on_ready():
    global slash_commands
    
    
        
    commands = [{"name": 'createroles', 'desc': 'Create server roles for the bot.', 'options': [{}]},
    {"name": 'info', 'desc': 'Bot help.', 'options': [{}]},
    {"name": 'help', 'desc': 'Bot help.', 'options': [{}]},
    {"name": 'deleteroles', 'desc': 'Delete the server roles.', 'options': [{}]},
    {"name": 'trackme', 'desc': 'Track a habit.', 'options': [{'name': 'habit', 'desc': 'Habit you wish to track.'},]},
    {"name": 'freesince', 'desc': 'Set the last date you did your habit.', 'options': [{'name': 'date', 'desc': 'Date in YYYY-MM-DD format.'},{'name': 'habit', 'desc': 'Habit you are updating.'}]},
    {"name": 'checkin', 'desc': 'Check in as free from your habit today.', 'options': [{'name': 'habit', 'desc': 'Habit you are updating.'},]},
    {"name": 'relapse', 'desc': 'Show that you relapsed on your habit today.', 'options': [{'name': 'habit', 'desc': 'Habit you are updating.'},]},
    {"name": 'displaymydata', 'desc': 'Show your current bot data.', 'options': [{},]},
    {"name": 'daysfree', 'desc': 'Show your time free from your habit.', 'options': [{'name': 'habit', 'desc': 'Habit you are displaying.'},]},
    {"name": 'untrackme', 'desc': 'Delete all data for you from the bot.', 'options': [{},]},
    {"name": 'invite', 'desc': 'Show bot invite.', 'options': [{},]}
    ]
    slash_commands = SlashCommands(client)
    for command in commands:
        slash_commands.new_slash_command(name=command["name"], description=command["desc"])
        for option in command["options"]:
            try:
                option["name"]
            except:
                continue
            print(str(option))
            slash_commands.add_command_option(command_name=command["name"], option_name=option["name"], description=option["desc"], required=True)
        slash_commands.add_global_slash_command(command_name=command["name"])
        await asyncio.sleep(5)
        
        
    await log_message("Logged into Discord!")
    
@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name)
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)

@client.event
async def on_message(message):
    invite_url = "https://discord.com/api/oauth2/authorize?client_id=702681888250396743&permissions=2147534848&scope=bot%20applications.commands"
    roles = ["One Day Free","One Week Free","One Month Free","Two Months Free","Three Months Free","Four Months Free","Six Months Free","Nine Months Free","One Year Free","Two Years Free","Three Years Free","Five Years Free","Ten Years Free","Fifteen Years Free","20+ years Free"]
#    roles = ["One Day","One Week","One Month","Two Months","Three Months","Four Months","Six Months","Nine Months","One Year","Two Years","Three Years","Five Years","Ten Years","Fifteen Years","20+ years"]
    
    if message.content.startswith('st!'):

        
        command_string = message.content.split(' ')
        command = command_string[0].replace('st!','')
        parsed_string = message.content.replace("st!" + command + " ","")
        if parsed_string == message.content:
            parsed_string = ""
        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string)

        if command == 'createroles':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "You must have manage server permissions to create roles!")
                return
            for role in roles:
                await message.guild.create_role(name=role)
            await reply_message(message, "Roles created!")
        elif command == 'deleteroles':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "You must have manage server permissions to delete roles!")
                return
            for role_name in roles:
                role = discord.utils.get(message.guild.roles, name=role_name)
                await role.delete()
            await reply_message(message, "Deleted roles from server.")
            
        elif command == 'trackme':
            if not parsed_string:
                await reply_message(message, "You didn't specify a habit to track!")
                return
                
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')
            result = await commit_sql("""INSERT INTO ServerSettings (ServerId, UserId, Habit, DateStarted) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id), parsed_string, formatted_date))
            if result:
                await reply_message(message, "Created new entry for user " + message.author.display_name + " for habit " + parsed_string + "!")
            else:
                await reply_message(message, "Database error!")
        elif command == 'sethabit':
            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record!")
                return            
            if not parsed_string:
                await reply_message(message, "You didn't set a habit!")
                return
            result = await commit_sql("""UPDATE ServerSettings SET Habit=%s WHERE ServerId=%s AND UserId=%s;""",(parsed_string, str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "Set your habit to " + parsed_string + ".")
            else:
                await reply_message("Database error!")
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await reply_message(message,"Admin command only!")
                return   
            await reply_message(message, "Server count: " + str(len(client.guilds)))                 
        elif command == 'checkin':
            if not parsed_string:
                await reply_message(message, "You didn't specify a habit to check in with!")
                return
                
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')
            records = await select_sql("""SELECT DateStarted,IFNULL(FreeSince,'No data'),IFNULL(LastRelapse,'No data'),IFNULL(LastCheckIn,'No data') FROM ServerSettings WHERE ServerId=%s AND UserId=%s AND Habit=%s;""",(str(message.guild.id),str(message.author.id), parsed_string))
            if not records:
                await reply_message(message, "You don't have a record for that habit!")
                return
            for row in records:
                if row[2] == 'No data':
                    free_since = str(row[1])
                  
                else:
                    result = await commit_sql("""UPDATE ServerSettings SET FreeSince=%s WHERE ServerId=%s AND UserId=%s AND Habit=%s;""",(str(formatted_date), str(message.guild.id),str(message.author.id), parsed_string))
                    result = await commit_sql("""UPDATE ServerSettings SET LastRelapse=NULL WHERE ServerId=%s AND UserId=%s AND Habit=%s;""", (str(message.guild.id),str(message.author.id), parsed_string))
                    await reply_message(message, "Updated your free since date to today.")
                    
            try:
                for role_name in roles:
                    role = discord.utils.get(message.guild.roles, name=role_name)
                    for user_role in message.author.roles:
                        if user_role == role:
                            try:
                                await message.author.remove_roles(role)            
                            except:
                                pass
                role = await calculate_role(free_since)
                if role != 'None':
                
                    role_obj = discord.utils.get(message.guild.roles, name=role)
                    try:
                        await message.author.add_roles(role_obj)
                        await reply_message(message, "Set your role to " + role + ".")
                    except:
                        pass
                    
                result = await commit_sql("""UPDATE ServerSettings SET LastCheckin=%s WHERE ServerId=%s AND UserId=%s AND Habit=%s;""",(formatted_date, str(message.guild.id),str(message.author.id), parsed_string))
                if result:
                    await reply_message(message, "Checked you in as free for today.")
                else:
                    await reply_message("Database error!")
            except: 
                await reply_message(message, "Checked you in as free for today.")
        elif command == 'relapse':
            if not parsed_string:
                await reply_message(message, "You didn't specify a habit to show a relapse on!")
                return
                
            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s AND Habit=%s;""",(str(message.guild.id),str(message.author.id), parsed_string))
            if not records:
                await reply_message(message, "You don't have a record for that habit!")
                return        
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')        
            result = await commit_sql("""UPDATE ServerSettings SET LastRelapse=%s WHERE ServerId=%s AND UserId=%s AND Habit=%s;""",(formatted_date, str(message.guild.id),str(message.author.id), parsed_string))
            try:
                for role_name in roles:
                    role = discord.utils.get(message.guild.roles, name=role_name)
                    for user_role in message.author.roles:
                        if user_role == role:
                            try:
                                await message.author.remove_roles(role)
                            except:
                                pass
                            
                if result:
                    await reply_message(message, "Recorded your relapse today.")
                else:
                    await reply_message(message, "Database error!")
            except:
                await reply_message(message, "Recorded your relapse today.")
        elif command == 'daysfree':
            if not parsed_string:
                await reply_message(message, "You didn't specify a habit to check your abstinence from!")
                return
                
            now = datetime.now()
            
            records = await select_sql("""SELECT IFNULL(Habit,'No data'), IFNULL(DateStarted,'No data'), IFNULL(LastRelapse,'No data'), IFNULL(LastCheckin,'No data'), IFNULL(FreeSince,'No data') FROM ServerSettings WHERE ServerId=%s AND UserId=%s AND Habit=%s;""",(str(message.guild.id),str(message.author.id), parsed_string))
            if not records:
                await reply_message(message, "You have no data!")
                return
            for row in records:
                habit = str(row[0])
                date_started = str(row[1])
                last_relapse = str(row[2])
                last_checkin = str(row[3])
                free_since = str(row[4])
            if last_relapse !='No data':
                date_to_check = last_relapse
            elif free_since != 'No data':
                date_to_check = free_since
            elif last_checkin != 'No data':
                date_to_check = last_checkin

            else:
                await reply_message(message, "No dates recorded yet! Please set your data using at least the st!freesince command.")
                return
            date_to_check = datetime.strptime(date_to_check, '%Y-%m-%d')
            delta_time = now - date_to_check
            days_delta = delta_time.days
            await reply_message(message, "You have been free " + str(days_delta) + " days.")
            
        elif command == 'freesince':
            if not parsed_string:
                await reply_message(message, "You didn't specify a habit to set your abstinence from!")
                return    
            date_re = re.compile(r"(?P<date>\d\d\d\d-\d\d-\d\d)")
            m = date_re.search(parsed_string)
            if m:
                the_date = m.group('date')
            else:
                await reply_message(message, "Invalid date!")
                return
            habit = re.sub(the_date, '', parsed_string)
            habit = habit.strip()
            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s AND Habit=%s;""",(str(message.guild.id),str(message.author.id), habit))
            if not records:
                await reply_message(message, "You don't have a record!")
                return        
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')     

            
            result = await commit_sql("""UPDATE ServerSettings SET FreeSince=%s WHERE ServerId=%s AND UserId=%s AND Habit=%s;""",(the_date, str(message.guild.id),str(message.author.id), habit))
            try:
                for role_name in roles:
                    role = discord.utils.get(message.guild.roles, name=role_name)
                    for user_role in message.author.roles:
                        if user_role == role:
                            try:
                                await message.author.remove_roles(role)
                            except:
                                pass
                role = await calculate_role(parsed_string)
                if role != 'None':
                    role_obj = discord.utils.get(message.guild.roles, name=role)
                    try:
                        await message.author.add_roles(role_obj)
                        await reply_message(message, "Set your role to " + role + ".")
                    except:
                        pass
                if result:
                    await reply_message(message, "Set your free since date to " + parsed_string + ".")
                else:
                    await reply_message("Database error!") 
            except:
                await reply_message(message, "Set your free since date to " + parsed_string + ".")
        
        elif command == 'invite':
            await reply_message(message, "Click here to invite SobrietyTracker: " + invite_url)

        elif command == 'serverlist':
            if not await admin_check(message.author.id):
                await reply_message(message, "Nope.")
                return
            response = "**SERVER LIST**\n\n"
            for guild in client.guilds:
                response = response + guild.name + "\n"
            response = response + "Server count: " + str(len(client.guilds))
            await reply_message(message, response)
            
        elif command == 'info' or command == 'help':
            response = "**Sobriety Tracker Discord Bot**\n\nVERSION 2.0: Track multiple habits! This bot will help people on a Discord server track and be accountable for their sobriety. The data will be visible to others on the server when roles are given or commands are used unless it is in a private channel.\n\n*Commands*\n\n`Prefix: st!`\n\n`st!createroles`: Create roles on the server (no color, not grouped separately by default) showing length of sobriety from whichever habit you checked in with last.\n\n`st!deleteroles`: Delete the bot server roles.\n\n`st!trackme habit`: Create an entry for you for a habit.\n\n`st!freesince YYYY-MM-DD habit` Set the last date you did your habit.\n\n`st!checkin habit`: Check in as not doing your habit today.\n\n`st!relapse habit`: Admit that you did your habit today and reset your roles.\n\n`st!displaymydata`: Show your data for this server.\n\n`st!daysfree habit`: Show how many days since your last relapse, checkin, or free since date, whichever is most recent.\n\n`st!untrackme`: Delete your data for this server from the bot.\n\n"
            await reply_message(message, response)
        elif command == 'untrackme':
            result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "Your data has been deleted!")
            else:
                await reply_message(message, "Database error!!")
        elif command == 'displaymydata':
            records = await select_sql("""SELECT IFNULL(Habit,'No data'), IFNULL(DateStarted,'No data'), IFNULL(LastRelapse,'No data'), IFNULL(LastCheckin,'No data'), IFNULL(FreeSince,'No data') FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You have no data!")
                return
            response = "Your data:\n\n"
            for row in records:
                habit = str(row[0])
                date_started = str(row[1])
                last_relapse = str(row[2])
                last_checkin = str(row[3])
                free_since = str(row[4])
                response = response +  "Habit: " + habit + "\nDate tracking started: " + date_started + "\nLast Relapse: " + last_relapse + "\nLast checkin: " + last_checkin + "\nFree since: " + free_since + "\n\n"
            await reply_message(message, response)
        else:
            pass
@client.event
async def on_interaction(member, interaction):
    global slash_commands
    print("called here" + str(interaction))
    slash_commands.convert_to_message(interaction, member, "st!")        
client.run('REDACTED')  

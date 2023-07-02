import discord
import discordslashcommands as dsc
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
import asyncio
from slashcommands import SlashCommands

class NakedObject(object):
    pass

intents = discord.Intents.all()

client = discord.Client(heartbeat_timeout=600,intents=intents)

    
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='TimeTracker', user='REDACTED', password='REDACTED', charset="utf8mb4")    
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
        connection = mysql.connector.connect(host='localhost', database='TimeTracker', user='REDACTED', password='REDACTED', charset="utf8mb4")
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
        connection = mysql.connector.connect(host='localhost', database='CharSheet', user='REDACTED', password='REDACTED', charset="utf8mb4")
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
            
async def direct_message(message, response):
    channel = await message.author.create_dm()
    await log_message("replied to user " + message.author.name + " in DM with " + response)
    try:
        message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
        for chunk in message_chunks:
            await channel.send(">>> " + chunk)
            time.sleep(1)
    except discord.errors.Forbidden:
        await dm_tracker[message.author.id]["commandchannel"].send(">>> You have DMs off. Please reply with //answer <reply> in the server channel.\n" + response)
    
async def send_message(message, response):
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
        
        
async def post_webhook(channel, name, response, picture):
    temp_webhook = await channel.create_webhook(name='Chara-Tron')
    sent_message = await temp_webhook.send(content=response, username=name, avatar_url=picture, wait=True)
    await asyncio.sleep(1)
    await temp_webhook.delete() 
    return sent_message

@client.event
async def on_ready():
    global slash_commands
    
        
    commands = [{"name": 'info', 'desc': 'Bot help.', 'options': [{},]},
    {"name": 'help', 'desc': 'Bot help.', 'options': [{},]},
    {"name": 'logtime','desc': 'Log time for yourself or another user.', 'options': [{'name': 'hours', 'desc': 'Number of hours to log.'},{'name': 'user', 'desc': 'Username to log time for.'}]},
    {"name": 'onduty', 'desc': 'Mark yourself as on duty.', 'options': [{},]},
    {"name": 'offduty', 'desc': 'Mark yourself as off duty.', 'options': [{},]},
    {"name": 'report', 'desc': 'Show the current server time report.', 'options': [{},]},
    {"name": 'clearweek', 'desc': 'Add the current week to the cumulative total and zero out the current week.', 'options': [{},]},
    {"name": 'removeofficer', 'desc': 'Remove the specified user ID from all time logs.', 'options': [{'name': 'id', 'desc': 'User ID.'},]},
    {"name": 'dutyofficer', 'desc': 'Show the users on duty.', 'options': [{},]},
    {"name": 'invite', 'desc': 'Invite the bot.', 'options': [{},]}
    ]

    slash_commands = SlashCommands(client)
    for command in commands:
        slash_commands.new_slash_command(name=command["name"].lower(), description=command["desc"])
        for option in command["options"]:
            try:
                option["name"]
            except:
                continue
            print(str(option))
            if option["name"] == 'user':
                slash_commands.add_user_command_option(command_name=command["name"].lower(), option_name=option["name"].lower(), description=option["desc"], required=False)
            else:
                slash_commands.add_command_option(command_name=command["name"].lower(), option_name=option["name"].lower(), description=option["desc"], required=True)
        slash_commands.add_guild_slash_command(620826239107727360,command_name=command["name"].lower())    
        await asyncio.sleep(5)

@client.event
async def on_guild_join(guild):
    pass
    

@client.event
async def on_guild_remove(guild):
    if not guild.name:
        return
    await log_message("Left guild " + guild.name)
    
    
@client.event
async def on_message(message):
    global command_handler
    if message.author == client.user:
        return
    if message.content.startswith('-'):
        
        command_string = message.content.split(' ')
        command = command_string[0].replace('-','')
        parsed_string = message.content.replace("-" + command + " ","").strip()
        if parsed_string == "-" + command:
            parsed_string = None
        print(parsed_string)
        if command == 'info' or command == 'help':
            embed = discord.Embed(title="Time Tracker Bot Help",description="Time Tracker is a bot for logging on duty time as an officer, rounded up to the next 15 minutes.")
            embed.add_field(name="/onduty",value="Start the timer for on-duty time.", inline=False)
            embed.add_field(name="/offduty", value="End the timer and add the total time to your weekly time.", inline=False)
            embed.add_field(name="/dutyofficer",value="Show which officers are currently on duty.", inline=False)
            embed.add_field(name="/logtime HOURS (user:) - optional",value="Add the number of hours to the user's current total.", inline=False)
            embed.add_field(name="/report",value="Show a report of all users and their current logged hours for the week and total logged hours.", inline=False)
            embed.add_field(name="/clearweek",value="Clear the logged hours for the week for all users and add their weekly totals to their cumulative totals. You must have administrator rights to run this command.", inline=False)
            embed.add_field(name="/removeofficer USER_ID",value="Remove an officer's log from the database. Only administrators may run this command.", inline=False)
            embed.add_field(name="/invite",value="Show the invite link for the bot.", inline=False)
            
            embed.add_field(name="Additional information",value="- The bot will not update the cumulative total for logged time until the /clearweek command is run. This will add the weekly time for each user to their cumulative total and reset their weekly totals to zero.", inline=False)
            await message.channel.send(embed=embed)
            
        elif command == 'onduty':
            records = await select_sql("""SELECT OnDutyTime FROM Timer WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if records:
                await send_message(message, "You are already on duty!")
                return
            result = await commit_sql("""INSERT INTO Timer (ServerId, UserId, OnDutyTime) VALUES (%s, %s, %s);""",(str(message.guild.id),str(message.author.id),str(datetime.now())))
            if result:
                await send_message(message, "Logged you in as on duty!")
            else:
                await send_message(message, "Unable to log in as on duty: database error.")
        elif command == 'offduty':
            records = await select_sql("""SELECT OnDutyTime FROM Timer WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id), str(message.author.id)))
            if not records:
                await send_message(message, "You haven't gone on duty!")
                return
            for row in records:
                onduty_time = row[0]
            current_time = datetime.now()
            total_time = current_time - onduty_time
            minutes_logged = int(total_time.total_seconds() / 60)
            if minutes_logged % 15 != 0:
                divisor = int(minutes_logged / 15)
                minutes_logged = (divisor + 1) * 15
            records = await select_sql("""SELECT WeeklyTime, TimeInMinutes FROM TimeLog WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                result = await commit_sql("""INSERT INTO TimeLog (ServerId, UserId, WeeklyTime, TimeInMinutes) VALUES (%s, %s, %s, %s);""",(str(message.guild.id), str(message.author.id), str(minutes_logged), str(0)))
                if result:
                    result2 = await commit_sql("""DELETE FROM Timer WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                    if result2:
                        await send_message(message, "Logged " + str(minutes_logged) + " minutes for you.")
                    else:
                        await send_message(message, "Unable to delete the timer log: database error.")
                else:
                    await send_message(message, "Unable to log time! Database error.")
            else:
                for row in records:
                    if row[0] is None:
                        weekly_time = 0
                    else:
                        weekly_time = int(row[0])
                    if row[1] is None:
                        on_duty_time = 0
                    else:
                        on_duty_time = int(row[1])
                new_weekly_time = weekly_time + minutes_logged
                result = await commit_sql("""UPDATE TimeLog SET WeeklyTime=%s WHERE ServerId=%s AND UserId=%s;""",(str(new_weekly_time),str(message.guild.id),str(message.author.id)))
                if result:
                    result2 = await commit_sql("""DELETE FROM Timer WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
                    if result2:
                        await send_message(message, "Logged " + str(minutes_logged) + " minutes for you.")
                    else:
                        await send_message(message, "Unable to delete the timer log: database error.")
                else:
                    await send_message(message, "Unable to log time! Database error.")
                
        elif command == 'logtime':
            if not parsed_string:
                await send_message(message, "You didn't specify a number of hours!")
                return
            if not re.search(r"\d+",message.content):
                await send_message(message, "The hours parameter specified is not a valid number.")
                return
            if message.mentions and not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to adjust time for another user!")
                return
            if message.mentions:
                user_id = message.mentions[0].id
                username = message.mentions[0].username
            else:
                user_id = message.author.id
                username = message.author.name
            minutes = float(parsed_string) * 60
            records = await select_sql("""SELECT WeeklyTime FROM TimeLog WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(user_id)))
            if not records:
                result = await commit_sql("""INSERT INTO TimeLog (ServerId, UserId, WeeklyTime, TimeInMinutes) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(user_id),str(minutes),str(0)))
                if result:
                    await send_message(message, "Logged " + parsed_string + " hours for " + username + ".")
                else:
                    await send_message(message, "Unable to log hours: database error!")
            else:
                for row in records:
                    if row[0] is None:
                        weekly_time = 0
                    else:
                        weekly_time = int(row[0])
                        
                total_time = weekly_time + minutes
                result = await commit_sql("""UPDATE TimeLog SET WeeklyTime=%s WHERE ServerId=%s AND UserId=%s;""",(str(total_time),str(message.guild.id),str(user_id)))
                if result:
                    await send_message(message, "Logged " + parsed_string + " hours for " + username + ".")
                else:
                    await send_message(message, "Unable to log hours: database error!")
                    
            
                
        elif command == 'report':
        
            records = await select_sql("""SELECT WeeklyTime,TimeInMinutes, UserId FROM TimeLog WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No time has been logged on this server yet!")
                return
            response = "**HOURLY TIME REPORT FOR " + message.guild.name + "**\n\n**Username, Current Week Time, Total Time**\n"
            for row in records:
                if row[0] is None:
                    weekly_time = 0
                else:
                    weekly_time = int(row[0]) / 60
                if row[1] is None:
                    total_time = 0
                else:
                    total_time = int(row[1]) / 60
                user = discord.utils.get(message.guild.members, id=int(row[2]))
                if not user:
                    username=str(row[2])
                else:
                    username = user.name
                response = response + username + ", " + str(weekly_time) + ", " + str(total_time) + "\n"
            await send_message(message, response)
            
        elif command == 'clearweek':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to run this command!")
                return            
            records = await select_sql("""SELECT UserId, WeeklyTime, TimeInMinutes FROM TimeLog WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message,"No time has been logged for this server yet!")
                return
            await send_message(message, "Updating time logs, please wait...")
            for row in records:
                user_id = int(row[0])
                if row[1] is None:
                    weekly_time = 0
                else:
                    weekly_time = int(row[1])
                if row[2] is None:
                    total_time = 0
                else:
                    total_time = int(row[2])
                new_total_time = total_time + weekly_time
                result = await commit_sql("""UPDATE TimeLog SET TimeInMinutes=%s, WeeklyTime=0 WHERE ServerId=%s AND UserId=%s;""",(str(new_total_time),str(message.guild.id),str(row[0])))
                if result:
                    pass
                else:
                    await send_message(message, "Unable to update user ID " + str(row[0]) + "!")
            await send_message(message, "All time logs updated and weekly totals set to zero.")
        elif command == 'removeofficer':
            if not message.author.guild_permissions.manage_guild:
                await send_message(message, "You must have manage server permissions to run this command!")
                return
            if not parsed_string:
                await send_message(message, "You did not specify a user ID!")
                return
            if not re.search(r"\d+",message.content):
                await send_message(message, "That is not a valid user ID.")
                return
            records = await select_sql("""SELECT Id FROM TimeLog WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(parsed_string)))
            if not records:
                await send_message(message, "That user ID was not found in the database.")
                return
            for row in records:
                data_id = row[0]
            result = await commit_sql("""DELETE FROM TimeLog WHERE Id=%s;""",(str(data_id),))
            if result:
                await send_message(message, "User ID has been deleted from the time log.")
            else:
                await send_message(message, "Unable to delete user ID: database error!")
        elif command == 'dutyofficer':
            records = await select_sql("""SELECT UserId FROM Timer WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No one is currently on duty!")
                return
            response = "**ON DUTY OFFICERS**\n\n"
            for row in records:
                user = discord.utils.get(message.guild.members, id=int(row[0]))
                response = response + user.display_name + "\n"
            await send_message(message, response)
        elif command == 'invite':
            await send_message(message, "Invite the bot here: https://discord.com/api/oauth2/authorize?client_id=1018521182619844639&permissions=2147534848&scope=bot%20applications.commands")
            
@client.event
async def on_interaction(member, interaction):
    global command_handler
    global slash_commands
    print("called here" + str(interaction))
    slash_commands.convert_to_message(interaction, member, "-") 

client.run'REDACTED'
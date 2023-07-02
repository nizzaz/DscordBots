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

intents = discord.Intents.all()
client = discord.Client(heartbeat_timeout=600,intents=intents)

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
        connection = mysql.connector.connect(host='localhost', database='NoContact', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='NoContact', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='NoContact', user='REDACTED', password='REDACTED')
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
    await log_message("Logged into Discord!")
    
@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name)
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)

@client.event
async def on_message(message):
    invite_url = "https://discordapp.com/api/oauth2/authorize?client_id=879513730482847795&permissions=268520512&scope=bot"
    roles = ["One Day Free","One Week Free","One Month Free","Two Months Free","Three Months Free","Four Months Free","Six Months Free","Nine Months Free","One Year Free","Two Years Free","Three Years Free","Five Years Free","Ten Years Free","Fifteen Years Free","20+ years Free"]
#    roles = ["One Day","One Week","One Month","Two Months","Three Months","Four Months","Six Months","Nine Months","One Year","Two Years","Three Years","Five Years","Ten Years","Fifteen Years","20+ years"]
    
    if message.content.startswith('nc!'):

        
        command_string = message.content.split(' ')
        command = command_string[0].replace('nc!','')
        parsed_string = message.content.replace("nc!" + command + " ","")
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
            
        elif command == 'start':
                
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            result = await commit_sql("""INSERT INTO ServerSettings (ServerId, UserId, DateStarted) VALUES (%s, %s, %s);""",(str(message.guild.id),str(message.author.id), formatted_date))
            if result:
                await reply_message(message, "Created new entry for user " + message.author.display_name + "!")
            else:
                await reply_message(message, "Database error!")
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await reply_message(message,"Admin command only!")
                return   
            await reply_message(message, "Server count: " + str(len(client.guilds)))                 

        elif command == 'restart':

            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record!")
                return        
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')        
            result = await commit_sql("""UPDATE ServerSettings SET LastRelapse=%s WHERE ServerId=%s AND UserId=%s;""",(formatted_date, str(message.guild.id),str(message.author.id)))
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
                    await reply_message(message, "Restarted today.")
                else:
                    await reply_message(message, "Database error!")
            except:
                await reply_message(message, "Restarted today.")
        elif command == 'progress':

            now = datetime.now()
            
            records = await select_sql("""SELECT IFNULL(Habit,'No data'), IFNULL(DateStarted,'No data'), IFNULL(LastRelapse,'No data'), IFNULL(LastCheckin,'No data'), IFNULL(FreeSince,'No data') FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id), ))
            if not records:
                await reply_message(message, "You have no data!")
                return
            for row in records:
                ex = str(row[0])
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
                await reply_message(message, "No dates recorded yet! Please set your data using at least the nc!freesince command.")
                return
            date_to_check = datetime.strptime(date_to_check, '%Y-%m-%d %H:%M:%S')
            delta_time = now - date_to_check
            
            days_delta = delta_time.days
            clocktime = str(delta_time)
            print(clocktime)
            m = re.search(r"(?P<hours>\d{1,2}):(?P<minutes>\d\d):(?P<seconds>\d\d)",clocktime)
            if m:
                hours = m.group('hours')
                minutes = m.group('minutes')
                seconds = m.group('seconds')
            years = int(days_delta /365)
            months = int(days_delta / 30)
            weeks = int(days_delta / 7)

            
            years_remainder = int(days_delta - years * 365)
            months = int(years_remainder / 30)
            await log_message("Years remainder:  " + str(years_remainder))
            months_remainder = years_remainder - (months * 30)
            await log_message("Months remainder: " + str(months_remainder))
            weeks = int(months_remainder / 7)
            await log_message("Weeks: " + str(weeks))
            days_remainder = int(months_remainder - weeks * 7)
            days = days_remainder
            response = "You have not contacted your ex in **"
            if years > 0:
                response = response + str(years) + " years, "
            if months > 0:
                response = response + str(months) + " months, "
            if weeks > 0:
                response = response + str(weeks) + " weeks, "
            if days > 0:
                response = response + str(days) + " days, "
            if hours != "00":
                response = response + str(hours) + " hours, "
            if minutes != "00":
                response = response + str(minutes) + " minutes, "
            if seconds != "00":
                response = response + str(seconds) + " seconds."
            response = re.sub(r", $","\.",response) + "**"
            
            await reply_message(message, response)
            
        elif command == 'settime':
 
            date_re = re.compile(r"(?P<date>\d\d\d\d-\d\d-\d\d \d\d:\d\d)")
            m = date_re.search(parsed_string)
            if m:
                the_date = m.group('date')
            else:
                await reply_message(message, "Invalid date!")
                return

            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record!")
                return        
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')     

            
            result = await commit_sql("""UPDATE ServerSettings SET FreeSince=%s WHERE ServerId=%s AND UserId=%s;""",(the_date, str(message.guild.id),str(message.author.id)))
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
            await reply_message(message, "Click here to invite NoContact: " + invite_url)

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
            response = "**No Contact Discord Bot**\n\nThis bot will keep track of how long it’s been since you have last contacted your ex.  \n\n**Commands**\n\n`Prefix: nc!`\n\n`nc!start`: Create an entry for you for a ex.\n\n`nc!settime YYYY-MM-DD HH:MM` Set the last date and time you contacted your ex. Please set the time to US Central Time.\n\n`nc!restart`: Restart your progress.\n\n`nc!progress`: Show your progress.\n\n`nc!stop`:Stop your progress.\n\n"
            await reply_message(message, response)
        elif command == 'stop':
            result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "Your data has been deleted!")
            else:
                await reply_message(message, "Database error!!")
        elif command == 'displaymydata':
            records = await select_sql("""SELECT IFNULL(DateStarted,'No data'), IFNULL(LastRelapse,'No data'), IFNULL(LastCheckin,'No data'), IFNULL(FreeSince,'No data') FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You have no data!")
                return
            response = "Your data:\n\n"
            for row in records:
                date_started = str(row[0])
                last_relapse = str(row[1])
                last_checkin = str(row[2])
                free_since = str(row[3])
                response = response +  "Date tracking started: " + date_started + "\nLast Relapse: " + last_relapse + "\nLast checkin: " + last_checkin + "\nFree since: " + free_since + "\n\n"
            await reply_message(message, response)
        else:
            pass
        
client.run('REDACTED')  

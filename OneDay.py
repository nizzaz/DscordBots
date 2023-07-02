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
import asyncio
import aiohttp

intents = discord.Intents.all()
client = discord.Client(heartbeat_timeout=600,intents=intents)

roles = ["30 Days Sober","60 Days Sober","120 Days Sober (4 mos)","150 Days Sober (5 mos)","180 Days Sober (6 mos)","9 Months Sober","One Year Sober","18 Months Sober","Two Years Sober","Three Years Sober","Four Years Sober","Five Years Sober","Six Years Sober","Seven Years Sober","Eight Years Sober","Nine Years Sober","Ten Years Sober","Eleven Years Sober","Twelve Years Sober","Thirteen Years Sober","Fourteen Years Sober","Fifteen Years Sober","Sixteen Years Sober","Seventeen Years Sober","Eighteen Years Sober","Nineteen Years Sober","20 Years Sober","21+ Years","30 Years Sober","31+ Years Sober","40 Years Sober","41+ Years Sober","50 Years Sober","51+ Years Sober"]
for x in range(2,29):
    roles.append(str(x) + " Days Sober")
roles.append("1 Day Sober")
    
announcements = {}

async def announce_timer():
    global announcements
    global roles
    await client.wait_until_ready()
    await log_message("Lanuching timer.")
    while True:
        current_time_obj = datetime.now()
        current_hour = int(current_time_obj.strftime("%H"))
        current_minute = int(current_time_obj.strftime("%M"))
        current_second = int(current_time_obj.strftime("%S"))
        current_month = int(current_time_obj.strftime("%m"))
        current_day = int(current_time_obj.strftime("%d"))
        for server_id in announcements.keys():
            try: announcements[server_id]["Hour"]
            except: announcements[server_id]["Hour"] = 0
            try: announcements[server_id]["Minute"]
            except: announcements[server_id]["Minute"] = 0
            #await log_message(str(current_hour) + ":" + str(current_minute) + ":" + str(current_second))
            
            if announcements[server_id]["Hour"] == current_hour and announcements[server_id]["Minute"] == current_minute and current_second == 0:
                await log_message("Posting announcements...")
                
                channel_obj = client.get_channel(announcements[server_id]["ChannelId"])


                response = "**SOBRIETY ANNIVERSARIES FOR TODAY:**\n\n"
                records = await select_sql("""SELECT UserId FROM Announcements WHERE (OptOut=0 OR OptOut IS NULL) AND ServerId=%s GROUP BY UserId;""",(str(server_id),))
                for row in records:
                    user_id=row[0]
                    announce_records = await select_sql("""SELECT SoberSince FROM ServerSettings WHERE UserId=%s LIMIT 1;""",(str(user_id),))
                    if not records:
                        return
                    for row in announce_records:
                        howlong =""
                        sober_since = str(row[0])
                        await log_message(sober_since)
                        m = re.search(r"(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)",sober_since)
                        if m:
                            month = m.group('month')
                            day = m.group('day')
                            await log_message(month)
                            await log_message(day)
                        else:
                            
                            await log_message("No match!")
                            continue
                            
                        time_sober,days_clean = await calculate_role(sober_since)
                        await log_message("Time sober: " + str(time_sober) + " Days clean: " + str(days_clean))
                        user = discord.utils.get(channel_obj.guild.members, id=int(user_id))
                        if not user:
                            continue
                        announce_it = True
                        for role in user.roles:
                            await log_message("Time sober: " + time_sober + " Role name: " + role.name)
 
                            if time_sober == role.name:
                                announce_it = False
                        
                        for role in user.roles:    
                            if re.search(r"\+ Years",role.name) and int(month) == int(current_month) and int(day) == current_day:
                                announce_it = True
                                await log_message("Announcing " + user.name + " because " + str(current_month) + " = " + str(month) + " and " +  str(current_day) + " = " + str(day) + " and role is " + role.name)
                                now = datetime.now()
                                date_to_check = datetime.strptime(sober_since, '%Y-%m-%d')
                                delta_time = now - date_to_check
                                days_delta = delta_time.days + int(await leap_year_check(re.findall(r"\d\d\d\d",str_date)[0]))
                                howlong = await calculate_time(days_delta)  
                            if time_sober != role.name and role.name in roles:
                                try:
                                    await user.remove_roles(role)
                                except:
                                    pass
                                server_obj = client.get_guild(server_id)
                                new_role = discord.utils.get(server_obj.roles, name=time_sober)
                                try:
                                    await user.add_roles(new_role)
                                except:
                                    pass
                        if announce_it:
                            response = response + "<@" + user_id + "> is "
                            if howlong:
                                response = response + howlong + " sober!\n"
                            else:
                                response = response + time_sober + "!\n"
                response = response + "\nCongratulations to everyone!"  
                try:
                    await channel_obj.send(response)
                except:
                    e = discord.exc_info()[0]
                    await log_message("Exception sending verse: " + str(e))

        await asyncio.sleep(1) 
async def admin_check(userid):
    if (userid != 610335542780887050):
        await log_message(str(userid) + " tried to call an admin message!")
        return False
    else:
        return True
 
async def leap_year_check(year_to_check):
    current_year = int(datetime.now().strftime('%Y'))
    leap_years = 0
    for year in range(int(year_to_check),current_year):
        if year % 4 == 0 and year % 100 != 0:
            leap_years = leap_years + 1

        elif year % 400 ==0:
            leap_years = leap_years + 1
    return leap_years
    
async def calculate_role(check_date):
    global roles
    now = datetime.now()

    
    date_to_check = datetime.strptime(check_date, '%Y-%m-%d')
    delta_time = now - date_to_check
    days_delta = delta_time.days
    if days_delta < 1:
        return "Working on 24 Hours",0
    elif days_delta == 1:
        return "1 Day Sober",1
    elif days_delta <= 30 and days_delta > 1:
        return str(days_delta) + " Days Sober", days_delta
    elif days_delta >= 31 and days_delta <=59:
        return "30 Days Sober",days_delta
    elif days_delta >= 60 and days_delta <= 119:
        return "60 Days Sober",days_delta
    elif days_delta >= 120 and days_delta <= 149:
        return "120 Days Sober (4 mos)",days_delta
    elif days_delta >= 150 and days_delta <= 179:
        return "150 Days Sober (5 mos)",days_delta
    elif days_delta >= 180 and days_delta <= 269:
        return "180 Days Sober (6 mos)",days_delta
    elif days_delta >= 270 and days_delta <= 364:
        return "9 Months Sober",days_delta
    elif days_delta >= 365 and days_delta <= (18 * 30) - 1:
        return "One Year Sober",days_delta
    elif days_delta >= 18*30 and days_delta <= (365 * 2) -1:
        return "18 Months Sober",days_delta
    elif days_delta >= (365 * 2) and days_delta <= (365 * 3) -1:
        return "Two Years Sober",days_delta        
    elif days_delta >= (365 * 3) and days_delta <= (365 * 4) -1:
        return "Three Years Sober",days_delta
    elif days_delta >= (365 * 4) and days_delta <= (365 * 5) -1:
        return "Four Years Sober",days_delta        
    elif days_delta >= (365 * 5) and days_delta <= (365 * 6) -1:
        return "Five Years Sober",days_delta
    elif days_delta >= (365 * 6) and days_delta <= (365 * 7) -1:
        return "Six Years Sober",days_delta 
    elif days_delta >= (365 * 7) and days_delta <= (365 * 8) -1:
        return "Seven Years Sober",days_delta        
    elif days_delta >= (365 * 8) and days_delta <= (365 * 9) -1:
        return "Eight Years Sober",days_delta 
    elif days_delta >= (365 * 9) and days_delta <= (365 * 10) -1:
        return "Nine Years Sober",days_delta        
    elif days_delta >= (365 * 10) and days_delta <= (365 * 11) -1:
        return "Ten Years Sober",days_delta
    elif days_delta >= (365 * 11) and days_delta <= (365 * 12) -1:
        return "Eleven Years Sober",days_delta
    elif days_delta >= (365 * 12) and days_delta <= (365 * 13) -1:
        return "Twelve Years Sober",days_delta    
    elif days_delta >= (365 * 13) and days_delta <= (365 * 14) -1:
        return "Thirteen Years Sober",days_delta 
    elif days_delta >= (365 * 14) and days_delta <= (365 * 15) -1:
        return "Fourteen Years Sober",days_delta        
    elif days_delta >= (365 * 15) and days_delta <= (365 * 16) - 1:
        return "Fifteen Years Sober",days_delta
    elif days_delta >= (365 * 16) and days_delta <= (365 * 17) -1:
        return "Sixteen Years Sober",days_delta   
    elif days_delta >= (365 * 17) and days_delta <= (365 * 18) -1:
        return "Seventeen Years Sober",days_delta 
    elif days_delta >= (365 * 18) and days_delta <= (365 * 19) -1:
        return "Eighteen Years Sober",days_delta       
    elif days_delta >= (365 * 19) and days_delta <= (365 * 20) -1:
        return "Nineteen Years Sober",days_delta        
    elif days_delta >= 365 * 20 and days_delta <= (365 * 21) - 1:
        return "20 Years Sober",days_delta
    elif days_delta >= (365 * 21) and days_delta <= (365 * 30) - 1:
        return "21+ Years",days_delta
    elif days_delta >= (365 * 30) and days_delta <= (365 * 31) -1:
        return "30 Years Sober",days_delta
    elif days_delta >= (365 * 31) and days_delta <= (365 * 40) -1:
        return "31+ Years Sober",days_delta    
    elif days_delta >= (365 * 40) and days_delta <= (365 * 41) -1:
        return "40 Years Sober",days_delta
    elif days_delta >= (365 * 41) and days_delta <= (365 * 50) -1:
        return "41+ Years Sober",days_delta   
    elif days_delta >= (365 * 50) and days_delta <= (365 * 51) -1:
        return "50 Years Sober",days_delta
    elif days_delta >= (365 * 51):
        return "51+ Years Sober",days_delta        
    else:
        return "None",0 
async def calculate_time(days_delta):
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
    
    return str(years) + " years, " + str(int(months)) + " months, " + str(weeks) + " weeks, " + str(days) + " days "
            

       
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='OneDay', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='OneDay', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='OneDay', user='REDACTED', password='REDACTED')
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
    global announcements
    for guild in client.guilds:
        announcements[guild.id] = { }
    records = await select_sql("""SELECT ServerId,ChannelId,Hour,Minute FROM Schedule;""")
    for row in records:
        announcements[int(row[0])] = {}
        announcements[int(row[0])]["ChannelId"] = int(row[1])
        announcements[int(row[0])]["Hour"] = int(row[2])
        announcements[int(row[0])]["Minute"] = int(row[3])    
    await log_message("Logged into Discord!")
    await client.loop.create_task(announce_timer())     
    
@client.event
async def on_guild_join(guild):
    global announcements
    announcements[guild.id] = {}
    await log_message("Joined guild " + guild.name)
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)

@client.event
async def on_message(message):
    global announcements
    global roles
    invite_url = "https://discord.com/api/oauth2/authorize?client_id=762164923966947348&permissions=268520448&scope=bot"

    good_messages = ["Another day.","But for the Grace of God, there go I.","Congratulations, another day."]

    
    if message.content.startswith('!'):

        
        command_string = message.content.split(' ')
        command = command_string[0].replace('!','')
        if command.startswith('i'):
            command = message.content.replace('!','')
            
        parsed_string = message.content.replace("!" + command + " ","")
        if parsed_string == message.content:
            parsed_string = ""
        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string)
        if command == 'trackme':
            records = await select_sql("""SELECT Id WHERE ServerId=%S AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if records:
                await reply_message(message, "You already have a record. Try !sobersince or !checkin.")
                return
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')
            result = await commit_sql("""INSERT INTO ServerSettings (ServerId, UserId, Habit, DateStarted) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id), 'Sobriety', formatted_date))
            if result:
                await reply_message(message, "Created new entry for user " + message.author.display_name + "!")
            else:
                await reply_message(message, "Database error!")
            result = await commit_sql("""INSERT INTO Announcements (ServerId, UserId, OptOut) VALUES (%s, %s, 0);""",(str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "You have been opted into sobriety anniversary announcements. Type `!noannounce` to opt out.")
            else:
                await reply_message(message, "Database error!")
        elif command == 'addgif':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "You must have manage server permissions to add GIFs!")
                return
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
 #           await reply_message(message, "File saved to " + file_name + "!")
                    with open('/home/REDACTED/BotMaster/onedaygif/' + parsed_string.strip() + "." + re.sub(r".*\.(.*)",r"\1",file_name), 'wb') as file:
                        bytes = await resp.read()
                        
                        file.write(bytes)
            await reply_message(message, "GIF added.")  
        elif command == 'gif':
            if not parsed_string:
                await reply_message(message, "No GIF specified!")
                return
            
            output = subprocess.run(["/home/REDACTED/BotMaster/onedaygif/list.sh"], universal_newlines=True, stdout=subprocess.PIPE)
            reaction_list = output.stdout.split('\n')
            reaction_found = False
            for reaction in reaction_list:
                await log_message("Reaction name: " + reaction + " Looking for: " + re.sub(r"(.*)\..*",r"\1",reaction))
                if re.sub(r"(.*)\..*",r"\1",reaction) == parsed_string.strip():
                    filename = reaction
                    reaction_found = True
            if not reaction_found:
                await reply_message(message, "That GIF wasn't found. Try adding it with `!addgif`.")
                return
            file_path = "/home/REDACTED/BotMaster/onedaygif/" + filename
            await message.channel.send(file=discord.File(file_path))  
        elif command == 'deletegif':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "You must have manage server permissions to delete GIFs!")
                return
            if not parsed_string:
                await reply_message(message, "No name supplied!")
                return
            output = subprocess.run(["/home/REDACTED/BotMaster/onedaygif/list.sh"], universal_newlines=True, stdout=subprocess.PIPE)
            reaction_list = output.stdout.split('\n')
            reaction_found = False
            for reaction in reaction_list:
                await log_message("Reaction name: " + reaction + " Looking for: " + re.sub(r"(.*)\..*",r"\1",reaction))
                if re.sub(r"(.*)\..*",r"\1",reaction) == parsed_string.strip():
                    filename = reaction
                    reaction_found = True
            if not reaction_found:
                await reply_message(message, "That GIF wasn't found.")
                return
            file_path = "/home/REDACTED/BotMaster/onedaygif/"+ filename
            output = subprocess.run(["rm",file_path], universal_newlines=True, stdout=subprocess.PIPE)
            await reply_message(message, "GIF deleted.")              
        elif command == 'listgifs':
            output = subprocess.run(["/home/REDACTED/BotMaster/onedaygif/list.sh"], universal_newlines=True, stdout=subprocess.PIPE)
            reaction_list = output.stdout.split('\n')
            response = "**Custom GIF List**\n\n"
            for reaction in reaction_list:
                response = response + re.sub(r"(.*)\..*",r"\1",reaction) + "\n"
            await reply_message(message, response)            
        elif re.search(r"i desire to stop drinking",command, re.IGNORECASE):
            role = discord.utils.get(message.guild.roles, id=755103493378932766)
            await message.author.add_roles(role)
            await reply_message(message, "You have expressed a desire to stop drinking and have been assigned the Friends role.")
        elif re.search(r"i desire to learn more about the fellowship of AA and also how I might support my friends who may have problems with drinking", command, re.IGNORECASE):
            role = discord.utils.get(message.guild.roles, id=762425891505831997)
            await message.author.add_roles(role)
            await reply_message(message, "You are now welcome to our open AA forum and assigned the role friends (observer/support). Our only request is keep the anonymity of “all of our friends”.  Who you see here, what is said here, stays here.")
        # elif re.search(r"i identify as male",command, re.IGNORECASE):
            # role = discord.utils.get(message.guild.roles, id=738923172983996416)
            # await message.author.add_roles(role)
            # await reply_message(message, "You have identified as male and have been assigned the Male Friends role.")
        # elif re.search(r"i identify as female",command, re.IGNORECASE):
            # role = discord.utils.get(message.guild.roles, id=738923166713380937)
            # await message.author.add_roles(role)
            # await reply_message(message, "You have identified as female and have been assigned the Female Friends role.") 
        elif command == 'calculateallroles':
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')
            records = await select_sql("""SELECT DateStarted,IFNULL(SoberSince,'No data'),IFNULL(LastRelapse,'No data'),IFNULL(LastCheckIn,'No data'),UserId FROM ServerSettings WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await reply_message(message, "No user defined!")
                return
            for row in records:
                current_user = discord.utils.get(message.guild.members, id=int(row[4]))
                
                if row[2] == 'No data':
                    free_since = str(row[1])
                     
                for old_role in message.guild.roles:
                    
                    for user_role in current_user.roles:
                        if re.search(r"Sober",user_role.name):
                            await current_user.remove_roles(user_role)
                            await reply_message(message, user_role.name + " removed from user " + current_user.name)

                role_name,day_delta = await calculate_role(free_since)

                last_checkin = row[3]
                last_relapse = row[2]
                role_obj = discord.utils.get(message.guild.roles, name=role_name)
                if day_delta >= 90:
                    new_role = discord.utils.get(message.guild.roles, id=738591991385817178)
                    has_role = False
                    for current_role in current_user.roles:
                        if current_role == new_role:
                            has_role = True
                    if not has_role:
                        await current_user.add_roles(new_role)
                        await reply_message(message, current_user.name + " granted the Greeter role!")
                elif day_delta >= 365:
                    role_list = current_user.roles
                    new_role = discord.utils.get(message.guild.roles, id=762353879278944297)
                    for n_role in role_list:
                        has_role = False
                        for current_role in current_user.roles:
                            if current_role == new_role:
                                has_role = True
                        if not has_role:
                            await current_user.add_roles(new_role)

                    
                    if not has_role:
                        await reply_message(message, current_user.name + " been granted the " + new_role.name + " role!")
                    new_role = discord.utils.get(message.guild.roles, id=738590441716449310)
                    has_role = False
                    for current_role in current_user.roles:
                        if current_role == new_role:
                            has_role = True
                    if not has_role:
                        await current_user.add_roles(new_role)                 

                        await reply_message(message, current_user.name + " has been granted the Trusted Servants role!")


                
                await log_message(role_obj.name)
  

                if last_relapse !='No data':
                    date_to_check = last_relapse
                elif free_since != 'No data':
                    date_to_check = free_since
                elif last_checkin != 'No data':
                    date_to_check = last_checkin
                now = datetime.now()
                date_to_check = datetime.strptime(date_to_check, '%Y-%m-%d')
                delta_time = now - date_to_check
                days_delta = delta_time.days
                howlong = await calculate_time(days_delta)
               
                await current_user.add_roles(role_obj) 
                await reply_message(message, current_user.name + " set to role " + role_obj.name + ".")
                
        elif command == 'checkin':
                
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')
            records = await select_sql("""SELECT DateStarted,IFNULL(SoberSince,'No data'),IFNULL(LastRelapse,'No data'),IFNULL(LastCheckIn,'No data') FROM ServerSettings WHERE ServerId=%s AND UserId=%s AND Habit='Sobriety';""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record for that habit!")
                return
            for row in records:
                if row[2] == 'No data' or row[3] == 'No data':
                    free_since = str(row[1])
                     
                for old_role in message.guild.roles:
                    
                    for user_role in message.author.roles:
                        if re.search(r"Sober",user_role.name):
                            await message.author.remove_roles(user_role)
                            await reply_message(message, user_role.name + " removed from user " + message.author.name)
                
                role_name,day_delta = await calculate_role(free_since)

                last_checkin = row[3]
                last_relapse = row[2]
                role_obj = discord.utils.get(message.guild.roles, name=role_name)
                if day_delta >= 90:
                    new_role = discord.utils.get(message.guild.roles, id=738591991385817178)
                    has_role = False
                    for current_role in message.author.roles:
                        if current_role == new_role:
                            has_role = True
                    if not has_role:
                        await message.author.add_roles(new_role)
                        await reply_message(message, message.author.name + " granted the Greeter role!")
                elif day_delta >= 365:
                    role_list = message.author.roles
                    new_role = discord.utils.get(message.guild.roles, id=762353879278944297)
                    for n_role in role_list:
                        has_role = False
                        for current_role in message.author.roles:
                            if current_role == new_role:
                                has_role = True
                        if not has_role:
                            await message.author.add_roles(new_role)

                    
                    if not has_role:
                        await reply_message(message, message.author.name + " been granted the " + new_role.name + " role!")
                    new_role = discord.utils.get(message.guild.roles, id=738590441716449310)
                    has_role = False
                    for current_role in message.author.roles:
                        if current_role == new_role:
                            has_role = True
                    if not has_role:
                        await message.author.add_roles(new_role)                 

                        await reply_message(message, message.author.name + " has been granted the Trusted Servants role!")


                
                await log_message(role_obj.name)
  

                if last_relapse !='No data':
                    date_to_check = last_relapse
                    date_to_check = last_relapse
                elif free_since != 'No data':
                    date_to_check = free_since
                elif last_checkin != 'No data':
                    date_to_check = last_checkin
                now = datetime.now()
                date_to_check = datetime.strptime(date_to_check, '%Y-%m-%d')
                delta_time = now - date_to_check
                days_delta = delta_time.days
                howlong = await calculate_time(days_delta)
               
                await message.author.add_roles(role_obj) 
                await reply_message(message, message.author.name + " set to role " + role_obj.name + ".")
                
            result = await commit_sql("""UPDATE ServerSettings SET LastCheckin=%s WHERE ServerId=%s AND UserId=%s AND Habit='Sobriety';""",(formatted_date, str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "Checked you in as sober for today.\nYou have been sober " + str(howlong) + ".")
                
                output = subprocess.run(["/home/REDACTED/BotMaster/onedaygif/list.sh"], universal_newlines=True, stdout=subprocess.PIPE)
                reaction_list = output.stdout.split('\n')
                file_name = random.choice(reaction_list)

                file_path = "/home/REDACTED/BotMaster/onedaygif/" + file_name
                await message.channel.send(file=discord.File(file_path))                 
            else:
                await reply_message(response,"Database error!")
        elif command == 'setupannouncements':
            if not message.channel_mentions:
                await reply_message(message, "No target channel specified!")
                return
            time_re = re.compile(r"(?P<hour>\d+):(?P<minute>\d+)")
            
            m = time_re.search(message.content)
            if m:
                minute = m.group('minute')
                hour = m.group('hour')
            else:
                await reply_message(message, "No time specified!")
                return
                
            target_channel = message.channel_mentions[0].id
            
            announcements[message.guild.id] = { }
            announcements[message.guild.id]["Hour"] = int(hour)
            announcements[message.guild.id]["Minute"] = int(minute)
            announcements[message.guild.id]["ChannelId"] = int(target_channel)
            records = await select_sql("""SELECT Id FROM Schedule WHERE ServerId=%s;""", (str(message.guild.id),))
            if not records:
                result = await commit_sql("""INSERT INTO Schedule (ServerId,ChannelId,Hour,Minute) VALUES (%s, %s, %s, %s);""", (str(message.guild.id),str(target_channel),str(hour),str(minute)))
                if result:
                    await reply_message(message, "Time for sobriety announcements set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await reply_message(message, "Database error!")
            else:
                result = await commit_sql("""UPDATE Schedule Set ChannelId=%s,Hour=%s,Minute=%s WHERE ServerId=%s;""", (str(target_channel),str(hour),str(minute), str(message.guild.id)))
                if result:
                    await reply_message(message, "Time for sobriety announcements set to channel " + message.channel_mentions[0].name + " at  " + hour + ":" + minute + "!")
                else:
                    await reply_message(message, "Database error!")                        
        elif command == 'relapse':
               
            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s AND Habit='Sobriety';""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record for that habit!")
                return        
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')        
            result = await commit_sql("""UPDATE ServerSettings SET LastRelapse=%s,SoberSince=NULL WHERE ServerId=%s AND UserId=%s AND Habit='Sobriety';""",(formatted_date, str(message.guild.id),str(message.author.id)))
            try:
                for role_name in roles:
                    role = discord.utils.get(message.guild.roles, name=role_name)
                    for user_role in message.author.roles:
                        if user_role == role:
                            try:
                                await message.author.remove_roles(role)
                            except:
                                pass
                try:
                    new_role = discord.utils.get(message.guild.roles, id=738591991385817178)
                    
                    await message.author.remove_roles(new_role)
                except:
                    pass
                try:
                    new_role = discord.utils.get(message.guild.roles, id=738590441716449310)
                    
                    await message.author.remove_roles(new_role)
                except:
                    pass
                try:
                    new_role = discord.utils.get(message.guild.roles, id=738781893260214424)
                    
                    await message.author.remove_roles(new_role)
                except:
                    pass
                try: 

                    new_role = discord.utils.get(message.guild.roles, id=739211115585601597)
                    await message.author.remove_roles(new_role)
                except:
                    pass
                try:
                    new_role = discord.utils.get(message.guild.roles, id=739490596602773537)
                    await message.author.remove_roles(new_role)
                except:
                    pass
                try:
                    new_role = discord.utils.get(message.guild.roles, id=762353879278944297)
                    await message.author.remove_roles(new_role)
                except:
                    pass
                if result:
                    await reply_message(message, "Each day a new beginning.")
                else:
                    await reply_message(message, "Database error!")
            except:
                await reply_message(message, "Each day a new beginning.")
        elif command == 'howlong':
                
            now = datetime.now()
            
            records = await select_sql("""SELECT IFNULL(Habit,'No data'), IFNULL(DateStarted,'No data'), IFNULL(LastRelapse,'No data'), IFNULL(LastCheckin,'No data'), IFNULL(SoberSince,'No data') FROM ServerSettings WHERE ServerId=%s AND UserId=%s AND Habit='Sobriety';""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You have no data!")
                return
            for row in records:
                habit = "Sobriety"
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
                await reply_message(message, "No dates recorded yet! Please set your data using at least the !sobersince command.")
                return
            str_date = date_to_check
            date_to_check = datetime.strptime(date_to_check, '%Y-%m-%d')
            delta_time = now - date_to_check
            days_delta = delta_time.days + int(await leap_year_check(re.findall(r"\d\d\d\d",str_date)[0]))
            response = await calculate_time(days_delta)
            

            await reply_message(message, "You have been sober " + response)
            
        elif command == 'sobersince':
            date_re = re.compile(r"(?P<date>\d\d\d\d-\d\d-\d\d)")
            m = date_re.search(parsed_string)
            if m:
                the_date = m.group('date')
            else:
                await reply_message(message, "Invalid date!")
                return
            habit = re.sub(the_date, '', parsed_string)
            habit = habit.strip()
            records = await select_sql("""SELECT DateStarted FROM ServerSettings WHERE ServerId=%s AND UserId=%s AND Habit='Sobriety';""",(str(message.guild.id),str(message.author.id)))
            if not records:
                await reply_message(message, "You don't have a record!")
                return        
            now = datetime.now()
            formatted_date = now.strftime('%Y-%m-%d')     

            
            result = await commit_sql("""UPDATE ServerSettings SET SoberSince=%s WHERE ServerId=%s AND UserId=%s AND Habit='Sobriety';""",(the_date, str(message.guild.id),str(message.author.id)))
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
                    await reply_message(message, "Set your sober since date to " + parsed_string + ".")
                else:
                    await reply_message("Database error!") 
            except:
                await reply_message(message, "Set your sober since date to " + parsed_string + ".")
            role = discord.utils.get(message.guild.roles, id=755103493378932766)
            await message.author.add_roles(role)
            await reply_message(message, "You have expressed a desire to stop drinking and have been assigned the Friends role.")        
        elif command == 'invite':
            await reply_message(message, "Click here to invite OneDay: " + invite_url)
        elif command == 'createroles':
            for role in roles:
                await message.guild.create_role(name=role)
            await reply_message(message, "Roles created.")
        elif command == 'announce':
            result = await commit_sql("""UPDATE Announcements SET OptOut=0 WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "You have been opted into announcements for sobriety anniversaries.")
            else:
                await reply_message(message, "Database error!")
            
        elif command == 'noannounce':
            result = await commit_sql("""UPDATE Announcements SET OptOut=1 WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "You have been opted out of announcements for sobriety anniversaries.")
            else:
                await reply_message(message, "Database error!")        
        elif command == 'serverlist':
            if not await admin_check(message.author.id):
                await reply_message(message, "Nope.")
                return
            response = "**SERVER LIST**\n\n"
            for guild in client.guilds:
                response = response + guild.name + "\n"
            await reply_message(message, response)
            
        elif command == 'info' or command == 'help':
            response = "**One Day at a Time**\n\nThe data will be visible to others on the server when roles are given or commands are used unless it is in a private channel.\n\n*Commands*\n\n`Prefix: !`\n\n`!i desire to stop drinking`: Express you want to stop drinking and grant the Friends role.\n\n`!i desire to learn more about the fellowship of AA and also how I might support my friends who may have problems with drinking`: Express that you wish to learn more about AA and grant the Friends (observer/support) role.\n\n `!trackme`: Create an entry for you.\n\n`!sobersince YYYY-MM-DD` Set the date you began sobriety.\n\n`!checkin`: Check in as sober today.\n\n`!relapse`: Admit that you did slip and you want to reset your sobriety date.\n\n`!showmychip`: Show your data for this server.\n\n`!howlong`: Show how many days since your last relapse, checkin, or sober since date, whichever is most recent.\n\n`!announce`: Opt into announcements for sobriety anniversaries (default).\n\n`!noannounce`: Opt out of announcements for sobriety anniversaries.\n\n`!setupannouncements #channel HH:MM`: Set the announcement channel and time HH:MM (24 hour format, central time).\n\n`!untrackme`: Delete your data for this server from the bot.\n\n*GIF Commands*\n\n`!addgif gifname`: Add a GIF to the bot. Type the command and then attach the GIF in Discord.\n\n`!gif gifname`: Display an uploaded GIF in the current channel.\n\n`!listgifs`: Show all GIFs defined for the bot.\n`!deletegif gifname`: Delete a GIF from the bot."
            await reply_message(message, response)
        elif command == 'untrackme':
            result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            result = await commit_sql("""DELETE FROM Announcements WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if result:
                await reply_message(message, "Your data has been deleted!")
            else:
                await reply_message(message, "Database error!!")
        elif command == 'showmychip':
            records = await select_sql("""SELECT IFNULL(Habit,'No data'), IFNULL(DateStarted,'No data'), IFNULL(LastRelapse,'No data'), IFNULL(LastCheckin,'No data'), IFNULL(SoberSince,'No data') FROM ServerSettings WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
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
                
                response = response + "\nDate tracking started: " + date_started + "\nLast Relapse: " + last_relapse + "\nLast checkin: " + last_checkin + "\nSober since: " + free_since + "\n\n"
            embed = discord.Embed(title="Your Chip")
            embed.add_field(name="Sober Since",value=free_since)
            embed.add_field(name="Date tracking started",value=date_started)
            embed.add_field(name="Last Check In",value=last_checkin)
            embed.add_field(name="Last Relapse",value=last_relapse)
            if last_relapse !='No data':
                date_to_check = last_relapse
            elif free_since != 'No data':
                date_to_check = free_since
            elif last_checkin != 'No data':
                date_to_check = last_checkin
            now = datetime.now()
            str_time = date_to_check
            date_to_check = datetime.strptime(date_to_check, '%Y-%m-%d')
            
            delta_time = now - date_to_check
            days_delta = delta_time.days + int(await leap_year_check(re.findall(r"\d\d\d\d",str_time)[0]))
            howlong = await calculate_time(days_delta)
            embed.add_field(name="Sobriety Time",value=howlong)
         
            await message.channel.send(embed=embed)
           # await reply_message(message, response)
        else:
            pass
        final_response = random.choice(good_messages)
        await reply_message(message,final_response)
        
client.run('REDACTED')  

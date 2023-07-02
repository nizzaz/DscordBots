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

intents = discord.Intents.default()
intents.members = True
client = discord.Client(heartbeat_timeout=600,intents=intents)

server_ranks = {} 
server_currency = { }
async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    try:
        connection = mysql.connector.connect(host='localhost', database='Leveler', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='Leveler', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
        await log_message(str(records))
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
        connection = mysql.connector.connect(host='localhost', database='Leveler', user='REDACTED', password='REDACTED')
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
		
@client.event
async def on_ready():
    global server_ranks
    global server_currency
    records = await select_sql("""SELECT ServerId,RankName,RankMessageCount,Id FROM ServerRanks;""")
    for guild in client.guilds:
        records = await select_sql("""SELECT ServerId,RankName,RankMessageCount,Id FROM ServerRanks WHERE ServerId=%s ORDER BY RankMessageCount DESC;""",(str(guild.id),))
        if not records:
            server_ranks[guild.id] = { }
            server_currency[guild.id] = { }
        else:
            for row in records:
                try:
                    server_ranks[int(row[0])]
                except:
                    server_ranks[int(row[0])] = { }
                server_ranks[int(row[0])][row[1]] = { } 
                server_ranks[int(row[0])][row[1]]["MessageCount"] = int(row[2])
                server_ranks[int(row[0])][row[1]]["Id"] = int(row[3])
        
    records = await select_sql("""SELECT ServerId,DefaultGrant,MessageCountGrant,CurrencyName FROM ServerCurrency;""")
    
    for row in records:
        try:
            server_currency[int(row[0])]
        except:
            server_currency[int(row[0])] = {}
        server_currency[int(row[0])]["DefaultGrant"] = int(row[1])
        server_currency[int(row[0])]["MessageCount"] = int(row[2])
        server_currency[int(row[0])]["Name"] = row[3]
    await log_message("Logged into Discord.")
    
@client.event
async def on_guild_join(guild):
    global server_ranks
    global server_currency
    server_ranks[guild.id] = {}
    server_currency[guild.id] = { }
    await log_message("Joined guild " + guild.name)

@client.event
async def on_member_join(member):
    await log_message("user " + member.name + " joined guild " + member.guild.name)
    await commit_sql("""INSERT INTO Ranks (ServerId,UserId,TotalMessageCount,CurrentRank,Currency) VALUES (%s, %s, 0, 0, 0);""",(str(member.guild.id),str(member.id)))
    
@client.event
async def on_message(message):
    global server_ranks
    global server_currency
    
    if message.author.bot:
        return
        
    if message.author == client.user:
        return
        
    if not message.content.startswith('-'):
        user_id = message.author.id
        guild_id = message.guild.id
        
        records = await select_sql("""SELECT TotalMessageCount,CurrentRank,Currency FROM Ranks WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
        if not records:
            await commit_sql("""INSERT INTO Ranks (ServerId,UserId,CurrentRank,TotalMessageCount,Currency) VALUES (%s, %s, 0, 1, 0);""",(str(message.guild.id),str(message.author.id)))
            return
        for row in records:
            message_count = int(row[0])
            current_rank = int(row[1])
            currency = int(row[2])
        
        message_count = message_count + 1
        if re.search(r"!d bump",message.content):
            currency = currency + (server_currency[guild_id]["DefaultGrant"] * 20)
            
        await log_message("Message count for " + message.author.name + " is " + str(message_count))
        for rank in list(server_ranks[message.guild.id].keys()):
            await log_message(rank + " " + str(message_count) + " " + str(server_ranks[message.guild.id][rank]["MessageCount"]))
            if message_count >= server_ranks[message.guild.id][rank]["MessageCount"]:
                if server_ranks[message.guild.id][rank]["Id"] == current_rank:
                    if re.search(r"!d bump",message.content):
                        message_count = message_count + 50                    
                    result = await commit_sql("""UPDATE Ranks SET TotalMessageCount=%s WHERE ServerId=%s AND UserId=%s;""",(str(message_count),str(guild_id),str(user_id)))
                    break
                else:
                    result = await commit_sql("""UPDATE Ranks SET TotalMessageCount=%s,CurrentRank=%s WHERE ServerId=%s AND UserId=%s;""",(str(message_count),str(server_ranks[message.guild.id][rank]["Id"]),str(guild_id),str(user_id)))
                    new_message = await message.channel.send(message.guild.get_member(message.author.id).name + " has ranked up to " + rank + "!")
                    await asyncio.sleep(10)
                    await new_message.delete()
                    break
            else:
                result = await commit_sql("""UPDATE Ranks SET TotalMessageCount=%s WHERE ServerId=%s AND UserId=%s;""",(str(message_count),str(guild_id),str(user_id)))
        if message_count % server_currency[message.guild.id]["MessageCount"] == 0 or re.search(r"!d bump",message.content):
            if re.search(r"!d bump",message.content):
                currency = currency + (server_currency[guild_id]["DefaultGrant"] * 20)
                new_message = await message.channel.send("You've been granted " + str(server_currency[guild_id]["DefaultGrant"] * 20) + " and 50 extra credits for bumping the server! Thanks!")
                await asyncio.sleep(10)
                await new_message.delete()                   
            else:
                currency = currency + server_currency[guild_id]["DefaultGrant"]
            result = await commit_sql("""UPDATE Ranks SET Currency=%s WHERE ServerId=%s AND UserId=%s;""",(str(currency),str(guild_id),str(user_id)))
 
            
            
    if message.content.startswith('-'):
        
     
            
        command_string = message.content.split(' ')
        command = command_string[0].replace('-','')
        parsed_string = message.content.replace("-" + command + " ","")
        username = message.author.name
        server_name = message.guild.name

        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        
        if command == 'info' or command == 'help':
            response = "**Welcome to the Leveler, the custom Discord leveling and currency bot!**\n\nBot prefix: `-`\n\n**COMMANDS**\n`-setcurrencyname name`: Set the name of the currency grant for the server.\n`-createrank MESSAGECOUNT RANK_NAME`: Create a rank of RANK_NAME for achieving MESSAGECOUNT number of messages.\n`-deleterank RANK_NAME`: Delete RANK_NAME from the server. Users of that rank will take the next rank down when messaging.\n`-setcurrencygrant MESSAGECOUNT GRANT`: Grant GRANT amount of your currency every MESSAGECOUNT messages.\n`-stats @USER`: Get the stats for the user mentioned. If no user is mentioned, get your own statistics.\n`-resetrank @USER`: Reset the currency and rank of a user to zero. Useful for server discipline or reverting bot abuse.\n`-givecurrency GRANT @USER`: Give GRANT amount of currency to @USER.\n`-serverranks`: List the current ranks on the server.\n`-servercurrency`: Show the current currency settings.\n`-invite`: Invite the bot.\n`-resetall`: Clear all data for the bot. This does not ask for confirmation!\n\nSupport server: https://discord.gg/eymcqQXaJ5"
            await send_message(message, response)
        elif command == 'setcurrencyname':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "Only a user with manage server permissions may run this command!")
                return
            # name of currency
            if not parsed_string:
                await send_message(message, "You didn't specify a currency name!")
                return
            records = await select_sql("""SELECT CurrencyName FROM ServerCurrency WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                result = await commit_sql("""UPDATE ServerCurrency SET CurrencyName=%s WHERE ServerId=%s;""",(str(parsed_string),str(message.guild.id)))
            else:
                result = await commit_sql("""INSERT INTO ServerCurrency (ServerId,UserId,CurrencyName) VALUES (%s, %s, %s);""",(str(message.guild.id),str(message.author.id),parsed_string))
                
            if result:
                await send_message(message, "Currency name set to **" + parsed_string + "** for this server.")
            else:
                await send_message(message, "Error! Contact bot support in -info!")
            try:
                server_currency[message.guild.id]["Name"] = parsed_string
            except:
                server_currency[message.guild.id] = { }
                server_currency[message.guild.id]["Name"] = parsed_string

        elif command == 'invite':
                await send_message(message,"\n\nInvite: https://discord.com/api/oauth2/authorize?client_id=787552037360893983&permissions=68608&scope=bot")
        elif command == 'deleterank':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "Only a user with manage server permissions may run this command!")
                return        
            if not parsed_string:
                await send_message(message, "You did not specify a rank to delete!")
                return
            records = await select_sql("""SELECT Id FROM ServerRanks WHERE ServerId=%s AND RankName=%s;""",(str(message.guild.id),str(parsed_string)))
            if not records:
                await send_message(message, "That rank doesn't exist!")
                return
            for row in records:
                deletion = row[0]
            result = await commit_sql("""DELETE FROM ServerRanks WHERE Id=%s;""",(str(deletion),))
            if result:
                await send_message(message, "Rank **" + parsed_string + " successfully deleted!")
            else:
                await send_message(message, "Error! Contact bot support in -info!")
            del server_ranks[message.guild.id][parsed_string]
            
        elif command == 'createrank':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "Only a user with manage server permissions may run this command!")
                return        
            rank_re = re.compile(r"(?P<messagecount>\d+) (?P<name>.+)")
            m = rank_re.search(parsed_string)
            
            if not m:
                await send_message(message, "You did not specify any parameters!")
                return
            else:
                message_count = m.group('messagecount')
                rank_name = m.group('name')
                
            if not message_count or not rank_name:
                await send_message(message, "You did not supply enough parameters!")
                return
                
            result = await commit_sql("""INSERT INTO ServerRanks (ServerId,UserId,RankName,RankMessageCount) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id),str(rank_name),str(message_count)))
            if result:
                await send_message(message, "New rank created!")
            else:
                await send_message(message, "Error! Contact bot support in -info!")
            records = await select_sql("""SELECT Id FROM ServerRanks WHERE ServerId=%s AND RankName=%s;""",(str(message.guild.id),str(rannk_name)))
            for row in records:
                new_id = int(row[0])
            try:
                server_ranks[message.guild.id][rank_name] = {}
                server_ranks[message.guild.id][rank_name]["MessageCount"] = int(message_count)
                server_ranks[message.guild.id][rank_name]["Id"] = new_id
            except:
                server_ranks[message.guild.id] = {} 
                server_ranks[message.guild.id][rank_name] = {}
                server_ranks[message.guild.id][rank_name]["MessageCount"] = int(message_count)
                server_ranks[message.guild.id][rank_name]["Id"] = new_id            
        elif command == 'setcurrencygrant':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "Only a user with manage server permissions may run this command!")
                return        
            currency_re = re.compile(r"(?P<messagecount>\d+) (?P<currencygrant>\d+)")
            
            m = currency_re.search(parsed_string)
            if not m:
                await send_message(message, "You didn't specify any parameters to set!")
                return
            else:
                message_count = m.group('messagecount')
                currency_grant = m.group('currencygrant')
            if not message_count or not currency_grant:
                await send_message(message, "You didn't specify a currency grant!")
                return
            records = await select_sql("""SELECT DefaultGrant FROM ServerCurrency WHERE ServerId=%s;""",(str(message.guild.id),))
            if records:
                result = await commit_sql("""UPDATE ServerCurrency SET MessageCountGrant=%s,DefaultGrant=%s WHERE ServerId=%s;""",(str(message_count),str(currency_grant),str(message.guild.id)))
            else:
                result = await commit_sql("""INSERT INTO ServerCurrency (ServerId,UserId,MessageCountGrant,DefaultGrant) VALUES (%s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id),str(message_count),str(currency_grant)))
                
            if result:
                await send_message(message, "Currency message count set to grant **" + str(currency_grant) + "** for every **" + message_count + "** messages for this server.")
            else:
                await send_message(message, "Error! Contact bot support in -info!")
                
            try:
                server_currency[message.guild.id]["DefaultGrant"] = int(currency_grant)
                server_currency[message.guild.id]["MessageCount"] = int(message_count)
            except:
                server_currency[message.guild.id] = { }
                server_currency[message.guild.id]["DefaultGrant"] = int(currency_grant)
                server_currency[message.guild.id]["MessageCount"] = int(message_count)        
                
        elif command == 'resetrank':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "Only a user with manage server permissions may run this command!")
                return        
            if not message.mentions:
                await send_message(message, "You didn't specify a user to reset!")
                return
            user_id = message.mentions[0].id
            result = await commit_sql("""UPDATE Ranks SET TotalMessageCount=0,CurrentRank=0,Currency=0 WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(user_id)))
            if result:
                await send_message(message, "User <@" + str(user_id) + "> has been reset to zero!")
            else:
                await send_message(message, "Error! Contact bot support in -info!")
        
        elif command == 'resetall':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "Only a user with manage server permissions may run this command!")
                return
            result = await commit_sql("""DELETE FROM ServerRanks WHERE ServerId=%s;""",(str(message.guild.id),))
            result = await commit_sql("""DELETE FROM Ranks WHERE ServerId=%s;""",(str(message.guild.id),))
            result = await commit_sql("""DELETE FROM ServerCurrency WHERE ServerId=%s;""",(str(message.guild.id),))
            server_ranks[message.guild.id] = {}
            server_currency[message.guild.id] = {}
            
            await send_message(message, "All data for this server has been deleted!")
            
        elif command == 'givecurrency':
            if not message.author.guild_permissions.manage_guild:
                await reply_message(message, "Only a user with manage server permissions may run this command!")
                return        
            if not message.mentions:
                await send_message(message, "You didn't mention a user to grant " + server_currency[message.guild.id]["Name"]  + " to!")
                return
            if not parsed_string:
                await send_message(message, "You didn't specify any " + server_currency[message.guild.id]["Name"] + " to grant!")
                return
            user_id = message.mentions[0].id
            parsed_string = re.sub(r"<.+>","",parsed_string)
            records = await select_sql("""SELECT Currency FROM Ranks WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(user_id)))
            for row in records:
                currency = int(row[0])
                
            currency = currency + int(parsed_string)
            result = await commit_sql("""UPDATE Ranks SET Currency=%s WHERE ServerId=%s AND UserId=%s;""",(str(currency),str(message.guild.id),str(user_id)))            
            if result:
                await send_message(message, "You granted <@" + str(user_id) + "> " + parsed_string + " "  + server_currency[message.guild.id]["Name"] + "!")
            else:
                await send_message(message, "Error! Contact bot support in -info!")
        elif command == 'stats':
            if not message.mentions:
                user_id = message.author.id
            else:
                user_id = message.mentions[0].id
                
            records = await select_sql("""SELECT TotalMessageCount,CurrentRank,Currency FROM Ranks WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(user_id)))
            if not records:
                await send_message(message, "No stats found!")
                return
                
            for row in records:
                message_count = row[0]
                rank_id = int(row[1])
                currency = row[2]
                
            for rank in list(server_ranks[message.guild.id].keys()):
                if server_ranks[message.guild.id][rank]["Id"] == rank_id:
                    rank_name = rank
            if rank_id == 0:
                rank_name = "No rank"
            try: rank_id
            except: rank_name = "No rank"
            try: currency
            except: currency = 0
            try: currency_name = server_currency[message.guild.id]["Name"]
            except: currency_name = "(No currency name defined)"
            
            embed = discord.Embed(title="Stats for " + message.guild.get_member(user_id).name + ":")
            embed.add_field(name="Message Count:",value=str(message_count))
            embed.add_field(name="Rank:",value=rank_name)
            embed.add_field(name=currency_name + ":",value = currency)
            await message.channel.send(embed=embed)
            
        elif command == 'serverranks':
            records = await select_sql("""SELECT RankName,RankMessageCount FROM ServerRanks WHERE ServerId=%s ORDER BY RankMessageCount DESC;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No server ranks defined yet!")
                return
            response = "**SERVER RANKS**\n\n"
            for row in records:
                response = response + row[0] + " " + str(row[1]) + "\n"
                
            await send_message(message, response)
                
        elif command == 'servercurrency':
            records = await select_sql("""SELECT CurrencyName,DefaultGrant,MessageCountGrant FROM ServerCurrency WHERE ServerId=%s;""",(str(message.guild.id),))
            if not records:
                await send_message(message, "No server currency defined yet!")
                return
            response = "**SERVER CURRENCY SETTINGS**\n\n"
            for row in records:
                response = response + "Currency Name: " + row[0] + "\nCurrency Grant: " + str(row[1]) + "\nCurrency Message Count: " + str(row[2])
                
            await send_message(message, response)
client.run'REDACTED' 		
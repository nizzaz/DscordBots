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

client = discord.Client(heartbeat_timeout=600)

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='TaskManager', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='TaskManager', user='REDACTED', password='REDACTED')
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
        connection = mysql.connector.connect(host='localhost', database='TaskManager', user='REDACTED', password='REDACTED')
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
    await log_message("Logged into Discord!")

@client.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name)
    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)
    
@client.event
async def on_message(message):
    invite_url = "https://discord.com/api/oauth2/authorize?client_id=765017910452027403&permissions=68608&scope=bot"
    if message.author == client.user:
        return
    if message.author.bot:
        return
        
    if message.content.startswith('^'):


        command_string = message.content.split(' ')
        command = command_string[0].replace('^','')
        parsed_string = message.content.replace("^" + command + " ","")
        username = message.author.name
        server_name = message.guild.name

        await log_message("Command " + message.content + " called by " + username + " from " + server_name)
        if (command == 'sayhi'):
            await message.channel.send("Hello there, " + username + "!")
                
        elif (command == 'info' or command == 'help'):
            await send_message(message, "**Welcome to TaskManager, the Discord task list bot!**\n\nCommands:\n\n`^newtask -name <taskname> -priority X -duedate MM/DD/YYYY`: Create a new task. Priority is a number where lower number is higher priority.\n`^mytasks duedate`: Show incomplete tasks by due date.\n`^mytasks priority`: Show incomplete tasks by priority.\n`^completetask X`: Mark task with ID X as complete.\n`^deletetask X`: Delete a task (complete or incomplete) from the bot.\n`^priority X Y`: Change the priority of task ID X to priority Y.\n`^duedate X MM/DD/YYYY`: Change the due date of task ID X.\n`^listallmytasks`: Show all your incomplete tasks and a count of completed tasks.\n`^listcompleted`: Show your completed tasks.\n`^clearallmytasks`: Delete all of your tasks from the bot.\n`^invite`: Show an invite link for the bot.\n")
        elif command == 'newtask':
            m = re.search(r"-name (?P<name>.*?) -priority (?P<priority>\d+) -duedate (?P<month>\d\d)/(?P<day>\d\d)/(?P<year>\d\d\d\d)",parsed_string)
            if m:
                task_name = m.group('name')
                priority = m.group('priority')
                month = m.group('month')
                day = m.group('day')
                year = m.group('year')
            else:
                await send_message(message, "A parameter is missing. Please check the command.")
                return
            due_date = year + "-" + month + "-" + day
            result = await commit_sql("""INSERT INTO ToDo (ServerId, UserId, ToDoItem, Priority, Completed, DueDate) VALUES (%s, %s, %s, %s, %s, %s);""",(str(message.guild.id),str(message.author.id),str(task_name), str(priority), str('0'), str(due_date)))
            if result:
                await send_message(message, "Task " + task_name + " added to your task list.")
            else:
                await send_message(message, "Database error!")
        
        elif command == 'mytasks':
            if parsed_string == 'duedate':
                records = await select_sql("""SELECT Id,ToDoItem, Priority, DueDate FROM ToDo WHERE ServerId=%s AND UserId=%s AND Completed=0 ORDER BY DueDate;""",(str(message.guild.id),str(message.author.id)))
                if not records:
                    await send_message(message, "You don't have any tasks!")
                    return
                response = "Your tasks:\n\n__ID__ __Task__ __Priority__ __Due Date__\n"
                
                for row in records:
                    task_id = str(row[0])
                    task_name = row[1]
                    priority = str(row[2])
                    due_date = str(row[3])
                    response = response + task_id + " - " + task_name + " - " + priority + " - " + due_date + "\n"
                await send_message(message, response)
            elif parsed_string == 'priority':
                records = await select_sql("""SELECT Id,ToDoItem, Priority, DueDate FROM ToDo WHERE ServerId=%s AND UserId=%s AND Completed=0 ORDER BY Priority;""",(str(message.guild.id),str(message.author.id)))
                            
                if not records:
                    await send_message(message, "You don't have any tasks!")
                    return
                response = "Your tasks:\n\n__ID__ __Task__ __Priority__ __Due Date__\n"
                
                for row in records:
                    task_id = str(row[0])
                    task_name = row[1]
                    priority = str(row[2])
                    due_date = str(row[3])
                    response = response + task_id + " - " + task_name + " - " + priority + " - " + due_date + "\n"
                await send_message(message, response)
            else:
                await send_message(message, "You didn't specify sorting by due date or priority!")
                return
        elif command == 'completetask':
            if not parsed_string:
                await send_message(message, "You didn't specify a task ID to complete!")
                return
            records = await select_sql("""SELECT Id,ToDoItem FROM ToDo WHERE ServerId=%s AND UserId=%s AND Id=%s;""",(str(message.guild.id),str(message.author.id),str(parsed_string)))
            if not records:
                await send_message(message, "That's not a valid task ID!")
                return
            for row in records:
                task_name = row[1]
            result = await commit_sql("""UPDATE ToDo SET Completed=1 WHERE Id=%s;""",(str(parsed_string),))
            if result:
                await send_message(message, "The task **" + task_name + "** has been marked complete!")
        elif command == 'deletetask':
            if not parsed_string:
                await send_message(message, "You didn't specify a task ID to delete!")
                return
            records = await select_sql("""SELECT Id,ToDoItem FROM ToDo WHERE ServerId=%s AND UserId=%s AND Id=%s;""",(str(message.guild.id),str(message.author.id),str(parsed_string)))
            if not records:
                await send_message(message, "That's not a valid task ID!")
                return
            for row in records:
                task_name = row[1]
            result = await commit_sql("""DELETE FROM ToDo WHERE Id=%s;""",(str(parsed_string),))
            if result:
                await send_message(message, "The task **" + task_name + "** has been deleted!")
            else:
                await send_message(message, "Database error!")
        elif command == 'priority':
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters!")
                return
            m = re.search(r"(?P<task>\d+) (?P<priority>\d+)",parsed_string)
            if m:
                task_id = m.group('task')
                priority = m.group('priority')
            else:
                await send_message(message, "You didn't specify the correct parameters! Try `^priority <taskID> <newpriority>`")
                return
            records = await select_sql("""SELECT Id, ToDoItem, Priority FROM ToDo WHERE ServerId=%s AND UserId=%s AND Id=%s;""",(str(message.guild.id),str(message.author.id),str(task_id)))
            if not records:
                await send_message(message, "That's not a valid task ID!")
                return
            for row in records:
                task_name = row[1]
                old_priority = str(row[2])
            result = await commit_sql("""UPDATE ToDo SET Priority=%s WHERE Id=%s;""",(str(priority),str(task_id)))
            if result:
                await send_message(message, "Updated task " + task_name + " from priority " + old_priority + " to " + str(priority) + ".")
            else:
                await send_message(message, "Database error!")
                
        elif command == 'duedate':
            if not parsed_string:
                await send_message(message, "You didn't specify any parameters!")
                return
            m = re.search(r"(?P<task>\d+) (?P<month>\d\d)/(?P<day>\d\d)/(?P<year>\d\d\d\d)",parsed_string)
            if m:
                task_id = m.group('task')
                month = m.group('month')
                day = m.group('day')
                year = m.group('year')
                
            else:
                await send_message(message, "You didn't specify the correct parameters! Try `^duedate <taskID> MM/DD/YYYY`")
                return
            due_date = year + "-" + month + "-" + day
            records = await select_sql("""SELECT Id, ToDoItem, DueDate FROM ToDo WHERE ServerId=%s AND UserId=%s AND Id=%s;""",(str(message.guild.id),str(message.author.id),str(task_id)))
            if not records:
                await send_message(message, "That's not a valid task ID!")
                return
            for row in records:
                task_name = row[1]
                old_duedate = str(row[2])
            result = await commit_sql("""UPDATE ToDo SET DueDate=%s WHERE Id=%s;""",(str(due_date),str(task_id)))
            if result:
                await send_message(message, "Updated task " + task_name + " from due date " + old_duedate + " to " + str(due_date) + ".")
            else:
                await send_message(message, "Database error!")
        elif command == 'clearallmytasks':
            result = await commit_sql("""DELETE FROM ToDo WHERE ServerId=%s AND UserId=%s;""",(str(message.guild.id),str(message.author.id)))
            if result:
                await send_message(message, "Your tasks have all been deleted.")
            else:
                await send_message(message, "Database error!")
        elif command == 'invite':
            await send_message(message, "Click here to invite me: https://discord.com/api/oauth2/authorize?client_id=765476382075256842&permissions=68608&scope=bot")
        elif command == 'listallmytasks':
            records = await select_sql("""SELECT Id,ToDoItem, Priority, DueDate FROM ToDo WHERE ServerId=%s AND UserId=%s AND Completed=0;""",(str(message.guild.id),str(message.author.id)))
                        
            if not records:
                await send_message(message, "You don't have any tasks!")
                return
            response = "Your current tasks:\n\n__ID__ __Task__ __Priority__ __Due Date__\n"
            
            for row in records:
                task_id = str(row[0])
                task_name = row[1]
                priority = str(row[2])
                due_date = str(row[3])
                response = response + task_id + " - " + task_name + " - " + priority + " - " + due_date + "\n"
            records = await select_sql("""SELECT COUNT(Id) FROM ToDo WHERE ServerId=%s AND UserId=%s AND Completed=1;""",(str(message.guild.id),str(message.author.id)))
            for row in records:
                completed_count = str(row[0])
            response = response + "\nCompleted task count: " + completed_count
            
            await send_message(message,response)
            
        elif command == 'listcompleted':    
            records = await select_sql("""SELECT Id,ToDoItem, Priority, DueDate FROM ToDo WHERE ServerId=%s AND UserId=%s AND Completed=1;""",(str(message.guild.id),str(message.author.id)))
                        
            if not records:
                await send_message(message, "You don't have any completed tasks!")
                return
            response = "Your completed tasks:\n\n__ID__ __Task__ __Priority__ __Due Date__\n"
            
            for row in records:
                task_id = str(row[0])
                task_name = row[1]
                priority = str(row[2])
                due_date = str(row[3])
                response = response + task_id + " - " + task_name + " - " + priority + " - " + due_date + "\n"                
            await send_message(message, response)

        else:
            pass
            
client.run'REDACTED' 		
		

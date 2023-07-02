import discord
import re
import time
from discord.utils import get
import discord.utils
from datetime import datetime
import decimal
import asyncio

client = discord.Client()

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
@client.event
async def on_ready():
    await log_message("Logged in!")

    
@client.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name)    


@client.event
async def on_message(message):

    if message.author.bot and message.author.id != 787355055333965844:
        return
    if message.author == client.user:
        return
    

    if message.content.startswith('convert'):

            
        command_string = message.content.split(' ')
        
        parsed_string = message.content.replace("convert ","")
        await log_message("Command " + message.content + " called by " + message.author.name + " from server " + message.guild.name + " in channel " + message.channel.name)
        await log_message("Parsed string: " + parsed_string)

        if command_string[1] == 'info':
            response = "usage: convert NUMBER -from UNIT -to UNIT\n\nUnits available: C/F, km/mi, cm/in, kg,lbs\n"
            await message.channel.send(response)
            
            return
        elif command_string[1] == 'invite':
            await message.channel.send("Click here to invite me: https://discord.com/api/oauth2/authorize?client_id=808417334363553913&permissions=3072&scope=bot")
            return
        conversion_re = re.compile(r"(-{0,1}\d+)")
        
        unit_from_re = re.compile("-from (.+) -")
        unit_to_re = re.compile("-to (.+)")
        
        m = conversion_re.search(message.content)
        if m:
            conversion = m.group(1)
        else:
            await message.channel.send("No number to convert specified!")
            return
            
        m = unit_from_re.search(message.content)
        if m:
            from_units = m.group(1)
        else:
            await message.channel.send("No from units specified!")
            return
        
        m = unit_to_re.search(message.content)
        if m:
            to_units = m.group(1)
        else:
            await message.channel.send("No to units specified!")
            return
        
        if from_units == 'F' and to_units == 'C':
            celcius = (float(conversion) - 32) * 5/9
            await message.channel.send(str(conversion) + " degrees Fahrenheit is " + str(celcius) + " Celcius.")
        elif from_units == 'C' and to_units == 'F':
            fahrenheit = (float(conversion) * 9/5) + 32
            await message.channel.send(str(conversion) + " degrees Celcius is " + str(fahrenheit) + " Fahrenheit.")
        elif from_units == 'km' and to_units == 'mi':
            mi = float(conversion) / 1.609
            await message.channel.send(str(conversion) + " kilometers is " + str(mi) + " miles.")
        elif from_units == 'mi' and to_units == 'km':
            km = float(conversion) * 1.609
            await message.channel.send(str(conversion) + " miles is " + str(km) + " kilometers.")
        elif from_units == 'cm' and to_units == 'in':
            inches = float(conversion) / 2.54
            await message.channel.send(str(conversion) + " centimeters is " + str(inches) +  " inches.")
        elif from_units == 'in' and to_units == 'cm':
            cm = float(conversion) * 2.54
            await message.channel.send(str(conversion) + " inches is " + str(cm) + " centimeters.")
        elif from_units == 'kg' and to_units =='lbs':
            lbs = float(conversion) * 2.2
            await message.channel.send(str(conversion) + " kilograms is " + str(lbs) + " pounds.")
        elif from_units == 'lbs' and to_units == 'kg':
            kg = float(conversion) / 2.2
            await message.channel.send(str(conversion) + " pounds is " + str(kg) + " kilograms.")
        elif command == 'servercount':
            if (message.author.id != 610335542780887050 and message.author.id != 787355055333965844):
                await send_message(message,"Admin command only!")
                return   
            await send_message(message, "Server count: " + str(len(client.guilds)))               
        else:
            await message.channel.send("No units specified exist!")
            
       
client.run'REDACTED'
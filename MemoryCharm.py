import discord
from mysql.connector import Error
import time
from discord.utils import get
import discord.utils
from datetime import datetime, timedelta

import string
import asyncio
import aiohttp

already_posted = {}
already_posted["Mongolians"] = False
already_posted["Galdan"] = False
already_posted["Zombies"] = False
client = discord.Client(heartbeat_timeout=600)


async def timer():
    global already_posted
    channel_id = 774456339190513664
    ping_id = 774866136897421332
    await client.wait_until_ready()
    print("Lanuching timer.")
    while True:
        current_time_obj = datetime.now()
        current_hour = int(current_time_obj.strftime("%H"))
        current_minute = int(current_time_obj.strftime("%M"))
        current_second = int(current_time_obj.strftime("%S"))
            
        if (current_hour == 11) and (current_minute == 0) and not already_posted["Mongolians"]:
            response = "Mongolians"
            channel_obj = client.get_channel(channel_id)
            await channel_obj.send(response + " <@&" + str(ping_id) + ">")
            already_posted["Mongolians"] = True

        elif (current_hour == 19) and (current_minute == 0) and not already_posted["Galdan"]:
            response = "Galdan"
            channel_obj = client.get_channel(channel_id)
            await channel_obj.send(response + " <@&" + str(ping_id) + ">")
            already_posted["Galdan"] = True
            
        elif (current_hour == 21) and (current_minute == 0):
            response = "Eliminate the Zombies"
            channel_obj = client.get_channel(channel_id)
            await channel_obj.send(response + " <@&" + str(ping_id) + ">")
            already_posted["Zombies"] = True
        elif (current_hour == 0) and (current_minute == 0):
            already_posted["Mongolians"] = False
            already_posted["Galdan"] = False
            already_posted["Zombies"] = False
        else:
            pass
        # if (current_hour == 20) and (current_minute == 10) and (current_second == 0):
            # response = "Mongolians"
            # channel_obj = client.get_channel(channel_id)
            # await channel_obj.send(response)
        # elif (current_hour == 20) and (current_minute == 11) and (current_second == 0):
            # response = "Galdan"
            # channel_obj = client.get_channel(channel_id)
            # await channel_obj.send(response)
        # elif (current_hour == 20) and (current_minute == 12) and (current_second == 0):
            # response = "Eliminate the Zombies"
            # channel_obj = client.get_channel(channel_id)
            # await channel_obj.send(response)                
        # else:
            # pass            
        time.sleep(60)

@client.event
async def on_ready():
	await client.loop.create_task(timer())
	print("Logged in!")

@client.event
async def on_message(message):
        if message.content == "testping":
            await message.channel.send("Test ping <@&" + str(774866136897421332) + ">")
            
client.run('REDACTED') 
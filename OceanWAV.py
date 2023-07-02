import discord
import re
import mysql.connector
from mysql.connector import Error
import subprocess
import time
import requests
import random
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import discord.utils
from datetime import datetime
import asyncio
import youtube_dl
import ffmpeg
import json

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)
    
async def commit_sql(sql_query, params = None):
    await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
    try:
        connection = mysql.connector.connect(host='localhost', database='OceanWAV', user='REDACTED', password='REDACTED')    
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
        connection = mysql.connector.connect(host='localhost', database='OceanWAV', user='REDACTED', password='REDACTED')
        cursor = connection.cursor()
        result = cursor.execute(sql_query, params)
        records = cursor.fetchall()
        if sql_query != 'SELECT UsersAllowed, CharName, PictureLink FROM Alts WHERE ServerId=%s AND Shortcut=%s;':
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
        connection = mysql.connector.connect(host='localhost', database='OceanWAV', user='REDACTED', password='REDACTED')
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

### Cog class from rappitz

youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


            
            
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        
        self.title = data.get('title')
        self.url = data.get('url')
        self.artist = data.get('artist')
        

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            print("entries: " + str(data))
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def from_playlist(cls, url, *, loop=None, stream = False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        
        return data
            
        
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.urls = {}
        self.queue = {}
        self.queue_counter = {}
        self.playlist_counter = {} 
        self.play_button = '▶'
        self.skip_forward = '⏭'
        self.shuffle = '🔀'
        self.skip_backward = '⏮'
        self.pause = '⏸'
        self.stop_button = '⏹'
        self.eject = '⏹'
        self.vol_up = '🔼'
        self.vol_down = '🔽'
        self.control_panel = {}

    @commands.command()
    async def panel(self, ctx):
        embed = discord.Embed(title="OceanWAV Control Panel")

        
        self.control_panel[ctx.guild.id] = None
        self.control_panel[ctx.guild.id] = await ctx.send(embed=embed)
        await self.control_panel[ctx.guild.id].add_reaction(self.skip_backward)
        await self.control_panel[ctx.guild.id].add_reaction(self.play_button)
        await self.control_panel[ctx.guild.id].add_reaction(self.pause)
        await self.control_panel[ctx.guild.id].add_reaction(self.skip_forward)
        await self.control_panel[ctx.guild.id].add_reaction(self.stop_button)
        await self.control_panel[ctx.guild.id].add_reaction(self.shuffle)
        await self.control_panel[ctx.guild.id].add_reaction(self.vol_up)
        await self.control_panel[ctx.guild.id].add_reaction(self.vol_down)
        await self.control_panel[ctx.guild.id].add_reaction(self.eject)
        
        
    @commands.command()
    async def createplaylist(self, ctx, playlist_name: str):
        result = await commit_sql("""INSERT INTO Playlists (ServerId, UserId, PlaylistName) VALUES (%s, %s, %s);""",(str(ctx.guild.id),str(ctx.author.id),playlist_name))
        if result:
            await ctx.send("Playlist " + playlist_name + " created!")
        else:
            await ctx.send("Database error!")
    @commands.command()
    async def addtoplaylist(self, ctx, playlist_name: str, url: str):
        if not playlist_name:
            await ctx.send("No playlist specified!")
            return
        if not url:
            await ctx.send("No URL specified!")
            return
            
        records = await select_sql("""SELECT Id,URLs FROM Playlists WHERE ServerId=%s AND UserId=%s AND PlaylistName=%s;""",(str(ctx.guild.id),str(ctx.author.id),str(playlist_name)))
        if not records:
            await ctx.send("No playlist found with that name or it's not your playlist!")
        else:
            for row in records:
                id = row[0]
                current_urls = row[1]
            if current_urls is None:
                current_urls = url
            else:
                current_urls = current_urls + "," + url
            result = await commit_sql("""UPDATE Playlists SET URLs=%s WHERE Id=%s;""",(str(current_urls),str(id)))
            if result:
                await ctx.send("URL added to playlist!")
            else:
                await ctx.send("Database error!")
    
    @commands.command()
    async def skipplaylist(self, ctx):
        if not self.urls:
            await ctx.send("No playlist loaded!")
            return
        self.playlist_counter[ctx.guild.id] = self.playlist_counter[ctx.guild.id] + 1

        await ctx.send("Skipping to next song..")
        async with ctx.typing():
            await ctx.voice_client.stop()
            await self.ensure_voice(ctx)
            
            for url in self.urls[self.playlist_counter[ctx.guild.id]:]:
                player = await YTDLSource.from_url(url, loop=self.bot.loop)
                records = await select_sql("""SELECT DefaultVolume FROM ServerSettings WHERE ServerId=%s;""",(str(ctx.author.guild.id),))
                
                for row in records:
                    default_volume = int(row[0])
                
                ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                ctx.voice_client.source.volume = default_volume / 100
                await ctx.send('Now playing: {}'.format(player.title))
                while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                    await asyncio.sleep(3)
                await ctx.voice_client.stop()
                self.playlist_counter[ctx.guild.id] = self.playlist_counter[ctx.guild.id] + 1

    @commands.command()
    async def deleteplaylist(self, ctx, playlist_name):
        if not playlist_name:
            await ctx.send("No playlist specified!")
            return
        result = await commit_sql("""DELETE FROM Playlists WHERE ServerId=%s and PlaylistName=%s;""",(str(ctx.guild.id),str(playlist_name)))
        await ctx.send("Playlist " +  playlist_name + " deleted!")
    
    @commands.command()
    async def invite(self, ctx):
        await ctx.send("Invite me: https://discord.com/api/oauth2/authorize?client_id=728636208930095204&permissions=573959232&scope=bot")
    @commands.command()
    async def showplaylist(self, ctx, playlist_name):
        if not playlist_name:
            await ctx.send("No playlist specified!")
            return
            
        records = await select_sql("""SELECT UserId,URLs FROM Playlists WHERE ServerId=%s AND PlaylistName=%s;""",(str(ctx.guild.id),str(playlist_name)))
        if not records:
            await ctx.send("No playlist found by that name!")
            return
        response = "Playlist " + playlist_name    
        for row in records:
            songs = row[1].split(',')
            user = ctx.guild.get_member(int(row[0]))
        response = response + " by user " + user.display_name + "\n\n"
        for song in songs:
            response = response + song + "\n"
        await ctx.send(response)
        
    @commands.command()
    async def shuffleplaylist(self, ctx, playlist_name: str):
        if not playlist_name:
            await ctx.send("No playlist specified!")
            return
        records = await select_sql("""SELECT URLs FROM Playlists WHERE ServerId=%s AND PlaylistName=%s;""",(str(ctx.guild.id),str(playlist_name)))
        if not records:
            await ctx.send("Playlist not found!")
        else:
            self.urls[ctx.guild.id] = []
            self.playlist_counter[ctx.guild.id] = 0
            for row in records:
                songs = row[0].strip().split(',')
                self.urls[ctx.guild.id] = random.sample(songs,len(songs))
            async with ctx.typing():
                await self.ensure_voice(ctx)
                
                for url in self.urls[ctx.guild.id]:
                    await log_message("URL: " + str(url))
                    player = await YTDLSource.from_url(url, loop=self.bot.loop)
                    records = await select_sql("""SELECT DefaultVolume FROM ServerSettings WHERE ServerId=%s;""",(str(ctx.author.guild.id),))
                    
                    for row in records:
                        default_volume = int(row[0])
                    
                    ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                    ctx.voice_client.source.volume = default_volume / 100
                    await ctx.send('Now playing: {}'.format(player.title))
                    while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                        await asyncio.sleep(3)
                    ctx.voice_client.stop()
                    self.playlist_counter[ctx.guild.id] = self.playlist_counter[ctx.guild.id] + 1                
    @commands.command()
    async def playlist(self, ctx, playlist_name: str):
        if not playlist_name:
            await ctx.send("No playlist specified!")
            return
        records = await select_sql("""SELECT URLs FROM Playlists WHERE ServerId=%s AND PlaylistName=%s;""",(str(ctx.guild.id),str(playlist_name)))
        if not records:
            await ctx.send("Playlist not found!")
        else:
            self.urls[ctx.guild.id] = []
            for row in records:
                self.urls[ctx.guild.id] = row[0].split(',')
            async with ctx.typing():
                await self.ensure_voice(ctx)
                self.playlist_counter[ctx.guild.id] = 0
                for url in self.urls[ctx.guild.id]:
                    player = await YTDLSource.from_url(url, loop=self.bot.loop)
                    records = await select_sql("""SELECT DefaultVolume FROM ServerSettings WHERE ServerId=%s;""",(str(ctx.author.guild.id),))
                    
                    for row in records:
                        default_volume = int(row[0])
                    
                    ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
                    ctx.voice_client.source.volume = default_volume / 100
                    await ctx.send('Now playing: {}'.format(player.title))
                    while ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                        await asyncio.sleep(3)
                    ctx.voice_client.stop()
                    self.playlist_counter[ctx.guild.id] = self.playlist_counter[ctx.guild.id] + 1
                    
        
    @commands.command()
    async def setdefaultvolume(self, ctx, default_volume: str):
        m = re.search(r"(\d+)", default_volume)
        if m:
            default_vol = m.group(1)
            result = await commit_sql("""UPDATE ServerSettings SET DefaultVolume=%s WHERE ServerId=%s;""",(str(default_vol),str(ctx.guild.id)))
            await ctx.send("Volume set to " + str(default_vol) + "% for the server.")
        else:
            await ctx.send("No volume specified!")
    
     
        
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

      

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_id = payload.guild_id
        emoji = str(payload.emoji)
        
        if payload.member == self.bot.user:
            return
        
        guild = await self.bot.fetch_guild(guild_id)
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        ctx = await self.bot.get_context(message)
        
        try: 
            self.control_panel[guild_id]
        except:
            return
        if self.control_panel[guild_id].id == payload.message_id:
            await message.remove_reaction(emoji, payload.member)
            if emoji == self.play_button:
                if ctx.voice_client.is_paused():
                        await ctx.send("Resuming music...")
                        ctx.voice_client.resume()
                        return
                if ctx.voice_client.is_playing():
                    pass
                else:
                    try:
                        
                        self.queue[guild_id]
                        
                        await self.playqueue(self, ctx)
                    except:
                        try:
                            self.urls[guild_id]
                        
                            await self.skipplaylist(self,ctx)
                        except:
                            pass
                        
            elif emoji == self.skip_backward:
                pass
            elif emoji == self.pause:
                if ctx.voice_client.is_playing():
                    await ctx.send("Pausing music...")
                    ctx.voice_client.pause()
                    return
            elif emoji == self.skip_forward:
                try: 
                    self.queue[guild_id]
                    await log_message("Skip forward queue")
                    await self.skipqueue(ctx)
                except:    
                    try:
                        self.urls[guild_id]
                        await log_message("Skip forward playlist")
                        await self.skipplaylist(ctx)
                    except:
                        pass
            elif emoji == self.stop_button:
                await ctx.send("Stopping music...")
                await ctx.voice_client.stop()
            elif emoji == self.vol_up:
                ctx.voice_client.source.volume = ctx.voice_client.source.volume + 0.05
            elif emoji == self.vol_down:
                ctx.voice_client.source.volume = ctx.voice_client.source.volume - 0.05
            elif emoji == self.eject:
                await ctx.send("Disconnecting...")
                await self.stop(ctx)
            elif emoji == self.shuffle:
                pass
            else:
                pass
        

    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                   
                await ctx.author.voice.channel.connect()
                
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            
    async def log_message(log_entry):
        current_time_obj = datetime.now()
        current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
        print(current_time_string + " - " + log_entry, flush = True)
        
    async def commit_sql(sql_query, params = None):
        await log_message("Commit SQL: " + sql_query + "\n" + "Parameters: " + str(params))
        try:
            connection = mysql.connector.connect(host='localhost', database='OceanWAV', user='REDACTED', password='REDACTED')    
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
            connection = mysql.connector.connect(host='localhost', database='OceanWAV', user='REDACTED', password='REDACTED')
            cursor = connection.cursor()
            result = cursor.execute(sql_query, params)
            records = cursor.fetchall()
            if sql_query != 'SELECT UsersAllowed, CharName, PictureLink FROM Alts WHERE ServerId=%s AND Shortcut=%s;':
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
            connection = mysql.connector.connect(host='localhost', database='OceanWAV', user='REDACTED', password='REDACTED')
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

bot = commands.Bot(command_prefix=commands.when_mentioned_or("wav "),
                   description='OceanWAV')
                   
### My code                   

voice_channel = None
voice_client = None
api = 'AIzaSyAHaZq5v4sILFzbtMnVFiQuPUR3Ar6ESL8'

async def log_message(log_entry):
    current_time_obj = datetime.now()
    current_time_string = current_time_obj.strftime("%b %d, %Y-%H:%M:%S.%f")
    print(current_time_string + " - " + log_entry, flush = True)


async def send_message(message, response):
    await log_message("Message sent back to server " + message.guild.name + " channel " + message.channel.name + " in response to user " + message.author.name + "\n\n" + response)
    message_chunks = [response[i:i+1900] for i in range(0, len(response), 1900)]
    for chunk in message_chunks:
        await message.channel.send(">>> " + chunk)
        time.sleep(1)
		
async def post_webhook(channel, name, response, picture):
    temp_webhook = await channel.create_webhook(name='Chara-Tron')
    await temp_webhook.send(content=response, username=name, avatar_url=picture)
    await temp_webhook.delete() 


@bot.event
async def on_ready():
    await log_message("Logged in!")

@bot.event
async def on_guild_join(guild):
    await log_message("Joined guild " + guild.name) 
    result = await commit_sql("""INSERT INTO ServerSettings (ServerId, DefaultVolume, DJRoleId) VALUES (%s,100,%s);""",(str(guild.id),str(guild.roles[0].id)))
    
    
@bot.event
async def on_guild_remove(guild):
    await log_message("Left guild " + guild.name) 
    result = await commit_sql("""DELETE FROM ServerSettings WHERE ServerId=%s;""",(str(guild.id),))
    



        
            

bot.add_cog(Music(bot))
bot.run('NzI4NjM2MjA4OTMwMDk1MjA0.Xv9RrQ.IPiDYpLcPtv9NyAW_oQcUv_pmEE')	

import requests
import re
import urllib.request
import discord
import json
from discord.utils import get
import discord.utils

class NakedObject(object):
    pass

class SlashCommands:
    # Options types
    SUB_COMMAND       = 1
    SUB_COMMAND_GROUP = 2
    STRING            = 3
    INTEGER           = 4
    BOOLEAN           = 5
    USER              = 6
    CHANNEL           = 7
    ROLE              = 8
    
    # Command types
    SLASH = 1
    
    def __init__(self, client):
        self.bot_user = client
        self.auth = client.http.token
        self.bot_id = str(client.user.id)
        self.commands_url = "https://discord.com/api/v10/applications/" + str(self.bot_id) + "/commands"
        self.guild_commands_url = "https://discord.com/api/v10/applications/" + str(self.bot_id) + "/guilds/"
        self.request_header = {"Authorization": "Bot " + self.auth }
        self.slash_commands = {}
        self.bot_user._connection.parsers["INTERACTION_CREATE"] = self.interaction_override
        
    def new_slash_command(self, name, description):
        # if not re.search(r"[a-z0-9]{1,32}$", name, re.UNICODE):
            # print("Command name does not match requirements!")
            # return False
        json = {
            "name": name,
            "type": self.SLASH,
            "description": description,
            "options": []
        }
        self.slash_commands[name] = json
        return True
        
    def add_global_slash_command(self, command_name):
        
        try:
            self.slash_commands[command_name]
        except:
            print("That slash command hasn't been defined yet!")
            return False
        r = requests.post(self.commands_url, headers=self.request_header, json=self.slash_commands[command_name])
        if re.search(r"400|404|403",str(r)):
            print("Discord returned " + str(r) + " and we were unable to add the global command!")
            return False
        elif re.search(r"200|201",str(r)):
            print("Command registered successfully.")
            return True
        else:
            print("Discord returned " + str(r) + " and we are unsure of the status.")
            return False

        
    def add_guild_slash_command(self, guild_id, command_name):
        try:
            self.slash_commands[command_name]
        except:
            print("That slash command hasn't been defined yet!")
            return False
        r = requests.post(self.guild_commands_url + str(guild_id) + "/commands", headers=self.request_header, json=self.slash_commands[command_name])
        if re.search(r"400|404|403",str(r)):
            print("Discord returned " + str(r) + " and we were unable to add the guild command!")
            return False
        elif re.search(r"200|201",str(r)):
            print("Command registered successfully.")
            return True
        else:
            print("Discord returned " + str(r) + " and we are unsure of the status.")
            return False
    def add_role_command_option(self, command_name, option_name, description, required):
        print("Adding option " + option_name + " to command " + command_name +"!")

        opt_json = { "name": option_name,
                     "description": description,
                     "type": self.ROLE,
                     "required": required,
                     "choices": []
                    }
        self.slash_commands[command_name]["options"].append(opt_json)
        return True            
    def add_user_command_option(self, command_name, option_name, description, required):
        print("Adding option " + option_name + " to command " + command_name +"!")

        opt_json = { "name": option_name,
                     "description": description,
                     "type": self.USER,
                     "required": required,
                     "choices": []
                    }
        self.slash_commands[command_name]["options"].append(opt_json)
        return True
    def add_channel_command_option(self, command_name, option_name, description, required):
        print("Adding option " + option_name + " to command " + command_name +"!")

        opt_json = { "name": option_name,
                     "description": description,
                     "type": self.CHANNEL,
                     "required": required,
                     "choices": []
                    }
        self.slash_commands[command_name]["options"].append(opt_json)
        return True           
    def add_command_option(self, command_name, option_name, description, required):
        # if not re.search(r"^[a-z0-9]{1,32}$", option_name, re.UNICODE):
            # print("Option name does not match requirements!")
            # return False
        print("Adding option " + option_name + " to command " + command_name +"!")

        opt_json = { "name": option_name,
                     "description": description,
                     "type": self.STRING,
                     "required": required,
                     "choices": []
                    }
        self.slash_commands[command_name]["options"].append(opt_json)
        return True
        
    def add_option_choice(self, command_name, option_name, choice_name, choice_value):
        choice_json = {
                        "name": choice_name,
                        "value": choice_value
                      }
        print("Adding choice " + choice_name + " to option " + option_name + " for command " + command_name + ".")
        try:
            option_index = self.slash_commands[command_name]["options"].index(option_name)
        except:
            print("Option doesn't exist!")
            return False
        self.slash_commands[command_name]["options"][option_index]["choices"].append(choice_json)
        return True
        
    def convert_to_message(self, interaction, member, prefix):
        print("called here")
        message = NakedObject()
        message.author = member
        message.reactions = []
        message.tts = False
        message.embeds = []
        message.mentions = []
        message.guild = self.bot_user.get_guild(int(interaction["guild"].id))
        message.content = prefix + interaction["data"]["name"]
        message.channel_mentions = []
#        try:
        if interaction["data"]["options"]:
            for option in interaction["data"]["options"]:
                print(option["name"])
                if option["name"] == 'user':
                    print("User option")
                    user_data = NakedObject()
                    user_data.id = interaction["data"]["resolved"]['users'][option['value']]['id']
                    user_data.username = interaction["data"]["resolved"]['users'][option['value']]['username']
                    user_data.avatar = interaction["data"]["resolved"]['users'][option['value']]['avatar']
                    user_data.discriminator = interaction["data"]["resolved"]['users'][option['value']]['discriminator']
                    user_data.avatar_decoration = interaction["data"]["resolved"]['users'][option['value']]['avatar_decoration']
                    user_data.public_flags = interaction["data"]["resolved"]['users'][option['value']]["public_flags"]
                    user_data.permissions = interaction["data"]["resolved"]['members'][user_data.id]["permissions"]
                    role_list = interaction["data"]["resolved"]['users'][option['value']]["roles"]
                    role_matrix = []
                    for role in role_list:
                        role_matrix.append(self.bot_user.get_role(int(role)))
                    user_data.roles = role_matrix
                    print("user data " + str(user_data))
                    message.mentions.append(user_data)
                    print("messge " + str(message.mentions))
                elif option['name'] == 'role':
                    role = NakedObject()
                    role.id = interaction["data"]["resolved"]['roles'][option['value']]['id']
                    role.name = interaction["data"]["resolved"]['roles'][option['value']]['name']
                    message.role_mentions = [role,]
                elif option['name'] == 'channel':
                    print("Channel option")
                    print(str(list(interaction["data"]["resolved"]["channels"])))
                    for cid in list(interaction["data"]["resolved"]["channels"]):
                        channel = NakedObject()
                        channel.id = interaction["data"]["resolved"]["channels"][cid]["id"]
                        channel.name = interaction["data"]["resolved"]["channels"][cid]["name"]
                        channel.permissions = interaction["data"]["resolved"]["channels"][cid]["permissions"]
                        channel.type = interaction["data"]["resolved"]["channels"][cid]["type"]
                        channel.parent_id = interaction["data"]["resolved"]["channels"][cid]["parent_id"]
                        message.channel_mentions.append(channel)
                    print(message.channel_mentions)
                else:
                    message.content = message.content + " " + str(option["value"])
                    
#        except:
 #           pass
        
        message.attachments = None
        message.channel = self.bot_user.get_channel(int(interaction["channel_id"]))
        print(str(message.content))
        url = "https://discord.com/api/v10/interactions/" + str(interaction["id"]) + "/" + str(interaction["token"]) + "/callback"

        

        json = {
         "type": 4,
         "flags": 64,
         "data": {
         "content": "<@" + str(member.id) + ">"
            }
        }
        r = requests.post(url, json=json)
        print(str(r))
        # delete_url = "https://discord.com/api/v10/webhooks/" + str(self.bot_user.user.id) + "/" + str(interaction["token"]) + "/messages/@original"
        # r2 = requests.delete(delete_url)
        # print("Delete response " + str(r2))        
        if re.search(r"400|404|403", str(r)):
            print("Discord returned " + str(r) + " and we failed to respond.")
            return False
        else:
            msg = self.bot_user.loop.create_task(self.bot_user.on_message(message))

            return True
        sleep(1)
        
    
    def get_emoji_list(guild):
        pass
        
    def get_role_list(guild):
        pass
        
    def get_member_list(guild):
        pass
    
    def interaction_override(self, data):
        guild = self.bot_user.get_guild(int(data["guild_id"]))
        print(str(data))
        member = discord.Member(guild=guild, data=data["member"], state=guild._state)
        _interaction = discord.Interaction(data=data, state=guild._state)
        interaction = {}
        interaction["client"]=self.bot_user
        interaction["version"]=data["version"]
        interaction["type"]=data["type"]
        interaction["token"]=data["token"]
        interaction["id"]=data["id"]
        interaction["guild"]=guild
        interaction["channel_id"]=data["channel_id"]
        interaction["data"]=data["data"]
        interaction["member_data"]=data["member"]
        self.bot_user.loop.create_task(self.bot_user.on_interaction(member, interaction))

    
    
    

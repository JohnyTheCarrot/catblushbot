import json
import os
import discord
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["database"]
servers = database["servers"]

template = {
	"ID": 0,
	"name": "",
	"channels": [],
	"prefix": None,
	"features": [],
	"logging": {
		"message_logs": 0,
		"server_logs": 0
	}
}

def create_server(guild: discord.Guild):
	if not server_exists(guild.id):
		data = {
			"ID": guild.id,
			"name": guild.name,
			"channels": [],
			"prefix": None,
			"features": [],
			"logging": {
				"message_logs": 0,
				"server_logs": 0
			}
		}
		for channel in guild.channels:
			data["channels"].append({"name": channel.name, "id": channel.id})
		servers.insert_one(data)

def update(guild: discord.Guild):
	channels = []
	for channel in guild.text_channels:
		channels.append({"name": channel.name, "id": channel.id})
	servers.update_one({"ID": guild.id}, {"$set": {"ID": guild.id, "name": guild.name, "channels": channels}})

def delete_server(ID: int):
	if server_exists(ID):
		servers.delete_one({"ID": ID})

def server_exists(ID: int):
	found = False
	for x in servers.find({"ID": ID}):
		found = True
	return found

def update_guild_name(ID: int, name: str):
	if server_exists(ID):
		servers.update_one({"ID": ID}, {"$set": {"name": name}})
	else:
		return None

def update_message_log(guild: int, channel: int):
	if server_exists(guild):
		servers.update_one({"ID": guild}, {"$set": {"logging": {"message_logs": channel, "server_logs": get_server_log(guild)}}})
	else:
		return None


def get_config(ID: int):
	doc = servers.find({"ID": ID}, {"_id": 0})
	for x in doc:
		return x

#def edit_config(ID: int, data):
#	if server_exists(ID):
#		with open('./data/{}.json'.format(ID), 'w') as outfile:  
#				json.dump(data, outfile)

def get_server_features(ID: int):
	if server_exists(ID):
		return get_config(ID)["features"]
	else:
		return None

def edit_server_features(ID: int, feature):
	if server_exists(ID):
		features = get_config(ID)["features"]
		features.append(feature)
		servers.update_one({"ID": ID}, {"$set": {"features": features}})

def get_server_prefix(ID: int):
	if server_exists(ID) and get_config(ID) is not None:
		return '$' if get_config(ID)["prefix"]==None else get_config(ID)["prefix"]
	else:
		return '$'

def set_server_prefix(ID: int, prefix: str):
	if server_exists(ID):
		servers.update_one({"ID": ID}, {"$set": {"prefix": prefix}})
		return get_config(ID)
	else:
		return None

async def is_setup(ctx):
	if server_exists(ctx.guild.id):
		return True
	else:
		await ctx.send("Server not set up yet! Please use `$setup` to set up your server.")
		return False

async def get_server_log(ID: int):
	if server_exists(ID) and get_config(ID) is not None:
		return get_config(ID)["logging"]["server_logs"]
	else:
		return None

async def get_message_log(ID: int):
	if server_exists(ID) and get_config(ID) is not None:
		return get_config(ID)["logging"]["message_logs"]
	else:
		return None

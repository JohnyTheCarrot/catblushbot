import discord
import DBHandler

async def AdminLog(client, message: str):
	await client.get_channel(570576350713217034).send(message)
	
async def ErrorLog(client, message: str):
	await client.get_channel(570607272808546315).send(message)
	
async def MessageLogs_str(client, guild: int, message: str):
    if DBHandler.server_exists(guild):
        channel = await DBHandler.get_message_log(guild)
        if channel is not 0:
            channel_obj = client.get_guild(guild).get_channel(channel)
            if channel_obj is not None:
                await channel_obj.send(message)
            else:
                print("Channel by ID {} not found in guild {}".format(channel, guild))
			
async def MessageLogs(client, guild: int, message: str, embed):
    if DBHandler.server_exists(guild):
        channel = await DBHandler.get_message_log(guild)
        if channel is not 0:
            channel_obj = client.get_guild(guild).get_channel(channel)
            if channel_obj is not None:
                await channel_obj.send(message, embed=embed)
            else:
                print("Channel by ID {} not found in guild {}".format(channel, guild))

async def ServerLogs_str(client, guild: int, message: str):
    if DBHandler.server_exists(guild):
        channel = await DBHandler.get_server_log(guild)
        if channel is not 0:
            channel_obj = client.get_guild(guild).get_channel(channel)
            if channel_obj is not None:
                await channel_obj.send(message)
            else:
                print("Channel by ID {} not found in guild {}".format(channel, guild))

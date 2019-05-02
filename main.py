import discord
from discord.ext import commands
from Util import Logging
import DBHandler
import leveling
from prometheus_client import CollectorRegistry
import json
import pymongo
import time

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["database"]
levels = database["levels"]

def get_prefix(bot, message):
	if not message.guild:
		return '$'

	# If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
	return commands.when_mentioned_or(DBHandler.get_server_prefix(message.guild.id))(bot, message)


bot = commands.Bot(command_prefix=get_prefix)
bot.load_extension("jishaku")

extensions = ['admin', 'setup', 'fun', 'moderation', 'leveling']

def get_guild(ID: int):
	return bot.get_guild(ID)

@bot.event
async def on_ready():
	print('logged in as {0.user}'.format(bot))

@bot.event
async def on_guild_join(guild):
	await Logging.AdminLog(bot, "Joined server by name **{}** ({})".format(sanitize(guild.name), guild.id))

@bot.event
async def on_guild_remove(guild):
	await Logging.AdminLog(bot, "Left server by name **{}** ({})".format(sanitize(guild.name), guild.id))
	DBHandler.delete_server(guild.id)

@bot.event
async def on_guild_update(before, after):
	DBHandler.update_guild_name(before.id, after.name)
	print("Updating guild name")

@bot.event
async def on_guild_channel_create(channel):
	print("Channel created, updating config.")
	DBHandler.update(channel.guild)

@bot.event
async def on_guild_channel_delete(channel):
	print("Channel deleted, updating config.")
	DBHandler.update(channel.guild)

@bot.event
async def on_guild_channel_update(before, after):
	print("Channel updated, updating config.")
	DBHandler.update(after.guild)

#user
@bot.command()
async def about(ctx):
	members = 0
	for guild in bot.guilds:
		members += len(guild.members)
	embed = discord.Embed(title="About Catblushbot", description="Serving {} members in {} guilds".format(members, len(bot.guilds)))
	await ctx.send(embed=embed)

@bot.event
async def on_message(message):
	if message.author.bot:
		return
	#TODO: Fix bug where pinging the bot does give you XP
	if not message.content.startswith(DBHandler.get_server_prefix(message.guild.id), 0, 1):
            doc = levels.find({"id": message.author.id, "guild_id": message.guild.id, "lastexecuted": {"$exists": True}}, {"_id": 0}).limit(0)
            exists = False
            content = None
            for x in doc:
                exists = True
                content = x
                break;
            current_unix = int(time.time())
            if exists:
                if current_unix >= content["lastexecuted"]+15: 
                    await leveling.givexp(message.author, 5)
                    levels.update_one({"id": message.author.id, "guild_id": message.guild.id}, {"$set": {"lastexecuted": current_unix}})
                else:
                    pass
                    #print("User {} sent a message, but couldn't gain xp because of their cooldown. They have {} left to their cooldown.".format(message.author.name, (content["lastexecuted"]+15)-current_unix))
	if ":catblush:" in message.content and message.channel.id == 565143658156785684:
		await message.author.add_roles(discord.utils.get(message.guild.roles, name="Movie Fren :catblush:"))
	ctx: commands.Context = await bot.get_context(message)
	
	await bot.invoke(ctx)

@bot.event
async def on_message_edit(before, after):
	if after.author.bot:
		return
	if not before.pinned and after.pinned:
		embed = discord.Embed(color=0x3333ff, description=after.content)
		embed.set_author(name="{}#{}".format(after.author.name, after.author.discriminator), url="https://discordapp.com/users/{}".format(after.author.id), icon_url=after.author.avatar_url)
		await Logging.MessageLogs(bot, after.guild.id, ":pushpin: A message was pinned in <#{}>".format(after.channel.id), embed)
	if before.pinned and not after.pinned:
		embed = discord.Embed(color=0x3333ff, description=after.content)
		embed.set_author(name="{}#{}".format(after.author.name, after.author.discriminator), url="https://discordapp.com/users/{}".format(after.author.id), icon_url=after.author.avatar_url)
		await Logging.MessageLogs(bot, after.guild.id, ":pushpin: A message was unpinned in <#{}>".format(after.channel.id), embed)
	elif after.edited_at is not None:
		embed = discord.Embed(color=0xFFC300)
		embed.add_field(name="Before", value=before.content, inline=False)
		embed.add_field(name="After", value=after.content, inline=False)
		await Logging.MessageLogs(bot,
								after.guild.id,
								":pencil: **{}**#**{}** (**{}**) edited a {}message in <#{}>:"
								.format(sanitize(after.author.name), after.author.discriminator, after.author.id, "pinned " if before.pinned and after.pinned else "", after.channel.id),
								embed
								)

@bot.event
async def on_message_delete(message):
	if not message.author.bot:
		embed = discord.Embed(description=message.content, color=0xff0000)
		await Logging.MessageLogs(bot,
								message.guild.id,
								":x: **{}**#**{}** (**{}**)'s {}message has been deleted from <#{}>:"
								.format(sanitize(message.author.name), message.author.discriminator, message.author.id, "pinned " if message.pinned else "", message.channel.id),
								embed
								)

#servelog
@bot.event
async def on_member_join(member):
	await Logging.ServerLogs_str(bot,
							member.guild.id,
							":inbox_tray: **{}**#**{}** (**{}**) joined the server."
							.format(sanitize(member.name), member.discriminator, member.id)
							)

def sanitize(msg: str):
	return discord.utils.escape_markdown(discord.utils.escape_mentions(msg))
	
if __name__ == '__main__':
	for extension in extensions:
		try:
			bot.load_extension(extension)
		except Exception as error:
			print('{} cannot be loaded. [{}]'.format(extension, error))

with open('./stuff_I_probably_shouldnt_leek.json', 'r') as json_file:
	copied_json = json.load(json_file)
	bot.run(copied_json["lolxd"])

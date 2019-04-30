import discord
from discord.ext import commands
import DBHandler
import pymongo
import aiohttp
import io

client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["database"]
levels = database["levels"]
servers = database["servers"]

class leveling(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def rank(self, ctx):
		if "LEVELING" in DBHandler.get_server_features(ctx.guild.id):
			level = get_registered_member(ctx.author)
			if level is None:
				await ctx.send("You're not in my database!")
			else:
				await ctx.send("You have **{}** xp at level **{}**.".format(level["xp"], level["level"]))
	
	@commands.command()
	async def rank_other(self, ctx, member: discord.Member):
		if "LEVELING" in DBHandler.get_server_features(ctx.guild.id):
			level = get_registered_member(member)
			if level is None:
				await ctx.send("This user is not in my database!")
			else:
				await ctx.send("User {} has **{}** xp at level **{}**.".format(sanitize(member.name), level["xp"], level["level"]))

	@commands.command()
	@commands.is_owner()
	async def serverdb(self, ctx):
		doc = levels.find({"guild_id": ctx.guild.id}, {"_id": 0})
		text = ""
		for x in doc:
			text+="{}\n".format(x)
		await ctx.send("```{}```".format(text))

	@commands.command()
	@commands.is_owner()
	async def wipe_sajuuks_xp(self, ctx):
		await ctx.send("Okay")
		levels.update_one({"id": 136429236167770112, "guild_id": ctx.guild.id}, {"$set": {"xp": 0, "level": 0}})

	@commands.command()
	async def snapxp(self, ctx, member: discord.Member):
		if "LEVELING" in DBHandler.get_server_features(ctx.guild.id) and ctx.message.author.guild_permissions.administrator:
			b = io.BytesIO(b"./assets/tenor.gif")
			if member_registered(member):
				new_exp = get_registered_member(member)["xp"]/2
				levels.update_one({"id": member.id, "guild_id": ctx.guild.id}, {"$set": {"xp": new_exp, "level": 0}})
				await givexp(member, 0)
				await ctx.send(content="Perfectly balanced, as all xp should be.\n{}'s xp is now {}".format(sanitize(member.name), new_exp), file=discord.File(fp=b.getvalue(), filename="snap.gif"))
			else:
				await ctx.send("That user is not in my database!")


	@commands.command()
	@commands.is_owner()
	async def _givexp(self, ctx, member: discord.Member, xp: int):
		if "LEVELING" in DBHandler.get_server_features(ctx.guild.id):
			await givexp(member, xp)
			await ctx.send("Added {} to user {}. Xp now {}".format(xp, sanitize(member.name), get_registered_member(member)["xp"]))

	@commands.group()
	async def levels(self, ctx):
		if "LEVELING" in DBHandler.get_server_features(ctx.guild.id) and ctx.message.author.guild_permissions.administrator:
			if ctx.invoked_subcommand is None:
				await ctx.send('Invalid sub command passed.')
	
	@levels.command()
	async def set(self, ctx, level: int, xp: int, role: discord.Role):
		await ctx.send("Setting")
		set_unlockable_role_at(ctx.guild.id, level, xp, role)
	
	@levels.command()
	async def get(self, ctx):
		text = ""
		for x in get_unlockable_roles(ctx.guild.id):
			text+="{}\n".format(x)
		await ctx.send("```{}```".format(text))

def sanitize(msg: str):
	return discord.utils.escape_markdown(discord.utils.escape_mentions(msg))

def register_member(member: discord.Member):
	if "LEVELING" in DBHandler.get_server_features(member.guild.id):
		levels.insert_one({"id": member.id, "guild_id": member.guild.id, "level": 0, "xp": 0})
		doc = levels.find({"id": member.id, "guild_id": member.guild.id}).limit(1)
		for x in doc:
			return x	

def member_registered(member: discord.Member):
	if "LEVELING" in DBHandler.get_server_features(member.guild.id):
		doc = levels.find({"id": member.id, "guild_id": member.guild.id}).limit(1)
		found = False
		for x in doc:
			found = True
		return found

def get_registered_member(member: discord.Member):
	registered = member_registered(member)
	if registered:
		doc = levels.find({"id": member.id, "guild_id": member.guild.id}, {"_id": 0})
		for x in doc:
			return x
		return None
	return None

async def givexp(member: discord.Member, xp: int):
	if "LEVELING" in DBHandler.get_server_features(member.guild.id):
		new_exp = 0
		if member_registered(member):
			new_exp = get_registered_member(member)["xp"]+xp
		else:
			registered_member = register_member(member)
			new_exp = registered_member["xp"]+xp
		role_ids = []
		for role in member.roles:
			role_ids.append(role.id)
		level_updated = False
		level = 0
		for unlockable_role in get_unlockable_roles(member.guild.id):
			if not unlockable_role["role"] in role_ids:
				if unlockable_role["xp"] <= new_exp:
					await member.add_roles(member.guild.get_role(unlockable_role["role"]), reason="User reached level {}".format(unlockable_role["level"]))
					level_updated = True
					level = unlockable_role["level"]
				elif unlockable_role["xp"] >= new_exp:
					await member.remove_roles(member.guild.get_role(unlockable_role["role"]), reason="User no longer has the level required")
		if level_updated:
			levels.update_one({"id": member.id, "guild_id": member.guild.id}, {"$set": {"xp": new_exp, "level": level}})
		else:
			levels.update_one({"id": member.id, "guild_id": member.guild.id}, {"$set": {"xp": new_exp}})

def  set_unlockable_role_at(guild: int, level: int, xp: int, role: discord.Role):
	doc = servers.find({"ID": guild}).limit(1)
	if doc is not None:
		unlockable_roles = []
		for x in doc:
			try:
				unlockable_roles = x["unlockable_roles"]
			except KeyError:
				pass
		updating = False
		for unlockable_role in unlockable_roles:
			if role.id == unlockable_role["role"]:
				print("updating, not inserting")
				updating = True
				unlockable_role["role"] = role.id
		if not updating:
			unlockable_roles.append({"level": level, "xp": xp, "role": role.id})
		servers.update_one({"ID": guild}, {"$set": {"unlockable_roles": unlockable_roles}})

def get_unlockable_roles(guild: int):
	doc = servers.find({"ID": guild}).limit(1)
	if doc is not None:
		unlockable_roles = []
		for x in doc:
			try:
				unlockable_roles = x["unlockable_roles"]
			except KeyError:
				return None
		return unlockable_roles
	else:
		return None

def setup(client):
	client.add_cog(leveling(client))
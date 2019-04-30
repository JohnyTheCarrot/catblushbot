import discord
import ast
import DBHandler
from discord.ext import commands
import os
import json
import inspect
import io
import textwrap
import traceback
import aiohttp
from contextlib import redirect_stdout
import base64
import json

class admin(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	@commands.command()
	async def ping(self, ctx):
		await ctx.send("pong!")

	@commands.group(aliases=["sf"])
	@commands.is_owner()
	async def server_features(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid sub command passed.')
			
	@server_features.command()
	async def list(self, ctx, guild: int):
		await ctx.send("```json\n{}```".format(DBHandler.get_server_features(guild)))
	
	@server_features.command()
	async def add(self, ctx, guild: int,  feature: str):
		DBHandler.edit_server_features(guild, feature)
		await ctx.send("```json\n{}```".format(DBHandler.get_server_features(guild)))

	@commands.command(name="eval")
	@commands.is_owner()
	async def _eval(self, ctx, *, body: str):
		#try:
		eval(body)
		#except Exception as ex:
		#	await ctx.send("```{}```".format(ex))

def setup(client):
	client.add_cog(admin(client))

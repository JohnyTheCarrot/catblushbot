import discord
from discord.ext import commands
from Util import Logging, Enums
import DBHandler

class server_setup(commands.Cog):
	def __init__(self, client):
		self.client = client

	#@commands.Cog.listener()
	#async def on_command_error(bot, ctx: commands.Context, error):
	#	await ctx.send(f"Something went wrong while executing that command")
	#	print(error)

	@commands.command()
	@commands.guild_only()
	async def setup(self, ctx):
		is_admin = ctx.message.author.guild_permissions.administrator
		if is_admin:
			await ctx.send("Setting up.")
			await Logging.AdminLog(self.client, "Setting up server **{}** (**{}**)".format(discord.utils.escape_mentions(discord.utils.escape_markdown(ctx.guild.name)), ctx.guild.id))
			DBHandler.create_server(ctx.guild)

	@commands.command()
	@commands.guild_only()
	async def prefix(self, ctx, prefix: str):
		is_setup = await DBHandler.is_setup(ctx)
		is_admin = ctx.message.author.guild_permissions.administrator
		if is_admin and is_setup:
			config = DBHandler.get_config(ctx.guild.id)
			config["prefix"] = prefix
			DBHandler.edit_config(ctx.guild.id, config)
			await ctx.send("Prefix set to {}".format(discord.utils.escape_mentions(discord.utils.escape_markdown(prefix))))

	@commands.command()
	@commands.guild_only()
	async def settings(self, ctx):
		is_setup = await DBHandler.is_setup(ctx)
		is_admin = ctx.message.author.guild_permissions.administrator
		if is_admin and is_setup:
			config = DBHandler.get_config(ctx.guild.id)
			message_log = await DBHandler.get_message_log(ctx.guild.id)
			embed = discord.Embed(title="Server Settings for " + ctx.guild.name, color=0x808cff)
			embed.add_field(name="Prefix", value=DBHandler.get_server_prefix(ctx.guild.id), inline=True)
			embed.add_field(name="Message Log", value=message_log, inline=True)
			embed.add_field(name="Features", value=DBHandler.get_server_features(ctx.guild.id), inline=False)
			await ctx.send(embed=embed)

	@commands.group()
	@commands.guild_only()
	async def logging(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid sub command passed.')

	@logging.command()
	@commands.guild_only()
	async def set(self, ctx, logtype: str, channel: discord.TextChannel):
		is_setup = await DBHandler.is_setup(ctx)
		is_admin = ctx.message.author.guild_permissions.administrator
		if is_admin and is_setup:
			if logtype == "messages":
				config = DBHandler.get_config(ctx.guild.id)
				config["logging"]["message_logs"] = channel.id
				DBHandler.edit_config(ctx.guild.id, config)

def setup(client):
	client.add_cog(server_setup(client))

import discord
from discord.ext import commands
from Util import Logging, Enums
import DBHandler

class moderation(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.command()
	async def userinfo(self, ctx, member: discord.Member):
		if ctx.message.author.guild_permissions.ban_members or ctx.message.author.guild_permissions.administrator:
			roles = ""
			for role in member.roles:
				roles += " `{}` ".format(role.name)
			embed = discord.Embed(color=member.color)
			embed.set_thumbnail(url=member.avatar_url)
			embed.description = "• Username: **{}**\n• Discriminator: **{}**\n• Roles: {}\n• Joined At: **{}**\n• Created At: **{}**".format(member.name, member.discriminator, roles, member.joined_at, member.created_at)
			await ctx.send(embed=embed)
	
	@commands.command()
	async def ban(self, ctx: commands.Context, users: discord.User, *, reason: str = ""):
		if ctx.message.author.guild_permissions.ban_members:
			await ctx.send("catblush")
		else:
			await ctx.send("You do not have permission to run that command!")

	@commands.command()
	async def roles(self, ctx):
		if ctx.message.author.guild_permissions.ban_members or ctx.message.author.guild_permissions.administrator:
			text = ""
			roles = ctx.guild.roles[:]
			roles.sort(reverse=True)
			for role in roles:
				text += "\"{}\" ({})\n".format(role.name, role.id)
			await ctx.send("```{}```".format(text))

def setup(client):
	client.add_cog(moderation(client))
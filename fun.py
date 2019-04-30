import discord
from discord.ext import commands
import DBHandler

class main(commands.Cog):
	def __init__(self, client):
		self.client = client
		
	@commands.command()
	async def catblush(self, ctx, user: discord.User):
		await ctx.send("<@{}> absolutely catblushed <@{}> <:catblush:564867978508894208><:catblush:564867978508894208><:catblush:564867978508894208><:catblush:564867978508894208>".format(ctx.author.id, user.id))
		
def setup(client):
	client.add_cog(main(client))
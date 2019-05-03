import discord, asyncio
from discord.ext import commands
from PromMonitoring import command_counter, ping_tracker

class GrafanaCog(commands.Cog):

    def __init__(self, client):
        self.client: commands.Bot = client
        self.ping_background_task = self.client.loop.create_task(self.log_ping())

    async def log_ping(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            ping_tracker.track_api_ping(self.client.latency)
            # debugging statement
            # print('logged ping {ping}'.format(ping=self.client.latency))
            await asyncio.sleep(30)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        command_counter.track_command_run(ctx.command.name)



def setup(client):
    client.add_cog(GrafanaCog(client))
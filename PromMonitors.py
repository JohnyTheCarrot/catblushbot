import prometheus_client as prom

class PromMonitors:
    def __init__(self, bot) -> None:
        self.command_counter = prom.Counter("commands_ran", "How many times commands were ran and who ran them", [
            "command_name",
            "guild_id"
        ])

    def track_command_run(self, command_name: str, guild_id: int):
        self.command_counter.labels(command_name=command_name, guild_id=guild_id).inc()
import prometheus_client as prom

class PromMinotors:
    def __init__(self, bot) -> None:
        self.command_counter = prom.Counter("commands_ran", "How many times commands were ran and who ran them", [
            "command_name",
            "guild_id"
        ])
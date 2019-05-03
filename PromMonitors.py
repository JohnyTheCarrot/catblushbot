import prometheus_client as prom

class CommandCounter:
    def __init__(self, registry: prom.CollectorRegistry) -> None:
        self.command_counter = prom.Gauge("commands_ran", "How many times commands were ran and who ran them", [
            "command_name"
        ], registry=registry)

    def track_command_run(self, command_name: str):
        self.command_counter.labels(command_name=command_name).inc()

class PingTracker:
    def __init__(self, registry: prom.CollectorRegistry) -> None:
        self.ping_tracker = prom.Gauge("api_ping", "the ping rate", registry=registry)

    def track_api_ping(self, ping):
        self.ping_tracker.set(ping)
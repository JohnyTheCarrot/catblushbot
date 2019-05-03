from prometheus_client import start_http_server, CollectorRegistry, REGISTRY
import PromMonitors as monitors

registry = CollectorRegistry()
command_counter = monitors.CommandCounter(registry)
ping_tracker = monitors.PingTracker(registry)

def start_server():
    REGISTRY.register(registry)
    start_http_server(9091)
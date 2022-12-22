"""xrootd exporter"""

import os
import time
from prometheus_client import start_http_server, Gauge, Enum, Counter
import psutil
import requests

class xrootd_exporter:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, port=9090, polling_interval_seconds=5):
        self.port = port
        self.polling_interval_seconds = polling_interval_seconds

        # Prometheus metrics to collect
        self.current_requests = Gauge("exporter_requests_current", "Current requests")
        self.pending_requests = Gauge("exporter_requests_pending", "Pending requests")
        self.total_uptime = Gauge("exporter_uptime", "Uptime")
        self.health = Enum("exporter_health", "Health", states=["healthy", "unhealthy"])
        self.xrootd_state={ "pid": Gauge("pid_running","XRootD running")}

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """

        self.xrootd_state['pid'].set(0)

def main():
    """Main entry point"""

    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "5"))
    my_port = int(os.getenv("XRTOOD_PORT", "1024"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9090"))

    app_metrics = xrootd_exporter(
        port=exporter_port,
        polling_interval_seconds=polling_interval_seconds
    )
    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()

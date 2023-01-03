"""xrootd exporter"""

import os
import time
from prometheus_client import start_http_server, Gauge, Enum, Counter
import psutil
import requests
import subprocess

class xrootd_exporter:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """
    def fetch_mpxstat(self):
        lines=[]
        while not lines or lines[-1]!="":
            line = self.mpx.stdout.readline()
            lines.append(line.decode('utf-8').rstrip())
        self.mpx_stats={l.split(' ')[0] : l.split(' ')[1] for l in lines[:-1:]}

    def __init__(self, port=9090, polling_interval_seconds=5):
        """Rlaceholder for metrics to collect"""
        self.mpx_stats={}
        self.port = port
        self.polling_interval_seconds = polling_interval_seconds
        self.mpx=subprocess.Popen('/usr/local/bin/mpxstats -f flat -p 10024'.split(' '),stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self.xrootd_state={
            "pid":           Gauge("pid_running","XRootD PID"),\
            "service_state": Enum("service_state","Service State", states=["active", "inactive","activating","deactivating","failed","dead"]),\
            "service_up":    Gauge("service_up","checks if the service is up"),
            "inodes":        Gauge("nr_inodes","number of inodes") }

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            start=time.time()
            while ((time.time() - start) < self.polling_interval_seconds):
                self.fetch_mpxstat()
                print(self.mpx_stats)
            self.fetch()

    def myrun(self, cmd ):
        result=subprocess.run(cmd.split(' '),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return str(result.stdout,'utf-8').rstrip()

    def systemctl_property(self,prop="MainPID"):
        return self.myrun(f"systemctl show --property {prop} --value xrootd@1.service")


    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        pid=self.systemctl_property('MainPID')
        self.xrootd_state['pid'].set(pid)
        self.xrootd_state['service_state'].state(self.systemctl_property('ActiveState'))
        self.xrootd_state['inodes'].set(len(self.myrun(f"ls -la /proc/{pid}/fd/").split('\n')))

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

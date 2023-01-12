# XRootD Exporter

This repository contains code for a [prometheus](https://prometheus.io/) exporter that exports metrics of [XRootD](https://xrootd.slac.stanford.edu/) dataservers and redirectors.
It uses XRootD's `mpxstats` tool, which can optionally be enabled on servers/redirectors to send statistics to listeners via UDP.
The exporter transforms `mpxstats` metrics into prometheus metrics, making those available for monitoring via prometheus.
A optional [file](./descriptions.cfg) containing descriptions for metrics is provided seperatly.

## Dependencies

* Python 3.X
* prometheus_client python package

## Usage

The process can be started by 

```
python3 /path/to/xrootd_exporter.py
```

Alternatively, a [systemd unitfile](./xrootd_exporter@.service) is provided.

### XRootD 

Modify your xrootd configuration and point it to the host::port running the exporter

```
xrd.report 127.0.0.1:10024 every 10 -all
```


## Configuration

On startup, xrootd_exporter.py looks for 4 optional environmental variables:

1) `MPX_PORT` defines the UDP listening port of the exporter's `mpxstats` process, the default is 10024
2) `MPX_PATH` defines the path to the `mpxstats` binary 
3) `EXPORTER_PORT` defines the TCP listening port of the exporter's prometheus web server, the default is 9090
4) `EXPORTER_DESCRIPTION_FILE` defines the path to [file containing metric descriptions](./descriptions.cfg)

When using the [systemd unitfile](./xrootd_exporter@.service) you can easily modify the service by adding

```
Environment=MPX_PATH=/usr/local/bin/mpxstats
```

## License

LGPL3 as described in the [License File](./LICENSE)

## Project status

As for the current scope this exporter is considered completed.
It implements all summary statistics available via `mpxstats`.
Even though, a much more advanced exporter based on the [detailed monitoring data format](https://xrootd.slac.stanford.edu/doc/dev55/xrd_monitoring.htm#_Toc99653748) might prove useful in the future.

## Contribution

Feel free to suggest features and report bugs via issues

## Vagrant setup

A Vagrant/Ansible setup consisting of 2 data servers and grafana/prometheus instance is available [here](https://github.com/GSI-HPC/xrootd_monitoring_setup).

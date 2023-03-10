"""xrootd exporter"""

import os
from prometheus_client import start_http_server, Gauge, Info
from subprocess import Popen, run, PIPE

class xrootd_exporter:
    """
    Encapsulates all metrics exported by XRootD via the mpxstats tool and transforms them into Prometheus metrics.
    """

    def fetch_mpxstat(self):
        """Reads the output stream of the mpx process into mpx_stats"""
        self.verify_mpx_running()
        read_line=lambda:self.mpx.stdout.readline().decode('utf-8').rstrip()
        line=read_line() 
        while line != "":
            k,v=line.split(' ')
            self.mpx_stats[k]=v
            line=read_line() 

    def create_gauge(self,name,desc,fx):
        """Shorthand function to create a gauge with value bound by a given a function"""
        g=Gauge(name,desc)
        g.set_function(fx)
        return g

    def get_description(self,name):
        if name not in self.descs.keys():
            return f"Refer to description found in the XRootD {self.mpx_stats['ver']} Monitoring manual"
        return f"{self.descs[name]}"

    def load_descriptions(self,path):
        with open(path,'r') as file:
            data=file.read()
        self.descs={line.split(' ')[0]: (line.split(' ',1)[1]).rstrip()  for line in data.split('\n')[:-1:]} 

    
    def verify_mpx_running(self):
        self.mpx.poll()
        rc=self.mpx.returncode
        if rc!=None: raise Exception(f"mpxstats process has terminated with {rc}")

    def __init__(self, mpx_port=10024,mpx_path='/usr/bin/mpxstats',desc_path=""):
        # create mpxstats process
        self.mpx=Popen([mpx_path,'-f','flat', '-p', str(mpx_port)],stdout=PIPE)
        self.mpx_stats={}
        self.fetch_mpxstat()
        self.descs={}

        # load the descriptions if a path is given
        if desc_path != "":
            self.load_descriptions(desc_path)

        # helper lambdas 
        repl_dots           = lambda st:st.replace(".","_")  #replace dots which are not allowed in prometheus vars
        run_cmd             = lambda cmd,stdout=PIPE: str(run(cmd,stdout=stdout).stdout,'utf-8').rstrip()
        get_mpxstat         = lambda key: lambda: self.mpx_stats[key]
        self.updt_mpx_infos = lambda: self.mpx_infos.info({f"xrd_{repl_dots(k)}":v for k,v in self.mpx_stats.items() if k in info_keys})
        
        #filterlist for non float info keys
        info_keys=["ver","src","pgm",'oss.paths.0.lp','oss.paths.0.rp','ofs.role']

        # generate a list of gauges for all values gathered by mpxstats, bind indirected lambda to access the value every time
        self.mpx_gauges=[ self.create_gauge(f"xrd_{repl_dots(k)}",self.get_description(k) , get_mpxstat(k)) 
                         for k in self.mpx_stats.keys() if not k in info_keys ]

        # generate a Info, use updt_mpx_infos to gather newest mpx info data from info_keys
        self.mpx_infos= Info("xrd_config",' '.join([f"{key}:{self.get_description(key)};" for key in info_keys]))
        self.updt_mpx_infos()

        # additional custom gauges
        self.xrd_inodes=  self.create_gauge("nr_inodes","number of inodes",
                                      lambda: run_cmd(['ls','-la',f"/proc/{self.mpx_stats['pid']}/fd/"]).count('\n')+1)

    def run_metrics_loop(self):
        """Endlessly fetch mpxstats"""

        while True:
            try:
                self.fetch_mpxstat()
                self.updt_mpx_infos()
            except Exception as e:
                self.mpx.kill()
                raise e


def main():
    """Main entry point"""

    mpx_port = int(os.getenv("MPX_PORT", "10024"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9090"))
    mpx_path=os.getenv("MPX_PATH","/usr/bin/mpxstats")
    desc_path=os.getenv("EXPORTER_DESCRIPTION_FILE","")

    xrd_metrics = xrootd_exporter(mpx_port=mpx_port,mpx_path=mpx_path,desc_path=desc_path)
    start_http_server(exporter_port)
    xrd_metrics.run_metrics_loop()

if __name__ == "__main__":
    main()

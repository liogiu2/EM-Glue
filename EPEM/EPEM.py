import os
import sys

if os.name == 'nt':
    pddl_path = "C:\\Users\\giulio17\\Documents\\Camelot_work\\EV_PDDL"
else:
    pddl_path = "/Users/giuliomori/Documents/GitHub/EV_PDDL/"

sys.path.insert(0, pddl_path)
import logging
import getopt
from pathlib import Path
from datetime import datetime
import subprocess
import atexit
import time

fastapi_process = None
camelot_process = None

def close_all():
    global fastapi_process, camelot_process
    fastapi_process.terminate()
    camelot_process.kill()

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hd")
    except getopt.GetoptError:
        print('Parameter not recognized')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("usage: python EPEM.py <optional> -d")
            sys.exit()
        elif opt == '-d':
            import debugpy
            debugpy.listen(5678)
            debugpy.wait_for_client()
            logname = "logEPEM"+datetime.now().strftime("%d%m%Y%H%M%S")+".log"
            Path("logs/python/").mkdir(parents=True, exist_ok=True)
            logging.basicConfig(filename='logs/python/'+logname, filemode='w', format='%(levelname)s:%(message)s', level=logging.DEBUG)
    os.chdir("EPEM")
    global fastapi_process, camelot_process
    fastapi_process = subprocess.Popen(["uvicorn", "environment_IO_communication:app", "--reload"])
    camelot_process = subprocess.Popen("cd \"C:\\Users\\giulio17\\Desktop\\Camelot v1.1 Windows\\Camelot v1.1 Windows\" && Camelot.exe", shell = True)
    atexit.register(close_all)

    while(True):
        time.sleep(1)
    
    


if __name__ == '__main__':
    main(sys.argv[1:])
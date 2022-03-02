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
from EPEM_manager import EPEM_Manager

fastapi_process = None
camelot_process = None

def close_all():
    global fastapi_process, camelot_process
    fastapi_process.terminate()
    camelot_process.kill()

def main(argv):
    os.remove("db/sql_app.db")
    try:
        opts, args = getopt.getopt(argv,"hdS")
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
        elif opt == '-S':
            os.chdir("EPEM")
            Path("db/").mkdir(parents=True, exist_ok=True)
            global fastapi_process, camelot_process
            fastapi_process= subprocess.Popen(["uvicorn", "API_communication:app", "--reload", "--port 8080"])
            camelot_process = subprocess.Popen("cd \"C:\\Users\\giulio17\\Desktop\\Camelot v1.1 Windows\\Camelot v1.1 Windows\" && Camelot.exe", shell = True)
            atexit.register(close_all)

    EPEM_Manager().main_loop()
    

if __name__ == '__main__':
    main(sys.argv[1:])
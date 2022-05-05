import os
import sys
from utilities import read_json_file

parameters = read_json_file("parameters.json")
if os.name == 'nt':
    pddl_path = parameters["Windows"]["PDDL_library_path"]
    environment_command = parameters["Windows"]["environment_command"]
    em_command = parameters["Windows"]["experience_manager_command"]
else:
    pddl_path = parameters["MAC"]["PDDL_library_path"]
    environment_command = parameters["MAC"]["environment_command"]
    em_command = parameters["MAC"]["experience_manager_command"]

sys.path.insert(0, pddl_path)
import logging
import getopt
from pathlib import Path
from datetime import datetime
import subprocess
import atexit
import EPEM_manager

fastapi_process = None
environment_process = None
em_process = None

def close_all():
    global fastapi_process, environment_process, em_process
    fastapi_process.terminate()
    environment_process.kill()
    em_process.kill()

def main(argv):
    try:
        os.remove("db/sql_app.db")
    except FileNotFoundError:
        pass
    try:
        opts, args = getopt.getopt(argv,"hdlS")
    except getopt.GetoptError:
        print('Parameter not recognized')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("usage: python EPEM.py <optional> -d -l -S")
            print("optional: -d to start the debug using debugpy on port 5678")
            print("optional: -l to start the logging")
            print("optional: -S to start the API server")
            sys.exit()
        elif opt == '-d':
            import debugpy
            debugpy.listen(5678)
            debugpy.wait_for_client()
        elif opt == '-l':
            logname = "logEPEM"+datetime.now().strftime("%d%m%Y%H%M%S")+".log"
            Path("logs/python/").mkdir(parents=True, exist_ok=True)
            logging.basicConfig(filename='logs/python/'+logname, filemode='w', format='%(levelname)s:%(message)s', level=logging.DEBUG)
        elif opt == '-S':
            try:
                os.chdir("EPEM")
            except FileNotFoundError:
                pass
            Path("db/").mkdir(parents=True, exist_ok=True)
            global fastapi_process
            print(os.getcwd())
            fastapi_process= subprocess.Popen(["uvicorn", "API_communication:app", "--port", "8080", "--log-config", ".\log\log.ini"])
            atexit.register(close_all)
    
    EPEM_manager.EPEM_Manager().main_loop()

def start_environment():
    global environment_process
    if environment_process is None:
        environment_process = subprocess.Popen(environment_command, shell = True)

def start_experience_manager():
    global em_process
    if em_process is None:
        em_process = subprocess.Popen("start cmd.exe /k \"" + em_command + "\"", shell = True, creationflags=subprocess.CREATE_NEW_CONSOLE)

if __name__ == '__main__':
    main(sys.argv[1:])
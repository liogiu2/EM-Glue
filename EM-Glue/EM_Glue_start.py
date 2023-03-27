import os
import sys
from utilities import read_json_file
from pathlib import Path
parameters = read_json_file("parameters.json")
if os.name == 'nt':
    environment_command = parameters["Windows"]["environment_command"]
    em_command = parameters["Windows"]["experience_manager_command"]
else:
    environment_command = parameters["MAC"]["environment_command"]
    em_command = parameters["MAC"]["experience_manager_command"]
import logging
import getopt
from datetime import datetime
import subprocess
import atexit
import EM_Glue_manager

fastapi_process = None
environment_process = None
em_process = None

def close_all():
    global fastapi_process, environment_process, em_process
    fastapi_process.terminate()
    environment_process.kill()
    if os.name == 'nt':
        em_process.kill()

def main(argv):
    try:
        os.remove("db/sql_app.db")
    except FileNotFoundError:
        pass
    try:
        opts, args = getopt.getopt(argv,"hdl")
    except getopt.GetoptError:
        print('Parameter not recognized')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("usage: python EM_Glue_start.py <optional> -d -l -S")
            print("optional: -d to start the debug using debugpy on port 5678")
            print("optional: -l to start the logging")
            sys.exit()
        elif opt == '-d':
            import debugpy
            debugpy.listen(5678)
            debugpy.wait_for_client()
        elif opt == '-l':
            logname = "logEPEM"+datetime.now().strftime("%d%m%Y%H%M%S")+".log"
            Path("logs/python/").mkdir(parents=True, exist_ok=True)
            logging.basicConfig(filename='logs/python/'+logname, filemode='w', format='%(levelname)s:%(message)s', level=logging.DEBUG)

    try:
        os.chdir("EPEM")
    except FileNotFoundError:
        pass
    Path("db/").mkdir(parents=True, exist_ok=True)
    global fastapi_process
    print(os.getcwd())
    if os.name == 'nt':
        fastapi_process= subprocess.Popen(["uvicorn", "API_communication:app", "--port", "8080", "--log-config", ".\log\log.ini"])
    else:
        fastapi_process= subprocess.Popen(["uvicorn", "API_communication:app", "--port", "8080", "--log-config", "./log/log.ini"])
    atexit.register(close_all)
    
    try:
        EM_Glue_manager.EM_Glue_Manager().main_loop()
    except Exception as e:
        print(e)

def start_environment():
    global environment_process
    if environment_process is None:
        environment_process = subprocess.Popen(environment_command, shell = True)

def start_experience_manager():
    global em_process
    if em_process is None:
        if os.name == 'nt':
            em_process = subprocess.Popen("start cmd.exe /k \"" + em_command + "\"", shell = True)
        else:
            from applescript import tell
            tell.app('Terminal', 'do script "' + em_command + '"')
            em_process = 'something'

if __name__ == '__main__':
    main(sys.argv[1:])
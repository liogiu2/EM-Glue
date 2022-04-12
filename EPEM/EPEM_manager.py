import threading
from sql_app import crud, schemas
from sql_app.database import SessionLocal
from utilities import singleton, read_json_file
import time
import requests
from EPEM import start_environment

@singleton
class EPEM_Manager:

    def __init__(self):
        self.communication_phase_messages = read_json_file("messages.json")
        self.__API_online = False
        self.__check_timer = 0.1
        self._is_platform_online()

    def main_loop(self):
        """
        This method is the main loop of the EPEM. 
        """

        self.wait_platform_online()

        with SessionLocal.begin() as db:
            crud.create_shared_data(db=db, item= schemas.SharedDataCreate(name = "protocol_phase", value = "PHASE_1"))

        while self.__API_online:
            with SessionLocal() as db:
                message = crud.get_messages_not_sent_for_Platform(db)
                if len(message) == 0:
                    time.sleep(0.1)
                    continue
                crud.update_sent_before_sending(query_result= message, db = db)
                protocol_phase = crud.get_shared_data_with_name(db, "protocol_phase")
            if protocol_phase.value == "PHASE_1":
                if message[0].text == self.communication_phase_messages["PHASE_1"]["message_in"]:
                    with SessionLocal() as db:
                        crud.update_value_of_shared_data_with_name(db=db, name="protocol_phase", value="PHASE_2")
                    start_environment()
            elif protocol_phase.value == "PHASE_2":
                pass
            elif protocol_phase.value == "PHASE_3":
                pass
            elif protocol_phase.value == "PHASE_4":
                pass
    
    def wait_platform_online(self):
        """
        This method is used to wait until the platform is online.
        """
        while not self.__API_online:
            self._is_platform_online()
            time.sleep(0.1)
        self.__check_timer = 5
    
    def _is_platform_online(self):
        """
        This method is used to check if the platform is online.
        """
        t = threading.Timer(self.__check_timer, self._is_platform_online)
        t.start()
        try:
            response = requests.head("http://127.0.0.1:8080/")
            if response.status_code == 200:
                self.__API_online = True
            else:
                t.cancel()
                self.__API_online = False
        except:
            t.cancel()
            self.__API_online = False
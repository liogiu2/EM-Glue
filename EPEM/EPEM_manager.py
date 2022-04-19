import threading
from sql_app import crud, schemas, exceptions
from sql_app.database import SessionLocal
from utilities import singleton, read_json_file
import time
import requests
from EPEM_start import start_environment

class EPEM_Manager:

    _em_id = None
    _plt_id = None
    _env_id = None

    def __init__(self, testing = False):
        self.communication_phase_messages = read_json_file("messages.json")
        self.phase3_part1_received = False
        self.phase3_part2_received = False
        self.pddl_text = ""
        self.__API_online = self._is_platform_online()
        self.testing = testing

    def main_loop(self):
        """
        This method is the main loop of the EPEM. 
        """
        self.wait_platform_online()
        
        self._change_protocol_phase("PHASE_1")

        while self._is_platform_online():
            with SessionLocal() as db:
                message = crud.get_first_message_not_sent_for_platform(db)
                if message is None:
                    time.sleep(0.1)
                    continue
                crud.update_sent_before_sending(query_result= [message], db = db)
                protocol_phase = self.get_protocol_phase()
                text = str(message.text)
            if protocol_phase== "PHASE_1":
                if text == self.communication_phase_messages["PHASE_1"]["message_1"]:
                    with SessionLocal() as db:
                        self._em_id = int(crud.get_user_with_role(db, "EM").id_user)
                        self._plt_id = int(crud.get_user_with_role(db, "PLATFORM").id_user)
                        try:
                            crud.create_message(db = db, item = schemas.MessageCreate(text = self.communication_phase_messages["PHASE_1"]["message_2"], from_user=self._plt_id, to_user=self._em_id))
                        except (exceptions.InvalidMessageIDException, exceptions.InvalidUserException):
                            pass
                    self._change_protocol_phase("PHASE_2")
                    start_environment()
            elif protocol_phase == "PHASE_2":
                if text == self.communication_phase_messages["PHASE_2"]["message_3"]:
                    with SessionLocal() as db:
                        self._env_id = int(crud.get_user_with_role(db, "ENV").id_user)
                        try:
                            crud.create_message(db = db, item = schemas.MessageCreate(text = self.communication_phase_messages["PHASE_2"]["message_4"], from_user=self._plt_id, to_user=self._env_id))
                        except (exceptions.InvalidMessageIDException, exceptions.InvalidUserException):
                            pass
                    self._change_protocol_phase("PHASE_3")
            elif protocol_phase == "PHASE_3":
                if text == self.communication_phase_messages["PHASE_3"]["message_5"]:
                    self.phase3_part1_received = True
                elif text.startswith(self.communication_phase_messages["PHASE_3"]["message_6"]):
                    self.phase3_part2_received = True
                    self.pddl_text = str(text)
                
                if self.phase3_part1_received and self.phase3_part2_received:
                    with SessionLocal() as db:
                        try:
                            crud.create_message(db = db, item = schemas.MessageCreate(text = self.pddl_text, from_user=self._plt_id, to_user=self._em_id))
                        except (exceptions.InvalidMessageIDException, exceptions.InvalidUserException):
                            pass
                        self._change_protocol_phase("PHASE_4")
                            
            elif protocol_phase == "PHASE_4":
                pass


    def _change_protocol_phase(self, phase: str):
        """
        This method is used to change the protocol phase.

        Parameters
        ----------
        phase : str
            The new protocol phase.
        """
        with SessionLocal.begin() as db:
            if phase == "PHASE_1":
                protocol_phase = self.get_protocol_phase()
                if protocol_phase is None:
                    crud.create_shared_data(db=db, item= schemas.SharedDataCreate(name = "protocol_phase", value = "PHASE_1"))
                else:
                    crud.update_value_of_shared_data_with_name(db=db, name="protocol_phase", value=phase)
            else:
                crud.update_value_of_shared_data_with_name(db=db, name="protocol_phase", value=phase)
    
    def get_protocol_phase(self) -> str:
        """
        This method is used to get the current protocol phase.

        Returns
        -------
        str
            The current protocol phase.
        """
        with SessionLocal() as db:
            protocol_phase = crud.get_shared_data_with_name(db, "protocol_phase")
            if protocol_phase is None:
                return None
            return protocol_phase.value
    
    def wait_platform_online(self):
        """
        This method is used to wait until the platform is online.
        """
        while not self.__API_online:
            self.__API_online = self._is_platform_online()
            if self.__API_online:
                break
            time.sleep(0.5)
    
    def _is_platform_online(self):
        """
        This method is used to check if the platform is online.
        """
        try:
            response = requests.head("http://127.0.0.1:8080/")
            if response.status_code == 200:
                self.__API_online = True
            else:
                self.__API_online = False
        except:
            self.__API_online = False
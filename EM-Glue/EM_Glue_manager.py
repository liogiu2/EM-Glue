import threading
from sql_app import crud, schemas, exceptions
from sql_app.database import SessionLocal
from utilities import singleton, read_json_file
import time
import requests
from EM_Glue_start import start_environment, start_experience_manager

class EM_Glue_Manager:

    _em_id = None
    _plt_id = None
    _env_id = None

    def __init__(self):
        print("EPEM Manager starting...")
        self.communication_phase_messages = read_json_file("messages.json")
        self.communication_urls = read_json_file("parameters.json")['url']
        self.phase3_part1_received = False
        self.phase3_part2_received = False
        self.pddl_text = ""
        self.__number_of_requests = 100
        self.__platform_online = False
        self.__max_number_of_requests = 20
        self.__API_online = self._is_platform_online(initialization=True)
        
    def main_loop(self):
        """
        This method is the main loop of the EPEM. 
        """
        print("EPEM Manager started")
        print("EPEM Manager waiting for platform online")
        self.wait_platform_online()
        
        print("EPEM starting PHASE_1")
        self._change_protocol_phase("PHASE_1")

        print("EPEM starting experience manager")
        start_experience_manager()

        self._communication_setup()

        print("EPEM starting main loop...")
        while self._is_platform_online():
            with SessionLocal() as db:
                message = crud.get_first_message_not_sent_for_platform(db)
                if message is None:
                    time.sleep(0.1)
                    continue

    
    def _communication_setup(self):
        """
        This method is used to handle the setup of the communication using the communication protocol.
        """

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
                print("EPEM PHASE_1 executing...")
                self._communication_protocol_phase_1(text)
                print("EPEM PHASE_1 executed")
            elif protocol_phase == "PHASE_2":
                print("EPEM PHASE_2 executing...")
                self._communication_protocol_phase_2(text)
                print("EPEM PHASE_2 executed")
            elif protocol_phase == "PHASE_3":
                print("EPEM PHASE_3 executing...")
                self._communication_protocol_phase_3(text)
            elif protocol_phase == "PHASE_4":
                print("EPEM PHASE_4 executing...")
                self._communication_protocol_phase_4(text)
                print("EPEM PHASE_4 executed")
                break
        print("EPEM communication setup finished")
    
    def _communication_protocol_phase_1(self, text : str):
        """
        This method is used to handle the first phase of the communication protocol

        Parameters
        ----------
        text : str
            The message received.
        """
        if text.startswith(self.communication_phase_messages["PHASE_1"]["message_1"]):
            with SessionLocal() as db:
                self._em_id = int(crud.get_user_with_role(db, "EM").id_user)
                self._plt_id = int(crud.get_user_with_role(db, "PLATFORM").id_user)
                try:
                    crud.create_message(db = db, item = schemas.MessageCreate(text = self.communication_phase_messages["PHASE_1"]["message_2"], from_user=self._plt_id, to_user=self._em_id))
                except (exceptions.InvalidMessageIDException, exceptions.InvalidUserException):
                    pass
            self._change_protocol_phase("PHASE_2")
            start_environment()
    
    def _communication_protocol_phase_2(self, text : str):
        """
        This method is used to handle the second phase of the communication protocol

        Parameters
        ----------
        text : str
            The message received.
        """
        if text.startswith(self.communication_phase_messages["PHASE_2"]["message_3"]):
            with SessionLocal() as db:
                self._env_id = int(crud.get_user_with_role(db, "ENV").id_user)
                try:
                    crud.create_message(db = db, item = schemas.MessageCreate(text = self.communication_phase_messages["PHASE_2"]["message_4"], from_user=self._plt_id, to_user=self._env_id))
                except (exceptions.InvalidMessageIDException, exceptions.InvalidUserException):
                    pass
            self._change_protocol_phase("PHASE_3")
    
    def _communication_protocol_phase_3(self, text : str):
        """
        This method is used to handle the third phase of the communication protocol
        
        Parameters
        ----------
        text : str
            The message received.
        """
        if text == self.communication_phase_messages["PHASE_3"]["message_5"]:
            self.phase3_part1_received = True
            print("EPEM PHASE_3 Experience Manager received")
        elif text.startswith(self.communication_phase_messages["PHASE_3"]["message_6"]):
            self.phase3_part2_received = True
            self.pddl_text = str(text)
            print("EPEM PHASE_3 ENV received")
        
        if self.phase3_part1_received and self.phase3_part2_received:
            with SessionLocal() as db:
                try:
                    crud.create_message(db = db, item = schemas.MessageCreate(text = self.pddl_text, from_user=self._plt_id, to_user=self._em_id))
                except (exceptions.InvalidMessageIDException, exceptions.InvalidUserException):
                    pass
                self._change_protocol_phase("PHASE_4")
                print("EPEM PHASE_3 executed")
    
    def _communication_protocol_phase_4(self, text):
        """
        This method is used to handle the fourth phase of the communication protocol

        Parameters
        ----------
        text : str
            The message received.
        """
        if text == self.communication_phase_messages["PHASE_4"]["message_8"]:
            with SessionLocal() as db:
                try:
                    t_ENV = self.communication_phase_messages["PHASE_4"]["message_9"] + "###" + self.communication_urls["in_env"] + "###"+ self.communication_urls["out_env"]
                    crud.create_message(db = db, item = schemas.MessageCreate(text = t_ENV, from_user=self._plt_id, to_user=self._env_id))  
                    t_EM = self.communication_phase_messages["PHASE_4"]["message_10"] + "###" + self.communication_urls["in_em"] + "###" + self.communication_urls["out_em"]
                    crud.create_message(db = db, item = schemas.MessageCreate(text = t_EM, from_user=self._plt_id, to_user=self._em_id))        
                except (exceptions.InvalidMessageIDException, exceptions.InvalidUserException):
                    pass
            self._change_protocol_phase("DONE")

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
            self.__API_online = self._is_platform_online(initialization=True)
            if self.__API_online:
                break
            time.sleep(0.5)
    
    def _is_platform_online(self, initialization = False):
        """
        This method is used to check if the platform is online.
        """
        base_link = "http://127.0.0.1:8080/"
        if initialization:
            try:
                response = requests.head(base_link, timeout=0.5)
                if response.status_code == 200:
                    return True
                else:
                    return False
            except:
                return False
        else:
            if self.__number_of_requests > self.__max_number_of_requests:
                try:
                    response = requests.head(base_link, timeout=0.5)
                    if response.status_code == 200:
                        self.__platform_online = True
                    else:
                        self.__platform_online = False
                except:
                    self.__platform_online = False
                self.__number_of_requests = 0
            else:
                self.__number_of_requests += 1
            
            return self.__platform_online
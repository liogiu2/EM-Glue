import imp
from sql_app import crud
from sql_app.database import SessionLocal
from utilities import singleton, read_json_file
from communication_protocol_phases import CommunicationProtocolPhases
import shared_variables
import time
from EPEM import start_camelot

@singleton
class EPEM_Manager:

    def __init__(self):
        shared_variables.communication_phase_messages = read_json_file("messages.json")
        shared_variables.protocol_phase = CommunicationProtocolPhases.PHASE_1

    def main_loop(self):
        """
        This method is the main loop of the EPEM. 
        """
        while True:
            with SessionLocal.begin() as db:
                message = crud.get_messages_not_sent_for_Platform(db)
                if len(message) > 0:
                    message = crud.update_sent_before_sending(query_result= message, db = db)
            if shared_variables.protocol_phase == CommunicationProtocolPhases.PHASE_1:
                if message[0].text == "inizialization_em_1 Received":
                    start_camelot()
            time.sleep(0.2)